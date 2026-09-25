# Documentation index

## Orientation and current evidence

| Read | Purpose |
|---|---|
| [MASTER_SPEC.md](../MASTER_SPEC.md) | Candidate functions, constraints, source sections and CH00–CH50 gates. Sections 49–50 are historical bootstrap recipes. |
| [PROJECT_STATE.md](../state/PROJECT_STATE.md) and [CHUNK_STATUS.csv](../state/CHUNK_STATUS.csv) | Current gate, pause point, next authorized unit, and status of all planned chunks. |
| [REQUIREMENTS_TRACEABILITY.csv](../state/REQUIREMENTS_TRACEABILITY.csv) | Provisional 223 IDs, proposed checks, source sections and linked issues. |
| [ASSUMPTIONS.md](../state/ASSUMPTIONS.md) | Numeric and product unknowns that must stay separate from frozen requirements. |
| [VERIFICATION_STATUS.md](../state/VERIFICATION_STATUS.md) | What the available checks actually establish. |
| [DECISIONS.md](../state/DECISIONS.md), [OPEN_ISSUES.md](../state/OPEN_ISSUES.md), [RISK_REGISTER.md](../state/RISK_REGISTER.md) | Chosen policies, unresolved decisions and risk/evidence owners. |

## Reviews and next work

- [CH01 requirements review](reviews/CH01_REQUIREMENTS_REVIEW.md) and [CH02 resource gate](reviews/CH02_GATE.md).
- [CH01 chunk record](chunks/CH01_REQUIREMENTS.md), [CH02 chunk record](chunks/CH02_CONCURRENT_MODES.md), and [chunk template](chunks/CH_TEMPLATE.md).
- [CH03 chunk record](chunks/CH03_POWER_ENERGY.md) and [CH03 model gate](reviews/CH03_GATE.md): synthetic model PASS; physical battery feasibility HOLD.
- [CH04 chunk record](chunks/CH04_DATA_MEMORY.md) and [CH04 model gate](reviews/CH04_GATE.md): conditional data/queue/storage arithmetic PASS; physical link and memory feasibility HOLD.
- [CH05 chunk record](chunks/CH05_CLOCK_TIMING.md), [primary-source timing survey](literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md), [ADR-0002 alternatives](adr/ADR-0002_CONDITIONAL_TIMEBASE.md) and [CH05 model gate](reviews/CH05_GATE.md): model PASS; physical clock/CDC/RTL HOLD.
- [CH06 entry charter](chunks/CH06_REGISTER_HOST.md) and [primary host/register survey](literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md): candidate model PASS, physical host/ASIC ABI held. [ADR-0003](adr/ADR-0003_CANDIDATE_HOST_CONTRACT.md), [generated contract](interfaces/CH06_REGISTER_PROTOCOL.md), [CH06 model gate](reviews/CH06_GATE.md).
- [CH07 entry charter](chunks/CH07_BIOPOTENTIAL_NUMERICAL.md) and [dated electrode/AFE primary survey](literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md): source survey and model PASS, topology/block spec paused. [Conditional numerical report](budgets/CH07_BIOPOTENTIAL_REVIEW.md) and [gate](reviews/CH07_GATE.md).
- [CH08–CH50 entry and evidence audit](reviews/CH08_CH50_ENTRY_AUDIT.md): prerequisites and current blockers for the remaining sequence; all NOT_RUN.
- [CH02 numerical report](budgets/CH02_CONCURRENCY_REVIEW.md) and [exact input assumptions](../specs/system/CH02_MODE_ASSUMPTIONS.json).
- [CH03 conditional energy report](budgets/CH03_ENERGY_REVIEW.md), [scenario input](../specs/system/CH03_ENERGY_SCENARIOS.json), and [machine summary](../reports/subsystem/CH03_ENERGY_SUMMARY.json).
- [CH04 conditional data/memory report](budgets/CH04_DATA_MEMORY_REVIEW.md), [scenario input](../specs/system/CH04_DATAFLOW_SCENARIOS.json), and [machine summary](../reports/subsystem/CH04_DATAFLOW_SUMMARY.json).
- [CH05 conditional timing report](budgets/CH05_TIMING_REVIEW.md), [scenario input](../specs/system/CH05_TIMING_SCENARIOS.json), [machine summary](../reports/subsystem/CH05_TIMING_SUMMARY.json), and [limited SV reference](../rtl/timestamp/ch05_continuous_reference.sv).
- [CH06 host/register model](../models/python/ch06_host.py), [candidate input](../specs/system/CH06_HOST_CONTRACT.json), and [machine summary](../reports/subsystem/CH06_HOST_SUMMARY.json).
- [CH07 numerical model](../models/python/ch07_biopotential.py), [synthetic input](../specs/biosignal/CH07_NUMERICAL_SCENARIOS.json), and [machine summary](../reports/block/CH07_NUMERICAL_SUMMARY.json).
- [Requested external inputs for unresolved gates](inputs/REQUIRED_INPUTS.md).
- [Safety evidence status](safety/README.md) and [package evidence status](package/README.md).
- [Literature review gate and template](literature/README.md) and [ADR template](adr/ADR_TEMPLATE.md).
- [Repository ownership map](REPOSITORY_MAP.md), [data rules](governance/DATA_POLICY.md), and [licensing status](governance/LICENSE_STATUS.md).

## Evidence labels

**Scenario/model** means arithmetic conditional on inputs. **Simulation** means a documented model or circuit run. **Measurement** means calibrated physical evidence under stated conditions. **Signoff** means independent accepted review at the required gate. At present the repository has scenario calculations and repository checks; it has no representative battery/link/storage/clock measurement, compiled RTL, circuit simulation, project silicon or signoff data. The published literature includes measurements from other devices that cannot substitute for project evidence.
