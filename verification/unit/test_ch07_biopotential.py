"""CH07 model math and bad assumptions; no electrode, analog, ADC or safety signoff."""

import copy
import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'models/python'))
import ch07_biopotential as bio  # noqa: E402


class BiopotentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads(bio.CONFIG.read_text())
        cls.c, cls.modes = bio.prepare(cls.cfg)

    def mode(self, i=0):
        return copy.deepcopy(self.modes[i][1])

    def test_resistor_loading_and_unequal_contact_cmr(self):
        p = self.mode()
        r = bio.evaluate(self.c, p)
        a1 = 1e9/(1e9+120000)
        a2 = 1e9/(1e9+65000)
        self.assertAlmostEqual(r['loading_fraction'], (a1+a2)/2)
        self.assertAlmostEqual(r['contact_mismatch_cm_residual_uv_peak'],
                               abs(a1-a2)*1e6)
        self.assertAlmostEqual(r['intrinsic_cmrr_residual_uv_peak'], 10.0)
        self.assertGreater(r['contact_mismatch_cm_residual_uv_peak'], 50)
        p['source_neg_ohm'] = p['source_pos_ohm']
        self.assertEqual(bio.evaluate(self.c,p)['contact_mismatch_cm_residual_uv_peak'], 0)

    def test_bias_and_pad_current_magnitudes_add_worst_case(self):
        p = self.mode()
        r = bio.evaluate(self.c, p)
        self.assertAlmostEqual(r['bias_plus_pad_worst_uv'], 74)
        p['pad_leakage_pa'] = 0
        self.assertAlmostEqual(bio.evaluate(self.c,p)['bias_plus_pad_worst_uv'], 55.5)

    def test_noise_integrates_band_and_not_deterministic_interference(self):
        p = self.mode()
        r = bio.evaluate(self.c, p)
        a1 = 1e9/(1e9+120000)
        a2 = 1e9/(1e9+65000)
        self.assertAlmostEqual(r['source_white_thermal_uv_rms'],
                               math.sqrt(4*bio.K_B*310*(120000*a1*a1+65000*a2*a2)*
                                         (250-0.1))*1e6)
        self.assertAlmostEqual(r['random_rss_input_noise_uv_rms']**2,
                               r['source_white_thermal_uv_rms']**2+0.6**2+0.4**2+
                               r['adc_ideal_quant_uv_rms']**2)
        self.assertEqual(r['random_noise_probe'], 'MODEL_ABOVE_GOAL')
        p['out_of_band_uv_peak'] = 2000
        r2 = bio.evaluate(self.c, p)
        self.assertEqual(r2['random_rss_input_noise_uv_rms'], r['random_rss_input_noise_uv_rms'])
        self.assertEqual(r2['first_alias_spur_uv_peak'], 2*r['first_alias_spur_uv_peak'])

    def test_resistance_and_bandwidth_change_thermal_term_by_root(self):
        p = self.mode()
        r = bio.evaluate(self.c,p)
        p['source_pos_ohm'] *= 2
        p['source_neg_ohm'] *= 2
        a1=1e9/(1e9+p['source_pos_ohm'])
        a2=1e9/(1e9+p['source_neg_ohm'])
        self.assertAlmostEqual(bio.evaluate(self.c,p)['source_white_thermal_uv_rms'],
                               math.sqrt(4*bio.K_B*310*(p['source_pos_ohm']*a1*a1+
                                   p['source_neg_ohm']*a2*a2)*(250-0.1))*1e6)
        p = self.mode()
        p['band_high_hz'] = 2*p['band_high_hz']-p['band_low_hz']
        self.assertAlmostEqual(bio.evaluate(self.c,p)['source_white_thermal_uv_rms'],
                               math.sqrt(2)*r['source_white_thermal_uv_rms'])

    def test_dc_gain_and_offset_incompatible_under_probe(self):
        p = self.mode()
        r = bio.evaluate(self.c,p)
        self.assertEqual(r['dc_coupled_headroom_probe'], 'MODEL_SATURATES')
        self.assertAlmostEqual(r['dc_coupled_input_half_scale_v'], 1/24)
        self.assertGreater(r['worst_phase_required_headroom_v'], 0.3)
        p['gain'] = 1
        self.assertEqual(bio.evaluate(self.c,p)['dc_coupled_headroom_probe'], 'MODEL_FITS')

    def test_ideal_word_length_not_analog_noise_claim(self):
        p = self.mode()
        r = bio.evaluate(self.c,p)
        self.assertAlmostEqual(r['adc_ideal_lsb_uv'], 2/24/2**24*1e6)
        self.assertAlmostEqual(r['adc_ideal_quant_uv_rms'], r['adc_ideal_lsb_uv']/math.sqrt(12))
        self.assertGreater(r['random_rss_input_noise_uv_rms'], 100*r['adc_ideal_quant_uv_rms'])

    def test_nyquist_first_image_and_osr_are_conditional(self):
        r = bio.evaluate(self.c,self.mode())
        self.assertEqual((r['sample_rate_sps'],r['first_alias_image_hz'],r['osr_label_only']),
                         (1000,750,256))
        self.assertGreater(r['first_alias_spur_uv_peak'], 1)
        self.assertLess(r['first_alias_analog_gain'], r['signal_edge_analog_gain'])
        p = self.mode()
        p['filter_order'] = 10
        self.assertLess(bio.evaluate(self.c,p)['first_alias_spur_uv_peak'],
                        r['first_alias_spur_uv_peak'])

    def test_two_distinct_bands_and_eight_channel_power_multiply_only(self):
        eeg, ecg = (bio.evaluate(self.c,p) for _,p in self.modes)
        self.assertEqual((eeg['band_hz'],ecg['band_hz']), ([0.1,250],[0.05,500]))
        self.assertEqual((eeg['eight_identical_channels_uw'],ecg['eight_identical_channels_uw']),
                         (80,96))
        self.assertEqual(ecg['dc_coupled_headroom_probe'], 'MODEL_SATURATES')
        self.assertEqual(ecg['random_noise_probe'], 'MODEL_ABOVE_GOAL')
        self.assertIn('rail losses',ecg['power_excludes'])

    def test_reject_units_missing_source_range_and_nonfinite_numbers(self):
        for change in (
            lambda c: c['common']['temperature_kelvin'].update(unit='C'),
            lambda c: c['common']['input_resistance_ohm'].update(source=''),
            lambda c: c['common']['noise_goal_uv_rms'].update(range=[2,3]),
            lambda c: c['scenarios'][0]['parameters']['source_pos_ohm'].update(value=float('nan')),
            lambda c: c['common']['adc_word_bits'].update(value=24.0),
            lambda c: c['scenarios'][0]['parameters']['power_per_channel_uw'].update(evidence='measured')):
            cfg=copy.deepcopy(self.cfg)
            change(cfg)
            with self.subTest(change=change), self.assertRaises(bio.ModelError):
                bio.prepare(cfg)

    def test_reject_nyquist_osr_contact_and_filter_errors(self):
        for name,value in (('sample_rate_sps',500),('modulator_rate_hz',257001),
                           ('source_neg_ohm',0),('filter_corner_hz',250),
                           ('filter_order',0),('gain',0)):
            cfg=copy.deepcopy(self.cfg)
            cfg['scenarios'][0]['parameters'][name]['value']=value
            with self.subTest(name=name), self.assertRaises(bio.ModelError):
                bio.prepare(cfg)

    def test_reject_selected_physical_inputs_and_ch02_mismatch(self):
        cfg=copy.deepcopy(self.cfg)
        cfg['physical_inputs']['measured_electrode_complex_impedance_noise_offset_motion_population']='selected'
        with self.assertRaises(bio.ModelError):
            bio.prepare(cfg)
        ch02=json.loads(bio.CH02.read_text())
        ch02['capacities']['BIO_ADC_simultaneous']=7
        with self.assertRaises(bio.ModelError):
            bio.prepare(self.cfg,ch02)

    def test_generated_provenance_and_gate_are_explicit(self):
        r=bio.generate(self.cfg)
        self.assertEqual(r['gate'],'NUMERICAL_MODEL_ONLY_TOPOLOGY_HOLD')
        self.assertEqual(len(r['physical_inputs_missing']),6)
        self.assertEqual(set(r['modes']),{'eeg_dry_resistive_probe','ecg_resistive_probe'})


if __name__ == '__main__':
    unittest.main()
