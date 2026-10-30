"""Block publishing any registered course that omits the project's teaching contract."""
from pathlib import Path
import runpy
from learning_content import load

ROOT = Path(__file__).resolve().parents[1]
assignment = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
total = 0
for path in (ROOT/'courses').glob('*/manifest.js'):
    course = assignment(path)
    expected = [s['id'].upper() if course.get('level')=='highschool' else s['id'] for s in course['sections']]
    load(path.parent/'understanding.json', expected)
    total += len(expected)
print('Teaching contract validated for '+str(total)+' registered reading units; explanation quality still requires review.')
