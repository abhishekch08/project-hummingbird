# Current Baseline

Architecture version: unselected; provisional requirements, CH02 scenarios, conditional CH03 energy, CH04 dataflow, CH05 timing and CH06 candidate host models only.
Canonical branch: `main`; read `git rev-parse HEAD` for the current commit after fetching.
Previous reviewed baseline: `124ef7843b7b71464c618b7cb256368b5e53500c` (CH06 literature/entry PR #9 merged before any host model).
Current chunk: CH07 next under user authorization for subsequent chapters. CH00–CH06 complete at limited gates; CH06 review is in the current candidate-contract publication.
CH07 is active at its entry charter and dated biopotential source review after CH06 PR #10 merged; the user has already authorized continuation.
Current subchunk: CH07 entry charter and dated biopotential primary-source survey before numerical design. CH05 timing and CH06 physical host ABI remain HOLD.
Current status: no product mode, battery runtime, host/BLE throughput, SRAM/NAND selection, pulse safety limit, electrical/timing target, chip architecture or tapeout claim approved.

# Passed Gates

- CH00: tracked scaffold and structural check; no silicon evidence.
- CH01: provisional 223-ID requirements register and consistency review, merged as PR #1.
- CH02: eight candidate modes and two stress probes with resource arithmetic and seven unit tests, merged as PR #2; see `docs/reviews/CH02_GATE.md`.
- CH03: conditional energy/sag/loss/peak-current arithmetic and nine focused tests, MODEL_PASS; measured battery/product/safety FEASIBILITY_HOLD in `docs/reviews/CH03_GATE.md`.
- CH04: CH02 raw-rate reconciliation, conditional packet/queue/SRAM/NAND arithmetic and 12 focused tests, MODEL_PASS; physical host/BLE/storage/product FEASIBILITY_HOLD in `docs/reviews/CH04_GATE.md`.
- CH05: primary timing survey/quantitative comparison merged as PR #7 before architecture work; conditional clock/trigger/drift/IMU model and 18 focused tests, MODEL_PASS; physical timing and uncompiled RTL HOLD in `docs/reviews/CH05_GATE.md`.
- CH06: host/register primary survey merged as PR #9 before candidate contract; 23 tests and CH04 rate reconciliation, MODEL_PASS; frozen host/ASIC ABI and physical SPI/DMA HOLD in `docs/reviews/CH06_GATE.md`.

# Active Work

- CH07 biopotential numerical entry is active; its own dated literature review and acceptance plan are being committed before numerical design. CH05's small SV reference is uncompiled and does not select a timebase. CH07 physical circuit design has not begun.
- `state/CHUNK_STATUS.csv` records the complete CH00–CH50 queue; folders marked reserved in `docs/REPOSITORY_MAP.md` are not completed deliverables.

# Blocked Items

- Product priorities/concurrency, measured cell voltage/impedance/pulse limit and capacity, real rail/load/duty data, optical source radiometry, actual host/BLE link and memory throughput/endurance, SRAM implementation, approved cross-sensor timing/error limits, qualified clocks/IMU and CDC/RDC, pinout/package rules and foundry/IP availability. See `state/OPEN_ISSUES.md` and `docs/inputs/REQUIRED_INPUTS.md`.
- Architecture and tapeout gates remain blocked by missing external evidence and by the later design/review sequence in `MASTER_SPEC.md`.

# Next Exact Action

- Publish CH07 entry charter and dated source comparison independently. Then build/test a conditional numerical noise/offset/headroom/ADC model; hold a selected topology until electrode and product quality targets are owner approved. Do not promote CH03–CH06's synthetic outputs to product targets.

# Required Inputs

- CH03 physical gate still requires representative cell chemistry/OCV/impedance/usable capacity across load, temperature and age; LED/rail/load waveforms and converter efficiency; validated pulse limit and owner-approved mode schedule. CH04 physical gate additionally requires approved stream/framing/feature policies, measured host and BLE goodput/wake traces, write/erase stalls, NAND capacity/ECC/retention/endurance and SRAM macro/power evidence. CH05 physical gate requires owner-approved relative timing accuracy, qualified clock PVT/phase/power/retention, trigger apertures, actual IMU and host sync behavior, and simulated/formally reviewed CDC/RDC and reset/clock changes. CH06 ABI freeze requires the exact host part/revision and errata, pin/SPI timing, measured bursts, SRAM/DMA/CDC and security/epoch/loss policy. CH07 topology selection needs electrode and signal/noise/power specifications with measured source models.

# Latest Regression

Command: `python3 scripts/verification/check_all.py`
Commit: read `git rev-parse HEAD` on the checkout under test; a commit cannot self-report its eventual merge SHA.
Result: PASS locally for CH00–CH06 public checks and 69 focused tests; see `state/VERIFICATION_STATUS.md` and CI on the published commit. SV reference is uncompiled; public checks validate bookkeeping and conditional models only.
Timestamp: 2026-09-25 UTC.
