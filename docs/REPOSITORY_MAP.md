# Repository map and artifact ownership

The tree follows `MASTER_SPEC.md` §39. Existing directories are reservations; their presence does not imply a functioning circuit or test flow. Create an artifact only when its chunk is active. Keep source and small reproducible outputs in Git; reference approved restricted evidence by checksum outside this public repository.

| Path | Responsibility | Current state / first expected use |
|---|---|---|
| `state/` | Chunk index, decisions, issues, risks, traceability, assumptions, verification status | CH00–CH06 limited gates; CH07 resistor and complex numerical subgates paused at topology; update with every chunk. |
| `docs/chunks/`, `docs/reviews/`, `docs/adr/` | Bounded work records, gate decisions, architecture decisions | CH01–CH06 limited reviews; ADR-0002/0003 proposed; no physical clock/circuit or host ABI approved. |
| `docs/literature/` | Block-specific, dated, benchmarked surveys with primary citations | CH05 and CH06 surveys merged before each model; CH07 biopotential survey merged before numerical model. Later blocks need separate reviews. |
| `docs/architecture/`, `docs/interfaces/`, `docs/budgets/` | Selected architecture, frozen contracts, unit-aware models | CH02 scenario, CH03 energy, CH04 data/memory, CH05 conditional timing and CH07 resistor/complex-source budgets; CH06 candidate host/register contract is not frozen. |
| `docs/package/`, `docs/safety/`, `docs/inputs/`, `docs/governance/` | Package/electrode decisions, safety evidence, external input requests, public repo policy | CH07 electrode/quality collection protocol and other input/policy files exist; measurements and safety/package signoff pending. |
| `specs/system/` | Machine-readable scenario definitions and subsequently approved system requirements | CH02 candidate modes and CH03–CH06 synthetic inputs; not silicon requirements. |
| `specs/{biosignal,eda_bioz,electrochem,optical,thermal,audio,adc_dac,digital,pmic,memory,dft}/` | Future block specifications, each traced to requirements and literature | `biosignal/` contains resistor and complex-source **synthetic** CH07 inputs but no frozen block spec; other folders reserved. |
| `models/python/`, `models/{matlab_octave,veriloga,rnm,spice,sensor_models}/` | Executable golden, behavioral and sensor models | CH02 scenario, CH03 energy, CH04 dataflow, CH05 timing, CH06 host and CH07 resistor/complex numerical models; other folders reserved. |
| `reports/{block,subsystem,fullchip,signoff}/` | Reproducible results, inputs, tool metadata and evidence class | CH02–CH06 generated JSON in `subsystem/`, CH07 resistor and complex sensitivity in `block/`; no signoff report. |
| `verification/{unit,formal,uvm,ams,regressions,coverage}/` | Tests and checks that can fail on a meaningful defect | CH02–CH07 Python unit tests, including five complex-source checks; future verification folders reserved. |
| `scripts/{setup,simulation,synthesis,verification,reporting}/` | Reproducible tool orchestration and repository checks | Standard-library repository checks in `verification/`. |
| `rtl/`, `analog/`, `pmic/`, `firmware/` | Synthesizable logic, circuits, power design, firmware | `rtl/timestamp/` contains an **uncompiled illustrative** continuous-counter SV reference after CH05 survey; all other design folders reserved. |
| `physical/`, `constraints/`, `synthesis/`, `sta/`, `pnr/`, `pex/`, `drc/`, `lvs/`, `emir/`, `reliability/` | Process-specific implementation and signoff | Reserved. No foundry PDK or licensed decks in this public repository. |
| `tapeout/` | Release manifests, independently approved signoff evidence and immutable hashes | Reserved; no release candidate. |

**Naming:** use `CHxx_...` for chunk artifacts, `ADR-xxxx_...` for decisions, and stable subsystem requirement IDs from the register. Date each literature review. Generated reports identify their source configuration and command; edit the source, regenerate, and review the diff rather than manually changing generated numbers.
