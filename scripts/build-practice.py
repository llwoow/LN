"""Validate exercise records and original/source provenance and compile their browser data."""
import json
import math
from pathlib import Path
import runpy
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
assignment=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
courses={c['id']:{s['id'] for s in c['sections']} for c in [assignment(p) for p in (ROOT/'courses').glob('*/manifest.js')] if not c.get('outlineOnly')}
data=json.loads((ROOT/'courses/practice/bank.json').read_text())
data['sources']=json.loads((ROOT/'courses/practice/sources.json').read_text())['sources']
source_ids=set()
for s in data['sources']:
    assert s['id'] not in source_ids
    source_ids.add(s['id'])
    for t in s['targets']:
        assert t['course'] in courses and t['section'] in courses[t['course']],s['id']
    assert s['answers'] and s['evidence'] and s['evidenceLevel'] and s['readScope'] and s['license'],s['id']
    assert len(s['guide'])>=2 and isinstance(s['ready'],bool),s['id']
    for l in s['links']+s['evidenceLinks']:
        assert urlsplit(l['url']).scheme=='https' and urlsplit(l['url']).netloc,s['id']
seen=set();coverage=set()
skills={'建模','因果与证据','推导计算','边界与反例','迁移设计','解释表达'}
for q in data['questions']:
    assert q['id'] not in seen,q['id'];seen.add(q['id'])
    assert q['course'] in courses and q['sections'] and set(q['sections'])<=courses[q['course']],q['id']
    if q.get('readingAnchor'):
        assert q['course']=='electrical-machines' and 'transformer-homework' in q['sections'],q['id']
        payload=assignment(ROOT/'courses/electrical-machines/lessons/transformer-homework.js')
        document=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['Document'](payload['html']).root
        assert any(n.attrs.get('id')==q['readingAnchor'] for n in document.walk()),q['id']
    coverage.add(q['course'])
    assert q['title'] and q['prompt'] and q['origin'] and q['hint'] and q['transfer'],q['id']
    assert len(q['steps'])>=3 and q['skills'] and set(q['skills'])<=skills,q['id']
    assert q['type'] in {'single','multi','numeric','open'},q['id']
    if q['type'] in {'single','multi'}:
        options=q['options'];ids={o['id'] for o in options}
        assert len(options)>=3 and len(ids)==len(options),q['id']
        assert all(o['text'] and o['feedback'] for o in options),q['id']
        assert set(q['answer'])<ids and len(set(q['answer']))==len(q['answer']),q['id']
        assert len(q['answer'])==(1 if q['type']=='single' else 2),q['id']
    else:
        assert len(q['rubric'])>=3,q['id']
        if q['type']=='numeric':
            assert math.isfinite(q['answer']) and 0<q['tolerance']<1 and q['unit'],q['id']
assert coverage==set(courses),'Exercise courses differ from registered courses'
(ROOT/'courses/practice/bank.js').write_text('window.LN_PRACTICE_BANK='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
print('Built',len(seen),'exercise records across',len(coverage),'courses; coverage is not a claim of full lesson assessment.')
