#!/usr/bin/env python3
"""Synthetic CH07 complex contact sweep; never a measured source or topology pass."""

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path

import ch07_biopotential as base

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/biosignal/CH07_COMPLEX_SENSITIVITY.json'
REPORT = ROOT / 'reports/block/CH07_COMPLEX_SENSITIVITY.json'
REVIEW = ROOT / 'docs/budgets/CH07_COMPLEX_ELECTRODE_REVIEW.md'
LEG_FIELDS = {'series_ohm': 'ohm', 'parallel_ohm': 'ohm',
              'interface_capacitance_nf': 'nF'}


def prepare(cfg, baseline):
    """Validate the illustrative fixture and anchor each leg's DC resistance."""
    if (set(cfg) != {'schema_version', 'evidence_class', 'source', 'physical_inputs',
                     'input_capacitance_pf', 'frequency_grid_hz', 'modes'} or
            cfg['schema_version'] != 1 or
            cfg['evidence_class'] != 'synthetic_complex_electrode_sensitivity' or
            not isinstance(cfg['source'], str) or not cfg['source'].strip() or
            set(cfg['physical_inputs']) != base.PHYSICAL or
            any(x is not None for x in cfg['physical_inputs'].values())):
        raise base.ModelError('complex fixture provenance or physical-input gate')
    common, old_modes = base.prepare(baseline)
    cap_pf = base.value('input_capacitance_pf', cfg['input_capacitance_pf'], 'pF')
    if cap_pf < 0:
        raise base.ModelError('negative input capacitance')
    grid = cfg['frequency_grid_hz']
    if (not isinstance(grid, dict) or set(grid) !=
            {'values', 'unit', 'evidence', 'source', 'conditions', 'range'} or
            grid['unit'] != 'Hz' or grid['evidence'] != 'assumed' or
            any(not isinstance(grid[k], str) or not grid[k].strip()
                for k in ('source', 'conditions')) or
            not isinstance(grid['range'], list) or len(grid['range']) != 2 or
            any(type(v) not in (int, float) or not math.isfinite(v) for v in grid['range']) or
            not isinstance(grid['values'], list) or len(grid['values']) < 3):
        raise base.ModelError('frequency grid units or provenance')
    freqs = grid['values']
    if (any(type(f) not in (int, float) or not math.isfinite(f) or
            not grid['range'][0] <= f <= grid['range'][1] or f <= 0 for f in freqs) or
            any(a >= b for a, b in zip(freqs, freqs[1:]))):
        raise base.ModelError('frequency grid is not finite, bounded and increasing')
    modes = cfg['modes']
    if (not isinstance(modes, list) or len(modes) != len(old_modes) or
            [m.get('id') for m in modes if isinstance(m, dict)] !=
            [name for name, _ in old_modes]):
        raise base.ModelError('complex modes must match CH07 baseline')
    prepared = []
    for mode, (name, old) in zip(modes, old_modes):
        if set(mode) != {'id', 'positive', 'negative'}:
            raise base.ModelError('unknown complex mode field')
        legs = {}
        for leg, old_field in [('positive', 'source_pos_ohm'),
                               ('negative', 'source_neg_ohm')]:
            raw = mode[leg]
            if not isinstance(raw, dict) or set(raw) != set(LEG_FIELDS):
                raise base.ModelError('missing complex leg parameter')
            p = {key: base.value(key, raw[key], unit)
                 for key, unit in LEG_FIELDS.items()}
            if (p['series_ohm'] < 0 or p['parallel_ohm'] <= 0 or
                    p['interface_capacitance_nf'] < 0 or
                    p['series_ohm'] + p['parallel_ohm'] != old[old_field]):
                raise base.ModelError(f'{name} {leg}: non-passive or DC baseline mismatch')
            legs[leg] = p
        prepared.append((name, legs))
    return common, cap_pf, freqs, prepared


def electrode_z(frequency_hz, leg):
    """Z = Rs + Rp/(1 + j*omega*Rp*C), passive series/parallel RC."""
    omega = 2 * math.pi * frequency_hz
    return leg['series_ohm'] + leg['parallel_ohm'] / (
        1 + 1j * omega * leg['parallel_ohm'] * leg['interface_capacitance_nf'] * 1e-9)


def evaluate(frequency_hz, legs, input_resistance_ohm, input_capacitance_pf,
             common_mode_vpeak, intrinsic_cmrr_db):
    """Independent symmetric inputs with Z_in shunt; small-signal steady state only."""
    omega = 2 * math.pi * frequency_hz
    y_in = 1/input_resistance_ohm + 1j*omega*input_capacitance_pf*1e-12
    zp = electrode_z(frequency_hz, legs['positive'])
    zn = electrode_z(frequency_hz, legs['negative'])
    hp, hn = 1/(1+zp*y_in), 1/(1+zn*y_in)
    differential = (hp+hn)/2
    cm = hp-hn
    return {
        'frequency_hz': frequency_hz,
        'z_positive_real_ohm': zp.real, 'z_positive_imag_ohm': zp.imag,
        'z_negative_real_ohm': zn.real, 'z_negative_imag_ohm': zn.imag,
        'differential_gain_magnitude': abs(differential),
        'differential_phase_deg': math.degrees(cmath.phase(differential)),
        'mismatch_cm_to_diff_gain_magnitude': abs(cm),
        'mismatch_cm_residual_uvpeak': abs(cm)*common_mode_vpeak*1e6,
        'intrinsic_cmrr_residual_uvpeak': common_mode_vpeak*10**(-intrinsic_cmrr_db/20)*1e6,
        'worst_phase_cm_bound_uvpeak':
            (abs(cm)+10**(-intrinsic_cmrr_db/20))*common_mode_vpeak*1e6,
        'source_mismatch_rejection_db': None if abs(cm) == 0 else -20*math.log10(abs(cm)),
    }


def generate(cfg, baseline):
    common, cap, freqs, modes = prepare(cfg, baseline)
    return {
        'schema_version': 1, 'evidence_class': cfg['evidence_class'],
        'gate': 'COMPLEX_SENSITIVITY_ONLY_CH07_TOPOLOGY_HOLD',
        'config_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        'baseline_sha256': hashlib.sha256(base.CONFIG.read_bytes()).hexdigest(),
        'physical_inputs_missing': sorted(base.PHYSICAL),
        'input_capacitance_pf_assumed': cap,
        'modes': {name: [evaluate(f, legs, common['input_resistance_ohm'], cap,
                                  common['test_common_mode_v'], common['cmrr_db'])
                         for f in freqs] for name, legs in modes},
    }


def render(report):
    rows = []
    for mode, samples in report['modes'].items():
        for result in samples:
            if result['frequency_hz'] in (0.05, 50, 500, 1500):
                rows.append(f"| `{mode}` | {result['frequency_hz']:g} | "
                            f"{result['differential_gain_magnitude']:.8f} | "
                            f"{result['differential_phase_deg']:.5f} | "
                            f"{result['mismatch_cm_residual_uvpeak']:.3f} | "
                            f"{result['worst_phase_cm_bound_uvpeak']:.3f} |")
    return f"""# CH07 passive complex-electrode sensitivity

Generate with `python3 models/python/ch07_complex_electrode.py --write`; verify with `--check`. Config SHA-256 `{report['config_sha256']}`; previous CH07 resistor fixture SHA-256 `{report['baseline_sha256']}`. The [entry acceptance](../chunks/CH07_EVIDENCE_READINESS.md) and [electrode evidence intake](../inputs/CH07_ELECTRODE_QUALITY_INTAKE.md) define the use and next review. **All capacitances are invented sensitivity inputs. No electrode, IC pad or AFE has been characterized for this project.**

For each leg use a passive series resistor plus a parallel resistor/capacitor: `Zs(f) = Rs + Rp/(1 + j2πf Rp C)`. Input admittance `Yin(f) = 1/Rin + j2πf Cin`, voltage transfer `H = 1/(1 + Zs Yin)`. For symmetric ±differential drive, `Hdiff = (Hp + Hn)/2`; for identical common-mode drive at both electrode sources, `Hcm→diff = Hp − Hn`. The table shows `|Hdiff|`, its phase, `|Hcm→diff|×Vcm`, and the worst-phase upper bound adding a separate intrinsic `Vcm×10^(−CMRR/20)` magnitude. The assumed common mode is **1 V peak at every listed frequency solely to expose sensitivity**, not a broadband/noise/clinical test; this worst-phase bound is not RSS or a measured circuit response.

| Synthetic mode | Frequency Hz | Differential magnitude | Phase deg | Source mismatch µVpeak | Mismatch + intrinsic upper bound µVpeak |
|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

The fixed DC series+parallel resistance equals the earlier CH07 resistor fixture on each leg. The published resistor model remains the source for its separate bias/offset, white-noise, gain and first-image arithmetic. This extension **does not integrate complex-source noise**, fit a constant-phase skin electrode, simulate polarization/movement, coupling between legs/body, protection nonlinearity, chopper charging, ADC filters, recovery or lead-off excitation. Its passband and image-grid samples are not a filter design or proof of alias rejection. It predicts how assumed contact/pad capacitance can alter loading and common-mode conversion with frequency and identifies measurements that must replace the fixture. **CH07 topology and full block spec remain HOLD; CH08 remains NOT_RUN.**
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = p.parse_args()
    report = generate(json.loads(CONFIG.read_text()), json.loads(base.CONFIG.read_text()))
    js, md = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n', render(report)
    if args.write:
        REPORT.write_text(js)
        REVIEW.write_text(md)
        print('CH07 synthetic complex sensitivity written; topology HOLD')
    elif REPORT.read_text() != js or REVIEW.read_text() != md:
        raise SystemExit('CH07 complex review stale: regenerate and inspect diff')
    else:
        print('CH07 synthetic complex sensitivity matches source; topology HOLD')


if __name__ == '__main__':
    main()
