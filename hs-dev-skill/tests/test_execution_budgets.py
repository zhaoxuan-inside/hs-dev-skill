"""Real checks, authorization boundaries and opt-in presentation after a product replay."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

from hsdev.engine import _run_check
from hsdev.store import read
import test_engine

CLI = Path(__file__).resolve().parents[1] / 'scripts/hs-dev.py'


class ExecutionBudgetTests(unittest.TestCase):
    def fixture(self):
        fixture = test_engine.EngineTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def checks(self, count, **extra):
        return [{'id': f'assert-{i}', 'argv': [sys.executable, 'checks.py'],
                 'expected': 'Execute the real zero and signed-operand assertions.', **extra} for i in range(count)]

    def test_more_than_sixteen_real_checks_run_and_keep_failure(self):
        f = self.fixture()
        f.plan(checks=self.checks(17, timeout_seconds=2))
        f.cmd('lock')
        f.cmd('apply', changes={'src/add.py': 'def add(a,b):\n    return a+b\n'})
        value = f.cmd('run')
        self.assertTrue(value['ok'], value)
        self.assertEqual(len(value['results']), 17)
        self.assertTrue(all(r['timeout_seconds'] == 2 and r['elapsed_seconds'] >= 0 for r in value['results']))
        f.cmd('apply', changes={'src/add.py': 'def add(a,b):\n    return a-b\n'})
        failed = f.cmd('run')
        self.assertFalse(failed['ok'])
        self.assertEqual(len(failed['results']), 17)
        self.assertTrue(all(r['exit_code'] != 0 for r in failed['results']))
        self.assertTrue(all((f.root / r['path']).is_file() for r in value['results'] + failed['results']))

    def test_budget_boundaries_and_invalid_types_are_rejected_at_plan(self):
        f = self.fixture()
        f.plan(checks=self.checks(64))
        for checks in (self.checks(65), self.checks(13, timeout_seconds=300),
                       *[self.checks(1, timeout_seconds=t) for t in (False, 0, -1, 301, 1.5, '30')]):
            with self.subTest(count=len(checks), budget=checks[0].get('timeout_seconds')):
                with self.assertRaises(ValueError):
                    f.plan(checks=checks)

    def test_run_cannot_override_authorized_budget(self):
        f = self.fixture()
        checks = self.checks(1, timeout_seconds=2)
        f.plan(checks=checks)
        f.cmd('lock')
        changed = copy.deepcopy(checks)
        changed[0]['timeout_seconds'] = 3
        with self.assertRaisesRegex(ValueError, 'time budgets'):
            f.cmd('run', checks=changed)
        # Legacy argv-only selections use the planned budget, never the caller's default.
        result = f.cmd('run', checks=[checks[0]['argv']])
        self.assertEqual(result['results'][0]['timeout_seconds'], 2)

    def test_real_timeout_retains_output_and_reaps_child(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / 'run.log'
            code = _run_check([sys.executable, '-u', '-c',
                               "import time;print('started real check');time.sleep(5)"],
                              root, log, timeout_seconds=1)
            self.assertEqual(code, 124)
            self.assertIn('started real check', log.read_text())

    def test_overall_deadline_limits_check_and_does_not_start_after_exhaustion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / 'run.log'
            argv = [sys.executable, '-u', '-c', "print('real check');import time;time.sleep(5)"]
            self.assertEqual(_run_check(argv, root, log, timeout_seconds=10,
                                        overall_deadline=time.monotonic()+0.2), 124)
            marker = root/'should-not-exist'
            self.assertEqual(_run_check([sys.executable, '-c', "from pathlib import Path;Path('should-not-exist').touch()"],
                                        root, log, overall_deadline=time.monotonic()-1), 124)
            self.assertFalse(marker.exists())
            self.assertIn('not started', log.read_text())

    def test_identical_apply_preserves_verification_but_not_scope_or_drift_bypass(self):
        f = self.fixture()
        f.locked()
        f.cmd('apply', changes={'src/add.py': 'def add(a,b):\n    return a+b\n'})
        original = f.cmd('run')
        result = f.cmd('apply', changes={'src/add.py': (f.root/'src/add.py').read_text()})
        state = read(f.root/f'hs-dev/execution/deliveries/{f.delivery}.json')
        self.assertEqual(result['changed'], [])
        self.assertEqual(state['verification'], original)
        deleted = f.cmd('apply', changes={f.paths[2]: None})
        self.assertEqual(deleted['changed'], [])
        self.assertEqual(read(f.root/f'hs-dev/execution/deliveries/{f.delivery}.json')['verification'], original)
        with self.assertRaisesRegex(ValueError, 'outside'):
            f.cmd('apply', changes={'checks.py': (f.root/'checks.py').read_text()})
        mixed = f.cmd('apply', changes={'src/add.py': (f.root/'src/add.py').read_text(),
                                       f.paths[2]: 'A real local handoff was added after the check.\n'})
        self.assertEqual(mixed['changed'], [f.paths[2]])
        self.assertIsNone(read(f.root/f'hs-dev/execution/deliveries/{f.delivery}.json')['verification'])
        (f.root/'src/add.py').write_text('external change\n')
        with self.assertRaisesRegex(ValueError, 'outside|changed|drifted'):
            f.cmd('apply', changes={'src/add.py': 'external change\n'})

    def test_compact_cli_keeps_full_run_record_and_failed_exit_status(self):
        f = self.fixture()
        f.locked()
        result = subprocess.run([sys.executable, str(CLI), '--root', str(f.root), '--compact',
                                 'run', f.delivery], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        compact = json.loads(result.stderr)['result']
        self.assertTrue(compact['compact'])
        self.assertFalse(compact['ok'])
        self.assertNotIn('sources', compact)
        self.assertTrue((f.root/compact['state_path']).is_file())
        state = read(f.root/f'hs-dev/execution/deliveries/{f.delivery}.json')
        full = state['verification']
        self.assertIn('src/add.py', full['sources'])
        self.assertIn('argv', full['results'][0])
        self.assertEqual(compact['results'][0]['digest'], full['results'][0]['digest'])
        self.assertTrue((f.root/compact['results'][0]['path']).is_file())
        resumed = subprocess.run([sys.executable, str(CLI), '--root', str(f.root),
                                  '--compact', 'resume', f.delivery], capture_output=True, text=True)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertIn('state_path', json.loads(resumed.stdout)['result'])

    def test_compact_resume_keeps_readiness_blocker_and_detail_location(self):
        f = self.fixture()
        f.ask_fixture_question()
        full = f.cmd('resume')
        resumed = subprocess.run([sys.executable, str(CLI), '--root', str(f.root),
                                  '--compact', 'resume', f.delivery], capture_output=True, text=True)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        summary = json.loads(resumed.stdout)['result']
        self.assertFalse(summary['ready'])
        self.assertEqual(summary['issues'], full['readiness']['issues'])
        self.assertEqual(summary['question_refs'][0]['id'], 'scope-question')
        self.assertNotIn('Continue the existing', summary['next_action'])


if __name__ == '__main__':
    unittest.main()
