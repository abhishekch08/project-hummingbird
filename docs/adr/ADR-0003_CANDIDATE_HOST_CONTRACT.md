# ADR-0003: Candidate register and host transport contract

Status: **proposed model contract, not a frozen ABI**. Date: 2026-09-25 UTC. Requirements `HIF-0001`–`HIF-0004`, `MEM-0001`–`MEM-0003`, `TIM-0001/0004`, `SEC-0003/0004`; issue `OI-013` chiefly. [Literature](../literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md), [generated contract](../interfaces/CH06_REGISTER_PROTOCOL.md), [gate](../reviews/CH06_GATE.md).

## Decision context and alternatives

CH04 research raw scenario supplies 1,548,240 unframed sample-group B/s. To make errors and retries testable without a selected SPI peripheral, use an illustrative single-lane, register plus framed FIFO interface. Its 1024 B maximum payload and 28 B header + 4 B CRC cost 49,312 B/s on these CH04 groups, totaling 1,597,552 B/s. At an invented 70% available wire duty with a 20% headroom guard, ≥21.91 MHz is the average threshold. A 16 MHz clock cannot pass this synthetic case; a 32 MHz clock clears only the average arithmetic. The fast stress probe would require ≥219.92 MHz and is not a qualified operating mode.

| Candidate alternative | Benefit | Cost / missing evidence |
|---|---|---|
| Register access plus framed FIFO and explicit ACK (modeled) | Byte-exact packet integrity, error accounting and host backpressure; atomic time snapshot; duplicate immediate command retry. | 32 B overhead per frame; no measured full-duplex timing, SRAM or physical link; CRC cannot authorize control. |
| Host reads raw unframed stream | Less packet overhead in ideal transfer. | No per-record integrity/sequence/boot/loss reporting until added elsewhere; clock and bus capacity still unknown. |
| Larger host-memory bursts and/or wider link | Could lower per-group overhead or support research stress. | Host part/revision support, pin count, clock/power and DMA/SRAM unavailable; cannot select a specific variant. |
| BLE direct egress | Avoids separate recording memory only when goodput suffices. | CH04's hypothetical BLE path accumulates backlog in high-rate modes; measured airtime/coexistence needed. |

Keep a **versioned proposed** register map and byte-level model. Separate command and data sequence spaces within one modeled epoch. Header timestamps are valid only with a flag, and unknown time is zero. Incremental parser drops an unfinished frame on chip-select release. Valid but illegal commands return ERROR; CRC failures get no reply. ACK of a previously viewed head frame is the only consume operation. Counting loss with a GAP marker preserves observability, but an unknown power-cycle epoch may still cause ambiguity. Physical pins, firmware and the production ABI are undecided.

Revisit when host exact silicon revision/errata and firmware, verified pins and SCK/mode/CS timing, measured worst-burst throughput and energy, full reset and wake behavior, actual SRAM DMA/CDC implementation, and the safety/security and timestamp owners provide input. Evaluate against CH04's timed queue and CH03's battery model before freeze. If constraints differ, revise the JSON, generated contract, tests and downstream implementations through a new review. No PHY or register block RTL is approved here.
