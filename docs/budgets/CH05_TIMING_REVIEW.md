# CH05 conditional timing review

Regenerate with `python3 models/python/ch05_timing.py --write`; check with `--check`. Source: `specs/system/CH05_TIMING_SCENARIOS.json` (SHA-256 `7e059d5714195bce691b75c21069a4f146aa67249decc4589592969cd05cf96c`). All clocks, latency, ppm and IMU data are **assumed**. The [CH05 literature review](../literature/timing/2026-09-25_STATE_OF_ART_REVIEW.md) was merged before this model.

## Clock tree and quantization

Concept: retained slow AON owns sleep continuity; fast capture exists only while awake. On wake, latch an AON epoch and restart fine relative time; an alternative continuous high-rate AON timer is compared, not selected. The [minimal SystemVerilog counter](../../rtl/timestamp/ch05_continuous_reference.sv) covers only this continuously clocked comparison. No SV simulator is available in this workspace; it is not an RTL verification result. No clock source, PLL, reset tree or silicon cell is approved.

| Synthetic domain | Period (µs) | Candidate ≤1 µs resolution while running |
|---|---:|---|
| AON | 30.517578 | No; LF capture is coarse |
| Awake fine | 0.5 | Tick only; inter-domain accuracy unproven |
| Continuous comparison | 1.0 | Tick only; power/retention unproven |

Illustrative handoff, monotonic microseconds: awake 990000, sleep 1199981, awake after wake 1259999. Continuous comparator sleep read 1200000. Coarse wake handoff uncertainty upper bound 32 µs, excluding clock tolerance. The model clamps a late coarse snapshot to preserve monotonicity and can repeat labels; this does **not** prove 1 µs cross-mode accuracy. Counter width is 64 bits, while its unit and elapsed-gap half-range rule remain separate from physical reset/retention proof.

## Triggers, crossings and error accounting

Every entry in `trigger_matrix` maps one of LED, optical ADC, EEG/ECG, audio, electrochemical, IMU sync, GPIO or DMA to a target. Simultaneous arrivals keep configured source priority and a sequence number even when timestamps tie. Example ordering: LED_PULSE, IMU_SYNC, GPIO. A trigger timestamp names its nominal sample aperture; source event time, captured edge, CDC latency and sensor aperture are separate values. **An event during sleep needs a wake-capable destination or retained queue; this is unproved.**

| Source | Conditional target |
|---|---|
| LED_PULSE | OPTICAL_ADC |
| OPTICAL_ADC | DMA |
| EEG_ECG | DMA |
| AUDIO_FRAME | DMA |
| ECHEM_WAVEFORM | DMA |
| IMU_SYNC | DMA |
| GPIO | EEG_ECG |
| DMA | GPIO |

| Worst-case bound term | Awake (ns) | Sleep (ns; end-to-end path unavailable) |
|---|---:|---:|
| Next source edge | 500 | 30518 |
| CDC destination phase | 500 | unavailable |
| CDC pipeline nominal | 500 | unavailable |
| Sample aperture jitter | 500 | unavailable |
| Trigger→sample envelope including nominal latency | 6500 | unavailable |
| Host drift over assumed resync interval | 2000000 | 2000000 |

Bounds sum conservatively; trigger→sample envelope is **latency plus uncertainty**, not an accuracy guarantee or a measured jitter value. Host drift (hypothetical 20 ppm over 100 s) is 2,000,000 ns, distinct from the 100,000 ns example exchange uncertainty and capture phase. Clock PVT, metastability MTBF, calibration error, signal conditioning and analog sample aperture are not represented. A 2-flop CDC alone does not preserve repeated/short events. Each multi-bit crossing needs a coherent snapshot/acknowledgment or FIFO, and each reset release/clock transition needs future RDC/CDC and glitch checks.

| Crossing | Candidate handling / review needed | Status |
|---|---|---|
| AON → fine timer snapshot | coherent handshake with retained epoch and acknowledgment | model only |
| async event → destination | captured/acknowledged event or queued toggle; no bare short pulse | model only |
| timestamp/descriptor → host/DMA | stable multi-bit handshake or async FIFO; no separate bit flops | model only |
| reset/clock transition → each domain | async assert, synchronized release and glitch-free switch proof pending | physical hold |

## IMU and gate

Example IMU anchor index 5, FIFO sample index 3 reconstructs sample aperture 1248000000 ns with uncertainty 102000 ns **before anchor-capture error**. The later FIFO read arrival 1300000 µs never substitutes for aperture time. Model requires known sync edge, sample index, sample period, pipeline delay and delay spread; actual part, FIFO conventions and orientation remain unresolved.

**Decision: MODEL_PASS / PHYSICAL_TIMING_HOLD.** No approved biomarker accuracy/retention/clock power, selected IMU, per-sensor latency, product clock/reset implementation, host exchange precision or physical CDC/RDC results. Do not freeze the timing tree, expose this invented trigger matrix as a software contract or begin CH06. See [CH05 gate](../reviews/CH05_GATE.md) and `docs/inputs/REQUIRED_INPUTS.md`.
