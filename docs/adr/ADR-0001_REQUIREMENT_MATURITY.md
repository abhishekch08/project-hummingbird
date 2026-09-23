# ADR-0001: Keep candidate engineering targets separate from approvals

Status: adopted process policy (CH01/CH02 baseline; no circuit selection)
Date: 2026-09-23
Requirement IDs: process IDs and affected subsystem IDs in `state/REQUIREMENTS_TRACEABILITY.csv`

## Context and evidence

The master plan contains aggressive numerical targets and biomedical feature ideas before product modes, cell performance, source impedances, safety scope, process or vendor access are established. CH01 classified 223 provisional/process rows and CH02 evaluated conditional scenarios. A count-level fit in CH02 does not prove electrical feasibility, safety or clinical performance.

## Decision

Preserve each register row's `CANDIDATE`, `NEEDS_DEFINITION`, `RESEARCH_ONLY` or `PROCESS_ACTIVE` status. Use the CH02 JSON as source for scenario arithmetic. Require the responsible product/engineering owner to record external evidence, units/conditions, changed traceability and an approved decision before marking a technical constraint or product mode as frozen. Keep a process check PASS separate from subsystem design PASS.

## Alternatives and tradeoff

Treating master targets or CH02 counts as fixed requirements would simplify near-term design choices but could lock in impossible battery, contact, noise or host budgets. Deferring all modeling would obscure conflicts. Conditional models expose scale and contradictions while protecting the quality/safety gates; they cost review time and must be explicitly labeled.

## Consequences, risk and verification

No architecture has been selected. CH03 can model energy with unknowns. Future changes to numeric scenarios need a versioned config update and regeneration; promotion to product requirements needs owner approval and the relevant quantitative gate. The register checker, CH02 model/tests and project state check the separation visible today; they do not substantiate the underlying physical targets. Revisit after product decisions and CH03–CH04 evidence, then at every affected block gate.
