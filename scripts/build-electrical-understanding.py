"""Prepend authored, model-first teaching without changing imported source material."""
from pathlib import Path
import html
import json
import re
import runpy
from learning_content import load, render

ROOT = Path(__file__).resolve().parents[1]
reference = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
math_renderer = runpy.run_path(str(ROOT/'scripts/build-highschool.py'))['render']
assignment = reference['assignment']
BEGIN = '<!--LN-UNDERSTANDING:BEGIN-->'
END = '<!--LN-UNDERSTANDING:END-->'


def build():
    course = assignment(ROOT/'courses/electrical-machines/manifest.js')
    records = load(ROOT/'courses/electrical-machines/understanding.json', [s['id'] for s in course['sections']])
    for index, section in enumerate(course['sections'], 1):
        path = ROOT/section['src']; payload = assignment(path)
        prior = payload.get('html', '')
        original = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END), '', prior, flags=re.S)
        if '<table' in ''.join(records[section['id']][key] for key in ('question','model','reasoning','example','boundaries','checks','transfer')):
            raise ValueError('Original symbol-table positions must remain stable: ' + section['id'])
        explanation = render(records[section['id']], 'U.'+str(index), math_renderer, course['id'])
        insert = BEGIN + explanation + '<h3 class="source-material-heading">补充说明与原材料</h3>' + END
        heading = re.search(r'<h2\b[^>]*>.*?</h2>', original, re.S)
        if heading:
            combined = original[:heading.end()] + insert + original[heading.end():]
        else:
            combined = '<h2>' + html.escape(section['title']) + '</h2>' + insert + original
        payload['html'] = combined
        key = course['id']+'/'+section['id']
        path.write_text('window.LN_LESSONS=window.LN_LESSONS||{};\nwindow.LN_LESSONS['+json.dumps(key)+']='+json.dumps(payload, ensure_ascii=False, separators=(',',':'))+';\n')
    print('Rebuilt model-first teaching for '+str(len(records))+' electrical-machines units.')


if __name__ == '__main__': build()
