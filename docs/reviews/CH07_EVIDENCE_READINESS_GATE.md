# CH07 follow-on gate: complex-source sensitivity and evidence intake

Date: 2026-09-28 UTC. Scope and acceptance were recorded in the [follow-on charter](../chunks/CH07_EVIDENCE_READINESS.md) after the CH07 survey and first [numerical gate](CH07_GATE.md). This is a separate bounded review of a synthetic passive model and a measurement intake protocol. It does not supersede CH07's held topology/block-spec gate.

| Gate | Decision | Evidence and limit |
|---|---|---|
| Source/provenance | **PASS for synthetic sensitivity** | [Versioned input](../../specs/biosignal/CH07_COMPLEX_SENSITIVITY.json) retains the CH07 resistor DC contacts and has assumed units/ranges/source/conditions; measured fields stay null. The [electrode/AFE survey](../literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md) preceded both models. |
| Complex steady-state math | **MODEL_PASS** | [Model](../../models/python/ch07_complex_electrode.py), [generated JSON](../../reports/block/CH07_COMPLEX_SENSITIVITY.json) and [calculation sheet](../budgets/CH07_COMPLEX_ELECTRODE_REVIEW.md) report two-leg RC source, shunt input capacitance, differential loading and source mismatch separately from intrinsic CMRR at 10 assumed frequencies per mode. Five focused tests include the exact resistive limit, passive impedance, equal-leg cancellation, cap sensitivity, bad provenance and non-passive/duplicate-frequency rejection. |
| Measurement acquisition | **PLAN_READY** | [Owner input protocol](../inputs/CH07_ELECTRODE_QUALITY_INTAKE.md) specifies geometry, calibration, complex spectra, offset/movement, signal-quality targets, IC pads/rails and independent safety decision; restricted evidence is referenced, not copied to this public repo. No physical evidence was supplied or certified by this document. |
| Topology selection, full block spec and CH08 | **HOLD / NOT_RUN** | No representative electrode spectra or motion/offset distributions, selected input capacitance/pad leakage, product passband/quality/recovery criteria, PDK/rail/power or approved body-current boundary. No AC/DC topology choice, behavioral channel pass, transistor/PDK work or silicon claim. |

At 50 Hz the two illustrative sources produce 107.06 and 135.66 µV peak mismatch residual for the assumed **1 V peak** common mode and invented capacitances; their worst-phase bounds including 100 dB intrinsic rejection are 117.06 and 145.66 µV peak. These are not measurements or accepted interference limits. A fixed 100 dB intrinsic amplifier CMRR does not fix full-chain source imbalance. Movement/polarization and ESD effects are absent; noise and deterministic interference cannot be combined as independent random quantities. The RC values are not fitted to skin and are not an AFE transfer function.

## Reproduce and next decision

```sh
python3 models/python/ch07_complex_electrode.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch07_complex_electrode.py'
python3 scripts/verification/check_all.py
git diff --check
```

The combined suite should have 86 Python tests after this work. GitHub CI must be checked on the published commit. External electrode and owner evidence must be collected and independently reviewed; a new approved evidence schema and fitting/error analysis will be required before selecting the topology and freezing a block spec. Only then is CH08 eligible. CH03–CH06 physical holds remain open. This subgate is **MODEL_PASS / EVIDENCE_PLAN_READY / TOPOLOGY_AND_REQUIREMENTS_HOLD**.
