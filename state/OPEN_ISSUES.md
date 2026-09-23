# Open Issues

These issues block **architecture freeze**, not CH01 transcription. CH02–CH04 resolve what can be resolved without vendor access. Requirements linked in `state/REQUIREMENTS_TRACEABILITY.csv` are provisional.

| ID | Question / decision | Owner role | Closure evidence / intended chunk |
|---|---|---|---|
| OI-001 | Which modalities and mode combinations are product requirements, research interfaces, or future options? Is high-power audio/UV needed? | Product + systems | Approved priorities, use cases and mode matrix; CH02 |
| OI-002 | Is bare-die nRF and MEMS/package co-integration commercially and technically available? Which memory is needed? | SiP + procurement | Vendor drawings, supply terms, NAND/NOR trade study; CH21/CH47 |
| OI-003 | Can 8–14 mAh usable battery support intended current pulses, wake, radio, LED, audio and logging duty cycles? | Power + systems | Measured cell impedance/usable energy and mode power/data models; CH02–CH04 |
| OI-004 | What are electrode/optical/thermal source models, environmental ranges, input protection leakage and complete noise/error budgets? | Sensors + analog | Sensor evidence and per-block literature, budgets and test plans; CH07 onward |
| OI-005 | Which market, medical/research claims, applicable safety criteria and independently enforced exposure/current limits apply? | Product + safety | Jurisdiction and qualified hazard/standards review; before energy-drive architecture selection |
| OI-006 | Which foundry PDK, licensed IP, die access, EDA and test facilities are available? | Silicon program | Confirmed vendor/IP agreements and tool/PDK evidence; CH30–CH31 |
| OI-007 | Can channel/converter/pad count, SRAM and 10% reserve fit the proposed 6–8 mm class SiP? | Architecture + package | CH02–CH04 resource budgets; vendor pin/assembly/floorplan estimates |
| OI-008 | What license terms and contribution policy should apply to this public repository? | Repository owner | Approved license and documented contribution policy; before outside contributions |
| OI-009 | Which voltage window, chemistry, cycle life, temperature range and aging model define usable battery energy? | Power + product | Cell datasheet and measured curves; CH03/CH23 |
| OI-010 | What sample-time accuracy and clock-drift bound does each cross-sensor biomarker actually require? | Algorithms + systems | Defined research hypotheses and reference datasets; CH02/CH05 |
| OI-011 | Does optical UV mode belong in this product; if so what calibrated spectral irradiance/geometry and qualified limits govern exposure? | Product + safety/optics | Radiometric measurements and independent safety review; CH11/CH12 |
| OI-012 | Which architecture and acquisition paths are simultaneous, and which may be multiplexed without invalidating timing? | System architecture | CH02 mode matrix and CH04 throughput analysis |
