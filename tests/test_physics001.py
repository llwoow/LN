"""Preservation and boundary checks; these do not certify learner understanding."""
from pathlib import Path
import hashlib,json,runpy,unittest
ROOT=Path(__file__).resolve().parents[1]
A=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
BASE=ROOT/'courses/hs-physics/physics-001'
class Physics001(unittest.TestCase):
 def test_existing_question_identities_and_meanings_are_unchanged(self):
  baseline=json.loads((BASE/'verification/baseline.json').read_text());bank=json.loads((ROOT/'courses/practice/bank.json').read_text());byid={q['id']:q for q in bank['questions']}
  self.assertEqual(bank['version'],baseline['practiceVersion'])
  for id,expected in baseline['practiceQuestions'].items():self.assertEqual(hashlib.sha256(json.dumps(byid[id],sort_keys=True,ensure_ascii=False).encode()).hexdigest(),expected,id)
 def test_original_reasoning_is_preserved_and_visible(self):
  d=json.loads((BASE/'content.json').read_text());original=json.loads((BASE/'verification/content-v1.2-source.json').read_text())
  self.assertEqual([q['sections'] for q in d['questions']],[q['sections'] for q in original['questions']])
  self.assertEqual([q['answer'] for q in d['questions']],[q['answer'] for q in original['questions']])
  for q in d['questions']:
   body=A(ROOT/f"courses/hs-physics/lessons/physics-001-q{q['id']:02d}.js")['html']
   for block in q['sections']:self.assertIn(block['title'],body)
   self.assertNotIn('katex-error',body);self.assertNotIn('autoplay',body)
 def test_conditional_reading_is_not_autograded_and_multiselect_has_three_choices(self):
  bank=json.loads((ROOT/'courses/practice/bank.json').read_text());q={x['id']:x for x in bank['questions']}
  self.assertEqual(q['hs-physics001-07']['type'],'open');self.assertIn('裁切',q['hs-physics001-07']['origin'])
  self.assertEqual(q['hs-physics001-13']['answer'],['A','B','D'])
  self.assertEqual({x['type'] for x in bank['questions'] if x['id'].startswith('hs-physics001-')},{'single','multi','open'})
 def test_all_media_have_real_route_targets_and_committed_files(self):
  data=json.loads((BASE/'content.json').read_text()); clips=[]
  for q in data['questions']:
   body=A(ROOT/f"courses/hs-physics/lessons/physics-001-q{q['id']:02d}.js")['html']
   for c in q['animations']:
    clips.append(c['id']);self.assertIn('id="motion-'+c['id']+'"',body)
    for folder,key in [('gifs','gif'),('video','video'),('posters','poster')]:self.assertTrue((BASE/'animations'/folder/c[key]).is_file())
  self.assertEqual(len(set(clips)),20)
 def test_original_chinese_equation_labels_are_preserved(self):
  equations=A(ROOT/'reference-index.js')['hs-physics']['sections']['physics-001-q07']['equations']
  self.assertEqual([e['number'] for e in equations if e['number']],['甲','乙'])
 def test_local_symbol_k_has_separate_source_backed_meanings(self):
  entries=A(ROOT/'courses/hs-physics/glossary-index.js')['entries']
  ks=[e for e in entries if 'k' in e.get('keys',[])];self.assertEqual(len(ks),4)
  self.assertTrue(all(len(e['sections'])==1 for e in ks));self.assertEqual(len({e['source']['section'] for e in ks}),4)
if __name__=='__main__':unittest.main()
