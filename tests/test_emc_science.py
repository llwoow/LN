"""Independent numerical review of formulas used in the LN EMC lessons.

These tests verify arithmetic and stated model assumptions, not compliance with
current safety/EMC standards or a full scan-by-scan textbook audit.
"""
import cmath
import math
import unittest


class ScientificEMCReview(unittest.TestCase):
    def test_capacitive_coupling_phasor_and_limits(self):
        f, r2, c12, c2g, source = 1e6, 1e4, 5e-12, 45e-12, 10
        w = 2 * math.pi * f
        h = (1j * w * r2 * c12) / (1 + 1j * w * r2 * (c12 + c2g))
        self.assertAlmostEqual(abs(h), 0.09528905139886872, places=10)
        self.assertAlmostEqual(abs(h) * source, 0.9528905139886872, places=10)
        self.assertAlmostEqual(math.degrees(cmath.phase(h)), 17.6567871514, places=7)
        self.assertAlmostEqual(source * c12 / (c12 + c2g), 1.0)
        self.assertLess(abs(h) * source, 1.0)  # full model does not diverge

    def test_skin_depth_and_only_absorption_component(self):
        mu, sigma, thickness = 4 * math.pi * 1e-7, 5.8e7, 0.0001
        results = []
        for f in (1e6, 1e7):
            delta = math.sqrt(2 / (2 * math.pi * f * mu * sigma))
            results.append((delta * 1e6, 20 * math.log10(math.e) * thickness / delta))
        self.assertAlmostEqual(results[0][0], 66.08549310, places=5)
        self.assertAlmostEqual(results[0][1], 13.14341352, places=5)
        self.assertAlmostEqual(results[1][1], 41.56312297, places=5)

    def test_filter_and_y_capacitor(self):
        ldm, cx, cy = 100e-6, 0.1e-6, 2.2e-9
        f0 = 1 / (2 * math.pi * math.sqrt(ldm * cx))
        i = 2 * math.pi * 50 * cy * 230
        self.assertAlmostEqual(f0 / 1000, 50.32921210, places=6)
        self.assertAlmostEqual(i * 1000, 0.15896458827, places=7)

    def test_ideal_switching_initial_conditions(self):
        l, c, e = 1e-3, 0.1e-6, 100
        f0 = 1 / (2 * math.pi * math.sqrt(l * c))
        self.assertAlmostEqual(f0 / 1000, 15.9154943, places=6)
        for initial, expected_peak in ((0, 200), (-100, 300)):
            samples = [e + (initial - e) * math.cos(x * 2 * math.pi / 360)
                       for x in range(361)]
            self.assertAlmostEqual(max(samples), expected_peak, places=8)

    def test_helmholtz_and_room_shielding(self):
        mu0, n, i, radius = 4 * math.pi * 1e-7, 100, 1.0, .5
        b0 = (4 / 5) ** 1.5 * mu0 * n * i / radius
        self.assertAlmostEqual(b0 * 1e6, 179.851, delta=0.02)
        self.assertAlmostEqual(20 * math.log10(1 / .001), 60.0)
        # This does not imply that the whole enclosure provides 60dB.

    def test_gis_first_reflection_and_other_teaching_examples(self):
        z0 = 100.0
        self.assertAlmostEqual((1e12 - z0) / (1e12 + z0), 1.0, places=9)
        self.assertAlmostEqual((0 - z0) / (0 + z0), -1.0)
        self.assertAlmostEqual(.5 * 100e-12 * 2000**2 * 1000, 0.2)
        self.assertAlmostEqual(math.hypot(3, 4) / 10 * 100, 50.0)


if __name__ == "__main__":
    unittest.main()
