"""Check diagnostic scope and independently calculated answer keys."""
import json
import math
from fractions import Fraction
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PracticeContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions=json.loads((ROOT/'courses/practice/bank.json').read_text())['questions']
        cls.byid={q['id']:q for q in cls.questions}

    def test_calculations_have_independently_checked_values(self):
        expected={'em-power':24*4-Fraction(1,2)*4**2,
            'em-transformer-calc':Fraction(100,5**2*2),
            'tr-calc-test':math.sqrt(2100),'tr-calc-line':10000/math.sqrt(3)/10,
            'tr-calc-base':Fraction(1,10),'tr-calc-eff':Fraction(800,830)*100,
            'tr-calc-parallel':math.sqrt(Fraction(105,10)**2+1),
            'tr-calc-auto':198*Fraction(1000,22),'tr-calc-burden':25*Fraction(18,100),
            'ac-ch3-313':(-10+math.sqrt(100+80))/2,'ac-ch3-316':Fraction(10,10),
            'ac-root-break':self.breakaway_gain(),
            'ac-root-angle':180-135-math.degrees(math.atan2(1,2))-90,
            'ac-root-8p16':8*Fraction(6,5)-Fraction(6,5)**2}
        numeric={q['id'] for q in self.questions if q['type']=='numeric'}
        self.assertEqual(numeric,set(expected))
        for identifier,value in expected.items():
            self.assertAlmostEqual(self.byid[identifier]['answer'],float(value),places=8)

    @staticmethod
    def breakaway_gain():
        # Independently bisect D'(s) on the valid real-axis interval.
        lo,hi=-3.0,-2.0
        for _ in range(60):
            x=(lo+hi)/2
            if 4*x**3+15*x*x+16*x+6>0:hi=x
            else:lo=x
        x=(lo+hi)/2
        return -x*(x+3)*(x*x+2*x+2)

    def test_restricted_or_incomplete_sources_are_not_sold_as_ready(self):
        data=json.loads((ROOT/'courses/practice/sources.json').read_text())
        sources={s['id']:s for s in data['sources']}
        self.assertNotIn('physport-fci-reference',sources)
        for id in ['mit-machines-ps1','nptel-transformer-week6']:
            self.assertTrue(sources[id]['ready'])
        for s in sources.values():
            self.assertTrue(s['answers']);self.assertTrue(s['targets']);self.assertTrue(s['evidenceLinks'])

    def test_misconceptions_have_reasoned_feedback_and_transfer(self):
        for q in self.questions:
            self.assertGreaterEqual(len(q['steps']),3,q['id'])
            self.assertTrue(q['transfer']);self.assertTrue(q['origin'])
            if q['type'] in ('single','multi'):
                self.assertTrue(all(o['feedback'].strip() and o['feedback']!=o['text'] for o in q['options']),q['id'])
                self.assertNotIn('以上都',q['prompt'])
            else:self.assertGreaterEqual(len(q['rubric']),3)
        self.assertIn('尚未覆盖274个阅读单元全部目标',(ROOT/'PRACTICE.md').read_text())

if __name__=='__main__':unittest.main()
