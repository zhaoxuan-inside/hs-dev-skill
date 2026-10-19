"""Deterministic semantic units derived from authoritative sources."""
import ast
from bisect import bisect_right
import json
import re

from ..storage import sha

FORMAT_VERSION = 1
UNIT_META = re.compile(r'<!--\s*hs-unit:\s*(\{[^\n]*\})\s*-->')


def file_id(path):
    return "file:" + path


def units(path, text):
    lines = text.splitlines()
    root = file_id(path)
    result, identities = [], {}

    def add(key, title, start, end, kind, parent=None, requires=(), searchable=True, metadata=None,
            revision_body=None):
        body = revision_body if revision_body is not None else "\n".join(lines[start - 1:end])
        meta = metadata or {}
        if not isinstance(meta, dict) or set(meta) - {"id", "requires", "references"}:
            raise ValueError("Invalid hs-unit metadata: " + path)
        if "id" in meta:
            if not isinstance(meta["id"], str) or not meta["id"].strip() or len(meta["id"]) > 1024:
                raise ValueError("Unit id must be a bounded nonempty string")
            key = "unit:" + meta["id"]
        for name in ("requires", "references"):
            if name in meta and (not isinstance(meta[name], list) or len(meta[name]) > 128 or any(not isinstance(x, str) or not x or len(x) > 1024 for x in meta[name])):
                raise ValueError("Unit relations must be arrays of IDs")
        identities[key] = identities.get(key, 0) + 1
        if identities[key] > 1:
            if "id" in meta:
                raise ValueError("Duplicate explicit unit identity: " + key)
            key += ":occurrence:" + str(identities[key])
        props = {"unit_id": key, "unit_revision": sha(body.encode()), "unit_kind": kind,
                 "parent_id": parent, "completeness": "atomic", "requires": list(requires) + meta.get("requires", []),
                 "references": meta.get("references", []), "format_version": FORMAT_VERSION}
        result.append({"key": key, "title": title, "start": start, "end": end,
                       "body": body if searchable else "", "properties": props})
        return key

    add(root, path, 1, len(lines), "file", searchable=False)
    if path.endswith(".md"):
        headings, metadata, fence = [], [], None
        for i, line in enumerate(lines):
            marker = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value
                elif value[0] == fence[0] and len(value) >= len(fence):
                    fence = None
                continue
            if fence is None:
                unit_match = UNIT_META.search(line)
                if unit_match:
                    metadata.append((i + 1, json.loads(unit_match.group(1))))
                match = re.match(r'^(#{1,6})\s+(.+?)\s*#*$', line)
                if match:
                    headings.append((i + 1, len(match.group(1)), match.group(2)))
        if headings:
            result[0]["properties"]["completeness"] = "splittable"
            if headings[0][0] > 1:
                add(root + ":preamble", path + " preamble", 1, headings[0][0] - 1, "preamble", root)

            # One stack pass assigns both subtree and own-section boundaries.
            # A child contributes its revision to its parent, so nested section
            # versions describe the same whole subtree in linear total work.
            sections, stack = [], []
            for start, depth, title in headings:
                if sections:
                    sections[-1]["own_end"] = start - 1
                while stack and stack[-1]["depth"] >= depth:
                    stack.pop()["end"] = start - 1
                section = {"start": start, "depth": depth, "title": title,
                           "end": len(lines), "own_end": len(lines),
                           "parent": stack[-1] if stack else None, "children": []}
                if section["parent"]:
                    section["parent"]["children"].append(section)
                sections.append(section)
                stack.append(section)

            section_starts = [section["start"] for section in sections]
            for line, meta in metadata:
                pos = bisect_right(section_starts, line) - 1
                if pos >= 0:
                    section = sections[pos]
                    if line <= section["own_end"]:
                        section.setdefault("metadata", []).append(meta)
            for section in sections:
                if len(section.get("metadata", [])) > 1:
                    raise ValueError("Multiple metadata declarations in one section: " + path)
                title, start, end = section["title"], section["start"], section["end"]
                anchor = re.search(r'\s*\{#([^}]+)\}\s*$', title)
                slug = anchor.group(1) if anchor else re.sub(r'\s+', '-', title.strip().casefold())
                parent = section["parent"]
                parent_key = parent.get("key") if parent else root
                logical = (parent["logical"] + "/" if parent else "") + slug
                section["logical"] = logical
                section["key"] = root + "#section:" + logical
                own_text = "\n".join(lines[start - 1:section["own_end"]])
                section["own_revision"] = sha(own_text.encode())
                section["key"] = add(section["key"], title, start, end, "section", parent_key,
                                     metadata=section.get("metadata", [None])[0], revision_body=own_text)
                section["item"] = result[-1]
                result[-1]["body"] = own_text

            for section in reversed(sections):
                child_revisions = [child["revision"] for child in section["children"]]
                section["revision"] = sha(json.dumps(
                    [FORMAT_VERSION, section["own_revision"], child_revisions],
                    ensure_ascii=False, separators=(",", ":")).encode())
                section["item"]["properties"]["unit_revision"] = section["revision"]
    elif path.endswith(".py"):
        tree = ast.parse(text, filename=path)
        definitions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        first = min((min([n.lineno] + [d.lineno for d in n.decorator_list]) for n in ast.walk(tree) if isinstance(n, definitions)), default=len(lines) + 1)
        preamble = None
        if first > 1:
            preamble = add(root + ":preamble", path + " preamble", 1, first - 1, "preamble", root)
        def walk(nodes, prefix="", parent=root, required=()):
            for node in nodes:
                if not isinstance(node, definitions):
                    # Nested conditional definitions still retain their lexical scope.
                    walk(list(ast.iter_child_nodes(node)), prefix, parent, required)
                    continue
                qualified = prefix + node.name
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                key = "symbol:" + path + ":" + qualified
                key = add(key, qualified, start, node.end_lineno, "symbol", parent, required)
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, definitions)]
                    first_child = methods[0] if methods else node.body[0]
                    header_end = min([first_child.lineno] + [d.lineno for d in getattr(first_child, "decorator_list", [])]) - 1
                    header = None
                    if header_end >= start:
                        header = add(key + ":header", qualified + " header", start, header_end, "preamble", key, required)
                    walk(node.body, qualified + ".", key, (*required, *((header,) if header else ())))
                else:
                    walk(node.body, qualified + ".<locals>.", key, (*required, key))
        walk(tree.body, required=(preamble,) if preamble else ())
        if any(u["properties"]["unit_kind"] == "symbol" for u in result):
            result[0]["properties"]["completeness"] = "splittable"
    if len(result) == 1:
        result[0]["body"] = text
    ids = [u["key"] for u in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate semantic unit identity: " + path)
    return result
