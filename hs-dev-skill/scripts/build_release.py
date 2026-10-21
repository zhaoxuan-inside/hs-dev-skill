"""Build validated, reproducible Skill ZIPs and SHA256SUMS for GitHub Releases."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile

from build_skill_packages import build, validate
from hs_dev import __version__


def archive(source, destination, paths):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for path in sorted(paths):
            if path.is_file():
                info = zipfile.ZipInfo(path.relative_to(source).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, path.read_bytes())


def release(root, destination, version):
    if not re.fullmatch(r"\d+(?:\.\d+){3}", version):
        raise ValueError("Release version must have four numeric components")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Release output directory must be empty")
    with tempfile.TemporaryDirectory() as temporary:
        packages = Path(temporary) / "skills"
        result = build(root, packages)
        errors = validate(packages)
        if errors:
            raise ValueError("Invalid Skill packages: " + "; ".join(errors))
        for package in sorted(packages.iterdir()):
            if package.is_dir():
                archive(packages, destination / f"{package.name}-v{version}.zip", package.rglob("*"))
        archive(packages, destination / f"hs-dev-all-skills-v{version}.zip", packages.rglob("*"))
        (destination / "catalog.json").write_bytes((packages / "catalog.json").read_bytes())
    assets = sorted(destination.iterdir())
    (destination / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in assets), encoding="utf-8")
    return {**result, "version": version, "assets": len(assets) + 1, "output": str(destination)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    destination = args.output or args.root / "output/releases" / f"v{__version__}"
    print(json.dumps(release(args.root.resolve(), destination.resolve(), __version__), ensure_ascii=False))


if __name__ == "__main__":
    main()
