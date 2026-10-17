#!/usr/bin/env python3
"""Check official stable releases and replace a complete installed Skill bundle."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from hs_paths import ensure_utf8_stdout
from skill_router import load_registry, validate_registry

REPOSITORY = "zhaoxuan-inside/hs-dev-skill"
API_URL = "https://api.github.com/repos/" + REPOSITORY + "/releases/latest"
BUNDLE_ROOT = Path(__file__).resolve().parent.parent
MAX_DOWNLOAD_BYTES = 64 * 1024 * 1024
MAX_UNPACKED_BYTES = 256 * 1024 * 1024
PACKAGE_ITEMS = ("SKILL.md", "README.md", "README.forum.md", "LICENSE", "Makefile",
                 ".gitignore", ".gitattributes", "skills", "scripts", "references",
                 "resources", "examples", "tests")


def parse_release_version(version):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)\.(\d+)", str(version))
    if not match:
        raise ValueError("Expected a stable four-part release version: " + str(version))
    return tuple(int(part) for part in match.groups())


def read_version(bundle):
    text = (Path(bundle) / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^  version:\s*[\"']?([^\"'\s]+)", text)
    if not match:
        raise ValueError("Missing installed metadata.version")
    version = match.group(1)
    parse_release_version(version)
    return version


def fetch_bytes(url, limit=MAX_DOWNLOAD_BYTES):
    request = urllib.request.Request(url, headers={
        "User-Agent": "hs-dev-skill-updater", "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=8) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Update download exceeds size limit")
    return data


def fetch_release():
    return json.loads(fetch_bytes(API_URL, 1024 * 1024).decode("utf-8"))


def release_version(release):
    if not isinstance(release, dict) or release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("Latest response is not a published stable release")
    tag = str(release.get("tag_name", ""))
    version = tag[1:] if tag.startswith("v") else tag
    parse_release_version(version)
    return version


def check_update(bundle):
    """No filesystem writes; unavailable is distinct from being up to date."""
    installed = None
    try:
        installed = read_version(bundle)
        latest = release_version(fetch_release())
        current_key, latest_key = parse_release_version(installed), parse_release_version(latest)
        available = latest_key > current_key
        status = "update_available" if available else "current" if latest_key == current_key else "ahead"
        target = Path(bundle).expanduser().resolve()
        method = "git" if (target / ".git").exists() else "bundle"
        command = (["git", "-C", str(target), "pull", "--ff-only"] if method == "git" else
                   [sys.executable, str(Path(__file__).resolve()), "install", "--target", str(target)])
        hint = "源码工作副本请先保存本地改动，再运行更新命令。" if method == "git" else "可运行 update_command 或回复“更新 hs-dev-skill”。"
        return {"ok": True, "status": status, "installed": installed, "latest": latest,
                "update_available": available,
                "release_url": "https://github.com/" + REPOSITORY + "/releases/tag/v" + latest,
                "update_method": method, "update_command": command,
                "message": ("hs-dev-skill 发现新版 v{}（当前 v{}），".format(latest, installed) + hint
                            if available else "当前版本已是最新正式版。" if status == "current" else "本地版本领先于最新正式发布版，无需降级。")}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"ok": False, "status": "unavailable", "installed": installed, "latest": None,
                "update_available": None, "message": "更新检测暂不可用；继续当前任务。", "error": str(exc)}


def validate_bundle(bundle):
    bundle = Path(bundle)
    version = read_version(bundle)
    text = (bundle / "SKILL.md").read_text(encoding="utf-8")
    body = re.search(r"版本：v([0-9.]+)", text)
    if not re.search(r"(?m)^name:\s*hs-dev-skill\s*$", text) or not body or body.group(1) != version:
        raise ValueError("Bundle identity/body version mismatch")
    if (bundle / "README.md").is_file():
        badge = re.search(r"badge/skill-v([0-9.]+)-blue", (bundle / "README.md").read_text(encoding="utf-8"))
        if badge and badge.group(1) != version:
            raise ValueError("README version mismatch")
    for name in ("skills", "scripts", "references", "resources"):
        if not (bundle / name).is_dir():
            raise ValueError("Incomplete bundle: missing " + name)
    validate_registry(bundle, load_registry(bundle))


def protect_target(target):
    target = Path(target).expanduser().absolute()
    if target.is_symlink():
        raise ValueError("Refusing to replace a symlink; choose the actual installed bundle")
    if (target / ".git").exists():
        raise ValueError("Refusing to overwrite a Git working copy; use git pull --ff-only after preserving local changes")
    if target.exists() and not target.is_dir():
        raise ValueError("Install target is not a directory")
    return target


def install_local(source, target, reinstall=False):
    target = protect_target(target)
    source = Path(source).expanduser().resolve()
    resolved_target = target.resolve()
    if source == resolved_target or source in resolved_target.parents or resolved_target in source.parents:
        raise ValueError("Source and target bundles must not overlap")
    validate_bundle(source)
    version = read_version(source)
    current = read_version(target) if target.exists() else None
    if current and parse_release_version(version) < parse_release_version(current):
        raise ValueError("Refusing a version downgrade")
    if current == version and not reinstall:
        validate_bundle(target)
        return {"ok": True, "status": "current", "installed": current, "target": str(target)}
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".hs-skill-update-", dir=str(target.parent)) as temporary:
        staged, previous = Path(temporary) / "staged", Path(temporary) / "previous"
        staged.mkdir()
        for name in PACKAGE_ITEMS:
            original = source / name
            if not original.exists():
                continue
            candidates = [original] + list(original.rglob("*")) if original.is_dir() else [original]
            if any(path.is_symlink() for path in candidates):
                raise ValueError("Package symlinks are not supported")
            if original.is_dir():
                shutil.copytree(original, staged / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".hs_cache"))
            else:
                shutil.copy2(original, staged / name)
        validate_bundle(staged)
        if target.exists():
            target.rename(previous)
        try:
            staged.rename(target)
            validate_bundle(target)
        except BaseException:
            if target.exists():
                shutil.rmtree(target)
            if previous.exists():
                previous.rename(target)
            raise
    return {"ok": True, "status": "updated", "previous": current, "installed": version,
            "target": str(target), "message": "完整包已更新，下次加载 Skill 时使用新版本。"}


def extract_bundle(data, destination):
    destination = Path(destination)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > 20000 or sum(info.file_size for info in members) > MAX_UNPACKED_BYTES:
            raise ValueError("Release archive exceeds extraction limits")
        seen = set()
        for info in members:
            parts = PurePosixPath(info.filename).parts
            key = info.filename.rstrip("/").casefold()
            if (not parts or parts[0] != "hs-dev-skill" or ".." in parts
                    or "\\" in info.filename or any(":" in part for part in parts)
                    or key in seen or stat.S_ISLNK(info.external_attr >> 16)
                    or info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                raise ValueError("Unsafe or duplicate release archive member: " + info.filename)
            seen.add(key)
        destination.mkdir(parents=True, exist_ok=True)
        for info in members:
            path = destination.joinpath(*PurePosixPath(info.filename).parts)
            if info.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as incoming, path.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
    return destination / "hs-dev-skill"


def install_release(target, reinstall=False):
    target = protect_target(target)
    release = fetch_release()
    version = release_version(release)
    current = read_version(target) if target.exists() else None
    if current and (parse_release_version(version) < parse_release_version(current) or (version == current and not reinstall)):
        validate_bundle(target)
        return {"ok": True, "status": "current" if version == current else "ahead", "installed": current, "latest": version}
    filename = "hs-dev-skill-v" + version + ".zip"
    prefix = "https://github.com/" + REPOSITORY + "/releases/download/v" + version + "/"
    assets = {asset["name"]: asset["browser_download_url"] for asset in release.get("assets", [])}
    for name in (filename, "SHA256SUMS"):
        if assets.get(name) != prefix + name:
            raise ValueError("Missing official full bundle/checksum release asset: " + name)
    checksums = fetch_bytes(assets["SHA256SUMS"], 1024 * 1024).decode("utf-8")
    hashes = re.findall(r"(?m)^([0-9a-fA-F]{64}) [ *]" + re.escape(filename) + r"\s*$", checksums)
    if len(hashes) != 1:
        raise ValueError("Release checksum entry is missing or ambiguous")
    data = fetch_bytes(assets[filename])
    if hashlib.sha256(data).hexdigest() != hashes[0].lower():
        raise ValueError("Release checksum mismatch; installation unchanged")
    with tempfile.TemporaryDirectory(prefix="hs-skill-download-") as temporary:
        source = extract_bundle(data, Path(temporary) / "extracted")
        if read_version(source) != version:
            raise ValueError("Archive version does not match release tag")
        result = install_local(source, target, reinstall=reinstall)
    return dict(result, archive_sha256=hashes[0].lower())


def main(argv=None):
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="Check latest stable release; never install")
    check.add_argument("--root", type=Path, default=BUNDLE_ROOT)
    check.add_argument("--quiet", action="store_true", help="Only print a human prompt if an update exists")
    install = commands.add_parser("install", help="Explicitly update an installed complete bundle")
    install.add_argument("--target", type=Path, default=BUNDLE_ROOT)
    install.add_argument("--source", type=Path, help="Validated local complete bundle; otherwise use official release")
    install.add_argument("--reinstall", action="store_true", help="Repair an installation of the same version")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            result = check_update(args.root)
            if args.quiet:
                if result.get("update_available"):
                    print(result["message"])
                    print(json.dumps(result["update_command"], ensure_ascii=False))
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        result = install_local(args.source, args.target, args.reinstall) if args.source else install_release(args.target, args.reinstall)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
