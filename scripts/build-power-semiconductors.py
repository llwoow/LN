"""Render the power semiconductor course with LN's local math renderer."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / 'courses/power-semiconductors'
LESSONS = COURSE / 'lessons'
LESSONS.mkdir(exist_ok=True)
SOURCES = ['foundations.html', 'content.html', 'devices.html', 'technology.html']
MATH = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.S)

source = '\n'.join((COURSE / name).read_text(encoding='utf-8') for name in SOURCES)
blocks = re.findall(r'<section data-lesson="([a-z0-9-]+)">(.*?)</section>', source, re.S)
sections = dict(blocks)
manifest = json.loads((COURSE / 'manifest.js').read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
order = [section['id'] for section in manifest['sections']]
if set(order) != set(sections) or len(order) != len(sections) or len(blocks) != len(sections):
    raise ValueError('Lesson source and manifest IDs differ or are duplicated')

jobs = [
    {'tex': match[1] or match[2], 'display': match[1] is not None}
    for name in order for match in MATH.finditer(sections[name])
]
rendered = subprocess.run(
    ['node', str(ROOT / 'scripts/render-math.cjs')], input=json.dumps(jobs),
    capture_output=True, encoding='utf-8', cwd=ROOT,
)
if rendered.returncode:
    raise ValueError('Power semiconductor math rendering failed:\n' + rendered.stderr)
formulas = iter(json.loads(rendered.stdout))
for section in order:
    key = f'power-semiconductors/{section}'
    payload = {'html': MATH.sub(lambda _: next(formulas), sections[section].strip())}
    if section == 'chapter-2-test':
        payload['questions'] = [{'number': n, 'anchor': f'question-{n}'} for n in ['1', '2', '3', '4']]
    assignment = f'window.LN_LESSONS=window.LN_LESSONS||{{}};window.LN_LESSONS[{json.dumps(key)}]='
    (LESSONS / f'{section}.js').write_text(assignment + json.dumps(payload, ensure_ascii=False) + ';\n', encoding='utf-8', newline='\n')
print(f'Rendered {len(sections)} reading units with {len(jobs)} equations.')
