"""Independent edge-case checks of LN's dry-run command contract."""
import math
import unittest
from command_guard import Guard, packet

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.g = Guard(); self.g.observe('obs-0', 0); self.g.arm()

    def test_no_result_does_not_block_ticks(self):
        for t in range(251): self.g.tick(t)
        self.assertEqual(self.g.state, 'HOLD')
        self.assertEqual(self.g.reference_rad, 0)

    def test_order_rejection_does_not_replace_last_valid_target(self):
        self.assertEqual(self.g.accept(packet(2), 20), 'accepted')
        self.assertEqual(self.g.accept(packet(1,target_rad=-.9), 21), 'out_of_order')
        self.assertEqual(self.g.target_rad, .5)

    def test_local_capture_time_defines_freshness(self):
        self.assertEqual(self.g.accept(packet(1), 121), 'stale_or_future')
        self.assertEqual(self.g.accept(packet(1), -1), 'stale_or_future')
        self.assertEqual(self.g.accept(packet(1,'unknown'), 20), 'unknown_observation')
        # Server cannot refresh observation age by adding an invented remote timestamp.
        self.assertEqual(self.g.accept(packet(1,capture_ms=120),121), 'schema')

    def test_invalid_numbers_and_structure(self):
        self.assertEqual(self.g.accept('{bad json}',20), 'malformed')
        self.assertEqual(self.g.accept('{"target_rad": NaN}',20), 'malformed')
        self.assertEqual(self.g.accept(packet(1,target_rad=True),20), 'nonfinite_or_type')
        self.assertEqual(self.g.accept(packet(1,seq=True) if False else packet(True),20), 'out_of_order')
        self.assertEqual(self.g.accept(packet(1,target_rad=1.1),20), 'outside_limits')
        self.assertEqual(self.g.accept(packet(1,vmax_rad_s=.7),20), 'outside_limits')
        self.assertEqual(self.g.accept(packet(1,session='old-run'),20), 'identity')

    def test_rate_bound_timeout_and_no_hidden_rearming(self):
        self.g.tick(19)
        self.assertEqual(self.g.accept(packet(1),20), 'accepted')
        self.assertAlmostEqual(self.g.tick(20), .0004)
        for t in range(21,121): self.g.tick(t)
        value = self.g.reference_rad
        self.g.tick(121); self.assertEqual(self.g.state,'HOLD')
        self.g.tick(250); self.assertEqual(self.g.reference_rad,value)
        self.g.disarm()
        self.assertEqual(self.g.accept(packet(2),30),'disarmed')

    def test_negative_target_and_clock_rollback(self):
        self.g.tick(0); self.g.accept(packet(1,target_rad=-.5),0)
        self.assertAlmostEqual(self.g.tick(1),-.0004)
        with self.assertRaises(ValueError):self.g.tick(0)

if __name__ == '__main__':unittest.main()
