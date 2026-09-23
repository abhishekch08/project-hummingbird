"""Check the specific decision risks exposed by the CH02 scenario model."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
from ch02_concurrency import CONFIG, evaluate  # noqa: E402


class ConcurrencyScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text())
        cls.result = evaluate(cls.config)
        cls.modes = {m['id']: m for m in cls.result['modes']}

    def test_mode_eight_candidates_and_separate_stress(self):
        candidates = [m for m in self.modes.values() if m['classification'] == 'candidate']
        stress = [m for m in self.modes.values() if m['classification'] == 'stress']
        self.assertEqual(len(candidates), 8)
        self.assertEqual(len(stress), 2)
        self.assertEqual(self.modes['deep_sleep']['guarded_host_payload_bps'], 0)
        self.assertIsNone(self.modes['deep_sleep']['minimum_illustrative_bus_clock_hz_at_assumed_efficiency'])

    def test_optical_port_count_is_not_simultaneous_adc_count(self):
        scan = self.modes['optical_spectroscopy']
        self.assertEqual(scan['active_sensor_channels']['OPT'], 12)
        self.assertEqual(scan['adc_occupancy']['OPT'], 8)
        self.assertEqual(scan['required_conversions_per_s']['OPT'], 24_000)
        self.assertEqual(scan['minimum_average_conversions_per_s_per_ADC']['OPT'], 3_000)
        optical = next(s for s in scan['streams'] if s['bank'] == 'OPT')
        self.assertEqual(optical['sample_rate_hz_per_PD_per_wavelength'], 250)
        self.assertEqual(optical['time_slots'], 2)
        self.assertFalse(scan['bank_conflicts'])

    def test_bio_and_optical_collisions_are_visible(self):
        conflict = self.modes['resource_conflict_probe']
        self.assertEqual(conflict['adc_occupancy']['BIO'], 10)
        self.assertEqual(conflict['adc_occupancy']['OPT'], 12)
        self.assertTrue(any('BIO' in item for item in conflict['bank_conflicts']))
        self.assertTrue(any('OPT' in item for item in conflict['bank_conflicts']))
        self.assertFalse(self.modes['research_raw']['bank_conflicts'])

    def test_fast_adc_stress_breaks_illustrative_host_window(self):
        base, fast = self.modes['research_raw'], self.modes['research_fast_stress']
        self.assertEqual(fast['raw_payload_bps'] - base['raw_payload_bps'], 32_000_000)
        self.assertGreater(fast['guarded_host_payload_bps'], 64_000_000 * 0.7)
        self.assertIsNone(fast['first_illustrative_clock_meeting_guard_hz'])
        self.assertEqual(base['first_illustrative_clock_meeting_guard_hz'], 32_000_000)
        self.assertEqual(fast['aggregate_sample_groups_per_s'] - base['aggregate_sample_groups_per_s'], 1_000_000)

    def test_no_battery_current_is_inferred_from_led_output(self):
        for mode in self.modes.values():
            self.assertIsNone(mode['battery_peak_current_ma'])
        self.assertEqual(self.modes['research_raw']['led_output_current_ma_candidate_max'], 300)
        self.assertEqual(self.modes['resource_conflict_probe']['led_output_current_ma_candidate_max'], 2400)

    def test_fails_if_optical_phase_count_is_inconsistent(self):
        changed = copy.deepcopy(self.config)
        changed['streams']['opt12_scan_2000']['wavelength_phases'] = 7
        with self.assertRaises(AssertionError):
            evaluate(changed)

    def test_signal_contact_scenarios_exclude_power_ground(self):
        lower = self.result['signal_contact_scenarios']['optimistic_sensor_to_ASIC']
        upper = self.result['signal_contact_scenarios']['less_shared_sensor_to_ASIC']
        self.assertLess(lower, upper)
        self.assertEqual(upper - lower, 16)
        self.assertIn('power and ground', self.config['signal_contact_scenarios']['excluded'])


if __name__ == '__main__':
    unittest.main()
