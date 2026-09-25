# Current Baseline

Architecture version: unselected; candidate requirements and CH02 scenarios only.
Canonical branch: `main`; read `git rev-parse HEAD` for the current commit after fetching.
Reviewed baseline before this documentation pass: `c6bd26ea057852b5861956bdd0a34f04de88d179` (CH02 merged as PR #2).
Current chunk: none active. CH00–CH02 are complete at their explicitly limited gates; CH03 is paused pending user instruction.
Current subchunk: none active; CH03 entry charter prepared without starting the model.
Current status: no product mode, electrical target, chip architecture, battery runtime or tapeout claim approved.

# Passed Gates

- CH00: tracked scaffold and structural check; no silicon evidence.
- CH01: provisional 223-ID requirements register and consistency review, merged as PR #1.
- CH02: eight candidate modes and two stress probes with resource arithmetic and seven unit tests, merged as PR #2; see `docs/reviews/CH02_GATE.md`.

# Active Work

- No engineering chunk active. The CH03 entry charter in `docs/chunks/CH03_POWER_ENERGY.md` defines the next bounded model without inventing cell or load data; no circuit implementation or block literature survey underway.
- `state/CHUNK_STATUS.csv` records the complete CH00–CH50 queue; folders marked reserved in `docs/REPOSITORY_MAP.md` are not completed deliverables.

# Blocked Items

- Product priorities/concurrency, cell voltage/impedance, optical source radiometry, actual nRF host throughput, pinout/package rules and foundry/IP availability. See `state/OPEN_ISSUES.md` and `docs/inputs/REQUIRED_INPUTS.md`.
- Architecture and tapeout gates remain blocked by missing external evidence and by the later design/review sequence in `MASTER_SPEC.md`.

# Next Exact Action

- Wait for the user's instruction to begin design. The next planned bounded unit is **CH03**, a parameterized energy, runtime and peak-current model for 8/10/14/20 mAh cases with unknown values and sensitivities clearly labeled. Review its scope and inputs at start. Do not begin CH04 or a block architecture before its own gate and required literature review.

# Required Inputs

- Cell chemistry, voltage window, impedance and capacity versus load/temperature; LED voltage/current and rail efficiency; MCU/RF, sensor and audio state currents; product duty cycles. A CH03 model can bound uncertainties without presenting missing measurements as facts.

# Latest Regression

Command: `python3 scripts/verification/check_all.py`
Commit: read `git rev-parse HEAD` on the checkout under test; a commit cannot self-report its eventual merge SHA.
Result: PASS locally after the pre-kickoff documentation update; see `state/VERIFICATION_STATUS.md` and the CI check on the published commit. Public checks establish repository consistency and CH02 arithmetic only.
Timestamp: 2026-09-25 UTC.
