"""Build standalone Agent Skill packages from the hs-dev-skill source collection."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")
def _relative_target(markdown: Path, target: str) -> Path | None:
    target = target.replace("\\", "/")
    target = target.split("#", 1)[0]
    if not target or "://" in target or target.startswith(("mailto:", "/")):
        return None
    return (markdown.parent / target).resolve()


def _resource_destination(source: Path, skill_source: Path, references_root: Path) -> Path:
    resolved = source.resolve()
    if resolved.is_relative_to(references_root.resolve()):
        return Path("references") / resolved.relative_to(references_root.resolve())
    skill_refs = (skill_source.parent / "references").resolve()
    if resolved.is_relative_to(skill_refs):
        return Path("references") / resolved.relative_to(skill_refs)
    raise ValueError(f"Resource escapes the Skill source roots: {source}")


def _render_markdown(text: str, source_file: Path, destination_file: Path,
                     skill_source: Path, references_root: Path,
                     known_skills: set[Path], package_root: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        resolved = _relative_target(source_file, target)
        if resolved is None:
            return match.group(0)
        if resolved in known_skills:
            return f"{label} ({resolved.parent.name})"
        if resolved.name == "SKILL.md" and resolved != skill_source.resolve():
            return label
        if not resolved.exists():
            raise ValueError(f"Broken source link in {source_file}: {target}")
        destination = _resource_destination(resolved, skill_source, references_root)
        rel = Path(os.path.relpath(package_root / destination, destination_file.parent))
        rewritten = rel.as_posix()
        if "#" in target:
            rewritten += "#" + target.split("#", 1)[1]
        return f"[{label}]({rewritten})"

    return LINK.sub(replace, text)


def _render_main_markdown(text: str, source_file: Path, destination_file: Path,
                          package_root: Path, source_root: Path,
                          references_source: Path, scripts_source: Path,
                          docs_source: Path, known_skills: set[Path]) -> str:
    """Flatten legacy source paths into a standard, self-contained Skill package."""
    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        resolved = _relative_target(source_file, target)
        if resolved in known_skills:
            return f"{label} ({resolved.parent.name})"
        if resolved is None:
            return match.group(0)
        if resolved == (source_root / "hs-dev-skill/SKILL.md").resolve():
            mapped = package_root / "SKILL.md"
        elif resolved == (source_root / "README.md").resolve():
            mapped = package_root / "README.md"
        elif resolved.is_relative_to(references_source.resolve()):
            mapped = package_root / "references" / resolved.relative_to(references_source.resolve())
        elif resolved.is_relative_to(scripts_source.resolve()):
            mapped = package_root / "scripts" / resolved.relative_to(scripts_source.resolve())
        elif resolved.is_relative_to(docs_source.resolve()):
            mapped = package_root / "references/skill-docs" / resolved.relative_to(docs_source.resolve())
        else:
            raise ValueError(f"Main Skill link is outside the published package: {source_file} -> {target}")
        if not mapped.exists():
            raise ValueError(f"Main Skill link points to an excluded resource: {source_file} -> {target}")
        suffix = "#" + target.split("#", 1)[1] if "#" in target else ""
        rel = Path(os.path.relpath(mapped, destination_file.parent)).as_posix()
        return f"[{label}]({rel}{suffix})"

    text = LINK.sub(replace, text)
    for old, new in (("hs-dev-skill/share/", "references/"),
                     ("hs-dev-skill/scripts/", "scripts/"),
                     ("hs-dev-docs/", "references/skill-docs/")):
        text = text.replace(old, new)
    return text


def _linked_resources(skill_source: Path, references_root: Path,
                      known_skills: set[Path]) -> set[Path]:
    pending = [skill_source]
    visited: set[Path] = set()
    resources: set[Path] = set()
    while pending:
        current = pending.pop().resolve()
        if current in visited:
            continue
        visited.add(current)
        text = current.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            target = match.group(2)
            resolved = _relative_target(current, target)
            if resolved is None or resolved in known_skills:
                continue
            if resolved.name == "SKILL.md" and resolved != skill_source.resolve():
                continue
            if not resolved.exists():
                raise ValueError(f"Broken source link in {current}: {target}")
            if resolved.suffix.lower() not in {".md", ".idx", ".json", ".yaml", ".yml", ".toml"}:
                continue
            _resource_destination(resolved, skill_source, references_root)
            resources.add(resolved)
            if resolved.suffix.lower() in {".md", ".idx"}:
                pending.append(resolved)
    return resources


def build(source_root: Path, output_root: Path) -> dict[str, object]:
    source_root = source_root.resolve()
    references_root = (source_root / "hs-dev-skill/share").resolve()
    manifest_path = source_root / "hs-dev-skill/skill-packages.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    skill_root = source_root / manifest["children_root"]
    child_sources = sorted(skill_root.rglob("SKILL.md"))
    known_skills = {p.resolve() for p in child_sources}
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    main_dest = output_root / manifest["main"]["name"]
    if main_dest.exists():
        shutil.rmtree(main_dest)
    main_dest.mkdir(parents=True)
    main = manifest["main"]
    references_source = (source_root / main["references"]).resolve()
    scripts_source = (source_root / main["scripts"]).resolve()
    docs_source = (source_root / main["skill_docs"]).resolve()
    shutil.copy2(source_root / main["source"], main_dest / "SKILL.md")
    shutil.copy2(source_root / main["license"], main_dest / "LICENSE")
    (main_dest / "README.md").write_text(
        "# hs-dev-skill\n\n"
        "这是可独立安装的总控 Skill 包。入口为 `SKILL.md`；按需资料位于 `references/`，"
        "运行工具位于 `scripts/`。子 Skill 是与本目录同级发布的独立包，层级与分类见 "
        "`references/skills/skills.idx`。\n\n"
        "在目标工程运行命令时使用：\n\n"
        "```bash\npython scripts/hs_dev.py --root /path/to/project status\n"
        "python scripts/hs_dev.py --root /path/to/project init\n```\n\n"
        "`init` 仅用于尚未初始化的工程。已有任务先检查 `status` 并按主入口恢复或续做。\n",
        encoding="utf-8")

    def exclude_nonruntime_scripts(directory: str, names: list[str]) -> set[str]:
        excluded = {name for name in names if name == "__pycache__" or name.endswith((".pyc", ".pyo"))}
        if Path(directory).resolve() == scripts_source:
            excluded.update(name for name in names if name in {
                "tests", "build_docs.py", "benchmark_context.py", "build_skill_packages.py", "build_release.py"})
        return excluded

    shutil.copytree(references_source, main_dest / "references")
    shutil.copytree(scripts_source, main_dest / "scripts", ignore=exclude_nonruntime_scripts)
    shutil.copytree(docs_source, main_dest / "references/skill-docs")

    workflow_catalog = main_dest / "scripts/hs_dev/data/workflow.json"
    workflow_data = json.loads(workflow_catalog.read_text(encoding="utf-8"))
    for stage in workflow_data["stages"]:
        stage["path"] = stage["path"].replace("hs-dev-skill/share/", "references/")
        for activity in stage["activities"]:
            activity["path"] = activity["path"].replace("hs-dev-skill/share/", "references/")
    workflow_catalog.write_text(json.dumps(workflow_data, ensure_ascii=False, indent=2) + "\n",
                                encoding="utf-8")

    index_file = main_dest / "references/skills/skills.idx"
    index_file.write_text(
        "# 子 Skill 路由索引\n\n"
        "子 Skill 作为总控包的同级独立发布包安装；本索引只记录层级与分类，不嵌套子 Skill 文件。"
        "总控按请求目标和自身路由规则选择实际需要的 Skill。\n\n"
        "| Skill | 分类 |\n|---|---|\n" +
        "".join(f"| {p.parent.name} | {p.parent.parent.name} |\n" for p in child_sources),
        encoding="utf-8")
    for markdown in [*main_dest.rglob("*.md"), *main_dest.rglob("*.idx")]:
        relative = markdown.relative_to(main_dest)
        if relative == Path("SKILL.md"):
            original = source_root / main["source"]
        elif relative == Path("README.md"):
            original = source_root / "README.md"
        elif relative.parts[0] == "references":
            tail = Path(*relative.parts[1:])
            original = (docs_source / tail.relative_to("skill-docs")
                        if tail.parts[0] == "skill-docs" else references_source / tail)
        else:
            original = scripts_source / Path(*relative.parts[1:])
        markdown.write_text(
            _render_main_markdown(markdown.read_text(encoding="utf-8"), original,
                                  markdown, main_dest, source_root, references_source,
                                  scripts_source, docs_source, known_skills),
            encoding="utf-8")

    catalog: list[dict[str, object]] = [{
        "name": manifest["main"]["name"], "type": "orchestrator",
        "path": manifest["main"]["name"], "independent": True
    }]
    for source in child_sources:
        name = source.parent.name
        package = output_root / name
        if package.exists():
            shutil.rmtree(package)
        package.mkdir(parents=True)
        shutil.copy2(source, package / "SKILL.md")
        policy = manifest["resource_policy"]
        resources = (_linked_resources(source, references_root, known_skills)
                     if policy.get("include_linked_resources") else set())
        mandatory_shared = manifest.get("shared_resources", [])
        if mandatory_shared and not policy.get("include_mandatory_shared_resources"):
            raise ValueError("Manifest has shared resources but policy disables mandatory shared resources")
        if policy.get("include_mandatory_shared_resources"):
            for path in mandatory_shared:
                shared = (source_root / path).resolve()
                resources.add(shared)
                if policy.get("include_linked_resources"):
                    resources.update(_linked_resources(shared, references_root, known_skills))
        destinations: dict[Path, Path] = {
            res: package / _resource_destination(res, source, references_root)
            for res in resources
        }
        for res, dest in destinations.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            if res.suffix.lower() in {".md", ".idx"}:
                body = _render_markdown(res.read_text(encoding="utf-8"), res,
                                        dest, source, references_root, known_skills, package)
                dest.write_text(body, encoding="utf-8")
            else:
                shutil.copy2(res, dest)
        body = _render_markdown((package / "SKILL.md").read_text(encoding="utf-8"),
                                source, package / "SKILL.md", source,
                                references_root, known_skills, package)
        (package / "SKILL.md").write_text(body, encoding="utf-8")
        category = next((group for group, names in manifest["categories"].items()
                         if name in names), None)
        if category is None:
            raise ValueError(f"Skill has no category in manifest: {name}")
        catalog.append({"name": name, "type": category, "path": name,
                        "parent": manifest["main"]["name"], "independent": True})

    (output_root / "catalog.json").write_text(
        json.dumps({"schema_version": 1, "skills": catalog}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    return {"packages": len(catalog), "children": len(child_sources), "output": str(output_root)}


def validate(output_root: Path) -> list[str]:
    errors: list[str] = []
    output_root = output_root.resolve()
    for skill_file in sorted(output_root.glob("*/SKILL.md")):
        package = skill_file.parent
        text = skill_file.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1] if text.startswith("---\n") and text.count("---") >= 2 else ""
        name = re.search(r"(?m)^name:\s*([^\s]+)\s*$", frontmatter)
        if not name or name.group(1) != package.name or not re.search(r"(?m)^description:\s*\S", frontmatter):
            errors.append(f"Invalid Skill frontmatter: {skill_file}")
        markdown_files = [skill_file, *package.rglob("*.md"), *package.rglob("*.idx")]
        for markdown in markdown_files:
            for match in LINK.finditer(markdown.read_text(encoding="utf-8")):
                target = match.group(2).split("#", 1)[0]
                if not target or "://" in target or target.startswith(("mailto:", "/")):
                    continue
                if not (markdown.parent / target).resolve().exists():
                    errors.append(f"Broken package link: {markdown.relative_to(output_root)} -> {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or (args.root / "output/skills")
    result = build(args.root, output)
    errors = validate(output)
    print(json.dumps({**result, "valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
