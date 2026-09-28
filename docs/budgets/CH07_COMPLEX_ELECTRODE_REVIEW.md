# CH07 passive complex-electrode sensitivity

Generate with `python3 models/python/ch07_complex_electrode.py --write`; verify with `--check`. Config SHA-256 `84127c2288701a9eb0e9a5d1b50e077536110b944ed9108af4479ef7563af1c6`; previous CH07 resistor fixture SHA-256 `0d6d5378c2b9edc87c94a0ec667e7a494d5030d998dffedbe923ca7b191c06a9`. The [entry acceptance](../chunks/CH07_EVIDENCE_READINESS.md) and [electrode evidence intake](../inputs/CH07_ELECTRODE_QUALITY_INTAKE.md) define the use and next review. **All capacitances are invented sensitivity inputs. No electrode, IC pad or AFE has been characterized for this project.**

For each leg use a passive series resistor plus a parallel resistor/capacitor: `Zs(f) = Rs + Rp/(1 + j2πf Rp C)`. Input admittance `Yin(f) = 1/Rin + j2πf Cin`, voltage transfer `H = 1/(1 + Zs Yin)`. For symmetric ±differential drive, `Hdiff = (Hp + Hn)/2`; for identical common-mode drive at both electrode sources, `Hcm→diff = Hp − Hn`. The table shows `|Hdiff|`, its phase, `|Hcm→diff|×Vcm`, and the worst-phase upper bound adding a separate intrinsic `Vcm×10^(−CMRR/20)` magnitude. The assumed common mode is **1 V peak at every listed frequency solely to expose sensitivity**, not a broadband/noise/clinical test; this worst-phase bound is not RSS or a measured circuit response.

| Synthetic mode | Frequency Hz | Differential magnitude | Phase deg | Source mismatch µVpeak | Mismatch + intrinsic upper bound µVpeak |
|---|---:|---:|---:|---:|---:|
| `eeg_dry_resistive_probe` | 0.05 | 0.99990751 | -0.00002 | 54.991 | 64.991 |
| `eeg_dry_resistive_probe` | 50 | 0.99984525 | -0.00463 | 107.056 | 117.056 |
| `eeg_dry_resistive_probe` | 500 | 0.99983987 | -0.03611 | 273.286 | 283.286 |
| `eeg_dry_resistive_probe` | 1500 | 0.99983812 | -0.10802 | 761.373 | 771.373 |
| `ecg_resistive_probe` | 0.05 | 0.99990001 | -0.00002 | 99.981 | 109.981 |
| `ecg_resistive_probe` | 50 | 0.99979000 | -0.00832 | 135.658 | 145.658 |
| `ecg_resistive_probe` | 500 | 0.99967100 | -0.02849 | 301.342 | 311.342 |
| `ecg_resistive_probe` | 1500 | 0.99966679 | -0.08149 | 937.346 | 947.346 |

The fixed DC series+parallel resistance equals the earlier CH07 resistor fixture on each leg. The published resistor model remains the source for its separate bias/offset, white-noise, gain and first-image arithmetic. This extension **does not integrate complex-source noise**, fit a constant-phase skin electrode, simulate polarization/movement, coupling between legs/body, protection nonlinearity, chopper charging, ADC filters, recovery or lead-off excitation. Its passband and image-grid samples are not a filter design or proof of alias rejection. It predicts how assumed contact/pad capacitance can alter loading and common-mode conversion with frequency and identifies measurements that must replace the fixture. **CH07 topology and full block spec remain HOLD; CH08 remains NOT_RUN.**
