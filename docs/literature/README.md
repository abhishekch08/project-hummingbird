# Block literature and prior-art reviews

**Current status:** The [dated CH05 timebase/CDC survey](timing/2026-09-25_STATE_OF_ART_REVIEW.md) and quantitative trade study were merged as PR #7 **before** CH05's model. It permits only a conditional CH05 timebase study and explicitly holds the physical oscillator/clock topology; it does not satisfy CH07 or any later block-specific literature gate. CH01–CH04 had no circuit survey. See `MASTER_SPEC.md` §0.7 and §59.

Before starting a technical block's topology, sizing, RTL or physical work, use `REVIEW_TEMPLATE.md` for a dated block review. Record exact searches, date range, inclusion/exclusion rules and sources (DOI or primary link), separating measured from simulated/vendor claims. Normalize benchmarks to bandwidth, supply, process, channels, external components and conditions. Compare plausible families across area, volume, power, noise/quality, safety and reliability, with requirement IDs and uncertainty. Capture a gate decision and link it from the chunk and ADR, then commit before implementation. Re-search at architecture freeze if evidence ages or scope changes.

Store bibliographic metadata and concise derived comparisons in Git. Follow `docs/governance/DATA_POLICY.md` for licensed publications and proprietary source data. A survey placeholder does not pass the gate.
