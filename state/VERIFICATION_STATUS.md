# Public verification status

As of 2026-09-25 UTC. Run `python3 scripts/verification/check_all.py` from a fresh checkout or any working directory with Python 3. The workflow in `.github/workflows/validate.yml` runs the same command for pushes and pull requests; the workflow's actual GitHub result must be read on the commit being reviewed.

| Gate | Available evidence and check | What it establishes | What it does not establish |
|---|---|---|---|
| CH00 structure | `scripts/verification/check_bootstrap.py` | Required files, CSV schema, CH00–CH50 headings and prohibited master term. | Completeness of all requirements or implementation. |
| CH01 register | `scripts/verification/check_requirements.py` | 223 provisional IDs, field validity, source-section coverage, issue linkage and ID uniqueness. | Proven electrical targets or approved product claims. |
| CH02 arithmetic | `models/python/ch02_concurrency.py --check` and seven `verification/unit/test_ch02_concurrency.py` tests | Deterministic generated report and selected conflicts, rates and assumptions. | Physical pin fit, battery peaks, ADC quality, host capability, safety or measured behavior. |
| CH03 conditional energy | `models/python/ch03_energy.py --check` and nine `verification/unit/test_ch03_energy.py` tests | Regenerable synthetic input/model/report; unit, quadratic-root, collision, loss, charge, cutoff, startup and missing-data checks. | Measured usable energy, cell pulse current, real mode runtime, thermal or safety limits. |
| Repository readiness | `scripts/verification/check_repository.py` | Relative Markdown links/anchors, contiguous chunk index and status, Python syntax, required governance files, no forbidden master wording. | Scientific completeness or independent engineering review. |
| Public regression | `scripts/verification/check_all.py` | Executes the four checks above plus unit tests in one failure-propagating invocation. | AMS, EDA, PDK, silicon, clinical or tapeout signoff. |

**Gate result:** CH00–CH02 retain their narrow scopes in `docs/reviews/CH01_REQUIREMENTS_REVIEW.md` and `docs/reviews/CH02_GATE.md`. CH03 is MODEL_PASS and physical FEASIBILITY_HOLD in `docs/reviews/CH03_GATE.md`. CH04–CH50 have no test results or gate approvals. This page records the reproducible procedure; CI on the latest merged commit is the authoritative public run.
