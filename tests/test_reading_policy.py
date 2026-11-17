"""Reader source presentation and real definition destinations."""
from pathlib import Path
import json,runpy,unittest
ROOT=Path(__file__).resolve().parents[1];B=runpy.run_path(str(ROOT/'scripts/build-glossary.py'))
class ReadingPolicy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.index=B['build']()
 def test_exact_definition_passages_are_real_and_anchors_are_stable(self):
  for cid,c in self.index.items():
   sections={s['id']:s for s in B['assignment'](ROOT/'courses'/cid/'manifest.js')['sections']}
   pins=json.loads((ROOT/'courses'/cid/'definition-anchors.json').read_text()) if (ROOT/'courses'/cid/'definition-anchors.json').exists() else {}
   for e in c['entries']:
    if e['id'] in pins:self.assertEqual(e['source']['anchor'],pins[e['id']])
    if e.get('sourceAnchor'):
     doc=B['Document'](B['assignment'](ROOT/sections[e['source']['section']]['src'])['html']).root
     nodes=[n for n in doc.walk() if n.tag in {'p','h2','h3','h4','li','td'}]
     target=nodes[e['source']['passage']]
     self.assertEqual(target.attrs.get('id'),e['sourceAnchor'],e['id'])
     self.assertIn(e['match'],B['clean'](target.text()),e['id'])
 def test_course_level_reference_is_not_repeated_in_each_lesson(self):
  for manifest in (ROOT/'courses').glob('*/manifest.js'):
   course=B['assignment'](manifest)
   for s in course['sections']:
    if s.get('kind')!='html':continue
    source=B['assignment'](ROOT/s['src']).get('html','')
    self.assertNotIn('class="reading-reference"',source,s['id'])
    if course['id']=='electromagnetic-compatibility':
     self.assertNotIn('课件',source,s['id']+' must explain the mechanism without external handout pointers')
  emc=B['assignment'](ROOT/'courses/electromagnetic-compatibility/lessons/emc-9-1.js')['html']
  for marker in ['id="emc-lightning-pulse"','id="emc-transformer-capacitive-coupling"','C<sub>12</sub>','C<sub>20</sub>']:
   self.assertIn(marker,emc)
  dev=B['assignment'](ROOT/'courses/electromagnetic-compatibility/lessons/emc-9-3.js')['html']
  self.assertIn('id="emc-surge-comparison"',dev)
  self.assertIn('GDT',dev);self.assertIn('MOV',dev);self.assertIn('TVS',dev)
 def test_math_atoms_keep_semantic_superscripts_and_hats(self):
  cases=[('<msup><mi>V</mi><mo>+</mo></msup>','V^+'),('<msup><mi>V</mi><mo>−</mo></msup>','V^-'),('<msubsup><mi>u</mi><mi>k</mi><mo>∗</mo></msubsup>','u_k^*'),('<mover><mi>i</mi><mo>^</mo></mover>','hat:i'),('<msup><mi>R</mi><mn>2</mn></msup>','R')]
  for markup,key in cases:
   node=B['Document'](markup).root.children[0];self.assertEqual(B['atom'](node),key)
 def test_brief_reference_and_no_detailed_citation_moved_to_end(self):
  for manifest in (ROOT/'courses').glob('*/manifest.js'):
   for s in B['assignment'](manifest)['sections']:
    if s.get('kind')!='html':continue
    text=B['Document'](B['assignment'](ROOT/s['src'])['html']).root.text()
    for forbidden in ['教材依据：','课件对应：','印刷第','核读资料与适用范围','原创教学讲解','不把本材料称为教材逐页转录']:
     self.assertNotIn(forbidden,text,s['id'])
if __name__=='__main__':unittest.main()
