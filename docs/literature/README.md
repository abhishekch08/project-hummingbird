# Block literature and prior-art reviews

**Current status:** No block design survey has been completed. CH01 reviewed source sections, CH02 performed conditional resource accounting, and CH03 built a synthetic battery model. None selects a circuit/block topology or qualifies as the literature gate for CH05/CH07 or later technical block design. See `MASTER_SPEC.md` §0.7 and §59.

Before starting a technical block's topology, sizing, RTL or physical work, copy `REVIEW_TEMPLATE.md` to a dated `CHxx_<block>_YYYY-MM-DD.md` file. Record exact searches, date range, inclusion/exclusion rules and sources (DOI or primary link), separating measured from simulated/vendor claims. Normalize benchmarks to bandwidth, supply, process, channels, external components and conditions. Compare plausible families across area, volume, power, noise/quality, safety and reliability, with requirement IDs and uncertainty. Capture a gate decision and link it from the chunk and ADR, then commit before implementation. Re-search at architecture freeze if evidence ages or scope changes.

Store bibliographic metadata and concise derived comparisons in Git. Follow `docs/governance/DATA_POLICY.md` for licensed publications and proprietary source data. A survey placeholder does not pass the gate.
