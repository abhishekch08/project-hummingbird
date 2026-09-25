# Repository instructions for engineering assistants

This public repository is the source of truth. Start with `README.md`, `MASTER_SPEC.md`, `state/PROJECT_STATE.md`, `state/CHUNK_STATUS.csv`, `state/DECISIONS.md`, `state/OPEN_ISSUES.md`, `state/ASSUMPTIONS.md`, and the active chunk file. Inspect Git status and fetch the latest canonical `main` before changing anything.

- Work on **one authorized bounded chunk** at a time. Define acceptance before implementation. Do not infer that an older completed chunk should be rerun because a historical prompt in the master spec says “first” or “second session.” Current state determines the next chunk.
- Do not begin architecture selection, analog/digital block design, RTL, circuit sizing, or physical design for a block until its current literature survey and quantitative trade study are committed. No block survey has been completed yet.
- `TARGET`, `CANDIDATE`, `NEEDS_DEFINITION`, and `RESEARCH_ONLY` are not frozen product requirements. Preserve source conditions, linked IDs, unknowns and evidence class. Do not invent PDK, battery, sensor, clinical or safety values.
- Quantify noise, power, area and performance tradeoffs. Reject changes that violate approved performance or safety bounds; revise requirements through a reviewed decision when necessary.
- Keep PDKs, foundry decks, proprietary IP, keys, patient data, and licensed publications out of this public repository. Refer to restricted evidence by metadata and checksum if authorized.
- Update state, risk, traceability, assumptions, tests and reproducibility instructions for a changed chunk. Run `python3 scripts/verification/check_all.py` and any chunk-specific checks. Record what was tested and what remains unverified.
- Commit/publish reviewable work. Keep `main` as the reviewed baseline. At present the program has stopped at the CH03 **synthetic model** gate; CH04 and circuit design await explicit instruction and their own entry gates. CH03 physical battery feasibility remains on hold pending measured inputs.

The user’s current instructions always take precedence over this file.
