"""Run with: python -m unittest discover -s tests -v. No extra dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import cmath
import json
import math
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / 'courses/electrical-machines'


def assignment(path):
    source = path.read_text('utf-8-sig').strip()
    return json.loads(source[source.rfind(']=') + 2:-1]) if ']=' in source else json.loads(source.split('=', 1)[1][:-1])


class Elements(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=True)
        self.ids, self.urls, self.tags, self.handlers = set(), [], [], []
        self.feed(markup)

    def handle_starttag(self, tag, pairs):
        self.tags.append(tag)
        attrs = dict(pairs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name, value in pairs:
            if name in ('src', 'href') and value:
                self.urls.append(value)
            if name.startswith('on'):
                self.handlers.append(name)


class CourseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = assignment(COURSE / 'manifest.js')
        cls.sections = {section['id']: section for section in cls.manifest['sections']}
        cls.payloads = {key: assignment(ROOT / value['src']) for key, value in cls.sections.items()}
        cls.markup = {key: Elements(value.get('html', '')) for key, value in cls.payloads.items()}

    def test_complete_chapters(self):
        self.assertEqual(len(self.sections), 45)
        self.assertEqual(len({section['group'] for section in self.sections.values()}), 3)
        self.assertIn('transformer-homework', self.sections)
        self.assertEqual(len([s for s in self.sections if s.startswith('transformer-sec2')]), 14)
        self.assertIn('winding-model', self.sections)

    def test_local_links_and_reference_targets(self):
        for key, document in self.markup.items():
            for url in document.urls:
                if url.startswith('https://'):
                    self.assertNotIn('chatgpt.site', url)
                elif url.startswith('#course/'):
                    parts = unquote(url).split('/')
                    self.assertEqual(parts[1], 'electrical-machines')
                    self.assertTrue(parts[2] in self.sections, (key, url))
                    if len(parts) > 3:
                        self.assertTrue(parts[3] in self.markup[parts[2]].ids, (key, url))
                else:
                    self.assertTrue((ROOT / unquote(urlsplit(url).path)).is_file(), (key, url))

    def test_no_audio_or_executable_imported_html(self):
        for path in COURSE.rglob('*'):
            self.assertNotIn(path.suffix.lower(), ('.mp3', '.wav', '.ogg', '.m4a', '.m3u8'))
        for key, document in self.markup.items():
            self.assertFalse(set(document.tags) & {'script', 'audio', 'iframe', 'object', 'embed', 'form'}, key)
            self.assertFalse(document.handlers, key)

    def test_homework_is_complete(self):
        payload = self.payloads['transformer-homework']
        self.assertEqual(len(payload['questions']), 13)
        self.assertEqual(len(payload['pages']), 13)
        self.assertEqual([q['number'] for q in payload['questions']], ['2-2', '2-3', '2-4', '2-6', '2-7', '2-12', '2-13', '2-17', '2-19', '2-20', '2-22', '2-25', '2-26'])
        for page in payload['pages']:
            self.assertTrue((ROOT / page['src']).is_file())
            self.assertGreater(page['width'], 1000)
        self.assertTrue((ROOT / payload['pdf']).is_file())

    def test_shared_fonts_and_no_broken_math(self):
        css = (ROOT / 'assets/katex/katex.min.css').read_text('utf-8')
        for url in re.findall(r'url\(([^)]+)\)', css):
            self.assertTrue((ROOT / 'assets/katex' / url.strip('"\'')).is_file(), url)
        for key, payload in self.payloads.items():
            self.assertNotIn('katex-error', payload.get('html', ''), key)
        self.assertTrue((ROOT / 'assets/katex/LICENSE').is_file())

    def test_quick_reference_pages_work_without_pdf_plugin(self):
        pages = self.payloads['transformer-quickref']['pages']
        self.assertEqual(len(pages), 6)
        for page in pages:
            self.assertTrue((ROOT / page['src']).is_file())


class HomeworkCalculations(unittest.TestCase):
    def test_yd_line_and_phase_values(self):
        self.assertAlmostEqual(5000 / (math.sqrt(3) * 10), 288.6751346, places=6)
        self.assertAlmostEqual(5000 / (math.sqrt(3) * 6.3), 458.2144994, places=6)
        self.assertAlmostEqual(5000 / (3 * 6.3), 264.5502646, places=6)

    def test_full_t_equivalent_2_19(self):
        ratio = 876 / 260
        secondary_current = 144 - 108j
        e2 = 6000 + (.15 + .964j) * secondary_current
        im_secondary = e2 / ((1250 + 12600j) / ratio ** 2)
        i1 = (secondary_current + im_secondary) / ratio
        u1 = ratio * e2 + (2.19 + 15.4j) * i1
        self.assertAlmostEqual(abs(i1), 54.563, places=3)
        self.assertAlmostEqual(math.degrees(cmath.phase(i1)), -38.11, places=2)
        self.assertAlmostEqual(abs(u1), 21275.08, places=2)

    def test_serial_and_parallel_excitation_2_22(self):
        serial_r = 4900 / 5 ** 2
        serial_x = math.sqrt(2000 ** 2 - serial_r ** 2)
        self.assertAlmostEqual(serial_r, 196)
        self.assertAlmostEqual(serial_x, 1990.4, places=1)
        self.assertAlmostEqual(10000 ** 2 / 4900, 20408.163265, places=5)
        x_pu = math.sqrt(.052 ** 2 - .014 ** 2)
        self.assertAlmostEqual(100 * (.014 * .8 + x_pu * .6), 4.12, places=2)
        self.assertAlmostEqual(800000 / (800000 + 4900 + 14000), .9769203, places=6)
        self.assertAlmostEqual(math.sqrt(4900 / 14000), .591607978, places=8)

    def test_circulating_current_discrepancy_is_retained(self):
        z1 = .05 * 3050 ** 2 / (5600000 / 3)
        z2 = .055 * 3000 ** 2 / (3200000 / 3)
        current = 50 / (z1 + z2)
        self.assertAlmostEqual(current, 70.10, places=2)
        self.assertGreater(abs(current - 68.79), 1)

    def test_load_sharing_and_limit_2_26(self):
        weights = [180 / .07, 320 / .065]
        s1 = 400 * weights[0] / sum(weights)
        s2 = 400 - s1
        self.assertAlmostEqual(s1, 137.243402, places=5)
        self.assertAlmostEqual(s2, 262.756598, places=5)
        self.assertGreater(s2 / 320, s1 / 180)
        maximum = 320 + 320 * weights[0] / weights[1]
        self.assertAlmostEqual(maximum, 487.142857, places=5)


if __name__ == '__main__':
    unittest.main()
