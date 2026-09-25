# CH07: Biopotential numerical design

Status: **entry charter; numerical model not yet started**. Date: 2026-09-25 UTC. Entry baseline: CH06 candidate host model PR #10 merged as `8b460f4d99c6a5f9aea960b6dbabea5e1b45e4cb`. This charter and the [dated block survey](../literature/biopotential/2026-09-25_STATE_OF_ART_REVIEW.md) are a separate publication **before** any CH07 numerical architecture model. User has authorized subsequent chapters; this is a bounded evidence gate under that authorization.

## Scope and boundary

`MASTER_SPEC.md` §§7, 42; `BIO-0001`–`BIO-0021`, especially noise `BIO-0008`, offset `BIO-0006`, source/input impedance `BIO-0003/0004`, CMRR `BIO-0007`, passband `BIO-0010/0011`, sampling `BIO-0013`, conversion `BIO-0015` and body-current safety `BIO-0021`. CH02 candidate 8 simultaneous channels and mode rates are study inputs. No actual electrode type, geometry, skin impedance spectrum, artifact/offset distribution, reference drive, pad leakage, AFE rail/power allotment, input noise criterion at a stated source/band, usable ADC implementation or PDK is approved. Prior conditional CH03–CH06 gates do not establish these values.

## Acceptance for conditional numerical study

1. Parameterize a distinct EEG and ECG scenario with units, source, range and **assumed** evidence. State per-band sample rate, source impedance and mismatch, bias/pad/leakage, electrode offset, common-mode amplitude, input impedance, amplifier and ADC integrated noise and reference, per-channel power/area and alias-filter order/corner. No vendor device number becomes a Hummingbird requirement by copying it.
2. Model two-terminal electrode source loading and bias error, ADC headroom after offset/gain, CMRR common-to-differential residual and source mismatch, RSS **only for explicitly independent random noise** versus worst-case sum for deterministic interference. Separate signal loss, motion artifact, DC offset and electronic noise. Show why gain ×128 and ±300 mV offset cannot blindly coexist.
3. For each scenario quantify noise density/bandwidth consistency, Nyquist guard, first-order or higher anti-alias attenuation at a stated interferer, ADC LSB/quantization assumptions, delta-sigma OSR bounds, channel power versus CH03 battery sensitivities and eight-channel aggregate. Do not infer actual ENOB, converter topology, measured SNR or clinical quality from a 24-bit word label.
4. Compare three architectural families (DC-coupled PGA/ΔΣ, AC-coupled chopper/servo, active electrode or impedance boost) with measured/vendor/simulated evidence separately labeled. Calculate example margins only under invented inputs; declare **topology selection and numerical requirement freeze HOLD** until electrode/model/quality and safety owners provide inputs.
5. Add deterministic config/model/reports and focused negative tests for units, input range, source loading, bias and CMRR imbalance, offset/gain saturation, band/noise integration, anti-alias, OSR, missing physical inputs and source hashes. Run public regression and GitHub CI. Publish a gate with clear results and risks; CH08 behavioral implementation cannot claim requirement pass from unapproved CH07 targets.

## Proposed deliverables

`specs/biosignal/CH07_NUMERICAL_SCENARIOS.json`, `models/python/ch07_biopotential.py`, `verification/unit/test_ch07_biopotential.py`, generated `reports/block/CH07_NUMERICAL_SUMMARY.json`, `docs/budgets/CH07_BIOPOTENTIAL_REVIEW.md`, `docs/reviews/CH07_GATE.md`, and updated assumptions, issues, risk, traceability and state. The full block specification and topology ADR remain **held** until source models and limits are approved. No transistor sizing or body-connected drive circuitry in this chapter.
