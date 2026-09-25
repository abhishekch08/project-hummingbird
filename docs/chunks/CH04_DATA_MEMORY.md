# CH04: System data rate, queues and memory feasibility

Status: **synthetic model complete; physical/product feasibility HOLD**. Date: 2026-09-25 UTC. Input baseline: CH03 merged on `main` as PR #5 (`b67dbb5bc352c125dae7160dcce38dc4e110b5b5`). CH03's physical feasibility remains on hold.

## Scope and decision boundary

Turn the eight CH02 candidate modes and two named stress probes into reproducible raw, sample-record and packet byte rates. Model time-aligned producer bursts, ASIC FIFO occupancy, a host transport and optional second BLE queue, or a local NAND write queue. Quantify SRAM needed for the FIFO plus separately declared workspace and reserve. Project NAND fill time and illustrative write wear for the master spec's 4/16 Gbit labels. Expose host clock/payload and BLE egress requirements without asserting a device capability.

CH04 is **system accounting**, not a choice of SRAM macro, NAND part, host protocol, wireless setting, DMA microarchitecture or product mode. CH05 timing, CH06 protocol, CH19 DMA, CH21 memory design and technical block literature surveys have separate gates. CH03's invented battery cycle cannot supply a recording duty factor. No exact host, BLE, NAND or product-throughput PASS is possible without measurements and approved modes.

## Inputs and linked requirements

- `MASTER_SPEC.md` §§14, 17, 21–23, 37, 42, 56–57; CH02 stream/mode config and report; CH03 gate; `state/REQUIREMENTS_TRACEABILITY.csv`; `docs/inputs/REQUIRED_INPUTS.md`.
- Trace `SYS-0008`, `SYS-0010`, `SYS-0016`, `MEM-0001`, `MEM-0002`, `MEM-0004`, `MEM-0005`, `HIF-0001`, `HIF-0002`, `TIM-0001` and `TIM-0004`; retain OI-001/002/007/012/013/014. IDs and statuses remain provisional.
- CH02 rates are assumed *aggregate samples per channel per second*; optical rate spans its wavelength phases. Byte packing, ID, packet overhead, batching, CRC, host wake, NAND stalls and radio egress require separate explicit CH04 assumptions. Unknown mandatory physical/product inputs stay null.
- Data routes are separate experiments; logging and live transmission are not implicitly simultaneous. Daily logging/wear figures, if calculated, must state a hypothetical duration and must not be presented as product duty.

## First-principles calculation and failure policy

1. Raw rate per stream is `channels × sample_rate × bits_per_channel`. One sample group packs all channel words, channel quality flags, group timestamp and optical phase ID into whole bytes. Each nonempty batch adds explicitly sized packet header/CRC and alignment; count slow streams only when they produce a sample.
2. At each declared batch boundary, drain **preexisting** backlog using only the available service window, then enqueue the just-produced batch. For BLE routes, drain the existing host queue, move available ASIC bytes over the host link into it, then enqueue new sensor packets into the ASIC. Track peak occupancy *after* arrivals, including descriptors for packets still in the ASIC FIFO. Measure the end-of-cycle backlog over repeated cycles; positive growth means no finite buffer can sustain the repeated scenario.
3. Compare `ceil(peak_FIFO × (1 + margin)) + workspace + reserve` with provisional 512 KiB and 2 MiB SRAM labels. A finite-horizon buffer for a growing queue is **not** called feasible. Log the first modeled overflow time for any illustrative capacity rather than dropping data silently.
4. Local NAND projections distinguish logical packet bytes, write amplification, usable capacity, fill time and hypothetical P/E cycles. Byte throughput, wear, ECC, bad blocks, energy and retention are different constraints. No real part's endurance or power is assumed.

## Outputs and acceptance

| Artifact | Required evidence |
|---|---|
| `specs/system/CH04_DATAFLOW_SCENARIOS.json` | Source-linked packet/batch, service-window, SRAM and NAND assumptions; physical/product unknown inventory |
| `models/python/ch04_dataflow.py` | Deterministic standard-library model; input checks, CH02 raw reconciliation, packet sizes, bounded/unbounded queue decisions |
| `verification/unit/test_ch04_dataflow.py` | Hand-calculated group/packet counts, rounding, sleep burst, packet descriptor retention, BLE second-stage stall, overload and overflow tests |
| `reports/subsystem/CH04_DATAFLOW_SUMMARY.json`, `docs/budgets/CH04_DATA_MEMORY_REVIEW.md` | Regenerated per-mode and per-case results, framing/queue/wear sensitivities, assumptions and known unknowns |
| `docs/reviews/CH04_GATE.md`, `state/` | Separate numerical MODEL_PASS versus physical/product FEASIBILITY_HOLD, tests and next stop point |

The model must reject invalid units/ranges, missing CH02 modes/streams, nonintegral service windows, impossible frame shapes and unknown physical-input formats. Regression must include CH00–CH03 checks, CH04 report freshness and meaningful CH04 failure cases. Publish the review and merge only after CI succeeds. **Stop at CH04; do not begin CH05 or block architecture.**

## Results and stop point

The input, source, 12 focused tests and deterministic reports exist at the paths above. The `docs/reviews/CH04_GATE.md` decision is MODEL_PASS for conditional accounting and FEASIBILITY_HOLD for real throughput, loss handling, memory fit, NAND endurance and product duty. An invented host or radio speed must not be treated as a device specification. `python3 scripts/verification/check_all.py` runs all public gates. CH05 is paused until separately requested.
