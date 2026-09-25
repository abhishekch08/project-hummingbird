# CH03 gate: Conditional system power and energy accounting

Date: 2026-09-25 UTC. Review scope: executable **synthetic** model and integrity checks. Input is `specs/system/CH03_ENERGY_SCENARIOS.json`; calculation is `models/python/ch03_energy.py`; regenerated outputs are `reports/subsystem/CH03_ENERGY_SUMMARY.json` and `docs/budgets/CH03_ENERGY_REVIEW.md`. CH02 mode IDs provide labels for a mock rest/daily-health cycle, not a selected product duty schedule.

## Decision

| Gate | Decision | Evidence and exact boundary |
|---|---|---|
| CH03 numerical model | **MODEL_PASS** | Nine focused unit tests; deterministic reports and input hashes; correct high-voltage quadratic solution for a simple OCV/R source with direct-current and constant-power loads; no-solution/cutoff reporting; explicit startup intervals, conversion and quiescent accounting; charge and energy integration, mode grouping and step-size comparison. |
| Real cell and mandatory-mode feasibility | **FEASIBILITY_HOLD** | No measured OCV versus state of charge/temperature/age, pulse-duration-dependent impedance, usable capacity, current limit, actual emitter voltage, rail efficiency/load curves, mode priorities or hardware current/safety limits. The 8/10/14/20 mAh *labels* are scenario cases, not verified usable capacities. |
| Block architecture / safety signoff | **NOT RUN** | This model chooses no battery, PMIC topology or circuit. No §0.7 block literature gate, hazard signoff, PDK/EDA, silicon or medical/clinical validation has occurred. |

The synthetic mock cycle has a short coincident LED and RF interval. Under **invented** OCV, resistance, forward voltage, efficiency and schedule assumptions, the requested battery peak is about 147 mA; its output LED current is the CH02 candidate 150 mA at a synthetic 2.0 V rail. The numbers differ because `Pout = Vout × Iout` is converted through efficiency, and `Pbat = Vterm × Ibat` includes all simultaneous loads and cell sag. No direction or ratio of battery current to LED current can be generalized from this example. The case table and test-only sensitivities are in the CH03 budget review, visibly labeled synthetic.

## What was tested

- Synthetic required metadata, unit/range/evidence checks, source linkage, CH02 mode/LED compatibility and enabled-rail completeness.
- Known quadratic root (`Voc = 4 V`, `R = 1 Ω`, `P = 3 W` gives `Vterm = 3 V`, `Ibat = 1 A`), direct-load power identity, no-solution and cutoff cases.
- Rail output versus battery input power, quiescent-current inclusion exactly once, overlapping LED/RF load, startup energy over its duration, lifetime energy allocation and charge/energy balance.
- Four capacity labels; parameter sensitivities for cell resistance, available charge, conversion efficiency and optical duty; analytic constant-current/zero-resistance case; missing physical inputs fail closed. Half-step and default integration differ by less than one mock cycle.

Reproduce from a clean clone:

```sh
python3 models/python/ch03_energy.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch03_*.py'
python3 scripts/verification/check_all.py
git diff --check
```

## Physics not established by these checks

The simple source is `Vterm = Voc(z) − Ibat R`. One fixed resistance lacks polarization, relaxation and temperature/time dependence; a 10 ms current pulse cannot be validated with it. The duty cycle, rail states and startup terms are synthetic. Integration uses interval endpoints; the half-step test bounds *numerical* sensitivity of this fixture, not cell/model uncertainty. If a requested constant-power load has no stable high-voltage solution, violates the illustrative cutoff, or would exceed a future **measured** pulse-current limit, the mode must be rejected or altered through a reviewed product/safety decision. Never clip away a failing pulse or silently promote it to a product mode.

## Traceability and unresolved evidence

| Requirement IDs | Evidence created | Remaining physical/product gate |
|---|---|---|
| `PMU-0001`, `PMU-0010` | Four charge-capacity labels, explicit OCV/R/cutoff and sensitivity machinery | Cell chemistry, measured available charge versus load/temperature/age, transient sag and mode duty; no runtime acceptance |
| `PMU-0009`, `PMU-0014` | Block-state inventory; synthetic active/idle/startup accounting and zero-load case | All implemented domains' measured active/idle/retention/off/startup/leakage, storage shelf-life and transition conditions |
| `SYS-0010`, `OPT-0002`, `AUD-0011` | Coincident optical/RF exercise, efficiency/duty sensitivities and explicit unmodeled CH02 modes | Owner-approved simultaneous modes, actual LED/audio and RF waveforms, supply losses and thermal limit |
| `SAFE-0002` | Missing safety/current-limit fields cause a feasibility HOLD | Independently defined and enforced hardware drive/exposure/temperature limits and fault review |

The register's requirement maturity statuses remain provisional and its artifact-path columns remain *planned destinations*. This gate links actual CH03 evidence without falsely upgrading `PMU-0010` or `SAFE-0002` to a validated product requirement. OI-001/003/005/009/015 and R-005 remain open. Sourced cell curves, measured load/efficiency waveforms and owner-approved schedules are needed before revisiting a physical runtime or peak-current verdict.

**Stop point:** CH03 model gate complete. CH04 is the next planned chunk and is paused until requested. Block topology selection still requires a block-specific literature survey and quantitative trade study.
