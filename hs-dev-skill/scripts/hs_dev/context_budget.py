"""Bound the entire canonical payload; tokenizer assets must be local."""
import json
import os
import hashlib
import base64
from types import FunctionType
import tempfile
from functools import lru_cache
from pathlib import Path


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


@lru_cache(maxsize=2)
def tokenizer(name):
    if not name:
        return None
    if name not in {"cl100k_base", "o200k_base"}:
        raise ValueError("Unsupported tokenizer")
    url = f"https://openaipublic.blob.core.windows.net/encodings/{name}.tiktoken"
    cache = Path(os.environ.get("TIKTOKEN_CACHE_DIR", os.environ.get("DATA_GYM_CACHE_DIR", str(Path(tempfile.gettempdir()) / "data-gym-cache"))))
    if not (cache / hashlib.sha1(url.encode()).hexdigest()).is_file():
        raise ValueError("Provision tokenizer ranks locally before context requests")
    try:
        import tiktoken
        from tiktoken_ext import openai_public
    except ImportError:
        raise ValueError("Configured tokenizer requires the optional tiktoken package") from None
    rank_file = cache / hashlib.sha1(url.encode()).hexdigest()
    def local_ranks(requested_url, expected_hash=None):
        if requested_url != url:
            raise ValueError("Tokenizer constructor requested an unprovisioned resource")
        data = rank_file.read_bytes()
        if expected_hash and hashlib.sha256(data).hexdigest() != expected_hash:
            raise ValueError("Local tokenizer ranks failed their integrity check")
        return {base64.b64decode(token, validate=True): int(rank)
                for token, rank in (line.split() for line in data.splitlines() if line)}
    original = getattr(openai_public, name)
    constructor = FunctionType(original.__code__, {**original.__globals__, "load_tiktoken_bpe": local_ranks})
    return tiktoken.Encoding(**constructor())



class Budget:
    def __init__(self, settings, direct):
        if not isinstance(direct, dict) or set(direct) - {"max_output_bytes", "max_output_tokens"}:
            raise ValueError("Invalid context budget")
        self.limits = {}
        for key in ("max_output_bytes", "max_output_tokens"):
            value = direct.get(key, settings[key])
            if type(value) is not int or value < (1024 if key.endswith("bytes") else 0) or value > settings[key]:
                raise ValueError("Context budget outside configured bounds: " + key)
            self.limits[key] = value
        self.encoder, self.name = tokenizer(settings["tokenizer"]), settings["tokenizer"]

    def fits(self, result, read_bytes):
        usage = result["usage"]
        usage.update(read_bytes=read_bytes, output_bytes=0, tokens=None, estimated_tokens=None,
                     count_kind="tokenizer:" + self.name + ":tokens_field_null" if self.encoder else "utf8_byte_upper_estimate",
                     token_limit_enforced=bool(self.encoder and self.limits["max_output_tokens"]))
        for _ in range(12):
            size = len(encode(result).encode())
            update = {"output_bytes": size, "estimated_tokens": None if self.encoder else size}
            if all(usage[k] == v for k, v in update.items()):
                break
            usage.update(update)
        if self.encoder:
            count = len(self.encoder.encode(encode(result), disallowed_special=()))
            usage.update(tokens=count, count_kind="tokenizer:" + self.name + ":tokens_field_null")
            # Converge byte count, which does not have tokenization oscillation.
            for _ in range(12):
                size = len(encode(result).encode())
                if usage["output_bytes"] == size:
                    break
                usage["output_bytes"] = size
            exact = len(self.encoder.encode(encode(result), disallowed_special=()))
            # Reported count excludes its own value; enforcement always measures
            # the actual final payload including counters.
        else:
            exact = None
        return usage["output_bytes"] <= self.limits["max_output_bytes"] and (
            not self.encoder or not self.limits["max_output_tokens"] or exact <= self.limits["max_output_tokens"])
