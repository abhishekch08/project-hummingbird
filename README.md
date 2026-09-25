# Project Hummingbird

Version-controlled research program for a compact heterogeneous physiological-computing ASIC/SiP for a head-worn wearable. The [master specification](MASTER_SPEC.md) is a **candidate engineering plan**. Channel counts, package size, performance numbers, chip partition and biomarker capabilities are not verified or approved product specifications.

## Current baseline

| Milestone | State | Evidence |
|---|---|---|
| CH00 repository scaffold | Complete, structure checked | [Project state](state/PROJECT_STATE.md) |
| CH01 requirements normalization | Provisional 223-ID register; no electrical targets frozen | [Register](state/REQUIREMENTS_TRACEABILITY.csv) · [Review](docs/reviews/CH01_REQUIREMENTS_REVIEW.md) |
| CH02 concurrent-mode scenarios | Eight candidate modes and two stress probes; arithmetic validated | [Review](docs/reviews/CH02_GATE.md) · [Mode report](docs/budgets/CH02_CONCURRENCY_REVIEW.md) |
| CH03 battery/energy feasibility | Synthetic model and nine tests PASS; **physical feasibility HOLD** | [Gate](docs/reviews/CH03_GATE.md) · [Model](models/python/ch03_energy.py) · [Inputs](docs/inputs/REQUIRED_INPUTS.md) |
| CH04 data/memory feasibility | Synthetic packet/queue/storage model and 12 tests PASS; **physical feasibility HOLD** | [Gate](docs/reviews/CH04_GATE.md) · [Model](models/python/ch04_dataflow.py) · [Report](docs/budgets/CH04_DATA_MEMORY_REVIEW.md) |
| CH05 timebase/synchronization | **Not started**; wait for user instruction | [Chunk plan](MASTER_SPEC.md#42-development-chunks) |
| First technical block design (CH07) | **Not started**; requires prior system gates and a committed block literature review | [Chunk plan](MASTER_SPEC.md#42-development-chunks) |

The project is paused after the CH04 **model** gate. Battery and data/memory numbers are conditional arithmetic; measured cell/link/storage data and approved product schedules remain missing. No circuit, RTL, ASIC layout, foundry mapping, clinical validation or tapeout signoff exists.

## Start or resume

1. Read [project state](state/PROJECT_STATE.md), [chunk status](state/CHUNK_STATUS.csv), [open issues](state/OPEN_ISSUES.md), [assumptions](state/ASSUMPTIONS.md) and the relevant chunk file.
2. Confirm the working tree and current `main` with `git status` and `git fetch origin main`.
3. For the **next authorized chunk**, define scope, source evidence and acceptance; run its checks; update traceability/state; commit and publish. Block design requires the [literature-first gate](MASTER_SPEC.md#07-mandatory-literature-first-design-gate).
4. Run the public checks from a fresh checkout:

   ```sh
   python3 scripts/verification/check_all.py
   ```

   These checks validate repository consistency, CH02 accounting and conditional CH03–CH04 arithmetic. They do not establish electrical, battery, real link, storage or medical performance.

## Find things

- [Documentation index and repository map](docs/README.md)
- [Master specification and CH00–CH50 program](MASTER_SPEC.md)
- [Assumption-backed CH02 model](specs/system/CH02_MODE_ASSUMPTIONS.json) · [Executable model](models/python/ch02_concurrency.py)
- [CH03 synthetic input set](specs/system/CH03_ENERGY_SCENARIOS.json) · [Conditional energy report](docs/budgets/CH03_ENERGY_REVIEW.md)
- [CH04 synthetic dataflow input](specs/system/CH04_DATAFLOW_SCENARIOS.json) · [Conditional memory report](docs/budgets/CH04_DATA_MEMORY_REVIEW.md)
- [Decision log](state/DECISIONS.md) · [Risk register](state/RISK_REGISTER.md) · [Verification status](state/VERIFICATION_STATUS.md)
- [Future-stage directory rules](docs/REPOSITORY_MAP.md) · [Documentation and data policy](docs/governance/DATA_POLICY.md)

## Repository status

This is a public repository. A project license has **not** been selected; see [licensing status](docs/governance/LICENSE_STATUS.md). Do not upload restricted IP, unlicensed papers, keys, or personal physiological recordings. Many folders are reserved for later engineering chunks and intentionally contain no design files.
