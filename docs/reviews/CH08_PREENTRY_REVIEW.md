# CH08 pre-entry literature and acceptance review

Date: 2026-09-28 UTC. The user authorized continued chapter work; this is a **bounded preparatory review** while CH07's topology/block-spec gate is paused. It does not start CH08 implementation or supersede [`MASTER_SPEC.md` §42](../../MASTER_SPEC.md#ch08-biopotential-behavioral-implementation).

| Check | Result | Evidence and boundary |
|---|---|---|
| Source freshness and provenance | PREENTRY_SURVEY_READY | [Dated review](../literature/biopotential/2026-09-28_CH08_BEHAVIORAL_PREENTRY_REVIEW.md) includes 2024 and 2026 measured electrodes, 2025 dry-EEG comparison, a 2017 device-specific ADC settling example, Accellera 2024/2025 standards, and a 2025 original mixed-signal process paper. Hardware/source evidence, standards and engineering inferences are separately labeled. |
| Scope and testability | PREENTRY_PLAN_READY | [Charter](../chunks/CH08_PREENTRY_BEHAVIORAL.md) derives candidate modeling boundaries and an input→fault→oracle matrix; no unapproved physical limit becomes a pass/fail test. The 8/16 thousand output events versus 2.048/4.096 million hypothetical modulator channel ticks per second and TI 3-period settling are explicitly scenario/vendor arithmetic, not measured runtime or selected hardware. |
| CH08 entry | **HOLD** | CH07's owner-approved electrode, quality, power, pad/ESD, safe body-connected boundary, topology and frozen block specification are still absent; selected EDA simulator and analog/RNM bridge are unknown. |
| Behavioral implementation and requirement gate | **NOT_RUN** | No Verilog-A, RNM, ADC, calibration, simulator, electrode-phantom or system-requirement result was created. `state/CHUNK_STATUS.csv` remains CH07 PAUSED and CH08 PLANNED / NOT_RUN. |

Reproduction: review the sources and links; run `python3 scripts/verification/check_all.py` and `git diff --check` for repository integrity. The public regression tests previous conditional models, **not the scientific conclusions of this survey**. Publish the pre-entry work to `main` only with these limits. The next executable design action remains the CH07 measured-evidence/topology review, followed by a refreshed CH08 literature/trade gate and then its behavioral implementation.
