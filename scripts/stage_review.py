"""Print a review inventory for explicitly supplied files; never sign acceptance."""

import argparse
import hashlib
import sys
from pathlib import Path


def inventory(root, documents):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("project root must be a directory")
    rows, seen = [], set()
    for document in documents:
        path = Path(document).expanduser()
        path = (path if path.is_absolute() else root / path).resolve()
        if path in seen:
            continue
        seen.add(path)
        row = {"name": path.name, "path": str(path), "sha256": "",
               "status": "SUBMITTED", "error": ""}
        try:
            if not path.is_file():
                raise FileNotFoundError("not a regular file")
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(65536), b""):
                    digest.update(chunk)
            row["sha256"] = digest.hexdigest()
        except OSError as error:
            row.update(status="MISSING", error=str(error))
        rows.append(row)
    return rows


def cell(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(
        ">", "&gt;").replace("|", "&#124;").replace("\n", "&#10;").replace("\r", "&#13;")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--document", action="append", required=True,
                        help="Repeat for every review document; relative to --root")
    args = parser.parse_args(argv)
    try:
        rows = inventory(args.root, args.document)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print("| 阶段 | 文档名 | 完整绝对路径 | SHA-256 | 文件候选状态 |")
    print("|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(cell(value) for value in
              (args.stage, row["name"], row["path"], row["sha256"], row["status"])) + " |")
        if row["error"]:
            print("{}: {}".format(row["path"], row["error"]), file=sys.stderr)
    print("\n仅校验所列文件及摘要；完整性、审阅范围和真实验收状态须由过程负责人核对。")
    return 1 if any(row["error"] for row in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
