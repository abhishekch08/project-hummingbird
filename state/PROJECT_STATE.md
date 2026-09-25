# Current Baseline

Architecture version: unselected; provisional requirements, CH02 scenarios and a conditional CH03 energy model only.
Canonical branch: `main`; read `git rev-parse HEAD` for the current commit after fetching.
Previous reviewed baseline: `207870f285841665f543e686e6853e7e85071ace` (CH03 entry charter merged as PR #4).
Current chunk: none active. CH00–CH03 are complete at limited gates; CH04 is paused pending user instruction.
Current subchunk: CH03 synthetic arithmetic complete; physical cell and product feasibility HOLD.
Current status: no product mode, battery runtime, pulse safety limit, electrical target, chip architecture or tapeout claim approved.

# Passed Gates

- CH00: tracked scaffold and structural check; no silicon evidence.
- CH01: provisional 223-ID requirements register and consistency review, merged as PR #1.
- CH02: eight candidate modes and two stress probes with resource arithmetic and seven unit tests, merged as PR #2; see `docs/reviews/CH02_GATE.md`.
- CH03: conditional energy/sag/loss/peak-current arithmetic and nine focused tests, MODEL_PASS; measured battery/product/safety FEASIBILITY_HOLD in `docs/reviews/CH03_GATE.md`.

# Active Work

- No engineering chunk active. CH03's input/model/report and incomplete physical inventory are versioned; CH04 and circuit design have not begun.
- `state/CHUNK_STATUS.csv` records the complete CH00–CH50 queue; folders marked reserved in `docs/REPOSITORY_MAP.md` are not completed deliverables.

# Blocked Items

- Product priorities/concurrency, measured cell voltage/impedance/pulse limit and capacity, real rail/load/duty data, optical source radiometry, actual nRF host throughput, pinout/package rules and foundry/IP availability. See `state/OPEN_ISSUES.md` and `docs/inputs/REQUIRED_INPUTS.md`.
- Architecture and tapeout gates remain blocked by missing external evidence and by the later design/review sequence in `MASTER_SPEC.md`.

# Next Exact Action

- Stop at CH03's limited model gate. Wait for the user's instruction to begin **CH04** data-rate, buffering and memory feasibility, then review its scope and acceptance. Do not select a technical block topology before its committed literature gate or promote CH03's synthetic runtime to a product target.

# Required Inputs

- CH03 physical gate still requires representative cell chemistry/OCV/impedance/usable capacity across load, temperature and age; LED/rail/load waveforms and converter efficiency; validated pulse limit and owner-approved mode schedule. CH04 requires measured host timings, framing, memory behavior and accepted loss/backpressure rules.

# Latest Regression

Command: `python3 scripts/verification/check_all.py`
Commit: read `git rev-parse HEAD` on the checkout under test; a commit cannot self-report its eventual merge SHA.
Result: PASS locally for CH00–CH03 public checks and 16 focused tests; see `state/VERIFICATION_STATUS.md` and CI on the published commit. This validates bookkeeping and synthetic math only.
Timestamp: 2026-09-25 UTC.
