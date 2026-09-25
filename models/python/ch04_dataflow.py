#!/usr/bin/env python3
"""CH04 conditional transport/buffer accounting. All link and storage probes are synthetic."""

import argparse
import copy
import csv
import hashlib
import json
import math
from collections import deque
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/system/CH04_DATAFLOW_SCENARIOS.json'
CH02 = ROOT / 'specs/system/CH02_MODE_ASSUMPTIONS.json'
CH02_REPORT = ROOT / 'reports/subsystem/CH02_RESOURCE_SUMMARY.json'
REPORT = ROOT / 'reports/subsystem/CH04_DATAFLOW_SUMMARY.json'
REVIEW = ROOT / 'docs/budgets/CH04_DATA_MEMORY_REVIEW.md'
REQUIRED_INPUTS = {
    'owner_approved_modes_and_recording_duty',
    'confirmed_sample_timing_and_processing_semantics',
    'selected_packet_timestamp_crc_and_loss_policy',
    'measured_host_link_payload_wake_and_flow_control',
    'measured_ble_application_goodput_and_airtime',
    'measured_memory_write_busy_and_power',
    'qualified_memory_capacity_endurance_ecc_and_retention',
    'asic_sram_macro_area_power_retention_and_yield',
}
REQUIREMENTS = {'SYS-0008', 'SYS-0010', 'SYS-0016', 'MEM-0001', 'MEM-0002',
                'MEM-0004', 'MEM-0005', 'HIF-0001', 'HIF-0002', 'TIM-0001', 'TIM-0004'}


class InvalidInput(ValueError):
    """A missing condition or invalid unit would silently change a transport decision."""


def parameter(obj, unit, integer=False):
    if not isinstance(obj, dict) or obj.get('unit') != unit:
        raise InvalidInput(f'Expected a {unit} parameter with explicit metadata')
    if obj.get('evidence') not in ('assumed', 'vendor', 'measured'):
        raise InvalidInput('Missing evidence class')
    if not all(isinstance(obj.get(k), str) and obj[k].strip()
               for k in ('source', 'conditions')):
        raise InvalidInput('Missing numeric source or conditions')
    value, bounds = obj.get('value'), obj.get('range')
    valid_number = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
    if (not valid_number(value) or not isinstance(bounds, list) or len(bounds) != 2
            or not all(valid_number(x) for x in bounds) or not bounds[0] <= value <= bounds[1]
            or (integer and any(int(x) != x for x in [value, *bounds]))):
        raise InvalidInput(f'Invalid {unit} value or declared range')
    return int(value) if integer else value


def ceil_to(value, multiple):
    return ((value + multiple - 1) // multiple) * multiple


def validate_ch02(ch02):
    if ch02.get('schema_version') != 1:
        raise InvalidInput('Unexpected CH02 schema')
    streams = ch02['streams']
    modes = ch02['modes']
    if (len(modes) != 10 or len({m['id'] for m in modes}) != len(modes)
            or sorted(m['class'] for m in modes) != ['candidate'] * 8 + ['stress'] * 2):
        raise InvalidInput('CH02 candidate/stress inventory changed; review the CH04 schema')
    for mode in modes:
        if len(set(mode['streams'])) != len(mode['streams']) or not set(mode['streams']) <= streams.keys():
            raise InvalidInput('Missing or repeated CH02 stream')
    for stream in streams.values():
        if (stream['bank'] not in ('BIO', 'EDA', 'ECH', 'OPT', 'IMU', 'THM', 'AUDIO', 'FAST')
                or any(isinstance(stream[k], bool) or not isinstance(stream[k], int)
                       or stream[k] <= 0 for k in ('channels', 'bits_per_channel', 'sample_rate_hz'))):
            raise InvalidInput('Invalid CH02 stream dimensions')
        if stream['bank'] == 'OPT' and (stream['wavelength_phases'] <= 0 or
                                      stream['sample_rate_hz'] % stream['wavelength_phases']):
            raise InvalidInput('Inconsistent optical aggregate/per-wavelength rate')
    fmt = ch02['format_assumptions']
    for key in ('quality_bits_per_channel_sample', 'timestamp_bits_per_sample_group',
                'optical_wavelength_id_bits_per_sample_group'):
        if not isinstance(fmt[key], int) or fmt[key] < 0:
            raise InvalidInput('Invalid CH02 frame component')
    return {m['id']: m for m in modes}


def prepare(config, ch02=None):
    """Validate provenance, parameter units, exact source linkage and queue windows."""
    if config.get('schema_version') != 1 or set(config['physical_inputs']) != REQUIRED_INPUTS:
        raise InvalidInput('Unknown CH04 schema or incomplete physical-input inventory')
    if any(value is not None for value in config['physical_inputs'].values()):
        raise InvalidInput('Physical inputs require a separately reviewed schema and model')
    ch02 = ch02 if ch02 is not None else json.loads(CH02.read_text())
    modes = validate_ch02(ch02)
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as fh:
        ids = {row['Req_ID'] for row in csv.DictReader(fh)}
    if not REQUIREMENTS <= ids:
        raise InvalidInput('Unlinked CH04 requirement')
    f, m, t = config['format'], config['memory'], config['transport_probes']
    window_ms = parameter(f['batch_window_ms'], 'ms', True)
    if window_ms <= 0 or 1000 % window_ms:
        raise InvalidInput('Batch window must divide a one-second cycle exactly')
    fmt = {'window_ms': window_ms}
    for key in ('packet_header_bytes', 'packet_crc_bytes', 'packet_alignment_bytes',
                'asic_descriptor_bytes_per_packet'):
        fmt[key] = parameter(f[key], 'B', True)
        if fmt[key] <= 0:
            raise InvalidInput('Packet fields and alignment must be positive')
    for key, unit in (('fifo_margin', 'ratio'), ('host_link_guard', 'ratio')):
        fmt[key] = Fraction(str(parameter(f[key], unit)))
    if fmt['fifo_margin'] < 0 or fmt['host_link_guard'] < 1:
        raise InvalidInput('Invalid reserve or host guard')
    fmt['feature_bits'] = parameter(f['feature_only_bits_per_channel'], 'bit', True)
    fmt['feature_rate'] = parameter(f['feature_only_groups_per_second'], 'Hz', True)
    if fmt['feature_bits'] <= 0 or fmt['feature_rate'] <= 0:
        raise InvalidInput('Invalid feature sensitivity')
    memory = {key: parameter(m[key], 'KiB', True) * 1024 for key in
              ('workspace_kib', 'other_reserved_kib', 'illustrative_asic_fifo_kib',
               'illustrative_host_staging_kib')}
    memory['sram_candidates_B'] = [parameter(x, 'KiB', True) * 1024
                                   for x in m['provisional_sram_kib']]
    if memory['sram_candidates_B'] != [512 * 1024, 2048 * 1024]:
        raise InvalidInput('CH04 SRAM target labels have changed')
    clocks = [parameter(x, 'Hz', True) for x in t['host_clock_hz']]
    if clocks != ch02['format_assumptions']['illustrative_single_data_line_clocks_hz']:
        raise InvalidInput('Host probes must match the CH02 illustrative clock labels')
    efficiency = Fraction(str(ch02['format_assumptions']['illustrative_bus_payload_efficiency']))
    if not 0 < efficiency <= 1:
        raise InvalidInput('Invalid CH02 hypothetical bus efficiency')
    ble_rate = parameter(t['ble_application_payload_bps'], 'bit/s', True)
    nand_rate = parameter(t['nand_effective_write_Bps'], 'B/s', True)
    if ble_rate <= 0 or nand_rate <= 0:
        raise InvalidInput('Synthetic sink rates must be positive')

    patterns = {}
    for name, segments in config['availability_patterns'].items():
        slots = []
        for segment in segments:
            duration = parameter(segment['duration_ms'], 'ms', True)
            if duration <= 0 or duration % window_ms or set(segment) != {'duration_ms', 'host', 'ble', 'nand'}:
                raise InvalidInput('A service interval is not an integral batch window')
            if any(type(segment[k]) is not bool for k in ('host', 'ble', 'nand')):
                raise InvalidInput('Availability must be boolean')
            slots.extend([{key: segment[key] for key in ('host', 'ble', 'nand')}]
                         * (duration // window_ms))
        if len(slots) != 1000 // window_ms:
            raise InvalidInput('A service pattern must cover exactly one second')
        patterns[name] = slots
    cases = config['cases']
    if len({c['id'] for c in cases}) != len(cases) or not cases:
        raise InvalidInput('Duplicate or absent transport case')
    for case in cases:
        route = case['route']
        if case['mode'] not in modes or case['pattern'] not in patterns or route not in ('host', 'host_ble', 'local_nand'):
            raise InvalidInput('Unknown mode, service pattern or destination')
        if route == 'local_nand':
            if 'host_clock_hz' in case or not any(x['nand'] for x in patterns[case['pattern']]):
                raise InvalidInput('NAND path cannot contain a host clock and needs a write window')
        elif case.get('host_clock_hz') not in clocks or not any(x['host'] for x in patterns[case['pattern']]):
            raise InvalidInput('Host path needs an explicitly probed clock and service window')
        if route == 'host_ble' and not any(x['ble'] for x in patterns[case['pattern']]):
            raise InvalidInput('BLE path lacks a radio service window')

    storage = config['nand_projection']
    if storage['mode'] not in modes or modes[storage['mode']]['class'] != 'candidate':
        raise InvalidInput('NAND projection needs a declared candidate mode')
    capacities = [parameter(x, 'Gbit', True) for x in storage['nominal_capacity_gbit']]
    if capacities != [4, 16]:
        raise InvalidInput('CH04 storage target labels have changed')
    nand = {'mode': storage['mode'], 'gbit': capacities,
            'usable': Fraction(str(parameter(storage['usable_capacity_fraction'], 'ratio'))),
            'page_B': parameter(storage['packed_page_bytes'], 'B', True),
            'write_amp': Fraction(str(parameter(storage['write_amplification'], 'ratio'))),
            'pe_cycles': parameter(storage['illustrative_pe_cycles'], 'cycle', True),
            'hours_per_day': Fraction(str(parameter(storage['illustrative_logging_hours_per_day'], 'h/day')))}
    if (not 0 < nand['usable'] <= 1 or nand['page_B'] <= 0 or nand['write_amp'] < 1
            or nand['pe_cycles'] <= 0 or not 0 < nand['hours_per_day'] <= 24):
        raise InvalidInput('Invalid NAND study parameters')
    return {'ch02': ch02, 'modes': modes, 'format': fmt, 'memory': memory,
            'host_efficiency': efficiency, 'host_clocks': clocks, 'ble_bps': ble_rate,
            'nand_Bps': nand_rate, 'patterns': patterns, 'cases': cases, 'nand': nand}


def group_bytes(stream, fmt, ch02_fmt, variant='raw'):
    if variant not in ('raw', 'feature_only'):
        raise InvalidInput('Unknown transformation profile')
    channels = stream['channels']
    payload_bits = channels * (stream['bits_per_channel'] if variant == 'raw' else fmt['feature_bits'])
    bits = (payload_bits + channels * ch02_fmt['quality_bits_per_channel_sample']
            + ch02_fmt['timestamp_bits_per_sample_group']
            + (ch02_fmt['optical_wavelength_id_bits_per_sample_group']
               if stream['bank'] == 'OPT' else 0))
    return (bits + 7) // 8


def packet_for_window(stream, fmt, ch02_fmt, index, variant='raw'):
    """Exact packet at a 10 ms boundary; no arrival for a zero-sample window."""
    window = fmt['window_ms']
    rate = stream['sample_rate_hz'] if variant == 'raw' else fmt['feature_rate']
    count = (index + 1) * rate * window // 1000 - index * rate * window // 1000
    if count == 0:
        return 0, 0
    size = (fmt['packet_header_bytes'] + fmt['packet_crc_bytes']
            + count * group_bytes(stream, fmt, ch02_fmt, variant))
    return count, ceil_to(size, fmt['packet_alignment_bytes'])


def mode_rate(mode, model, variant='raw'):
    streams, ch02_fmt = model['ch02']['streams'], model['ch02']['format_assumptions']
    fmt = model['format']
    output = {'sample_groups_per_s': 0, 'packets_per_s': 0, 'sample_group_bytes_per_s': 0,
              'framed_bytes_per_s': 0, 'stream_detail': []}
    for name in mode['streams']:
        stream = streams[name]
        packets = [packet_for_window(stream, fmt, ch02_fmt, idx, variant)
                   for idx in range(1000 // fmt['window_ms'])]
        groups = sum(count for count, _ in packets)
        count_packets = sum(size > 0 for _, size in packets)
        gbytes = group_bytes(stream, fmt, ch02_fmt, variant)
        framed = sum(size for _, size in packets)
        expected = stream['sample_rate_hz'] if variant == 'raw' else fmt['feature_rate']
        if groups != expected:
            raise AssertionError('A one-second stream lost sample groups')
        output['sample_groups_per_s'] += groups
        output['packets_per_s'] += count_packets
        output['sample_group_bytes_per_s'] += groups * gbytes
        output['framed_bytes_per_s'] += framed
        output['stream_detail'].append({'stream': name, 'group_bytes': gbytes,
                                        'groups_per_s': groups, 'packets_per_s': count_packets,
                                        'framed_bytes_per_s': framed})
    output['raw_payload_bps'] = sum(streams[name]['channels'] * streams[name]['bits_per_channel']
                                    * streams[name]['sample_rate_hz'] for name in mode['streams'])
    output['packet_bytes_per_s'] = output['framed_bytes_per_s'] - output['sample_group_bytes_per_s']
    return output


class PacketQueue:
    """Whole frame occupies one descriptor until its final byte is serviced."""

    def __init__(self, descriptor_bytes):
        self.packets = deque()
        self.payload_bytes = 0
        self.descriptor_bytes = descriptor_bytes

    @property
    def memory_bytes(self):
        return self.payload_bytes + self.descriptor_bytes * len(self.packets)

    def add(self, size):
        if size <= 0:
            raise InvalidInput('A queued frame must have positive size')
        self.packets.append(size)
        self.payload_bytes += size

    def drain(self, budget):
        if budget < 0:
            raise InvalidInput('Negative service budget')
        sent = min(budget, self.payload_bytes)
        remaining = sent
        while remaining:
            old = self.packets[0]
            moved = min(old, remaining)
            remaining -= moved
            self.payload_bytes -= moved
            if moved == old:
                self.packets.popleft()
            else:
                self.packets[0] = old - moved
        return sent


def simulate_case(model, case):
    """Two repeated one-second periods expose a growing queue; no silent clipping."""
    fmt, memory, route = model['format'], model['memory'], case['route']
    pattern = model['patterns'][case['pattern']]
    q = PacketQueue(fmt['asic_descriptor_bytes_per_packet'])
    stage = 0
    peak_asic = peak_stage = total_in = total_delivered = 0
    overflow_asic_ms = overflow_stage_ms = None
    cycle_end = []
    cycle_signatures = []
    for cycle in range(2):
        for index, availability in enumerate(pattern):
            if route == 'host_ble' and availability['ble']:
                radio_budget = model['ble_bps'] * fmt['window_ms'] // 8000
                moved = min(stage, radio_budget)
                stage -= moved
                total_delivered += moved
            if route in ('host', 'host_ble') and availability['host']:
                link_budget = (Fraction(case['host_clock_hz'] * fmt['window_ms'], 8000)
                               * model['host_efficiency'])
                moved = q.drain(link_budget.numerator // link_budget.denominator)
                if route == 'host_ble':
                    stage += moved
                else:
                    total_delivered += moved
            if route == 'local_nand' and availability['nand']:
                moved = q.drain(model['nand_Bps'] * fmt['window_ms'] // 1000)
                total_delivered += moved
            peak_stage = max(peak_stage, stage)
            if stage > memory['illustrative_host_staging_kib'] and overflow_stage_ms is None:
                overflow_stage_ms = (cycle * len(pattern) + index + 1) * fmt['window_ms']
            for name in model['modes'][case['mode']]['streams']:
                _, size = packet_for_window(model['ch02']['streams'][name], fmt,
                                            model['ch02']['format_assumptions'], index)
                if size:
                    q.add(size)
                    total_in += size
            peak_asic = max(peak_asic, q.memory_bytes)
            if q.memory_bytes > memory['illustrative_asic_fifo_kib'] and overflow_asic_ms is None:
                overflow_asic_ms = (cycle * len(pattern) + index + 1) * fmt['window_ms']
        cycle_end.append((q.payload_bytes, q.memory_bytes, stage))
        cycle_signatures.append((tuple(q.packets), stage))
    if total_in != total_delivered + q.payload_bytes + stage:
        raise AssertionError('Produced bytes differ from delivered plus queued bytes')
    growth = {'asic_payload_B': cycle_end[1][0] - cycle_end[0][0],
              'asic_with_descriptors_B': cycle_end[1][1] - cycle_end[0][1],
              'host_stage_B': cycle_end[1][2] - cycle_end[0][2]}
    status = ('BOUNDED_IN_SYNTHETIC_CYCLE' if cycle_signatures[0] == cycle_signatures[1]
              else 'REPEATED_CYCLE_GROWTH')
    if any(v < 0 for v in growth.values()):
        raise AssertionError('Backlog from an empty queue cannot shrink over two identical cycles')
    if status == 'REPEATED_CYCLE_GROWTH' and not any(v > 0 for v in growth.values()):
        raise InvalidInput('Two cycles are insufficient to establish a repeated-state queue')
    fifo_with_margin = math.ceil(peak_asic * (1 + fmt['fifo_margin']))
    sram = (fifo_with_margin + memory['workspace_kib']
            + memory['other_reserved_kib']) if status == 'BOUNDED_IN_SYNTHETIC_CYCLE' else None
    return {'id': case['id'], 'mode': case['mode'], 'class': model['modes'][case['mode']]['class'],
            'route': route, 'service_pattern': case['pattern'],
            'host_clock_hz_probe': case.get('host_clock_hz'),
            'queue_status': status, 'cycle_end_backlog_B': cycle_end,
            'second_cycle_backlog_growth_B': growth,
            'peak_asic_fifo_with_descriptors_B': peak_asic,
            'peak_host_stage_payload_B': peak_stage if route == 'host_ble' else None,
            'first_illustrative_asic_fifo_overflow_ms': overflow_asic_ms,
            'first_illustrative_host_stage_overflow_ms': (overflow_stage_ms if route == 'host_ble' else None),
            'illustrative_asic_fifo_limit_B': memory['illustrative_asic_fifo_kib'],
            'illustrative_host_stage_limit_B': (memory['illustrative_host_staging_kib']
                                                 if route == 'host_ble' else None),
            'finite_horizon_asic_fifo_with_margin_B': fifo_with_margin,
            'minimum_total_sram_B_if_bounded': sram,
            'sram_candidate_fit_if_bounded': ({str(n // 1024) + '_KiB': sram <= n
                                                for n in memory['sram_candidates_B']}
                                               if sram is not None else None),
            'produced_bytes_two_cycles': total_in,
            'delivered_bytes_two_cycles': total_delivered,
            'remaining_payload_bytes': q.payload_bytes + stage,
            'note': 'Two cycles of a synthetic service trace; stable queue is not a measured link, NAND or radio pass.'}


def nand_projections(model, mode_rates):
    nand = model['nand']
    bps = mode_rates[nand['mode']]['raw']['framed_bytes_per_s']
    if bps <= 0:
        raise InvalidInput('NAND projection needs a nonempty mode')
    daily_logical = Fraction(bps * 3600) * nand['hours_per_day']
    daily_pages = math.ceil(daily_logical / nand['page_B'])
    physical_day = daily_pages * nand['page_B'] * nand['write_amp']
    output = []
    for gbit in nand['gbit']:
        usable = Fraction(gbit * 1_000_000_000, 8) * nand['usable']
        cycles_day = physical_day / usable
        output.append({'candidate_nominal_gbit_decimal': gbit,
                       'synthetic_usable_bytes': int(usable),
                       'framed_logging_bytes_per_s': bps,
                       'full_if_continuous_minutes': round(float(usable / bps / 60), 3),
                       'assumed_logging_hours_per_day': float(nand['hours_per_day']),
                       'logical_bytes_per_assumed_day': float(daily_logical),
                       'physical_bytes_per_assumed_day_with_page_and_WA': float(physical_day),
                       'synthetic_full_equivalent_PE_cycles_per_day': round(float(cycles_day), 6),
                       'synthetic_PE_limit_days_if_offloaded': round(float(nand['pe_cycles'] / cycles_day), 3),
                       'one_assumed_day_fits_without_offload': daily_logical <= usable,
                       'note': 'Wear example assumes even wear and continued offload; ECC, retention, bad blocks and actual P/E unknown.'})
    return output


def evaluate(config):
    model = prepare(config)
    ch02_result = {row['id']: row for row in json.loads(CH02_REPORT.read_text())['modes']}
    if set(ch02_result) != set(model['modes']):
        raise InvalidInput('CH02 generated report and source modes differ')
    mode_rates = {}
    for name, mode in model['modes'].items():
        raw = mode_rate(mode, model)
        feature = mode_rate(mode, model, 'feature_only')
        if raw['raw_payload_bps'] != ch02_result[name]['raw_payload_bps']:
            raise InvalidInput('CH04 raw bits disagree with the checked CH02 output')
        raw['minimum_host_clock_hz_at_illustrative_efficiency_and_guard'] = math.ceil(
            Fraction(raw['framed_bytes_per_s'] * 8) * model['format']['host_link_guard']
            / model['host_efficiency']) if raw['framed_bytes_per_s'] else None
        mode_rates[name] = {'class': mode['class'], 'ch02_scenario_framed_bps':
                            ch02_result[name]['scenario_framed_bps'],
                            'ch02_bank_conflicts': ch02_result[name]['bank_conflicts'],
                            'raw': raw, 'feature_only_hypothesis': feature}
    cases = [simulate_case(model, x) for x in model['cases']]
    storage = nand_projections(model, mode_rates)
    # Re-evaluate a few explicitly declared study bounds, never as vendor limits.
    batch = copy.deepcopy(config)
    batch['format']['batch_window_ms']['value'] = 20
    batch_model = prepare(batch)
    audio_20ms = simulate_case(batch_model, next(x for x in batch_model['cases']
                                                  if x['id'] == 'audio_host_wake'))
    host_wake = copy.deepcopy(config)
    windows = host_wake['availability_patterns']['host_sleep_200ms']
    windows[0]['duration_ms']['value'] = 300
    windows[1]['duration_ms']['value'] = 700
    wake_model = prepare(host_wake)
    audio_300ms = simulate_case(wake_model, next(x for x in wake_model['cases']
                                                  if x['id'] == 'audio_host_wake'))
    slow_ble = copy.deepcopy(config)
    slow_ble['transport_probes']['ble_application_payload_bps']['value'] = 100000
    ble_model = prepare(slow_ble)
    daily_ble_slow = simulate_case(ble_model, next(x for x in ble_model['cases']
                                                    if x['id'] == 'daily_host_ble'))
    busy_nand = copy.deepcopy(config)
    windows = busy_nand['availability_patterns']['nand_busy_first_100ms']
    windows[0]['duration_ms']['value'] = 300
    windows[1]['duration_ms']['value'] = 700
    nand_model = prepare(busy_nand)
    research_nand_busy = simulate_case(nand_model, next(x for x in nand_model['cases']
                                                        if x['id'] == 'research_local_nand'))
    sensitivities = [
        {'change': 'audio batch 10→20 ms (synthetic)', 'result': audio_20ms},
        {'change': 'audio host unavailable 200→300 ms (synthetic)', 'result': audio_300ms},
        {'change': 'daily BLE available goodput 1,000,000→100,000 bit/s (synthetic)',
         'result': daily_ble_slow},
        {'change': 'research NAND busy 100→300 ms (synthetic)', 'result': research_nand_busy},
    ]
    return {'schema_version': 1, 'evidence_class': 'SYNTHETIC_CONDITIONAL',
            'gate': {'model': 'MODEL_PASS_IF_REGRESSION_PASSES', 'physical': 'FEASIBILITY_HOLD',
                     'missing': sorted(REQUIRED_INPUTS)},
            'input_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
            'ch02_input_sha256': hashlib.sha256(CH02.read_bytes()).hexdigest(),
            'ch02_report_sha256': hashlib.sha256(CH02_REPORT.read_bytes()).hexdigest(),
            'accounting': {'batch_window_ms': model['format']['window_ms'],
                           'packet_header_B': model['format']['packet_header_bytes'],
                           'packet_crc_B': model['format']['packet_crc_bytes'],
                           'packet_alignment_B': model['format']['packet_alignment_bytes'],
                           'descriptor_B_per_packet': model['format']['asic_descriptor_bytes_per_packet'],
                           'illustrative_host_payload_efficiency': float(model['host_efficiency']),
                           'sram_workspace_B': model['memory']['workspace_kib'],
                           'sram_other_reserved_B': model['memory']['other_reserved_kib']},
            'mode_rates': mode_rates, 'two_cycle_queue_cases': cases,
            'nand_capacity_and_wear_projections': storage, 'sensitivity': sensitivities,
            'limitations': 'All source rates candidate/stress; derived frame scheme/clock/radio/NAND/workspace are assumptions. No verified host, BLE, SRAM, product duty, real NAND endurance, ECC, retention, power or raw-to-feature equivalence.'}


def render(result):
    lines = [
        '# CH04: Conditional data rate, queue and memory review', '',
        '**Evidence class:** SYNTHETIC_CONDITIONAL. Eight CH02 modes are candidates; two are intentional stress probes. No product recording duty, protocol, real link throughput, BLE goodput or memory component is approved. A bounded synthetic queue is not a hardware PASS.', '',
        f'CH04 input SHA-256 `{result["input_sha256"]}`; CH02 source SHA-256 `{result["ch02_input_sha256"]}`; CH02 report SHA-256 `{result["ch02_report_sha256"]}`. Regenerate with `python3 models/python/ch04_dataflow.py --write`; verify with `--check`.', '',
        '## Framing and conservation rules', '',
        '- Raw stream `bit/s = channels × effective sample groups/s × nominal bits/channel`. CH02 optical rates are *aggregate per photodiode across wavelengths*. The frame encodes one whole-byte sample group containing all channel words, 8 quality bits per channel, 64 timestamp bits per group and 8 extra optical wavelength bits per group (the last three values come from CH02). The scenario additionally uses 4 B header + 2 B CRC and aligns each nonempty batch to 4 B. The header hypothetically carries stream ID and sequence/length; its format is not selected.',
        '- Frames arrive at each 10 ms boundary; drain existing FIFO first, then enqueue arriving frames. A partially drained ASIC packet retains its 16 B descriptor. For host→BLE, the host stage is an ideal byte queue; BLE drains existing host bytes before host transfer and new ASIC arrivals. Two repetitions expose sustained queue growth. The finite-horizon peak is never a valid sustainable SRAM size for a growing queue. This 10 ms aggregation cannot bound shorter simultaneous bursts or wake jitter.',
        '- At an illustrative 70% host payload efficiency, the *continuous-mode average* single-data-line clock target is `ceil(CH04 packet bit/s × 1.2 / 0.7)`; the timed queue separately captures the stated wake gaps. Service credits are rounded down to whole bytes per window, losing less than one byte of capacity per service window. Byte rounding and packet overhead explain differences from CH02 framed figures; neither is a strict protocol upper bound. The separately named feature-only sensitivity outputs one invented 16-bit feature/channel/second and **discards all original raw samples**. It cannot replace raw research/clinical evidence.', '',
        '## One-second continuous-mode accounting', '',
        '| CH02 mode | Class | Raw Mb/s | CH02 framed Mb/s | CH04 packed+packet Mb/s | Frames/s | Illustrative continuous-mode guarded host clock | Feature-only Mb/s |',
        '|---|---|---:|---:|---:|---:|---:|---:|',
    ]
    for name, row in result['mode_rates'].items():
        raw, feat = row['raw'], row['feature_only_hypothesis']
        clock = raw['minimum_host_clock_hz_at_illustrative_efficiency_and_guard']
        host = f'{clock/1e6:.3f} MHz' if clock else 'none'
        lines.append(f'| `{name}` | {row["class"]} | {raw["raw_payload_bps"]/1e6:.3f} | {row["ch02_scenario_framed_bps"]/1e6:.3f} | {raw["framed_bytes_per_s"]*8/1e6:.3f} | {raw["packets_per_s"]:,} | {host} | {feat["framed_bytes_per_s"]*8/1e6:.3f} |')
    lines += ['', 'The `resource_conflict_probe` is intentionally BIO/OPT converter-infeasible in CH02; its rate row is arithmetic only. Feature-only numbers are an invented output-profile sensitivity, not lossless compression, quality equivalence, or permission to stop storing raw samples.', '',
              '## Timed queues and SRAM', '',
              '| Case and route | Repeated-cycle queue | Growth per cycle | Peak ASIC FIFO incl. descriptors | Peak host staging | First 512 KiB ASIC overflow | First 128 KiB host overflow | Total SRAM if bounded |',
              '|---|---|---:|---:|---:|---|---|---:|']
    for row in result['two_cycle_queue_cases']:
        stage = (f'{row["peak_host_stage_payload_B"]/1024:.1f} KiB'
                 if row['peak_host_stage_payload_B'] is not None else 'n/a')
        sram = (f'{row["minimum_total_sram_B_if_bounded"]/1024:.1f} KiB'
                if row['minimum_total_sram_B_if_bounded'] is not None else 'no finite buffer')
        overflow = (f'{row["first_illustrative_asic_fifo_overflow_ms"]} ms'
                    if row['first_illustrative_asic_fifo_overflow_ms'] is not None else 'none in 2 s')
        host_overflow = (f'{row["first_illustrative_host_stage_overflow_ms"]} ms'
                         if row['first_illustrative_host_stage_overflow_ms'] is not None else 'none in 2 s') if row['route'] == 'host_ble' else 'n/a'
        growth = (row['second_cycle_backlog_growth_B']['asic_payload_B']
                  + row['second_cycle_backlog_growth_B']['host_stage_B'])
        lines.append(f'| `{row["id"]}` ({row["route"]}) | {row["queue_status"]} | {growth/1024:.1f} KiB/s | {row["peak_asic_fifo_with_descriptors_B"]/1024:.1f} KiB | {stage} | {overflow} | {host_overflow} | {sram} |')
    lines += ['', 'ASIC total SRAM uses `ceil((peak packet bytes + outstanding descriptor bytes) × 1.2) + 128 KiB workspace + 64 KiB other reserve`. The 512 KiB/2 MiB bounds in §21 are provisional. BLE staging is **additional host memory** and is not included in ASIC SRAM. Any growing ASIC *or host* queue makes the route unsustainable under this repeated synthetic service profile, even if it fits for the first two seconds. Overflow is reported, not silently dropped; actual loss/flow-control semantics need CH06/CH19.', '',
              '## Synthetic sensitivities', '',
              '| Changed assumption | Cycle status | Peak ASIC FIFO | Peak host staging |',
              '|---|---|---:|---:|']
    for entry in result['sensitivity']:
        row = entry['result']
        stage = (f'{row["peak_host_stage_payload_B"]/1024:.1f} KiB'
                 if row['peak_host_stage_payload_B'] is not None else 'n/a')
        lines.append(f'| {entry["change"]} | {row["queue_status"]} | {row["peak_asic_fifo_with_descriptors_B"]/1024:.1f} KiB | {stage} |')
    lines += ['', '## Local NAND conditional projection', '',
              'Packed research-raw frames are assumed to be written directly to a local candidate NAND, with **no simultaneous host/BLE duplicate route**. This storage example assumes 1 hour/day of the *unapproved* raw-research mode, 80% usable logical capacity, packed 2048 B pages, 2× write amplification, ideal even wear and a **hypothetical** 1000 P/E cycle label. A page is not padded separately for every stream packet.', '',
              '| Nominal NAND | Usable example | Filled by continuous research mode | Example one-day capture fits without offload | Example equivalent P/E cycles/day | Hypothetical P/E days if offloaded |',
              '|---:|---:|---:|---|---:|---:|']
    for row in result['nand_capacity_and_wear_projections']:
        lines.append(f'| {row["candidate_nominal_gbit_decimal"]} Gbit | {row["synthetic_usable_bytes"]/1e6:.0f} MB | {row["full_if_continuous_minutes"]:.2f} min | {"yes" if row["one_assumed_day_fits_without_offload"] else "no"} | {row["synthetic_full_equivalent_PE_cycles_per_day"]:.3f} | {row["synthetic_PE_limit_days_if_offloaded"]:.0f} |')
    lines += ['', 'A modeled fill time does not imply a successful log: sustained write bandwidth, busy-window backlog, controller ECC, bad blocks, retention, power and offload policy have no measured evidence. The hypothetical P/E arithmetic assumes prior offload and ideal wear leveling; real storage endurance is unknown.', '',
              '## Gate', '',
              '**MODEL_PASS** means deterministic packet/byte accounting, two-stage queue conservation, failures and tested sensitivities. **FEASIBILITY_HOLD** applies to approved modes, real host/BLE/NAND rate, SRAM area/power, buffer-loss policy, NAND endurance and any claim that feature extraction preserves needed raw information. CH03 physical battery feasibility also remains on hold. No technical block topology or timing architecture was selected.', '',
              'Missing evidence: ' + '; '.join(f'`{x}`' for x in result['gate']['missing']) + '. See `docs/reviews/CH04_GATE.md` and `docs/inputs/REQUIRED_INPUTS.md`. Stop at CH04; CH05 needs its own kickoff.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = evaluate(json.loads(CONFIG.read_text()))
    outputs = {REPORT: json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n',
               REVIEW: render(result)}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        print('Wrote CH04 conditional data, queue and NAND reports; physical feasibility HOLD')
    elif args.check:
        for path, content in outputs.items():
            if not path.is_file() or path.read_text() != content:
                raise AssertionError(f'Stale CH04 output: {path}')
        print('CH04 reports match inputs and model; physical feasibility HOLD')
    else:
        print(render(result))


if __name__ == '__main__':
    main()
