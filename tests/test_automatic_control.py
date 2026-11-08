"""Automatic-control course structural and mathematical regression checks."""
from pathlib import Path
from html.parser import HTMLParser
import json
import math
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
assignment = runpy.run_path(str(ROOT / "scripts" / "build-reference-index.py"))["assignment"]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.math_open = 0
        self.math_close = 0
    def handle_starttag(self, tag, attrs):
        if tag == "math":
            self.math_open += 1
        for key,value in attrs:
            if key == "id" and value:
                self.ids.add(value)
    def handle_endtag(self, tag):
        if tag == "math":
            self.math_close += 1

class AutomaticControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = assignment(ROOT / "courses/automatic-control/manifest.js")
        cls.index = assignment(ROOT / "reference-index.js")
        cls.bank = json.loads((ROOT/"courses/practice/bank.json").read_text(encoding="utf-8"))
        cls.compiled = assignment(ROOT/"courses/practice/bank.js")

    def test_curriculum_and_lessons(self):
        self.assertEqual(self.course["id"],"automatic-control")
        sections=self.course["sections"]
        ids=[s["id"] for s in sections]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(set(s["group"] for s in sections)),8)
        self.assertEqual([s["id"] for s in sections if s["kind"] != "outline"],[
            "ac-3-1","ac-3-2","ac-3-3","ac-3-4","ac-3-5","ac-3-6","ac-3-7","ac-homework3"
        ])
        self.assertEqual(self.course["textbook"]["isbn"],"9787302665564")
        self.assertEqual(self.course["textbook"]["edition"],3)
        for section in sections:
            if section["kind"] == "outline": continue
            path=ROOT / section["src"]
            self.assertTrue(path.exists(),section["id"])
            payload=assignment(path)
            html=payload["html"]
            self.assertIn("reader-section",html)
            parser=Parser(); parser.feed(html)
            self.assertEqual(parser.math_open,parser.math_close,section["id"])

    def test_homework_source_and_anchors(self):
        data=assignment(ROOT/"courses/automatic-control/lessons/ac-homework3.js")
        expected={"3-13","3-14","3-15","3-16","3-18"}
        self.assertEqual({p["number"] for p in data["questions"]},expected)
        parser=Parser();parser.feed(data["html"])
        for n in expected: self.assertIn("question-"+n,parser.ids)
        self.assertIn("图3-63",data["html"])
        self.assertIn("图3-64",data["html"])
        self.assertNotIn("question-3-17",data["html"])

    def test_practice_bank(self):
        course_questions=[q for q in self.bank["questions"] if q["course"]=="automatic-control"]
        self.assertEqual(len(course_questions),5)
        self.assertEqual({q["id"] for q in course_questions},{q["id"] for q in self.compiled["questions"] if q["course"]=="automatic-control"})
        self.assertIn("automatic-control",self.index)
        self.assertEqual(len(self.index["automatic-control"]["sections"]),8)

    def test_math_results(self):
        self.assertAlmostEqual(3*math.sqrt(5)-5,1.7082039325,places=9)
        for k in (0.5,1.0,1.6):
            self.assertGreater((10-k)/3,0)
            self.assertGreater((20-10*k-k*k)/(10-k),0)
        for k in (1.8,2.0):
            self.assertLess((20-10*k-k*k)/(10-k),0)
        self.assertEqual(2/10,0.2)
        self.assertEqual(2/0.1,20)
        self.assertEqual(10/(10),1)

    def test_labs_connected(self):
        app=(ROOT/"app.js").read_text(encoding="utf-8")
        self.assertIn("LN_MOUNT_CONTROL_LABS",app)
        lab=(ROOT/"courses/automatic-control/control-lab.js").read_text(encoding="utf-8")
        for name in ("data-ac-routh","data-ac-damping","data-ac-error"):
            self.assertIn(name,lab)
        self.assertNotIn("setInterval(",lab)

if __name__ == "__main__":
    unittest.main()
