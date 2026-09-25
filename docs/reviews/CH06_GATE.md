# CH06 gate: candidate register map and host protocol

Date: 2026-09-25 UTC. Entry baseline: [CH06 literature and charter PR #9](https://github.com/abhishekch08/project-hummingbird/pull/9), merged as `124ef7843b7b71464c618b7cb256368b5e53500c` before the first protocol model commit. Scope: `MASTER_SPEC.md` §§21–23, 42; [entry charter](../chunks/CH06_REGISTER_HOST.md), [dated primary survey](../literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md), [source configuration](../../specs/system/CH06_HOST_CONTRACT.json), [reference implementation](../../models/python/ch06_host.py), [generated contract](../interfaces/CH06_REGISTER_PROTOCOL.md) and [generated results](../../reports/subsystem/CH06_HOST_SUMMARY.json).

## Gate decision

| Gate | Result | Evidence and boundary |
|---|---|---|
| Literature before candidate design | PASS | Primary vendor register/SPI/DMA/errata documentation and CRC standard with applicability limits, committed and reviewed first in PR #9. No Hummingbird silicon benchmark exists. |
| Executable candidate ABI | **MODEL_PASS** | One JSON source checked for widths, register offsets/access/reset/masks and provenance; byte-exact versioned CRC32c packet encoder/decoder; bounded parser; per-epoch command ordering and immediate retry without repeating side effects; timestamp snapshot, W1C IRQ with hardware-set priority; FIFO ownership, backpressure, counted loss markers and reset discontinuity. 23 focused tests and public CI. |
| Link rate feasibility | **AVERAGE_DEFICIT at 16 MHz research; otherwise CONDITIONAL/UNKNOWN** | CH04 unframed whole groups repacked into CH06 28+4 B frames. Research requires 1,597,552 B/s and ≥21,909,285 Hz under invented 70% payload duty and 20% guard; 32 MHz is an average-only probe, not burst/energy feasibility. Fast stress needs ≥219,921,189 Hz under the same fiction. No selected safe host frequency, real chip-select/turnaround/dummy cost, sleep/wake, BLE backpressure or SRAM/DMA implementation. |
| Frozen host/ASIC ABI and physical handshake | **ABI_AND_PHYSICAL_HOLD** | Host exact die/build/errata, pins/SPI mode/clock, measured transfer traces, SRAM macro/CDC/DMA, IRQ/wake/reset/fault electrical and firmware semantics, product loss and time epoch policy, and reviewed access/security authority are missing. Numeric offsets, frame types and capacities remain **candidate** and must not be used as a production ABI or physical RTL specification. |

## Verification and reproduction

```sh
python3 models/python/ch06_host.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch06_*.py'
python3 scripts/verification/check_all.py
git diff --check
```

CH06: 23 unit cases including golden byte vector, CRC32c known check, malformed/version/type/reserved/cross-chip-select recovery, sequence wrap/reorder and duplicate, command reply/error/CRC/retry/reset, W1C/snapshot, FIFO ACK and overflow GAP, unknown physical inputs and CH04 hash reconciliation. The public suite also runs prior chapters and repository checks. CI must pass on the published commit; local test output cannot certify the hardware. The queue capacity counts **payload bytes**, while credit counts **wire bytes**. The model does not implement a DMA engine, true full-duplex SPI timing, a retained epoch across complete power loss, authenticated access, watchdog or actual interrupt pins.

## Requirement links and exit

| Provisional IDs | Model evidence | Closure for selected implementation |
|---|---|---|
| `HIF-0001/0002` | Framing, CRC, duplicate-safe retry, credit, throughput guard and explicit overflow/GAP | Measured selected host/ASIC payload and power traces across worst approved bursts; actual firmware/DMA FIFO tests. |
| `HIF-0003/0004` | Modeled READY/SESSION_BREAK status, interrupt register and reset epoch; no drive-enable register | Electrical pin/reset/wake/fault handshake, debug and authenticated command policy; threat and safety review. |
| `MEM-0001/0002/0003` | Payload-only bounded FIFO, counted loss; no SRAM selection | SRAM banking/ECC/BIST, macro leakage/area, physical FIFO capacity and fault injection. |
| `TIM-0001/0004`, `SEC-0003/0004` | 64-bit snapshot with consistency sequence, CRC integrity and boot-epoch discontinuity | CH05 physical timebase/CDC, persistent epoch semantics and authenticated safety boundary. CRC alone grants no authority. |

Open `OI-001/002/005/006/007/010/012/013/014/015`. [ADR-0003](../adr/ADR-0003_CANDIDATE_HOST_CONTRACT.md) records the proposed contract. **CH06 model scope is complete.** CH07 can begin its separate literature and numerical entry work under the user's authorization; the frozen host ABI and prior physical feasibility gates stay on hold. Stop CH07 before topology selection without approved electrode model and signal/noise/power targets.
