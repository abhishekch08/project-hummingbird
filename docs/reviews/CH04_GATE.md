# CH04 gate: Conditional data transport and memory accounting

Date: 2026-09-25 UTC. Scope: numerical **synthetic** accounting based on the CH02 candidate/stress stream inventory. Sources: `specs/system/CH02_MODE_ASSUMPTIONS.json`, `specs/system/CH04_DATAFLOW_SCENARIOS.json`; program: `models/python/ch04_dataflow.py`; generated evidence: `reports/subsystem/CH04_DATAFLOW_SUMMARY.json` and `docs/budgets/CH04_DATA_MEMORY_REVIEW.md`.

## Decision

| Gate | Result | Evidence and boundary |
|---|---|---|
| CH04 accounting | **MODEL_PASS** | Ten CH02 modes reconciled at raw bit rate, byte-aligned sample groups, nonempty packet batches, 12 focused tests, two-stage byte conservation, packet-descriptor retention, repeated-cycle backlog and overflow reporting, conditional SRAM and NAND arithmetic, deterministic regeneration. |
| Real host, BLE, NAND, SRAM and product feasibility | **FEASIBILITY_HOLD** | No approved modes/duty, selected frame or loss policy, measured effective host/BLE/write service and wake/busy traces, proven feature semantics, qualified SRAM area/power, or vendor NAND ECC/retention/endurance. Neither a bounded invented queue nor a synthetic P/E number passes hardware feasibility. |
| Block timing/protocol/memory architecture | **NOT RUN** | No interface selection, SRAM macro, NAND chip/controller, BLE profile, clock domain, DMA RTL or circuit choice; technical block surveys and trade studies remain separate gates. CH03 physical battery feasibility is also HOLD. |

## Main conditional findings

The model computes **raw bits first** from concurrent stream widths and sample rates, then packet bytes from whole-byte sample groups, CH02 timestamp/quality assumptions, and CH04 invented header/CRC/alignment. The packet figure differs from CH02's bit-level illustrative framing because individual groups and packets are rounded. Optical CH02 rates are aggregate per photodiode across wavelength phases; the model does not multiply them again.

| Invented service path | Conditional result | What it establishes |
|---|---|---|
| Research raw, continuous 16 MHz host clock at assumed 70% payload | ~153,120 **ASIC payload B/s** added per repeated cycle | No finite FIFO sustains that synthetic route; waiting for a larger FIFO cannot repair an average-rate deficit. |
| Research raw, continuous 32 MHz host clock at the same assumed efficiency | Bounded two-cycle ASIC queue, ~210.4 KiB conditional total SRAM including declared workspace/reserve | Shows a service-rate sensitivity, **not** that an actual host supports 32 MHz or the framing/wake policy. |
| Audio, 16 MHz host then synthetic 1 Mbit/s BLE application goodput available 200 ms/s | ASIC drains, but **host staging grows ~749,424 B/s** and a hypothetical 128 KiB host staging limit is crossed | The bottleneck can move to the wireless/firmware stage; ASIC FIFO fit is not end-to-end success. |
| Research raw local NAND with hypothetical 2 MB/s write service and 100 ms/s initial busy window | Conditional ASIC queue bounded; research frame production is ~1,553,120 B/s | Queue arithmetic for this invented write trace only; write power, busy tails, ECC and bad blocks missing. |

At the same synthetic research frame rate, 4/16 **decimal Gbit** NAND labels with an assumed 80% usable fraction store only ~4.29/~17.17 minutes if acquisition continues without offload. The separately shown wear figures assume one unapproved hour of research logging per day, 2× write amplification, ideal wear leveling and a made-up 1000-cycle label; neither size holds a full hypothetical day of that recording without offload. Endurance under prior offload and recording retention are independent questions. This is a decision pressure for an approved duty/retention requirement, not a selection of storage size.

The feature-only branch produces hypothetical 16-bit features at 1 Hz per selected channel and discards original samples. Its much lower traffic cannot be used to claim that synchronized raw EEG/audio/optical evidence is preserved, nor does it validate a DSP algorithm. The 10 ms aggregation cannot bound sub-window bursts, DMA contention or wake-time variation; all numerical fits are conditional on the declared event order and service windows.

## Test and provenance record

- Hand-calculated audio and 1 Hz thermal framing, byte rounding and exact CH02 raw-rate reconciliation; source-linked framing parameters and all eight physical-input fields must be explicit.
- FIFO packet descriptors survive partial transfer; producer bytes equal delivered plus outstanding bytes in all eight scenarios. Host and BLE backlogs fail independently; intentional overloaded host and fast stress paths report growth and finite-capacity overflow.
- SRAM candidate comparison is withheld for a growing queue; NAND capacity/fill/wear calculations and batch, wake, BLE, NAND-busy sensitivities exercised. Invalid units, source tags, missing CH02 streams, unbalanced service windows, unsupported clock and physical-value formats fail closed.

Reproduce from a fresh checkout:

```sh
python3 models/python/ch04_dataflow.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch04_*.py'
python3 scripts/verification/check_all.py
git diff --check
```

## Requirement trace and unresolved decisions

| Requirements | Evidence here | Remaining acceptance |
|---|---|---|
| `SYS-0008`, `SYS-0010`, `SYS-0016` | Ten-mode raw/packet matrix, counterexample for raw-to-feature substitution, guarded average transport demand | Approved mandatory and simultaneous modes, raw-data access and actual memory bandwidth/area denominator |
| `MEM-0001`, `MEM-0002` | Burst queues, descriptors, conditional SRAM plus first synthetic FIFO/host overflow time | Real wake, flow control, on-chip SRAM macros/ECC/power and explicit loss/error timestamps |
| `MEM-0004`, `MEM-0005` | Local NAND path and 4/16 Gbit capacity/write-wear examples | Selected hierarchy, retention time, actual capacity/write amplification/ECC/bad-block policy and measured writes |
| `HIF-0001`, `HIF-0002` | Host link average rate/guard and burst queue for test clocks | Verified nRF/ASIC link timing, actual frame/CRC, sustained payload, DMA and backpressure |
| `TIM-0001`, `TIM-0004` | CH02 group timestamp bits are accounted for | Timestamp semantics, alignment and rollover/continuity through sleep in CH05 |

All requirement maturity statuses remain provisional. OI-001/002/007/012/013/014 remain open; in particular, CH04 cannot turn the optional fast-ADC stress or CH02 BIO/OPT conflict probe into a supported mode. R-003/010/013 remain open. Measured hardware profiles and owner-approved recording/offload rules must precede a physical transport, storage or SRAM verdict.

**Stop point:** CH04 model/review complete. Do not begin CH05 until separately directed; do not promote an example link clock, storage capacity or feature-only rate to a product requirement.
