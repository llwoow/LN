"""Build the high-school outline from the supplied Hainan textbook index."""
from pathlib import Path
import json
from lesson_math import render

ROOT = Path(__file__).resolve().parents[1]
ORDER = ['chinese','math','english','physics','chemistry','biology','politics','history','geography']
TRACKS = {'chinese':'语言','english':'语言','math':'数理化生','physics':'数理化生','chemistry':'数理化生','biology':'数理化生','politics':'政史地','history':'政史地','geography':'政史地'}


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def build():
    courses = []
    directory = ROOT / 'courses/highschool'
    learning_paths = json.loads((directory / 'learning-paths.json').read_text(encoding='utf-8'))
    studies = json.loads((directory / 'studies/catalog.json').read_text(encoding='utf-8'))
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
        materials = []
        if supplemental.exists():
            materials.extend(json.loads(supplemental.read_text(encoding='utf-8'))['materials'])
        study_sections, study_links = [], []
        material_group = '专题学习'
        for study in studies.get(slug, []):
            section_id, title = study['id'], study['title']
            source = folder / 'lessons' / (section_id + '.js')
            source.parent.mkdir(exist_ok=True)
            document = (directory / 'studies' / study['file']).read_text(encoding='utf-8')
            source.write_text('window.LN_LESSONS=window.LN_LESSONS||{};window.LN_LESSONS[' + dump(course_id + '/' + section_id) + ']=' + dump({'html': render(document, study['equationPrefix'])}) + ';\n', encoding='utf-8')
            study_sections.append({'id': section_id, 'title': title, 'group': material_group,
                                   'kind': 'html', 'supplement': 'study', 'keywords': study['keywords'],
                                   'src': source.relative_to(ROOT).as_posix()})
            for link in study['connections']:
                if link['section'] not in ids:
                    raise ValueError('Study link does not refer to a textbook node: ' + link['section'])
                study_links.append({'from': link['section'], 'to': section_id,
                                    'label': link['label'], 'description': link['description']})
        if study_sections:
            materials.append({'group': material_group, 'description': '从具体问题进入教材知识',
                              'links': [{'label': '教材与来源', 'href': '#highschool/resources'}],
                              'sections': study_sections, 'knowledgeLinks': study_links})
        if materials:
            for material in materials:
                for section in material['sections']:
                    if section['id'] in ids or not (ROOT / section['src']).is_file():
                        raise ValueError('Invalid supplementary section: ' + section['id'])
                    ids.add(section['id'])
                    manifest['sections'].append(section)
                manifest['resources'][material['group']] = {'links': material['links']}
                if material['group'] not in {chapter['group'] for chapter in manifest['knowledgeMap']['chapters']}:
                    manifest['knowledgeMap']['chapters'].append({'group': material['group'], 'description': material['description']})
                manifest['knowledgeMap'].setdefault('links', []).extend(material.get('knowledgeLinks', []))
            def map_note(section):
                if section.get('supplement') == 'study':
                    return ' · '.join(section['keywords'])
                return section.get('curriculum') or ('试卷讲解与学习记录' if section['id'] == 'physics-001' else '逐题讲解与运动模型')
            manifest['knowledgeMap']['nodes'] = [{'section': s['id'], 'title': s['title'], 'note': map_note(s)} for s in manifest['sections']]
            manifest['outlineOnly'] = False
            manifest['topics'] = ['教材目录', *[m['group'] for m in materials]]
            if (folder / 'glossary.json').is_file():
                manifest['glossary'] = 'courses/' + course_id + '/glossary-index.js'
        (folder / 'manifest.js').write_text('window.LN_HS_' + slug.upper() + '=' + dump(manifest) + ';\n', encoding='utf-8', newline='\n')
        courses.append(manifest)
    (directory / 'courses.js').write_text('window.LN_HIGH_SCHOOL_COURSES=' + dump(courses) + ';\n', encoding='utf-8', newline='\n')
    print(f"Built {len(courses)} high-school outlines with {sum(len(c['sections']) for c in courses)} nodes.")


if __name__ == '__main__':
    build()
