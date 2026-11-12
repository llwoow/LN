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


    def test_transverse_cylinder_from_interface_conditions_and_eddy_turn(self):
        # Solve the four interface equations independently of the closed-form answer.
        a,b,mu=20.0,22.0,200.0
        rows=[[1,-1,-1/a**2,0,0],[1,-mu,mu/a**2,0,0],
              [0,1,1/b**2,-1/b**2,1],[0,mu,-mu/b**2,1/b**2,1]]
        for col in range(4):
            pivot=max(range(col,4),key=lambda r:abs(rows[r][col]))
            rows[col],rows[pivot]=rows[pivot],rows[col]
            value=rows[col][col];rows[col]=[x/value for x in rows[col]]
            for r in range(4):
                if r!=col:
                    factor=rows[r][col]
                    rows[r]=[x-factor*y for x,y in zip(rows[r],rows[col])]
        A,B,C,D=[row[-1] for row in rows]
        ratio=4*mu/((mu+1)**2-(mu-1)**2*(a/b)**2)
        self.assertAlmostEqual(A,ratio,places=12)
        self.assertAlmostEqual(A,B+C/a**2,places=12)
        self.assertAlmostEqual(A,mu*(B-C/a**2),places=12)
        self.assertAlmostEqual(20*math.log10(1/A),19.6373919583,places=7)
        for permeability,inner in [(1,a),(mu,b)]:
            self.assertAlmostEqual(4*permeability/((permeability+1)**2-(permeability-1)**2*(inner/b)**2),1)
        resistance, inductance, mutual = .1, 1e-6, .2e-6
        response = lambda f: 2 * math.pi * f * mutual / math.hypot(resistance, 2 * math.pi * f * inductance)
        self.assertLess(response(1000), response(1e5))
        self.assertAlmostEqual(response(1e8), mutual / inductance, delta=.001)
        # Neither current ratio nor simple cylinder formula certifies actual enclosure shielding.

    def test_active_filter_phase_requires_complex_sum(self):
        self.assertAlmostEqual(abs(1/(1+9)),.1)
        self.assertAlmostEqual(abs(1/(1-9)),.125)
        self.assertAlmostEqual(abs(1/(1-.9)),10)

    def test_probes_near_field_and_calibrated_current(self):
        f, m, current = 1e5, .5e-6, .1
        self.assertAlmostEqual(2 * math.pi * f * m * current * 1000, 31.4159265359, places=7)
        self.assertAlmostEqual(.5 * .1, .05)  # 0.5 ohm calibrated transfer impedance
        area, b_peak, f2 = 1e-4, 1e-6, 1e6
        self.assertAlmostEqual(2 * math.pi * f2 * area * b_peak * 1000, .6283185307, places=7)

    def test_capacitor_esl_esr_reality_vs_ideal_srf(self):
        c, esl, esr = 1e-6, 1e-9, .02
        f0 = 1 / (2 * math.pi * math.sqrt(c * esl))
        self.assertAlmostEqual(f0 / 1e6, 5.0329212104, places=8)
        impedance = lambda f: math.hypot(esr, 2 * math.pi * f * esl - 1 / (2 * math.pi * f * c))
        self.assertAlmostEqual(impedance(f0), esr, places=10)
        self.assertGreater(impedance(1e3), esr)
        self.assertGreater(impedance(100e6), esr)

    def test_lossless_line_source_and_load_reflections(self):
        vs, z0, zs, rs, speed, length = 3.3, 50.0, 10.0, 40.0, 2e8, .5
        launched = vs * z0 / (z0 + zs + rs)
        gamma_s = (zs + rs - z0) / (zs + rs + z0)
        self.assertAlmostEqual(launched, 1.65)
        self.assertAlmostEqual(gamma_s, 0.0)
        self.assertAlmostEqual(2 * launched, vs)  # ideal open ΓL=+1
        self.assertAlmostEqual(length / speed * 1e9, 2.5)
        self.assertAlmostEqual((0-z0)/(0+z0), -1)
        self.assertAlmostEqual((z0-z0)/(z0+z0), 0)
        gamma_s_unmatched = (zs-z0)/(zs+z0)
        self.assertLess(gamma_s_unmatched, 0)
        self.assertNotEqual(gamma_s_unmatched, 0)


    def test_hemisphere_ground_potential_and_step_model(self):
        rho, i, r0, r, a = 100.0, 100.0, .5, 2.0, .8
        potential = lambda radius: rho * i / (2 * math.pi * radius)
        self.assertAlmostEqual(potential(r0), 3183.0988618, places=5)
        self.assertAlmostEqual(rho / (2 * math.pi * r0), 31.830988618, places=6)
        self.assertAlmostEqual(potential(r) - potential(r + a), 227.36420442, delta=.02)
        self.assertGreater(potential(r), potential(r + a))

    def test_lightning_lead_inductance_is_not_device_clamping_voltage(self):
        inductance, ramp = .6e-6, 1000 / 1e-6
        self.assertAlmostEqual(inductance * ramp, 600.0)
        # Same R and di/dt cannot establish actual SPD residual voltage.

    def test_impulse_shield_parallel_inductors_and_parasitic_resonance(self):
        l1, l2 = 1e-6, 3e-6
        self.assertAlmostEqual(l1/(l1+l2), .25)
        circuit_l, cs = 1.5e-6, 1000e-12
        f0 = 1/(2*math.pi*math.sqrt(circuit_l*cs))
        self.assertAlmostEqual(f0/1e6, 4.10936296, places=5)
        self.assertAlmostEqual((2 * math.pi * f0)**2 * circuit_l * cs, 1.0)

if __name__ == "__main__":
    unittest.main()
