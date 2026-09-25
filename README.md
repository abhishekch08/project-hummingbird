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
| CH05 timebase/synchronization | Literature gate merged; synthetic clock/trigger/IMU model and 18 tests PASS; **physical timing HOLD** | [Gate](docs/reviews/CH05_GATE.md) · [Survey](docs/literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md) · [Report](docs/budgets/CH05_TIMING_REVIEW.md) |
| CH06 host protocol | Literature gate merged; candidate register/packet model and 23 tests PASS; **physical link/ABI HOLD** | [Gate](docs/reviews/CH06_GATE.md) · [Contract](docs/interfaces/CH06_REGISTER_PROTOCOL.md) · [Survey](docs/literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md) |
| First technical block design (CH07) | **Not started**; requires prior system gates and a committed block literature review | [Chunk plan](MASTER_SPEC.md#42-development-chunks) |

CH06's candidate model follows its separately merged entry survey. Battery, data/memory, timing and protocol numbers are conditional models; measured cell/link/storage/clock/sensor data and approved product schedules remain missing. CH05 includes a minimal **uncompiled** SystemVerilog counter reference for one continuous-clock comparison, not complete timing RTL or CDC. No verified circuit, ASIC layout, foundry mapping, clinical validation or tapeout signoff exists.

## Start or resume

1. Read [project state](state/PROJECT_STATE.md), [chunk status](state/CHUNK_STATUS.csv), [open issues](state/OPEN_ISSUES.md), [assumptions](state/ASSUMPTIONS.md) and the relevant chunk file.
2. Confirm the working tree and current `main` with `git status` and `git fetch origin main`.
3. For the **next authorized chunk**, define scope, source evidence and acceptance; run its checks; update traceability/state; commit and publish. Block design requires the [literature-first gate](MASTER_SPEC.md#07-mandatory-literature-first-design-gate).
4. Run the public checks from a fresh checkout:

   ```sh
   python3 scripts/verification/check_all.py
   ```

   These checks validate repository consistency, CH02 accounting and conditional CH03–CH06 models. They do not establish electrical, battery, real link, storage, physical timing or medical performance.

## Find things

- [Documentation index and repository map](docs/README.md)
- [Master specification and CH00–CH50 program](MASTER_SPEC.md)
- [Assumption-backed CH02 model](specs/system/CH02_MODE_ASSUMPTIONS.json) · [Executable model](models/python/ch02_concurrency.py)
- [CH03 synthetic input set](specs/system/CH03_ENERGY_SCENARIOS.json) · [Conditional energy report](docs/budgets/CH03_ENERGY_REVIEW.md)
- [CH04 synthetic dataflow input](specs/system/CH04_DATAFLOW_SCENARIOS.json) · [Conditional memory report](docs/budgets/CH04_DATA_MEMORY_REVIEW.md)
- [CH05 synthetic timing input](specs/system/CH05_TIMING_SCENARIOS.json) · [Conditional timing report](docs/budgets/CH05_TIMING_REVIEW.md) · [Timestamp SV reference](rtl/timestamp/ch05_continuous_reference.sv)
- [CH06 candidate contract input](specs/system/CH06_HOST_CONTRACT.json) · [Generated register/host protocol](docs/interfaces/CH06_REGISTER_PROTOCOL.md) · [Executable model](models/python/ch06_host.py)
- [Decision log](state/DECISIONS.md) · [Risk register](state/RISK_REGISTER.md) · [Verification status](state/VERIFICATION_STATUS.md)
- [Future-stage directory rules](docs/REPOSITORY_MAP.md) · [Documentation and data policy](docs/governance/DATA_POLICY.md)

## Repository status

This is a public repository. A project license has **not** been selected; see [licensing status](docs/governance/LICENSE_STATUS.md). Do not upload restricted IP, unlicensed papers, keys, or personal physiological recordings. Many folders are reserved for later engineering chunks and intentionally contain no design files.
