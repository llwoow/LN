"""Source coverage, semantic math and independent numerical checks for the 13 solved exercises."""
import hashlib
import json
import math
import runpy
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
class SolvedHomework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'courses/electrical-machines/homework-source.json').read_text())
        cls.payload=REF['assignment'](ROOT/'courses/electrical-machines/lessons/transformer-homework.js')
        cls.doc=REF['Document'](cls.payload['html']).root
    def test_original_question_numbers_and_all_subparts_are_web_content(self):
        expected=['2-2','2-3','2-4','2-6','2-7','2-12','2-13','2-17','2-19','2-20','2-22','2-25','2-26']
        self.assertEqual([q['number'] for q in self.data['questions']],expected)
        course=REF['assignment'](ROOT/'courses/electrical-machines/manifest.js')
        self.assertEqual(next(s for s in course['sections'] if s['id']=='transformer-homework')['kind'],'html')
        ids={n.attrs.get('id') for n in self.doc.walk()}
        for n in expected:self.assertIn('question-'+n,ids)
        for page in range(1,14):self.assertIn('page-'+str(page),ids)
        text=self.doc.text()
        for evidence in ['高压侧参数','完全忽略励磁支路','图b','额定调整率','最大效率','68.79','60.56','59.56','487.142857','变比平方']:
            if evidence=='变比平方':continue
            self.assertIn(evidence,text)
        self.assertNotIn('pdf-image',self.payload['html'])
        self.assertNotIn('assets/homework/page-',self.payload['html'])
        self.assertGreater(sum(n.tag=='math' for n in self.doc.walk()),80)
        self.assertNotIn('katex-error',self.payload['html'])
        self.assertTrue(all(n.attrs['data-equation'].startswith('H.2.') for n in self.doc.walk() if 'data-equation' in n.attrs))
    def test_wiring_diagrams_and_source_citation_are_retained(self):
        metadata=json.loads((ROOT/'courses/electrical-machines/homework-figures.json').read_text())
        self.assertNotIn('pdf',self.payload)
        self.assertIn('出版社书目',self.payload['html'])
        self.assertEqual(len(metadata['figures']),7)
        for figure in metadata['figures']:
            content=(ROOT/'courses/electrical-machines/assets/homework'/figure['file']).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(),figure['sha256'])
            self.assertIn(figure['file'],self.payload['html'])
        self.assertIn('figure-2-61',{n.attrs.get('id') for n in self.doc.walk()})
        figure=next(t for t in REF['build_index']()['electrical-machines']['targets'] if t['section']=='transformer-homework' and t['anchor']=='figure-2-61')
        self.assertEqual(figure['number'],'2.61')
        self.assertEqual(figure['displayNumber'],'2-61')
    def test_independent_power_and_basis_checks(self):
        r=runpy.run_path(str(ROOT/'assets/practice/homework/reproduce.py'))['compute']()
        t=r['q2_19'];self.assertAlmostEqual(t['ratio_squared'],(876/260)**2,places=10)
        self.assertLess(abs(t['power_balance_residual_W']),1e-8)
        self.assertLess(t['magnetizing_node_residual_A'],1e-12)
        self.assertAlmostEqual(t['I1_A']['magnitude'],54.5634012120,places=8)
        self.assertAlmostEqual(t['U1_V']['magnitude'],21275.0750088,places=6)
        self.assertAlmostEqual(t['U1_series_only_V']['magnitude'],21249.7763727,places=6)
        self.assertAlmostEqual(r['q2_17']['primary_three_phase_VA'],5e6)
        self.assertAlmostEqual(r['q2_17']['secondary_three_phase_VA'],5e6)
        self.assertEqual(r['q2_20']['clock_group'],7)
        self.assertLess(abs(r['q2_22']['loss_equality_residual_W']),1e-8)
        self.assertAlmostEqual(r['q2_22']['regulation_percent'],4.1247961661,places=8)
        self.assertAlmostEqual(r['q2_22']['max_efficiency_percent'],97.9713773039,places=8)
        self.assertLess(abs(r['q2_25']['loop_voltage_residual_V']),1e-10)
        self.assertGreater(abs(r['q2_25']['secondary_phase_current_A']-68.79),1)
        self.assertLess(abs(r['q2_26']['primary_of_distribution_sum_residual_kVA']),1e-10)
        self.assertAlmostEqual(r['q2_26']['maximum_total_kVA'],487.1428571429,places=8)
    def test_each_original_exercise_has_stable_collection_identity_and_exact_return(self):
        bank=json.loads((ROOT/'courses/practice/bank.json').read_text())
        qs={q['id']:q for q in bank['questions']}
        for source in self.data['questions']:
            q=qs['hw-'+source['number']]
            self.assertEqual(q['readingAnchor'],'question-'+source['number'])
            self.assertEqual(q['type'],'open')
            self.assertEqual(q['rubric'],source['rubric'])
            self.assertIn('用户提供',q['origin'])
        self.assertIn("ln.practice.v1",(ROOT/'practice.js').read_text())
