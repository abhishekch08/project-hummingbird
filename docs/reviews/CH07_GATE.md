# CH07 gate: conditional EEG/ECG numerical budget; topology held

Date: 2026-09-25 UTC. Literature and [entry charter](../chunks/CH07_BIOPOTENTIAL_NUMERICAL.md) were separately merged in [PR #11](https://github.com/abhishekch08/project-hummingbird/pull/11) as `4e6bd443a2de7402f0ff92fcaba076790b717a19` **before** the first CH07 numerical model commit. [Primary source review](../literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md), [scenario fixture](../../specs/biosignal/CH07_NUMERICAL_SCENARIOS.json), [Python model](../../models/python/ch07_biopotential.py), [generated JSON](../../reports/block/CH07_NUMERICAL_SUMMARY.json) and [numerical report](../budgets/CH07_BIOPOTENTIAL_REVIEW.md) comprise this gate.

| Gate | Decision | Evidence and remaining limit |
|---|---|---|
| Literature before numerical design | PASS | Fabricated EEG AFEs, measured dry electrodes and artifact experiments distinguished from vendor specifications and post-simulation; source bands and test conditions recorded. |
| Conditional numerical accounting | **MODEL_PASS** | Six explicit missing physical input classes; 12 focused tests for units/provenance, resistor loading, bias/pad, common-mode mismatch, noise RSS, offset/gain, Nyquist/OSR, first image, power and CH02 eight-channel reconciliation. Deterministic generated report; public suite and CI. |
| Provisional noise, headroom, alias and interference | **MODEL FAILURES in chosen fixtures, not product failure verdicts** | With a fictional 1 µVrms goal, EEG/ECG resistor-plus-circuit RMS is 1.145/1.647 µVrms. DC offset and worst-phase inputs need ~0.30015/~0.30024 V while gain settings allow 0.04167/0.25 V; a 1 V common-mode stimulus gives 54.99/99.98 µV contact-mismatch plus 10 µV ideal intrinsic residual. First-image probe leaves 137.93 µV peak in both fixtures. The assumptions can be changed only with evidence and re-review; these are not chip measurements. |
| Selected AFE topology and frozen block specification | **TOPOLOGY_AND_REQUIREMENTS_HOLD** | There is no owner-approved electrode impedance *versus frequency*, polarization/motion/offset distributions, head-worn EEG/ECG quality requirements, required passband and allowed dropouts, pad/ESD/leakage, AFE rail/current/area or safe body drive policy. Cannot compare AC- versus DC-coupled channels or sign off full-chain CMRR/noise/alias and overload recovery at a physical operating point. |
| CH08 behavioral requirement pass and CH09 onward | **NOT ELIGIBLE YET** | `MASTER_SPEC.md` CH08 gate requires a behavioral channel to pass **system requirements**. No selected topology or frozen numerical targets exist; implementing a behavioral channel now would encode arbitrary product conditions. CH09 and later depend on this path. |

## Reproduction

```sh
python3 models/python/ch07_biopotential.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch07_*.py'
python3 scripts/verification/check_all.py
git diff --check
```

The 12 new tests bring the public Python unit suite to 81, covering only the assumed resistive noise and error math. No SPICE, Verilog-A/RNM, silicon, electrode-phantom bench, ESD/protection simulation, actual converter transfer, ADC ENOB, PDK area/power, head measurement or independently reviewed safety result is claimed. Random independent source/IA/ADC/quantization terms are RSS; coherent line pickup, motion and offset are explicitly **not** added as random noise. Eight-channel power (80/96 µW per all-identical fixture) omits bias drive, rail losses, shared circuits and clocks.

## Trace and exit criteria

| Provisional requirement | Accounted for | Needed for closure |
|---|---|---|
| `BIO-0001/0002`, `BIO-0010`–`BIO-0015` | CH02 eight candidate paths, EEG/ECG scenario bands, sample/OSR and ideal LSB/first-image probes | Product owner chooses channels, valid band, digital/analog filter attenuation, anti-alias rejection, noise and ADC ENOB/SNDR conditions. |
| `BIO-0003`–`BIO-0009`, `BIO-0016/0017/0019/0020` | Per-leg resistive load, bias/pad, common-mode source imbalance, random integrated noise and DC-coupled headroom | Measured complex electrode/source/contact, offset and artifact distributions, PDK pads, selected AFE/ADC, regulator noise and overload/lead-off recovery. |
| `BIO-0018/0021`, `SAFE-0001/0003/0005` | Explicitly absent pad/ESD/mux/drive evidence | Qualified hardware current/protection and safety review, PDK ESD/leakage, selected passive/active electrode interface. Body-connected drive remains disabled/unselected. |

Open `OI-001/004/005/006/007/012` and risks `R-001/004/005/012/016`. The [CH08–CH50 dependency audit](CH08_CH50_ENTRY_AUDIT.md) identifies the later evidence gates. **CH07 is paused at topology/requirement freeze after a passing conditional numerical subgate.** Resume CH07 with the specific source, quality, PDK/power and safety evidence above; select a topology and freeze an independently reviewed block specification, then start CH08 behavioral implementation and its own gate. The broad user authorization continues; missing physical and product facts prevent a valid next pass.
