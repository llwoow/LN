"""Definitions retain their real source and scientific symbol identity."""
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
BUILDER = runpy.run_path(str(ROOT / 'scripts/build-glossary.py'))


class DefinitionIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = BUILDER['build']()['electrical-machines']['entries']
        cls.sections = {s['id']: s for s in BUILDER['assignment'](
            ROOT / 'courses/electrical-machines/manifest.js')['sections']}

    def test_generated_index_matches_sources(self):
        self.assertEqual((ROOT / 'glossary-index.js').read_text(), BUILDER['render']())

    def test_every_link_reaches_its_exact_source(self):
        self.assertEqual(len(self.entries), len({e['id'] for e in self.entries}))
        for entry in self.entries:
            source = entry['source']
            document = BUILDER['Document'](BUILDER['assignment'](
                ROOT / self.sections[source['section']]['src'])['html']).root
            if 'row' in source:
                tables = [n for n in document.walk() if n.tag == 'table']
                row = [n for n in tables[source['table']].walk() if n.tag == 'tr'][source['row']]
                cells = [n for n in row.children if isinstance(n, BUILDER['Element']) and n.tag == 'td']
                self.assertEqual(entry['definitionHtml'], BUILDER['inner'](cells[1]))
            else:
                nodes = [n for n in document.walk() if n.tag in {'p','h2','h3','h4','li','td'}]
                self.assertEqual(entry['definitionHtml'], BUILDER['inner'](nodes[source['passage']]))
            self.assertTrue(entry['definitionHtml'])

    def test_identical_letters_keep_distinct_chapter_meanings(self):
        for key, section, transformer, dc in [('a', 'transformer-symbols', '匝数比', '支路对数'), ('ω', 'magnetic-overview', '电角频率', '机械角速度')]:
            definitions = {e['source']['section']: e['description'] for e in self.entries if e['kind'] == 'symbol' and key in e['keys']}
            self.assertIn(transformer, definitions[section])
            self.assertIn(dc, definitions['dc-overview'])

    def test_math_fonts_subscripts_and_primes_remain_semantic(self):
        by_id = {e['id']: e for e in self.entries}
        self.assertEqual(by_id['symbol-magnetic-overview-7']['keys'], ['cal:R', 'Λ'])
        self.assertEqual(by_id['symbol-magnetic-overview-13']['keys'], ['W_m', "W_m'", 'V_c'])
        self.assertEqual(by_id['symbol-transformer-symbols-17']['keys'], ['ph', 'line'])
        self.assertIn('M', by_id['symbol-magnetic-overview-10']['keys'])
        self.assertNotIn('bold:M', by_id['symbol-magnetic-overview-10']['keys'])
        self.assertIn('bold:M', by_id['magnetization']['keys'])
        self.assertEqual(by_id['symbol-dc-overview-2']['keys'], ['I_a', 'I_f', 'I_L'])

    def test_acronyms_have_reviewed_full_names_and_operating_conditions(self):
        terms = {e['id']: e for e in self.entries if e['kind'] == 'term'}
        self.assertIn('Current Transformer', terms['ct']['english'])
        self.assertIn('二次不应开路', terms['ct']['description'])
        self.assertIn('Voltage Transformer', terms['vt']['english'])
        self.assertIn('二次不应短路', terms['vt']['description'])
        for term in terms.values():
            self.assertTrue(term['aliases'])
            self.assertTrue(term['english'])
            self.assertTrue(term['description'])

    def test_local_quantities_have_explicit_lesson_scopes(self):
        by_id = {e['id']: e for e in self.entries}
        for name in ['dc-commutation-current', 'dc-commutation-time', 'dc-commutation-inductance', 'dc-reactance-emf']:
            self.assertEqual(by_id[name]['sections'], ['dc-sec39'])
        self.assertNotIn('transformer-7', by_id['transformer-open-test']['sections'])
        self.assertNotIn('transformer-7', by_id['transformer-excitation-current']['sections'])
        self.assertEqual(by_id['magnetic-coupling']['sections'], ['magnetic-sec14'])
        self.assertIn('dot:I_1', by_id['transformer-current-ports']['keys'])
        self.assertIn("dot:I_2'", by_id['transformer-referred-current']['keys'])

    def test_every_scope_is_a_real_lesson(self):
        for entry in self.entries:
            for section in entry.get('sections', []):
                self.assertIn(section, self.sections)
            if entry['kind'] == 'symbol':
                self.assertTrue(entry['symbolHtml'])


if __name__ == '__main__':
    unittest.main()
