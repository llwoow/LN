"""Independent physics keys, actual file links and regression/data contracts."""
import hashlib,importlib.util,json,math,re,runpy,subprocess,sys,unittest
from pathlib import Path
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'courses/robot-drive-engineering'
assignment=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['assignment']
Document=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))['Document']
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class RobotDrive(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((BASE/'manuscript.json').read_text())
 def test_numeric_keys_independent_of_authored_answers(self):
  e={'rd-loaded-divider':12*(4000*4000/(4000+4000))/(2000+4000*4000/(4000+4000)),
     'rd-probe-loading':3*1e6/(1e5+1e6),'rd-shunt-scale':3.3/4096/.005/20*1000,
     'rd-acquisition-settling':-math.log(1/(2*4096))*10000*10e-12*1e6,
     'rd-uart-time':14*(1+8+1)/115200*1000,'rd-backlog':1000/(20000-18000),
     'rd-gate-peak':8e-9/40e-9,'rd-buck-ripple':(24-12)/100e-6*(12/24)/1e5,
     'rd-inverter-phase':24-(24+0+0)/3,'rd-torque':1.5*4*.02*2,
     'rd-gear-inertia':(2e-5+.02/(50*50))*1e6,'rd-park-q':-2*math.sin(math.pi/6),
     'rd-current-gain':.001*1000,'rd-trapezoid-time':2*(1/2)+(1-1**2/2)/1,
     'rd-command-age':170-0,'rd-rl-exact':6/2*(1-math.exp(-.002*2/.004)),
     'rd-euler-pole':1-.005*2/.004}
  q={q['id']:q for q in self.d['questions'] if q['type']=='numeric'}
  self.assertEqual(set(q),set(e))
  for k,v in e.items():self.assertAlmostEqual(q[k]['answer'],v,places=10,msg=k)
 def test_old_exercise_payloads_and_storage_version_unchanged(self):
  # Immutable digest of all 96 old records at baseline f8fad65, including ordering.
  # No Git history dependency: the same guard works in shallow CI/static archives.
  new=json.loads((ROOT/'courses/practice/bank.json').read_text())
  self.assertEqual(1,new['version'])
  old=[q for q in new['questions'] if q['course']!='robot-drive-engineering']
  digest=hashlib.sha256(json.dumps(old,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
  self.assertEqual(digest,'0006ce68e751ff19d1a1b6eda60ca226a6fd7465541feb640f3210b561f17e4d')
 def test_new_lesson_links_and_unique_ids(self):
  courses={c['id']:c for c in [assignment(p) for p in (ROOT/'courses').glob('*/manifest.js')]}
  for l in self.d['lessons']:
   doc=Document(assignment(BASE/'lessons'/(l['id']+'.js'))['html']).root
   ids=[n.attrs['id'] for n in doc.walk() if 'id' in n.attrs]
   self.assertEqual(len(ids),len(set(ids)),l['id'])
   for n in doc.walk():
    href=n.attrs.get('href','')
    if href.startswith('courses/'):
     self.assertTrue((ROOT/href.split('#')[0]).is_file(),(l['id'],href))
    if href.startswith('#course/'):
     parts=[unquote(x) for x in href[8:].split('/')];cid,sid=parts[:2]
     self.assertIn(cid,courses,(l['id'],href))
     if sid=='map':continue
     sections={s['id']:s for s in courses[cid]['sections']};self.assertIn(sid,sections,(l['id'],href))
     if len(parts)>2:
      dest=Document(assignment(ROOT/sections[sid]['src'])['html']).root
      self.assertTrue(any(x.attrs.get('id')==parts[2] for x in dest.walk()),href)
   self.assertFalse(any(ord(c)<32 and c not in '\n\t' for c in l['html']),l['id'])
 def test_original_computation_checks(self):
  m=module('rd_measurement',BASE/'files/measurement/reproduce.py');r=m.calculate()
  self.assertAlmostEqual(r['current_step_A'],.008056640625)
  self.assertAlmostEqual(r['cm_current_error_A'],.24)
  self.assertLess(r['alias_19k_1k_max_sample_difference'],1e-10)
  g=module('rd_gradient',BASE/'files/ai/gradient_descent.py').run()
  self.assertAlmostEqual(g['history'][1]['w'],.08)
  self.assertLess(g['history'][-1]['loss'],1e-9)
 def test_contract_and_clock_boundary_suite(self):
  r=subprocess.run([sys.executable,'-m','unittest','-v','test_command_guard.py'],cwd=BASE/'files/ai',capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr)
 def test_power_energy_and_trajectory_numbers(self):
  d=json.loads((BASE/'files/power-results.json').read_text())
  self.assertAlmostEqual(d['gate']['bootstrap_Cmin_F'],29e-9/.25)
  self.assertAlmostEqual(d['buck']['i_rms2_A2'],2**2+.6**2/12)
  # Independent phase voltages reconstruct αβ rather than repeating duty formulas.
  phase=d['inverter']['phase_average_V'] if 'inverter' in d else d['svpwm']['phase_average_V']
  self.assertAlmostEqual((2*phase[0]-phase[1]-phase[2])/3,10*math.cos(math.pi/6))
  self.assertAlmostEqual((phase[1]-phase[2])/math.sqrt(3),5)
if __name__=='__main__':unittest.main()
