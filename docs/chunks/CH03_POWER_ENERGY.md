# CH03: System power, energy and peak-current feasibility

Status: **synthetic model complete and numerically checked; physical battery feasibility HOLD**. Date: 2026-09-25. CH02's scenario gate is complete; product modes, measured battery runtime and peak safety are not approved.

## Goal and scope

Build an executable, unit-aware model that maps **time-aligned block/rail states** to battery charge draw, terminal voltage, peak current, lost power, startup energy and conditional runtime. Evaluate the master spec's 8/10/14/20 mAh *capacity sensitivity cases* separately. Use CH02 mode combinations only as candidate active-window scenarios. A daily or sleep duty schedule needs an explicitly supplied product assumption; an active-window payload or LED current cannot be treated as a 24-hour average.

First answer whether the proposed calculations are self-consistent. Only then assess physical feasibility using sourced cell and component data under matching temperature, age, duration and load. Produce a clearly labeled `MODEL_PASS`/`FEASIBILITY_HOLD` if external data remain absent, even when all numerical tests pass.

## Boundaries

- Do not choose chemistry, rail topology, PMIC die, clock/power architecture, product mode or regulator efficiency from a hypothetical scenario. CH22–CH24 own power architecture and later implementation.
- Do not substitute 150 mA **LED output** from CH02 for battery current. Emitter voltage, enabled outputs, converter input voltage/efficiency, other coincident loads and cell impedance determine battery demand. The 16-output fault probe is a hazard stress case, not a supported mode.
- No safety, medical, UV exposure or runtime claim passes from a Python simulation alone. Do not add files to reserved circuit, RTL or physical-design folders during this system feasibility chunk.

## Requirements and dependencies

Trace `PMU-0001`, `PMU-0009`, `PMU-0010`, `PMU-0014`, `SYS-0010`, `OPT-0002`, `AUD-0011` and `SAFE-0002`; resolve or retain OI-001/003/005/009/015. Inputs are `MASTER_SPEC.md` §42, the CH02 mode config/report, `state/ASSUMPTIONS.md`, and `docs/inputs/REQUIRED_INPUTS.md`. A circuit/block topology still requires the separate §0.7 literature and quantitative trade-study gate. CH03 can start as system accounting with unknowns made explicit; it is not a block architecture decision.

| Parameter group | Required units and meaning | Current evidence |
|---|---|---|
| Cell | Open-circuit voltage versus state of charge/temperature/age; load-duration-dependent impedance or bounded equivalent; cutoff, current limit and *usable* charge versus conditions | Missing representative cell curves; 8/10/14/20 mAh are labeled cases, not measured usable capacity |
| Rails and loads | Per-rail output voltage and per-block current in active/idle/retention/off; regulator efficiency versus input/output/load/temperature and quiescent draw | Missing; no vendor-typical number promoted to a design limit |
| Events | LED forward voltage and pulse waveform, radio/audio/storage activity, wake startup energy and duration, overlapping events and software-controlled enable schedule | CH02 has only selected LED **output-current** scenarios; other waveforms/duty factors missing |
| Environment and product | Mandatory mode set, recording/transmission schedule, temperature, age and reserve policy | Unapproved product decisions and missing measurements |

Each value in an executable input must carry unit, evidence class (`assumed`, `vendor`, or `measured`), source/conditions and uncertainty or range. Unknown mandatory fields must stay null/absent and prevent an absolute runtime verdict; an optional illustrative input set may yield only *conditional* numbers.

## Calculation contract

1. For output rail `j`, use `P_out,j(t) = V_out,j(t) × I_out,j(t)`. If converter efficiency **includes** its quiescent draw, `P_in,j(t) = P_out,j(t) / η_j(V_b, I_out,j, T)`; otherwise add quiescent input current exactly once. Sum coincident loads and direct battery currents at the same instant. State time and charge in SI units internally. Never add rail output current directly to battery input current.
2. For an explicitly justified simple cell sensitivity, `V_term = V_OC(z,T,age) − I_b R_eff(z,T,age,pulse duration)`, with `P_b = V_term × I_b`. Solve the battery current and terminal voltage consistently. If a constant-power-only interval uses constant `V_OC` and `R`, the lower-current quadratic root exists only if `V_OC² ≥ 4 R P_b`; any missing root, voltage below cutoff or exceeded validated pulse limit is a **failed scenario**, not a negative runtime or a silently clipped voltage. More detailed measured dynamic cell behavior can replace the simple equivalent when available.
3. Integrate `dQ/dt = −I_b(t)` across the time-aligned schedule, including startup events and inactive-state leakage, until the selected cell's validated cutoff or an explicit limit. Capacity in mAh is charge, not energy; `capacity × nominal voltage` is not a sufficient runtime model when voltage, sag and efficiency change. Report energy from an independent `∫ V_term I_b dt` calculation as a cross-check, without subtracting conversion losses twice.
4. Treat mutually exclusive product modes with a duty-sum of one; model overlapping sources as simultaneous currents. Resolve temporal detail and run a step-size/convergence check for short LED/RF/audio pulses, stating where the equivalent cell model is too simple to bound real transients.
5. Sweep capacity cases, temperature/age, cell impedance, rail efficiency and activity assumptions only within *declared* ranges. Identify which inputs dominate energy and peak-voltage failure; distinguish a conditional result from a vendor/bench-backed pass.

## Planned outputs and acceptance

| Artifact | Purpose |
|---|---|
| `specs/system/CH03_ENERGY_SCENARIOS.json` | Versioned input schema and explicit candidate schedule(s), source conditions and unknown fields |
| `models/python/ch03_energy.py` | Deterministic standard-library calculation with units and unambiguous failure states |
| `verification/unit/test_ch03_energy.py` | Analytic constant-current/zero-resistance check, power/charge conservation, conversion loss, coincident peaks, cutoff and missing-input cases |
| `reports/subsystem/CH03_ENERGY_SUMMARY.json` and `docs/budgets/CH03_ENERGY_REVIEW.md` | Regenerable scenario output, uncertainty and ranked feasibility blockers |
| `state/` and `docs/reviews/CH03_GATE.md` | Updated assumptions, issues, traceability, risk and limited gate result |

Acceptance requires: exact input provenance; reproducible outputs; tests that fail on incorrect unit conversion, energy/current double counting, underestimated coincident peaks and invalid/incomplete cell data; separate current/voltage traces and runtime by case; sensitivity to unknowns; explicit conditions for every pass/fail. A model-only PASS does **not** close OI-003/009/015. A real architecture/runtime PASS additionally requires representative cell and load measurements and owner-approved mandatory mode schedules. Stop before CH04 and before a PMIC topology or circuit decision.

## Results and stop point

The source input, model, nine focused tests and generated machine/human reports exist at the paths above. `docs/reviews/CH03_GATE.md` records MODEL_PASS for conditional arithmetic and FEASIBILITY_HOLD for physical battery, mandatory modes, peak limit and safety. The synthetic one-second cycle is a test fixture, **not** a daily/sleep product schedule. The missing evidence queue remains in `docs/inputs/REQUIRED_INPUTS.md`; OI-001/003/005/009/015 stay open. `python3 scripts/verification/check_all.py` reproduces both CH02 and CH03 public gates. Stop at CH03; CH04 requires a separate kickoff.
