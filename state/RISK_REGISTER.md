# Risk Register

Qualitative screening only, 2026-09-23. Impact `I` and likelihood `L` use 1 (low) to 5 (high); the product is a **ranking aid, not a measured probability**. Product/safety owner reviews rankings in CH02. All risks are open.

| ID | Risk | I | L | Score | Owner role | Mitigation / next evidence |
|---|---|---:|---:|---:|---|---|
| R-001 | Electrode/ISE input ESD leakage corrupts µV/mV signals | 5 | 4 | 20 | Analog + ESD | PDK-backed pad study and electrode model; OI-004/006 |
| R-002 | Optical dynamic range and UV exposure misclassified | 5 | 4 | 20 | Optics + safety | Radiometry, ambient model and independent exposure limits; OI-011 |
| R-003 | Multimodal concurrency exceeds converters, pins or memory bandwidth | 4 | 5 | 20 | Systems | CH02 matrix exposes eight-bank occupancy and optional 149.263 Mb/s guarded stress; CH04 loss-free model; OI-007/012/013 |
| R-004 | Switching/RF/audio coupling invalidates microvolt sensing | 5 | 4 | 20 | AMS + package | Noise isolation budget and package return-path analysis; OI-004 |
| R-005 | Tiny cell cannot deliver peak current or intended runtime | 5 | 4 | 20 | Power | CH02 quantifies 150/300 mA selected LED outputs; battery peak remains unknown; CH03 cell/rail model; OI-003/009/015 |
| R-006 | Biochemical/optical capability interpreted as validated biomarker | 5 | 4 | 20 | Product + science | Restrict claims; reference study and transducer evidence; OI-001/005 |
| R-007 | Dense SiP/RF/MEMS/memory assembly fails size/yield | 4 | 4 | 16 | SiP | DFM rules and vendor assembly assessment; OI-002/007 |
| R-008 | Bare-die and licensed PDK/IP inaccessible | 5 | 3 | 15 | Program + procurement | Written vendor terms and PDK availability; OI-002/006 |
| R-009 | Analog test access/calibration time erodes yield and capacity | 4 | 4 | 16 | DFT | Pin and production-time plan before package freeze; OI-006/007 |
| R-010 | Candidate feature load consumes 10% reserve | 4 | 5 | 20 | Architecture | CH02 estimates 78–94 sensor signal contacts before power/test/RF; CH03–CH04 Pareto study and approved denominator; OI-007 |
| R-011 | Near-DC thermal measurement offset/drift overwhelms signal | 4 | 4 | 16 | Thermal analog | Long-term low-frequency characterization; OI-004 |
| R-012 | Body-connected drive or software fault exceeds safe limit | 5 | 3 | 15 | Safety + analog | Independent interlocks and fault injection; OI-005 |
| R-013 | High-rate timestamp/framing floods host and FIFO | 4 | 4 | 16 | Digital architecture | CH02 fast stress 149.263 Mb/s guarded; CH04 framing/FIFO alternatives; OI-013 |
| R-014 | Scanned PDs are mistaken for simultaneous optical data | 4 | 4 | 16 | Optics + timing | CH02 explicitly splits 12 PDs across 8 ADCs; define coherence; OI-014 |
