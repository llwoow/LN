"""Prepare LN's existing static application for hosting."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / 'scripts/build-transformer-homework.py')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/build-physics001.py')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/build-highschool.py')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/check-teaching.py')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/build-resource-library.py')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/build-practice.py')], check=True)
out = root / 'dist'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'styles.css', 'app.js', 'courses.js', 'knowledge-map.js', 'publication.js', 'glossary.js', 'highschool-library.js', 'resource-library.js', 'practice.js'):
    shutil.copy2(root / name, out / name)
for name in ('assets', 'courses'):
    shutil.copytree(root / name, out / name,
                    ignore=shutil.ignore_patterns('*.md', '__pycache__', 'verification'))
# Source-tree existence is insufficient: every advertised download must ship.
resources = json.loads((root / 'courses/resources/catalog.json').read_text())
for resource in resources['resources']:
    for download in resource['downloads']:
        if not (out / download['path']).is_file():
            raise ValueError('Download absent from static output: ' + download['path'])
subprocess.run([sys.executable, str(root / 'scripts/build-reference-index.py'), '--output', str(out / 'reference-index.js')], check=True)
subprocess.run([sys.executable, str(root / 'scripts/build-glossary.py'), '--output', str(out / 'glossary-index.js')], check=True)
print('Static site prepared in dist/')
