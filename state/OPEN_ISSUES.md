# Open Issues

These issues block **architecture freeze**, not CH01 transcription. CH02 provides conditional scenarios; CH03–CH04 are paused/planned and will resolve what they can without vendor access. Requirements linked in `state/REQUIREMENTS_TRACEABILITY.csv` are provisional. An issue remains open until its owner supplies the closure evidence and records a decision.

| ID | Question / decision | Owner role | Closure evidence / intended chunk |
|---|---|---|---|
| OI-001 | Which modalities and mode combinations are product requirements, research interfaces, or future options? Is high-power audio/UV needed? | Product + systems | CH02 candidate scenarios complete; owner-approved priorities and product mode matrix still needed |
| OI-002 | Is bare-die nRF and MEMS/package co-integration commercially and technically available? Which memory is needed? | SiP + procurement | Vendor drawings, supply terms, NAND/NOR trade study; CH21/CH47 |
| OI-003 | Can 8–14 mAh usable battery support intended current pulses, wake, radio, LED, audio and logging duty cycles? | Power + systems | Measured cell impedance/usable energy and mode power/data models; CH02–CH04 |
| OI-004 | What are electrode/optical/thermal source models, environmental ranges, input protection leakage and complete noise/error budgets? | Sensors + analog | Sensor evidence and per-block literature, budgets and test plans; CH07 onward |
| OI-005 | Which market, medical/research claims, applicable safety criteria and independently enforced exposure/current limits apply? | Product + safety | Jurisdiction and qualified hazard/standards review; before energy-drive architecture selection |
| OI-006 | Which foundry PDK, licensed IP, die access, EDA and test facilities are available? | Silicon program | Confirmed vendor/IP agreements and tool/PDK evidence; CH30–CH31 |
| OI-007 | Can channel/converter/pad count, SRAM and 10% reserve fit the proposed 6–8 mm class SiP? | Architecture + package | CH02–CH04 resource budgets; vendor pin/assembly/floorplan estimates |
| OI-008 | What license terms and contribution policy should apply to this public repository? | Repository owner | `docs/governance/LICENSE_STATUS.md` records unresolved choice; owner-approved license and contribution policy before outside contributions |
| OI-009 | Which voltage window, chemistry, cycle life, temperature range and aging model define usable battery energy? | Power + product | Cell datasheet and measured curves; CH03/CH23 |
| OI-010 | What sample-time accuracy and clock-drift bound does each cross-sensor biomarker actually require? | Algorithms + systems | Defined research hypotheses and reference datasets; CH02/CH05 |
| OI-011 | Does optical UV mode belong in this product; if so what calibrated spectral irradiance/geometry and qualified limits govern exposure? | Product + safety/optics | Radiometric measurements and independent safety review; CH11/CH12 |
| OI-012 | Which architecture and acquisition paths are simultaneous, and which may be multiplexed without invalidating timing? CH02 demonstrates 12 optical ports need ≥2 temporal slots on eight candidate ADCs; product coherence remains undecided. | System architecture | CH02 scenario matrix complete; CH04 throughput and CH05 timing analysis |
| OI-013 | Can the selected nRF-to-ASIC interface and DMA/FIFO policy sustain candidate research framing? CH02 active-window demand reaches 14.863 Mb/s research or 149.263 Mb/s with the optional fast-ADC stress under stated assumptions. | Digital architecture | Actual link timing, packet format, block timestamping, throughput/backpressure and storage plan; CH04/CH06/CH19 |
| OI-014 | Does 12-PD optical work require physically simultaneous measurements, or is 8+4 time scanning acceptable across source wavelengths? | Optics + algorithms | Optical coherence/error requirement and schedule/settling data; CH05/CH11/CH16 |
| OI-015 | What hardware upper bound restricts simultaneous LED enables, and what are the resulting worst-case output and battery currents? | Power + safety | Independent enable/current limiter and cell/rail transient evidence; CH03/CH12/CH22 |
