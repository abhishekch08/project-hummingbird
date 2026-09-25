"""CH04 independent arithmetic cases and failure paths; synthetic figures are not vendor specs."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
from ch04_dataflow import (CH02, CONFIG, InvalidInput, PacketQueue, evaluate,
                           group_bytes, mode_rate, packet_for_window, prepare,
                           simulate_case)  # noqa: E402


class DataflowAccounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text())
        cls.ch02 = json.loads(CH02.read_text())
        cls.model = prepare(cls.config)
        cls.result = evaluate(cls.config)

    def test_hand_calculated_audio_packets_and_ch02_raw_reconciliation(self):
        fmt = self.model['format']
        audio = self.ch02['streams']['audio2_48000']
        # 2×(24 data + 8 quality) + 64 timestamp = 128 bit/group.
        self.assertEqual(group_bytes(audio, fmt, self.ch02['format_assumptions']), 16)
        self.assertEqual(packet_for_window(audio, fmt, self.ch02['format_assumptions'], 0),
                         (480, 7688))  # 480 × 16 B + 4 B header + 2 B CRC, aligned to 4 B.
        row = self.result['mode_rates']['audio']['raw']
        self.assertEqual(row['raw_payload_bps'], 2_317_648)
        self.assertEqual(row['framed_bytes_per_s'], 774424)
        self.assertEqual(row['packets_per_s'], 301)
        self.assertEqual(len(self.result['mode_rates']), 10)
        for mode in self.result['mode_rates'].values():
            self.assertLessEqual(mode['raw']['raw_payload_bps'],
                                 mode['raw']['framed_bytes_per_s'] * 8)
        self.assertEqual(self.result['gate']['physical'], 'FEASIBILITY_HOLD')

    def test_slow_sensor_batches_only_if_a_sample_exists(self):
        stream = self.ch02['streams']['temp2_1']
        f = self.model['format']
        ch02_f = self.ch02['format_assumptions']
        self.assertEqual(packet_for_window(stream, f, ch02_f, 0), (0, 0))
        self.assertEqual(packet_for_window(stream, f, ch02_f, 98), (0, 0))
        self.assertEqual(packet_for_window(stream, f, ch02_f, 99), (1, 24))
        row = mode_rate(self.model['modes']['daily_health'], self.model)
        self.assertEqual(row['sample_groups_per_s'], 233)
        self.assertEqual(row['packets_per_s'], 233)
        self.assertEqual(row['framed_bytes_per_s'], 6264)

    def test_partly_transferred_packet_keeps_its_descriptor(self):
        queue = PacketQueue(16)
        queue.add(100)
        queue.add(24)
        self.assertEqual(queue.memory_bytes, 156)
        self.assertEqual(queue.drain(99), 99)
        self.assertEqual(queue.memory_bytes, 57)  # 25 B payload + two descriptors.
        self.assertEqual(queue.drain(1), 1)
        self.assertEqual(queue.memory_bytes, 40)  # First descriptor freed only now.
        self.assertEqual(queue.drain(100), 24)
        self.assertEqual(queue.memory_bytes, 0)

    def test_burst_peak_sram_and_conservation(self):
        cases = {x['id']: x for x in self.result['two_cycle_queue_cases']}
        daily = cases['daily_host_wake']
        audio = cases['audio_host_wake']
        self.assertEqual(daily['queue_status'], 'BOUNDED_IN_SYNTHETIC_CYCLE')
        self.assertGreater(audio['peak_asic_fifo_with_descriptors_B'],
                           daily['peak_asic_fifo_with_descriptors_B'])
        self.assertLess(audio['minimum_total_sram_B_if_bounded'], 512 * 1024)
        for case in cases.values():
            self.assertEqual(case['produced_bytes_two_cycles'],
                             case['delivered_bytes_two_cycles'] + case['remaining_payload_bytes'])

    def test_average_deficit_cannot_be_cured_by_finite_fifo(self):
        cases = {x['id']: x for x in self.result['two_cycle_queue_cases']}
        slow = cases['research_host_16m']
        fast = cases['research_host_32m']
        self.assertEqual(slow['queue_status'], 'REPEATED_CYCLE_GROWTH')
        self.assertGreater(slow['second_cycle_backlog_growth_B']['asic_payload_B'], 0)
        self.assertIsNone(slow['minimum_total_sram_B_if_bounded'])
        self.assertEqual(fast['queue_status'], 'BOUNDED_IN_SYNTHETIC_CYCLE')
        self.assertEqual(fast['second_cycle_backlog_growth_B']['asic_payload_B'], 0)
        stress = cases['fast_stress_host_64m']
        self.assertEqual(stress['first_illustrative_asic_fifo_overflow_ms'], 50)
        self.assertIsNone(stress['sram_candidate_fit_if_bounded'])

    def test_ble_second_stage_can_fail_while_asic_queue_drains(self):
        cases = {x['id']: x for x in self.result['two_cycle_queue_cases']}
        daily, audio = cases['daily_host_ble'], cases['audio_host_ble']
        self.assertEqual(daily['queue_status'], 'BOUNDED_IN_SYNTHETIC_CYCLE')
        self.assertEqual(audio['second_cycle_backlog_growth_B']['asic_payload_B'], 0)
        self.assertGreater(audio['second_cycle_backlog_growth_B']['host_stage_B'], 0)
        self.assertEqual(audio['queue_status'], 'REPEATED_CYCLE_GROWTH')
        self.assertIsNotNone(audio['first_illustrative_host_stage_overflow_ms'])
        self.assertIsNone(audio['minimum_total_sram_B_if_bounded'])

    def test_nand_rate_fill_and_wear_are_separate_constraints(self):
        case = next(x for x in self.result['two_cycle_queue_cases']
                    if x['id'] == 'research_local_nand')
        self.assertEqual(case['queue_status'], 'BOUNDED_IN_SYNTHETIC_CYCLE')
        rates = self.result['mode_rates']['research_raw']['raw']
        self.assertEqual(rates['framed_bytes_per_s'], 1553120)
        projections = self.result['nand_capacity_and_wear_projections']
        self.assertEqual([x['synthetic_usable_bytes'] for x in projections],
                         [400_000_000, 1_600_000_000])
        self.assertAlmostEqual(projections[0]['full_if_continuous_minutes'],
                               400_000_000 / 1553120 / 60, places=3)
        self.assertFalse(any(x['one_assumed_day_fits_without_offload'] for x in projections))
        # A synthetic P/E limit with prior offload cannot fix the local capacity failure.
        self.assertGreater(projections[1]['synthetic_PE_limit_days_if_offloaded'],
                           projections[0]['synthetic_PE_limit_days_if_offloaded'])

    def test_sensitivity_changes_correct_queue_without_using_undeclared_bounds(self):
        base = {x['id']: x for x in self.result['two_cycle_queue_cases']}
        sensitivity = {x['change']: x['result'] for x in self.result['sensitivity']}
        audio = base['audio_host_wake']['peak_asic_fifo_with_descriptors_B']
        self.assertGreater(sensitivity['audio batch 10→20 ms (synthetic)']['peak_asic_fifo_with_descriptors_B'], audio)
        self.assertGreater(sensitivity['audio host unavailable 200→300 ms (synthetic)']['peak_asic_fifo_with_descriptors_B'], audio)
        self.assertEqual(sensitivity['daily BLE available goodput 1,000,000→100,000 bit/s (synthetic)']['queue_status'], 'REPEATED_CYCLE_GROWTH')
        self.assertEqual(sensitivity['research NAND busy 100→300 ms (synthetic)']['queue_status'], 'REPEATED_CYCLE_GROWTH')

    def test_feature_only_is_explicitly_smaller_but_not_raw_equivalent(self):
        mode = self.result['mode_rates']['sleep_neuroscience']
        raw, feature = mode['raw'], mode['feature_only_hypothesis']
        self.assertLess(feature['framed_bytes_per_s'], raw['framed_bytes_per_s'])
        self.assertEqual(feature['sample_groups_per_s'], len(self.model['modes']['sleep_neuroscience']['streams']))
        self.assertEqual(feature['packets_per_s'], feature['sample_groups_per_s'])
        self.assertEqual(raw['raw_payload_bps'], feature['raw_payload_bps'])
        self.assertEqual(self.result['evidence_class'], 'SYNTHETIC_CONDITIONAL')

    def test_input_units_provenance_and_physical_missing_fields_fail_closed(self):
        bad = copy.deepcopy(self.config)
        bad['format']['packet_crc_bytes']['unit'] = 'bit'
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        bad['memory']['workspace_kib']['source'] = ''
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        bad['physical_inputs']['measured_host_link_payload_wake_and_flow_control'] = {'value': 1}
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        del bad['physical_inputs']['qualified_memory_capacity_endurance_ecc_and_retention']
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        bad['availability_patterns']['host_sleep_200ms'][0]['duration_ms']['value'] = 250
        with self.assertRaises(InvalidInput):
            prepare(bad)  # 250 ms is within declared range but not balanced to 1000 ms.
        bad = copy.deepcopy(self.config)
        bad['format']['batch_window_ms']['value'] = 7
        bad['format']['batch_window_ms']['range'] = [7, 7]
        with self.assertRaises(InvalidInput):
            prepare(bad)

    def test_missing_ch02_stream_route_or_service_is_rejected(self):
        ch02 = copy.deepcopy(self.ch02)
        del ch02['streams']['imu_100']
        with self.assertRaises(InvalidInput):
            prepare(self.config, ch02)
        bad = copy.deepcopy(self.config)
        bad['cases'][0]['host_clock_hz'] = 12_000_000
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        bad['cases'][0]['route'] = 'local_nand'
        with self.assertRaises(InvalidInput):
            prepare(bad)
        bad = copy.deepcopy(self.config)
        bad['cases'][1]['id'] = bad['cases'][0]['id']
        with self.assertRaises(InvalidInput):
            prepare(bad)

    def test_empty_mode_has_no_sensor_packet_or_unbounded_queue(self):
        extra = {'id': 'sleep_transport_probe', 'mode': 'deep_sleep', 'route': 'host',
                 'host_clock_hz': 8000000, 'pattern': 'host_continuous'}
        row = simulate_case(self.model, extra)
        self.assertEqual(row['produced_bytes_two_cycles'], 0)
        self.assertEqual(row['queue_status'], 'BOUNDED_IN_SYNTHETIC_CYCLE')
        self.assertEqual(row['minimum_total_sram_B_if_bounded'], 192 * 1024)
        self.assertIsNone(row['first_illustrative_asic_fifo_overflow_ms'])


if __name__ == '__main__':
    unittest.main()
