# External inputs and decision queue

These are requests for evidence, **not blockers to drafting a parameterized CH03 model**. A real architecture/runtime verdict depends on them. Do not fill missing values with asserted vendor numbers.

| Priority | Input / decision | Needed for | Acceptable evidence | Current state |
|---|---|---|---|---|
| P0 | Cell chemistry, usable voltage window, capacity at load/temperature/aging, internal impedance and pulse-current limits | CH03 peak sag, energy and charger constraints | Cell datasheet plus measurements on representative cells | Missing; OI-003/009 |
| P0 | Intended mandatory modes, concurrency and duty cycle for daily/sleep/audio/optical operation | CH03 runtime and CH04 transport sizing | Product-mode decision and instrumented usage trace | Missing; OI-001/012 |
| P0 | LED forward-voltage range, optical current profile, emission duty cycle, actual rail tree and efficiencies | CH03 battery input-current conversion and thermal peaks | Selected emitter and PMIC data, bench waveform | Missing; OI-003/015 |
| P0 | AON, MCU/RF, IMU, analog AFE, audio and NAND current in each power state, startup time/energy | CH03 energy sum and power-domain transitions | Measured current traces or vendor conditions matched to selected mode | Missing; OI-003 |
| P1 | Host link clock, framing, CRC, sleep/wake overhead and storage backpressure | CH04 exact sustained/burst throughput | Vendor interface confirmation and prototype timing | Missing; OI-013 |
| P1 | Channel topology, electrodes, skin contact and source impedance/capacitance by modality | CH07 onward noise and pad/ESD | Measured sensor/electrode model and fixture | Missing; OI-004 |
| P1 | Whether 12 optical PDs must share one instant or may use 8+4 scanning | CH05/CH11/CH16 timing/converter partition | Accuracy hypothesis and motion/optical coherence tests | Missing; OI-014 |
| P1 | Intended market, use claims, optical/electrode safety criteria and independent reviewer | Any body/UV drive and later safety signoff | Product decision and qualified hazard/standards review | Missing; OI-005/011 |
| P2 | nRF/MEMS bare-die access, package rules, process/PDK/IP availability | Partition and implementation | Vendor terms, assembly drawing and foundry access | Missing; OI-002/006/007 |
| P2 | Repository licensing and contribution terms | Outside contributions and reuse | Owner decision with relevant IP review | Missing; OI-008 |

CH02 numeric rates and current are traceable *scenario* values in `specs/system/CH02_MODE_ASSUMPTIONS.json`. They must not be substituted for the missing measured inputs above.
