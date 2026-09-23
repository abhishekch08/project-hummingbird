# Repository map and artifact ownership

The tree follows `MASTER_SPEC.md` §39. Existing directories are reservations; their presence does not imply a functioning circuit or test flow. Create an artifact only when its chunk is active. Keep source and small reproducible outputs in Git; reference approved restricted evidence by checksum outside this public repository.

| Path | Responsibility | Current state / first expected use |
|---|---|---|
| `state/` | Chunk index, decisions, issues, risks, traceability, assumptions, verification status | Active CH00–CH02; update with every chunk. |
| `docs/chunks/`, `docs/reviews/`, `docs/adr/` | Bounded work records, gate decisions, architecture decisions | CH01/CH02 reviews; no circuit ADR approved. |
| `docs/literature/` | Block-specific, dated, benchmarked surveys with primary citations | Template only; required before each technical block design. |
| `docs/architecture/`, `docs/interfaces/`, `docs/budgets/` | Selected architecture, frozen contracts, unit-aware models | CH02 provisional budget only; CH03–CH06 produce next artifacts. |
| `docs/package/`, `docs/safety/`, `docs/inputs/`, `docs/governance/` | Package/electrode decisions, safety evidence, external input requests, public repo policy | Input and policy files exist; numeric safety/package signoff pending. |
| `specs/system/` | Machine-readable scenario definitions and subsequently approved system requirements | CH02 JSON assumptions; not silicon requirements. |
| `specs/{biosignal,eda_bioz,electrochem,optical,thermal,audio,adc_dac,digital,pmic,memory,dft}/` | Future block specifications, each traced to requirements and literature | Reserved until authorized chunk. |
| `models/python/`, `models/{matlab_octave,veriloga,rnm,spice,sensor_models}/` | Executable golden, behavioral and sensor models | CH02 Python scenario model only. |
| `reports/{block,subsystem,fullchip,signoff}/` | Reproducible results, inputs, tool metadata and evidence class | CH02 generated JSON in `subsystem/`; no signoff report. |
| `verification/{unit,formal,uvm,ams,regressions,coverage}/` | Tests and checks that can fail on a meaningful defect | CH02 unit tests only; future verification folders reserved. |
| `scripts/{setup,simulation,synthesis,verification,reporting}/` | Reproducible tool orchestration and repository checks | Standard-library repository checks in `verification/`. |
| `rtl/`, `analog/`, `pmic/`, `firmware/` | Synthesizable logic, circuits, power design, firmware | Empty by design until reviewed specification and required survey. |
| `physical/`, `constraints/`, `synthesis/`, `sta/`, `pnr/`, `pex/`, `drc/`, `lvs/`, `emir/`, `reliability/` | Process-specific implementation and signoff | Reserved. No foundry PDK or licensed decks in this public repository. |
| `tapeout/` | Release manifests, independently approved signoff evidence and immutable hashes | Reserved; no release candidate. |

**Naming:** use `CHxx_...` for chunk artifacts, `ADR-xxxx_...` for decisions, and stable subsystem requirement IDs from the register. Date each literature review. Generated reports identify their source configuration and command; edit the source, regenerate, and review the diff rather than manually changing generated numbers.
