#!/usr/bin/env python3
"""Validate the catalog, local document references and standalone Skills."""
import re
from pathlib import Path
from hsdev.templates import verify_catalog
from guide import render
import json

root = Path(__file__).resolve().parents[1]
report = verify_catalog()
if not report["ok"] or (report["stages"],report["activities"],report["outputs"]) != (9,38,114):
    raise ValueError("Invalid activity catalog: " + str(report))
expected = render(json.loads((root / "references/catalog.json").read_text()))
if (root / "references/activities.md").read_text() != expected:
    raise ValueError("Activity navigation is stale; run scripts/guide.py")
skills = [root / 'SKILL.md', *sorted((root / 'skills').glob('*/SKILL.md'))]
if len(skills) != 10:
    raise ValueError('Expected main Skill and nine stage Skills')
errors = []
for file in root.rglob('*.md'):
    for link in re.findall(r'\]\(([^)]+)\)',file.read_text()):
        link = link.split('#')[0]
        if not link or '://' in link or link.startswith('mailto:'):
            continue
        if not (file.parent / link).exists():
            errors.append(f'{file.relative_to(root)}: {link}')
if errors:
    raise ValueError('Broken references: '+ '; '.join(errors))
print({**report,'skills':len(skills),'references':'valid'})
