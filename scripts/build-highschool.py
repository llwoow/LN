"""Build the high-school outline from the supplied Hainan textbook index."""
from pathlib import Path
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['chinese','math','english','physics','chemistry','biology','politics','history','geography']
TRACKS = {'chinese':'语言','english':'语言','math':'数理化生','physics':'数理化生','chemistry':'数理化生','biology':'数理化生','politics':'政史地','history':'政史地','geography':'政史地'}
MATH = re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', re.S)


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def render(markup, prefix):
    matches = list(MATH.finditer(markup))
    if not matches:
        return markup
    expressions = [{'tex': html.unescape(m[1] if m[1] is not None else m[2]), 'display': m[1] is not None} for m in matches]
    proc = subprocess.run(['node', str(ROOT/'scripts/render-math.cjs')], input=dump(expressions), text=True, capture_output=True)
    if proc.returncode:
        raise ValueError('Math rendering failed in '+prefix+': '+proc.stderr[-1800:])
    rendered = iter(json.loads(proc.stdout)); sequence = 0
    def substitute(match):
        nonlocal sequence
        formula = next(rendered)
        if match[1] is not None:
            sequence += 1
            return '<div class="math display" data-equation="'+prefix+'.'+str(sequence)+'">'+formula+'</div>'
        return '<span class="math inline">'+formula+'</span>'
    return MATH.sub(substitute, markup)


def build():
    courses = []
    directory = ROOT / 'courses/highschool'
    learning_paths = json.loads((directory / 'learning-paths.json').read_text(encoding='utf-8'))
    for slug in ORDER:
        course_id = 'hs-' + slug
        folder = ROOT / 'courses' / course_id
        data = json.loads((folder / 'source-index.json').read_text(encoding='utf-8'))
        books = {book['教材编号']: book for book in data['books'] if book['索引层级'] == '主索引'}
        sections = []
        for node in data['nodes']:
            identifier = node['知识节点编号']
            book = books[identifier.rsplit('-', 1)[0]]
            sections.append({
                'id': identifier.lower(), 'title': node['模块或主题'], 'group': book['册次'],
                'kind': 'outline', 'curriculum': node['课程类别'], 'keywords': [identifier, node['版本']],
            })
        ids = {section['id'] for section in sections}
        if len(ids) != len(sections):
            raise ValueError('Duplicate outline node in ' + course_id)
        paths = learning_paths[course_id]
        for path in paths:
            steps = [step['section'] for step in path['steps']]
            if len(set(steps)) != len(steps) or len(steps) < 2 or not set(steps) <= ids:
                raise ValueError('Invalid outline path: ' + path['id'])
        chapters = [{'group': book['册次'], 'description': book['课程类别'] + ' · ' + book['版本']} for book in books.values()]
        manifest = {
            'id': course_id, 'title': data['subject'], 'level': 'highschool', 'category': '高中',
            'track': TRACKS[slug], 'outlineOnly': True, 'topics': ['仅目录'],
            'versionNote': data['overview'][0]['地区核验状态'], 'sections': sections,
            'resources': {book['册次']: {'links': [{'label': '教材与来源', 'href': '#highschool/resources'}]} for book in books.values()},
            'knowledgeMap': {'chapters': chapters, 'paths': paths},
        }
        supplemental = folder / 'supplements.json'
        if supplemental.exists():
            extras = json.loads(supplemental.read_text(encoding='utf-8'))
            for material in extras['materials']:
                for section in material['sections']:
                    if section['id'] in ids or not (ROOT / section['src']).is_file():
                        raise ValueError('Invalid supplementary section: ' + section['id'])
                    ids.add(section['id'])
                    manifest['sections'].append(section)
                manifest['resources'][material['group']] = {'links': material['links']}
                manifest['knowledgeMap']['chapters'].append({'group': material['group'], 'description': material['description']})
                manifest['knowledgeMap'].setdefault('links', []).extend(material.get('knowledgeLinks', []))
            manifest['knowledgeMap']['nodes'] = [{'section': s['id'], 'title': s['title'], 'note': s.get('curriculum') or s.get('note') or ('原卷与学习记录' if s['id']=='physics-001' else '逐题讲解与运动模型')} for s in manifest['sections']]
            manifest['outlineOnly'] = False
            manifest['topics'] = ['教材目录', *dict.fromkeys(m.get('label','试卷讲解') for m in extras['materials'])]
            manifest['glossary'] = 'courses/' + course_id + '/glossary-index.js'
        (folder / 'manifest.js').write_text('window.LN_HS_' + slug.upper() + '=' + dump(manifest) + ';\n', encoding='utf-8', newline='\n')
        courses.append(manifest)
    (directory / 'courses.js').write_text('window.LN_HIGH_SCHOOL_COURSES=' + dump(courses) + ';\n', encoding='utf-8', newline='\n')
    print(f"Built {len(courses)} high-school outlines with {sum(len(c['sections']) for c in courses)} nodes.")


if __name__ == '__main__':
    build()
