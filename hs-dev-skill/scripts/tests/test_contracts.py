"""Contract registry integrity and the E1/E2 reconciliation gate."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.cli import main
from hs_dev import task_store as store

SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
          "properties": {"user": {"type": "string"}}}
OPENAPI = {"openapi": "3.1.0", "info": {"title": "API", "version": "1"}, "paths": {"/login": {"post": {}}}}


def registry(contracts):
    return {"schema_version": 1, "contracts": list(contracts)}


class ContractRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.call("init")

    def call(self, *args, success=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.root), "--output", "json", *args])
        payload = None
        if out.getvalue().strip():
            try:
                payload = json.loads(out.getvalue())["result"]
            except (json.JSONDecodeError, KeyError):
                payload = None
        if success:
            self.assertEqual(code, 0, err.getvalue())
            return payload
        self.assertEqual(code, 1)
        return payload if payload is not None else err.getvalue()

    def test_empty_registry_passes(self):
        result = self.call("contracts")
        self.assertTrue(result["registry"])
        self.assertTrue(result["ok"], result["errors"])

    def test_registered_contract_must_exist_and_parse(self):
        path = self.root / "hs_dev_docs/foundation/contracts.json"
        path.write_text(json.dumps(registry([
            {"id": "K1", "kind": "data", "format": "json-schema", "path": "schemas/login.json"}])), encoding="utf-8")
        result = self.call("contracts", success=False)
        self.assertIn("Contract file missing: K1", result["errors"])
        (self.root / "schemas").mkdir()
        (self.root / "schemas/login.json").write_text("{broken", encoding="utf-8")
        result = self.call("contracts", success=False)
        self.assertTrue(any("not valid JSON" in e for e in result["errors"]))
        (self.root / "schemas/login.json").write_text(json.dumps(SCHEMA), encoding="utf-8")
        self.assertTrue(self.call("contracts")["ok"])

    def test_structure_rules_per_format(self):
        (self.root / "schemas").mkdir()
        rows = [
            {"id": "K1", "kind": "interface", "format": "openapi", "path": "schemas/api.json"},
            {"id": "K2", "kind": "interface", "format": "openapi", "path": "schemas/bad_api.json"},
            {"id": "K3", "kind": "data", "format": "json-schema", "path": "schemas/ok.json"},
            {"id": "K4", "kind": "data", "format": "json-schema", "path": "schemas/bad.json"},
            {"id": "K5", "kind": "data", "format": "proto", "path": "schemas/x.json"},
        ]
        (self.root / "schemas/api.json").write_text(json.dumps(OPENAPI), encoding="utf-8")
        (self.root / "schemas/bad_api.json").write_text(json.dumps({"openapi": 3}), encoding="utf-8")
        (self.root / "schemas/ok.json").write_text(json.dumps({"type": "object", "properties": {}}), encoding="utf-8")
        (self.root / "schemas/bad.json").write_text(json.dumps({"foo": 1}), encoding="utf-8")
        (self.root / "hs_dev_docs/foundation/contracts.json").write_text(json.dumps(registry(rows)), encoding="utf-8")
        errors = self.call("contracts", success=False)["errors"]
        self.assertTrue(any("not a valid OpenAPI" in e for e in errors))
        self.assertTrue(any("not a recognizable JSON Schema" in e for e in errors))
        self.assertTrue(any("Unknown contract format: K5" in e for e in errors))

    def test_derive_binding_requires_registered_contract(self):
        task = self.call("task-start", "契约文档", "--activities", "H1", "--mode", "mute")["task_id"]
        doc = ('<!-- hs: {"id": "api-doc", "relations": [{"source": "api-doc", "target": "K1", "kind": "derives"}]} -->\n'
               "# 接口说明\n\n派生自 K1。\n")
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps({
            "hs_dev_docs/foundation/contracts.json": json.dumps(registry([
                {"id": "K1", "kind": "interface", "format": "openapi", "path": "schemas/api.json"}])),
            "schemas/api.json": json.dumps(OPENAPI),
            "hs_dev_docs/api.md": doc}), "--checks", json.dumps([["true"]]))
        result = self.call("contracts")
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["counts"]["deriving_docs"], 1)
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/api.md": doc.replace('"K1"', '"K9"')}), "--checks", json.dumps([["true"]]))
        errors = self.call("contracts", success=False)["errors"]
        self.assertTrue(any("derives from unknown or superseded contract: K9" in e for e in errors))

    def test_e1_gate_blocks_broken_registry_and_finish_rechecks(self):
        task = self.call("task-start", "契约设计", "--activities", "E1,E2", "--mode", "mute")["task_id"]
        for consumer, producers in (("E1", ("D1", "D2")), ("E2", ("B2", "D2"))):
            for producer in producers:
                self.call("dependency-bind", task, consumer, producer,
                          "file:hs_dev_docs/README.md", "--actor", "model", "--confirmation", "模型：绑定基线")
        broken = registry([{"id": "K1", "kind": "data", "format": "json-schema", "path": "schemas/missing.json"}])
        self.call("commit", task, "--activity", "E1", "--changes", json.dumps(
            {"hs_dev_docs/foundation/contracts.json": json.dumps(broken)}), "--checks", json.dumps([["true"]]))
        error = self.call("check", task, "E1", "E1.1", "NA", "--reason", "n/a", success=False)
        self.assertIn("Contract reconciliation failed", error)

        good = registry([{"id": "K1", "kind": "data", "format": "json-schema", "path": "schemas/login.json"}])
        self.call("commit", task, "--activity", "E1", "--changes", json.dumps({
            "hs_dev_docs/foundation/contracts.json": json.dumps(good),
            "schemas/login.json": json.dumps(SCHEMA)}), "--checks", json.dumps([["true"]]))
        for activity in ("E1", "E2"):
            for check in store.definition(activity)["checks"]:
                self.call("check", task, activity, check["id"], "NA", "--reason", "n/a")
        self.call("complete", task, "--checks", json.dumps([["true"]]))
        self.assertEqual(self.call("status")["ok"], True)


if __name__ == "__main__":
    unittest.main()
