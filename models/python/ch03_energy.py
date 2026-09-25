#!/usr/bin/env python3
"""CH03: synthetic, conditional battery-energy accounting; no product or cell signoff."""

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/system/CH03_ENERGY_SCENARIOS.json'
CH02 = ROOT / 'specs/system/CH02_MODE_ASSUMPTIONS.json'
RESULTS = ROOT / 'reports/subsystem/CH03_ENERGY_SUMMARY.json'
REVIEW = ROOT / 'docs/budgets/CH03_ENERGY_REVIEW.md'
REQUIREMENTS = {'PMU-0001', 'PMU-0009', 'PMU-0010', 'PMU-0014',
                'SYS-0010', 'OPT-0002', 'AUD-0011', 'SAFE-0002'}
PHYSICAL_REQUIRED = {
    'product_mode_priorities_and_duty_schedule',
    'representative_cell_ocv_vs_soc_temperature_age',
    'representative_cell_impedance_vs_soc_temperature_age_pulse_duration',
    'usable_capacity_vs_load_temperature_age', 'validated_cell_pulse_current_limit',
    'emitter_forward_voltage_and_pulse_waveform',
    'measured_rail_efficiency_vs_input_load_temperature',
    'measured_block_state_and_startup_loads', 'independent_safety_and_thermal_limits',
}
PHYSICAL_BLOCKS = {
    'aon', 'compute', 'bio', 'eda_bioz', 'electrochemical', 'optical_rx',
    'optical_led', 'thermal', 'audio_input', 'audio_output', 'host_rf',
    'imu', 'memory', 'pmic',
}


class InvalidInput(ValueError):
    """A scenario could silently misstate an engineering unit or condition."""


def parameter(obj, unit):
    """Read a numeric input only when its units and provenance are explicit."""
    if not isinstance(obj, dict) or obj.get('unit') != unit:
        raise InvalidInput(f'Expected parameter with unit {unit}: {obj!r}')
    if obj.get('evidence') not in ('assumed', 'vendor', 'measured'):
        raise InvalidInput('Numeric parameter lacks evidence classification')
    if not all(isinstance(obj.get(key), str) and obj[key].strip()
               for key in ('source', 'conditions')):
        raise InvalidInput('Numeric parameter lacks source or conditions')
    value, bounds = obj.get('value'), obj.get('range')
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not isinstance(bounds, list)
            or len(bounds) != 2 or any(isinstance(x, bool) or not isinstance(x, (int, float))
                                      or not math.isfinite(x) for x in bounds)
            or not bounds[0] <= value <= bounds[1]):
        raise InvalidInput('Numeric parameter must be finite and inside its declared study range')
    return float(value)


def inside_study_range(obj, value):
    tol = 1e-12 * max(1.0, abs(value))
    if not obj['range'][0] - tol <= value <= obj['range'][1] + tol:
        raise InvalidInput('Sensitivity changed a value outside its declared study range')
    return value


def solve_cell(ocv_v, resistance_ohm, constant_power_w, direct_current_a, cutoff_v=0):
    """High-voltage stable branch of V=OCV-R*(I_direct+P/V), or an explicit failure."""
    if (ocv_v <= 0 or resistance_ohm < 0 or constant_power_w < 0
            or direct_current_a < 0 or cutoff_v < 0):
        raise InvalidInput('Nonphysical cell calculation input')
    if resistance_ohm == 0:
        terminal_v = ocv_v
    else:
        a = ocv_v - resistance_ohm * direct_current_a
        discriminant = a * a - 4 * resistance_ohm * constant_power_w
        if a <= 0 or discriminant < 0:
            return {'reason': 'NO_POWER_SOLUTION', 'terminal_v': None, 'current_a': None}
        terminal_v = (a + math.sqrt(discriminant)) / 2
    if terminal_v <= 0:
        return {'reason': 'NO_POWER_SOLUTION', 'terminal_v': None, 'current_a': None}
    current_a = direct_current_a + constant_power_w / terminal_v
    if terminal_v < cutoff_v:
        return {'reason': 'VOLTAGE_CUTOFF', 'terminal_v': terminal_v, 'current_a': current_a}
    return {'reason': None, 'terminal_v': terminal_v, 'current_a': current_a}


def input_status(config):
    missing = sorted(key for key, value in config['physical_inputs'].items() if value is None)
    if not missing:
        return {'gate': 'INDEPENDENT_REVIEW_REQUIRED', 'missing': [],
                'note': 'Populated fields never auto-approve product or cell feasibility.'}
    return {'gate': 'FEASIBILITY_HOLD', 'missing': missing,
            'note': 'All reported numeric runtime cases use synthetic inputs; no measured feasibility verdict.'}


def prepare(config, variant=None):
    """Validate a synthetic fixture and expand each phase into exact startup/event intervals."""
    if config.get('schema_version') != 1:
        raise InvalidInput('Unknown CH03 input schema')
    if set(config['physical_inputs']) != PHYSICAL_REQUIRED:
        raise InvalidInput('Missing physical input inventory')
    inventory = config['physical_state_inventory']
    if (set(inventory) != PHYSICAL_BLOCKS or any(
            set(row) != {'rail', 'active', 'idle', 'retention', 'off',
                         'startup_energy', 'startup_duration'} or
            any(row[name] is not None for name in
                ('active', 'idle', 'retention', 'off', 'startup_energy', 'startup_duration'))
            for row in inventory.values())):
        raise InvalidInput('Incomplete or unreviewed physical block-state inventory')
    if any(value is not None for value in config['physical_inputs'].values()):
        raise InvalidInput('Physical inputs are not yet implemented; never silently use an unknown format')
    cases = [parameter(x, 'mAh') for x in config['capacity_cases']]
    if cases != [8, 10, 14, 20]:
        raise InvalidInput('The four CH03 study cases must remain explicit')
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as handle:
        ids = {row['Req_ID'] for row in csv.DictReader(handle)}
    if not REQUIREMENTS <= ids:
        raise InvalidInput('CH03 requirement link is missing')
    ch02_modes = {x['id']: x for x in json.loads(CH02.read_text())['modes']}
    example = config['synthetic_example']
    if 'synthetic' not in example['classification'].lower():
        raise InvalidInput('Unmeasured example cannot be labeled physical')
    cell = example['cell']
    ocv_empty = parameter(cell['ocv_empty'], 'V')
    ocv_full = parameter(cell['ocv_full'], 'V')
    resistance = parameter(cell['series_resistance'], 'ohm')
    cutoff = parameter(cell['cutoff_voltage'], 'V')
    fraction = parameter(cell['capacity_fraction'], 'ratio')
    if not (0 < fraction <= 1 and ocv_full > ocv_empty > cutoff > 0 and resistance >= 0):
        raise InvalidInput('Invalid synthetic cell bounds')
    multiplier = 1.0
    variant_id = 'base'
    variant_parameter = None
    if variant is not None:
        variant_id = variant['id']
        variant_parameter = variant['parameter']
        multiplier = parameter(variant['multiplier'], 'ratio')
        if multiplier <= 0 or variant_parameter not in ('series_resistance', 'capacity_fraction',
                                                        'efficiency', 'optical_duty'):
            raise InvalidInput('Unsupported or nonpositive sensitivity multiplier')
        if variant_parameter == 'series_resistance':
            resistance = inside_study_range(cell['series_resistance'], resistance * multiplier)
        elif variant_parameter == 'capacity_fraction':
            fraction = inside_study_range(cell['capacity_fraction'], fraction * multiplier)
    if not 0 < fraction <= 1:
        raise InvalidInput('Available-charge study fraction exceeds one')

    rails = {}
    for name, raw in example['rails'].items():
        voltage = parameter(raw['output_voltage'], 'V')
        efficiency = parameter(raw['efficiency'], 'ratio')
        iq_a = parameter(raw['quiescent_battery_current'], 'mA') / 1000
        if variant_parameter == 'efficiency':
            efficiency = inside_study_range(raw['efficiency'], efficiency * multiplier)
        if voltage <= 0 or not 0 < efficiency <= 1 or iq_a < 0:
            raise InvalidInput(f'Invalid rail power data: {name}')
        rails[name] = {'voltage_v': voltage, 'efficiency': efficiency, 'iq_a': iq_a}

    blocks = {}
    for name, raw in example['blocks'].items():
        rail = raw['rail']
        if rail != 'battery' and rail not in rails:
            raise InvalidInput(f'Unknown rail: {name}')
        states = {key: parameter(value, 'mA') / 1000
                  for key, value in raw['state_currents'].items()}
        if any(value < 0 for value in states.values()):
            raise InvalidInput(f'Negative current: {name}')
        blocks[name] = {'rail': rail, 'state_currents_a': states}
    if set(blocks) - set(config['physical_state_inventory']):
        raise InvalidInput('Synthetic block missing from physical state inventory')

    phases = []
    for raw in example['cycle']:
        name = raw['id']
        mode = ch02_modes.get(raw['ch02_reference_mode'])
        if mode is None or mode['class'] != 'candidate':
            raise InvalidInput(f'Phase refers to an unapproved/missing CH02 mode: {name}')
        duration = parameter(raw['duration'], 's')
        if variant_parameter == 'optical_duty' and name == 'optical_and_radio':
            duration *= multiplier
        if variant_parameter == 'optical_duty' and name == 'rest':
            original_pulse = next(parameter(p['duration'], 's') for p in example['cycle']
                                  if p['id'] == 'optical_and_radio')
            duration -= original_pulse * (multiplier - 1)
        inside_study_range(raw['duration'], duration)
        enabled = raw['enabled_rails']
        if len(enabled) != len(set(enabled)) or not set(enabled) <= rails.keys():
            raise InvalidInput(f'Duplicated/unknown enabled rail: {name}')
        if set(raw['block_states']) != blocks.keys() or duration <= 0:
            raise InvalidInput(f'Missing block state or invalid duration: {name}')
        p_out_by_rail = defaultdict(float)
        i_direct = 0.0
        for block_name, state in raw['block_states'].items():
            block = blocks[block_name]
            if state not in block['state_currents_a']:
                raise InvalidInput(f'Unspecified state current: {block_name}.{state}')
            current_a = block['state_currents_a'][state]
            if block['rail'] == 'battery':
                i_direct += current_a
            else:
                if current_a and block['rail'] not in enabled:
                    raise InvalidInput(f'Active {block_name} on disabled rail')
                p_out_by_rail[block['rail']] += current_a * rails[block['rail']]['voltage_v']
        if raw['block_states'].get('optical_led') == 'active' and mode['led_active_max'] < 1:
            raise InvalidInput('LED requested in a CH02 mode with no LED output')
        p_output = sum(p_out_by_rail.values())
        p_converter = sum(p / rails[rail]['efficiency'] for rail, p in p_out_by_rail.items())
        iq = sum(rails[rail]['iq_a'] for rail in enabled)
        events = []
        for event in raw['startup_events']:
            energy_j = parameter(event['input_energy'], 'uJ') / 1e6
            event_s = parameter(event['duration'], 's')
            if not (0 < event_s <= duration and energy_j >= 0):
                raise InvalidInput(f'Invalid startup event: {name}')
            events.append((event_s, energy_j / event_s))
        boundaries = sorted({0.0, duration, *(seconds for seconds, _ in events)})
        for start, stop in zip(boundaries, boundaries[1:]):
            startup_p = sum(power for seconds, power in events if start < seconds)
            phases.append({'id': name, 'mode': mode['id'], 'duration_s': stop - start,
                           'p_out_w': p_output, 'p_converter_w': p_converter,
                           'p_startup_w': startup_p, 'i_direct_a': i_direct, 'i_q_a': iq,
                           'enabled_rails': list(enabled), 'active_blocks': sorted(
                               key for key, state in raw['block_states'].items()
                               if blocks[key]['state_currents_a'][state] > 0)})
    if not phases or sum(p['duration_s'] for p in phases) <= 0:
        raise InvalidInput('Synthetic schedule is empty')
    return {'variant': variant_id, 'capacity_cases_mAh': cases,
            'cell': {'ocv_empty_v': ocv_empty, 'ocv_full_v': ocv_full,
                     'r_ohm': resistance, 'cutoff_v': cutoff, 'capacity_fraction': fraction},
            'phases': phases, 'cycle_duration_s': sum(p['duration_s'] for p in phases),
            'physical_gate': input_status(config)}


def point(phase, cell, soc):
    ocv = cell['ocv_empty_v'] + (cell['ocv_full_v'] - cell['ocv_empty_v']) * soc
    p = phase['p_converter_w'] + phase['p_startup_w']
    i0 = phase['i_direct_a'] + phase['i_q_a']
    return solve_cell(ocv, cell['r_ohm'], p, i0, cell['cutoff_v'])


def snapshots(model):
    """Cycle-resolved voltage/current demand at declared synthetic SOCs, not a cell transient."""
    output = []
    for soc in (1.0, 0.5, 0.1):
        phases = []
        for phase in model['phases']:
            result = point(phase, model['cell'], soc)
            phases.append({'phase': phase['id'], 'reference_mode': phase['mode'],
                           'duration_s': phase['duration_s'], 'active_blocks': phase['active_blocks'],
                           'output_load_w': phase['p_out_w'], 'reason': result['reason'],
                           'battery_current_mA': round(result['current_a'] * 1000, 6)
                           if result['current_a'] is not None else None,
                           'terminal_voltage_v': round(result['terminal_v'], 6)
                           if result['terminal_v'] is not None else None})
        output.append({'state_of_charge': soc, 'cycle_segments': phases})
    return output


def simulate(model, capacity_mAh, step_divisor=1, max_cycles=1_000_000):
    """Piecewise constant pulse integration; check cutoff at each segment boundary."""
    if not isinstance(step_divisor, int) or step_divisor <= 0 or capacity_mAh <= 0:
        raise InvalidInput('Bad capacity or integration resolution')
    cell = model['cell']
    charge_c = capacity_mAh * 3.6 * cell['capacity_fraction']
    remaining_c = charge_c
    if all(p['p_converter_w'] + p['p_startup_w'] == 0 and
           p['i_direct_a'] + p['i_q_a'] == 0 for p in model['phases']):
        return {'reason': 'NO_FINITE_RUNTIME', 'conditional_runtime_s': None,
                'capacity_label_mAh': capacity_mAh}
    elapsed_s = peak_requested_a = peak_delivered_a = 0.0
    min_delivered_v = float('inf')
    energy = defaultdict(float)
    by_mode_energy = defaultdict(float)
    reason = first_failed_v = None
    unsolved_peak_request = False
    samples = 0
    for _ in range(max_cycles):
        for phase in model['phases']:
            for _ in range(step_divisor):
                soc = max(remaining_c / charge_c, 0.0)
                solved = point(phase, cell, soc)
                if solved['current_a'] is not None:
                    peak_requested_a = max(peak_requested_a, solved['current_a'])
                if solved['reason']:
                    reason, first_failed_v = solved['reason'], solved['terminal_v']
                    unsolved_peak_request = reason == 'NO_POWER_SOLUTION'
                    break
                voltage, current = solved['terminal_v'], solved['current_a']
                dt = phase['duration_s'] / step_divisor
                if current * dt >= remaining_c:
                    dt = remaining_c / current
                    reason = 'CHARGE_EXHAUSTED'
                used_c = current * dt
                remaining_c = max(0.0, remaining_c - used_c)
                elapsed_s += dt
                peak_delivered_a = max(peak_delivered_a, current)
                min_delivered_v = min(min_delivered_v, voltage)
                battery_j = voltage * current * dt
                energy['battery_j'] += battery_j
                energy['output_j'] += phase['p_out_w'] * dt
                energy['converter_loss_j'] += (phase['p_converter_w'] - phase['p_out_w']) * dt
                energy['direct_and_quiescent_j'] += voltage * (phase['i_direct_a'] + phase['i_q_a']) * dt
                energy['startup_j'] += phase['p_startup_w'] * dt
                by_mode_energy[phase['mode']] += battery_j
                samples += 1
                if reason:
                    break
            if reason:
                break
        if reason:
            break
    else:
        reason = 'MAX_CYCLES_REACHED'
    balance_j = (energy['battery_j'] - energy['output_j'] - energy['converter_loss_j']
                 - energy['direct_and_quiescent_j'] - energy['startup_j'])
    return {'capacity_label_mAh': capacity_mAh, 'conditional_runtime_s': round(elapsed_s, 6),
            'max_integration_interval_s': round(max(p['duration_s'] for p in model['phases']) / step_divisor, 6),
            'reason': reason, 'first_failed_terminal_voltage_v': round(first_failed_v, 6)
            if first_failed_v is not None else None,
            'peak_requested_battery_current_mA': None if unsolved_peak_request
            else round(peak_requested_a * 1000, 6),
            'peak_delivered_battery_current_mA': round(peak_delivered_a * 1000, 6),
            'minimum_delivered_terminal_voltage_v': None if math.isinf(min_delivered_v)
            else round(min_delivered_v, 6),
            'battery_energy_mWh': round(energy['battery_j'] / 3.6, 9),
            'load_output_energy_mWh': round(energy['output_j'] / 3.6, 9),
            'converter_loss_mWh': round(energy['converter_loss_j'] / 3.6, 9),
            'direct_and_quiescent_mWh': round(energy['direct_and_quiescent_j'] / 3.6, 9),
            'startup_input_mWh': round(energy['startup_j'] / 3.6, 9),
            'balance_error_mWh': round(balance_j / 3.6, 12),
            'discharged_charge_mAh': round((charge_c - remaining_c) / 3.6, 9),
            'battery_energy_by_reference_mode_mWh': {
                mode: round(value / 3.6, 9) for mode, value in sorted(by_mode_energy.items())},
            'integration_steps': samples,
            'cell_pulse_current_limit': 'UNKNOWN; no physical current-safety pass'}


def evaluate(config):
    model = prepare(config)
    physical_gate = model['physical_gate']
    base = [simulate(model, capacity) for capacity in model['capacity_cases_mAh']]
    variants = []
    for sensitivity in config['synthetic_example']['sensitivities']:
        altered = prepare(config, sensitivity)
        variants.append({'id': sensitivity['id'], 'parameter': sensitivity['parameter'],
                         'multiplier': parameter(sensitivity['multiplier'], 'ratio'),
                         'case_mAh': 10, 'result': simulate(altered, 10)})
    finer = simulate(model, 10, step_divisor=2)
    baseline_10 = next(row for row in base if row['capacity_label_mAh'] == 10)
    convergence_difference = abs(baseline_10['conditional_runtime_s']
                                 - finer['conditional_runtime_s'])
    if convergence_difference > model['cycle_duration_s'] + 1e-5:
        raise AssertionError('Step-size convergence exceeds a whole synthetic cycle')
    ids = {m['id'] for m in json.loads(CH02.read_text())['modes']}
    modeled_modes = {phase['mode'] for phase in model['phases']}
    return {'schema_version': 1, 'evidence_class': 'SYNTHETIC_CONDITIONAL',
            'gate': {'model': 'MODEL_PASS_IF_REGRESSION_PASSES', **physical_gate},
            'input_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'ch02_input_sha256': hashlib.sha256(CH02.read_bytes()).hexdigest(),
            'cycle_duration_s': model['cycle_duration_s'],
            'physical_state_inventory': config['physical_state_inventory'],
            'unmodeled_ch02_modes': sorted(ids - modeled_modes),
            'reference_mode_cycle_energy': 'Synthetic rest + daily-health examples; not real product schedules',
            'synthetic_traces': snapshots(model),
            'capacity_cases': base,
            'ten_mAh_sensitivities': variants,
            'convergence_10_mAh': {'base_runtime_s': baseline_10['conditional_runtime_s'],
                                   'half_step_runtime_s': finer['conditional_runtime_s'],
                                   'difference_s': round(convergence_difference, 6),
                                   'tolerance_s': model['cycle_duration_s']},
            'assumption_limit': 'Linear OCV and fixed R/efficiency are arithmetic probes only; no pulse dynamics, heating, temperature/aging law, validated current limit, safety or physical runtime verdict'}


def render(config, result):
    cases = result['capacity_cases']
    variants = result['ten_mAh_sensitivities']
    lines = [
        '# CH03: Synthetic battery-energy and peak-current accounting', '',
        '**Evidence class:** SYNTHETIC_CONDITIONAL. The cell, efficiency, duty cycle and nearly all loads are invented mathematical inputs. The 150 mA LED value is a CH02 candidate *output* target, not a measured battery current or safe operating limit. No product mode, runtime, cold performance or charge limit is approved.', '',
        f'Input SHA-256: `{result["input_sha256"]}`; CH02 SHA-256: `{result["ch02_input_sha256"]}`. Regenerate with `python3 models/python/ch03_energy.py --write`; check with `--check`.', '',
        '## First-principles accounting', '',
        '- Per enabled rail: battery-equivalent constant power is `Vout × Iout / η`; quiescent current is added once at the battery input. Direct battery loads and coincident RF/optical loads are summed at the same instant. Battery energy is integrated as `∫ Vterm × Ibat dt`, separately from charge `∫ Ibat dt`. mAh alone is not energy.',
        '- The illustrative cell uses a linear open-circuit-voltage-versus-charge line and one fixed series resistance. The high-voltage root of `Vterm = Voc − R × (Idirect + Iq + Pconstant/Vterm)` is used; no real chemistry, transient impedance, recovery or battery pulse-current limit is supplied.',
        '- CH02 mode IDs label a synthetic one-second rest/sense/optical collision cycle. This is **not** a 24-hour wear schedule. Every other CH02 mode lacks a power-state and product-duty map. Startup energy is applied over a stated event window; shorter unmeasured transients could create a higher peak.', '',
        '## Four capacity labels in the synthetic cycle', '',
        '| Label | Approximate synthetic runtime | Stop reason | Peak requested battery current | Minimum delivered terminal voltage | Battery energy |',
        '|---:|---:|---|---:|---:|---:|',
    ]
    for row in cases:
        peak = f'{row["peak_requested_battery_current_mA"]:.2f} mA' if row['peak_requested_battery_current_mA'] is not None else 'unsolved'
        minimum_v = (f'{row["minimum_delivered_terminal_voltage_v"]:.3f} V'
                     if row['minimum_delivered_terminal_voltage_v'] is not None else 'not delivered')
        lines.append(f'| {row["capacity_label_mAh"]:g} mAh | {row["conditional_runtime_s"]/3600:.3f} h | {row["reason"]} | {peak} | {minimum_v} | {row["battery_energy_mWh"]:.3f} mWh |')
    lines += ['', 'These are illustrative charge-capacity **labels** with synthetic OCV, resistance and load data. A `VOLTAGE_CUTOFF` result rejects a requested load after the listed approximate elapsed time. The interval solver checks operating conditions at each segment start, with at most 0.89 s between checks here. This is **not** a guaranteed bound on numerical error or a measured cell runtime.', '',
              '## Sensitivity at the 10 mAh label', '',
              '| Input change (invented) | Conditional runtime | Peak requested current | Stop reason |',
              '|---|---:|---:|---|']
    base10 = next(row for row in cases if row['capacity_label_mAh'] == 10)
    lines.append(f'| baseline | {base10["conditional_runtime_s"]/3600:.3f} h | {base10["peak_requested_battery_current_mA"]:.2f} mA | {base10["reason"]} |')
    for variant in variants:
        row = variant['result']
        peak = f'{row["peak_requested_battery_current_mA"]:.2f} mA' if row['peak_requested_battery_current_mA'] is not None else 'unsolved'
        lines.append(f'| {variant["id"]}: ×{variant["multiplier"]:g} | {row["conditional_runtime_s"]/3600:.3f} h | {peak} | {row["reason"]} |')
    lines += ['', f'Half-step integration changes the 10 mAh approximate runtime by {result["convergence_10_mAh"]["difference_s"]:.6f} s, within the chosen {result["convergence_10_mAh"]["tolerance_s"]:.3f} s numerical regression tolerance. Energy is separately allocated to rail output, conversion loss, direct/quiescent draw and startup. The largest rounded energy-balance residual across base cases is {max(abs(x["balance_error_mWh"]) for x in cases):.3g} mWh.', '',
              '## Mode and per-block state coverage', '',
              'The generated JSON records the three synthetic cycle segments at 100%, 50% and 10% assumed state of charge, with battery current and terminal voltage *at each segment*; it also records lifetime energy by referenced CH02 mode. These snapshots are static-equivalent traces, not measured pulse waveforms. Unmodeled CH02 modes: ' + ', '.join(f'`{x}`' for x in result['unmodeled_ch02_modes']) + '.', '',
              '| Physical state inventory | Source condition | Active / idle / retention / off / startup evidence |',
              '|---|---|---|']
    for name in sorted(result['physical_state_inventory']):
        lines.append(f'| `{name}` | Unselected hardware and mode | All missing; synthetic subset does not close this row |')
    lines += ['', '## Gate and blockers', '',
              '**MODEL_PASS** for reproducible, internally consistent synthetic accounting and fault reporting. **FEASIBILITY_HOLD** for any battery, runtime, safety or architecture claim: the physical fields remain missing and must be reviewed independently, even if populated later. In particular, fixed resistance cannot prove whether a 10 ms LED/RF pulse is safe for a small cell. No numeric battery current limit is asserted.', '',
              'Missing source inputs: ' + '; '.join(f'`{name}`' for name in result['gate']['missing']) + '.', '',
              'No technical block topology was selected; the §0.7 literature gate remains pending for subsequent block design. See `docs/reviews/CH03_GATE.md` for verification commands and decision boundaries.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true', help='regenerate committed CH03 reports')
    group.add_argument('--check', action='store_true', help='compare current reports with source and model')
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    result = evaluate(config)
    outputs = {RESULTS: json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n',
               REVIEW: render(config, result)}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        print('Wrote CH03 synthetic report and machine summary; physical feasibility HOLD')
    elif args.check:
        for path, content in outputs.items():
            if not path.is_file() or path.read_text() != content:
                raise AssertionError(f'Stale CH03 output: {path}')
        print('CH03 reports match model and input; physical feasibility HOLD')
    else:
        print(render(config, result))


if __name__ == '__main__':
    main()
