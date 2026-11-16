"""Public knowledge/evidence behavior; no prior runtime is used."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import subprocess
from unittest.mock import patch
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from hsdev.knowledge import locate, read_unit, register_source, reindex, source_state


def utc(delta=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=delta)).isoformat().replace("+00:00", "Z")


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def write(self, path, content):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            file.write_bytes(content)
        else:
            file.write_text(content, encoding="utf-8")
        return file

    def source(self, **changes):
        value = {"id": "evidence-1", "kind": "document", "path": "hs-dev/deliveries/d1/evidence.md",
                 "version": "0.0.2", "observed_at": utc(-60), "scope": "d1", "claim_type": "fact"}
        value.update(changes)
        return value

    def test_reads_do_not_create_missing_index(self):
        self.write("README.md", "# Product\nKnown requirement.")
        self.assertEqual(locate(self.root, "Product")["status"], "missing_index")
        self.assertEqual(read_unit(self.root, "README.md")["status"], "missing_index")
        self.assertFalse((self.root / "hs-dev/execution").exists())

    def test_chinese_words_do_not_match_scattered_characters(self):
        self.write("hs-dev/project/orders.md", "# 取消订单\n\n未发货订单可取消。")
        self.write("noise.md", "# 其他\n\n先取回对象，稍后消耗资源。")
        reindex(self.root)
        result = locate(self.root, "取消")
        self.assertEqual([r["path"] for r in result["results"]], ["hs-dev/project/orders.md"])
        self.assertNotIn("text", result["results"][0])

    def test_code_and_document_relationships_are_searchable_both_ways(self):
        self.write("src/order.py", "def cancel_order(order):\n    return order\n")
        self.write("hs-dev/project/orders.md", "# Order cancellation\n\nImplementation: [cancel](../../src/order.py#L1).")
        reindex(self.root)
        result = locate(self.root, "cancel_order")
        card = next(r for r in result["results"] if r["path"] == "src/order.py")
        self.assertEqual(card["kind"], "code")
        self.assertEqual(card["relations"][0]["source"], "hs-dev/project/orders.md")
        self.assertEqual(card["relations"][0]["target"], "src/order.py")
        selector = card["selector"]
        read = read_unit(self.root, selector["path"], selector["start"], selector["end"], selector["source_digest"])
        self.assertTrue(read["ok"])
        self.assertIn("def cancel_order", read["text"])

    def test_current_project_delivery_and_code_exclude_controls_history_and_drafts(self):
        self.write("hs-dev/project/current.md", "# Current\nsharedneedle")
        self.write("hs-dev/deliveries/d1/decision.md", "# Decision\nsharedneedle")
        self.write("src/app.ts", "export const sharedneedle = 1;")
        for path in ("hs-dev/execution/evidence/log.txt", "history/old.md", "draft/unfinished.md", "superseded/old.md", "node_modules/lib/a.js"):
            self.write(path, "# Excluded\nsharedneedle")
        self.write("hs-dev/project/old.md", "---\nstatus: superseded\n---\n# Old\nsharedneedle")
        self.write("hs-dev/project/future.md", "---\nstatus: draft\n---\n# Future\nsharedneedle")
        self.write(".env", "sharedneedle=secret")
        reindex(self.root)
        paths = {r["path"] for r in locate(self.root, "sharedneedle", limit=30)["results"]}
        self.assertEqual(paths, {"hs-dev/project/current.md", "hs-dev/deliveries/d1/decision.md", "src/app.ts"})

    def test_explicit_missing_path_never_falls_back_to_similar_content(self):
        self.write("src/app.py", "# missing.py\nvalue = 1")
        reindex(self.root)
        value = locate(self.root, "src/missing.py")
        self.assertEqual(value["status"], "not_found")
        self.assertEqual(value["results"], [])

    def test_exact_line_heading_and_unrecognized_ids_do_not_guess(self):
        self.write("a.md", "# Rule\nOriginal.\n## Failure path\nRejected.")
        reindex(self.root)
        card = locate(self.root, "a.md#L3-L4")["results"][0]
        self.assertEqual(card["selector"]["start"], 3)
        self.assertEqual(card["selector"]["end"], 4)
        self.assertEqual(locate(self.root, "a.md#failure-path")["results"][0]["heading"], "Failure path")
        self.assertEqual(locate(self.root, "a.md#unknown-heading")["status"], "not_found")
        self.assertEqual(locate(self.root, "unit:missing-rule")["status"], "not_found")

    def test_incremental_update_and_stale_queries_are_explicit(self):
        file = self.write("hs-dev/project/rules.md", "# Rule\nOriginal.")
        initial = reindex(self.root)
        self.assertEqual(reindex(self.root)["status"], "unchanged")
        file.write_text("# Rule\nChanged.")
        self.assertEqual(locate(self.root, "Rule")["status"], "stale_index")
        update = reindex(self.root)
        self.assertEqual(update["changed_files"], 1)
        self.assertNotEqual(update["generation"], initial["generation"])
        self.assertIn("Changed", read_unit(self.root, "hs-dev/project/rules.md")["text"])

    def test_expected_digest_refuses_new_version_even_after_reindex(self):
        self.write("a.md", "# Rule\nOriginal.")
        reindex(self.root)
        card = locate(self.root, "a.md")["results"][0]
        self.write("a.md", "# Rule\nChanged.")
        reindex(self.root)
        result = read_unit(self.root, "a.md", expected_digest=card["source_digest"])
        self.assertFalse(result["ok"])
        self.assertNotIn("text", result)

    def test_output_budget_is_whole_compact_json_and_large_read_is_not_silently_cut(self):
        for i in range(8):
            self.write(f"docs/a{i}.md", "# Order\n" + "Order cancellation rules. " * 100)
        reindex(self.root)
        value = locate(self.root, "Order", limit=8, max_bytes=1300)
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
        self.assertLessEqual(len(encoded), 1300)
        self.assertEqual(value["usage"]["output_bytes"], len(encoded))
        self.assertEqual(value["status"], "truncated")
        read = read_unit(self.root, "docs/a0.md", max_bytes=512)
        self.assertEqual(read["status"], "over_budget")
        self.assertNotIn("text", read)

    def test_long_document_cannot_fill_all_result_slots(self):
        self.write("large.md", "# API\n" + "\n".join(f"## API {i}\nAPI contract." for i in range(100)))
        self.write("small.md", "# API errors\nAPI failure contract.")
        reindex(self.root)
        paths = [r["path"] for r in locate(self.root, "API")["results"]]
        self.assertEqual(set(paths), {"large.md", "small.md"})
        self.assertEqual(len(paths), 2)

    def test_secret_control_and_parent_paths_are_forbidden(self):
        self.write(".env", "TOKEN=do-not-read")
        self.write("hs-dev/execution/evidence/a.txt", "evidence")
        self.write("hs-dev/execution/control.json", "{}")
        for path in (".env", "../outside.md", "/etc/passwd", "hs-dev/execution/control.json", "hs-dev/execution/evidence/a.txt"):
            with self.assertRaises(ValueError, msg=path):
                read_unit(self.root, path)
        self.write("hs-dev/deliveries/d1/evidence.md", "# Evidence")
        with self.assertRaises(ValueError):
            register_source(self.root, self.source(path="hs-dev/execution/control.json"))

    def test_symlinks_are_not_followed_or_registered(self):
        real = self.write("real.md", "# Real evidence")
        (self.root / "alias.md").symlink_to(real)
        reindex(self.root)
        with self.assertRaises(ValueError):
            read_unit(self.root, "alias.md")
        with self.assertRaises(ValueError):
            register_source(self.root, self.source(path="alias.md"))

    def test_source_registry_does_not_make_index_stale(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "# Evidence\nActual observation.")
        reindex(self.root)
        state = register_source(self.root, self.source())
        self.assertTrue(state["usable"])
        self.assertEqual(state["digest"], hashlib.sha256((self.root / state["path"]).read_bytes()).hexdigest())
        self.assertTrue(locate(self.root, "Evidence")["ok"])
        self.assertNotIn("hs-dev/deliveries/sources.json", [r["path"] for r in locate(self.root, "source", limit=30)["results"]])

    def test_external_sources_require_verified_version_provenance_and_expiry(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "# Snapshot\nCollected official release docs.")
        value = self.source(kind="official", url="https://example.org/spec/v3", publisher="Standards owner",
                            quality_reason="Version 3 primary specification, applicable operation section", valid_until=utc(3600))
        self.assertTrue(register_source(self.root, value)["usable"])
        for version in ("latest", "unknown", "current", "TBD", "the latest release", "当前版本"):
            with self.assertRaises(ValueError, msg=version):
                register_source(self.root, {**value, "version": version})
        for field in ("url", "publisher", "quality_reason", "valid_until"):
            changed = dict(value)
            changed.pop(field)
            with self.assertRaises(ValueError, msg=field):
                register_source(self.root, changed)
        value["url"] = "http://intranet.local/spec/v3"
        self.assertTrue(register_source(self.root, value)["usable"])

    def test_hypothesis_is_preserved_but_never_usable_as_fact(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "# Hypothesis\nNeeds real observation.")
        state = register_source(self.root, self.source(claim_type="hypothesis"))
        self.assertFalse(state["usable"])
        self.assertEqual(state["status"], "hypothesis")
        self.assertEqual(source_state(self.root, "evidence-1")["claim_type"], "hypothesis")

    def test_binary_evidence_is_hash_registered_without_text_search_or_understanding(self):
        self.write("hs-dev/execution/evidence/ui.png", b"\x89PNG\r\n\x1a\n\x00\xffactual-image-bytes")
        state = register_source(self.root, self.source(kind="execution", path="hs-dev/execution/evidence/ui.png",
                      version={"not_applicable_reason": "Screenshot content is identified by its recorded digest and observation time"}))
        self.assertTrue(state["usable"])
        reindex(self.root)
        self.assertEqual(locate(self.root, "actual-image-bytes")["results"], [])
        with self.assertRaises(ValueError):
            read_unit(self.root, "hs-dev/execution/evidence/ui.png")

    def test_expired_and_drifted_sources_remain_visible_but_unusable(self):
        file = self.write("hs-dev/deliveries/d1/evidence.md", "# Snapshot\nVersion 1.")
        expired = self.source(kind="private", publisher="Authorized owner", quality_reason="Collected directly from authorized owner",
                              observed_at=utc(-7200), valid_until=utc(-3600))
        value = register_source(self.root, expired)
        self.assertFalse(value["usable"])
        self.assertEqual(value["status"], "expired")
        file.write_text("# Snapshot\nChanged content.")
        self.assertTrue(any("drifted" in issue for issue in source_state(self.root, "evidence-1")["issues"]))
        self.assertTrue(any("expired" in issue for issue in source_state(self.root, "evidence-1")["issues"]))

    def test_future_timestamps_and_invalid_utc_are_rejected(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "Actual snapshot")
        for timestamp in (utc(3600), "2020-01-01T00:00:00", "2020-01-01T00:00:00+08:00"):
            with self.assertRaises(ValueError):
                register_source(self.root, self.source(observed_at=timestamp))

    def test_source_refresh_preserves_history_and_changes_record_fingerprint(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "Actual snapshot")
        before = register_source(self.root, self.source(claim_type="hypothesis"))
        after = register_source(self.root, self.source(claim_type="requirement", scope="*"))
        self.assertEqual(before["digest"], after["digest"])
        self.assertNotEqual(before["record_digest"], after["record_digest"])
        self.assertTrue(after["usable"])
        registry = json.loads((self.root / "hs-dev/deliveries/sources.json").read_text())
        self.assertEqual(registry["history"][0]["claim_type"], "hypothesis")

    def test_private_key_disguised_as_markdown_is_rejected(self):
        self.write("hs-dev/deliveries/d1/evidence.md", "-----BEGIN RSA PRIVATE KEY-----\nsecret\n-----END RSA PRIVATE KEY-----")
        with self.assertRaises(ValueError):
            register_source(self.root, self.source())

    def test_unsupported_and_oversized_sources_are_not_claimed_indexed(self):
        self.write("media.png", b"not searchable")
        self.write("too-large.md", "x" * 2_000_001)
        result = reindex(self.root)
        self.assertEqual(result["indexed_files"], 0)
        self.assertEqual(result["skipped"], [{"path": "too-large.md", "reason": "oversized"}])

    def test_cross_process_source_writer_conflict_is_explicit_and_retry_preserves_both(self):
        from hsdev.knowledge import _mutation
        self.write("hs-dev/deliveries/d1/evidence.md", "Actual snapshot")
        first = self.source(id="first")
        second = self.source(id="second")
        register_source(self.root, first)
        script = "from hsdev.knowledge import register_source; import json,sys; register_source(sys.argv[1],json.loads(sys.argv[2]))"
        environment = dict(__import__("os").environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "scripts"), PYTHONDONTWRITEBYTECODE="1")
        with _mutation(self.root):
            result = subprocess.run([sys.executable, "-c", script, str(self.root), json.dumps(second)],
                                    capture_output=True, text=True, env=environment, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Knowledge mutation is busy", result.stderr)
        retry = subprocess.run([sys.executable, "-c", script, str(self.root), json.dumps(second)],
                               capture_output=True, text=True, env=environment, timeout=20)
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertTrue(source_state(self.root, "first")["usable"])
        self.assertTrue(source_state(self.root, "second")["usable"])

    def test_source_registration_and_reindex_share_one_mutation_lock(self):
        from hsdev.knowledge import _mutation
        self.write("a.md", "# Source")
        with _mutation(self.root):
            with self.assertRaisesRegex(ValueError, "busy"):
                reindex(self.root)
        self.assertTrue(reindex(self.root)["ok"])

    def test_unchanged_queries_reuse_verified_signatures_instead_of_reading_all_bodies(self):
        self.write("a.md", "# Rule\nKnown content.")
        reindex(self.root)
        from hsdev import knowledge
        original = knowledge._stable_bytes
        calls = []
        def track(file, capture=None):
            calls.append(file.name)
            return original(file, capture)
        with patch.object(knowledge, "_stable_bytes", side_effect=track):
            self.assertTrue(locate(self.root, "Rule")["ok"])
        self.assertEqual(calls, [])
        # Reading an actual selected unit still hashes its real contents.
        with patch.object(knowledge, "_stable_bytes", side_effect=track):
            self.assertTrue(read_unit(self.root, "a.md")["ok"])
        self.assertIn("a.md", calls)

    def test_corrupt_index_is_explicit_and_reindex_can_rebuild_it(self):
        self.write("a.md", "# Rule\nCurrent.")
        reindex(self.root)
        (self.root / "hs-dev/execution/index.sqlite").write_bytes(b"broken")
        self.assertEqual(locate(self.root, "Rule")["status"], "invalid_index")
        self.assertTrue(reindex(self.root)["ok"])
        self.assertTrue(locate(self.root, "Rule")["ok"])



class EvidenceInterfaceTests(unittest.TestCase):
    def test_single_source_and_evidence_reader_are_bounded_and_control_safe(self):
        from hsdev.knowledge import register_source, get_source, read_evidence, reindex, locate
        from hsdev.store import write, hash_file
        from datetime import datetime, timezone, timedelta
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            evidence='hs-dev/execution/evidence/demo/run.log'
            write(root/evidence,'actual fixture assertion result\n')
            register_source(root,{'id':'run-result','kind':'execution','path':evidence,'version':{'not_applicable_reason':'Command log is identified by digest'},'observed_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),'scope':'demo','claim_type':'fact'})
            self.assertTrue(get_source(root,'run-result')['ok'])
            self.assertEqual(read_evidence(root,evidence,hash_file(root/evidence))['text'],'actual fixture assertion result\n')
            with self.assertRaises(ValueError):read_evidence(root,'hs-dev/execution/workspace.json','anything')
            with self.assertRaises(ValueError):read_evidence(root,evidence,'stale')
            self.assertFalse(get_source(root,'missing-source')['ok'])

    def test_exact_registered_source_locates_its_document(self):
        from hsdev.knowledge import register_source,reindex,locate
        from hsdev.store import write
        from datetime import datetime,timezone,timedelta
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            write(root/'hs-dev/project/rule.md','# Exact rule\nA declared rule for this fixture.\n')
            register_source(root,{'id':'rule-identity','kind':'document','path':'hs-dev/project/rule.md','version':'1.0.0','observed_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat(),'scope':'project','claim_type':'requirement'})
            reindex(root)
            result=locate(root,'source:rule-identity')
            self.assertEqual(result['results'][0]['path'],'hs-dev/project/rule.md')
            self.assertEqual(result['results'][0]['match'],'source-id')

if __name__ == "__main__":
    unittest.main()
