"""Integrity checks for shared scientific cross-references; no extra dependencies."""
from pathlib import Path
import collections
import runpy
import unittest
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))

class PublicationReferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.index = BUILDER['build_index']()

    def test_index_tracks_current_material(self):
        self.assertEqual((ROOT / 'reference-index.js').read_text(), BUILDER['render_index']())

    def test_targets_are_unique_within_each_lesson(self):
        for course in self.index.values():
            keys = [(target['section'], target['anchor']) for target in course['targets']]
            self.assertEqual(len(keys), len(set(keys)))
            for target in course['targets']:
                self.assertIn(target['section'], course['sections'])

    def test_original_numbering_is_preserved(self):
        sections = self.index['electrical-machines']['sections']
        original = lambda entries: [e for e in entries if not (e['number'] or '').startswith('U.')]
        self.assertEqual([e['number'] for e in original(sections['magnetic-sec11']['equations']) if e['number']], ['1.1', '1.2', '1.3', '1.4'])
        self.assertEqual(original(sections['transformer-3']['equations'])[0]['number'], '3.1')
        self.assertEqual([f['number'] for f in original(sections['transformer-symbols']['figures'])], ['S.1', 'S.2'])
        self.assertEqual(original(sections['dc-sec35']['equations'])[0]['number'], '3.9')
        for section, anchors in {
            'magnetic-sec11':['equation-unnumbered-3','equation-unnumbered-5','equation-unnumbered-7','equation-unnumbered-8'],
            'dc-sec34':['equation-unnumbered-1','equation-unnumbered-3','equation-unnumbered-7','equation-unnumbered-8','equation-unnumbered-9'],
            'dc-sec35':['equation-unnumbered-3']
        }.items():
            self.assertEqual([e['anchor'] for e in sections[section]['equations'] if not e['number']], anchors)

    def test_imported_aliases_still_reach_their_targets(self):
        targets = self.index['electrical-machines']['targets']
        aliases = {alias: target for target in targets for alias in target['aliases']}
        self.assertEqual(aliases['eq:basechange']['section'], 'transformer-4')
        self.assertEqual(aliases['eq:basechange']['kind'], 'equation')
        self.assertEqual(aliases['tab:terminals']['kind'], 'table')
        self.assertEqual(aliases['tab:terminals']['number'], '6.1')

    def test_three_level_and_appendix_labels(self):
        label = BUILDER['label']
        self.assertEqual(label('（1.1.1）'), '1.1.1')
        self.assertEqual(label('(2-3-1)'), '2.3.1')
        self.assertEqual(label('图 S.2'), 'S.2')
        self.assertIsNone(label('2026'))

    def test_formula_text_does_not_confuse_data_assignment(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'lesson.js'
            path.write_text('window.LN_LESSONS=window.LN_LESSONS||{};\nwindow.LN_LESSONS["a/b"]={"html":"[x]=y"};\n')
            self.assertEqual(BUILDER['assignment'](path),{'html':'[x]=y'})

if __name__ == '__main__': unittest.main()
