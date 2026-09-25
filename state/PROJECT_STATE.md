# Current Baseline

Architecture version: unselected; provisional requirements, CH02 scenarios, conditional CH03 energy, CH04 dataflow and CH05 timing models only.
Canonical branch: `main`; read `git rev-parse HEAD` for the current commit after fetching.
Previous reviewed baseline: `bb0ce3ecb772a27819932cdb7680f832536d0320` (CH05 literature/entry PR #7 merged before any timing model).
Current chunk: none active. CH00–CH05 complete at limited gates; CH06 is paused pending user instruction.
Current subchunk: CH05 synthetic clock, monotonic time, trigger/CDC budget and IMU FIFO model complete; physical timing architecture HOLD.
Current status: no product mode, battery runtime, host/BLE throughput, SRAM/NAND selection, pulse safety limit, electrical/timing target, chip architecture or tapeout claim approved.

# Passed Gates

- CH00: tracked scaffold and structural check; no silicon evidence.
- CH01: provisional 223-ID requirements register and consistency review, merged as PR #1.
- CH02: eight candidate modes and two stress probes with resource arithmetic and seven unit tests, merged as PR #2; see `docs/reviews/CH02_GATE.md`.
- CH03: conditional energy/sag/loss/peak-current arithmetic and nine focused tests, MODEL_PASS; measured battery/product/safety FEASIBILITY_HOLD in `docs/reviews/CH03_GATE.md`.
- CH04: CH02 raw-rate reconciliation, conditional packet/queue/SRAM/NAND arithmetic and 12 focused tests, MODEL_PASS; physical host/BLE/storage/product FEASIBILITY_HOLD in `docs/reviews/CH04_GATE.md`.
- CH05: primary timing survey/quantitative comparison merged as PR #7 before architecture work; conditional clock/trigger/drift/IMU model and 18 focused tests, MODEL_PASS; physical timing and uncompiled RTL HOLD in `docs/reviews/CH05_GATE.md`.

# Active Work

- No engineering chunk active. CH03–CH05 sources, models and reports are versioned; CH06 and physical circuit design have not begun. The small SV reference is uncompiled and does not select a timebase.
- `state/CHUNK_STATUS.csv` records the complete CH00–CH50 queue; folders marked reserved in `docs/REPOSITORY_MAP.md` are not completed deliverables.

# Blocked Items

- Product priorities/concurrency, measured cell voltage/impedance/pulse limit and capacity, real rail/load/duty data, optical source radiometry, actual host/BLE link and memory throughput/endurance, SRAM implementation, approved cross-sensor timing/error limits, qualified clocks/IMU and CDC/RDC, pinout/package rules and foundry/IP availability. See `state/OPEN_ISSUES.md` and `docs/inputs/REQUIRED_INPUTS.md`.
- Architecture and tapeout gates remain blocked by missing external evidence and by the later design/review sequence in `MASTER_SPEC.md`.

# Next Exact Action

- Stop at CH05's limited model gate. Wait for the user's instruction to begin **CH06** register map/host protocol; define its scope, literature requirement and acceptance first. Do not select a technical block topology before its committed literature gate or promote CH03–CH05's synthetic outputs to product targets.

# Required Inputs

- CH03 physical gate still requires representative cell chemistry/OCV/impedance/usable capacity across load, temperature and age; LED/rail/load waveforms and converter efficiency; validated pulse limit and owner-approved mode schedule. CH04 physical gate additionally requires approved stream/framing/feature policies, measured host and BLE goodput/wake traces, write/erase stalls, NAND capacity/ECC/retention/endurance and SRAM macro/power evidence. CH05 physical gate requires owner-approved relative timing accuracy, qualified clock PVT/phase/power/retention, trigger apertures, actual IMU and host sync behavior, and simulated/formally reviewed CDC/RDC and reset/clock changes.

# Latest Regression

Command: `python3 scripts/verification/check_all.py`
Commit: read `git rev-parse HEAD` on the checkout under test; a commit cannot self-report its eventual merge SHA.
Result: PASS locally for CH00–CH05 public checks and 46 focused tests; see `state/VERIFICATION_STATUS.md` and CI on the published commit. SV reference is uncompiled; public checks validate bookkeeping and conditional math only.
Timestamp: 2026-09-25 UTC.
