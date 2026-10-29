"""Coverage and provenance checks for the user-supplied Hainan curriculum index."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import collections
import json
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
assignment, Document = REFERENCE['assignment'], REFERENCE['Document']
GLOSSARY = runpy.run_path(str(ROOT/'scripts/build-glossary.py'))


class HighSchoolIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses = assignment(ROOT/'courses/highschool/courses.js')
        cls.index = {c['id']:c for c in cls.courses}
        cls.documents = {(c['id'],s['id']): Document(assignment(ROOT/s['src'])['html']).root for c in cls.courses for s in c['sections']}

    def test_nine_subjects_fifty_books_and_original_235_nodes(self):
        self.assertEqual(len(self.courses),9)
        self.assertEqual(sum(len(c['sections']) for c in self.courses),235)
        self.assertEqual(sum(len({s['group'] for s in c['sections']}) for c in self.courses),50)
        self.assertEqual(collections.Counter(c['track'] for c in self.courses),{'复习主线':6,'合格考与拓展':3})
        for course in self.courses:
            source=json.loads((ROOT/'courses'/course['id']/'source-index.json').read_text())
            self.assertEqual({s['id'] for s in course['sections']},{n['知识节点编号'].lower() for n in source['nodes']})
            self.assertEqual(assignment(ROOT/'courses'/course['id']/'manifest.js'),course)

    def test_lessons_contain_teaching_examples_and_answers(self):
        for (course_id,section),document in self.documents.items():
            with self.subTest(course=course_id,section=section):
                self.assertGreater(len(document.text()),350)
                nodes=list(document.walk())
                self.assertGreaterEqual(sum(n.tag=='h3' for n in nodes),2)
                self.assertTrue(any('study-answer' in n.classes for n in nodes))
                self.assertTrue(any('study-sources' in n.classes for n in nodes))
                self.assertFalse(any('katex-error' in n.classes for n in nodes))
                self.assertFalse(any(n.tag in {'script','iframe','object','embed','audio'} for n in nodes))
                self.assertFalse(any(k.startswith('on') for n in nodes for k in n.attrs))

    def test_every_knowledge_link_and_citation_has_a_real_target(self):
        for key,document in self.documents.items():
            for node in document.walk():
                href=node.attrs.get('href','')
                if href.startswith('#course/'):
                    parts=unquote(href).split('/')
                    self.assertIn((parts[1],parts[2]),self.documents,(key,href))
                    if len(parts)>3:self.assertTrue(any(n.attrs.get('id')==parts[3] for n in self.documents[parts[1],parts[2]].walk()),href)
                elif href.startswith('http'):
                    self.assertEqual(urlsplit(href).scheme,'https')
                    self.assertTrue(urlsplit(href).hostname)
        for course in self.courses:
            authored=json.loads((ROOT/'courses'/course['id']/'content.json').read_text())
            self.assertGreaterEqual(len(authored['sources']),3)
            self.assertTrue(all(lesson.get('sources') for lesson in authored['lessons']))

    def test_graph_relations_are_explained_and_links_are_valid(self):
        for course in self.courses:
            ids={s['id'] for s in course['sections']};graph=course['knowledgeMap']
            self.assertEqual({n['section'] for n in graph['nodes']},ids)
            self.assertTrue(graph['links'])
            seen=set()
            for edge in graph['links']:
                self.assertIn(edge['from'],ids);self.assertIn(edge['to'],ids)
                self.assertNotEqual(edge['from'],edge['to'])
                self.assertTrue(edge['label']);self.assertGreater(len(edge['description']),10)
                self.assertNotIn((edge['from'],edge['to']),seen);seen.add((edge['from'],edge['to']))

    def test_definitions_load_per_course_and_respect_local_scope(self):
        data=GLOSSARY['build']();bundles=GLOSSARY['lazy_bundles'](data)
        base=(ROOT/'glossary-index.js').read_text()
        for course in self.courses:
            with self.subTest(course=course['id']):
                self.assertNotIn('"'+course['id']+'":',base)
                self.assertEqual((ROOT/course['glossary']).read_text(),bundles[course['id']])
                entries=data[course['id']]['entries']
                self.assertGreaterEqual(sum(e['kind']=='term' for e in entries),10)
                for entry in entries:
                    self.assertEqual(entry['sections'],[entry['source']['section']])
                    doc=self.documents[course['id'],entry['source']['section']]
                    passages=[n for n in doc.walk() if n.tag in {'p','h2','h3','h4','li','td'}]
                    self.assertEqual(entry['definitionHtml'],GLOSSARY['inner'](passages[entry['source']['passage']]))

    def test_original_evidence_and_version_differences_are_retained(self):
        data=json.loads((ROOT/'courses/highschool/catalog.json').read_text())
        self.assertEqual(len(data['教材册次与知识']),104)
        self.assertEqual(len(data['外研七册单元']),42)
        self.assertEqual(len(data['来源目录']),28)
        self.assertEqual(len(data['待核事项']),5)
        for name in ['hainan-2027-report.pdf','hainan-2027-index.xlsx']:
            self.assertTrue((ROOT/'courses/highschool/assets'/name).is_file())
        for relation in data['crossLinks']:
            self.assertIn((relation['from']['course'],relation['from']['section']),self.documents)
            self.assertIn((relation['to']['course'],relation['to']['section']),self.documents)


if __name__=='__main__':unittest.main()
