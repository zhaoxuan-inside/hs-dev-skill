"""Real subprocess interface, relocated packages and errors remain observable."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/hs-dev.py'


class CliTests(unittest.TestCase):
    def call(self,*args):
        return subprocess.run([sys.executable,str(CLI),*args],text=True,capture_output=True)

    def test_version_and_activity_contract(self):
        result=self.call('--version')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'0.0.2')
        result=self.call('template','--activity','A1','--output','A1.O1')
        self.assertEqual(result.returncode,0,result.stderr)
        record=json.loads(result.stdout)
        self.assertTrue(record['ok'])
        self.assertIn('outputs',record['result'])

    def test_bad_json_does_not_succeed(self):
        result=self.call('source-add','--record','{')
        self.assertNotEqual(result.returncode,0)
        self.assertFalse(json.loads(result.stderr)['ok'])

    def test_question_flags_and_evidence_backed_resolution(self):
        with tempfile.TemporaryDirectory() as folder:
            def run(*args):
                result=self.call('--root',folder,*args)
                self.assertEqual(result.returncode,0,result.stderr)
                return json.loads(result.stdout)['result']
            run('init')
            delivery=run('start','--title','Synthetic generic platform design','--activity','B1',
                         '--scope','fixture-platform')['delivery']
            q=run('question',delivery,'--id','sample','--question','Which later example?',
                  '--reason','Later evaluation needs a sample.','--recommendation','Continue generic design.',
                  '--blocking','false','--affected-work','Later effect evaluation',
                  '--nonblocking-reason','Platform capability mapping does not depend on the sample.')['question']
            self.assertIs(q['blocking'],False)
            self.assertEqual(q['affected_work'],'Later effect evaluation')
            # CLI rejects malformed boolean values rather than treating a string as truthy.
            bad=self.call('--root',folder,'question',delivery,'--blocking','no')
            self.assertNotEqual(bad.returncode,0)
            Path(folder,'correction.md').write_text('Synthetic user decision: no example is required for generic design.')
            run('source-add','--record',json.dumps({'id':'correction','kind':'user','claim_type':'decision',
                'path':'correction.md','scope':'fixture-platform','observed_at':datetime.now(timezone.utc).isoformat(),
                'version':{'not_applicable_reason':'Synthetic correction fixture'}}))
            resolved=run('question-resolve',delivery,'--record',json.dumps({'question_id':'sample',
                'outcome':'invalid-premise','reason':'The synthetic user rejects this prerequisite.',
                'source_ids':['correction']}))['question']
            self.assertEqual(resolved['resolution']['outcome'],'invalid-premise')
            self.assertNotIn('answer',resolved)
            resumed=run('resume',delivery)
            self.assertEqual(resumed['questions']['sample']['question'],'Which later example?')

    def test_missing_source_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            result=self.call('--root',folder,'read','--path','missing.md')
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(json.loads(result.stderr)['ok'])

    def test_package_is_deterministic_and_relocated(self):
        import hashlib
        import zipfile
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'packages'
            command=[sys.executable,str(ROOT/'scripts/build.py'),'--output',str(output)]
            first=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*.zip')}
            self.assertEqual(len(hashes),10)
            second=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(second.returncode,0,second.stderr)
            self.assertEqual(hashes,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob('*.zip')})
            for bundle in output.glob('*.zip'):
                destination=Path(folder)/bundle.stem
                with zipfile.ZipFile(bundle) as archive:
                    self.assertFalse(any('..' in Path(p).parts for p in archive.namelist()))
                    archive.extractall(destination)
                script=next(destination.glob('*/scripts/hs-dev.py'))
                result=subprocess.run([sys.executable,str(script),'template','--activity','G1'],text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertTrue(json.loads(result.stdout)['ok'])


if __name__=='__main__':
    unittest.main()
