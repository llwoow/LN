"""Check new source anchors and selected quantitative claims against independent calculations."""
import cmath
import json
import math
from pathlib import Path
import runpy
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = runpy.run_path(str(ROOT / 'scripts/build-reference-index.py'))
assignment = REFERENCE['assignment']
Document = REFERENCE['Document']


class CurriculumRectification(unittest.TestCase):
    def test_new_routes_open_registered_reading_or_question(self):
        courses = {c['id']: c for c in (
            assignment(path) for path in (ROOT / 'courses').glob('*/manifest.js'))}
        sections = {(cid, s['id']): s for cid, c in courses.items() for s in c['sections']}
        questions = {q['id']: q for q in assignment(ROOT / 'courses/practice/bank.js')['questions']}
        for (cid, sid), section in sections.items():
            if 'manuscript' not in section and section.get('supplement') != 'study':
                continue
            body = Document(assignment(ROOT / section['src'])['html']).root
            for node in body.walk():
                href = unquote(node.attrs.get('href', ''))
                if not href.startswith(('#course/', '#practice/')):
                    continue
                with self.subTest(origin=f'{cid}/{sid}', href=href):
                    view, target_course, target_id, *anchor = href.split('/')
                    target = sections[(target_course, target_id)]
                    if view == '#practice':
                        self.assertEqual(len(anchor), 1)
                        question = questions[anchor[0]]
                        self.assertEqual(question['course'], target_course)
                        self.assertIn(target_id, question['sections'])
                    elif anchor:
                        doc = Document(assignment(ROOT / target['src'])['html']).root
                        self.assertEqual(sum(n.attrs.get('id') == anchor[0] for n in doc.walk()), 1)

    def test_motor_steady_example_satisfies_both_balances(self):
        speed, current = 16, 5.2
        self.assertAlmostEqual(2 * current + 0.1 * speed, 12)
        self.assertAlmostEqual(0.02 * speed + 0.2, 0.1 * current)
        # Input equals copper loss, mechanical load power and viscous loss.
        self.assertAlmostEqual(12 * current, 2 * current**2 + 0.2 * speed + 0.02 * speed**2)

    def test_loop_margins_match_nyquist_intersections(self):
        def loop(w):
            return 4 / (1 + 1j * w)**3

        phase_crossover = math.sqrt(3)
        self.assertAlmostEqual(loop(phase_crossover).imag, 0)
        self.assertAlmostEqual(loop(phase_crossover).real, -0.5)
        gain_crossover = math.sqrt(4**(2/3) - 1)
        self.assertAlmostEqual(abs(loop(gain_crossover)), 1)
        delay = (math.pi + cmath.phase(loop(gain_crossover))) / gain_crossover
        delayed = loop(gain_crossover) * cmath.exp(-1j * gain_crossover * delay)
        self.assertAlmostEqual(delay, 0.38425, places=5)
        self.assertAlmostEqual(abs(delayed + 1), 0)

    def test_thermal_peak_matches_direct_iteration(self):
        rise = 1 - math.exp(-0.5)
        peak = 0
        for _ in range(40):
            trough = peak * (1 - rise)
            peak = trough + (20 - trough) * rise
        self.assertAlmostEqual(peak, 12.45, places=2)
        self.assertGreater(peak, max(10, 20 * rise))
        self.assertAlmostEqual(peak * (1 - rise), 7.55, places=2)

    def test_synchronous_power_matches_complex_phasor(self):
        terminal = 230
        generated = 210 * cmath.exp(-1j * math.radians(20))
        current = (terminal - generated) / 4j
        power_kw = (3 * terminal * current.conjugate()).real / 1000
        self.assertAlmostEqual(power_kw, 12.39, places=2)
        torque = power_kw * 1000 / (1500 * 2 * math.pi / 60)
        self.assertAlmostEqual(torque, 78.87, delta=0.05)

    def test_dielectric_energy_density_uses_working_field(self):
        epsilon0 = 8.8541878128e-12
        densities = [epsilon0 * relative * field**2 / 2e3 for relative, field in ((4, 50e6), (10, 20e6))]
        self.assertAlmostEqual(densities[0], 44.27, places=2)
        self.assertAlmostEqual(densities[1], 17.71, places=2)
        self.assertGreater(densities[0], densities[1])


if __name__ == '__main__':
    unittest.main()
