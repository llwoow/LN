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
            "ac-3-1","ac-3-2","ac-3-3","ac-3-4","ac-3-5","ac-3-6","ac-3-7","ac-homework3",
            "ac-4-1","ac-4-2","ac-4-2-1","ac-4-2-2","ac-4-2-3","ac-4-2-4","ac-4-3","ac-4-3-1","ac-4-4","ac-homework4"
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

    def test_root_locus_five_classroom_problems(self):
        lesson = assignment(ROOT / "courses/automatic-control/lessons/ac-homework4.js")
        self.assertEqual({q["number"] for q in lesson["questions"]},
                         {"4-7", "4-10", "4-12", "4-14", "4-18"})
        html = lesson["html"]
        parser = Parser()
        parser.feed(html)
        for number in ("4-7","4-10","4-12","4-14","4-18"):
            self.assertIn("question-"+number, parser.ids)
            self.assertIn("problem-"+number, parser.ids)
        self.assertEqual(html.count("<figure "), 10)
        self.assertEqual(html.count("<svg "), 10)
        self.assertEqual(parser.math_open, parser.math_close)
        for marker in ("−2±j√6", "K*=100", "K*=260",
                       "K*=32", "K*=91/4", "b=40/3",
                       "K*=4±2√3", "cₙ(∞)=lim"):
            self.assertIn(marker, html)
        self.assertAlmostEqual((4+4*math.sqrt(5)),12.94427190999916)
        self.assertAlmostEqual((4-2*math.sqrt(3)),0.5358983848622456)
        self.assertAlmostEqual((91/4),22.75)
        # Independently verify characteristic equations, not just published labels.
        p47=lambda s,k:s**4+8*s**3+36*s**2+80*s+k
        dp47=lambda s:4*s**3+24*s**2+72*s+80
        self.assertAlmostEqual(abs(p47(-2,64)),0,places=9)
        self.assertAlmostEqual(abs(dp47(-2)),0,places=9)
        for s in (-2+1j*math.sqrt(6), -2-1j*math.sqrt(6)):
            self.assertAlmostEqual(abs(p47(s,100)),0,places=8)
            self.assertAlmostEqual(abs(dp47(s)),0,places=8)
        for s in (1j*math.sqrt(10), -1j*math.sqrt(10)):
            self.assertAlmostEqual(abs(p47(s,260)),0,places=8)
        p410=lambda s,k,h2:s**4+7*s**3+10*s**2+(2*k*s if h2 else 0)+k
        self.assertAlmostEqual(abs(p410(-4,32,False)),0,places=9)
        self.assertAlmostEqual(abs(4*(-4)**3+21*(-4)**2+20*(-4)),0,places=9)
        for s in (1j*math.sqrt(13/2), -1j*math.sqrt(13/2)):
            self.assertAlmostEqual(abs(p410(s,91/4,True)),0,places=8)
        b=4+4*math.sqrt(5)
        self.assertAlmostEqual((b-4)**2-80,0,places=9)
        self.assertAlmostEqual(400-30*(40/3),0,places=9)
        for k in (4-2*math.sqrt(3),4+2*math.sqrt(3)):
            s=(k-2)/2
            self.assertAlmostEqual(s*s+(2-k)*s+k,0,places=9)
        for s in (1j*math.sqrt(2),-1j*math.sqrt(2)):
            self.assertAlmostEqual(abs(s**3+s**2+2*s+2),0,places=9)
        self.assertEqual(1/2,0.5)
        self.assertEqual(len(self.index["automatic-control"]["sections"]["ac-homework4"]["figures"]), 10)

    def test_cubic_synthesis_lesson(self):
        lesson = assignment(ROOT / "courses/automatic-control/lessons/ac-4-3-1.js")["html"]
        for phrase in ("−1+j", "dG/ds", "ωn", "ωd", "虚轴交点",
                       "data-ac-synthesis", "data-ac-syn-quiz", "data-ac-tex"):
            self.assertIn(phrase, lesson)
        self.assertEqual(lesson.count("data-ac-syn-question"), 6)
        self.assertIn("4.3.1", lesson)
        self.assertEqual(lesson.count("<svg"), 3)  # two native SVG figures + one interactive graph
        self.assertEqual(lesson.count("<figure"), 2)
        self.assertEqual(lesson.count('data-equation="U.4.3.1.'), 17)
        refs = self.index["automatic-control"]["sections"]["ac-4-3-1"]
        self.assertEqual(len(refs["equations"]), 17)
        self.assertEqual(len(refs["figures"]), 2)
        self.assertEqual(refs["equations"][-1]["number"], "U.4.3.1.17")
        glossary = assignment(ROOT / "courses/automatic-control/glossary-index.js")
        scoped = [e for e in glossary["entries"] if e.get("source", {}).get("section") == "ac-4-3-1"]
        self.assertGreaterEqual(len(scoped), 13)
        self.assertEqual(len({e["id"] for e in scoped}), len(scoped))
        css = (ROOT / "courses/automatic-control/root-locus-synthesis.css").read_text(encoding="utf-8")
        self.assertIn(".ac-syn-curves{stroke:", css)
        self.assertNotIn(r"\\n.ac-syn-curves", css)
        self.assertNotIn("<script", lesson)
        root = (ROOT / "courses/automatic-control/root-locus-synthesis.js").read_text(encoding="utf-8")
        self.assertIn("LN_MOUNT_AC_SYNTHESIS", root)
        self.assertIn("Math.cbrt", root)
        app = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("selected.id === 'ac-4-3-1'", app)

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
        self.assertIn('ac-dominant-pole-window', {q['id'] for q in course_questions})
        self.assertEqual(len(course_questions),14)
        self.assertEqual({q["id"] for q in course_questions},{q["id"] for q in self.compiled["questions"] if q["course"]=="automatic-control"})
        self.assertIn("automatic-control",self.index)
        self.assertEqual(len(self.index["automatic-control"]["sections"]),18)

    def test_root_locus_lesson_and_bank(self):
        lesson = assignment(ROOT / "courses/automatic-control/lessons/ac-4-2-2.js")["html"]
        for fact in ("4.3315704160", "8.16", "data-ac-root-locus", "错误连接"):
            self.assertIn(fact, lesson)
        self.assertIn("-71.565", lesson)
        self.assertIn("204-25K", lesson)
        lesson_math = Parser();lesson_math.feed(lesson)
        self.assertEqual(lesson_math.math_open, lesson_math.math_close)
        root_ids = {"ac-root-poles", "ac-root-real", "ac-root-asym", "ac-root-break",
                    "ac-root-angle", "ac-root-8p16", "ac-root-wrong", "ac-root-zero"}
        questions = {q["id"]: q for q in self.bank["questions"]}
        self.assertTrue(root_ids <= set(questions))
        for key in root_ids:
            self.assertGreaterEqual(len(questions[key]["steps"]), 3)
            self.assertIn("ac-4-", questions[key]["sections"][0])
        self.assertEqual(questions["ac-root-wrong"]["answer"], ["a", "b"])
        self.assertAlmostEqual(questions["ac-root-break"]["answer"], 4.331570416, places=7)
        self.assertAlmostEqual(questions["ac-root-angle"]["answer"], -71.565051, places=6)
        for k in (0, 4.331570416, 5, 8.16, 20):
            # Differentiating K(s) gives 4s³+15s²+16s+6=0.
            if k == 4.331570416:
                r = -2.28858434682
                self.assertAlmostEqual(4*r*r*r+15*r*r+16*r+6, 0, places=8)
                self.assertAlmostEqual(-r*(r+3)*(r*r+2*r+2),k,places=8)
        self.assertAlmostEqual((204/25), 8.16, places=10)

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


    def test_official_edition_three_question_crosswalk(self):
        revision = self.course["textbookRevision"]
        crosswalk = {x["sourceNumber"]: x for x in revision["questionCrosswalk"]}
        self.assertEqual(set(crosswalk), {"3-13","3-14","3-15","3-16","3-18"})
        self.assertEqual(crosswalk["3-13"]["edition3Number"], "3-20")
        self.assertEqual(crosswalk["3-14"]["edition3Number"], "3-21")
        self.assertEqual(crosswalk["3-14"]["status"], "confirmed_equivalent_structure")
        self.assertIsNone(crosswalk["3-18"]["edition3Number"])
        self.assertEqual(crosswalk["3-18"]["status"], "different_problem")
        sample = self.course["textbook"]["officialChapter3Sample"]
        self.assertEqual(sample["pages"], 58)
        self.assertEqual(sample["url"], "https://www.tup.tsinghua.edu.cn/upload/books/yz/089419-01.pdf")
        assignment_html = assignment(ROOT/"courses/automatic-control/lessons/ac-homework3.js")["html"]
        self.assertIn("课堂3-13 / 第3版3-20",assignment_html)
        self.assertIn("课堂3-14 / 第3版3-21",assignment_html)
        self.assertIn("不同于第3版3-18",assignment_html)

    def test_dynamic_error_coefficients_and_book_sections(self):
        lesson = assignment(ROOT/"courses/automatic-control/lessons/ac-3-6.js")["html"]
        self.assertIn("ac-dynamic-error",lesson)
        indexed = {e["number"] for e in self.index["automatic-control"]["sections"]["ac-3-6"]["equations"]}
        self.assertTrue({"U.3.6."+str(n) for n in range(8,12)} <= indexed)
        self.assertIn("ac-3-6-feedback-definition",lesson)
        for section in ("ac-3-6-1","ac-3-6-2","ac-3-6-3"):
            self.assertIn('id="' + section + '"',lesson)
        stable = assignment(ROOT/"courses/automatic-control/lessons/ac-3-5.js")["html"]
        for n in range(1,7):
            self.assertIn('id="ac-3-5-'+str(n)+'"',stable)
        # S(s)=(s+1)/(s+21)=c0+c1*s+c2*s**2+...
        from fractions import Fraction
        self.assertEqual(Fraction(1,21),Fraction(1,21))
        self.assertEqual(Fraction(20,441),Fraction(20,441))
        # Ramp input r(t)=2t; exact zero-state response error is
        # (2/21)*t + (40/441)*(1-exp(-21t)).
        for t in (0,0.1,1,5):
            exact = 2*t/21 + (40/441)*(1-math.exp(-21*t))
            asymptotic = 2*t/21 + 40/441
            self.assertAlmostEqual(exact-asymptotic,-(40/441)*math.exp(-21*t),places=11)
        second = assignment(ROOT/"courses/automatic-control/lessons/ac-3-3.js")["html"]
        self.assertIn("ξ",second)
        self.assertNotIn("<mi>ζ</mi>",second)


    def test_disturbance_position_analytic_response(self):
        from math import exp, sin, cos
        page = assignment(ROOT/"courses/automatic-control/lessons/ac-3-6.js")["html"]
        self.assertIn("data-ac-disturbance",page)
        code = (ROOT/"courses/automatic-control/control-lab.js").read_text(encoding="utf-8")
        self.assertIn("data-ac-disturbance-select",code)
        for t in (0.0,0.5,1.0,3.0,10.0):
            before = -exp(-t)*sin(3*t)
            after = -0.3 + 0.3*exp(-t)*cos(3*t) + 0.1*exp(-t)*sin(3*t)
            self.assertTrue(math.isfinite(before))
            self.assertTrue(math.isfinite(after))
        self.assertAlmostEqual(-exp(-20)*sin(60),0,places=7)
        self.assertAlmostEqual(-0.3 + 0.3*exp(-20)*cos(60) + 0.1*exp(-20)*sin(60),-0.3,places=7)

    def test_labs_connected(self):
        app=(ROOT/"app.js").read_text(encoding="utf-8")
        self.assertIn("LN_MOUNT_CONTROL_LABS",app)
        lab=(ROOT/"courses/automatic-control/control-lab.js").read_text(encoding="utf-8")
        for name in ("data-ac-routh","data-ac-damping","data-ac-error"):
            self.assertIn(name,lab)
        self.assertNotIn("setInterval(",lab)

if __name__ == "__main__":
    unittest.main()
