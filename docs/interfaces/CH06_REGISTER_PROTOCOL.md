# CH06 candidate register and host protocol contract

Generate with `python3 models/python/ch06_host.py --write`; verify `--check`. Input `specs/system/CH06_HOST_CONTRACT.json` SHA-256 `148a85c7b1846d541dfa682fa89c6b38b8c54cd21813ad87ce536b1499e24e4b` and CH04 report SHA-256 `85353d4fa9d5a8c42f1d1a387ab90b1ef7a75dc8734b4981434997dac367e087`. The [CH06 host survey](../literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md) was merged before model work. **Proposed ABI, not frozen hardware/firmware.** All address, size, clock and frame choices are candidate fixtures.

## Byte-exact packet candidate

Frame = 28-byte little-endian header, 0–1024 B payload, then 4-byte CRC-32c. Ordered fields: magic `0xC35A` (u16), major (u8=1), type (u8), flags (u16: bit0 time-valid, bit1 gap), payload length (u16), sequence (u32), modeled boot epoch (u32), sample time in µs (u64), reserved zero (u32). CRC-32c reflected polynomial `0x82F63B78`, init/final XOR `0xFFFFFFFF`; covers header+payload; append little-endian. Check vector `123456789` → `0xe3069283`. Types: DATA=1, GAP=2 (u32 nonzero lost record count), STATUS=3, READ=16 (u32 aligned offset), WRITE=17 (u32 offset+u32 value), ACK=18 (u32 sequence), REPLY=19 (u32 status 0 + u32 result), ERROR=20 (u32 code 1 + u32 zero). REPLY/ERROR echo the command sequence and epoch. Unknown version/type/flags/reserved, illegal lengths, bad CRC and truncated frames fail. Parser may receive byte chunks **within one chip select**; an unfinished frame at CS end is discarded. CRC detects corruption but cannot authenticate a command; there is no body-drive enable in this map.

Frame sequence increments modulo 2³² **per emitted frame**. Host negotiates boot epoch before accepting frame sequence; duplicate sequence must contain identical bytes, a gap or reordering is reported. Data events lost before a frame is made are represented by the next GAP marker with a count. A soft-reset discontinuity starts a new modeled boot epoch; uniqueness through full power loss is unresolved. An unacknowledged frame remains in FIFO and a retry returns identical bytes. FIFO data is consumed only by ACK of the head sequence and matching epoch. A CRC-successful transfer alone is **not** a commit. Credit counts total wire bytes, including header/CRC.

Host commands have their own per-epoch sequence space and receive byte-identical replies for a retry of the **immediately previous** identical command; side effects execute once. A malformed command or changed epoch gets no reply, whereas a valid but illegal access gets ERROR and sets BAD_COMMAND. READ returns the register value; WRITE returns zero; ACK returns the acknowledged frame wire-byte count. An older replay, authenticated origin, clocking of full-duplex reply and long-term command history remain unresolved. REPLY/ERROR are control frames and cannot carry sensor time.

## Candidate 32-bit register map

| Register | Offset | Access | Reset | Valid mask |
|---|---:|---|---:|---:|
| `DEVICE_ID` | `0x000` | RO | `0x484D4231` | `0xFFFFFFFF` |
| `ABI_VERSION` | `0x004` | RO | `0x00010000` | `0xFFFFFFFF` |
| `STATUS` | `0x008` | RO | `0x00000001` | `0x0000003F` |
| `IRQ_ENABLE` | `0x00C` | RW | `0x00000000` | `0x0000003F` |
| `IRQ_PENDING` | `0x010` | RW1C | `0x00000000` | `0x0000003F` |
| `TIME_SNAPSHOT` | `0x014` | WO | `0x00000000` | `0x00000001` |
| `TIME_LO` | `0x018` | RO | `0x00000000` | `0xFFFFFFFF` |
| `TIME_HI` | `0x01C` | RO | `0x00000000` | `0xFFFFFFFF` |
| `TIME_SEQ` | `0x020` | RO | `0x00000000` | `0xFFFFFFFF` |
| `FIFO_BYTES` | `0x024` | RO | `0x00000000` | `0xFFFFFFFF` |
| `LOSS_COUNT` | `0x028` | RO | `0x00000000` | `0xFFFFFFFF` |
| `BOOT_EPOCH` | `0x02C` | RO | `0x00000001` | `0xFFFFFFFF` |

All reads/writes are one aligned 32-bit word. Unmapped/unaligned, reserved-bit, illegal access or unsupported command fails. `STATUS`: READY, OVERFLOW, CRC_ERROR, BAD_COMMAND, TIME_INVALID, SESSION_BREAK bits 0–5; sticky until modeled reset. `IRQ_ENABLE` masks `IRQ_PENDING`. `IRQ_PENDING` is write-one-to-clear, with a simultaneous hardware set winning over software clear. Writing exactly 1 to `TIME_SNAPSHOT` latches the 64-bit time and increments `TIME_SEQ`; reading LO and HI afterward cannot tear until the next snapshot. A host can bracket LO/HI with SEQ and retry if another software actor snapshots concurrently. Dynamic FIFO_BYTES counts payload only, distinct from wire credits or SRAM capacity. No external wake/reset/IRQ electrical timing or actuator permission is approved.

## Average throughput sensitivities

Reframe each CH04 *unframed whole sample group* per stream into ≤1024-byte payloads without splitting a group; aggregate counts over one second. CH04's alternative framed rate already has its **own** header/CRC and is not added again. Illustrative SCK bound = `ceil(8 × CH06 wire B/s × 1.2 / 0.7)`, with invented full-duty availability and no separate measured CS or wake cost. `AVERAGE_ONLY` is no timed-queue or physical pass.

| CH02 mode | Group B/s | Whole-group frames/s | New CH06 wire B/s | Minimum SCK Hz (synthetic) | 16/32 MHz probe |
|---|---:|---:|---:|---:|---|
| `audio` | 772216 | 756 | 796408 | 10922167 | AVERAGE_ONLY / AVERAGE_ONLY |
| `cardiovascular` | 44916 | 47 | 46420 | 636618 | AVERAGE_ONLY / AVERAGE_ONLY |
| `daily_health` | 4600 | 7 | 4824 | 66158 | AVERAGE_ONLY / AVERAGE_ONLY |
| `deep_sleep` | 0 | 0 | 0 | 0 | AVERAGE_ONLY / AVERAGE_ONLY |
| `optical_spectroscopy` | 104760 | 104 | 108088 | 1482350 | AVERAGE_ONLY / AVERAGE_ONLY |
| `research_fast_stress` | 15548240 | 15240 | 16035920 | 219921189 | AVERAGE_DEFICIT / AVERAGE_DEFICIT |
| `research_raw` | 1548240 | 1541 | 1597552 | 21909285 | AVERAGE_DEFICIT / AVERAGE_ONLY |
| `resource_conflict_probe` | 138000 | 136 | 142352 | 1952256 | AVERAGE_ONLY / AVERAGE_ONLY |
| `sleep_neuroscience` | 203216 | 202 | 209680 | 2875612 | AVERAGE_ONLY / AVERAGE_ONLY |
| `sweat_biochemistry` | 2504 | 5 | 2664 | 36535 | AVERAGE_ONLY / AVERAGE_ONLY |

Latency, burst peaks, BLE, contention, silicon clock power, SRAM and DMA energy remain unverified; see CH04 timed queue and `OI-013`. Nordic engineering-B host errata require **part/build-specific** qualification before implementation. No selected SPI mode, pin, safe SCK or software ABI is approved. [CH06 gate](../reviews/CH06_GATE.md): MODEL_PASS / ABI_AND_PHYSICAL_HOLD.
