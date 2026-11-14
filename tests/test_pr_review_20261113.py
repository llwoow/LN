"""Combined PR integration: stable learning data and independent model/diagram checks."""
import hashlib,json,math,re,runpy,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
B=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'));assignment=B['assignment'];Document=B['Document']
BASELINE_IDS=set(['em-start', 'em-load', 'em-flux', 'em-transformer-dc', 'em-fit', 'em-regen', 'em-power', 'em-transformer-calc', 'em-test-design', 'em-core-design', 'tr-rating', 'tr-nonlinear', 'tr-load', 'tr-node', 'tr-test', 'tr-group', 'tr-pu', 'tr-leading', 'tr-circulation', 'tr-zero', 'tr-star-negative', 'tr-auto', 'tr-transients', 'tr-burden', 'tr-calc-test', 'tr-calc-line', 'tr-calc-base', 'tr-calc-eff', 'tr-calc-parallel', 'tr-calc-auto', 'tr-calc-burden', 'tr-open-zero', 'tr-open-star', 'tr-open-initial', 'ac-ch3-313', 'ac-ch3-314', 'ac-ch3-315', 'ac-ch3-316', 'ac-ch3-318', 'ac-root-poles', 'ac-root-real', 'ac-root-asym', 'ac-root-break', 'ac-root-angle', 'ac-root-8p16', 'ac-root-wrong', 'ac-root-zero', 'emc-mode-decompose', 'emc-coupling-limits', 'emc-ground-loop', 'emc-shield-absorption', 'emc-filter-install', 'emc-lisn', 'emc-esd', 'emc-pcb-ground', 'emc-surge-device', 'emc-harmonics', 'emc-gis-vfto', 'emc-magnetic-cylinder', 'emc-probe-emf', 'emc-capacitor-resonance', 'emc-line-reflection-step', 'emc-ground-step', 'emc-lightning-lead-voltage', 'emc-impulse-shield-current', 'rd-loaded-divider', 'rd-c-integer', 'rd-probe-loading', 'rd-ground-ring', 'rd-shunt-scale', 'rd-offset-calibration', 'rd-alias-identity', 'rd-acquisition-settling', 'rd-uart-time', 'rd-backlog', 'rd-volatile-record', 'rd-deadline-time', 'rd-gate-peak', 'rd-buck-ripple', 'rd-inverter-phase', 'rd-bootstrap-refresh', 'rd-torque', 'rd-gear-inertia', 'rd-park-q', 'rd-current-gain', 'rd-trapezoid-time', 'rd-saturation', 'rd-command-age', 'rd-qos-freshness', 'rd-edge-evidence', 'rd-rl-exact', 'rd-euler-pole', 'rd-identifiability', 'rd-comparison', 'hw-2-2', 'hw-2-3', 'hw-2-4', 'hw-2-6', 'hw-2-7', 'hw-2-12', 'hw-2-13', 'hw-2-17', 'hw-2-19', 'hw-2-20', 'hw-2-22', 'hw-2-25', 'hw-2-26', 'hs-physics001-01', 'hs-physics001-02', 'hs-physics001-03', 'hs-physics001-04', 'hs-physics001-05', 'hs-physics001-06', 'hs-physics001-07', 'hs-physics001-08', 'hs-physics001-09', 'hs-physics001-10', 'hs-physics001-11', 'hs-physics001-12', 'hs-physics001-13', 'hs-physics001-14', 'hs-physics001-15', 'hs-physics001-16', 'hs-physics001-17', 'hs-physics001-18'])
BASELINE_SHA256='20f5545324aa3723e9e15597ff561d20efafe202a0eb038b43c2e779aa4d3e86'
class ReviewedPRs(unittest.TestCase):
 def test_all_125_published_question_payloads_and_order_survive(self):
  bank=json.loads((ROOT/'courses/practice/bank.json').read_text())
  self.assertEqual(bank['version'],1)
  # Raw-photo links in promptHtml were withdrawn on 2026-11-14; all semantic fields stay frozen.
  subset=[{k:v for k,v in q.items() if k!='promptHtml'} for q in bank['questions'] if q['id'] in BASELINE_IDS]
  self.assertEqual(len(subset),125)
  self.assertEqual(hashlib.sha256(json.dumps(subset,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),BASELINE_SHA256)
 def test_material_textbook_and_supplied_routes_coexist(self):
  course=assignment(ROOT/'courses/electrical-materials/manifest.js')
  book=[s for s in course['sections'] if s.get('textbookSection')]
  self.assertEqual(len(book),29)
  self.assertEqual(sum(s['kind']=='outline' for s in book),24)
  self.assertEqual({s['id'] for s in course['sections'] if s['id'].startswith('em-test-')},{'em-test-summary','em-test-fill','em-test-short','em-test-review'})
  for s in book:
   if s['kind']=='outline':self.assertNotIn('src',s)
  courses=(ROOT/'courses.js').read_text();self.assertEqual(courses.count('...window.LN_ELECTRICAL_MATERIALS,'),1)
 def test_new_supplied_and_dc_questions_use_real_source_anchors(self):
  qs=json.loads((ROOT/'courses/practice/bank.json').read_text())['questions']
  supplied=[q for q in qs if q['id'].startswith('materials-photo-')]
  dc=[q for q in qs if q['id'].startswith('dc-branch-') or q['id'] in {'dc-generator-rated-port','dc-total-brush-drop','dc-lap-wave-tradeoff'}]
  self.assertEqual(len(supplied),16);self.assertEqual(len(dc),5)
  self.assertTrue(all(q['type']=='open' for q in supplied))
  for q in supplied+dc:
   course=assignment(ROOT/'courses'/q['course']/'manifest.js');section=next(s for s in course['sections'] if s['id']==q['readingSection'])
   nodes=list(Document(assignment(ROOT/section['src'])['html']).root.walk())
   self.assertEqual(sum(n.attrs.get('id')==q['readingAnchor'] for n in nodes),1,q['id'])
 def test_ultimate_strength_marker_is_at_the_curve_maximum(self):
  s=assignment(ROOT/'courses/electrical-materials/lessons/em-2-5.js')['html']
  fig=next(n for n in Document(s).root.walk() if n.attrs.get('id')=='em-stress-strain')
  curve=next(n.attrs['d'] for n in fig.walk() if n.tag=='path' and n.attrs.get('stroke-width')=='4')
  cubics=[tuple(map(float,x)) for x in re.findall(r'C([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)',curve)]
  p0=cubics[0][-2:];c=cubics[1];p1,p2,p3=c[:2],c[2:4],c[4:]
  # Derivative of the cubic y coordinate; min pixel y is max engineering stress.
  aa=-p0[1]+3*p1[1]-3*p2[1]+p3[1];bb=2*(p0[1]-2*p1[1]+p2[1]);cc=p1[1]-p0[1]
  roots=[(-bb+sgn*math.sqrt(bb*bb-4*aa*cc))/(2*aa) for sgn in [-1,1]];t=next(x for x in roots if 0<x<1)
  point=lambda i:(1-t)**3*p0[i]+3*(1-t)**2*t*p1[i]+3*(1-t)*t*t*p2[i]+t**3*p3[i]
  marker=min([n for n in fig.walk() if n.tag=='circle'],key=lambda n:float(n.attrs['cy']))
  self.assertAlmostEqual(float(marker.attrs['cx']),point(0),places=2)
  self.assertAlmostEqual(float(marker.attrs['cy']),point(1),places=2)
 def test_potential_marker_has_horizontal_tangent(self):
  s=assignment(ROOT/'courses/electrical-materials/lessons/em-2-2.js')['html']
  fig=next(n for n in Document(s).root.walk() if n.attrs.get('id')=='em-potential-figure')
  curve=next(n.attrs['d'] for n in fig.walk() if n.tag=='path' and n.attrs.get('stroke-width')=='3.5')
  c=tuple(map(float,re.search(r'C([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)',curve).groups()))
  self.assertEqual(c[3],c[5])
 def test_scr_current_balance_is_consistent(self):
  for a1,a2,gate,cbo1,cbo2 in [(.45,.5,.002,0,0),(.2,.3,.001,1e-6,2e-6),(.4,.55,.0005,4e-6,2e-6)]:
   ia=(a2*gate+cbo1+cbo2)/(1-a1-a2);ik=ia+gate;ic1=a1*ia+cbo1;ic2=a2*ik+cbo2
   self.assertAlmostEqual(ia,ic1+ic2);self.assertAlmostEqual(ik,ia+gate)
  self.assertAlmostEqual((.5*.002)/(1-.45-.5),.02)
if __name__=='__main__':unittest.main()
