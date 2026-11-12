"""Structural and independent arithmetic checks for the 29 EMC additions.

These are teaching-model checks, not a substitute for a textbook page audit,
a calibrated EMC laboratory, or certification against an applicable standard.
"""
from collections import Counter
from html.parser import HTMLParser
import math
from pathlib import Path
import re
import runpy
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "courses" / "electromagnetic-compatibility" / "lessons"
ASSIGN = runpy.run_path(str(ROOT / "scripts" / "build-reference-index.py"))["assignment"]
DEEP_ALREADY = {
    "emc-2-2", "emc-4-3", "emc-4-4", "emc-5-4", "emc-6-2",
    "emc-8-1", "emc-8-2", "emc-9-2", "emc-10-2", "emc-10-3", "emc-10-4",
}


class IDs(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.ids = Counter()
        self.feed(content)
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids[value] += 1


class NewEMCAdditions(unittest.TestCase):
    def test_29_derived_formulas_diagrams_and_examples_are_indexed(self):
        manifest = ASSIGN(ROOT / "courses/electromagnetic-compatibility/manifest.js")
        index = ASSIGN(ROOT / "reference-index.js")["electromagnetic-compatibility"]
        augmented = [s for s in manifest["sections"] if s["id"] not in DEEP_ALREADY]
        self.assertEqual(len(augmented), 29)
        for s in augmented:
            sid = s["id"]
            with self.subTest(section=sid):
                html = ASSIGN(DIR / (sid + ".js"))["html"]
                ids = IDs(html).ids
                self.assertTrue(ids)
                self.assertTrue(all(n == 1 for n in ids.values()),
                                (sid, [k for k, n in ids.items() if n != 1]))
                self.assertEqual(ids["emc-deepen-" + sid], 1)
                self.assertEqual(ids["emc-deepen-svg-" + sid], 1)
                self.assertEqual(ids["emc-deepen-figure-" + sid], 1)
                self.assertEqual(ids["emc-deepen-example-" + sid], 1)
                self.assertRegex(html, r'<figure id="emc-deepen-figure-' + sid)
                self.assertIn("figcaption", html)
                formula = re.search(r'<div class="math display" data-equation="(D\.[^"]+)">'
                                    r'(<math[^>]*>.*?</math>)', html, re.S)
                self.assertIsNotNone(formula, sid)
                ET.fromstring(formula.group(2))
                targets = index["sections"][sid]
                self.assertIn(formula.group(1), [e["number"] for e in targets["equations"]])
                self.assertIn("emc-deepen-figure-" + sid,
                              [f["anchor"] for f in targets["figures"]])

    def test_original_calculation_assumptions_and_units(self):
        close = lambda actual, expected, rel=1e-6: self.assertTrue(
            math.isclose(actual, expected, rel_tol=rel, abs_tol=1e-10),
            (actual, expected))
        close(.12 * .5, .06)                                      # 1.1 V
        close(10 ** (60 / 20), 1000)                            # 1.2 microvolt
        close(.35 / (10e-9) / 1e6, 35)                          # 1.3 MHz
        close(.5 * 100e-12 * 2000**2 * 1000, .2)               # 1.4 mJ
        close(1e-9 * 200 / .2e-6, 1)                           # 2.1 A
        close((3e8 / 30e6) / (2 * math.pi), 1.59154943)        # 2.3 m
        close(20e-3 * 3, .06)                                  # 3.1 V
        close(2 * math.pi * 10e6 * 1e-6, 62.83185307)         # 3.2 ohm
        close(.10 * .02 * 1000, 2)                             # 3.3 mV
        close(10e-3 * 5 * .2 * 1000, 10)                       # 3.4 mV
        close(20 * math.log10(10 / .1), 40)                    # 4.1 dB
        close(3e-12 * (400 / 1e-6) * 1e3, 1.2)                 # 4.2 mA
        close(3e8 / (2 * .02) / 1e9, 7.5)                     # 4.5 GHz
        close(20 * math.log10(.3 / .03), 20)                   # 5.1 dB
        close(50 / (2 * math.pi * 100e-6) / 1e3, 79.5774715)  # 5.2 kHz
        close(50 / math.hypot(50, 2 * math.pi * 1e6 * 100e-6),
              .0793267, rel=1e-3)                             # 5.2 ratio
        close(.1**2 * 20, .2)                                  # 5.3 W
        close(20 * math.log10(1 / (1 + 9)), -20)              # 5.5 dB
        close(2 * .5**2 / .30, 1.66666667)                    # 6.1 m
        close(35 + 18 + 2 - 10, 45)                           # 6.3 dB microvolt/m
        close(3**2 / 377, .023872679)                         # 6.4 W/m2
        close(20e-9 / 100e-12, 200)                           # 7.1 V
        close(330 * 150e-12 * 1e9, 49.5)                     # 7.2 ns
        close(2000 / 330, 6.06060606)                         # 7.2 A
        close(5 / 5e-9, 1e9)                                  # 7.3 V/m
        close(5e-9 * 1 / 1e-9, 5)                             # 7.4 V
        close(.5e-12 * 2 / 1e-9 * 50, .05)                   # 8.3 V
        close(.2e-6 * 1000 / 1e-6, 200)                      # 9.1 V
        close(600 + 2 * (30 - 10), 640)                       # 9.3 V
        close(640 * 20 * 10e-6, .128)                          # 9.3 J
        close(15e-9 * .5 / 1e-9, 7.5)                        # 9.4 V
        close(math.sqrt(10**2 + 3**2 + 4**2), 11.18033989)   # 10.1 A
        close((10**2 + 3**2 + 4**2) / 10**2, 1.25)          # 10.1 copper ratio


if __name__ == "__main__":
    unittest.main()
