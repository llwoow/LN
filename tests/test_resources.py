"""Check provenance, scope and runnable learning artifacts, not project popularity."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import csv
import hashlib
import json
import runpy
import unittest

ROOT=Path(__file__).resolve().parents[1]
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))


class LearningResources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'courses/resources/catalog.json').read_text())
        cls.resources={r['id']:r for r in cls.data['resources']}
        cls.courses={}
        for path in (ROOT/'courses').glob('*/manifest.js'):
            course=REF['assignment'](path);cls.courses[course['id']]=course

    def test_resources_resolve_to_real_lessons_and_downloads(self):
        covered=set()
        for resource in self.resources.values():
            self.assertGreaterEqual(len(resource['steps']),3)
            self.assertTrue(resource['license']);self.assertTrue(resource['limits'])
            for target in resource['targets']:
                course=self.courses[target['course']]
                self.assertIn(target['section'],[s['id'] for s in course['sections']]);covered.add(course['id'])
            for link in resource['links']+resource['evidence']:
                self.assertEqual(urlsplit(link['url']).scheme,'https')
            for link in resource['downloads']:self.assertTrue((ROOT/link['path']).is_file())
            if resource['verification']['executed']:self.assertTrue(resource['downloads'])
        self.assertEqual(covered,{c['id'] for c in self.courses.values() if not c.get('outlineOnly')})
        self.assertNotIn('/workspace/',json.dumps(self.data))
        anchor=self.resources['motor-catalogue-check']['localLesson'].split('/')[-1]
        section=next(s for s in self.courses['electrical-machines']['sections'] if s['id']=='dc-sec35')
        doc=REF['Document'](REF['assignment'](ROOT/section['src'])['html']).root
        self.assertTrue(any(n.attrs.get('id')==unquote(anchor) for n in doc.walk()))

    def test_unrun_or_inaccessible_projects_are_not_claimed_as_reproduced(self):
        for identifier in ['modelica-machines','femm','wpilib-sysid','openmct-measured-data']:
            self.assertFalse(self.resources[identifier]['verification']['executed'],identifier)

    def test_motor_catalogue_case_preserves_observable_model_error(self):
        folder=ROOT/'assets/practice/dc-specs'
        spec=json.loads((folder/'specification.json').read_text());result=json.loads((folder/'results.json').read_text())
        self.assertEqual(spec['sourceType'],'manufacturer_published_specification_not_raw_measurement')
        self.assertAlmostEqual(spec['rotor_inertia_kg_m2'],10.4e-7)
        self.assertGreater(result['baseline_speed_error_percent'],7)
        self.assertGreater(result['calibrated_speed_error_percent'],3)
        self.assertIn('not independently validated',result['interpretation'])
        self.assertLess(abs(result['dynamic_viscous_candidate']['energy_residual_J']),1e-4)
        self.assertGreater(result['dynamic_viscous_candidate']['peak_current_A'],spec['nominal_current_A'])
        rows=list(csv.DictReader((folder/'simulation.csv').read_text().splitlines()))
        self.assertIn('sim_rpm',rows[0]);self.assertEqual(len(rows),1001)

    def test_actual_penguin_data_has_reproducible_provenance(self):
        path=ROOT/'assets/practice/checks/data/penguins.csv';raw=path.read_bytes()
        self.assertEqual(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'25b46d384bf81f8399188500ea54917bb49d8890')
        rows=list(csv.DictReader(path.read_text().splitlines()));self.assertEqual(len(rows),344)
        self.assertEqual(sum(r['flipper_length_mm']!='NA' and r['body_mass_g']!='NA' for r in rows),342)


if __name__=='__main__':unittest.main()
