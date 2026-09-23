# CH01: Requirements normalization and traceability

Status: complete: provisional extraction accepted; architecture not frozen
Baseline: `MASTER_SPEC.md` at CH00 remote commit `5ea0185f5b527efd0647e9197d92fea1e7b646da`.

## Scope

Extract atomic, stable candidate requirement IDs from the master specification; classify requirement maturity, identify duplicated statements and conflicts; assign planned verification methods, roles and source sections. Review the requirements as a *provisional* register. Update project state and record the first unresolved decisions.

## Non-scope

No block literature survey, architecture selection, electrical modeling, RTL, circuit implementation, or silicon performance verification. CH02–CH06 remain prerequisites for the first proposed biopotential design chunk (CH07). No proposed electrical number becomes a frozen specification in CH01.

## Inputs

- `MASTER_SPEC.md`, Sections 0–61.
- Current `state/` records and `docs/chunks/CH_TEMPLATE.md`.
- Product priorities, measured cell/sensor data, foundry information and regulatory market: presently unresolved.

## Method

- One row represents one independently reviewable behavior, bound or process control. A conditional safety rule applies if the associated energy/drive feature is selected.
- Preserve numeric targets and operating conditions as proposed, and flag unspecified conditions.
- `Priority` describes intent in the master, while `Status` describes requirement maturity: `CANDIDATE`, `NEEDS_DEFINITION`, `RESEARCH_ONLY`, or `PROCESS_ACTIVE`. `MUST` does not imply that a silicon implementation is already validated.
- `Notes` contains the source section and linked open issue. `Design_Artifact` and `Test_Artifact` are **planned paths**, not claims that files or test results exist.
- Repeated target summaries and repeated process instructions map to the same IDs; descriptive examples and selectable architecture options are not requirements to implement every option.

## Acceptance

1. Requirements CSV has unique, stable IDs; no empty requirement, priority, owner, method, status or source.
2. All functional areas in Sections 1–38 and normative program rules have documented candidate IDs or justified dispositions.
3. Safety-critical clauses and headline numerical targets have individual IDs.
4. Review identifies numerical contradictions, missing operating conditions and research-only biomarker claims without silently resolving them.
5. Bootstrap and requirements checks pass. Save test evidence, commit and publish this chunk before CH02.

## Literature survey

Not applicable to CH01: this is requirement transcription and review. The literature-first design gate applies before CH05/CH07 or any design choice and remains unpassed.

## Results

- 223 candidate/process IDs in the register; source coverage and conflicts recorded in `docs/reviews/CH01_REQUIREMENTS_REVIEW.md`.
- `python3 scripts/verification/check_bootstrap.py` and `python3 scripts/verification/check_requirements.py`: PASS on 2026-09-23. These checks do not demonstrate electrical performance.
- Commit: use the CH01 feature branch HEAD after publication.

## Next exact action

CH02: quantify concurrent operating modes and resource conflicts, using these provisional requirements and the open issues.
