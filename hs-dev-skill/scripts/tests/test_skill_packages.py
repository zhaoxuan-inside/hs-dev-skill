import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_skill_packages import build, validate
from hs_dev.bundle import validate as validate_bundle


ROOT = Path(__file__).resolve().parents[3]


def test_builds_self_contained_packages_for_all_skills(tmp_path):
    output = tmp_path / "skills"
    result = build(ROOT, output)

    assert result["packages"] == 32
    assert result["children"] == 31
    assert validate(output) == []


def test_child_packages_include_shared_contracts_and_keep_skill_hierarchy(tmp_path):
    output = tmp_path / "skills"
    build(ROOT, output)
    catalog = json.loads((output / "catalog.json").read_text(encoding="utf-8"))
    children = [item for item in catalog["skills"] if item["type"] != "orchestrator"]

    assert children
    assert all(item["parent"] == "hs-dev-skill" and item["independent"] for item in children)
    for item in children:
        package = output / item["path"]
        assert (package / "SKILL.md").is_file()
        assert (package / "references/core/execution.md").is_file()
        assert (package / "references/core/acceptance.md").is_file()

    orchestrator = output / "hs-dev-skill"
    assert (orchestrator / "references").is_dir()
    assert (orchestrator / "scripts/hs_dev.py").is_file()
    assert not (orchestrator / "hs-dev-skill").exists()
    assert validate_bundle(orchestrator)["ok"]
    assert not list(orchestrator.glob("references/skills/*/*/SKILL.md"))
    route_index = (orchestrator / "references/skills/skills.idx").read_text()
    assert "hs-dev-implementation" in route_index

    # A package may contain the mandatory shared protocols without loading unrelated workflow assets.
    web = output / "hs-dev-frontend-web"
    assert (web / "references/core/execution.md").is_file()
    assert (web / "references/core/acceptance.md").is_file()
    assert not (web / "references/workflow").exists()

    manifest = json.loads((ROOT / "hs-dev-skill/skill-packages.json").read_text(encoding="utf-8"))
    assert manifest["resource_policy"]["include_linked_resources"] is True
    assert manifest["resource_policy"]["include_mandatory_shared_resources"] is True

    project = tmp_path / "project"
    project.mkdir()
    entry = orchestrator / "scripts/hs_dev.py"
    for command in ("init", "status"):
        result = subprocess.run(
            [sys.executable, str(entry), "--root", str(project), "--output", "json", command],
            cwd=tmp_path, capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, result.stderr


def test_selected_workflow_resources_are_bundled_without_all_workflow_material(tmp_path):
    output = tmp_path / "skills"
    build(ROOT, output)
    implementation = output / "hs-dev-implementation/references/workflow"

    assert (implementation / "g_implementation_integration/g1_slice_implementation/checklist.md").is_file()
    assert (implementation / "examples/g_implementation_frontend_web.md").is_file()
    assert not (implementation / "a_product_intent").exists()


def test_catalog_indexes_cover_every_directory_and_direct_child():
    import re
    catalogs = ROOT / "hs-dev-skill/share/catalogs"
    directories = [path for path in catalogs.rglob("*") if path.is_dir()]
    for directory in directories:
        index = directory / f"{directory.name}.idx"
        assert index.is_file(), f"Missing index: {index.relative_to(ROOT)}"
        targets = set(re.findall(r"\]\(([^)]+)\)", index.read_text(encoding="utf-8")))
        expected = {
            f"{child.name}/{child.name}.idx" if child.is_dir() else child.name
            for child in directory.iterdir() if child != index
        }
        assert expected <= targets, f"Index omits children in {index.relative_to(ROOT)}"
        assert all((directory / target).exists() for target in targets), f"Broken link in {index.relative_to(ROOT)}"


def test_catalog_indexes_are_packaged_when_referenced(tmp_path):
    output = tmp_path / "skills"
    build(ROOT, output)
    assert (output / "hs-dev-skill/references/catalogs/catalogs.idx").is_file()
    assert (output / "hs-dev-product/references/catalogs/features/features.idx").is_file()
    assert (output / "hs-dev-framework-backend/references/catalogs/practices/practices.idx").is_file()


def test_skill_loading_matrix_references_only_published_skill_names():
    manifest = json.loads((ROOT / "hs-dev-skill/skill-packages.json").read_text(encoding="utf-8"))
    published = {manifest["main"]["name"]}
    for category in manifest["categories"].values():
        published.update(category)
    matrix = (ROOT / "hs-dev-docs/skill-loading.md").read_text(encoding="utf-8")
    import re
    named_skills = set(re.findall(r"`(hs-dev-[a-z0-9-]+)`", matrix))
    assert named_skills
    assert named_skills <= published
    assert "常见任务路由矩阵" in matrix
    assert "不表示宿主会把它们全部加入当前对话" in matrix
