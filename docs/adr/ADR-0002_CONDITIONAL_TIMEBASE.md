# ADR-0002: Conditional timebase alternatives

Status: **proposed model study; no physical clock selected**. Date: 2026-09-25 UTC. Links: `TIM-0001`–`TIM-0007`, `TIM-0009`, `OI-006/010/012/014`. Evidence: [CH05 primary survey](../literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md) committed/merged first; [CH05 numerical report](../budgets/CH05_TIMING_REVIEW.md) and [gate](../reviews/CH05_GATE.md).

## Context and alternatives

| Alternative | Nominal model tick | Sleep continuity and accuracy | Power/area/safety state |
|---|---:|---|---|
| Slow LF AON only | 30.518 µs at 32,768 Hz | If retained, continuity; fails candidate ≤1 µs resolution. | PDK power/area and system drift unknown; cannot align close sensor events. |
| Continuous 1 MHz AON | 1 µs | Conditional tick resolution during sleep if clock stays alive; actual jitter/phase unknown. | Additional always-on energy unknown; must revisit CH03 energy and clock integrity. |
| Retained LF AON + awake 2 MHz fine | 30.518 µs sleep, 0.5 µs awake | Monotonic model with ~32 µs wake-handoff quantization upper bound; sleep fine capture invalid. | Unknown cross-calibration, wake latency, reset/race and startup power; can mislabel close multimodal events. |
| Independently timestamped peripherals + host alignment | Device-dependent | Host/FIFO reception cannot reconstruct unknown sensor aperture or missed device sync. | No common monotonic clock contract until physical anchor and tolerances exist. |

## Conditional decision

Keep the LF+fine and continuous candidates in a common parameterized reference. Require a retained time owner, source-timestamp preservation, explicit epoch handoff, host offset mapping without stepping monotonic ticks, and coherent CDC for multi-bit state. Reject LF-only for the candidate ≤1 µs active tick and reject unanchored FIFO arrival as sample time. Trigger safety interlocks and physical clock source remain undecided. There is no measured area/power figure for the Hummingbird clock tree; the P1/P2 oscillator measurements in the survey cannot be transplanted to this process.

Consequence: physical timing gate held even though conditional state/error accounting passes. Review with algorithm owner to set per-modality allowed timing and jitter, selected IMU/clock vendor/PDK for PVT/power/phase and reset/CDC/RTL signoff, and system owner for awake/sleep event policy. Revisit at a reviewed architecture gate before use of the SV reference or registration of CH06 protocol semantics.
