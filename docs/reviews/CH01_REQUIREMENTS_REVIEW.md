# CH01 requirements normalization review

Date: 2026-09-23
Source baseline: `MASTER_SPEC.md` from CH00 remote commit `5ea0185f5b527efd0647e9197d92fea1e7b646da`; CH01 safety wording correction is documented below.
Status: **CH01 register accepted as a provisional extraction; system requirements review and architecture selection are open.**

## Register and interpretation

The register contains **223 unique IDs** across program, system, sensing, conversion, timing, power, package, safety, security, DFT and validation topics. Every ID has a proposed owner role, planned verification method, planned design/test destination, top-level master section and linked open issue. `MUST` and `SHOULD` preserve normative intent, not technical feasibility. The design/test path columns are destinations; there are **no tested block designs** yet. `NEEDS_DEFINITION` flags missing conditions or acceptance limits. `RESEARCH_ONLY` prevents electrical feature claims from becoming clinical or biochemical claims. The actual baseline and test command are recorded in `state/PROJECT_STATE.md`.

The source uses `TARGET` as a maturity qualifier on many numbers. These are transcribed as candidates with `TARGET` in `Target_or_Limit` and `NEEDS_DEFINITION` status. None is frozen. Deliberately duplicated presentation of the same target in §53 and the architecture summary does not create additional IDs. Architecture choices given as alternatives (NAND versus NOR, BCD versus CMOS, piezo versus electromagnetic, shared versus dedicated ADC) are trade studies, not commitments to implement every option.

## Source coverage and disposition

| Source sections | CH01 IDs / disposition |
|---|---|
| 0, 38–52, 55, 59–61 | `PRC-*` and `VAL-*`: process gates, literature, persistence, traceability, verification and signoff. Section 42 chunk steps are execution planning, not hardware requirements. |
| 1–6, 36–37, 56–58 | `SYS-*`: product modes, architecture candidate, reserve, validity and optimization. |
| 7 | `BIO-*`: channel, electrode, bandwidth, noise, safety. |
| 8 | `EDA-*`: conductance, impedance, excitation, receive and calibration. |
| 9 | `ECH-*`: ISE, potentiostat, leakage, dynamic current range and research chemistry. |
| 10 | `OPT-*`: drive, receive, timing, spectral research and UV safety. |
| 11 | `THM-*`: NTC and low-frequency thermopile path. |
| 12–13 | `AUD-*`: audio input/output and battery implications. |
| 14, 17, 27 | `TIM-*`: IMU, global timebase, clocking and trigger determinism. |
| 15–16 | `ADC-*`, `DAC-*`: converter candidates and metrology. |
| 18, 25, 28 | `AON-*`: always-on and power/reset sequence. |
| 19–20 | `DSP-*`: selected accelerators and metadata. |
| 21–22 | `MEM-*`: buffering and storage choices. |
| 23 | `HIF-*`: nRF link and flow control. |
| 24–26 | `PMU-*`: charger, fuel gauge, power domains and energy. |
| 28–30, 58 | `SAFE-*`: interlocks, exposed optics, body-connected ESD. |
| 31 | `CAL-*`: reference and calibration infrastructure. |
| 32 | `SEC-*`: identity, firmware, debug, data and stimulation access. |
| 33 | `DFT-*`: digital/analog testability. |
| 34–35 | `PKG-*`: SiP constraints and external transducers. |
| 43–50, 57–58 | `VAL-*`: budgets and verification/release gates. |
| 53 | Repetition of provisional top-level targets mapped to their primary section IDs. |
| 54 | Conceptual explanation of architecture; no additional independently testable limit. |

The source coverage is **section-level**. A pass proves no top-level source section has been omitted; it does **not** prove that every line is an approved requirement. CH02–CH04 may split candidate IDs further when product concurrency and physical budgets are established. No arbitrary number was promoted to an acceptance threshold.

## Conflicts and closure evidence

| ID | Issue, linked requirements | Why it matters from first principles | Closure evidence and gate |
|---|---|---|---|
| C-01 | Modalities and concurrency: `SYS-0006`, `SYS-0010`, `BIO-0001`, `OPT-0008`, `ADC-0001`, `ADC-0003`, `PKG-0001`; OI-001/007 | Nominal 8 biopotential, 8 electrochemical, 12 optical and further channels imply pads, independent converters, quiet returns and simultaneous storage demand. Package footprint alone cannot establish feasibility. | CH02 simultaneous-mode and pad/converter matrix, then CH04 throughput and CH30 PDK/package proof. |
| C-02 | Tiny cell versus LED/audio: `PMU-0001`, `OPT-0002`, `AUD-0011`, `SYS-0019`; OI-003 | An illustrative 8–14 mAh usable cell at an **assumed** 3.7 V contains only ≈30–52 mWh before conversion losses. One 150 mA, 3.7 V electrical load consumes ≈0.56 W while active. LED current is a channel *peak candidate*, not proof the cell can supply all channels or audio concurrently. | CH03 chemistry, cell impedance/voltage sag, emitter forward voltage, converter efficiency, pulse duty cycle and runtime model measured with representative cells. |
| C-03 | Area reserve versus scope: `SYS-0011`, `MEM-0001`, `PKG-0001`; OI-007 | 512 KB–2 MB SRAM and multiple precision analog banks could dominate die/pad area in the proposed small SiP. The 10% reserve has no defined denominator until process and floorplan. | CH02/CH04 resource models; CH29/CH42 die and floorplan data; revise scope or envelope through ADR. |
| C-04 | 24-bit-class versus actual noise: `BIO-0015`, `ADC-0001` through `ADC-0008`; OI-004 | Output word width alone sets neither input-referred noise nor effective resolution. Source impedance, DC offsets, flicker noise and bandwidth govern usable accuracy. | CH07/CH16 band-limited noise, dynamic range, ENOB and full-scale budgets at defined conditions. |
| C-05 | Wide BioZ range: `EDA-0003`, `EDA-0004`; OI-004/005 | 0.1 Hz to 1 MHz spans seven decades; a single excitation/readout path might not preserve safety, phase precision and low power across all ranges. | CH09 electrode/tissue models, band-specific accuracy and safe current/frequency limits. |
| C-06 | ISE leakage and dynamic current: `ECH-0004`, `ECH-0005`, `ECH-0009`, `SAFE-0003`; OI-004/006 | A 1 pA leakage through a 1 TΩ source changes measured voltage by 1 V in a simple resistive model; actual electrode behavior is more complex. The 100 pA–100 µA goal spans six decades, requiring calibrated ranges and compatible protection. | CH10 sensor/reference models and actual source impedance; CH30/CH35 PDK/ESD/temperature data. |
| C-07 | Thermal offset/noise at near DC: `THM-0005` through `THM-0010`; OI-004 | Offset drift, long settling and chopper ripple can be comparable to ~100 µV signals even if broadband noise is low. | CH13 defined 0.1–10 Hz measurement duration/source impedance; CH37 drift and post-layout evidence. |
| C-08 | UV interlock is not a dose model: `OPT-0017`, `OPT-0018`, `SAFE-0006`; OI-005 | The old master equation summed electrical drive × time; it lacks wavelength, calibrated accessible radiant output, distance/geometry and accepted exposure criterion. Electrical current cannot by itself establish optical exposure. | CH11/CH12 optical radiometry and independent safety assessment before UV enable. CH01 clarified §10.8 as a fault proxy, not a safety proof. |
| C-09 | Biomarker and medical capability: `SYS-0007`, `SYS-0020`, `ECH-0021`, `OPT-0022`; OI-005 | Electrodes and wavelengths measure physical signals; glucose, hormones, BP and other biomarkers require selective chemistry or validated inference against reference data. | Defined transducer and study protocols before product claims. |
| C-10 | nRF bare die, NAND stack and RF/analog isolation: `SYS-0002`, `MEM-0004`, `PKG-0001`, `PKG-0002`; OI-002/006 | Procurement, die access and package parasitics cannot be inferred from packaged datasheets. | Vendor commercial terms, die drawings, PDK/IP and package DFM evidence before partition freeze. |
| C-11 | Product safety boundaries and limits: `BIO-0021`, `ECH-0018`, `SAFE-0001` through `SAFE-0006`; OI-005 | A fail-safe output requires explicit physical current, optical, thermal and time limits. `OFF` by default is not a substitute for measured fault containment. | Qualified, jurisdiction-specific hazard analysis with hardware fault injection and product-mode review. |

The UV correction is informed by the [IEC 62471:2006 summary](https://webstore.iec.ch/en/publication/7076), the [IEC 62471-6:2022 UV product summary](https://webstore.iec.ch/en/publication/59543), and the [IEC TR 62471-4:2022 radiometric measurement summary](https://webstore.iec.ch/en/publication/33225). Their applicability and numerical limits require qualified assessment for the actual wearable and market; CH01 does not interpret or claim compliance with a standard.

## CH01 gate result

- PASS: register consistency, source-section coverage, safety target capture, uncertainty/open-issue logging, master UV safety correction and state update.
- OPEN: System Requirements Review and product scope decisions. All electrical values remain provisional.
- NEXT: CH02 concurrency matrix. A hardware block architecture/design gate has **not** passed and no first circuit is implemented.
