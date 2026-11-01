"""Textbook alignment, local notation and physical consistency of authored models."""
from pathlib import Path
import json
import math
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))

class TransformerCompletion(unittest.TestCase):
    def test_fourteen_sections_are_real_and_preserve_reference_routes(self):
        c=REF['assignment'](ROOT/'courses/electrical-machines/manifest.js')
        canonical=[s for s in c['sections'] if s.get('textbookSection')]
        self.assertEqual([s['textbookSection'] for s in canonical],['2.'+str(i) for i in range(1,15)])
        self.assertEqual(len({s['teachingIndex'] for s in c['sections']}),len(c['sections']))
        self.assertEqual(c['textbook']['isbn'],'9787111447092')
        for s in canonical:
            doc=REF['Document'](REF['assignment'](ROOT/s['src'])['html']).root
            self.assertFalse(any(n.attrs.get('data-learning-standard') for n in doc.walk()))
            self.assertTrue(any(n.tag=='a' and 'section-jumplinks' in (n.parent.parent.attrs.get('class','') if n.parent.parent else '') for n in doc.walk()))
        self.assertTrue(all(next(s for s in c['sections'] if s['id']=='transformer-'+str(i))['referenceOnly'] for i in range(1,11)))
        self.assertEqual(next(s for s in c['sections'] if s['id']=='dc-sec35')['teachingIndex'],30)

    def test_same_symbol_has_distinct_local_physical_meaning(self):
        config=json.loads((ROOT/'courses/electrical-machines/glossary.json').read_text())
        defs={d['id']:d for d in config['symbolDefinitions']}
        zero=defs['pdf-10-sequences'];magnetizing=defs['pdf-3-main'];star=defs['pdf-11-star']
        self.assertIn('I_0',zero['keys']);self.assertIn('I_0',magnetizing['keys'])
        self.assertEqual(zero['sections'],['transformer-sec210'])
        self.assertEqual(magnetizing['sections'],['transformer-sec23'])
        self.assertIn('虚拟',star['description']);self.assertEqual(star['sections'],['transformer-sec211'])

    def test_hypothetical_model_checks_conserve_and_retain_limits(self):
        r=runpy.run_path(str(ROOT/'assets/practice/transformer/reproduce.py'))['compute']()
        self.assertLess(abs(r['T_resistive']['power_residual_W']),1e-9)
        self.assertLess(abs(r['three_winding_loaded']['power_residual_W']),1e-9)
        self.assertEqual(r['parallel']['kcl_abs_A'],0)
        self.assertEqual(r['parallel']['bus_match_V'],0)
        self.assertGreater(r['parallel']['I2_abs_A'],10)
        self.assertLess(r['three_winding']['star_x_pu'][2],0)
        self.assertGreater(r['three_winding']['determinant'],0)
        self.assertAlmostEqual(r['autotransformer']['add_S_VA'],11000)
        self.assertAlmostEqual(r['autotransformer']['subtract_S_VA'],9000)
        t=r['transients'];self.assertEqual(t['initial_A'],0)
        self.assertLess(t['first_peak_s'],.01);self.assertGreater(t['first_peak_A'],t['half_cycle_A'])
        self.assertGreater(r['neutral']['larger_R_load_V'],230)
        self.assertAlmostEqual(r['burden']['CT_VA'],4.5)

    def test_each_section_has_diagnostic_and_known_source_scope(self):
        q=json.loads((ROOT/'courses/practice/bank.json').read_text())['questions']
        for i in range(1,15):self.assertTrue(any('transformer-sec2'+str(i) in x['sections'] for x in q))
        coverage=json.loads((ROOT/'courses/electrical-machines/transformer-coverage.json').read_text())
        self.assertIn('未取得',coverage['book']['notVerified'])
        sources=json.loads((ROOT/'courses/practice/sources.json').read_text())['sources']
        source=next(s for s in sources if s['id']=='nptel-transformer-week6')
        self.assertTrue(source['ready']);self.assertIn('Q10',source['selection']);self.assertIn('排除',source['selection'])

if __name__=='__main__':unittest.main()
