# CH02: Concurrent operating modes and shared resources

Status: complete for scenario accounting; physical feasibility not frozen
Input baseline: merged CH01 on `main` (`03ffe313f2325d26455e741416bbf821346c5118`).

## Scope

Translate §37's eight example modes into explicit **candidate** stream combinations; quantify raw and framed sample traffic, simultaneous converter occupancy, minimum logical acquisition producers, peak programmed LED output current, and sensor-to-ASIC signal contacts. Include stress probes for simultaneous-bank violations and optional fast research ADCs. Link each unresolved conflict to the CH01 register.

## Non-scope

Do not select an ADC topology, physical pinout, host SPI frequency, battery chemistry, sensor duty cycle, signal bandwidth or product mode as mandatory. CH03 owns power/energy and battery-current calculations; CH04 owns buffering, storage throughput and precise host packet/framing models. A mode's computed traffic is **not** evidence it can run with required noise, safety, timestamp accuracy or battery life. No circuit block is designed here, so the block literature gate remains pending.

## Inputs and assumption policy

- `MASTER_SPEC.md` §§4–5, 7–27, 37, 42; `state/REQUIREMENTS_TRACEABILITY.csv`; `state/OPEN_ISSUES.md`.
- `specs/system/CH02_MODE_ASSUMPTIONS.json` holds explicit illustrative sample rates, word widths, modes and hypothetical interface capacities. Every mode is provisional until product approval.
- No external IC spec, foundry figure, actual cell voltage or rail efficiency is assumed. Unknown peak battery/RF/audio current is reported as unknown.

## Outputs

1. Executable standard-library model `models/python/ch02_concurrency.py` with deterministic machine and human readable output.
2. `reports/subsystem/CH02_RESOURCE_SUMMARY.json` and `docs/budgets/CH02_CONCURRENCY_REVIEW.md` with matrix, loads, conflicts and requirements.
3. Focused regression covering numerical accounting, violations, unknown battery current, and source register links.
4. Updated issues, risk and state files.

## Acceptance

- All eight §37 modes represented as candidates and two separate research stress probes represented without assuming they are supported product modes.
- Compute raw bit/s, conservative framed bit/s, guarded link requirement, stream count, ADC bank occupancy, known LED output current and pin-contact bounds.
- Explicitly flag BIO/optical bank oversubscription and protocol sensitivity; never convert optical LED output current directly into battery current.
- All mode requirement IDs exist; output regenerates deterministically with `python3 models/python/ch02_concurrency.py --write`.
- `python3 -m unittest discover -s verification/unit -p 'test_ch02_*.py'`, CH00/CH01 checks and `git diff --check` pass.
- Commit on a CH02 feature branch; stop before CH03.

## Results

- Eight candidate modes and two stress probes modeled with reproducible machine/human reports.
- Seven focused tests, deterministic regeneration, CH00/CH01 checks and `git diff --check` pass.
- Formal gate result and limitations: `docs/reviews/CH02_GATE.md`.
- Commit and PR: inspect this feature branch after publication.

## Next exact action

CH03: measured/parameterized battery energy and transient-current model using approved mode duty cycles and cell data. Keep unapproved modes as explicit scenarios.
