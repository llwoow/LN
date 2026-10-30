"""Keep primary explanations complete, readable, distinct and ahead of reference material."""
from pathlib import Path
import json
import runpy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from learning_content import FIELDS, load
REF = runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))


class TeachingContract(unittest.TestCase):
    def test_existing_definition_links_keep_their_published_anchors(self):
        glossary = runpy.run_path(str(ROOT/'scripts/build-glossary.py'))['build']()
        checked = 0
        for path in (ROOT/'courses').glob('*/definition-anchors.json'):
            entries = {e['id']:e for e in glossary[path.parent.name]['entries']}
            for identifier, anchor in json.loads(path.read_text()).items():
                self.assertEqual(entries[identifier]['source']['anchor'], anchor)
                checked += 1
        self.assertEqual(checked, 466)

    def test_every_registered_unit_has_an_authored_review_and_visible_learning_sequence(self):
        total = 0
        for path in (ROOT/'courses').glob('*/manifest.js'):
            course = REF['assignment'](path)
            records_path = path.parent/'understanding.json'
            records = json.loads(records_path.read_text())
            keys = [s['id'] if course['id']=='electrical-machines' else s['id'].upper() for s in course['sections']]
            load(records_path, keys)
            for section, key in zip(course['sections'], keys):
                with self.subTest(course=course['id'], section=key):
                    payload = REF['assignment'](ROOT/section['src'])
                    document = REF['Document'](payload['html']).root
                    sequences = [n for n in document.walk() if 'learning-sequence' in n.classes]
                    self.assertEqual(len(sequences), 1)
                    sequence = sequences[0]
                    self.assertEqual([n.attrs['data-learning-step'] for n in sequence.children if isinstance(n, REF['Element'])], list(FIELDS))
                    self.assertFalse(any(n.tag=='details' or 'hidden' in n.attrs for n in sequence.walk()))
                    example = next(n for n in sequence.walk() if n.attrs.get('data-learning-step')=='example')
                    self.assertGreaterEqual(sum(n.tag=='li' for n in example.walk()), 3)
                    self.assertNotIn('katex-error', payload['html'])
                    self.assertNotIn(r'\[', sequence.text())
                    self.assertNotIn(r'\(', sequence.text())
                    self.assertLess(payload['html'].index('learning-sequence'), payload['html'].index('source-material-heading'))
                    total += 1
        self.assertEqual(total, 274)

    def test_new_math_keeps_a_separate_numbering_namespace(self):
        targets = REF['build_index']()
        additions = 0
        for path in (ROOT/'courses').glob('*/manifest.js'):
            course = REF['assignment'](path)
            for section in course['sections']:
                doc = REF['Document'](REF['assignment'](ROOT/section['src'])['html']).root
                seq = next(n for n in doc.walk() if 'learning-sequence' in n.classes)
                for node in seq.walk():
                    if {'math','display'} <= node.classes:
                        number = node.attrs.get('data-equation','')
                        self.assertTrue(number.startswith('U.'))
                        self.assertTrue(any(t['section']==section['id'] and t['number']==number for t in targets[course['id']]['targets']))
                        additions += 1
        self.assertGreater(additions, 40)


if __name__=='__main__': unittest.main()
