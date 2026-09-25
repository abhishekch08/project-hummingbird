#!/usr/bin/env python3
"""CH07 resistive EEG/ECG sensitivity math; no electrode, ADC or ASIC validated."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/biosignal/CH07_NUMERICAL_SCENARIOS.json'
CH02 = ROOT / 'specs/system/CH02_MODE_ASSUMPTIONS.json'
REPORT = ROOT / 'reports/block/CH07_NUMERICAL_SUMMARY.json'
REVIEW = ROOT / 'docs/budgets/CH07_BIOPOTENTIAL_REVIEW.md'
K_B = 1.380649e-23  # Exact SI Boltzmann constant in J/K.
COMMON = {'temperature_kelvin': 'K', 'input_resistance_ohm': 'ohm',
          'adc_word_bits': 'bit', 'adc_full_scale_vpp': 'Vpp',
          'cmrr_db': 'dB', 'test_common_mode_v': 'V',
          'noise_goal_uv_rms': 'uVrms', 'channel_count': 'channel'}
FIELDS = {'band_low_hz': 'Hz', 'band_high_hz': 'Hz', 'sample_rate_sps': 'SPS',
          'modulator_rate_hz': 'Hz', 'source_pos_ohm': 'ohm',
          'source_neg_ohm': 'ohm', 'electrode_offset_mv': 'mV',
          'bias_current_pa': 'pA', 'pad_leakage_pa': 'pA',
          'amplifier_noise_uv_rms': 'uVrms', 'adc_noise_uv_rms': 'uVrms',
          'minimum_signal_uv_peak': 'uVpeak', 'gain': 'V/V',
          'filter_corner_hz': 'Hz', 'filter_order': 'pole',
          'out_of_band_uv_peak': 'uVpeak', 'power_per_channel_uw': 'uW'}
PHYSICAL = {'approved_eeg_ecg_biomarkers_bands_quality_and_gain_policy',
            'measured_electrode_complex_impedance_noise_offset_motion_population',
            'qualified_pad_esd_mux_leakage_and_parasitic_capacitance',
            'approved_reference_drive_leadoff_and_body_current_safety',
            'selected_afe_supply_power_area_and_pdk',
            'measured_afe_adc_noise_transfer_function_and_alias_response'}
REQUIREMENTS = {f'BIO-{i:04d}' for i in range(1, 22)}
INTEGER = {'adc_word_bits', 'channel_count', 'sample_rate_sps',
           'modulator_rate_hz', 'filter_order', 'gain'}


class ModelError(ValueError):
    """Source, unit or physically meaningful study-bound violation."""


def value(name, data, unit):
    if (not isinstance(data, dict) or set(data) !=
            {'value', 'unit', 'evidence', 'source', 'conditions', 'range'} or
            data['unit'] != unit or data['evidence'] != 'assumed' or
            any(not isinstance(data[k], str) or not data[k].strip()
                for k in ('source', 'conditions'))):
        raise ModelError(f'{name}: unreviewed units/provenance')
    v, rng = data['value'], data['range']
    if (type(v) not in (int, float) or not math.isfinite(v) or
            type(rng) is not list or len(rng) != 2 or
            any(type(x) not in (int, float) or not math.isfinite(x) for x in rng) or
            not rng[0] <= v <= rng[1] or (name in INTEGER and
             (type(v) is not int or any(type(x) is not int for x in rng)))):
        raise ModelError(f'{name}: invalid numeric bounds')
    return v


def prepare(cfg, ch02=None):
    if (cfg.get('schema_version') != 1 or
            cfg.get('evidence_class') != 'synthetic_biopotential_sensitivity' or
            not isinstance(cfg.get('source'), str) or not cfg['source'].strip() or
            set(cfg.get('physical_inputs', {})) != PHYSICAL or
            any(v is not None for v in cfg['physical_inputs'].values())):
        raise ModelError('Physical input requires independent gate/revised schema')
    if set(cfg.get('common', {})) != set(COMMON):
        raise ModelError('Missing common parameter')
    c = {name: value(name, cfg['common'][name], unit) for name, unit in COMMON.items()}
    if (c['temperature_kelvin'] <= 0 or c['input_resistance_ohm'] <= 0 or
            c['adc_full_scale_vpp'] <= 0 or c['noise_goal_uv_rms'] <= 0 or
            c['channel_count'] <= 0 or c['adc_word_bits'] <= 0):
        raise ModelError('Invalid physical base')
    ch02 = ch02 if ch02 is not None else json.loads(CH02.read_text())
    if (ch02.get('schema_version') != 1 or
            ch02['capacities']['BIO_ADC_simultaneous'] != c['channel_count']):
        raise ModelError('CH02 simultaneous channels mismatch')
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as fh:
        ids = {row['Req_ID'] for row in csv.DictReader(fh)}
    if not REQUIREMENTS <= ids:
        raise ModelError('Missing biopotential requirement IDs')
    scenarios = cfg.get('scenarios')
    if (not isinstance(scenarios, list) or len(scenarios) != 2 or
            [s.get('id') for s in scenarios if isinstance(s, dict)] !=
            ['eeg_dry_resistive_probe', 'ecg_resistive_probe']):
        raise ModelError('Scenario identity changed')
    prepared = []
    for s in scenarios:
        if set(s) != {'id', 'parameters'} or set(s['parameters']) != set(FIELDS):
            raise ModelError('Unknown or missing per-mode parameter')
        p = {name: value(name, s['parameters'][name], unit) for name, unit in FIELDS.items()}
        if (not 0 < p['band_low_hz'] < p['band_high_hz'] < p['sample_rate_sps']/2 or
                p['modulator_rate_hz'] % p['sample_rate_sps'] or
                p['modulator_rate_hz'] // p['sample_rate_sps'] < 2 or
                p['source_pos_ohm'] <= 0 or p['source_neg_ohm'] <= 0 or
                p['filter_corner_hz'] <= p['band_high_hz'] or
                p['filter_order'] < 1 or p['gain'] < 1 or p['power_per_channel_uw'] <= 0 or
                any(p[k] < 0 for k in ('electrode_offset_mv', 'bias_current_pa',
                    'pad_leakage_pa', 'amplifier_noise_uv_rms', 'adc_noise_uv_rms',
                    'out_of_band_uv_peak'))):
            raise ModelError('Nyquist, OSR, source or nonnegative error violated')
        prepared.append((s['id'], p))
    return c, prepared


def evaluate(c, p):
    """Purely resistive source, white independent noise, worst-phase deterministic errors."""
    r1, r2, rin = p['source_pos_ohm'], p['source_neg_ohm'], c['input_resistance_ohm']
    a1, a2 = rin/(rin+r1), rin/(rin+r2)
    differential_transfer = (a1+a2)/2
    # Identical additive common-mode at electrodes produces unequal loaded voltages.
    cm_imbalance_uv = c['test_common_mode_v'] * abs(a1-a2) * 1e6
    intrinsic_cm_uv = c['test_common_mode_v'] * 10**(-c['cmrr_db']/20) * 1e6
    cm_worst_uv = intrinsic_cm_uv + cm_imbalance_uv
    bias_uv = (p['bias_current_pa']+p['pad_leakage_pa'])*1e-12*(r1+r2)*1e6
    bw = p['band_high_hz']-p['band_low_hz']
    source_uv_rms = math.sqrt(4*K_B*c['temperature_kelvin']*bw*
                              (r1*a1*a1+r2*a2*a2))*1e6
    q_lsb_uv = (c['adc_full_scale_vpp']/p['gain']) / 2**c['adc_word_bits'] * 1e6
    q_uv_rms = q_lsb_uv/math.sqrt(12)
    # ADC noise and quantization are independent only in the assumed model.
    noise_uv_rms = math.sqrt(source_uv_rms**2 + p['amplifier_noise_uv_rms']**2 +
                             p['adc_noise_uv_rms']**2 + q_uv_rms**2)
    input_half_scale = c['adc_full_scale_vpp']/2/p['gain']
    required_headroom = (p['electrode_offset_mv']*1e-3 +
                         (bias_uv+cm_worst_uv+p['minimum_signal_uv_peak']*differential_transfer)*1e-6)
    alias_at_hz = p['sample_rate_sps']-p['band_high_hz']
    def lp(f):
        return (1+(f/p['filter_corner_hz'])**2)**(-p['filter_order']/2)
    alias_uv = p['out_of_band_uv_peak']*lp(alias_at_hz)
    return {'source_pos_ohm': r1, 'source_neg_ohm': r2,
            'loading_fraction': differential_transfer,
            'bias_plus_pad_worst_uv': bias_uv,
            'intrinsic_cmrr_residual_uv_peak': intrinsic_cm_uv,
            'contact_mismatch_cm_residual_uv_peak': cm_imbalance_uv,
            'worst_phase_common_mode_uv_peak': cm_worst_uv,
            'source_white_thermal_uv_rms': source_uv_rms,
            'adc_ideal_lsb_uv': q_lsb_uv,
            'adc_ideal_quant_uv_rms': q_uv_rms,
            'random_rss_input_noise_uv_rms': noise_uv_rms,
            'assumed_noise_goal_uv_rms': c['noise_goal_uv_rms'],
            'random_noise_probe': 'MODEL_BELOW_GOAL' if noise_uv_rms <= c['noise_goal_uv_rms'] else 'MODEL_ABOVE_GOAL',
            'minimum_signal_after_loading_uv_peak': p['minimum_signal_uv_peak']*differential_transfer,
            'dc_coupled_input_half_scale_v': input_half_scale,
            'worst_phase_required_headroom_v': required_headroom,
            'dc_coupled_headroom_probe': 'MODEL_FITS' if required_headroom <= input_half_scale else 'MODEL_SATURATES',
            'band_hz': [p['band_low_hz'], p['band_high_hz']],
            'sample_rate_sps': p['sample_rate_sps'], 'osr_label_only': p['modulator_rate_hz']//p['sample_rate_sps'],
            'first_alias_image_hz': alias_at_hz,
            'signal_edge_analog_gain': lp(p['band_high_hz']),
            'first_alias_analog_gain': lp(alias_at_hz),
            'first_alias_spur_uv_peak': alias_uv,
            'first_alias_probe': 'MODEL_ABOVE_NOISE_GOAL' if alias_uv > c['noise_goal_uv_rms'] else 'MODEL_BELOW_NOISE_GOAL',
            'eight_identical_channels_uw': c['channel_count']*p['power_per_channel_uw'],
            'power_excludes': ['ADC/AFE implementation uncertainty', 'rail losses', 'pads',
                               'bias/lead-off drive', 'clock and digital', 'motion artifact']}


def generate(cfg):
    c, ps = prepare(cfg)
    return {'schema_version': 1, 'evidence_class': cfg['evidence_class'],
            'gate': 'NUMERICAL_MODEL_ONLY_TOPOLOGY_HOLD',
            'config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'ch02_sha256': hashlib.sha256(CH02.read_bytes()).hexdigest(),
            'assumptions': c, 'physical_inputs_missing': sorted(PHYSICAL),
            'modes': {name: evaluate(c,p) for name,p in ps}}


def render(report):
    rows = '\n'.join(f"| `{name}` | {m['source_white_thermal_uv_rms']:.3f} | "
                     f"{m['random_rss_input_noise_uv_rms']:.3f} | "
                     f"{m['contact_mismatch_cm_residual_uv_peak']:.2f} + "
                     f"{m['intrinsic_cmrr_residual_uv_peak']:.2f} | "
                     f"{m['worst_phase_required_headroom_v']:.6f} / "
                     f"{m['dc_coupled_input_half_scale_v']:.6f} | "
                     f"{m['first_alias_spur_uv_peak']:.2f} | "
                     f"{m['eight_identical_channels_uw']} |"
                     for name,m in report['modes'].items())
    return f"""# CH07 conditional biopotential numerical review

Generate with `python3 models/python/ch07_biopotential.py --write`, check with `--check`. Config SHA-256 `{report['config_sha256']}`; CH02 input SHA-256 `{report['ch02_sha256']}`. [Literature survey](../literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md) was merged as PR #11 before this model. **Synthetic probe, no selected EEG/ECG electrode, AFE, ADC, PDK or body-current path.**

## Equations and deliberate limits

For a *real, constant resistance* on each of two electrode legs, `aᵢ = Rin/(Rin+Rᵢ)`. Differential signal transfer ≈`(a₁+a₂)/2` for symmetric ±signal/2. A common-mode voltage makes differential `|a₁−a₂| Vcm`; add the intrinsic `Vcm × 10^(−CMRR/20)` by worst phase, **not RSS**. Bias+ESD leakage worst-case differential magnitude is bounded by `(|Ibias|+|Ipad|)(R₁+R₂)`. DC-coupled headroom needs electrode offset + this bias + common-mode error + attenuated signal, compared with `Vpp/(2×gain)`. These are simplified sensitivities, not an input-common-mode, pad or servo simulation.

Thermal electrode white noise **at the loaded input** for two resistors over flat `B = fhigh − flow` is `sqrt(4 k T B (R₁ a₁²+R₂ a₂²))`, with exact SI `k = 1.380649e−23 J/K`. RSS includes this source noise, separately assumed independent IA noise, ADC noise and *ideal uniform* converter LSB/√12. Electrode polarization, 1/f, motion, ESD, reference, ADC noise shaping, passband weighting and correlations are **omitted**. Peak-to-peak manufacturer noise is never converted to rms. A 24-bit word and `OSR = fmod/fs` are labels; neither implies ENOB/SNDR or safe anti-aliasing.

The anti-alias probe cascades `n` identical analog first-order low-pass poles with magnitude `[1+(f/fc)²]^(−n/2)`. It samples the first image at `fs − fhigh`, reports input-referred output spur from an assumed interferer and shows signal-band edge gain separately. This is **one frequency** and does not model decimator stopbands, broad EMI, transients or a real analog transfer function.

| Synthetic mode | Resistor noise µVrms | Random RSS µVrms | Common-mode mismatch + intrinsic µVpeak | Required / allowed DC input headroom V | First-image spur µVpeak | Eight identical channels µW |
|---|---:|---:|---:|---:|---:|---:|
{rows}

An assumed 1 µVrms goal is exceeded for both fixtures; neither provides offset headroom at its chosen DC-coupled gain. At 1 V common mode, the unequal source impedances produce a residual **in addition** to ideal 100 dB intrinsic rejection. The first-image interference exceeds the 1 µV comparison value. Random noise and deterministic interference are **not** interchangeable; an external noise target and artifact/recovery acceptance are still needed. The eight-channel power line multiplies only invented per-channel input power and omits ADC/clock, shared analog, rails and body drive; no battery runtime or SiP area follows from it.

## Architecture review and next gate

DC-coupled simultaneous PGA/ΔΣ can preserve low-frequency waveform but needs enough offset headroom at useful gain. AC-coupled chopper/servo can remove DC and flicker at cost of corner, settle, input charging and ripple. An active electrode or input impedance boost can limit pickup along a high-impedance lead but adds on-body electronics, power and safety complexity. These are alternatives, not selected topology. See [CH07 gate](../reviews/CH07_GATE.md): NUMERICAL_MODEL_PASS / TOPOLOGY_AND_REQUIREMENTS_HOLD. Source measurements, owner quality criteria, PDK/pad and reviewed body-current limits must arrive before freezing a block specification, transistor sizing or claiming CH08 behavioral requirements pass.
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = p.parse_args()
    report = generate(json.loads(CONFIG.read_text()))
    js, md = json.dumps(report, indent=2, sort_keys=True)+'\n', render(report)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REVIEW.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(js)
        REVIEW.write_text(md)
        print('CH07 synthetic numerical reports written; topology HOLD')
    elif REPORT.read_text() != js or REVIEW.read_text() != md:
        raise SystemExit('CH07 report stale: run --write and review changes')
    else:
        print('CH07 numerical reports match synthetic source/model; topology HOLD')


if __name__ == '__main__':
    main()
