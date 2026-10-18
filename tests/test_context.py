"""End-to-end semantic context contracts, including failure and invalidation."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hs_dev.cli import main
from hs_dev.context import ContextProvider, Selection
from hs_dev.context_budget import encode
from hs_dev.indexing.engine import Index, PUBLICATION
from hs_dev.indexing.semantic import units, file_id
from hs_dev.indexing.units import resolve_units
from hs_dev.indexing.service import dispatch, Resident
from hs_dev.workspace import operation
from hs_dev.acceptance import approval_valid
from hs_dev import task_store


class ContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cli('init')

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(['--root', str(self.root), '--output', 'json', *args])
        self.assertEqual(code, 0, err.getvalue())
        return json.loads(out.getvalue())['result']

    def publish(self, files):
        with operation(self.root):
            for path, text in files.items():
                target = self.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            with Index(self.root) as index:
                index.publish()

    def obtain(self, **request):
        return ContextProvider(self.root).obtain(request)

    def selector(self, path, start=None, end=None, required=False):
        return {'path': path, 'scope': {'kind': 'file'} if start is None else {'kind': 'lines', 'start': start, 'end': end}, 'required': required}

    def test_overlap_merges_and_counts_full_serialized_payload(self):
        self.publish({'a.txt': '\n'.join(str(i) for i in range(100))})
        result = self.obtain(selectors=[self.selector('a.txt', 10, 30), self.selector('a.txt', 20, 40)])
        self.assertEqual([(b['start'], b['end']) for b in result['body']], [(10, 40)])
        self.assertEqual(result['usage']['read_bytes'], (self.root / 'a.txt').stat().st_size)
        self.assertEqual(result['usage']['output_bytes'], len(encode(result).encode()))
        self.assertIsNone(result['usage']['tokens'])
        self.assertFalse(result['usage']['token_limit_enforced'])

    def test_full_file_subsumes_ranges(self):
        self.publish({'a.txt': 'one\ntwo\nthree'})
        result = self.obtain(selectors=[self.selector('a.txt'), self.selector('a.txt', 2, 2)])
        self.assertEqual(len(result['body']), 1)
        self.assertEqual(result['body'][0]['text'], 'one\ntwo\nthree')

    def test_symbol_after_line_80_and_preamble(self):
        source = 'import os\n' + '\n' * 100 + '@staticmethod\ndef target():\n    return os.name\n'
        self.publish({'module.py': source})
        result = self.obtain(selectors=[{'path': 'module.py', 'scope': {'kind': 'symbol', 'name': 'target'}, 'required': True}])
        self.assertTrue(result['ok'])
        self.assertEqual(len(result['units']), 2)
        self.assertIn('@staticmethod', '\n'.join(b['text'] for b in result['body']))
        self.assertIn('import os', '\n'.join(b['text'] for b in result['body']))

    def test_symbol_identity_survives_line_shift(self):
        old = units('a.py', 'def f():\n    return 1\n')
        new = units('a.py', '\n\ndef f():\n    return 1\n')
        a = next(u for u in old if u['properties']['unit_kind'] == 'symbol')
        b = next(u for u in new if u['properties']['unit_kind'] == 'symbol')
        self.assertEqual(a['key'], b['key'])
        self.assertEqual(a['properties']['unit_revision'], b['properties']['unit_revision'])

    def test_same_named_methods_have_qualified_identities(self):
        values = units('a.py', 'class A:\n    def run(self): pass\nclass B:\n    def run(self): pass\n')
        keys = {u['key'] for u in values}
        self.assertIn('symbol:a.py:A.run', keys)
        self.assertIn('symbol:a.py:B.run', keys)

    def test_duplicate_symbols_return_ambiguity(self):
        self.publish({'a.py': 'def f(): return 1\ndef f(): return 2\n'})
        result = self.obtain(selectors=[{'path': 'a.py', 'scope': {'kind': 'symbol', 'name': 'f'}}])
        self.assertEqual(result['status'], 'needs_selection')
        self.assertEqual(len(result['missing'][0]['candidates']), 2)
        self.assertFalse(result['body'])

    def test_markdown_hierarchy_fences_and_explicit_id(self):
        self.publish({'a.md': '# API\n## Auth\n<!-- hs-unit: {"id":"api.auth"} -->\nrule\n```md\n# Fake\n```\n## Errors\nerror'})
        result = self.obtain(selectors=[{'unit_id': 'unit:api.auth', 'required': True}])
        self.assertEqual(result['units'][0]['parent_id'], 'file:a.md#section:api')
        self.assertIn('# Fake', result['body'][0]['text'])
        self.assertNotIn('## Errors', result['body'][0]['text'])

    def test_section_revision_tracks_subtree_but_not_sibling_or_line_shift(self):
        first = units('a.md', '# API\n## Auth\nrule\n## Errors\nerror')
        shifted = units('a.md', '# Intro\nnew\n# API\n## Auth\nrule\n## Errors\nerror')
        changed_sibling = units('a.md', '# API\n## Auth\nrule\n## Errors\nnew error')
        auth = lambda values: next(u for u in values if u['key'].endswith('#section:api/auth'))
        self.assertEqual(auth(first)['properties']['unit_revision'], auth(shifted)['properties']['unit_revision'])
        self.assertEqual(auth(first)['properties']['unit_revision'], auth(changed_sibling)['properties']['unit_revision'])
        self.assertNotEqual(next(u for u in first if u['key'].endswith('#section:api'))['properties']['unit_revision'],
                            next(u for u in changed_sibling if u['key'].endswith('#section:api'))['properties']['unit_revision'])

    def test_semantic_resolver_returns_section_revision(self):
        self.publish({'a.md': '# API\n<!-- hs-unit: {"id":"api.auth"} -->\n## Auth\nrule\n## Errors\nerror'})
        unit = self.obtain(selectors=[{'unit_id': 'unit:api.auth', 'required': True}])['units'][0]
        resolved = resolve_units(self.root, ['unit:api.auth'])['unit:api.auth']
        self.assertEqual(resolved['unit_revision'], unit['unit_revision'])

    def test_duplicate_section_title_requires_selection(self):
        self.publish({'a.md': '# Repeated\nfirst\n# Repeated\nsecond'})
        result = self.obtain(selectors=[{'path': 'a.md', 'scope': {'kind': 'section', 'title': 'Repeated'}}])
        self.assertEqual(result['status'], 'needs_selection')

    def test_required_dependencies_are_atomic_and_cycles_rejected(self):
        self.publish({'a.md': '# A\n<!-- hs-unit: {"id":"a", "requires":["unit:b"]} -->\na',
                      'b.md': '# B\n<!-- hs-unit: {"id":"b"} -->\nb'})
        result = self.obtain(selectors=[{'unit_id': 'unit:a', 'required': True}])
        self.assertEqual({u['unit_id'] for u in result['units']}, {'unit:a', 'unit:b'})
        self.publish({'b.md': '# B\n<!-- hs-unit: {"id":"b", "requires":["unit:a"]} -->\nb'})
        result = self.obtain(selectors=[{'unit_id': 'unit:a', 'required': True}])
        self.assertFalse(result['ok'])
        self.assertEqual(result['missing'][0]['details'][0]['reason'], 'dependency_cycle')
        self.assertEqual(result['body'], [])

    def test_missing_dependency_does_not_return_partial_required_body(self):
        self.publish({'a.md': '# A\n<!-- hs-unit: {"id":"a", "requires":["unit:absent"]} -->\na'})
        result = self.obtain(selectors=[{'unit_id': 'unit:a', 'required': True}])
        self.assertEqual(result['status'], 'material_missing')
        self.assertEqual(result['body'], [])

    def test_required_budget_failure_and_optional_deferral(self):
        self.publish({'big.md': 'constraint\n' * 2000, 'small.txt': 'small'})
        request = {'selectors': [self.selector('big.md', required=True), self.selector('small.txt', required=True)], 'budget': {'max_output_bytes': 1500}}
        result = self.obtain(**request)
        self.assertEqual(result['status'], 'insufficient_budget')
        self.assertEqual(result['body'], [])
        self.assertLessEqual(len(encode(result).encode()), 1500)
        request['selectors'][0]['required'] = False
        result = self.obtain(**request)
        self.assertTrue(result['ok'])
        self.assertEqual([b['path'] for b in result['body']], ['small.txt'])
        self.assertGreater(result['coverage']['deferred'], 0)

    def test_delta_change_and_reset(self):
        self.publish({'a.md': '# A\n<!-- hs-unit: {"id":"a"} -->\noriginal'})
        selectors = [{'unit_id': 'unit:a', 'required': True}]
        full = self.obtain(selectors=selectors)
        held = [{k: u[k] for k in ('unit_id', 'unit_revision')} for u in full['units']]
        delta = self.obtain(selectors=selectors, held=held, delivery='delta')
        self.assertEqual(delta['body'], [])
        self.assertEqual(delta['units'][0]['delivery'], 'held')
        self.publish({'a.md': '# A\n<!-- hs-unit: {"id":"a"} -->\nchanged'})
        changed = self.obtain(selectors=selectors, held=held, delivery='delta')
        self.assertIn('changed', changed['body'][0]['text'])
        restored = self.obtain(selectors=selectors, delivery='delta')
        self.assertEqual(restored['body'], changed['body'])
        self.assertEqual(self.obtain(selectors=selectors, held=held, delivery='full')['body'], changed['body'])

    def test_delta_subtracts_overlap_already_held(self):
        self.publish({'a.txt': '\n'.join(str(i) for i in range(100))})
        first = self.obtain(selectors=[self.selector('a.txt', 1, 80)])
        unit = first['units'][0]
        delta = self.obtain(selectors=[self.selector('a.txt', 50, 100)], delivery='delta',
                            held=[{'unit_id': unit['unit_id'], 'unit_revision': unit['unit_revision']}])
        self.assertEqual([(b['start'], b['end']) for b in delta['body']], [(81, 100)])
        self.assertEqual(delta['units'][0]['delivery'], 'body')

    def test_source_drift_even_when_body_is_held(self):
        self.publish({'a.txt': 'original'})
        initial = self.obtain(selectors=[self.selector('a.txt')])
        held = [{k: u[k] for k in ('unit_id', 'unit_revision')} for u in initial['units']]
        (self.root / 'a.txt').write_text('unpublished')
        with self.assertRaises(ValueError):
            self.obtain(selectors=[self.selector('a.txt')], held=held, delivery='delta')

    def test_change_during_assembly_is_rejected(self):
        self.publish({'a.txt': 'original'})
        read = Selection.read
        def drift(session, path):
            result = read(session, path)
            (self.root / 'a.txt').write_text('changed')
            return result
        with patch.object(Selection, 'read', drift), self.assertRaises(ValueError):
            self.obtain(selectors=[self.selector('a.txt')])

    def test_cli_and_service_use_identical_task_budget(self):
        self.publish({'a.txt': 'x' * 3000})
        config = self.root / 'hs-dev-skill/config/config.json'
        config.write_text(json.dumps({'context': {'max_output_bytes': 1500}}))
        request = {'selectors': [self.selector('a.txt', required=True)]}
        cli = self.obtain(**request)
        with Index(self.root) as index:
            service = dispatch(index, Resident(self.root, 100_000), {'action': 'context', 'request': request})
        self.assertEqual(cli, service)
        self.assertEqual(service['status'], 'insufficient_budget')

    def test_private_data_and_invalid_requests(self):
        for selector in (self.selector('hs-dev-skill/recovery/private'), {'unit_id': 'file:history/private.md'}):
            with self.assertRaises(ValueError):
                self.obtain(selectors=[selector])
        for request in ({'paths': []}, {'selectors': [{'path': 'a.txt'}]}, {'delivery': 'unknown'}, {'budget': {'max_output_bytes': 100}}, {'held': [{'unit_id': 'a'}]}):
            with self.assertRaises(ValueError):
                self.obtain(**request)

    def test_no_tokenizer_uses_only_byte_limit(self):
        self.publish({'a.txt': 'hello'})
        result = self.obtain(selectors=[self.selector('a.txt')])
        self.assertEqual(result['usage']['count_kind'], 'utf8_byte_upper_estimate')
        self.assertEqual(result['usage']['estimated_tokens'], result['usage']['output_bytes'])

    def test_token_budget_accounts_for_metadata(self):
        class Counter:
            def encode(self, text, **kwargs):
                return list(text)
        self.publish({'a.txt': 'hello' * 100})
        config = self.root / 'hs-dev-skill/config/config.json'
        config.write_text(json.dumps({'context': {'max_output_tokens': 5000}}))
        with patch('hs_dev.context_budget.tokenizer', return_value=Counter()):
            result = self.obtain(selectors=[self.selector('a.txt', required=True)], budget={'max_output_tokens': 800})
        self.assertEqual(result['status'], 'insufficient_budget')
        self.assertTrue(result['usage']['token_limit_enforced'])
        self.assertLessEqual(len(encode(result)), 800)

    def test_index_rebuild_preserves_business_approval(self):
        task = self.cli('task-start', 'review', '--activities', 'H1', '--mode', 'activity')['task_id']
        for check in task_store.definition('H1')['checks']:
            self.cli('check', task, 'H1', check['id'], 'NA', '--reason', 'not applicable')
        self.cli('approve', task, 'H1', '--actor', 'human', '--confirmation', 'accepted')
        before = task_store.load_task(self.root, task)
        previous = json.loads((self.root / PUBLICATION).read_text())["generation"]
        with operation(self.root):
            with Index(self.root) as index:
                index.connect(create=True).execute("DELETE FROM text_fts")
                index.db.commit()
                index.publish()
        current = json.loads((self.root / PUBLICATION).read_text())["generation"]
        self.assertNotEqual(previous, current)
        self.assertTrue(approval_valid(self.root, before, 'H1'))

    def test_file_includes_external_section_constraints(self):
        self.publish({'a.md': '# A\n<!-- hs-unit: {"id":"a", "requires":["unit:b"]} -->\na',
                      'b.md': '# B\n<!-- hs-unit: {"id":"b"} -->\nb'})
        result = self.obtain(selectors=[self.selector('a.md', required=True)])
        self.assertEqual({b['path'] for b in result['body']}, {'a.md', 'b.md'})

    def test_section_inherits_ancestor_constraints(self):
        self.publish({'a.md': '# Parent\n<!-- hs-unit: {"id":"parent", "requires":["unit:b"]} -->\n## Child\nchild',
                      'b.md': '# B\n<!-- hs-unit: {"id":"b"} -->\nb'})
        result = self.obtain(selectors=[{'path': 'a.md', 'scope': {'kind': 'section', 'title': 'Child'}, 'required': True}])
        self.assertIn('unit:b', {u['unit_id'] for u in result['units']})

    def test_fenced_metadata_is_only_example_text(self):
        parsed = units('a.md', '# Examples\n```html\n<!-- hs-unit: {"id":"example"} -->\n```\n')
        self.assertNotIn('unit:example', {u['key'] for u in parsed})

    def test_read_budget_returns_structured_failure(self):
        self.publish({'a.txt': 'x' * 2000})
        (self.root / 'hs-dev-skill/config/config.json').write_text(json.dumps({'context': {'max_read_bytes': 1000}}))
        result = self.obtain(selectors=[self.selector('a.txt', required=True)])
        self.assertEqual(result['status'], 'insufficient_budget')
        self.assertEqual(result['body'], [])
        optional = self.obtain(selectors=[self.selector('a.txt')])
        self.assertEqual(optional['deferred'][0]['reason'], 'read_budget_exceeded')

    def test_binary_acceptance_material_keeps_raw_revision(self):
        task = self.cli('task-start', 'binary', '--activities', 'H1')['task_id']
        self.publish({'placeholder.txt': 'published'})
        # Register a binary deliverable through an authorized source operation.
        with operation(self.root):
            (self.root / 'figure.png').write_bytes(bytes([137, 80, 78, 71, 255, 0]))
            with Index(self.root) as index:
                index.publish()
        self.cli('acceptance-material', task, 'H1', 'figure.png', '--unit-id', 'file:figure.png', '--title', 'Figure', '--focus', 'Review image')
        card = self.cli('acceptance', task)['materials'][0]
        self.assertEqual(card['unit_id'], 'file:figure.png')
        self.assertEqual(card['unit_revision'], card['source_digest'])

    def test_service_context_uses_one_consistent_read_session(self):
        self.publish({'a.txt': 'payload'})
        original = Index.read_session
        calls = []
        from contextlib import contextmanager
        @contextmanager
        def counted(index):
            calls.append(1)
            with original(index):
                yield index
        request = {'action':'context', 'request': {'selectors':[self.selector('a.txt')]}}
        with patch.object(Index, 'read_session', counted):
            with Index(self.root) as index:
                dispatch(index, Resident(self.root, 100_000), request)
        self.assertEqual(len(calls), 1)

    def test_cli_and_service_return_same_success_payload(self):
        self.publish({'a.txt': 'same payload'})
        request = {'selectors': [self.selector('a.txt')]}
        cli = self.cli('context', json.dumps(request))
        with Index(self.root) as index:
            service = dispatch(index, Resident(self.root, 100_000), {'action': 'context', 'request': request})
        self.assertEqual(cli, service)

    def test_offline_tokenizer_rejects_corrupt_ranks_without_network(self):
        import hashlib
        import os
        import types
        from hs_dev.context_budget import tokenizer
        url = 'https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken'
        data = b'YQ== 0\nYg== 1\n'
        rank_file = self.root / hashlib.sha1(url.encode()).hexdigest()
        rank_file.write_bytes(data)
        namespace = {'url': url, 'expected': hashlib.sha256(data).hexdigest()}
        exec('def cl100k_base():\n    return {"mergeable_ranks": load_tiktoken_bpe(url, expected_hash=expected)}', namespace)
        fake = types.ModuleType('tiktoken')
        fake.Encoding = lambda **kwargs: kwargs
        package = types.ModuleType('tiktoken_ext')
        public = types.ModuleType('tiktoken_ext.openai_public')
        public.cl100k_base = namespace['cl100k_base']
        package.openai_public = public
        modules = {'tiktoken': fake, 'tiktoken_ext': package, 'tiktoken_ext.openai_public': public}
        tokenizer.cache_clear()
        self.addCleanup(tokenizer.cache_clear)
        with patch.dict(os.environ, {'TIKTOKEN_CACHE_DIR': str(self.root)}), patch.dict(sys.modules, modules):
            self.assertEqual(tokenizer('cl100k_base')['mergeable_ranks'], {b'a': 0, b'b': 1})
            tokenizer.cache_clear()
            rank_file.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'integrity'):
                tokenizer('cl100k_base')


if __name__ == '__main__':
    unittest.main()
