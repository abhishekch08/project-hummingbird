# CH05 gate: Conditional clock, timestamp and synchronization model

Date: 2026-09-25 UTC. Entry baseline: CH05 literature/charter [PR #7](https://github.com/abhishekch08/project-hummingbird/pull/7), merged as `bb0ce3ecb772a27819932cdb7680f832536d0320` **before** the first CH05 architecture model commit. Scope: `MASTER_SPEC.md` §§17, 42; [entry charter](../chunks/CH05_CLOCK_TIMING.md), [reviewed source survey](../literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md), [scenario](../../specs/system/CH05_TIMING_SCENARIOS.json), [Python reference](../../models/python/ch05_timing.py) and [limited SV counter reference](../../rtl/timestamp/ch05_continuous_reference.sv). Report: [machine-readable result](../../reports/subsystem/CH05_TIMING_SUMMARY.json) and [human-readable budget](../budgets/CH05_TIMING_REVIEW.md).

## Decision

| Gate | Decision | Basis and limit |
|---|---|---|
| Survey before design | **PASS for conditional CH05 work** | Primary measured RC oscillator reports, manufacturer IMU guidance and original OpenTitan/AMD clock/CDC documents, with measured versus vendor/analytical cases labeled. Committed/merged first. |
| Behavioral time/trigger accounting | **MODEL_PASS** | Explicit clocks/ppm/apertures, retained coarse epoch, awake fine or continuous comparison, monotonic sleep/wake trace, half-range rollover/overflow rejection, stable simultaneous trigger order, CDC/latency/jitter terms, host mapping and indexed IMU FIFO correction. Generated reports verified against their source and 18 focused CH05 tests. |
| Candidate 1 µs across all modes | **NOT MET by LF-only / HOLD overall** | Illustrative 32,768 Hz sleep period ~30.518 µs; the awake fine tick is 0.5 µs, but this does not establish ≤1 µs sleep capture or cross-mode accuracy. The continuous 1 MHz counter is only an analytical alternative without known power, clock quality and retention. |
| Physical clock and complete RTL implementation | **PHYSICAL_TIMING_HOLD** | Oscillator, PVT, power/area, CLK/RST gating, wake event delivery, trigger aperture, sensor clock ratio, real IMU, CDC/RDC tools and independent review absent. SV reference only increments an already-synchronized continuous clock and was not simulated/compiled here because no SV simulator is installed. Python tests do not verify RTL equivalence. |
| CH06 host protocol | **NOT RUN** | CH06 remains at its next separate entry gate. |

## What the model establishes

The synthetic LF+fine comparator labels are monotonic at 990,000 µs awake, 1,199,981 µs asleep and 1,259,999 µs awake after a slightly off-edge wake. Its handoff upper bound is **32 µs** of quantization under the assumed phase alignment, plus clock drift and unknown physical effects. Clamping coarse observations prevents a backward label but can repeat values. A separate continuously clocked 1 MHz comparator keeps a 1 µs tick during sleep **if** the clock truly remains powered, which CH03 has not established. Neither path is selected product architecture.

The active illustrative LED trigger captured after an edge passes via a synthetic two-stage destination synchronizer and one trigger pipeline cycle, then reaches a sensor aperture after a nominal 4 µs. The report lists capture (<500 ns), destination phase (<500 ns), pipeline (500 ns), dispatch (500 ns), nominal sample latency (4 µs) and hypothetical jitter (500 ns), a conservative 6.5 µs occurrence-to-sample envelope; the full event record retains separate physical event and sample timestamp. During sleep, a destination that cannot run must reject triggering until a wake/retained-queue contract is supplied. Host epoch mapping may be recalibrated without stepping sensor monotonic time; a fictional 20 ppm over 100 s permits 2 ms timebase drift *before* host exchange and clock phase terms.

The IMU example derives a sample aperture at 1,248,000,000 ns from sync anchor, FIFO index, sample period and sample pipeline correction; the later FIFO read at 1,300,000 µs is not sample time. Its model-only 102,000 ns uncertainty excludes anchor-capture uncertainty. Actual IMU sync semantics/ODR trim and packet indexing are not selected. The conceptual eight-source trigger matrix is **not** a register map or safe exposure policy; source-to-target assignments remain candidate fixtures.

## Reproduction and verification

```sh
python3 models/python/ch05_timing.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch05_*.py'
python3 scripts/verification/check_all.py
git diff --check
```

CH05 unit suite: 18 tests covering ideal edge quantization, half-range wrap and 64-bit overflow, sleep/wake continuity and fine-clock validity, stable simultaneous events and sample latency, sleep destination rejection, host epoch update/drift, IMU indexed sample time and invalid provenance/physical data. Whole public regression: CH00–CH05 source/report checks and 46 focused tests. The GitHub Actions run on this PR/merge is the authoritative published CI result; write it only after it completes. No hardware measurements, SV compile/formal equivalence, gate-level timing, CDC/RDC signoff or medical validation were run.

## Requirement mapping and exit criteria

| ID | Conditional evidence | Remaining closure |
|---|---|---|
| `TIM-0001`, `TIM-0002`, `TIM-0004` | Monotonic retained model, tick comparison, 64-bit overflow and short-counter ambiguity tests | Qualified AON retention/clock, approved longest logging interval, sensor-wide capture accuracy, reset behavior. |
| `TIM-0003`, `TIM-0006` | Host-drift example and sum of separate capture, crossing and sample terms | Owner-approved sample error and resync requirement; measured clock PVT/phase, host exchange and analog aperture. |
| `TIM-0005` | Eight conceptual source routes, stable ties/sequence, explicit occurrence and sample values | Approved trigger programmability, priority, backpressure, safety gating and actual register contract in CH06/later chunks. |
| `TIM-0007` | Sync anchor + FIFO index/period/delay calculation and invalid-index/read check | Selected IMU/FIFO pin timing, native timestamp rate/trimming and calibration. |
| `TIM-0009` | Crossing inventory, sleep-destination rejection, coherent-bus and reset-release policy | RTL simulation, formal/CDC/RDC reports, silicon library clock mux/reset implementation and signoff. |
| `SYS-0010`, `MEM-0001` | Keeps CH02 candidate simultaneous streams and CH04 64-bit group accounting separate from event capture | End-to-end schedule/queue effects and timestamp width/protocol after actual CH06/CH19 design. |

All IDs retain provisional maturity. Open `OI-001/006/010/012/013/014/015` and related timing/transport risks. [ADR-0002](../adr/ADR-0002_CONDITIONAL_TIMEBASE.md) records the comparison without a physical selection. **Stop point:** CH05 conditional gate complete; hold its physical architecture and all CH06 work until separately requested. CH03/CH04 physical feasibility stays on hold.
