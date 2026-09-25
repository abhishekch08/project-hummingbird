# Current Baseline

Architecture version: unselected; provisional requirements, CH02 scenarios, conditional CH03 energy, CH04 dataflow, CH05 timing, CH06 candidate host and CH07 biopotential numerical models only.
Canonical branch: `main`; read `git rev-parse HEAD` for the current commit after fetching.
Previous reviewed baseline: `4e6bd443a2de7402f0ff92fcaba076790b717a19` (CH07 entry/literature PR #11 merged before any numerical model).
Current chunk: CH07 under user authorization for subsequent chapters. CH00–CH06 complete at limited gates; CH07 has a passing conditional numerical subgate and an unfulfilled topology/block-spec gate.
CH07 is paused at its topology and frozen-requirements gate for owner-approved electrode, signal-quality, PDK/power and safety evidence; user authorization already covers continuation when those inputs exist.
Current subchunk: CH07 source survey merged as PR #11, synthetic numerical report and 12 tests published as a limited model gate. CH05 timing and CH06 physical host ABI remain HOLD.
Current status: no product mode, battery runtime, host/BLE throughput, SRAM/NAND selection, pulse safety limit, electrical/timing target, chip architecture or tapeout claim approved.

# Passed Gates

- CH00: tracked scaffold and structural check; no silicon evidence.
- CH01: provisional 223-ID requirements register and consistency review, merged as PR #1.
- CH02: eight candidate modes and two stress probes with resource arithmetic and seven unit tests, merged as PR #2; see `docs/reviews/CH02_GATE.md`.
- CH03: conditional energy/sag/loss/peak-current arithmetic and nine focused tests, MODEL_PASS; measured battery/product/safety FEASIBILITY_HOLD in `docs/reviews/CH03_GATE.md`.
- CH04: CH02 raw-rate reconciliation, conditional packet/queue/SRAM/NAND arithmetic and 12 focused tests, MODEL_PASS; physical host/BLE/storage/product FEASIBILITY_HOLD in `docs/reviews/CH04_GATE.md`.
- CH05: primary timing survey/quantitative comparison merged as PR #7 before architecture work; conditional clock/trigger/drift/IMU model and 18 focused tests, MODEL_PASS; physical timing and uncompiled RTL HOLD in `docs/reviews/CH05_GATE.md`.
- CH06: host/register primary survey merged as PR #9 before candidate contract; 23 tests and CH04 rate reconciliation, MODEL_PASS; frozen host/ASIC ABI and physical SPI/DMA HOLD in `docs/reviews/CH06_GATE.md`.
- CH07: electrode/AFE survey merged as PR #11 before any numerical model; conditional resistor/noise/interference/headroom/alias/OSR sensitivities and 12 focused tests, MODEL_PASS; selected topology and block specification HOLD in `docs/reviews/CH07_GATE.md`.

# Active Work

- CH07 numerical fixtures are versioned; both violate at least one invented goal and select no circuit. CH08 and later chapters requiring a frozen block spec cannot claim a valid requirement-pass gate; see `docs/reviews/CH08_CH50_ENTRY_AUDIT.md`. CH05's small SV reference is uncompiled and does not select a timebase. Physical circuit design has not begun.
- `state/CHUNK_STATUS.csv` records the complete CH00–CH50 queue; folders marked reserved in `docs/REPOSITORY_MAP.md` are not completed deliverables.

# Blocked Items

- Product priorities/concurrency, measured cell voltage/impedance/pulse limit and capacity, real rail/load/duty data, optical source radiometry, actual host/BLE link and memory throughput/endurance, SRAM implementation, approved cross-sensor timing/error limits, qualified clocks/IMU and CDC/RDC, EEG/ECG electrode complex source/noise/artifact distributions and quality limits, safe body-drive/protection policy, pinout/package rules and foundry/IP availability. See `state/OPEN_ISSUES.md` and `docs/inputs/REQUIRED_INPUTS.md`.
- Architecture and tapeout gates remain blocked by missing external evidence and by the later design/review sequence in `MASTER_SPEC.md`.

# Next Exact Action

- Close CH07's topology/specification gate with representative electrode model versus frequency and movement, approved EEG/ECG signal-quality/passband/recovery/power targets, qualified pad/PDK and body-current safety policy. Then choose/review topology and only then start CH08 behavior. Do not promote CH03–CH07's synthetic outputs to product targets.

# Required Inputs

- CH03 physical gate still requires representative cell chemistry/OCV/impedance/usable capacity across load, temperature and age; LED/rail/load waveforms and converter efficiency; validated pulse limit and owner-approved mode schedule. CH04 physical gate additionally requires approved stream/framing/feature policies, measured host and BLE goodput/wake traces, write/erase stalls, NAND capacity/ECC/retention/endurance and SRAM macro/power evidence. CH05 physical gate requires owner-approved relative timing accuracy, qualified clock PVT/phase/power/retention, trigger apertures, actual IMU and host sync behavior, and simulated/formally reviewed CDC/RDC and reset/clock changes. CH06 ABI freeze requires the exact host part/revision and errata, pin/SPI timing, measured bursts, SRAM/DMA/CDC and security/epoch/loss policy. CH07 topology selection needs electrode and signal/noise/power specifications with measured source models.

# Latest Regression

Command: `python3 scripts/verification/check_all.py`
Commit: read `git rev-parse HEAD` on the checkout under test; a commit cannot self-report its eventual merge SHA.
Result: PASS locally for CH00–CH07 public checks and 81 focused tests; see `state/VERIFICATION_STATUS.md` and CI on the published commit. SV reference is uncompiled; public checks validate bookkeeping and conditional models only.
Timestamp: 2026-09-25 UTC.
