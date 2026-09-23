#!/usr/bin/env python3
"""CH02 scenario resource accounting. No electrical, battery or timing signoff."""

import argparse
import csv
import json
from collections import Counter
from fractions import Fraction
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / 'specs/system/CH02_MODE_ASSUMPTIONS.json'
RESULTS = ROOT / 'reports/subsystem/CH02_RESOURCE_SUMMARY.json'
REVIEW = ROOT / 'docs/budgets/CH02_CONCURRENCY_REVIEW.md'

BANKS = {
    'BIO': ('BIO_ADC_simultaneous', 'BIO-0001'),
    'EDA': ('EDA_receive_simultaneous', 'EDA-0001'),
    'ECH': ('ECH_receive_simultaneous', 'ECH-0001'),
    'OPT': ('OPT_ADC_simultaneous', 'OPT-0008'),
    'THM': ('THM_receive_simultaneous', 'THM-0001'),
    'AUDIO': ('AUDIO_ADC_simultaneous', 'AUD-0001'),
    'FAST': ('FAST_ADC_simultaneous', 'ADC-0005'),
    'IMU': ('IMU_external_streams', 'TIM-0007'),
}


def aggregate_contacts(config):
    scenarios = config['signal_contact_scenarios']
    return {key: sum(mapping.values()) for key, mapping in scenarios.items() if isinstance(mapping, dict)}


def evaluate(config):
    """Return deterministic quantitative scenario summaries and explicit unresolved dimensions."""
    streams = config['streams']
    capacities = config['capacities']
    fmt = config['format_assumptions']
    timestamp_bits = fmt['timestamp_bits_per_sample_group']
    quality_bits = fmt['quality_bits_per_channel_sample']
    wavelength_bits = fmt['optical_wavelength_id_bits_per_sample_group']
    guard = Fraction(str(fmt['host_link_guard_factor']))
    payload_efficiency = Fraction(str(fmt['illustrative_bus_payload_efficiency']))
    assert guard >= 1 and 0 < payload_efficiency <= 1
    assert all(isinstance(x, int) and x >= 0 for x in capacities.values())
    assert len(set(mode['id'] for mode in config['modes'])) == len(config['modes'])
    with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as handle:
        ids = {row['Req_ID'] for row in csv.DictReader(handle)}
    assert {'SYS-0010', 'HIF-0001', *(req for _, req in BANKS.values())} <= ids
    for name, stream in streams.items():
        assert stream['bank'] in BANKS, name
        assert all(isinstance(stream[key], int) and stream[key] > 0 for key in ('channels', 'simultaneous_channels', 'bits_per_channel', 'sample_rate_hz')), name
        assert stream['simultaneous_channels'] <= stream['channels'], name
        if stream['bank'] != 'IMU':
            assert stream.get('time_slots', 1) >= ceil(stream['channels'] / stream['simultaneous_channels']), name
        if stream['bank'] == 'OPT':
            assert stream['wavelength_phases'] > 0 and stream['sample_rate_hz'] % stream['wavelength_phases'] == 0, name
    contacts = aggregate_contacts(config)
    output = {'schema_version': 1, 'assumption_source': config['provenance'],
              'signal_contact_scenarios': contacts, 'modes': []}
    for mode in config['modes']:
        assert mode['class'] in ('candidate', 'stress')
        assert len(mode['streams']) == len(set(mode['streams'])), mode['id']
        assert set(mode['streams']) <= streams.keys(), mode['id']
        occupancy = Counter()
        ports = Counter()
        conversions_per_s = Counter()
        details = []
        raw = structured = sample_groups_per_s = 0
        for name in mode['streams']:
            s = streams[name]
            bank = s['bank']
            channels, rate = s['channels'], s['sample_rate_hz']
            occupancy[bank] += s['simultaneous_channels']
            ports[bank] += channels
            conversions_per_s[bank] += channels * rate
            raw_bits = channels * rate * s['bits_per_channel']
            framed_bits = raw_bits + quality_bits * channels * rate + timestamp_bits * rate
            if bank == 'OPT':
                framed_bits += wavelength_bits * rate
            raw += raw_bits
            structured += framed_bits
            sample_groups_per_s += rate
            details.append({'stream': name, 'bank': bank, 'channels': channels,
                            'simultaneous_channels': s['simultaneous_channels'],
                            'time_slots': s.get('time_slots', 1), 'sample_rate_hz_per_channel': rate,
                            'wavelength_phases': s.get('wavelength_phases'),
                            'sample_rate_hz_per_PD_per_wavelength': (rate // s['wavelength_phases'] if bank == 'OPT' else None),
                            'raw_bps': raw_bits, 'scenario_framed_bps': framed_bits})
        conflicts = []
        for bank, use in sorted(occupancy.items()):
            key, req = BANKS[bank]
            if use > capacities[key]:
                conflicts.append(f'{bank} simultaneous converters/receivers {use}>{capacities[key]} ({req})')
        if ports['OPT'] > capacities['OPT_input_ports']:
            conflicts.append(f"OPT input ports {ports['OPT']}>{capacities['OPT_input_ports']} (OPT-0007)")
        if mode['active_potentiostats'] > capacities['ECH_potentiostat_simultaneous']:
            conflicts.append('ECH potentiostats exceed four candidate paths (ECH-0002)')
        if mode['active_potentiostats'] > ports['ECH']:
            conflicts.append('Active potentiostats exceed selected electrochemical channels')
        if mode['led_active_max'] > capacities['LED_output_ports']:
            conflicts.append('LED enabled outputs exceed candidate ports (OPT-0001)')
        assert mode['led_active_max'] >= 0
        guarded = ceil(structured * guard)
        minimum_clock = ceil(Fraction(guarded, 1) / payload_efficiency)
        illustrative = next((clock for clock in fmt['illustrative_single_data_line_clocks_hz']
                             if Fraction(clock) * payload_efficiency >= guarded), None)
        requirements = sorted({'SYS-0010', 'HIF-0001', *(BANKS[streams[n]['bank']][1] for n in mode['streams']),
                               *(['OPT-0002'] if mode['led_active_max'] else []),
                               *(['AUD-0011'] if mode['audio_output'] else []),
                               *(['ECH-0002'] if mode['active_potentiostats'] else [])})
        assert set(requirements) <= ids
        output['modes'].append({
            'id': mode['id'], 'classification': mode['class'], 'source': mode['source'],
            'notes': mode['note'], 'streams': details, 'adc_occupancy': dict(sorted(occupancy.items())),
            'active_sensor_channels': dict(sorted(ports.items())),
            'required_conversions_per_s': dict(sorted(conversions_per_s.items())),
            'minimum_average_conversions_per_s_per_ADC': {
                bank: (conversions_per_s[bank] + capacities[BANKS[bank][0]] - 1) // capacities[BANKS[bank][0]]
                for bank in sorted(conversions_per_s) if bank != 'IMU'
            },
            'logical_acquisition_producers_min': len(details),
            'aggregate_sample_groups_per_s': sample_groups_per_s,
            'raw_payload_bps': raw, 'scenario_framed_bps': structured,
            'guarded_host_payload_bps': guarded,
            'minimum_illustrative_bus_clock_hz_at_assumed_efficiency': (minimum_clock if guarded else None),
            'first_illustrative_clock_meeting_guard_hz': (illustrative if guarded else None),
            'led_programmed_outputs_max': mode['led_active_max'],
            'led_output_current_ma_candidate_max': mode['led_active_max'] * capacities['LED_output_peak_ma_per_port_candidate'],
            'battery_peak_current_ma': None,
            'battery_peak_current_status': 'UNKNOWN: cell voltage, LED voltage, efficiencies, RF, audio and ASIC/IMU load not specified',
            'audio_output_active': mode['audio_output'], 'active_potentiostats': mode['active_potentiostats'],
            'radio': mode['radio'], 'storage': mode['storage'], 'bank_conflicts': conflicts,
            'requirements': requirements,
        })
    return output


def mbits(bits):
    return f'{bits / 1_000_000:.3f}'


def render(config, result):
    c = config['capacities']
    f = config['format_assumptions']
    totals = result['signal_contact_scenarios']
    lines = [
        '# CH02: Candidate mode concurrency and resource review', '',
        '**Status:** Scenario analysis only. Eight modes transcribed from `MASTER_SPEC.md` §37; sample rates, active channel counts, framing and interface efficiency are explicitly assumed in `specs/system/CH02_MODE_ASSUMPTIONS.json`. None is an approved product mode or verified electrical design.', '',
        '## Accounting rules', '',
        f'- Raw payload = Σ(channels × effective samples/s per channel × bits/sample). Per-channel rate is an **assumption**, including for scanned optics.',
        f'- Illustrative framed traffic = raw payload + {f["quality_bits_per_channel_sample"]} quality bits per channel sample + {f["timestamp_bits_per_sample_group"]} timestamp bits per stream sample group + {f["optical_wavelength_id_bits_per_sample_group"]} wavelength-ID bits per optical sample group. The audio per-sample timestamping is deliberately heavy; omitted CRC, dark/ambient cycles and packet details mean this is **not a guaranteed upper bound**. CH04 chooses real framing.',
        '- For optical streams, sample rate is **aggregate per photodiode over all programmed wavelengths**. Divide by `wavelength_phases` in the config to obtain the assumed per-PD, per-wavelength rate. More wavelengths at the same per-wavelength rate increase throughput proportionally.',
        f'- Guarded host payload = ceil({f["host_link_guard_factor"]} × conservative framed bound). This defines 20% capacity-over-demand headroom when the factor is 1.2; no bus or nRF rate is asserted.',
        '- `ADC occupancy` is the number required at the same instant, **not** a proof of converter maximum sample frequency, settling, calibration or analog noise. Scanned optical channels use multiple slots, so their samples are not all simultaneous.',
        '- `Logical acquisition producers` count independently queued stream groups. They are a minimum arbitration demand, not necessarily distinct hardware DMA channels; CH19 will allocate the actual DMA/FIFO scheme.',
        '- LED current is a programmed **output current** assuming selected output enable count. Battery current is explicitly unknown in every mode. CH03 supplies the voltage, efficiency, load and cell-sag model.', '',
        '## Candidate mode matrix and traffic', '',
        '| Mode | Status | Active streams | ADC occupancy | Raw Mb/s | Framed scenario Mb/s | Guarded host Mb/s | Producers | Groups/s | Candidate LED output peak | Bank conflict |',
        '|---|---|---|---|---:|---:|---:|---:|---:|---:|---|',
    ]
    for m in result['modes']:
        occupied = ', '.join(f'{bank}:{used}/{c[BANKS[bank][0]]}' for bank, used in m['adc_occupancy'].items()) or 'none'
        streams = ', '.join(s['stream'] for s in m['streams']) or 'AON only'
        lines.append(f'| `{m["id"]}` | {m["classification"]} | {streams} | {occupied} | {mbits(m["raw_payload_bps"])} | {mbits(m["scenario_framed_bps"])} | {mbits(m["guarded_host_payload_bps"])} | {m["logical_acquisition_producers_min"]} | {m["aggregate_sample_groups_per_s"]:,} | {m["led_output_current_ma_candidate_max"]} mA | {"; ".join(m["bank_conflicts"]) or "None at count level"} |')
    lines += ['', 'The `resource_conflict_probe` deliberately requests EEG8 + ECG2 on BIO8 and 12 simultaneous optical ADCs from a candidate bank of eight. It tests that both conflicts are reported. The optional `research_fast_stress` includes two 1 MSPS × 16-bit channels and is a stress probe, not a supported product mode.', '',
              '`Groups/s` sums independent stream sample-group clocks. It gives a worst-case unbatched event rate for arbitration discussion, not a DMA descriptor or interrupt requirement; FIFO batching is necessary for fast scenarios.', '',
              '### Per-mode assumptions and identified gaps', '']
    for m in result['modes']:
        clocks = m['first_illustrative_clock_meeting_guard_hz']
        if m['minimum_illustrative_bus_clock_hz_at_assumed_efficiency'] is None:
            clock_note = 'No acquisition stream; host data clock is not needed by this scenario.'
        else:
            label = f'{clocks/1e6:g} MHz' if clocks else '>64 MHz in illustrative set'
            clock_note = f'Minimum hypothetical single-data-line clock at {f["illustrative_bus_payload_efficiency"]:.0%} efficiency is {m["minimum_illustrative_bus_clock_hz_at_assumed_efficiency"]/1e6:.2f} MHz; first 8/16/32/64 MHz probe that passes is **{label}**. Actual capability is TBD.'
        lines.append(f'- **{m["id"]}:** {m["notes"].rstrip(".")}. {clock_note}')
    lines += ['', '## Channel capacity, optical scan and pin-contact bounds', '',
              f'- Candidate receive capacities: BIO {c["BIO_ADC_simultaneous"]}, EDA {c["EDA_receive_simultaneous"]}, ECH {c["ECH_receive_simultaneous"]} ({c["ECH_potentiostat_simultaneous"]} full potentiostats), OPT {c["OPT_input_ports"]} PD input ports but only {c["OPT_ADC_simultaneous"]} instantaneous ADC paths, THM {c["THM_receive_simultaneous"]}, AUDIO {c["AUDIO_ADC_simultaneous"]}, FAST {c["FAST_ADC_simultaneous"]}. These are candidates, not placed macros.',
              '- `opt12_scan_2000`: 12 physical PD inputs × 2000 aggregate samples/s = **24,000 conversions/s** across eight wavelength phases (250 samples/s/PD/wavelength) and two or more temporal PD slots. Eight ADC paths imply an *average* lower bound of 3000 conversions/s/ADC if balanced. Settling, dark frames and conversion headroom could require more; no claim of 12 simultaneous samples.',
              f'- Illustrative routed sensor-to-ASIC signal contacts: **{totals["optimistic_sensor_to_ASIC"]}** optimistic with shared electrochemical reference/counter and four single-ended thermal inputs; **{totals["less_shared_sensor_to_ASIC"]}** with independent electrochem references/counters and eight differential thermal inputs. A further **{totals["separate_internal_inter_die_logical_nets_optimistic"]}** logical inter-die nets cover an illustrative host/IMU/memory interface. These are net counts, **not package ball counts**. Power, ground, RF, test, clock, guard and extra return nets are excluded.',
              '- Fixed external capability contacts cannot be inferred from *mode concurrency*: a nonconcurrent sensor still occupies its connection unless a separately proven mux or co-packaged partition removes/moves that net. Shared dry electrodes can add leakage or cross-talk and require CH07/CH09/CH10 evidence.', '',
              '## Hard gaps before design choice', '',
              '1. **Product selection:** OI-001/OI-012 remain open; all eight modes are candidate examples. Confirm mandatory channel counts, their sample timing, intermittent windows, which streams must leave the ASIC, and whether multiwavelength samples need simultaneity.',
              '2. **Battery peak:** 150 mA per selected LED port is a candidate **load** current. One/two selected ports imply 150/300 mA candidate LED output; 16 unconstrained ports imply 2400 mA theoretical stress. These are not battery currents or duty-cycle averages. Hardware must bound concurrent enable, fault current and UV exposure independently of software; audio/RF peaks and cell data remain unknown (CH03, OI-003/OI-005).',
              '3. **ADC feasibility:** Count-level fits do not validate 4 kSPS BIO, 4 kSPS OPT, 1 kSPS ECH or 1 MSPS FAST at target noise/energy. ADC maximum effective conversion rate, mux settling and coexistence/spur budgets are TBD (CH07/CH16).',
              '4. **Host/backpressure:** The guarded host rates use the illustrative framing scenario during an active window. Exact SPI clock, CRC, headers, dark/ambient frames, FIFO, NAND busy windows, host wake, radio egress and loss policy remain unapproved (CH04/CH06/CH19). The 70% payload efficiency and candidate clocks are illustrative probes, never nRF specifications.',
              '5. **Physical pin feasibility:** SiP interconnect/pad and package pin budgets differ. Shared references and co-packaged transducers could move nets but require leakage, return path and manufacturability evidence (CH29/CH47).', '',
              '## Requirements and next gate', '',
              'Relevant IDs: `SYS-0010`, `BIO-0001`, `EDA-0001`, `ECH-0001`, `ECH-0002`, `OPT-0001`, `OPT-0007`, `OPT-0008`, `AUD-0001`, `ADC-0005`, `MEM-0001`, `HIF-0001`, `PMU-0010`, `PKG-0001`, `TIM-0001` and `SAFE-0002`. Per-mode ID lists are in the JSON report.',
              'CH02 passes when the mode matrix is regenerated, account rules and intentional conflicts are tested, and open inputs are recorded. **Architecture feasibility remains unproven.** CH03 next models battery energy and actual peak battery current without promoting scenario values to requirements.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true', help='regenerate committed report artifacts')
    group.add_argument('--check', action='store_true', help='check committed report artifacts are up to date')
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    result = evaluate(config)
    outputs = {
        RESULTS: json.dumps(result, indent=2, ensure_ascii=False) + '\n',
        REVIEW: render(config, result),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        print(f'Wrote {len(result["modes"])} modeled scenarios and CH02 review')
    elif args.check:
        for path, content in outputs.items():
            assert path.is_file() and path.read_text() == content, f'Stale report: {path}'
        print('CH02 reports match the configuration/model')
    else:
        print(render(config, result))


if __name__ == '__main__':
    main()
