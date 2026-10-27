"""Prepare LN's existing static application for hosting."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
if out.exists():
    shutil.rmtree(out)
out.mkdir()
for name in ('index.html', 'styles.css', 'app.js', 'courses.js', 'knowledge-map.js'):
    shutil.copy2(root / name, out / name)
for name in ('assets', 'courses'):
    shutil.copytree(root / name, out / name,
                    ignore=shutil.ignore_patterns('*.md', '__pycache__', 'verification'))
print('Static site prepared in dist/')
