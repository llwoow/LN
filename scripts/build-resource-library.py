"""Validate reviewed links and reproducibility claims before exposing them in the reader."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
assignment=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
courses={}
for path in (ROOT/'courses').glob('*/manifest.js'):
    course=assignment(path);courses[course['id']]={s['id'] for s in course['sections']}
data=json.loads((ROOT/'courses/resources/catalog.json').read_text());seen=set();covered=set()
for resource in data['resources']:
    identifier=resource['id']
    if not re.fullmatch('[a-z][a-z0-9-]*',identifier) or identifier in seen:raise ValueError('Resource id: '+identifier)
    seen.add(identifier)
    for field in ['title','question','requirements','license']:
        if not isinstance(resource.get(field),str) or not resource[field].strip():raise ValueError('Missing '+field+': '+identifier)
    if len(resource['steps'])<3 or not resource['limits']:raise ValueError('Missing executable task/boundary: '+identifier)
    for target in resource['targets']:
        if target['course'] not in courses or target['section'] not in courses[target['course']]:raise ValueError('Unknown resource target: '+str(target))
        covered.add(target['course'])
    for entry in resource['links']+resource['evidence']:
        if urlsplit(entry['url']).scheme!='https':raise ValueError('Expected a secure, direct external link: '+entry['url'])
    for entry in resource['downloads']:
        path=Path(entry['path'])
        if path.is_absolute() or '..' in path.parts or not (ROOT/path).is_file():raise ValueError('Missing public artifact: '+str(path))
    if resource['verification']['executed'] and not resource['downloads']:raise ValueError('Executed claim needs reproducible artifacts: '+identifier)
if covered!=set(courses):raise ValueError('Courses without reviewed learning resources: '+str(set(courses)-covered))
data['motorSpecification']=json.loads((ROOT/'assets/practice/dc-specs/specification.json').read_text())
data['motorResults']=json.loads((ROOT/'assets/practice/dc-specs/results.json').read_text())
(ROOT/'courses/resources/catalog.js').write_text('window.LN_RESOURCE_CATALOG='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n')
print('Built '+str(len(seen))+' reviewed resources across '+str(len(covered))+' courses.')
