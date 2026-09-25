# Risk Register

Qualitative screening only, updated 2026-09-25. Impact `I` and likelihood `L` use 1 (low) to 5 (high); the product is a **ranking aid, not a measured probability**. Product/safety owner review is still pending after CH05. All risks are open.

| ID | Risk | I | L | Score | Owner role | Mitigation / next evidence |
|---|---|---:|---:|---:|---|---|
| R-001 | Electrode/ISE input ESD leakage corrupts µV/mV signals | 5 | 4 | 20 | Analog + ESD | PDK-backed pad study and electrode model; OI-004/006 |
| R-002 | Optical dynamic range and UV exposure misclassified | 5 | 4 | 20 | Optics + safety | Radiometry, ambient model and independent exposure limits; OI-011 |
| R-003 | Multimodal concurrency exceeds converters, pins or memory bandwidth | 4 | 5 | 20 | Systems | CH02 bank conflict; CH04 conditional rate/queue model and fast stress show backlog growth at invented 64 MHz/70%; physical links and simultaneous modes unverified; OI-007/012/013 |
| R-004 | Switching/RF/audio coupling invalidates microvolt sensing | 5 | 4 | 20 | AMS + package | Noise isolation budget and package return-path analysis; OI-004 |
| R-005 | Tiny cell cannot deliver peak current or intended runtime | 5 | 4 | 20 | Power | CH03 synthetic sag/duty/efficiency sensitivities show why load and cell conditions matter; physical battery peak remains unverified until representative cell and load measurement; OI-003/009/015 |
| R-006 | Biochemical/optical capability interpreted as validated biomarker | 5 | 4 | 20 | Product + science | Restrict claims; reference study and transducer evidence; OI-001/005 |
| R-007 | Dense SiP/RF/MEMS/memory assembly fails size/yield | 4 | 4 | 16 | SiP | DFM rules and vendor assembly assessment; OI-002/007 |
| R-008 | Bare-die and licensed PDK/IP inaccessible | 5 | 3 | 15 | Program + procurement | Written vendor terms and PDK availability; OI-002/006 |
| R-009 | Analog test access/calibration time erodes yield and capacity | 4 | 4 | 16 | DFT | Pin and production-time plan before package freeze; OI-006/007 |
| R-010 | Candidate feature load consumes 10% reserve | 4 | 5 | 20 | Architecture | CH02 estimates 78–94 sensor contacts; CH04 synthetic FIFO + workspace can be compared with provisional SRAM labels, but no macro area or reserve denominator exists; OI-007 |
| R-011 | Near-DC thermal measurement offset/drift overwhelms signal | 4 | 4 | 16 | Thermal analog | Long-term low-frequency characterization; OI-004 |
| R-012 | Body-connected drive or software fault exceeds safe limit | 5 | 3 | 15 | Safety + analog | Independent interlocks and fault injection; OI-005 |
| R-013 | High-rate timestamp/framing floods host and FIFO | 4 | 4 | 16 | Digital architecture | CH04 separates packet/frame bytes, ASIC FIFO and host→BLE staging; invented audio BLE and research 16 MHz paths grow each cycle; measured links, loss policy and CH06/CH19 design needed; OI-013 |
| R-014 | Scanned PDs are mistaken for simultaneous optical data | 4 | 4 | 16 | Optics + timing | CH02 explicitly splits 12 PDs across 8 ADCs; define coherence; OI-014 |
| R-015 | LF sleep capture or an incoherent clock/reset handoff is mislabeled as 1 µs cross-sensor accuracy | 5 | 4 | 20 | Digital timing + algorithms | CH05 quantifies ~32 µs synthetic wake uncertainty and rejects sleep triggers without wake queue; require biomarker error limits, measured clock PVT/phase, RTL simulation and CDC/RDC signoff; OI-006/010/012 |
