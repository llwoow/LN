"""Independent checks for the DC chapter question keys and scientific assumptions."""
from pathlib import Path
import json
import math
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/"courses/electrical-machines/assessment"
NAMES=("dc-31-33.json","dc-34-36.json","dc-37-39.json","dc-integrated.json")

def load():
    return [q for name in NAMES
            for q in json.loads((FOLDER/name).read_text(encoding="utf-8"))["questions"]]

class DCComprehensiveAssessment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all=load()
        cls.index={q["id"]:q for q in cls.all}
    def test_total_group_type_and_id_coverage(self):
        self.assertEqual(len(self.all),60)
        self.assertEqual(len(self.index),60)
        kinds={t:sum(q["type"]==t for q in self.all) for t in ("single","multi","numeric","open")}
        self.assertEqual(kinds,{"single":21,"multi":10,"numeric":12,"open":17})
        for chapter,n in (("31",6),("32",6),("33",6),("34",6),("35",6),("36",6),("37",6),("38",8),("39",4),("mix",6)):
            self.assertEqual(sum(q["id"].startswith("dc-test-"+chapter+"-") for q in self.all),n)
        existing=json.loads((ROOT/"courses/practice/bank.json").read_text())
        self.assertEqual(existing["version"],1)
        self.assertFalse({q["id"] for q in existing["questions"]}&set(self.index))
        self.assertTrue(all(q["sections"][0]=="dc-chapter-test" for q in self.all))

    def test_independently_derived_numeric_keys(self):
        # Independent calculations from the stated physical model, not copied from the bank.
        pi=math.pi
        expected={
          "dc-test-31-04": (.8*220*50)/(2*pi*1000/60),
          "dc-test-32-03": 72/6,
          "dc-test-34-01": (4*600/(60*4))*.020*1500,
          "dc-test-34-02": (4*600/(2*pi*4))*.020*30,
          "dc-test-35-02": 240-20*.5-2,
          "dc-test-35-03": ((220-40*.5)*40-600)/1000,
          "dc-test-36-03": 10+220/220,
          "dc-test-37-02": 1200*(240-30*.4)/(240-20*.4),
          "dc-test-38-02": 240/60-.4,
          "dc-test-38-03": 1000*(180-20*.5)/(220-20*.5),
          "dc-test-mix-01": 1200*(200-30*.6)/(240-30*.6),
          "dc-test-mix-02": 1200*(200-(30*240/200)*.6)/(240-30*.6)*(240/200),
        }
        self.assertEqual({q["id"] for q in self.all if q["type"]=="numeric"},set(expected))
        for identifier,value in expected.items():
            self.assertAlmostEqual(self.index[identifier]["answer"],value,places=7,msg=identifier)
            self.assertLess(self.index[identifier]["tolerance"],1)

    def test_every_option_has_explanation_and_transfer(self):
        for q in self.all:
            self.assertGreaterEqual(len(q["steps"]),3,q["id"])
            self.assertTrue(q["hint"] and q["transfer"],q["id"])
            if q["type"] in ("single","multi"):
                self.assertTrue(all(o["feedback"]!=o["text"] and len(o["feedback"])>=16 for o in q["options"]),q["id"])
                self.assertEqual(len(set(q["answer"])),len(q["answer"]))
                self.assertEqual(len(q["answer"])==1,q["type"]=="single")
            else:self.assertGreaterEqual(len(q["rubric"]),3)
        self.assertEqual(sum("promptHtml" in q for q in self.all),5)

    def test_bundled_quiz_matches_source_files(self):
        run=subprocess.run([sys.executable,str(ROOT/"scripts/build-dc-chapter.py"),"--check"],
            cwd=str(ROOT),capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr+run.stdout)
        html=(ROOT/"courses/electrical-machines/lessons/dc-chapter-test.js").read_text()
        self.assertIn('data-practice-section=\\"dc-chapter-test\\"',html)
        for chapter in ("31","32","33","34","35","36","37","38","39","mix"):
            self.assertIn("dc-test-"+chapter+"-01",html)

if __name__=="__main__":
    unittest.main()
