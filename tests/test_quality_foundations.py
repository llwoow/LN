"""Independently check quantities explained in the first LN content revision."""
import json
import math
from pathlib import Path
import unittest

BANK = Path(__file__).resolve().parents[1] / 'courses/practice/bank.json'


class QualityFoundationsTests(unittest.TestCase):
    def test_third_order_residues_and_crossing(self):
        epsilon = 0.01
        coefficients = ((1 + epsilon) / 10, -5 * epsilon / 36,
                        (epsilon - 4) / 20, (9 - epsilon) / 90)
        poles = (0, 1, 5, 10)
        for s in (0.25, 1, 2, 10):
            source = 5 * (s + 1 + epsilon) / (s * (s + 1) * (s + 5) * (s + 10))
            self.assertAlmostEqual(sum(a / (s + p) for a, p in zip(coefficients, poles)), source)
        self.assertAlmostEqual(sum(coefficients), 0)
        crossing_time = math.log(abs(coefficients[2] / coefficients[1])) / 4
        self.assertAlmostEqual(crossing_time, 1.24, delta=0.01)
        self.assertGreater(abs(coefficients[2] * math.exp(-5 * 0.2)),
                           abs(coefficients[1] * math.exp(-0.2)))

    def test_transformer_equivalents_return_same_terminal_current(self):
        voltage = 200
        series_current = voltage / complex(240, 320)
        parallel_current = voltage * (1 / (200**2 / 60) + 1 / (500j))
        self.assertAlmostEqual(series_current, parallel_current)
        self.assertAlmostEqual(abs(series_current), 0.5)
        self.assertAlmostEqual((voltage * series_current.conjugate()).real, 60)
        self.assertAlmostEqual(abs(complex(1.2, 1.6)) / (voltage / 5), 10 / voltage)

    def test_motor_timescale_and_back_emf(self):
        volts, resistance, inductance = 12, 2, 0.004
        tau = inductance / resistance
        limit_time = -tau * math.log1p(-2 / (volts / resistance))
        self.assertAlmostEqual(limit_time * 1000, 0.81, delta=0.01)
        # Midpoint integration of the frozen-rotor current during the first electrical time constant.
        count = 200
        integrated_current = sum(volts / resistance * (1 - math.exp(-(j + 0.5) / count))
                                 for j in range(count)) * tau / count
        angular_speed = 0.04 / 0.0002 * integrated_current
        self.assertAlmostEqual(angular_speed * 0.04, 0.035, delta=0.001)

    def test_lc_voltage_divider_matches_exercise(self):
        inductance, capacitance = 100e-6, 1e-6
        omega = 1 / math.sqrt(inductance * capacitance)

        def gain(factor, resistance):
            jw = complex(0, factor * omega)
            z_parallel = 1 / (1 / resistance + jw * capacitance)
            return abs(z_parallel / (jw * inductance + z_parallel))

        self.assertAlmostEqual(gain(1, 50), 5)
        self.assertAlmostEqual(gain(1, 10), 1)
        self.assertGreater(gain(0.7, 10), 1)
        exercises = json.loads(BANK.read_text(encoding='utf-8'))['questions']
        entry = next(q for q in exercises if q['id'] == 'emc-lc-natural-frequency-gain')
        self.assertAlmostEqual(entry['answer'], 20 * math.log10(gain(1, 20)))


if __name__ == '__main__':
    unittest.main()
