"""Check real lesson targets, source assets and compatibility of the English adapter."""
from pathlib import Path
import json,re,runpy,unittest

ROOT=Path(__file__).resolve().parents[1]
assignment=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']

class English2027(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course=assignment(ROOT/'courses/hs-english/manifest.js')
        cls.bank=json.loads((ROOT/'courses/practice/bank.json').read_text())
        cls.qs=[q for q in cls.bank['questions'] if q.get('collection')=='english-2027']

    def test_reading_and_practice_are_in_existing_course(self):
        source=json.loads((ROOT/'courses/hs-english/source-index.json').read_text())
        self.assertEqual([(s['id'],s['title']) for s in self.course['sections'] if s['kind']=='outline'],[(n['知识节点编号'].lower(),n['模块或主题']) for n in source['nodes']])
        supplemental=[s for s in self.course['sections'] if s.get('supplement')=='english-2027']
        self.assertEqual(len(supplemental),55)
        for s in supplemental:
            p=assignment(ROOT/s['src'])
            self.assertEqual(p['id'],s['id'])
            self.assertTrue(p['html'])
            self.assertNotIn('href="#source-',p['html'])
            for path in re.findall(r'(?:src|href)="(courses/[^"#]+)',p['html']):
                self.assertTrue((ROOT/path).is_file(),path)
        self.assertEqual({s['group'] for s in supplemental},{m['group'] for m in json.loads((ROOT/'courses/hs-english/supplements.json').read_text())['materials']})

    def test_valid_alternatives_and_real_knowledge_targets(self):
        byid={q['sourceQuestion']:q for q in self.qs}
        self.assertEqual(len(byid),91)
        self.assertEqual(self.bank['version'],1)
        self.assertEqual(byid['G08']['answer'],['but'])
        self.assertEqual(set(byid['M13']['answer']),{'that','which'})
        self.assertEqual(set(byid['M20']['answer']),{'leave','should leave'})
        self.assertEqual(set(byid['M19']['answer']),{'would join','could join','might join'})
        targets={s['id'] for s in self.course['sections'] if s['kind']!='outline'}
        for q in self.qs:
            self.assertTrue(set(q['sections'])<=targets)
            self.assertTrue(q['transfer'])
            if q['type']=='fill':self.assertTrue(q['answer'])

    def test_worked_solutions_mark_reference_use(self):
        byid={q['id']:q for q in self.qs}
        for code in ['P12','P13','P14','P15','P16','P17','P18','P19','P20']:
            p=assignment(ROOT/f'courses/hs-english/lessons/english-2027-{code.lower()}.js')
            self.assertTrue(p['referenceQuestions'])
            self.assertTrue(set(p['referenceQuestions'])<=byid.keys())

    def test_public_course_has_only_web_assets(self):
        folder=ROOT/'courses/hs-english/review-2027'
        self.assertFalse(any(p.suffix.lower() in {'.pdf','.xlsx','.zip','.jpg','.png'} for p in folder.rglob('*')))
        self.assertEqual(len(list((folder/'audio').glob('*.mp3'))),10)
        for p in (folder/'audio').glob('*.mp3'):self.assertGreater(p.stat().st_size,1000)
        self.assertNotIn('88/150',(folder/'manuscript.json').read_text())
        home=assignment(ROOT/'courses/hs-english/lessons/english-2027-home.js')
        self.assertIn('data-english-records',home['html'])

if __name__=='__main__':unittest.main()
