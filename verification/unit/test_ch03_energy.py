"""CH03 invariants and failure paths; invented data is never product evidence."""

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
from ch03_energy import (CONFIG, InvalidInput, evaluate, parameter, point, prepare,
                         simulate, solve_cell)  # noqa: E402


class EnergyAccounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text())
        cls.model = prepare(cls.config)
        cls.result = evaluate(cls.config)

    def test_quadratic_branch_and_infeasible_power(self):
        stable = solve_cell(4, 1, 3, 0, 2)
        self.assertAlmostEqual(stable['terminal_v'], 3)
        self.assertAlmostEqual(stable['current_a'], 1)
        self.assertEqual(stable['reason'], None)
        self.assertEqual(solve_cell(4, 1, 5, 0, 2)['reason'], 'NO_POWER_SOLUTION')
        self.assertEqual(solve_cell(4, 1, 3, 0, 3.1)['reason'], 'VOLTAGE_CUTOFF')
        with_direct = solve_cell(4, 1, 2, 0.1, 2)
        self.assertAlmostEqual(with_direct['terminal_v'], 4 - with_direct['current_a'])
        self.assertAlmostEqual(with_direct['terminal_v'] * (with_direct['current_a'] - 0.1), 2)

    def test_led_and_radio_draw_concurrently_without_current_double_count(self):
        pulse = next(p for p in self.model['phases'] if p['id'] == 'optical_and_radio')
        sense = next(p for p in self.model['phases'] if p['id'] == 'sense_and_send'
                     and p['p_startup_w'] == 0)
        self.assertIn('optical_led', pulse['active_blocks'])
        self.assertIn('host_rf', pulse['active_blocks'])
        self.assertGreater(point(pulse, self.model['cell'], 1)['current_a'],
                           point(sense, self.model['cell'], 1)['current_a'])
        electrical = point(pulse, self.model['cell'], 1)
        self.assertAlmostEqual(electrical['terminal_v'] * electrical['current_a'],
                               pulse['p_converter_w'] + electrical['terminal_v'] *
                               (pulse['i_direct_a'] + pulse['i_q_a']))
        self.assertGreater(pulse['p_converter_w'], pulse['p_out_w'])

    def test_charge_energy_and_mode_balance(self):
        for run in self.result['capacity_cases']:
            parts = (run['load_output_energy_mWh'] + run['converter_loss_mWh']
                     + run['direct_and_quiescent_mWh'] + run['startup_input_mWh'])
            self.assertAlmostEqual(run['battery_energy_mWh'], parts, places=7)
            self.assertAlmostEqual(sum(run['battery_energy_by_reference_mode_mWh'].values()),
                                   run['battery_energy_mWh'], places=7)
            self.assertLessEqual(run['discharged_charge_mAh'], run['capacity_label_mAh'])
        self.assertTrue(all(x is None for x in self.config['physical_inputs'].values()))
        self.assertEqual(self.result['gate']['gate'], 'FEASIBILITY_HOLD')
        self.assertEqual(self.result['evidence_class'], 'SYNTHETIC_CONDITIONAL')

    def test_capacity_and_sensitivity_behave_in_expected_direction(self):
        base = self.result['capacity_cases']
        self.assertEqual([r['capacity_label_mAh'] for r in base], [8, 10, 14, 20])
        self.assertEqual([r['reason'] for r in base], ['CHARGE_EXHAUSTED'] * 4)
        self.assertEqual(sorted(r['conditional_runtime_s'] for r in base),
                         [r['conditional_runtime_s'] for r in base])
        reference = base[1]['conditional_runtime_s']
        for scenario in self.result['ten_mAh_sensitivities']:
            self.assertLess(scenario['result']['conditional_runtime_s'], reference)
        self.assertLessEqual(self.result['convergence_10_mAh']['difference_s'],
                             self.result['convergence_10_mAh']['tolerance_s'])

    def test_units_and_incomplete_physical_inputs_fail_closed(self):
        invalid = copy.deepcopy(self.config)
        invalid['synthetic_example']['blocks']['optical_led']['state_currents']['active']['unit'] = 'A'
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        invalid = copy.deepcopy(self.config)
        invalid['synthetic_example']['rails']['led']['efficiency']['value'] = 1.1
        invalid['synthetic_example']['rails']['led']['efficiency']['range'] = [1.1, 1.1]
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        invalid = copy.deepcopy(self.config)
        invalid['physical_inputs']['product_mode_priorities_and_duty_schedule'] = {'value': 'unreviewed'}
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        invalid = copy.deepcopy(self.config)
        del invalid['physical_inputs']['validated_cell_pulse_current_limit']
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        invalid = copy.deepcopy(self.config)
        del invalid['physical_state_inventory']['audio_output']
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        with self.assertRaises(InvalidInput):
            parameter({'value': True, 'unit': 's', 'evidence': 'assumed', 'source': 'test',
                       'conditions': 'test', 'range': [0, 1]}, 's')

    def test_disabled_rail_and_mode_led_conflicts_fail_closed(self):
        invalid = copy.deepcopy(self.config)
        invalid['synthetic_example']['cycle'][2]['enabled_rails'].remove('led')
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        invalid = copy.deepcopy(self.config)
        invalid['synthetic_example']['cycle'][2]['ch02_reference_mode'] = 'deep_sleep'
        with self.assertRaises(InvalidInput):
            prepare(invalid)

    def test_no_power_solution_reports_unknown_peak(self):
        changed = copy.deepcopy(self.config)
        r = changed['synthetic_example']['cell']['series_resistance']
        r['value'] = 20
        r['range'] = [20, 20]
        result = simulate(prepare(changed), 10)
        self.assertEqual(result['reason'], 'NO_POWER_SOLUTION')
        self.assertIsNone(result['peak_requested_battery_current_mA'])
        self.assertGreater(result['conditional_runtime_s'], 0)
        changed['synthetic_example']['cycle'][0]['block_states']['aon'] = 'active'
        r['value'] = 100000
        r['range'] = [100000, 100000]
        changed['synthetic_example']['cell']['ocv_full']['value'] = 3.8
        impossible = simulate(prepare(changed), 10)
        self.assertEqual(impossible['reason'], 'NO_POWER_SOLUTION')
        self.assertIsNone(impossible['minimum_delivered_terminal_voltage_v'])
        json.dumps(impossible, allow_nan=False)

    def test_zero_load_and_analytic_constant_current(self):
        model = {'cell': {'ocv_empty_v': 4, 'ocv_full_v': 4, 'r_ohm': 0,
                          'cutoff_v': 3, 'capacity_fraction': 1},
                 'phases': [{'id': 'test', 'mode': 'test', 'duration_s': 1,
                             'p_out_w': 0, 'p_converter_w': 0, 'p_startup_w': 0,
                             'i_direct_a': 0, 'i_q_a': 0}]}
        self.assertEqual(simulate(model, 1)['reason'], 'NO_FINITE_RUNTIME')
        model['phases'][0]['i_direct_a'] = 0.001
        run = simulate(model, 1)
        self.assertEqual(run['reason'], 'CHARGE_EXHAUSTED')
        self.assertAlmostEqual(run['conditional_runtime_s'], 3600, places=3)
        self.assertAlmostEqual(run['battery_energy_mWh'], 4, places=3)

    def test_startup_event_is_time_resolved(self):
        sense = [p for p in self.model['phases'] if p['id'] == 'sense_and_send']
        self.assertEqual(len(sense), 2)
        self.assertAlmostEqual(sum(p['duration_s'] for p in sense), 0.1)
        self.assertAlmostEqual(sum(p['p_startup_w'] * p['duration_s'] for p in sense),
                               11 / 1e6)
        invalid = copy.deepcopy(self.config)
        event = invalid['synthetic_example']['cycle'][1]['startup_events'][0]['duration']
        event['value'] = 0.2
        event['range'] = [0.2, 0.2]
        with self.assertRaises(InvalidInput):
            prepare(invalid)
        outside = {'id': 'out_of_bounds', 'parameter': 'optical_duty',
                   'multiplier': {'value': 3, 'unit': 'ratio', 'evidence': 'assumed',
                                  'source': 'test', 'conditions': 'synthetic', 'range': [3, 3]}}
        with self.assertRaises(InvalidInput):
            prepare(self.config, outside)


if __name__ == '__main__':
    unittest.main()
