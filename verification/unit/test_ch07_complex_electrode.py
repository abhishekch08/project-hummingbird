"""CH07 complex-source sensitivity invariants, not an electrode qualification."""

import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
import ch07_biopotential as base  # noqa: E402
import ch07_complex_electrode as complex_model  # noqa: E402


class ComplexElectrodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(complex_model.CONFIG.read_text())
        cls.baseline = json.loads(base.CONFIG.read_text())
        cls.common, cls.cap_pf, cls.grid, cls.modes = complex_model.prepare(cls.cfg, cls.baseline)

    def run_probe(self, f, legs, cap_pf=None):
        return complex_model.evaluate(f, legs, self.common['input_resistance_ohm'],
                                      self.cap_pf if cap_pf is None else cap_pf,
                                      self.common['test_common_mode_v'], self.common['cmrr_db'])

    def test_zero_capacitance_limit_matches_resistive_baseline(self):
        legs = copy.deepcopy(self.modes[0][1])
        for leg in legs.values():
            leg['interface_capacitance_nf'] = 0
        result = self.run_probe(50, legs, 0)
        old = base.evaluate(self.common, base.prepare(self.baseline)[1][0][1])
        self.assertAlmostEqual(result['differential_gain_magnitude'], old['loading_fraction'])
        self.assertAlmostEqual(result['mismatch_cm_residual_uvpeak'],
                               old['contact_mismatch_cm_residual_uv_peak'])
        self.assertAlmostEqual(result['worst_phase_cm_bound_uvpeak'],
                               old['worst_phase_common_mode_uv_peak'])
        self.assertEqual(result['differential_phase_deg'], 0)

    def test_complex_series_parallel_and_transfer_obey_kirchhoff(self):
        f, leg = 50, self.modes[0][1]['positive']
        omega = 2*math.pi*f
        z = leg['series_ohm'] + 1/(1/leg['parallel_ohm'] +
                                    1j*omega*leg['interface_capacitance_nf']*1e-9)
        self.assertAlmostEqual(complex_model.electrode_z(f,leg).real, z.real)
        self.assertAlmostEqual(complex_model.electrode_z(f,leg).imag, z.imag)
        self.assertLess(z.imag, 0)
        result = self.run_probe(f,self.modes[0][1])
        self.assertGreater(result['mismatch_cm_residual_uvpeak'], 0)
        self.assertGreater(result['worst_phase_cm_bound_uvpeak'],
                           result['mismatch_cm_residual_uvpeak'])
        self.assertLess(result['differential_gain_magnitude'], 1)

    def test_identical_legs_cancel_source_common_mode_and_pad_capacitance_matters(self):
        legs = copy.deepcopy(self.modes[0][1])
        legs['negative'] = copy.deepcopy(legs['positive'])
        result = self.run_probe(500, legs)
        self.assertEqual(result['mismatch_cm_residual_uvpeak'], 0)
        self.assertIsNone(result['source_mismatch_rejection_db'])
        self.assertAlmostEqual(result['worst_phase_cm_bound_uvpeak'], 10)
        unequal = self.modes[0][1]
        no_cap = self.run_probe(500,unequal,0)
        pad_cap = self.run_probe(500,unequal,100)
        self.assertNotAlmostEqual(no_cap['mismatch_cm_residual_uvpeak'],
                                  pad_cap['mismatch_cm_residual_uvpeak'])

    def test_reject_unreviewed_or_nonpassive_fixture(self):
        for change in (
            lambda c: c['physical_inputs'].update(measured_electrode_complex_impedance_noise_offset_motion_population='ready'),
            lambda c: c['modes'][0]['positive']['series_ohm'].update(value=-1),
            lambda c: c['modes'][0]['positive']['parallel_ohm'].update(value=109000),
            lambda c: c['modes'][0]['negative']['interface_capacitance_nf'].update(unit='pF'),
            lambda c: c['input_capacitance_pf'].update(evidence='measured'),
            lambda c: c['frequency_grid_hz'].update(values=[0.1,50,50]),
            lambda c: c['frequency_grid_hz'].update(values=[0.1,50,float('inf')]),
        ):
            cfg = copy.deepcopy(self.cfg)
            change(cfg)
            with self.subTest(change=change), self.assertRaises(base.ModelError):
                complex_model.prepare(cfg,self.baseline)

    def test_report_cannot_claim_product_pass(self):
        report = complex_model.generate(self.cfg,self.baseline)
        self.assertEqual(report['gate'],'COMPLEX_SENSITIVITY_ONLY_CH07_TOPOLOGY_HOLD')
        self.assertEqual(len(report['physical_inputs_missing']),6)
        self.assertEqual([len(v) for v in report['modes'].values()],[10,10])
        self.assertTrue(all(x['z_positive_imag_ohm'] <= 0
                            for x in report['modes']['eeg_dry_resistive_probe']))


if __name__ == '__main__':
    unittest.main()
