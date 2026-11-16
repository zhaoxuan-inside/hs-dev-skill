#!/usr/bin/env python3
"""Build reproducible installable main and stage Skills without legacy code."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
from hsdev import __version__

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True)
args = parser.parse_args()
output = Path(args.output).resolve()
if output == root or root in output.parents:
    raise ValueError('Build output must be outside the source Skill')
output.mkdir(parents=True,exist_ok=True)
artifacts = []
for name, skill in [('hs-dev-skill',root / 'SKILL.md'), *[(p.parent.name,p) for p in sorted((root / 'skills').glob('*/SKILL.md'))]]:
    files = {'SKILL.md':skill.read_bytes()}
    if (root / 'LICENSE').is_file():
        files['LICENSE'] = (root / 'LICENSE').read_bytes()
    if name == 'hs-dev-skill':
        files['README.md'] = (root / 'README.md').read_bytes()
        for p in (root / 'skills').rglob('*.md'):
            files[p.relative_to(root).as_posix()] = p.read_bytes()
    else:
        # Installed stage Skills contain their complete runtime and shared references.
        files['SKILL.md'] = files['SKILL.md'].replace(b'../../references/',b'references/').replace(b'../../SKILL.md',b'references/main-skill.md')
        files['references/main-skill.md'] = (root / 'SKILL.md').read_bytes().replace(b'(references/',b'(').replace(b'(skills/',b'(../skills/')
    for folder in ['scripts','references','skills']:
        for p in sorted((root / folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                files[p.relative_to(root).as_posix()] = p.read_bytes()
    target = output / f'{name}-{__version__}.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, data in sorted(files.items()):
            info = zipfile.ZipInfo(name+'/'+relative,date_time=(2026,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info,data)
    artifacts.append({'name':name,'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(output / 'manifest.json').write_text(json.dumps({'version':__version__,'artifacts':artifacts},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'version':__version__,'artifacts':len(artifacts),'output':str(output)}))
