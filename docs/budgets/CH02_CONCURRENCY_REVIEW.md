# CH02: Candidate mode concurrency and resource review

**Status:** Scenario analysis only. Eight modes transcribed from `MASTER_SPEC.md` §37; sample rates, active channel counts, framing and interface efficiency are explicitly assumed in `specs/system/CH02_MODE_ASSUMPTIONS.json`. None is an approved product mode or verified electrical design.

## Accounting rules

- Raw payload = Σ(channels × effective samples/s per channel × bits/sample). Per-channel rate is an **assumption**, including for scanned optics.
- Illustrative framed traffic = raw payload + 8 quality bits per channel sample + 64 timestamp bits per stream sample group + 8 wavelength-ID bits per optical sample group. The audio per-sample timestamping is deliberately heavy; omitted CRC, dark/ambient cycles and packet details mean this is **not a guaranteed upper bound**. CH04 chooses real framing.
- For optical streams, sample rate is **aggregate per photodiode over all programmed wavelengths**. Divide by `wavelength_phases` in the config to obtain the assumed per-PD, per-wavelength rate. More wavelengths at the same per-wavelength rate increase throughput proportionally.
- Guarded host payload = ceil(1.2 × conservative framed bound). This defines 20% capacity-over-demand headroom when the factor is 1.2; no bus or nRF rate is asserted.
- `ADC occupancy` is the number required at the same instant, **not** a proof of converter maximum sample frequency, settling, calibration or analog noise. Scanned optical channels use multiple slots, so their samples are not all simultaneous.
- `Logical acquisition producers` count independently queued stream groups. They are a minimum arbitration demand, not necessarily distinct hardware DMA channels; CH19 will allocate the actual DMA/FIFO scheme.
- LED current is a programmed **output current** assuming selected output enable count. Battery current is explicitly unknown in every mode. CH03 supplies the voltage, efficiency, load and cell-sag model.

## Candidate mode matrix and traffic

| Mode | Status | Active streams | ADC occupancy | Raw Mb/s | Framed scenario Mb/s | Guarded host Mb/s | Producers | Groups/s | Candidate LED output peak | Bank conflict |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `deep_sleep` | candidate | AON only | none | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 mA | None at count level |
| `daily_health` | candidate | imu_100, temp2_1, ppg2_100, eda1_32 | EDA:1/4, IMU:1/1, OPT:2/8, THM:2/4 | 0.014 | 0.037 | 0.044 | 4 | 233 | 150 mA | None at count level |
| `sleep_neuroscience` | candidate | eeg8_500, ppg4_200, imu_100, temp2_1, audio1_16000 | AUDIO:1/4, BIO:8/8, IMU:1/1, OPT:4/8, THM:2/4 | 0.378 | 1.626 | 1.951 | 5 | 16,801 | 150 mA | None at count level |
| `cardiovascular` | candidate | ecg2_1000, ppg8_500, imu_400, temp2_1 | BIO:2/8, IMU:1/1, OPT:8/8, THM:2/4 | 0.166 | 0.359 | 0.431 | 4 | 1,901 | 150 mA | None at count level |
| `sweat_biochemistry` | candidate | ech8_10, eda2_32, temp4_1, ppg2_100 | ECH:8/8, EDA:2/4, OPT:2/8, THM:4/4 | 0.007 | 0.020 | 0.024 | 4 | 143 | 150 mA | None at count level |
| `optical_spectroscopy` | candidate | opt12_scan_2000, imu_100, temp2_10 | IMU:1/1, OPT:8/8, THM:2/4 | 0.490 | 0.838 | 1.006 | 3 | 2,110 | 150 mA | None at count level |
| `audio` | candidate | audio2_48000, imu_100, ppg2_100, temp2_1 | AUDIO:2/4, IMU:1/1, OPT:2/8, THM:2/4 | 2.318 | 6.178 | 7.413 | 4 | 48,201 | 150 mA | None at count level |
| `research_raw` | candidate | eeg8_4000, eda4_1000, ech8_1000, opt8_4000, temp4_10, audio4_48000, imu_1000 | AUDIO:4/4, BIO:8/8, ECH:8/8, EDA:4/4, IMU:1/1, OPT:8/8, THM:4/4 | 6.385 | 12.386 | 14.863 | 7 | 59,010 | 300 mA | None at count level |
| `research_fast_stress` | stress | eeg8_4000, eda4_1000, ech8_1000, opt8_4000, temp4_10, audio4_48000, imu_1000, fast2_1000000 | AUDIO:4/4, BIO:8/8, ECH:8/8, EDA:4/4, FAST:2/2, IMU:1/1, OPT:8/8, THM:4/4 | 38.385 | 124.386 | 149.263 | 8 | 1,059,010 | 300 mA | None at count level |
| `resource_conflict_probe` | stress | eeg8_500, ecg2_1000, opt12_true_2000 | BIO:10/8, OPT:12/8 | 0.624 | 1.104 | 1.325 | 3 | 3,500 | 2400 mA | BIO simultaneous converters/receivers 10>8 (BIO-0001); OPT simultaneous converters/receivers 12>8 (OPT-0008) |

The `resource_conflict_probe` deliberately requests EEG8 + ECG2 on BIO8 and 12 simultaneous optical ADCs from a candidate bank of eight. It tests that both conflicts are reported. The optional `research_fast_stress` includes two 1 MSPS × 16-bit channels and is a stress probe, not a supported product mode.

`Groups/s` sums independent stream sample-group clocks. It gives a worst-case unbatched event rate for arbitration discussion, not a DMA descriptor or interrupt requirement; FIFO batching is necessary for fast scenarios.

### Per-mode assumptions and identified gaps

- **deep_sleep:** AON supervision not streamed; actual AON load unknown. No acquisition stream; host data clock is not needed by this scenario.
- **daily_health:** EDA included as upper bound; PPG rate is active-window rate, not all-day duty cycle. Minimum hypothetical single-data-line clock at 70% efficiency is 0.06 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.
- **sleep_neuroscience:** Continuous raw 16 kHz audio is a conservative upper stream; local event extraction could reduce host traffic. Minimum hypothetical single-data-line clock at 70% efficiency is 2.79 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.
- **cardiovascular:** ECG2 and 8 optical conversion paths are illustrative; cross-sensor timing not yet budgeted. Minimum hypothetical single-data-line clock at 70% efficiency is 0.62 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.
- **sweat_biochemistry:** Optional intermittent PPG counted while active; 8 ECHEM and 4 potentiostats require reference-electrode proof. Minimum hypothetical single-data-line clock at 70% efficiency is 0.03 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.
- **optical_spectroscopy:** 12 PD inputs are scanned in at least two slots with 8 simultaneous ADC paths; all-12 instantaneous coherence is absent. Minimum hypothetical single-data-line clock at 70% efficiency is 1.44 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.
- **audio:** Optical PPG counted as limited optional upper bound; bone-output peak current unknown. Minimum hypothetical single-data-line clock at 70% efficiency is 10.59 MHz; first 8/16/32/64 MHz probe that passes is **16 MHz**. Actual capability is TBD.
- **research_raw:** Illustrative all-bank raw acquisition excluding fast ADC; rates not approved and analog interference unverified. Minimum hypothetical single-data-line clock at 70% efficiency is 21.23 MHz; first 8/16/32/64 MHz probe that passes is **32 MHz**. Actual capability is TBD.
- **research_fast_stress:** Adds both candidate 1 MSPS fast ADCs; intentional host/data stress, not an approved mode. Minimum hypothetical single-data-line clock at 70% efficiency is 213.23 MHz; first 8/16/32/64 MHz probe that passes is **>64 MHz in illustrative set**. Actual capability is TBD.
- **resource_conflict_probe:** Intentionally infeasible: BIO demand 10>8, OPT demand 12>8, and theoretical 16 LED ports at full candidate current. Minimum hypothetical single-data-line clock at 70% efficiency is 1.89 MHz; first 8/16/32/64 MHz probe that passes is **8 MHz**. Actual capability is TBD.

## Channel capacity, optical scan and pin-contact bounds

- Candidate receive capacities: BIO 8, EDA 4, ECH 8 (4 full potentiostats), OPT 12 PD input ports but only 8 instantaneous ADC paths, THM 4, AUDIO 4, FAST 2. These are candidates, not placed macros.
- `opt12_scan_2000`: 12 physical PD inputs × 2000 aggregate samples/s = **24,000 conversions/s** across eight wavelength phases (250 samples/s/PD/wavelength) and two or more temporal PD slots. Eight ADC paths imply an *average* lower bound of 3000 conversions/s/ADC if balanced. Settling, dark frames and conversion headroom could require more; no claim of 12 simultaneous samples.
- Illustrative routed sensor-to-ASIC signal contacts: **78** optimistic with shared electrochemical reference/counter and four single-ended thermal inputs; **94** with independent electrochem references/counters and eight differential thermal inputs. A further **20** logical inter-die nets cover an illustrative host/IMU/memory interface. These are net counts, **not package ball counts**. Power, ground, RF, test, clock, guard and extra return nets are excluded.
- Fixed external capability contacts cannot be inferred from *mode concurrency*: a nonconcurrent sensor still occupies its connection unless a separately proven mux or co-packaged partition removes/moves that net. Shared dry electrodes can add leakage or cross-talk and require CH07/CH09/CH10 evidence.

## Hard gaps before design choice

1. **Product selection:** OI-001/OI-012 remain open; all eight modes are candidate examples. Confirm mandatory channel counts, their sample timing, intermittent windows, which streams must leave the ASIC, and whether multiwavelength samples need simultaneity.
2. **Battery peak:** 150 mA per selected LED port is a candidate **load** current. One/two selected ports imply 150/300 mA candidate LED output; 16 unconstrained ports imply 2400 mA theoretical stress. These are not battery currents or duty-cycle averages. Hardware must bound concurrent enable, fault current and UV exposure independently of software; audio/RF peaks and cell data remain unknown (CH03, OI-003/OI-005).
3. **ADC feasibility:** Count-level fits do not validate 4 kSPS BIO, 4 kSPS OPT, 1 kSPS ECH or 1 MSPS FAST at target noise/energy. ADC maximum effective conversion rate, mux settling and coexistence/spur budgets are TBD (CH07/CH16).
4. **Host/backpressure:** The guarded host rates use the illustrative framing scenario during an active window. Exact SPI clock, CRC, headers, dark/ambient frames, FIFO, NAND busy windows, host wake, radio egress and loss policy remain unapproved (CH04/CH06/CH19). The 70% payload efficiency and candidate clocks are illustrative probes, never nRF specifications.
5. **Physical pin feasibility:** SiP interconnect/pad and package pin budgets differ. Shared references and co-packaged transducers could move nets but require leakage, return path and manufacturability evidence (CH29/CH47).

## Requirements and next gate

Relevant IDs: `SYS-0010`, `BIO-0001`, `EDA-0001`, `ECH-0001`, `ECH-0002`, `OPT-0001`, `OPT-0007`, `OPT-0008`, `AUD-0001`, `ADC-0005`, `MEM-0001`, `HIF-0001`, `PMU-0010`, `PKG-0001`, `TIM-0001` and `SAFE-0002`. Per-mode ID lists are in the JSON report.
CH02 passes when the mode matrix is regenerated, account rules and intentional conflicts are tested, and open inputs are recorded. **Architecture feasibility remains unproven.** CH03 next models battery energy and actual peak battery current without promoting scenario values to requirements.
