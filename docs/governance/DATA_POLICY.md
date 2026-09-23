# Public repository data and reproducibility policy

- Commit public-source code, configuration, synthetic inputs, small reproducible results, URLs/DOIs, review records, tool versions, and checksums needed to reproduce a conclusion.
- Do not commit foundry PDKs/decks, licensed libraries or macros, proprietary die drawings, credentials, signing keys, raw personal/health data, unpublished third-party papers, or confidential vendor pricing. The ignore file is a guard against accidents, not a security boundary.
- In public literature reviews, store citations and derived comparisons with conditions; link to the authorized publication instead of copying a restricted PDF.
- Mark evidence **assumed**, **calculated**, **simulated**, **measured**, or **independently reviewed**. Preserve units, corner, sample rate, sensor/source conditions, seed and tool version. A target remains provisional until its validation gate approves it.
- Before pushing, inspect staged paths with `git diff --cached --name-only` and `git diff --cached --check`. Never rely on private local files that a fresh checkout cannot reproduce.
- If restricted engineering data later becomes necessary, record only a non-sensitive identifier, access owner, version and cryptographic hash in this public repo; agree a separate approved access process. Do not include a private URL or token.
