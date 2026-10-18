"""Current-version project initialization. Never converts or reads old formats."""

from pathlib import Path
from .storage import CONTROL, atomic, write_json
from .workflow import catalog
from .indexing.engine import Index

DOC_STAGES = ["_01_product_intent", "_02_product_design", "_03_quality_technical_decisions", "_04_architecture",
              "_05_engineering_preparation", "_06_delivery_planning", "_07_implementation_integration", "_08_delivery_feedback"]


def create_document(path, text):
    if not path.exists():
        atomic(path, text)


def initialize(root):
    root = Path(root).resolve()
    publication = root / CONTROL / "state/publication.json"
    if publication.exists():
        raise ValueError("Workspace already initialized; use status and explicit continue/rollback")
    create_document(root / CONTROL / "README.md", "# Skill项目运行数据\n\n配置、任务和恢复数据属于本项目，不能作为全局设计文档。勿手动删除未完成任务状态。\n")
    if not (root / CONTROL / "config/config.json").exists():
        write_json(root / CONTROL / "config/config.json", {"execution": {"mode": "stage"}})
    create_document(root / "hs_dev_docs/README.md", "# 项目文档\n\n从file_index.jsonl定位文件，再从活动content_index.jsonl定位内容。有效空索引表示已检查但没有内容。当前契约与历史记录分离，历史默认不加载。\n")
    foundation = root / "hs_dev_docs/_00_foundation"
    foundation.mkdir(parents=True, exist_ok=True)
    create_document(foundation / "README.md", "# 项目基座\n\n术语、项目说明和权威产物登记。历史材料保留来源，不默认作为当前规则。\n")
    for directory, stage in zip(DOC_STAGES, catalog()["stages"]):
        base = root / "hs_dev_docs" / directory
        create_document(base / "README.md", f"# {stage['id']} {stage['title']}\n\n活动清单和产物在本目录；任务进度、证据与验收记录在hs-dev-skill/task中，已完成后可归档。\n\n验收统一使用 acceptance TASK_ID --scope {stage['id']} --format markdown，展示进度导航、材料卡片和结果摘要；activity模式按活动ID指定范围。\n")
        for number, activity in enumerate(stage["activities"], 1):
            slug = Path(activity["path"]).name.split("_", 1)[1]
            activity_dir = base / f"_{number:02}_{slug}"
            create_document(activity_dir / "README.md", f"# {activity['id']} {activity['title']}\n\n定位：{stage['title']}。输入是相关有效基线，输出是本活动设计或结论。验收以内部活动逐项检查，不以文件存在替代。\n\n使用 acceptance-material 登记待审文档，并由 acceptance 统一展示进度和卡片。勾选或明确回答后记录材料决定；未通过沟通暂缓或继续修复，暂缓不记通过。\n")
            text = "# 验收规则\n\n| ID | 内部活动 | 通过标准 |\n|---|---|---|\n"
            text += "".join(f"| {c['id']} | {c['title']} | {c['criterion']} |\n" for c in activity["checks"])
            create_document(activity_dir / "checklist.md", text)
    with Index(root) as index:
        return index.publish()
