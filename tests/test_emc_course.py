"""EMC curriculum integrity tests (structural only, not content certification)."""
from pathlib import Path
import json
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "courses" / "electromagnetic-compatibility"
ASSIGN = runpy.run_path(str(ROOT / "scripts" / "build-reference-index.py"))["assignment"]


class EMCCourseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curriculum = json.loads((DIR / "curriculum.json").read_text(encoding="utf-8"))
        cls.course = ASSIGN(DIR / "manifest.js")
        cls.graph = ASSIGN(DIR / "knowledge-map.js")

    def test_textbook_outline_and_routes(self):
        self.assertEqual(len(self.curriculum["chapters"]), 10)
        self.assertEqual(len(self.curriculum["sections"]), 40)
        self.assertEqual(sum(len(section["subsections"]) for section in self.curriculum["sections"]), 107)
        self.assertEqual(len(self.course["sections"]), 40)
        self.assertEqual({s["id"] for s in self.course["sections"]}, {s["id"] for s in self.curriculum["sections"]})
        self.assertEqual(len({s["id"] for s in self.course["sections"]}), 40)
        for entry in self.curriculum["sections"]:
            self.assertRegex(entry["number"], r"^\d{1,2}\.\d{1,2}$")
            section = next(s for s in self.course["sections"] if s["id"] == entry["id"])
            self.assertEqual(section["title"], entry["number"] + " " + entry["title"])
            self.assertEqual(section["group"], entry["group"])
            self.assertEqual(section["kind"], "html")
            self.assertEqual(section["textbookSection"], entry["number"])

    def test_lesson_files_have_source_page_and_subsection_anchors(self):
        for entry in self.curriculum["sections"]:
            with self.subTest(section=entry["id"]):
                section = next(s for s in self.course["sections"] if s["id"] == entry["id"])
                payload = ASSIGN(ROOT / section["src"])
                content = payload["html"]
                self.assertIn("印刷第" + str(entry["page"]) + "页", content)
                self.assertIn(entry["number"] + " " + entry["title"], content)
                for item in entry["subsections"]:
                    anchor = "part-" + item["number"].replace(".", "-")
                    self.assertIn('id="' + anchor + '"', content)
                    self.assertIn(item["number"] + " " + item["title"], content)

    def test_knowledge_map_only_links_real_reading_sections(self):
        ids = {s["id"] for s in self.course["sections"]}
        nodes = self.graph["nodes"]
        self.assertEqual(len(nodes), 40)
        self.assertEqual({n["section"] for n in nodes}, ids)
        for link in self.graph["links"]:
            self.assertIn(link["from"], ids)
            self.assertIn(link["to"], ids)
            self.assertTrue(link["description"])

    def test_glossary_matches_actual_source_passages(self):
        glossary = json.loads((DIR / "glossary.json").read_text(encoding="utf-8"))
        self.assertTrue(glossary["lazy"])
        for entry in glossary["terms"]:
            with self.subTest(term=entry["id"]):
                section = next(s for s in self.course["sections"] if s["id"] == entry["section"])
                html = ASSIGN(ROOT / section["src"])["html"]
                self.assertIn(entry["match"], re.sub(r"<[^>]+>", "", html))

    def test_original_figures_are_captioned_and_indexed(self):
        ref = ASSIGN(ROOT / "reference-index.js")["electromagnetic-compatibility"]
        for section, anchor, label in (
            ("emc-2-2", "emc-capacitive-figure", "2.2.1"),
            ("emc-2-2", "emc-mutual-figure", "2.2.2"),
            ("emc-4-4", "emc-shield-wave", "4.4.1"),
            ("emc-5-4", "emc-mains-filter", "5.4.1"),
            ("emc-10-3", "emc-switching-lc", "10.3.1"),
            ("emc-10-3", "emc-gis-reflection", "10.3.2"),
            ("emc-4-3", "emc-magnetic-reluctance", "4.3.1"),
            ("emc-4-3", "emc-eddy-shortturn", "4.3.2"),
            ("emc-6-2", "emc-current-probe-schematic", "6.2.1"),
            ("emc-6-2", "emc-emi-receiver-chain", "6.2.2"),
            ("emc-8-1", "emc-rcl-nonideal", "8.1.1"),
            ("emc-8-1", "emc-decoupling-loop", "8.1.2"),
            ("emc-8-2", "emc-line-terminations", "8.2.1"),
            ("emc-8-2", "emc-wave-bounce", "8.2.2"),
            ("emc-8-3", "emc-pcb-return-figure", "8.3.1"),
        ):
            html = ASSIGN(ROOT / next(s["src"] for s in self.course["sections"] if s["id"] == section))["html"]
            self.assertIn('id="' + anchor + '"', html)
            self.assertIn("图 " + label, html)
            self.assertIn((anchor, label), [(f["anchor"], f["number"]) for f in ref["sections"][section]["figures"]])



    def test_deep_lesson_math_and_interactives(self):
        import xml.etree.ElementTree as ET
        ref = ASSIGN(ROOT / "reference-index.js")["electromagnetic-compatibility"]
        for section_id in ("emc-2-2", "emc-4-3", "emc-4-4", "emc-5-4", "emc-6-2", "emc-8-1", "emc-8-2", "emc-10-3"):
            section = next(s for s in self.course["sections"] if s["id"] == section_id)
            html = ASSIGN(ROOT / section["src"])["html"]
            self.assertIn('data-emc-lab=', html)
            self.assertGreaterEqual(html.count('class="math display"'), 3)
            displays = list(re.finditer(r'<math\b[^>]*>.*?</math>', html, re.S))
            self.assertEqual(len(displays), len(ref["sections"][section_id]["equations"]))
            for display in displays:
                ET.fromstring(display.group(0))
            self.assertIn("<figure ", html)

if __name__ == "__main__":
    unittest.main()
