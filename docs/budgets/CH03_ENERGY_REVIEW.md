# CH03: Synthetic battery-energy and peak-current accounting

**Evidence class:** SYNTHETIC_CONDITIONAL. The cell, efficiency, duty cycle and nearly all loads are invented mathematical inputs. The 150 mA LED value is a CH02 candidate *output* target, not a measured battery current or safe operating limit. No product mode, runtime, cold performance or charge limit is approved.

Input SHA-256: `2f7163e18aa73d7ff1e0266bb0c7419651700d62893f321f9af701c1d2edd12b`; CH02 SHA-256: `c3043a250688a9e7a7901a26cc1956137250e86269150284ed6ae9053b688e67`. Regenerate with `python3 models/python/ch03_energy.py --write`; check with `--check`.

## First-principles accounting

- Per enabled rail: battery-equivalent constant power is `Vout × Iout / η`; quiescent current is added once at the battery input. Direct battery loads and coincident RF/optical loads are summed at the same instant. Battery energy is integrated as `∫ Vterm × Ibat dt`, separately from charge `∫ Ibat dt`. mAh alone is not energy.
- The illustrative cell uses a linear open-circuit-voltage-versus-charge line and one fixed series resistance. The high-voltage root of `Vterm = Voc − R × (Idirect + Iq + Pconstant/Vterm)` is used; no real chemistry, transient impedance, recovery or battery pulse-current limit is supplied.
- CH02 mode IDs label a synthetic one-second rest/sense/optical collision cycle. This is **not** a 24-hour wear schedule. Every other CH02 mode lacks a power-state and product-duty map. Startup energy is applied over a stated event window; shorter unmeasured transients could create a higher peak.

## Four capacity labels in the synthetic cycle

| Label | Approximate synthetic runtime | Stop reason | Peak requested battery current | Minimum delivered terminal voltage | Battery energy |
|---:|---:|---|---:|---:|---:|
| 8 mAh | 4.722 h | CHARGE_EXHAUSTED | 147.20 mA | 3.006 V | 27.569 mWh |
| 10 mAh | 5.902 h | CHARGE_EXHAUSTED | 147.20 mA | 3.006 V | 34.461 mWh |
| 14 mAh | 8.263 h | CHARGE_EXHAUSTED | 147.20 mA | 3.006 V | 48.245 mWh |
| 20 mAh | 11.804 h | CHARGE_EXHAUSTED | 147.20 mA | 3.006 V | 68.922 mWh |

These are illustrative charge-capacity **labels** with synthetic OCV, resistance and load data. A `VOLTAGE_CUTOFF` result rejects a requested load after the listed approximate elapsed time. The interval solver checks operating conditions at each segment start, with at most 0.89 s between checks here. This is **not** a guaranteed bound on numerical error or a measured cell runtime.

## Sensitivity at the 10 mAh label

| Input change (invented) | Conditional runtime | Peak requested current | Stop reason |
|---|---:|---:|---|
| baseline | 5.902 h | 147.20 mA | CHARGE_EXHAUSTED |
| higher_cell_resistance: ×2 | 3.374 h | 147.47 mA | VOLTAGE_CUTOFF |
| lower_available_charge: ×0.7 | 4.132 h | 147.20 mA | CHARGE_EXHAUSTED |
| lower_conversion_efficiency: ×0.8 | 4.248 h | 184.32 mA | VOLTAGE_CUTOFF |
| double_optical_duty: ×2 | 3.333 h | 147.20 mA | CHARGE_EXHAUSTED |

Half-step integration changes the 10 mAh approximate runtime by 0.000457 s, within the chosen 1.000 s numerical regression tolerance. Energy is separately allocated to rail output, conversion loss, direct/quiescent draw and startup. The largest rounded energy-balance residual across base cases is 5.2e-11 mWh.

## Mode and per-block state coverage

The generated JSON records the three synthetic cycle segments at 100%, 50% and 10% assumed state of charge, with battery current and terminal voltage *at each segment*; it also records lifetime energy by referenced CH02 mode. These snapshots are static-equivalent traces, not measured pulse waveforms. Unmodeled CH02 modes: `audio`, `cardiovascular`, `optical_spectroscopy`, `research_fast_stress`, `research_raw`, `resource_conflict_probe`, `sleep_neuroscience`, `sweat_biochemistry`.

| Physical state inventory | Source condition | Active / idle / retention / off / startup evidence |
|---|---|---|
| `aon` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `audio_input` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `audio_output` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `bio` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `compute` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `eda_bioz` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `electrochemical` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `host_rf` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `imu` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `memory` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `optical_led` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `optical_rx` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `pmic` | Unselected hardware and mode | All missing; synthetic subset does not close this row |
| `thermal` | Unselected hardware and mode | All missing; synthetic subset does not close this row |

## Gate and blockers

**MODEL_PASS** for reproducible, internally consistent synthetic accounting and fault reporting. **FEASIBILITY_HOLD** for any battery, runtime, safety or architecture claim: the physical fields remain missing and must be reviewed independently, even if populated later. In particular, fixed resistance cannot prove whether a 10 ms LED/RF pulse is safe for a small cell. No numeric battery current limit is asserted.

Missing source inputs: `emitter_forward_voltage_and_pulse_waveform`; `independent_safety_and_thermal_limits`; `measured_block_state_and_startup_loads`; `measured_rail_efficiency_vs_input_load_temperature`; `product_mode_priorities_and_duty_schedule`; `representative_cell_impedance_vs_soc_temperature_age_pulse_duration`; `representative_cell_ocv_vs_soc_temperature_age`; `usable_capacity_vs_load_temperature_age`; `validated_cell_pulse_current_limit`.

No technical block topology was selected; the §0.7 literature gate remains pending for subsequent block design. See `docs/reviews/CH03_GATE.md` for verification commands and decision boundaries.
