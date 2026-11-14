"""Content migration regressions; these checks do not certify teaching quality."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import unittest
ROOT=Path(__file__).resolve().parents[1]
REF=runpy.run_path(str(ROOT/'scripts/build-reference-index.py'))
class ContentIntegration(unittest.TestCase):
    def test_published_definition_sources_keep_their_anchors(self):
        glossary=runpy.run_path(str(ROOT/'scripts/build-glossary.py'))['build']()
        for path in (ROOT/'courses').glob('*/definition-anchors.json'):
            entries={e['id']:e for e in glossary[path.parent.name]['entries']}
            for identifier,anchor in json.loads(path.read_text()).items():
                self.assertEqual(entries[identifier]['source']['anchor'],anchor,identifier)
    def test_registered_material_does_not_reintroduce_generated_template(self):
        count=0
        for path in (ROOT/'courses').glob('*/manifest.js'):
            course=REF['assignment'](path)
            for section in course['sections']:
                count+=1
                if section['kind']=='outline':
                    self.assertNotIn('src',section)
                    continue
                payload=REF['assignment'](ROOT/section['src']);body=payload.get('html','')
                self.assertNotIn('LN-UNDERSTANDING:BEGIN',body)
                self.assertNotIn('data-learning-standard="understanding-v1"',body)
                self.assertNotIn('katex-error',body)
                if section['kind']=='html':self.assertTrue(body.strip())
        self.assertGreaterEqual(count,311)  # Additional real courses may register more routes.
        self.assertFalse((ROOT/'scripts/build-electrical-understanding.py').exists())
        self.assertNotIn('render_understanding',(ROOT/'scripts/build-highschool.py').read_text())
    def test_user_pdf_scientific_svg_is_preserved(self):
        fingerprint=json.loads((ROOT/'courses/electrical-machines/pdf-source-fingerprints.json').read_text())
        for section,expected in fingerprint['svgSHA256'].items():
            if section=='transformer-homework':continue  # Separately transcribed and covered by homework conversion tests.
            h=REF['assignment'](ROOT/'courses/electrical-machines/lessons'/(section+'.js'))['html']
            actual=[hashlib.sha256(s.encode()).hexdigest() for s in re.findall(r'<svg\b.*?</svg>',h,re.S)]
            if section=='transformer-quickref':
                # Raster quickref withdrawn; the stable route now uses the existing native formula index.
                canonical=REF['assignment'](ROOT/'courses/electrical-machines/lessons/transformer-formulas.js')['html']
                self.assertTrue(h.startswith(canonical))
                expected_native=[hashlib.sha256(x.encode()).hexdigest() for x in re.findall(r'<svg\b.*?</svg>',canonical,re.S)]
                self.assertEqual(actual,expected_native)
            else:
                self.assertEqual(actual,expected,section)
