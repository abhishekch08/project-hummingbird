# CH07 conditional biopotential numerical review

Generate with `python3 models/python/ch07_biopotential.py --write`, check with `--check`. Config SHA-256 `0d6d5378c2b9edc87c94a0ec667e7a494d5030d998dffedbe923ca7b191c06a9`; CH02 input SHA-256 `c3043a250688a9e7a7901a26cc1956137250e86269150284ed6ae9053b688e67`. [Literature survey](../literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md) was merged as PR #11 before this model. **Synthetic probe, no selected EEG/ECG electrode, AFE, ADC, PDK or body-current path.**

## Equations and deliberate limits

For a *real, constant resistance* on each of two electrode legs, `aᵢ = Rin/(Rin+Rᵢ)`. Differential signal transfer ≈`(a₁+a₂)/2` for symmetric ±signal/2. A common-mode voltage makes differential `|a₁−a₂| Vcm`; add the intrinsic `Vcm × 10^(−CMRR/20)` by worst phase, **not RSS**. Bias+ESD leakage worst-case differential magnitude is bounded by `(|Ibias|+|Ipad|)(R₁+R₂)`. DC-coupled headroom needs electrode offset + this bias + common-mode error + attenuated signal, compared with `Vpp/(2×gain)`. These are simplified sensitivities, not an input-common-mode, pad or servo simulation.

Thermal electrode white noise **at the loaded input** for two resistors over flat `B = fhigh − flow` is `sqrt(4 k T B (R₁ a₁²+R₂ a₂²))`, with exact SI `k = 1.380649e−23 J/K`. RSS includes this source noise, separately assumed independent IA noise, ADC noise and *ideal uniform* converter LSB/√12. Electrode polarization, 1/f, motion, ESD, reference, ADC noise shaping, passband weighting and correlations are **omitted**. Peak-to-peak manufacturer noise is never converted to rms. A 24-bit word and `OSR = fmod/fs` are labels; neither implies ENOB/SNDR or safe anti-aliasing.

The anti-alias probe cascades `n` identical analog first-order low-pass poles with magnitude `[1+(f/fc)²]^(−n/2)`. It samples the first image at `fs − fhigh`, reports input-referred output spur from an assumed interferer and shows signal-band edge gain separately. This is **one frequency** and does not model decimator stopbands, broad EMI, transients or a real analog transfer function.

| Synthetic mode | Resistor noise µVrms | Random RSS µVrms | Common-mode mismatch + intrinsic µVpeak | Required / allowed DC input headroom V | First-image spur µVpeak | Eight identical channels µW |
|---|---:|---:|---:|---:|---:|---:|
| `eeg_dry_resistive_probe` | 0.890 | 1.145 | 54.99 + 10.00 | 0.300149 / 0.041667 | 137.93 | 80 |
| `ecg_resistive_probe` | 1.308 | 1.647 | 99.98 + 10.00 | 0.300240 / 0.250000 | 137.93 | 96 |

An assumed 1 µVrms goal is exceeded for both fixtures; neither provides offset headroom at its chosen DC-coupled gain. At 1 V common mode, the unequal source impedances produce a residual **in addition** to ideal 100 dB intrinsic rejection. The first-image interference exceeds the 1 µV comparison value. Random noise and deterministic interference are **not** interchangeable; an external noise target and artifact/recovery acceptance are still needed. The eight-channel power line multiplies only invented per-channel input power and omits ADC/clock, shared analog, rails and body drive; no battery runtime or SiP area follows from it.

## Architecture review and next gate

DC-coupled simultaneous PGA/ΔΣ can preserve low-frequency waveform but needs enough offset headroom at useful gain. AC-coupled chopper/servo can remove DC and flicker at cost of corner, settle, input charging and ripple. An active electrode or input impedance boost can limit pickup along a high-impedance lead but adds on-body electronics, power and safety complexity. These are alternatives, not selected topology. See [CH07 gate](../reviews/CH07_GATE.md): NUMERICAL_MODEL_PASS / TOPOLOGY_AND_REQUIREMENTS_HOLD. Source measurements, owner quality criteria, PDK/pad and reviewed body-current limits must arrive before freezing a block specification, transistor sizing or claiming CH08 behavioral requirements pass.
