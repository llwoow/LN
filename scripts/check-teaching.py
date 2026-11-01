"""Structural checks only; never certify accuracy or teaching quality from a template."""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[1]
a=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
for path in (ROOT/'courses').glob('*/manifest.js'):
 course=a(path)
 for section in course['sections']:
  payload=a(ROOT/section['src']);body=payload.get('html','')
  if 'LN-UNDERSTANDING:BEGIN' in body or 'data-learning-standard="understanding-v1"' in body:
   raise ValueError('Removed template was reintroduced: '+section['id'])
  if not body and section['kind']=='html':raise ValueError('Missing reading material: '+section['id'])
print('Reading files exist and removed templates are absent; content quality requires actual review.')
