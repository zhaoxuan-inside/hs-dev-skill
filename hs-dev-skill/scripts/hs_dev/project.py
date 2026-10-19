"""Current-version project initialization. Never converts or reads old formats."""

from pathlib import Path
from .storage import CONTROL, atomic, write_json
from .indexing.engine import Index

def create_document(path, text):
    if not path.exists():
        atomic(path, text)


def initialize(root):
    root = Path(root).resolve()
    publication = root / CONTROL / "index/publication.json"
    if (root / CONTROL / "state/publication.json").exists() or (root / CONTROL / "task").exists():
        raise ValueError("Old runtime format detected; explicit migration required")
    if publication.exists():
        raise ValueError("Workspace already initialized; use status and explicit continue/rollback")
    create_document(root / CONTROL / "README.md", "# Skill项目运行数据\n\n配置、任务和恢复数据属于本项目，不能作为全局设计文档。勿手动删除未完成任务状态。\n")
    if not (root / CONTROL / "config/config.json").exists():
        write_json(root / CONTROL / "config/config.json", {"execution": {"mode": "stage"}})
    create_document(root / "hs_dev_docs/README.md", "# 项目文档\n\n本目录保存当前有效项目文档，按实际活动创建。通过 Skill 的 context/search 定位内容，索引独立存放于运行目录；恢复历史不提供给模型。\n")
    foundation = root / "hs_dev_docs/foundation"
    foundation.mkdir(parents=True, exist_ok=True)
    create_document(foundation / "README.md", "# 项目基座\n\n术语、项目说明和权威产物登记。历史材料保留来源，不默认作为当前规则。\n")
    with Index(root) as index:
        return index.publish()
