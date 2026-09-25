# Contributing to Project Hummingbird

This is an engineering research repository with a provisional specification and no selected source/documentation license (OI-008). The repository owner must decide terms before inviting or accepting outside contributions. The workflow below describes project-maintainer work in the meantime; it is not a grant of reuse or contribution rights.

1. Read `README.md`, `state/PROJECT_STATE.md`, `state/CHUNK_STATUS.csv` and the current open issues. Work on an explicitly authorized bounded chunk; CH05 and later design are paused until the user instructs otherwise. CH03–CH04's conditional model gates do not approve physical feasibility.
2. Write scope, input provenance, units, acceptance and linked requirement IDs in the chunk record before implementation. For technical block architecture or implementation, complete and commit the literature/prior-art gate first.
3. Keep unpublished vendor IP, credentials, keys, foundry decks and personal health data outside this public repository. Mark assumptions and scenario/model/simulation/measurement distinctly. Discuss proposed product and safety choices in a reviewed ADR; do not silently freeze a target.
4. Run `python3 scripts/verification/check_all.py`, inspect staged paths and whitespace with `git diff --cached --name-only` and `git diff --cached --check`, and record the limited evidence in `state/VERIFICATION_STATUS.md` or the chunk report.
5. Use a descriptive feature branch, a non-draft PR with the gate result and the exact remaining blockers, then merge to `main` after review. Keep `state/PROJECT_STATE.md` accurate for the next session. A check passing does not represent PDK, silicon, clinical or tapeout signoff.
