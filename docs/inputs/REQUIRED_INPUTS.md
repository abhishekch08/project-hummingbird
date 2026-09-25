# External inputs and decision queue

CH03–CH04 parameterized models are complete at conditional-math gates. These are still **missing physical/product inputs** for a real architecture, runtime, peak-current, transport or memory verdict. Do not fill missing values with asserted vendor numbers.

| Priority | Input / decision | Needed for | Acceptable evidence | Current state |
|---|---|---|---|---|
| P0 | Cell chemistry, usable voltage window, capacity at load/temperature/aging, internal impedance and pulse-current limits | CH03 peak sag, energy and charger constraints | Cell datasheet plus measurements on representative cells | Missing; OI-003/009 |
| P0 | Intended mandatory modes, concurrency and duty cycle for daily/sleep/audio/optical operation | CH03 runtime and CH04 transport sizing | Product-mode decision and instrumented usage trace | Missing; OI-001/012 |
| P0 | LED forward-voltage range, optical current profile, emission duty cycle, actual rail tree and efficiencies | CH03 battery input-current conversion and thermal peaks | Selected emitter and PMIC data, bench waveform | Missing; OI-003/015 |
| P0 | AON, MCU/RF, IMU, analog AFE, audio and NAND current in each power state, startup time/energy | CH03 energy sum and power-domain transitions | Measured current traces or vendor conditions matched to selected mode | Missing; OI-003 |
| P1 | Host link payload versus clock/load, exact packet/timestamp/CRC fields, DMA and sleep/wake/flow-control timing | CH04 physical FIFO and sustained/burst transport verdict; CH05/CH06/CH19 | Selected interfaces, vendor timing and instrumented link/wake trace including busy/backpressure | Missing; CH04 synthetic model only; OI-013 |
| P1 | BLE application goodput/airtime, host staging policy, retry and coexistence profile | CH04 end-to-end egress and buffering | Measured payload and loss/backpressure trace on actual nRF firmware and RF conditions | Missing; CH04 BLE route is an invented service profile; OI-013 |
| P1 | NAND/NOR capacity and write/erase busy windows, ECC/bad-block/retention/endurance, write energy, SRAM macros and reserve | CH04 memory selection, logging retention, CH21 storage and area/power | Selected component/PDK evidence plus representative sustained writes and recording/offload policy | Missing; CH04 capacity/wear and SRAM are synthetic labels; OI-002/007/013 |
| P1 | Channel topology, electrodes, skin contact and source impedance/capacitance by modality | CH07 onward noise and pad/ESD | Measured sensor/electrode model and fixture | Missing; OI-004 |
| P1 | Whether 12 optical PDs must share one instant or may use 8+4 scanning | CH05/CH11/CH16 timing/converter partition | Accuracy hypothesis and motion/optical coherence tests | Missing; OI-014 |
| P1 | Intended market, use claims, optical/electrode safety criteria and independent reviewer | Any body/UV drive and later safety signoff | Product decision and qualified hazard/standards review | Missing; OI-005/011 |
| P2 | nRF/MEMS bare-die access, package rules, process/PDK/IP availability | Partition and implementation | Vendor terms, assembly drawing and foundry access | Missing; OI-002/006/007 |
| P2 | Repository licensing and contribution terms | Outside contributions and reuse | Owner decision with relevant IP review | Missing; OI-008 |

CH02 numeric rates and LED output current are traceable *scenario* values in `specs/system/CH02_MODE_ASSUMPTIONS.json`. CH03/CH04 input files contain **synthetic** cell/rail/load and packet/link/storage values for arithmetic verification. None substitutes for the missing measurements above; feature-only CH04 output discards raw evidence unless a reviewed product decision permits it.
