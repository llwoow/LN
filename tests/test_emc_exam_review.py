"""Source-derived EMC review inventory and independent numerical checks."""
import math
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
assignment = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))['assignment']

class EmcExamReview(unittest.TestCase):
    def test_scope(self):
        d = assignment(ROOT / 'courses/electromagnetic-compatibility/exam-review-data.js')
        chapters = d['chapters']
        self.assertEqual([c['n'] for c in chapters], list(range(1, 11)))
        rows = [r for c in chapters for r in c['rows']]
        self.assertEqual(len(rows), 40)
        self.assertEqual(len({r['id'] for r in rows}), 40)
        self.assertTrue(all(r['method'] and r['trap'] for r in rows))
        self.assertEqual(sum(len(r['formulas']) for r in rows), 75)
        self.assertTrue(all(f['tex'] and f['plain'] for r in rows for f in r['formulas']))
        self.assertTrue(all(c['question'] and c['answer'] for c in chapters))
        self.assertIn('2.632×10⁻⁵', chapters[1]['answer'])
        self.assertIn('33.58', chapters[1]['answer'])

    def test_calculation_models(self):
        ec = 1.257e-6 * 1e-3 * 1e8 * 0.1 / 10
        ed = 1.316e-14 * 1e-2 * 1e16 * 0.1 * 0.002 / 10
        self.assertAlmostEqual(ed, 2.632e-5)
        self.assertAlmostEqual(20*math.log10(ec/ed),33.58,places=2)
        self.assertAlmostEqual(20*math.log10(19.81),25.94,places=2)
        self.assertAlmostEqual(10*math.log10(1+(2*math.pi*1e5*100e-6/100)**2),1.45,places=2)
        self.assertAlmostEqual((4/5)**1.5*4*math.pi*1e-7*100/.25*1e6,359.67,places=2)
        self.assertAlmostEqual(.5*150e-12*2000**2*1000,.3)
        self.assertAlmostEqual(330*150e-12*1e9,49.5)
        self.assertAlmostEqual(math.sqrt(6)/math.pi*100,77.97,places=2)
        self.assertAlmostEqual(200/(200+1800)*10,1)

if __name__ == '__main__':
    unittest.main()
