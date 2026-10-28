"""Prepare LN's existing static application for hosting."""
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'styles.css', 'app.js', 'courses.js', 'knowledge-map.js', 'publication.js'):
    shutil.copy2(root / name, out / name)
subprocess.run([sys.executable, str(root / 'scripts/build-reference-index.py'), '--output', str(out / 'reference-index.js')], check=True)
for name in ('assets', 'courses'):
    shutil.copytree(root / name, out / name,
                    ignore=shutil.ignore_patterns('*.md', '__pycache__', 'verification'))
print('Static site prepared in dist/')
