"""Verify that the Hainan outline retains its structure and has no teaching payloads."""
import collections
import json
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
assignment = REFERENCE['assignment']


class HighSchoolIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses = assignment(ROOT/'courses/highschool/courses.js')

    def test_nine_subjects_fifty_books_and_original_235_nodes(self):
        self.assertEqual(len(self.courses), 9)
        self.assertEqual(sum(len(c['sections']) for c in self.courses), 235)
        self.assertEqual(sum(len({s['group'] for s in c['sections']}) for c in self.courses), 50)
        self.assertEqual(collections.Counter(c['track'] for c in self.courses), {'语言':2,'数理化生':4,'政史地':3})
        for course in self.courses:
            folder = ROOT/'courses'/course['id']
            source = json.loads((folder/'source-index.json').read_text(encoding='utf-8'))
            expected = [(n['知识节点编号'].lower(), n['模块或主题']) for n in source['nodes']]
            self.assertEqual([(s['id'], s['title']) for s in course['sections']], expected)
            self.assertEqual(assignment(folder/'manifest.js'), course)

    def test_outline_nodes_have_no_teaching_payload(self):
        index = assignment(ROOT/'reference-index.js')
        for course in self.courses:
            folder = ROOT/'courses'/course['id']
            self.assertTrue(course['outlineOnly'])
            self.assertNotIn('glossary', course)
            self.assertFalse((folder/'content.json').exists())
            self.assertFalse(list(folder.glob('lessons/*.js')))
            self.assertFalse(course['knowledgeMap'].get('links'))
            self.assertEqual(index[course['id']], {'sections': {}, 'targets': []})
            for section in course['sections']:
                self.assertEqual(section['kind'], 'outline')
                self.assertNotIn('src', section)

    def test_teaching_catalogs_exclude_outline_courses(self):
        outline = {course['id'] for course in self.courses}
        practice = assignment(ROOT/'courses/practice/bank.js')
        resources = assignment(ROOT/'courses/resources/catalog.js')
        self.assertFalse(any(q['course'] in outline for q in practice['questions']))
        self.assertFalse(any(t['course'] in outline for r in practice['sources'] + resources['resources'] for t in r['targets']))

    def test_original_evidence_and_version_differences_are_retained(self):
        data = json.loads((ROOT/'courses/highschool/catalog.json').read_text(encoding='utf-8'))
        for key, count in [('教材册次与知识',104), ('外研七册单元',42), ('来源目录',28), ('待核事项',5)]:
            self.assertEqual(len(data[key]), count)
        for name in ['hainan-2027-report.pdf', 'hainan-2027-index.xlsx']:
            self.assertTrue((ROOT/'courses/highschool/assets'/name).is_file())

    def test_learning_paths_keep_their_titles_and_valid_ordered_nodes(self):
        self.assertEqual(sum(len(c['knowledgeMap']['paths']) for c in self.courses), 17)
        for course in self.courses:
            ids = {s['id'] for s in course['sections']}
            for path in course['knowledgeMap']['paths']:
                self.assertTrue(path['title'])
                self.assertNotIn('summary', path)
                self.assertGreaterEqual(len(path['steps']), 2)
                self.assertEqual(len(path['steps']), len({s['section'] for s in path['steps']}))
                for step in path['steps']:
                    self.assertIn(step['section'], ids)
                    self.assertNotIn('focus', step)


if __name__ == '__main__':
    unittest.main()
