#!/usr/bin/env python3
"""Compare context delivery against a Git revision in isolated temporary projects.

No checkout, task, source or index in the user's project is changed.
"""
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

PROGRAM = r'''
import contextlib, io, json, sys, tempfile, time
from pathlib import Path
package = Path(sys.argv[1])
sys.path.insert(0, str(package / ('hs-dev-skill/scripts' if (package / 'hs-dev-skill/scripts/hs_dev').is_dir() else 'src')))
from hs_dev.cli import main
from hs_dev.context import ContextProvider
from hs_dev.workspace import operation
from hs_dev.indexing.engine import Index
modern = sys.argv[2] == 'modern'
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(['--root', str(root), '--output', 'json', 'init']) == 0
    code = 'import os\n\ndef work():\n    """benchmarkneedle"""\n' + ''.join('    value_%d = %d\n' % (i, i) for i in range(40)) + '    return os.name\n'
    contract = '# Contract\n' + ''.join('Rule %d: preserve the required invariant.\n' % i for i in range(180))
    with operation(root):
        (root / 'sample.py').write_text(code)
        (root / 'contract.md').write_text(contract)
        with Index(root) as index:
            index.publish()
    provider = ContextProvider(root)
    def stats(results, elapsed):
        return {'payload_bytes': sum(len(json.dumps(r, ensure_ascii=False, separators=(',', ':')).encode()) for r in results),
                'body_bytes': sum(len(b['text'].encode()) for r in results for b in r['body' if modern else 'active']),
                'calls': len(results), 'elapsed_ms': round(elapsed * 1000, 3)}
    started = time.perf_counter()
    result = provider.obtain({'query':'benchmarkneedle'}) if modern else provider.obtain(query='benchmarkneedle')
    assert result['ok']
    overlap = stats([result], time.perf_counter() - started)
    started, results, held = time.perf_counter(), [], []
    for i in range(3):
        if modern:
            result = provider.obtain({'selectors':[{'path':'contract.md','scope':{'kind':'file'},'required':True}], 'delivery':'delta', 'held':held})
            held = [{k:u[k] for k in ('unit_id','unit_revision')} for u in result['units']]
        else:
            result = provider.obtain(required=['contract.md'])
        assert result['ok']
        results.append(result)
    repeated = stats(results, time.perf_counter() - started)
    print(json.dumps({'overlapping_code_search':overlap, 'three_round_contract':repeated}))
'''


def measure(package, mode):
    result = subprocess.run([sys.executable, '-c', PROGRAM, str(package), mode], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=60)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, help='Git revision using the previous context protocol')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    revision = subprocess.check_output(['git', 'rev-parse', '--verify', args.baseline + '^{commit}'], cwd=root, text=True).strip()
    archive = subprocess.check_output(['git', 'archive', revision], cwd=root)
    with tempfile.TemporaryDirectory(prefix='hs-context-baseline-') as directory:
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(directory, filter='data')
        before = measure(Path(directory), 'baseline')
        after = measure(root, 'modern')
    print(json.dumps({'baseline_revision':revision, 'measurement':'canonical payload bytes; no tokenizer',
                      'scope':'synthetic overlap and repeated-delivery fixtures; not task correctness or a general savings rate',
                      'before':before, 'after':after}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
