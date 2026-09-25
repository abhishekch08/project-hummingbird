"""Behavioral CH05 corner cases; synthetic time is not an oscillator measurement."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
import ch05_timing as timing  # noqa: E402


class TimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(timing.CONFIG.read_text())
        cls.p = timing.prepare(cls.original)
        cls.routes = [(x['source'], x['target']) for x in cls.original['trigger_routes']]

    def test_analytical_tick_and_drift_are_not_accuracy(self):
        p = self.p
        self.assertAlmostEqual(1_000_000 / p['aon_clock_hz'], 30.517578125)
        self.assertEqual(timing.event_budget(p, p['aon_clock_hz'])['host_drift_bound_ns'], 2_000_000)
        self.assertEqual(timing.event_budget(p, p['aon_clock_hz'])['capture_quantization_bound_ns'], 30518)

    def test_exact_edge_and_next_edge(self):
        self.assertEqual(timing.next_edge(500, 2_000_000), 500)
        self.assertEqual(timing.next_edge(501, 2_000_000), 1000)
        self.assertEqual(timing.count_at(999, 1_000_000), 0)
        self.assertEqual(timing.count_at(1000, 1_000_000), 1)

    def test_half_range_wrap_and_reset_ambiguity(self):
        self.assertEqual(timing.extend_counter(250, 3, 8), 259)
        with self.assertRaisesRegex(timing.InvalidTiming, 'Ambiguous'):
            timing.extend_counter(250, 122, 8)

    def test_64_bit_overflow_never_rolls_to_zero(self):
        with self.assertRaisesRegex(timing.InvalidTiming, 'overflow'):
            timing.extend_counter((1 << 64) - 1, 0, 64)

    def test_sleep_wake_retains_monotonic_counter_and_declares_uncertainty(self):
        t = timing.Timekeeper(32768, 2_000_000)
        values = [t.observe(990_000_000), t.transition('sleep', 1_000_000_000),
                  t.observe(1_200_000_000), t.transition('awake', 1_250_001_000),
                  t.observe(1_260_000_000)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(t.wake_quantization_us, 32)
        self.assertLess(t.observe(1_260_000_000), 1_260_000)  # coarse anchor uncertainty persists
        with self.assertRaises(timing.InvalidTiming):
            t.observe(1_000_000_000)

    def test_continuous_clock_still_ticks_during_sleep(self):
        t = timing.Timekeeper(32768, 1_000_000, continuous=True)
        t.transition('sleep', 1_000_000_000)
        self.assertEqual(t.observe(1_000_001_000), 1_000_001)

    def test_simultaneous_events_keep_all_occurrences_and_priority(self):
        t = timing.Timekeeper(32768, 2_000_000)
        events = [{'source': 'GPIO', 'time_ns': 100_001},
                  {'source': 'LED_PULSE', 'time_ns': 100_001},
                  {'source': 'LED_PULSE', 'time_ns': 100_001}]
        out = timing.trigger_events(events, self.p, t, self.routes)
        self.assertEqual([e['source'] for e in out], ['LED_PULSE', 'LED_PULSE', 'GPIO'])
        self.assertEqual([e['sequence'] for e in out], [0, 1, 2])
        self.assertEqual([e['event_ns'] for e in out], [100_001] * 3)
        self.assertEqual(out[0]['sample_timestamp_us'], out[2]['sample_timestamp_us'])
        self.assertGreater(out[0]['capture_ns_upper'], 100_001)

    def test_cross_domain_sample_latency_is_separate_from_capture(self):
        p = self.p
        t = timing.Timekeeper(32768, 2_000_000)
        e = timing.trigger_events([{'source': 'LED_PULSE', 'time_ns': 501}], p, t, self.routes)[0]
        self.assertEqual(e['capture_ns_upper'], 1000)
        self.assertEqual(e['sample_ns_upper'], 6000)  # CDC 500 ns + dispatch 500 ns + 4 us sensor
        self.assertEqual(e['sample_timestamp_us'], 6)
        self.assertEqual(e['budget']['sample_time_vs_event_bound_ns'], 6500)

    def test_missing_sleep_destination_contract_fails_closed(self):
        t = timing.Timekeeper(32768, 2_000_000)
        t.transition('sleep', 1_000)
        with self.assertRaisesRegex(timing.InvalidTiming, 'off in sleep'):
            timing.trigger_events([{'source': 'GPIO', 'time_ns': 2_000}], self.p, t, self.routes)
        budget = timing.event_budget(self.p, 32768, asleep=True)
        self.assertEqual(budget['capture_quantization_bound_ns'], 30518)
        self.assertIsNone(budget['sample_time_vs_event_bound_ns'])

    def test_malformed_event_fails_as_timing_error(self):
        t = timing.Timekeeper(32768, 2_000_000)
        with self.assertRaises(timing.InvalidTiming):
            timing.trigger_events([{'source': 'GPIO'}], self.p, t, self.routes)

    def test_epoch_correction_does_not_step_monotonic_tick(self):
        t = timing.Timekeeper(32768, 1_000_000, continuous=True)
        before = t.observe(1_000_000)
        epoch = timing.EpochMap(20)
        epoch.synchronize(before, 5_000_000_000, 50_000)
        first = epoch.estimate(before + 1_000_000)
        epoch.synchronize(before + 1_000_000, 6_500_000_000, 70_000)
        self.assertNotEqual(first['epoch_ns'], epoch.estimate(before + 1_000_000)['epoch_ns'])
        self.assertEqual(t.observe(1_001_000_000), before + 1_000_000)
        self.assertEqual(first['uncertainty_bound_ns'], 50_000 + 20_000)

    def test_epoch_requires_anchor_and_rejects_backwards_update(self):
        e = timing.EpochMap(20)
        with self.assertRaises(timing.InvalidTiming):
            e.estimate(1)
        e.synchronize(10, 1_000, 0)
        with self.assertRaises(timing.InvalidTiming):
            e.synchronize(9, 9_000, 0)

    def test_imu_fifo_read_is_not_sample_time(self):
        sample = timing.imu_sample(1_270_000, 5, 3, 1_300_000, self.p)
        self.assertEqual(sample['sample_ns'], 1_248_000_000)
        self.assertEqual(sample['uncertainty_bound_ns'], 102_000)
        self.assertNotEqual(sample['read_arrival_us'] * 1000, sample['sample_ns'])
        with self.assertRaises(timing.InvalidTiming):
            timing.imu_sample(1_270_000, 5, 3, 1_240_000, self.p)

    def test_imu_rejects_missing_or_ambiguous_fifo_index(self):
        for index in (-1, 1 << 16, 4.5):
            with self.subTest(index=index), self.assertRaises(timing.InvalidTiming):
                timing.imu_sample(1_270_000, 0, index, 2_000_000, self.p)

    def test_missing_physical_inventory_or_unreviewed_measurement_fails(self):
        bad = copy.deepcopy(self.original)
        bad['physical_inputs'].pop('qualified_host_epoch_exchange_uncertainty')
        with self.assertRaises(timing.InvalidTiming):
            timing.prepare(bad)
        bad = copy.deepcopy(self.original)
        bad['physical_inputs']['qualified_host_epoch_exchange_uncertainty'] = 500
        with self.assertRaises(timing.InvalidTiming):
            timing.prepare(bad)

    def test_malformed_clock_metadata_and_bounds_fail(self):
        for field, value in [('unit', 'kHz'), ('value', True), ('value', 99999999),
                             ('source', ''), ('evidence', 'measured')]:
            with self.subTest(field=field, value=value):
                bad = copy.deepcopy(self.original)
                bad['parameters']['aon_clock_hz'][field] = value
                with self.assertRaises(timing.InvalidTiming):
                    timing.prepare(bad)

    def test_duplicate_or_unknown_routes_fail(self):
        bad = copy.deepcopy(self.original)
        bad['trigger_routes'][0] = bad['trigger_routes'][1]
        with self.assertRaises(timing.InvalidTiming):
            timing.prepare(bad)

    def test_report_cannot_claim_physical_pass(self):
        report = timing.generate(self.original)
        self.assertEqual(report['gate'], 'MODEL_PASS_PHYSICAL_HOLD')
        self.assertEqual(len(report['physical_inputs_missing']), 7)
        self.assertEqual(len(report['trigger_matrix']), 8)
        self.assertEqual([x['source'] for x in report['simultaneous_events']],
                         ['LED_PULSE', 'IMU_SYNC', 'GPIO'])


if __name__ == '__main__':
    unittest.main()
