# CH05: Clock, timestamp and synchronization

Status: **conditional model complete; physical timing HOLD**. Date: 2026-09-25 UTC. Entry baseline: merged CH04 PR #6 (`95b48dad1460882f068f4d96573aa268491d6ae1`). This charter fixed scope and acceptance before implementation; its first version and the [dated timing literature review](../literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md) merged in PR #7 **before** any CH05 architecture/model work.

## Boundary and trace

CH05 covers `MASTER_SPEC.md` §§17 and 42 and provisional `TIM-0001`–`TIM-0007`, `TIM-0009`, `SYS-0010` and `MEM-0001`. It must describe a single monotonic timestamp representation, clock/wake handoff, trigger relation and event ordering, clock/reset crossings, uncertainty budgeting and IMU FIFO alignment. Preserve CH02 candidate rates and CH04 group timestamp width as assumptions. An internal 64-bit counter and ≤1 µs tick are *candidate model conditions*, not approved electrical targets. `TIM-0008` axis orientation remains a package/IMU contract dependency outside this timing model.

No clock source, cell, RTL topology, physical jitter, power/area, biomarker synchrony threshold, actual IMU, host epoch, analog settling or glitch-free clock switch can be certified without selected silicon and measured interface evidence. CH05 may pass a **conditional model gate**, while physical timing architecture remains on hold. CH06 and all later chunks stay untouched.

## Accepted model contracts

1. Parameterize the active/AON tick rates, 64-bit representation, sleep/wake sequence, bounds on relative clock error, resynchronization interval, event capture/CDC stages, sample latency/jitter and IMU anchor/FIFO correction. Reject invalid and unsupported configurations. Distinguish an exact model integer time from a real hardware clock.
2. AON ownership never goes backward on sleep/wake or host epoch correction. Fine capture is valid only while its clock is running; a low-frequency tick alone must not claim sub-microsecond accuracy. Quantization and uncertainty are reported separately from timestamp word width. Detect ambiguous counter wrap or reset rather than concealing it.
3. Define programmable conceptual trigger routes for LED, optical ADC, EEG/ECG, audio, electrochemical waveform, IMU sync, GPIO and DMA. Preserve occurrence time and stable simultaneous ordering; account for capture, CDC, destination trigger and sample latency. State which high-rate events need a lossless handshake/queue, versus a single-bit synchronizer; never directly synchronize a multi-bit counter.
4. Reconstruct IMU sample time from a **documented hypothetical** hardware sync anchor and FIFO sample index/period, not FIFO read arrival; reject missing anchors, ambiguous indices or unknown actual sensor delay. Host epoch corrections annotate a mapping but do not step monotonic ticks.
5. Generate deterministic machine-readable and human-readable scenario results including clock-tree concept, timing and drift budget, trigger matrix, CDC/RDC inventory, physical inputs still missing and explicit model/physical gate decisions. Do not silently promote any study value to a product requirement.

## Required outputs and tests

| Artifact | Acceptance |
|---|---|
| `specs/system/CH05_TIMING_SCENARIOS.json` | Source/evidence/range for all numbers and explicit missing physical inputs |
| `models/python/ch05_timing.py` | Standard-library deterministic reference with `--check` regeneration |
| `rtl/timestamp/ch05_continuous_reference.sv` | Limited continuous-clock counter reference with explicit unimplemented crossings and no synthesis claim |
| `verification/unit/test_ch05_timing.py` | Tick wrap boundary, ambiguous wrap, simultaneous triggers, async capture, CDC/trigger uncertainties, sleep/wake monotonicity, drift/epoch, IMU FIFO alignment and invalid inputs |
| `reports/subsystem/CH05_TIMING_SUMMARY.json`, `docs/budgets/CH05_TIMING_REVIEW.md` | Reproducible conditional results, physical hold and cross-links |
| `docs/reviews/CH05_GATE.md`, `state/` | Requirement trace, open decisions, recorded regression and next stop point |

Acceptance requires the survey committed first, `python3 scripts/verification/check_all.py` and `git diff --check` passing, reviewable publication with CI green, and a gate explicitly separating model behavior from hardware claims. The SV counter only sketches the continuous-clock comparison; no SV simulator is installed here. Python tests exercise behavioral contracts, **not** RTL equivalence. This RTL is no signoff evidence without simulation, CDC/RDC tools, physical clocks and PDK. Stop at CH05 gate.

## Results and stop point

The [CH05 gate](../reviews/CH05_GATE.md) records MODEL_PASS for the conditional reference and PHYSICAL_TIMING_HOLD for device accuracy, clock power and complete CDC/RTL. The [generated review](../budgets/CH05_TIMING_REVIEW.md) reports 0.5 µs awake and 30.518 µs slow-sleep ticks plus the unproved ~32 µs wake handoff. The input, source, 18 focused tests and reports are versioned; public regression runs 46 tests. CH06 is paused for a separate instruction.
