# CH04: Conditional data rate, queue and memory review

**Evidence class:** SYNTHETIC_CONDITIONAL. Eight CH02 modes are candidates; two are intentional stress probes. No product recording duty, protocol, real link throughput, BLE goodput or memory component is approved. A bounded synthetic queue is not a hardware PASS.

CH04 input SHA-256 `32c6aceec269b8978ccf8caaf99afdd5a1900afb978037b779ac2e2af2a12cf5`; CH02 source SHA-256 `c3043a250688a9e7a7901a26cc1956137250e86269150284ed6ae9053b688e67`; CH02 report SHA-256 `22189aff4432c4cd94e306dee8f5fbcf65a84adaae41f83b841436db80e937c2`. Regenerate with `python3 models/python/ch04_dataflow.py --write`; verify with `--check`.

## Framing and conservation rules

- Raw stream `bit/s = channels × effective sample groups/s × nominal bits/channel`. CH02 optical rates are *aggregate per photodiode across wavelengths*. The frame encodes one whole-byte sample group containing all channel words, 8 quality bits per channel, 64 timestamp bits per group and 8 extra optical wavelength bits per group (the last three values come from CH02). The scenario additionally uses 4 B header + 2 B CRC and aligns each nonempty batch to 4 B. The header hypothetically carries stream ID and sequence/length; its format is not selected.
- Frames arrive at each 10 ms boundary; drain existing FIFO first, then enqueue arriving frames. A partially drained ASIC packet retains its 16 B descriptor. For host→BLE, the host stage is an ideal byte queue; BLE drains existing host bytes before host transfer and new ASIC arrivals. Two repetitions expose sustained queue growth. The finite-horizon peak is never a valid sustainable SRAM size for a growing queue. This 10 ms aggregation cannot bound shorter simultaneous bursts or wake jitter.
- At an illustrative 70% host payload efficiency, the *continuous-mode average* single-data-line clock target is `ceil(CH04 packet bit/s × 1.2 / 0.7)`; the timed queue separately captures the stated wake gaps. Service credits are rounded down to whole bytes per window, losing less than one byte of capacity per service window. Byte rounding and packet overhead explain differences from CH02 framed figures; neither is a strict protocol upper bound. The separately named feature-only sensitivity outputs one invented 16-bit feature/channel/second and **discards all original raw samples**. It cannot replace raw research/clinical evidence.

## One-second continuous-mode accounting

| CH02 mode | Class | Raw Mb/s | CH02 framed Mb/s | CH04 packed+packet Mb/s | Frames/s | Illustrative continuous-mode guarded host clock | Feature-only Mb/s |
|---|---|---:|---:|---:|---:|---:|---:|
| `deep_sleep` | candidate | 0.000 | 0.000 | 0.000 | 0 | none | 0.000 |
| `daily_health` | candidate | 0.014 | 0.037 | 0.050 | 233 | 0.086 MHz | 0.001 |
| `sleep_neuroscience` | candidate | 0.378 | 1.626 | 1.648 | 401 | 2.825 MHz | 0.001 |
| `cardiovascular` | candidate | 0.166 | 0.359 | 0.378 | 301 | 0.648 MHz | 0.001 |
| `sweat_biochemistry` | candidate | 0.007 | 0.020 | 0.029 | 143 | 0.050 MHz | 0.001 |
| `optical_spectroscopy` | candidate | 0.490 | 0.838 | 0.850 | 210 | 1.457 MHz | 0.001 |
| `audio` | candidate | 2.318 | 6.178 | 6.195 | 301 | 10.621 MHz | 0.001 |
| `research_raw` | candidate | 6.385 | 12.386 | 12.425 | 610 | 21.300 MHz | 0.002 |
| `research_fast_stress` | stress | 38.385 | 124.386 | 124.431 | 710 | 213.311 MHz | 0.002 |
| `resource_conflict_probe` | stress | 0.624 | 1.104 | 1.123 | 300 | 1.925 MHz | 0.001 |

The `resource_conflict_probe` is intentionally BIO/OPT converter-infeasible in CH02; its rate row is arithmetic only. Feature-only numbers are an invented output-profile sensitivity, not lossless compression, quality equivalence, or permission to stop storing raw samples.

## Timed queues and SRAM

| Case and route | Repeated-cycle queue | Growth per cycle | Peak ASIC FIFO incl. descriptors | Peak host staging | First 512 KiB ASIC overflow | First 128 KiB host overflow | Total SRAM if bounded |
|---|---|---:|---:|---:|---|---|---:|
| `daily_host_wake` (host) | BOUNDED_IN_SYNTHETIC_CYCLE | 0.0 KiB/s | 2.1 KiB | n/a | none in 2 s | n/a | 194.5 KiB |
| `audio_host_wake` (host) | BOUNDED_IN_SYNTHETIC_CYCLE | 0.0 KiB/s | 159.8 KiB | n/a | none in 2 s | n/a | 383.8 KiB |
| `research_host_16m` (host) | REPEATED_CYCLE_GROWTH | 149.5 KiB/s | 314.7 KiB | n/a | none in 2 s | n/a | no finite buffer |
| `research_host_32m` (host) | BOUNDED_IN_SYNTHETIC_CYCLE | 0.0 KiB/s | 15.3 KiB | n/a | none in 2 s | n/a | 210.4 KiB |
| `fast_stress_host_64m` (host) | REPEATED_CYCLE_GROWTH | 9720.6 KiB/s | 19510.2 KiB | n/a | 50 ms | n/a | no finite buffer |
| `daily_host_ble` (host_ble) | BOUNDED_IN_SYNTHETIC_CYCLE | 0.0 KiB/s | 0.2 KiB | 5.0 KiB | none in 2 s | none in 2 s | 192.2 KiB |
| `audio_host_ble` (host_ble) | REPEATED_CYCLE_GROWTH | 731.9 KiB/s | 7.6 KiB | 1456.1 KiB | none in 2 s | 180 ms | no finite buffer |
| `research_local_nand` (local_nand) | BOUNDED_IN_SYNTHETIC_CYCLE | 0.0 KiB/s | 167.9 KiB | n/a | none in 2 s | n/a | 393.5 KiB |

ASIC total SRAM uses `ceil((peak packet bytes + outstanding descriptor bytes) × 1.2) + 128 KiB workspace + 64 KiB other reserve`. The 512 KiB/2 MiB bounds in §21 are provisional. BLE staging is **additional host memory** and is not included in ASIC SRAM. Any growing ASIC *or host* queue makes the route unsustainable under this repeated synthetic service profile, even if it fits for the first two seconds. Overflow is reported, not silently dropped; actual loss/flow-control semantics need CH06/CH19.

## Synthetic sensitivities

| Changed assumption | Cycle status | Peak ASIC FIFO | Peak host staging |
|---|---|---:|---:|
| audio batch 10→20 ms (synthetic) | BOUNDED_IN_SYNTHETIC_CYCLE | 166.7 KiB | n/a |
| audio host unavailable 200→300 ms (synthetic) | BOUNDED_IN_SYNTHETIC_CYCLE | 235.9 KiB | n/a |
| daily BLE available goodput 1,000,000→100,000 bit/s (synthetic) | REPEATED_CYCLE_GROWTH | 0.2 KiB | 8.5 KiB |
| research NAND busy 100→300 ms (synthetic) | REPEATED_CYCLE_GROWTH | 608.3 KiB | n/a |

## Local NAND conditional projection

Packed research-raw frames are assumed to be written directly to a local candidate NAND, with **no simultaneous host/BLE duplicate route**. This storage example assumes 1 hour/day of the *unapproved* raw-research mode, 80% usable logical capacity, packed 2048 B pages, 2× write amplification, ideal even wear and a **hypothetical** 1000 P/E cycle label. A page is not padded separately for every stream packet.

| Nominal NAND | Usable example | Filled by continuous research mode | Example one-day capture fits without offload | Example equivalent P/E cycles/day | Hypothetical P/E days if offloaded |
|---:|---:|---:|---|---:|---:|
| 4 Gbit | 400 MB | 4.29 min | no | 27.956 | 36 |
| 16 Gbit | 1600 MB | 17.17 min | no | 6.989 | 143 |

A modeled fill time does not imply a successful log: sustained write bandwidth, busy-window backlog, controller ECC, bad blocks, retention, power and offload policy have no measured evidence. The hypothetical P/E arithmetic assumes prior offload and ideal wear leveling; real storage endurance is unknown.

## Gate

**MODEL_PASS** means deterministic packet/byte accounting, two-stage queue conservation, failures and tested sensitivities. **FEASIBILITY_HOLD** applies to approved modes, real host/BLE/NAND rate, SRAM area/power, buffer-loss policy, NAND endurance and any claim that feature extraction preserves needed raw information. CH03 physical battery feasibility also remains on hold. No technical block topology or timing architecture was selected.

Missing evidence: `asic_sram_macro_area_power_retention_and_yield`; `confirmed_sample_timing_and_processing_semantics`; `measured_ble_application_goodput_and_airtime`; `measured_host_link_payload_wake_and_flow_control`; `measured_memory_write_busy_and_power`; `owner_approved_modes_and_recording_duty`; `qualified_memory_capacity_endurance_ecc_and_retention`; `selected_packet_timestamp_crc_and_loss_policy`. See `docs/reviews/CH04_GATE.md` and `docs/inputs/REQUIRED_INPUTS.md`. Stop at CH04; CH05 needs its own kickoff.
