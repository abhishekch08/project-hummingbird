# CH05 clock/timestamp state-of-the-art review

Date: 2026-09-25 UTC. Scope: CH05 system timebase, oscillator class, sleep continuity, clock crossings, trigger capture and IMU alignment. Requirement IDs: `TIM-0001`–`TIM-0007`, `TIM-0009`, `SYS-0010`. This review is the prerequisite to CH05 conditional architecture work; it **does not** approve a clock circuit or satisfy subsequent block-specific reviews.

## Search and evidence method

Searched primary IEEE author manuscripts/university publication records (queries: *measured low-power RC oscillator 20 kHz 700 kHz ppm*), OpenTitan design documentation (*always-on timer clock manager*), AMD CDC macro documentation (*single bit handshake asynchronous FIFO*) and ST primary IMU documentation (*FIFO timestamp internal frequency*), accessible 2026-09-25. Excluded secondary comparisons, inaccessible full-text metrics, unverified paper snippets and claims without test conditions. Electrical figures below come from measured author reports only; reference implementations/vendor data occupy a separate table. No proprietary paper, vendor PDF or licensed content is copied into this repository.

## Primary source register and measured-silicon benchmarks

| ID | Primary source / evidence class | Reported measurement and conditions | Limits for this project |
|---|---|---|---|
| P1 | [Mirchandani & Shrivastava, IEEE TCAS-I 2023, DOI:10.1109/TCSI.2023.3261182](https://pmc.ncbi.nlm.nih.gov/articles/PMC10361407/), open author manuscript; measured 130 nm CMOS | RC oscillator nominal 20 kHz; 254 nW at 1 V low-power and 345 nW high-stability; measured four-chip temperature coefficient 21–49 ppm/°C from −20 to 100 °C, once trimmed; reported 5.5%/V average supply sensitivity from 0.9–1.3 V. | Its 50 µs nominal tick cannot by itself resolve ≤1 µs. Temperature coefficient is **not** an absolute ppm bound and the published power is not an ASIC budget for this design. |
| P2 | [Xu et al., ESSCIRC 2023, DOI:10.1109/ESSCIRC59616.2023.10268752](https://researchportal.hkust.edu.hk/en/publications/a-125-ppmc-1086-nwkhz-relaxation-oscillator-with-clock-gated-disc/), author institution record of measured 22 nm prototype | 700 kHz, 760 nW, 12.5 ppm/°C measured from −40 to 85 °C; 1.086 nW/kHz reported. | ~1.429 µs tick; still above the candidate 1 µs tick, and process/voltage/clock-load differences prohibit importing its power into Hummingbird. Sample size and area not reported in accessible abstract. |

These are **independent demonstration chips**, not normalized head-to-head tests: P1 and P2 differ in process, supply, temperature, circuit and reporting conditions. No selected foundry or exact Hummingbird oscillator was measured; no on-die clock power, area, PVT corners or phase noise can be inferred by scaling either result. No primary measured-silicon comparison of a complete Hummingbird-like multimodal timestamp chain was located; this is an evidence gap, not a zero-cost assumption.

## Reference implementations and manufacturer documents (not measured ASIC benchmarks)

| ID | Source | Finding and implication |
|---|---|---|
| V1 | [OpenTitan AON timer theory](https://opentitan.org/book/hw/ip/aon_timer/doc/theory_of_operation.html) and [clock manager](https://opentitan.org/book/hw/ip/clkmgr/index.html) | Reference design uses ~200 kHz AON, 64-bit wake counter and clock controls. A 64-bit word avoids ordinary rollover but its 5 µs nominal tick alone does not give 1 µs capture accuracy. Its clock topology and power are **not** Hummingbird measurements. |
| V2 | [AMD XPM_CDC_SINGLE](https://docs.amd.com/r/en-US/pg382-xpm-cdc-generator/XPM_CDC_SINGLE), [XPM_CDC_HANDSHAKE](https://docs.amd.com/r/en-US/pg382-xpm-cdc-generator/XPM_CDC_HANDSHAKE), [XPM_FIFO_ASYNC](https://docs.amd.com/r/en-US/ug953-vivado-7series-libraries/XPM_FIFO_ASYNC) | Single-bit level synchronization, coherent multi-bit handshake with acknowledgment before reuse, and asynchronous FIFO address distinct CDC problems. They are FPGA primitives/guidance, **not** drop-in ASIC cells; event toggle/handshake must account for back-to-back edges and reset. |
| V3 | [ST LSM6DSV16X datasheet DS13510 rev. 4, §§9.52–9.53](https://www.st.com/resource/en/datasheet/lsm6dsv16x.pdf) | Vendor says timestamp resolution and ODR depend on `FREQ_FINE` (0.13%/step); nominal timestamp period at zero code is 1/46080 s ≈21.70 µs. This is an example **other** IMU, not the project-selected device. FIFO read completion cannot be equated with physical sample time. |

## Quantitative candidate trade study

Derived arithmetic below is **not measured silicon**. Tick period `T = 1/f`; ideal nearest-tick quantization ≤T/2, capture to next tick <T. Drift bound for constant assumed rate error `|ε|` ppm over an uncalibrated interval `Δt` is `|ε| × 10⁻⁶ × Δt`, excluding temperature dynamics, phase noise and host error. The candidate ≤1 µs is a resolution target, **not** an accuracy/jitter guarantee.

| Candidate clock representation (analytical) | Tick and worst ideal capture quantization | Relative timing while main clock sleeps | Power/area/physical feasibility |
|---|---|---|---|
| 32,768 Hz AON-only counter | 30.518 µs tick; <30.518 µs next-tick latency | Runs if AON stays alive; cannot meet ≤1 µs tick | Source/clock-tree dependent; no accepted power/area estimate |
| 200 kHz AON-only counter (V1 reference frequency) | 5 µs tick; <5 µs capture latency | Runs if AON stays alive; still fails ≤1 µs tick | OpenTitan is a reference design, not a physical budget |
| 1 MHz continuously running counter | 1 µs tick; <1 µs capture latency | Candidate tick resolution possible through sleep **only if** clock/retention survives | AON power, jitter, capture metastability, PVT and area remain unknown; physical decision on hold |
| Slow AON + awake 2 MHz fine capture | 0.5 µs awake tick; if 32,768 Hz AON, 30.518 µs sleep tick | Fine timestamps only during valid awake clock; transition/cross-calibration and sleep event uncertainty require measured bounds | Saves unspecified fast-clock idle power; no claims of sub-µs sleep capture |

A hypothetical 20 ppm constant offset accumulates 1.728 s in 24 h; 50 ppm accumulates 4.32 s. A 100 s unsynchronized gap at 20 ppm already gives a 2 ms drift bound. These examples are scenario sensitivities, **not P1/P2 device accuracy**, nor synchronization requirements. For a 64-bit 1 MHz counter the mathematical unsigned wrap interval is >584,000 years; electrical continuity, reset, frame width and serialized counter snapshots still need verification. Under independent worst-case uncertainty terms a conservative total is quantization + bounded CDC phase + trigger/sample latency spread + inter-domain calibration + drift + IMU sample-delay spread; do not RSS-sum these limits or label resolution as cross-sensor accuracy.

## Finding → implication → conditional decision

| Evidence/finding | Hummingbird implication | Decision at this gate |
|---|---|---|
| P1/P2 achieve low-power measured kHz clocks, but their reported period exceeds 1 µs. | AON-only timestamp cannot support the candidate high-resolution capture. | Model an AON owner for continuity plus an explicitly qualified awake fine-capture option; also compare a continuous 1 MHz candidate. **No oscillator/cell selected.** |
| V1 separates AON timer from system clock controls. | Sleeping or restarting the fine clock may step time unless a retained epoch and explicit handoff are maintained. | Require continuity, rollover and re-lock tests; invalidate fine capture outside its running interval. |
| V2 requires purpose-specific CDC mechanisms. | Syncing an entire 64-bit binary word with independent flops risks incoherent reads; a pulse can be missed. | Inventory each crossing; use coherent snapshot/handshake or suitable queue for data, acknowledged events for bursts and reset synchronization; physical CDC/RDC signoff later. |
| V3 documents device-local timestamp trim; FIFO may batch samples. | Late packet arrival and device clock error corrupt host-relative sample time. | Require valid sync anchor and sample index/period plus uncertainty; actual IMU contract remains open. |

## Decisions held, risks, and re-survey

- AON clock choice, clock generation, wake handshake/glitch-free mux, physical metastability MTBF and ASIC async-FIFO implementation require PDK, clock tolerance, power, clock quality and CDC/RDC tooling (`OI-006`, `TIM-0009`).
- Cross-sensor accuracy, drift calibration period and trigger-to-aperture tolerances need algorithm-owner constraints (`OI-010`); optical scan simultaneity/settling and IMU pin/FIFO contract need `OI-012`/`OI-014` and selected sensor evidence. Host epoch frame versioning and link timing need `OI-013`/CH06.
- Safety implications: incorrect relative timing can mislabel multimodal biomarkers and actuator exposure. Timing triggers do not replace independent LED/body-current safety limits (`OI-005`, `OI-015`).
- Re-survey when product timing accuracy, oscillator/PDK, IMU, link, sample apertures or CDC tool flow is chosen, or before committing a physical clock tree/synthesizable timestamp block. Evidence decision here: **SURVEY_PASS_FOR_CONDITIONAL_CH05_MODEL; PHYSICAL_TOPOLOGY_HOLD**.
