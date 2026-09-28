# CH08 pre-entry: biopotential behavioral verification charter

Date: 2026-09-28 UTC. **Status: PREPARATION ONLY; CH08 remains PLANNED / NOT_RUN.** The current CH07 [topology and block-spec gate](../reviews/CH07_GATE.md) is held. This charter records literature and an acceptance matrix so the behavioral work can begin promptly after that gate passes. It does not constitute CH08 entry, implementation, or a waiver of the `MASTER_SPEC.md` §42 requirement that the channel pass approved system requirements.

## Scope, sources, and boundary

Prepare a [dated primary-source review](../literature/biopotential/2026-09-28_CH08_BEHAVIORAL_PREENTRY_REVIEW.md) of electrode dynamics, mixed-signal model semantics, converter startup/settling, and model-to-testbench verification. Literature window 2021–2026, plus an older manufacturer datasheet as an explicitly condition-specific reference. Compare event/discrete, continuous analog, hybrid, and measured-trace approaches; quantify known example conditions without transferring another device's values to Hummingbird.

CH08 will later implement a selected electrode model, AFE/ADC behavior, saturation and recovery, calibration, quality flags and automated tests in a simulator/toolchain that is actually available. This preparatory work selects **no** AFE coupling, converter filter, reference drive, recovery constant, power state or HDL simulator. It includes no Verilog-A, RNM, ADC implementation, private sensor data or patient-current stimulus.

Trace `BIO-0001`–`BIO-0021`, especially `BIO-0003/0004/0006`–`BIO-0011/0013/0015`–`BIO-0021`, and `SAFE-0001/0003/0005`. Inputs are the [CH07 assumed-only models](../../models/python/ch07_biopotential.py), [CH07 electrode intake](../inputs/CH07_ELECTRODE_QUALITY_INTAKE.md), CH05 timing and CH06 candidate host contracts. All product bands, EEG/ECG quality, allowed dropout, recovery, pad admittance/leakage, body-current policy, rail/power and elected topology are still pending `OI-001/004/005/006/007/010/012/013`.

## Acceptance for this preparatory subchunk

1. Cite original measured electrode work, a real converter datasheet, and current official modeling/verification standards; label the external boundary, bandwidth, conditions, sample count, measured versus vendor versus standard, and transfer limit. Include at least one 2025–2026 primary source and reconcile its fixture/material with the older CH07 survey.
2. Derive the behavioral chain and separate the continuous input/contact dynamics from sampled ADC/filter, calibration, clipping, and quality-state transitions. Give an explicit test stimulus and expected invariant for DC/AC loading, common-mode mismatch, offset and motion, gain/rail saturation, recovery/filter settling, alias, noise with seed, sample timing and reset/lead-off. Do not invent pass limits.
3. Compare modeling representations on continuous-time fidelity, event/runtime scaling, portability, privacy, PDK/tool dependence and required cross-validation. Quantify only the CH07 **candidate** rate arithmetic and an external converter's actual settling example under its stated conditions.
4. Publish a review with `PREENTRY_SURVEY_READY / CH08_ENTRY_HOLD`, run the existing public regression and repository link checks, and leave CH07 `PAUSED` and CH08 `PLANNED, NOT_RUN`. No simulator equivalence or behavioral requirement pass may be claimed.

The later CH08 acceptance will require owner-approved electrode/source distributions and frozen CH07 topology/spec, selected tool support, parameter provenance, an executable electrode/AFE/ADC model, independent test oracles and simulator runs showing each approved system requirement over its corner envelope. Area/power optimization and simulation speed matter after the circuit boundary is chosen; no quality, timing, safety or recovery requirement may be weakened to reduce model complexity.
