"""Rebuild-from-docs: a fresh workspace carrying ONLY the document system must be
able to restore an equivalent-behavior project.

Project A is built doc-first. Workspace B receives nothing but A's document
system (behavior kernels, blueprint, declared gate). The rebuilder never sees
A's source: the implementation is rewritten strictly from the kernel specs —
different code structure, same documented behavior, error text copied verbatim
from the contract. The same gate (same cases) decides whether the rebuild is
equivalent. A drift in even the error message must fail the rebuild.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.cli import main
from hs_dev import task_store as store

DOC = """# 便笺：文档即规格

## 创建便笺

:::contract
{"id": "feature:note.create", "title": "创建便笺"}
:::

:::contract
{"id": "behavior:note.create", "feature": "feature:note.create",
 "trigger": "提交非空标题",
 "output": {"ok": "返回含 title 的便笺对象"},
 "postcondition": "便笺可被后续查询",
 "covered_by": ["case:note.create.ok", "case:note.create.reject"],
 "implemented_by": ["symbol:app/service.py:create_note"]}
:::

:::contract
{"id": "behavior:note.create.reject", "feature": "feature:note.create",
 "trigger": "提交空标题",
 "output": {"error": "ValueError(empty title)"},
 "covered_by": ["case:note.create.reject"],
 "implemented_by": ["symbol:app/service.py:create_note"]}
:::

叙述外壳不参与校验。
"""

BLUEPRINT = {"schema_version": 1,
             "features": [{"id": "feature:note.create", "title": "创建便笺"}],
             "scenarios": [
                 {"id": "scenario:note.create.normal", "feature": "feature:note.create", "title": "正常创建", "kind": "normal"},
                 {"id": "scenario:note.create.error", "feature": "feature:note.create", "title": "空标题被拒", "kind": "error"}],
             "cases": [
                 {"id": "case:note.create.ok", "scenario": "scenario:note.create.normal", "evidence": "test_note.py"},
                 {"id": "case:note.create.reject", "scenario": "scenario:note.create.error", "evidence": "test_note.py"}]}

GATES = {"schema_version": 1, "entries": [
    {"id": "unit", "argv": ["python3", "-m", "pytest", "test_note.py", "-q",
                            "--junitxml=hs-dev-skill/reports/junit.xml"],
     "report": {"format": "junit", "path": "hs-dev-skill/reports/junit.xml"}}]}

# 工程 A 的原始实现（仅用于建设 A；复原者不可见）。
ORIGINAL_CODE = ("def create_note(title):\n"
                 "    if not title:\n        raise ValueError('empty title')\n"
                 "    return {'title': title}\n")

# 复原实现：从未见过 ORIGINAL_CODE，仅依据内核规格重写——
# 结构不同（显式字典构造），行为与错误文本逐字来自文档。
REBUILT_CODE = ("def create_note(title):\n"
                "    if not title:\n"
                "        raise ValueError('empty title')\n"
                "    note = dict()\n"
                "    note['title'] = title\n"
                "    return note\n")
# 复原测试：断言取自内核 output 规格；错误文本按契约 match。
REBUILT_TESTS = ("import pytest\n"
                 "from app.service import create_note\n\n"
                 "def test_ok():\n"
                 "    assert create_note('a') == {'title': 'a'}\n\n"
                 "def test_reject():\n"
                 "    with pytest.raises(ValueError, match='empty title'):\n"
                 "        create_note('')\n")


def build_call(root):
    def call(*args, success=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(root), "--output", "json", *args])
        payload = None
        if out.getvalue().strip():
            try:
                payload = json.loads(out.getvalue())["result"]
            except (json.JSONDecodeError, KeyError):
                payload = None
        if success:
            assert code == 0, err.getvalue()
            return payload
        assert code == 1
        return payload if payload is not None else err.getvalue()
    return call


class RebuildFromDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_rebuild_restores_equivalent_behavior_from_docs_only(self):
        a, b = self.base / "project-a", self.base / "rebuild-b"
        a.mkdir()
        call = build_call(a)

        # -- 工程 A：建立文档体系与实现（单任务一次提交，作为文档体系的来源） --
        call("init")
        task = call("task-start", "建设", "--activities", "H1", "--mode", "mute")["task_id"]
        call("commit", task, "--activity", "H1", "--changes", json.dumps({
            "docs/notes.md": DOC,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT),
            "hs_dev_docs/foundation/gates.json": json.dumps(GATES),
            "app/__init__.py": "", "app/service.py": ORIGINAL_CODE,
            "test_note.py": REBUILT_TESTS}), "--checks", json.dumps([["gate:unit"]]))
        for check in store.definition("H1")["checks"]:
            call("check", task, "H1", check["id"], "NA", "--reason", "建设")
        done = call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")

        # -- 工程 B：只携带文档体系内容，从零复原 --
        b.mkdir()
        call_b = build_call(b)
        call_b("init")
        task = call_b("task-start", "按文档复原", "--activities", "H1", "--mode", "mute")["task_id"]

        # 复原前事实：只发布文档（声称的实现不存在）会被一致性门禁拦下。
        error = call_b("commit", task, "--activity", "H1", "--changes", json.dumps({
            "docs/notes.md": DOC,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT)}),
            "--checks", json.dumps([["true"]]), success=False)  # 门禁尚未声明，自由命令引导态
        self.assertIn("unknown code unit", str(error), error)
        stuck = [json.loads(p.read_text(encoding="utf-8"))
                 for p in sorted((b / "hs-dev-skill/recovery/operations").glob("*.json"))
                 if json.loads(p.read_text(encoding="utf-8"))["state"] in {"PREPARED", "INTERRUPTED"}]
        call_b("rollback", stuck[-1]["operation_id"], "--decision", "rollback")

        # 复原偏离：错误文本与契约不符 -> 同一门禁拦下这次复原。
        drifted = REBUILT_CODE.replace("'empty title'", "'invalid title'")
        error = call_b("commit", task, "--activity", "H1", "--changes", json.dumps({
            "docs/notes.md": DOC,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT),
            "hs_dev_docs/foundation/gates.json": json.dumps(GATES),
            "app/__init__.py": "", "app/service.py": drifted,
            "test_note.py": REBUILT_TESTS}), "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("Behavior verification failed", str(error))
        stuck = [json.loads(p.read_text(encoding="utf-8"))
                 for p in sorted((b / "hs-dev-skill/recovery/operations").glob("*.json"))
                 if json.loads(p.read_text(encoding="utf-8"))["state"] in {"PREPARED", "INTERRUPTED"}]
        call_b("rollback", stuck[-1]["operation_id"], "--decision", "rollback")

        # 复原：实现结构不同、行为与错误文本逐字符合文档，与文档同批发布。
        call_b("commit", task, "--activity", "H1", "--changes", json.dumps({
            "docs/notes.md": DOC,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT),
            "hs_dev_docs/foundation/gates.json": json.dumps(GATES),
            "app/__init__.py": "", "app/service.py": REBUILT_CODE,
            "test_note.py": REBUILT_TESTS}), "--checks", json.dumps([["gate:unit"]]))
        for check in store.definition("H1")["checks"]:
            call_b("check", task, "H1", check["id"], "NA", "--reason", "按文档复原")
        done = call_b("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")

        evidence = json.loads((b / done["verification"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["reports"][0]["cases"], 2)
        self.assertEqual(evidence["reports"][0]["failures"], [])
        self.assertTrue(call_b("kernel")["ok"])
        self.assertTrue(call_b("blueprint")["ok"])
        self.assertTrue(call_b("status")["ok"])
        # 复原产物与原实现不同源码、同行为。
        self.assertNotEqual((b / "app/service.py").read_text(), (a / "app/service.py").read_text())
        self.assertIn("dict()", (b / "app/service.py").read_text())

        # -- 显式差分对比：同一组输入分别驱动原项目与复原项目的实现 --
        # 覆盖文档规格内输入（正常、空标题）与盲区输入（仅空白标题）：前者由文档
        # 保证一致；若复原者在盲区上做出不同实现选择，差分会在此暴露分歧。
        import importlib.util

        def load(path, name):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        original = load(a / "app/service.py", "svc_original")
        rebuilt = load(b / "app/service.py", "svc_rebuilt")
        for title in ("a", "便笺", ""):
            outcomes = []
            for module in (original, rebuilt):
                try:
                    outcomes.append(("ok", module.create_note(title)))
                except ValueError as error:
                    outcomes.append(("error", str(error)))
            self.assertEqual(outcomes[0], outcomes[1], f"输入 {title!r} 行为分叉: {outcomes}")
        # 盲区输入不构成等价承诺，但当前复原忠实按文档实现，差分一致。
        blind = []
        for module in (original, rebuilt):
            try:
                blind.append(("ok", module.create_note("  ")))
            except ValueError as error:
                blind.append(("error", str(error)))
        self.assertEqual(blind[0], blind[1])


if __name__ == "__main__":
    unittest.main()
