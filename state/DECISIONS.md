# Decisions

| ID | Status | Decision and scope | Evidence / revisit trigger |
|---|---|---|---|
| ADR-0001 | Adopted process policy | Preserve candidate, research and process statuses; require owner evidence before promoting a technical target or product mode. No circuit architecture selected. | `docs/adr/ADR-0001_REQUIREMENT_MATURITY.md`; revisit after CH03–CH04 and product review. |
| ADR-0002 | Proposed conditional timebase study | Compare LF retained owner plus awake fine capture with a continuous 1 MHz counter; both are synthetic and neither is a physical selection. | `docs/adr/ADR-0002_CONDITIONAL_TIMEBASE.md`; revisit with qualified clock/IMU, timing-accuracy owners, CDC/RDC and energy data. |
| ADR-0003 | Proposed candidate host contract | Versioned byte-exact register/frame/FIFO model, ACK commit, CRC integrity and counted loss; no host/ASIC hardware ABI freeze. | `docs/adr/ADR-0003_CANDIDATE_HOST_CONTRACT.md`; revisit with selected host revision/errata, measured bursts, SRAM/CDC and security approval. |

Record each future architectural decision as a numbered ADR under `docs/adr/` with quantitative alternatives, requirement IDs, risk and verification. Open decisions are listed in `state/OPEN_ISSUES.md`; an unchosen option in the master spec does not constitute an ADR.
