#!/usr/bin/env python3
"""CH05 behavioral timestamp reference. Synthetic clocks; no synthesizable RTL claim."""

import argparse
import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/system/CH05_TIMING_SCENARIOS.json'
REPORT = ROOT / 'reports/subsystem/CH05_TIMING_SUMMARY.json'
REVIEW = ROOT / 'docs/budgets/CH05_TIMING_REVIEW.md'
NSEC = 1_000_000_000
SOURCES = ('LED_PULSE', 'OPTICAL_ADC', 'EEG_ECG', 'AUDIO_FRAME',
           'ECHEM_WAVEFORM', 'IMU_SYNC', 'GPIO', 'DMA')
PHYSICAL = {'owner_approved_cross_sensor_accuracy_and_drift',
            'qualified_aon_fine_clock_pvt_jitter_power_area',
            'clock_reset_tree_implementation_and_cdc_rdc_signoff',
            'real_trigger_to_aperture_and_scan_settling',
            'selected_imu_sync_fifo_period_delay_and_tolerance',
            'qualified_host_epoch_exchange_uncertainty',
            'approved_while_asleep_event_capture_policy'}
REQUIREMENTS = {f'TIM-{i:04}' for i in (1, 2, 3, 4, 5, 6, 7, 9)} | {'SYS-0010', 'MEM-0001'}
UNITS = {'aon_clock_hz': 'Hz', 'fine_clock_hz': 'Hz', 'continuous_clock_hz': 'Hz',
         'representation_bits': 'bit', 'clock_error_ppm': 'ppm', 'resync_interval_s': 's',
         'cdc_stages': 'cycle', 'destination_clock_hz': 'Hz',
         'trigger_pipeline_cycles': 'cycle', 'sample_latency_ns': 'ns',
         'sample_jitter_bound_ns': 'ns', 'imu_period_ns': 'ns',
         'imu_pipeline_delay_ns': 'ns', 'imu_delay_spread_ns': 'ns',
         'imu_clock_error_ppm': 'ppm'}


class InvalidTiming(ValueError):
    """A requested guarantee cannot be deduced from the stated timebase."""


def ceil_fraction(x):
    return -(-x.numerator // x.denominator)


def number(entry, unit):
    if not isinstance(entry, dict) or set(entry) != {'value', 'unit', 'evidence', 'source', 'conditions', 'range'}:
        raise InvalidTiming('Each parameter needs value/unit/evidence/source/conditions/range')
    if entry['unit'] != unit or entry['evidence'] != 'assumed' or any(
            not isinstance(entry[k], str) or not entry[k].strip() for k in ('source', 'conditions')):
        raise InvalidTiming(f'Unreviewed evidence or unit: {unit}')
    value, limits = entry['value'], entry['range']
    if (type(value) is not int or type(limits) is not list or len(limits) != 2 or
            any(type(x) is not int for x in limits) or not limits[0] <= value <= limits[1]):
        raise InvalidTiming(f'Out-of-range integer {unit}')
    return value


def prepare(config):
    if config.get('schema_version') != 1 or set(config.get('physical_inputs', {})) != PHYSICAL:
        raise InvalidTiming('Missing physical inputs or unexpected schema')
    if any(v is not None for v in config['physical_inputs'].values()):
        raise InvalidTiming('Physical evidence needs a revised schema and gate')
    raw = config.get('parameters', {})
    if set(raw) != set(UNITS) or not isinstance(config.get('evidence_note'), str):
        raise InvalidTiming('Unexpected or missing clock parameter')
    p = {k: number(raw[k], unit) for k, unit in UNITS.items()}
    for key in ('aon_clock_hz', 'fine_clock_hz', 'continuous_clock_hz',
                'destination_clock_hz', 'resync_interval_s', 'imu_period_ns'):
        if p[key] <= 0:
            raise InvalidTiming(f'{key} must be positive')
    if p['representation_bits'] != 64 or p['cdc_stages'] < 2:
        raise InvalidTiming('CH05 tests assume 64-bit representation and at least two CDC stages')
    if p['fine_clock_hz'] < p['aon_clock_hz']:
        raise InvalidTiming('Fine capture clock must exceed AON clock')
    order = config.get('source_order')
    routes = config.get('trigger_routes')
    if order != list(SOURCES) or not isinstance(routes, list) or not routes:
        raise InvalidTiming('Incomplete or unstable trigger priority')
    pairs = []
    for route in routes:
        if (not isinstance(route, dict) or set(route) != {'source', 'target'} or
                route['source'] not in SOURCES or route['target'] not in SOURCES):
            raise InvalidTiming('Unknown trigger route')
        pairs.append((route['source'], route['target']))
    if len(pairs) != len(set(pairs)) or {x for x, _ in pairs} != set(SOURCES):
        raise InvalidTiming('Duplicate route or missing trigger source')
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as stream:
        ids = {row['Req_ID'] for row in csv.DictReader(stream)}
    if not REQUIREMENTS <= ids:
        raise InvalidTiming('Missing requirement link')
    return p


def count_at(time_ns, hz, error_ppm=0):
    if type(time_ns) is not int or time_ns < 0 or type(hz) is not int or hz <= 0:
        raise InvalidTiming('Invalid time or clock frequency')
    if type(error_ppm) is not int or abs(error_ppm) >= 1_000_000:
        raise InvalidTiming('Invalid signed clock tolerance')
    return time_ns * hz * (1_000_000 + error_ppm) // (NSEC * 1_000_000)


def next_edge(time_ns, hz):
    """Nominal next clock edge, represented as an exact rational nanosecond."""
    if type(time_ns) is not int or time_ns < 0 or type(hz) is not int or hz <= 0:
        raise InvalidTiming('Invalid event time or clock')
    count = ceil_fraction(Fraction(time_ns * hz, NSEC))
    return Fraction(count * NSEC, hz)


def extend_counter(previous_extended, raw, bits):
    """Half-range rule: reject intervals indistinguishable from backward/wrapped counts."""
    if (type(previous_extended) is not int or previous_extended < 0 or
            type(bits) is not int or not 2 <= bits <= 64 or
            type(raw) is not int or not 0 <= raw < (1 << bits)):
        raise InvalidTiming('Invalid counter snapshot')
    mask = (1 << bits) - 1
    delta = (raw - (previous_extended & mask)) & mask
    if delta >= 1 << (bits - 1):
        raise InvalidTiming('Ambiguous interval: more than half a counter range or reset')
    extended = previous_extended + delta
    if extended >= 1 << 64:
        raise InvalidTiming('64-bit timestamp overflow requires a new epoch')
    return extended


class Timekeeper:
    """Discrete clock readout and retained coarse epoch; no access to a true physical time oracle."""

    def __init__(self, aon_hz, fine_hz, *, continuous=False):
        if any(type(v) is not int or v <= 0 for v in (aon_hz, fine_hz)):
            raise InvalidTiming('Invalid clock')
        self.aon_hz, self.fine_hz, self.continuous = aon_hz, fine_hz, continuous
        self.mode = 'awake'
        self.last_us = 0
        self.last_real_ns = 0
        self.fine_anchor_count = 0
        self.epoch_us = 0
        self.wake_quantization_us = 0

    def transition(self, mode, real_ns):
        if mode not in ('awake', 'sleep') or type(real_ns) is not int or real_ns < self.last_real_ns:
            raise InvalidTiming('Clock transition is out of order')
        self.observe(real_ns)
        if mode == 'awake' and self.mode == 'sleep' and not self.continuous:
            coarse_us = count_at(real_ns, self.aon_hz) * 1_000_000 // self.aon_hz
            self.epoch_us = max(self.last_us, coarse_us)
            self.fine_anchor_count = count_at(real_ns, self.fine_hz)
            self.wake_quantization_us = (ceil_fraction(Fraction(1_000_000, self.aon_hz)) +
                                         ceil_fraction(Fraction(1_000_000, self.fine_hz)))
        self.mode = mode
        return self.last_us

    def observe(self, real_ns):
        if type(real_ns) is not int or real_ns < self.last_real_ns:
            raise InvalidTiming('Clock observation stepped backward')
        self.last_real_ns = real_ns
        if self.continuous:
            us = count_at(real_ns, self.fine_hz) * 1_000_000 // self.fine_hz
        elif self.mode == 'sleep':
            us = count_at(real_ns, self.aon_hz) * 1_000_000 // self.aon_hz
        else:
            us = self.epoch_us + ((count_at(real_ns, self.fine_hz) - self.fine_anchor_count)
                                  * 1_000_000 // self.fine_hz)
        self.last_us = max(self.last_us, us)
        if self.last_us >= 1 << 64:
            raise InvalidTiming('64-bit timestamp overflow')
        return self.last_us


class EpochMap:
    """Host epoch calibration never changes hardware monotonic timestamps."""

    def __init__(self, clock_error_ppm):
        if type(clock_error_ppm) is not int or clock_error_ppm < 0:
            raise InvalidTiming('Invalid clock error')
        self.error_ppm = clock_error_ppm
        self.anchor = None

    def synchronize(self, monotonic_us, epoch_ns, exchange_uncertainty_ns):
        if (type(monotonic_us) is not int or monotonic_us < 0 or
                type(epoch_ns) is not int or type(exchange_uncertainty_ns) is not int or
                exchange_uncertainty_ns < 0 or
                (self.anchor is not None and monotonic_us < self.anchor[0])):
            raise InvalidTiming('Invalid or backward host synchronization')
        self.anchor = (monotonic_us, epoch_ns, exchange_uncertainty_ns)

    def estimate(self, monotonic_us):
        if self.anchor is None or type(monotonic_us) is not int or monotonic_us < self.anchor[0]:
            raise InvalidTiming('Missing host anchor or time preceding anchor')
        base_us, epoch_ns, uncertainty_ns = self.anchor
        delta_us = monotonic_us - base_us
        return {'epoch_ns': epoch_ns + 1000 * delta_us,
                'uncertainty_bound_ns': uncertainty_ns +
                ceil_fraction(Fraction(delta_us * self.error_ppm, 1000))}


def event_budget(p, source_hz, *, asleep=False):
    if source_hz <= 0:
        raise InvalidTiming('Invalid capture clock')
    q_ns = ceil_fraction(Fraction(NSEC, source_hz))
    cdc_phase_ns = ceil_fraction(Fraction(NSEC, p['destination_clock_hz']))
    fixed_cdc_ns = ceil_fraction(Fraction((p['cdc_stages'] - 1) * NSEC,
                                         p['destination_clock_hz']))
    drift_ns = p['clock_error_ppm'] * p['resync_interval_s'] * 1000
    if asleep:
        # No active destination or bounded wake/retained queue exists in this model.
        return {'capture_quantization_bound_ns': q_ns, 'cdc_phase_bound_ns': None,
                'cdc_pipeline_nominal_ns': None,
                'sample_jitter_bound_ns': None, 'host_drift_bound_ns': drift_ns,
                'sample_time_vs_event_bound_ns': None, 'sleep_capture': True}
    return {'capture_quantization_bound_ns': q_ns,
            'cdc_phase_bound_ns': cdc_phase_ns,
            'cdc_pipeline_nominal_ns': fixed_cdc_ns,
            'sample_jitter_bound_ns': p['sample_jitter_bound_ns'],
            'host_drift_bound_ns': drift_ns,
            'sample_time_vs_event_bound_ns': q_ns + cdc_phase_ns + fixed_cdc_ns +
            ceil_fraction(Fraction(p['trigger_pipeline_cycles'] * NSEC, p['destination_clock_hz'])) +
            p['sample_latency_ns'] + p['sample_jitter_bound_ns'],
            'sleep_capture': asleep}


def trigger_events(events, p, keeper, routes):
    """Stable priority for ties; every event gets its own capture, no coalescing."""
    start_ns = keeper.last_real_ns
    if keeper.mode == 'sleep' and not keeper.continuous:
        raise InvalidTiming('Destination clock is off in sleep; no measured wake/queue contract')
    route_map = dict(routes)
    for event in events:
        if (not isinstance(event, dict) or set(event) != {'source', 'time_ns'} or
                event['source'] not in route_map or type(event['time_ns']) is not int or
                event['time_ns'] < start_ns):
            raise InvalidTiming('Unsupported, invalid or out-of-order trigger event')
    ordered = sorted(enumerate(events), key=lambda pair: (pair[1]['time_ns'],
                     SOURCES.index(pair[1]['source']), pair[0]))
    results = []
    for _, event in ordered:
        src = keeper.aon_hz if keeper.mode == 'sleep' and not keeper.continuous else keeper.fine_hz
        capture = next_edge(event['time_ns'], src)
        cdc = next_edge(ceil_fraction(capture), p['destination_clock_hz']) + Fraction(
            (p['cdc_stages'] - 1) * NSEC, p['destination_clock_hz'])
        trigger = cdc + Fraction(p['trigger_pipeline_cycles'] * NSEC, p['destination_clock_hz'])
        sample = trigger + p['sample_latency_ns']
        # Timestamp represents nominal sample aperture; input event has its own earlier occurrence.
        timestamp = keeper.observe(max(keeper.last_real_ns, ceil_fraction(sample)))
        results.append({'sequence': len(results), 'source': event['source'],
                        'target': route_map[event['source']], 'event_ns': event['time_ns'],
                        'capture_ns_upper': ceil_fraction(capture),
                        'sample_ns_upper': ceil_fraction(sample), 'sample_timestamp_us': timestamp,
                        'budget': event_budget(p, src, asleep=keeper.mode == 'sleep')})
    return results


def imu_sample(anchor_us, sync_index, sample_index, read_arrival_us, p):
    """Timestamp the physical aperture, not a batched FIFO read; allow earlier buffered samples."""
    if (any(type(v) is not int for v in (anchor_us, sync_index, sample_index, read_arrival_us)) or
            anchor_us < 0 or sync_index < 0 or sample_index < 0 or read_arrival_us < anchor_us or
            abs(sample_index - sync_index) >= 1 << 16):
        raise InvalidTiming('Missing/ambiguous IMU index, anchor, or FIFO arrival')
    distance = sample_index - sync_index
    nominal_ns = anchor_us * 1000 + distance * p['imu_period_ns'] - p['imu_pipeline_delay_ns']
    if nominal_ns < 0 or read_arrival_us * 1000 < nominal_ns:
        raise InvalidTiming('IMU aperture cannot follow its FIFO read')
    return {'sample_ns': nominal_ns, 'read_arrival_us': read_arrival_us,
            'uncertainty_bound_ns': p['imu_delay_spread_ns'] +
            ceil_fraction(Fraction(abs(distance) * p['imu_period_ns'] * p['imu_clock_error_ppm'], 1_000_000))}


def generate(config):
    p = prepare(config)
    hybrid = Timekeeper(p['aon_clock_hz'], p['fine_clock_hz'])
    awake_before = hybrid.observe(990_000_000)
    hybrid.transition('sleep', 1_000_000_000)
    sleep_sample = hybrid.observe(1_200_000_000)
    hybrid.transition('awake', 1_250_001_000)
    awake_after = hybrid.observe(1_260_000_000)
    continuous = Timekeeper(p['aon_clock_hz'], p['continuous_clock_hz'], continuous=True)
    continuous.observe(990_000_000)
    continuous.transition('sleep', 1_000_000_000)
    continuous_sleep = continuous.observe(1_200_000_000)
    continuous.transition('awake', 1_250_001_000)
    events = trigger_events([{'source': 'IMU_SYNC', 'time_ns': 1_270_000_000},
                             {'source': 'LED_PULSE', 'time_ns': 1_270_000_000},
                             {'source': 'GPIO', 'time_ns': 1_270_000_000}],
                            p, hybrid, [(r['source'], r['target']) for r in config['trigger_routes']])
    epoch = EpochMap(p['clock_error_ppm'])
    epoch.synchronize(awake_after, 1_700_000_000_000_000_000, 100_000)
    report = {
        'schema_version': 1, 'source_sha256': hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        'evidence_class': 'synthetic_model', 'gate': 'MODEL_PASS_PHYSICAL_HOLD',
        'clock_tree_concept': {'continuity_owner': 'retained AON domain',
                               'awake_capture': 'fine clock only while valid; explicit epoch handoff',
                               'comparison': 'continuous high-resolution counter, conditional on power'},
        'candidate_ticks_us': {name: round(1_000_000 / p[key], 6) for name, key in
                               [('aon', 'aon_clock_hz'), ('fine_awake', 'fine_clock_hz'),
                                ('continuous', 'continuous_clock_hz')]},
        'sleep_wake_probe_us': {'awake_before': awake_before, 'sleep': sleep_sample,
                                'awake_after': awake_after, 'continuous_sleep': continuous_sleep,
                                'wake_handoff_uncertainty_us': hybrid.wake_quantization_us},
        'host_epoch_probe': epoch.estimate(awake_after + p['resync_interval_s'] * 1_000_000),
        'trigger_matrix': config['trigger_routes'], 'simultaneous_events': events,
        'active_budget': event_budget(p, p['fine_clock_hz']),
        'sleep_budget': event_budget(p, p['aon_clock_hz'], asleep=True),
        'imu_fifo_probe': imu_sample(1_270_000, 5, 3, 1_300_000, p),
        'cdc_rdc_inventory': [
            {'path': 'AON → fine timer snapshot', 'method': 'coherent handshake with retained epoch and acknowledgment', 'state': 'model only'},
            {'path': 'async event → destination', 'method': 'captured/acknowledged event or queued toggle; no bare short pulse', 'state': 'model only'},
            {'path': 'timestamp/descriptor → host/DMA', 'method': 'stable multi-bit handshake or async FIFO; no separate bit flops', 'state': 'model only'},
            {'path': 'reset/clock transition → each domain', 'method': 'async assert, synchronized release and glitch-free switch proof pending', 'state': 'physical hold'}],
        'physical_inputs_missing': sorted(PHYSICAL),
    }
    return report


def render(report):
    ticks = report['candidate_ticks_us']
    probe = report['sleep_wake_probe_us']
    active, sleep = report['active_budget'], report['sleep_budget']
    routes = '\n'.join(f"| {x['source']} | {x['target']} |" for x in report['trigger_matrix'])
    crossings = '\n'.join(f"| {x['path']} | {x['method']} | {x['state']} |"
                          for x in report['cdc_rdc_inventory'])
    return f"""# CH05 conditional timing review

Regenerate with `python3 models/python/ch05_timing.py --write`; check with `--check`. Source: `specs/system/CH05_TIMING_SCENARIOS.json` (SHA-256 `{report['source_sha256']}`). All clocks, latency, ppm and IMU data are **assumed**. The [CH05 literature review](../literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md) was merged before this model.

## Clock tree and quantization

Concept: retained slow AON owns sleep continuity; fast capture exists only while awake. On wake, latch an AON epoch and restart fine relative time; an alternative continuous high-rate AON timer is compared, not selected. The [minimal SystemVerilog counter](../../rtl/timestamp/ch05_continuous_reference.sv) covers only this continuously clocked comparison. No SV simulator is available in this workspace; it is not an RTL verification result. No clock source, PLL, reset tree or silicon cell is approved.

| Synthetic domain | Period (µs) | Candidate ≤1 µs resolution while running |
|---|---:|---|
| AON | {ticks['aon']} | No; LF capture is coarse |
| Awake fine | {ticks['fine_awake']} | Tick only; inter-domain accuracy unproven |
| Continuous comparison | {ticks['continuous']} | Tick only; power/retention unproven |

Illustrative handoff, monotonic microseconds: awake {probe['awake_before']}, sleep {probe['sleep']}, awake after wake {probe['awake_after']}. Continuous comparator sleep read {probe['continuous_sleep']}. Coarse wake handoff uncertainty upper bound {probe['wake_handoff_uncertainty_us']} µs, excluding clock tolerance. The model clamps a late coarse snapshot to preserve monotonicity and can repeat labels; this does **not** prove 1 µs cross-mode accuracy. Counter width is 64 bits, while its unit and elapsed-gap half-range rule remain separate from physical reset/retention proof.

## Triggers, crossings and error accounting

Every entry in `trigger_matrix` maps one of LED, optical ADC, EEG/ECG, audio, electrochemical, IMU sync, GPIO or DMA to a target. Simultaneous arrivals keep configured source priority and a sequence number even when timestamps tie. Example ordering: {', '.join(x['source'] for x in report['simultaneous_events'])}. A trigger timestamp names its nominal sample aperture; source event time, captured edge, CDC latency and sensor aperture are separate values. **An event during sleep needs a wake-capable destination or retained queue; this is unproved.**

| Source | Conditional target |
|---|---|
{routes}

| Worst-case bound term | Awake (ns) | Sleep (ns; end-to-end path unavailable) |
|---|---:|---:|
| Next source edge | {active['capture_quantization_bound_ns']} | {sleep['capture_quantization_bound_ns']} |
| CDC destination phase | {active['cdc_phase_bound_ns']} | unavailable |
| CDC pipeline nominal | {active['cdc_pipeline_nominal_ns']} | unavailable |
| Sample aperture jitter | {active['sample_jitter_bound_ns']} | unavailable |
| Trigger→sample envelope including nominal latency | {active['sample_time_vs_event_bound_ns']} | unavailable |
| Host drift over assumed resync interval | {active['host_drift_bound_ns']} | {sleep['host_drift_bound_ns']} |

Bounds sum conservatively; trigger→sample envelope is **latency plus uncertainty**, not an accuracy guarantee or a measured jitter value. Host drift (hypothetical 20 ppm over 100 s) is 2,000,000 ns, distinct from the 100,000 ns example exchange uncertainty and capture phase. Clock PVT, metastability MTBF, calibration error, signal conditioning and analog sample aperture are not represented. A 2-flop CDC alone does not preserve repeated/short events. Each multi-bit crossing needs a coherent snapshot/acknowledgment or FIFO, and each reset release/clock transition needs future RDC/CDC and glitch checks.

| Crossing | Candidate handling / review needed | Status |
|---|---|---|
{crossings}

## IMU and gate

Example IMU anchor index 5, FIFO sample index 3 reconstructs sample aperture {report['imu_fifo_probe']['sample_ns']} ns with uncertainty {report['imu_fifo_probe']['uncertainty_bound_ns']} ns **before anchor-capture error**. The later FIFO read arrival {report['imu_fifo_probe']['read_arrival_us']} µs never substitutes for aperture time. Model requires known sync edge, sample index, sample period, pipeline delay and delay spread; actual part, FIFO conventions and orientation remain unresolved.

**Decision: MODEL_PASS / PHYSICAL_TIMING_HOLD.** No approved biomarker accuracy/retention/clock power, selected IMU, per-sensor latency, product clock/reset implementation, host exchange precision or physical CDC/RDC results. Do not freeze the timing tree, expose this invented trigger matrix as a software contract or begin CH06. See [CH05 gate](../reviews/CH05_GATE.md) and `docs/inputs/REQUIRED_INPUTS.md`.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = generate(json.loads(CONFIG.read_text()))
    js = json.dumps(report, indent=2, sort_keys=True) + '\n'
    md = render(report)
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REVIEW.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(js)
        REVIEW.write_text(md)
        print('CH05 synthetic timing reports written; physical gate HOLD')
    else:
        if REPORT.read_text() != js or REVIEW.read_text() != md:
            raise SystemExit('CH05 reports stale: run --write and review the diff')
        print('CH05 timing reports match synthetic source and model; physical gate HOLD')


if __name__ == '__main__':
    main()
