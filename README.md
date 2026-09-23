# Project Hummingbird

Research and engineering workspace for a compact physiological computing ASIC/SiP. [MASTER_SPEC.md](MASTER_SPEC.md) defines the candidate requirements and chunk gates; it is not a verified tapeout specification.

Start each session at [state/PROJECT_STATE.md](state/PROJECT_STATE.md). Read the master spec and current state, complete one bounded chunk, run its checks, update evidence and state, commit and push. Design-oriented chunks require a documented recent literature survey before architecture selection.

CH00 is the repository scaffold. Next is CH01 requirements normalization. Run the structural check with `python3 scripts/verification/check_bootstrap.py`. No proprietary PDK, licensed IP, credentials or personal physiological data belongs in this repository.
