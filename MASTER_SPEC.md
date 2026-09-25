# Physiological Computing Platform
## Master ASIC / SiP Requirements Specification + Execution Plan for GPT-6 Astra Work Mode

**Document role:** Authoritative starting specification for a new GPT-6 Astra Work-mode engineering project and GitHub repository.  
**Project type:** Ultra-miniaturized, ultra-low-power, high-performance heterogeneous physiological-computing ASIC/SiP for a head-worn wearable.  
**Status:** Candidate requirements baseline. CH00–CH02 passed limited repository, provisional-register and scenario-accounting gates. CH03 has a passing synthetic energy-model gate but **physical battery/product feasibility remains on hold**; CH04 onward are not started. Numerical targets remain provisional pending measured evidence and architecture review. See `state/PROJECT_STATE.md` for the current execution point.
**Primary design philosophy:** Maximize physiological sensing capability, signal integrity, compute capability, energy efficiency, and functional density per mm²/mm³ without knowingly sacrificing measurement performance.  
**Important:** This document is a system and implementation specification, not a claim that any generated layout is tapeout-ready. Final tapeout requires the selected foundry PDK, licensed IP/macros, signoff EDA flow, DRC/LVS/ERC/PEX/STA/EM-IR/reliability closure, and engineering review.

---

# 0. OPERATING INSTRUCTIONS FOR GPT-6 ASTRA WORK MODE

## 0.1 Mission

Act as the primary engineering copilot for implementing the **Physiological Computing Platform** as a version-controlled silicon-development program.

Do **not** attempt to implement the entire system in one session.

The project must be executed as a sequence of bounded, independently reviewable, testable, version-controlled chunks. Every chunk must leave the repository in a coherent state, with all work saved, tests/results recorded, and project state updated before starting the next chunk.

The project shall progress:

```text
Requirements
    ↓
System architecture
    ↓
Numerical budgets
    ↓
Behavioral/reference models
    ↓
Block specifications
    ↓
RTL / Verilog-A / SPICE implementation
    ↓
Block verification
    ↓
Subsystem integration
    ↓
PDK mapping
    ↓
Transistor-level implementation
    ↓
Physical design
    ↓
Post-layout verification
    ↓
Full-chip signoff
    ↓
Tapeout release package
```

The governing principle is:

> Never trade verification discipline for speed. Never proceed from a failing gate by silently accepting an error. Record every assumption, waiver, risk, and unresolved item.

---

## 0.2 Repository persistence is mandatory

All meaningful engineering work must be stored in the Git repository.

At the beginning of every Work-mode session:

1. Pull/fetch the latest repository state.
2. Read:
   - this master specification,
   - `state/PROJECT_STATE.md`,
   - `state/DECISIONS.md`,
   - `state/OPEN_ISSUES.md`,
   - `state/RISK_REGISTER.md`,
   - `state/REQUIREMENTS_TRACEABILITY.csv`,
   - the active chunk specification.
3. Confirm the current branch and clean/dirty working tree.
4. Determine exactly one next bounded unit of work.
5. Define acceptance criteria before implementation.

At the end of every bounded unit of work:

1. Save source files.
2. Save scripts.
3. Save testbenches.
4. Save reports/results required to reproduce conclusions.
5. Update state files.
6. Run the defined regression/tests.
7. Record pass/fail.
8. Commit with a descriptive message.
9. Push to the remote repository if access permits.
10. Only then move to the next unit.

Do not leave important reasoning only in chat. Convert decisions into repository artifacts.

---

## 0.3 Commit discipline

Use small, atomic commits.

Preferred commit format:

```text
<type>(<subsystem>): <specific change>

Examples:
spec(biopotential): freeze EEG/ECG input dynamic-range requirements
model(optical): add photodiode shot-noise reference model
rtl(timestamp): implement 64-bit global timestamp counter
test(echem): add potentiostat saturation corner tests
fix(pmu): prevent illegal rail enable ordering
docs(state): record ADC architecture decision
```

Recommended `type` values:

- `spec`
- `arch`
- `model`
- `rtl`
- `analog`
- `test`
- `verify`
- `fix`
- `physical`
- `signoff`
- `docs`
- `build`
- `ci`

Never combine unrelated subsystems in one commit.

---

## 0.4 Branch strategy

Use `main` for merged reviewed milestones and `feature/CHxx-<short-name>` for active engineering chunks. A `develop` integration branch may be added if needed; the current repository does not use one. Historical baseline tags should point to real approved milestones; do not create a tag solely because a template lists it. Suggested future names:

```text
main
develop
feature/CHxx-<short-name>
fix/<short-name>
signoff/<milestone>
```

Rules:

- `main` = reviewed stable milestones only.
- `develop` = integrated engineering baseline.
- Feature branches = one chunk/subchunk.
- No direct experimental work on `main`.
- Merge only when acceptance criteria pass.
- Tag major baselines:
  - `arch-v0.1`
  - `ams-model-v0.1`
  - `rtl-v0.1`
  - `subsystem-v0.1`
  - `pdk-mapped-v0.1`
  - `prelayout-v0.1`
  - `postlayout-v0.1`
  - `tapeout-rc1`

---

## 0.5 Decision discipline

Every non-trivial architectural choice shall be captured in `state/DECISIONS.md` or individual ADRs under:

```text
docs/adr/
```

Use:

```text
ADR-XXXX: <title>

Status:
Context:
Decision:
Alternatives:
Why selected:
Consequences:
Risks:
Revisit trigger:
```

Examples:

- ADC sharing vs per-channel ADC
- continuous-time vs discrete-time delta-sigma
- 130 nm vs 180 nm precision analog
- separate PowerAudio die vs monolithic mixed-signal
- raw NAND vs managed NAND
- number of optical RX channels
- whether LED boost is shared with piezo HV
- whether NOR is retained once nRF internal NVM is sufficient

---

## 0.6 Assumption discipline

Never invent missing foundry/IP values.

Tag every requirement/parameter using:

- **MUST** — required for project success/safety.
- **SHOULD** — strong preference; deviation requires justification.
- **MAY** — optional.
- **STRETCH** — desirable if cost/area/power allow.
- **TBD** — intentionally unresolved pending analysis, PDK, vendor data, measurements, or product decision.

Any numerical value not yet validated must be marked as one of:

- `TARGET`
- `LIMIT`
- `PLACEHOLDER`
- `TBD`

---

## 0.7 Mandatory literature-first design gate

**No technical block may enter architecture selection, circuit design, RTL implementation, transistor sizing, or physical implementation before a documented state-of-the-art review has been completed for that block.**

For every block or materially new sub-block, the active chunk must begin with a **Literature and Prior-Art Survey**.

### Required source classes

Search and review, in priority order:

1. recent peer-reviewed journal papers,
2. recent high-quality conference papers,
3. semiconductor-vendor technical documentation and reference designs,
4. foundry/application/reference-design material,
5. recent patents where architecture/IP direction is relevant,
6. standards, regulatory guidance, and safety documents where applicable,
7. credible academic theses or technical reports when they add implementation detail,
8. teardown/reverse-engineering sources only as supplementary evidence.

### Recency rule

- Prefer material from the **most recent 5 years**.
- Include older seminal work when it remains architecturally important.
- For fast-moving blocks, explicitly search the **most recent 12–24 months**.
- Record publication year and source type.
- Do not assume an older architecture remains state-of-the-art without comparison.

### Minimum survey content

For each candidate block, produce:

```text
docs/literature/<block>/<YYYY-MM-DD>_STATE_OF_ART_REVIEW.md
```

The review must contain:

- block/function definition,
- target application conditions,
- search scope and keywords,
- reviewed sources with links/DOIs,
- state-of-the-art architectures,
- best reported measured performance,
- die/core area,
- power and energy/sample,
- supply voltage,
- input-referred noise,
- bandwidth,
- dynamic range,
- resolution/ENOB where relevant,
- process node,
- channel count,
- calibration method,
- test methodology,
- known limitations,
- failure modes,
- manufacturability concerns,
- safety concerns,
- packaging implications,
- comparison table,
- architecture trade study,
- lessons applicable to this project,
- identified knowledge gaps,
- recommended architecture,
- explicit reasons for rejecting alternatives.

### Evidence hierarchy

Do not select an architecture merely because it is familiar.

The recommendation must be grounded in:
- measured silicon results where available,
- reproducible technical evidence,
- application fit,
- area efficiency,
- energy efficiency,
- signal quality,
- process compatibility,
- manufacturability,
- integration risk.

### Literature-consumption requirement

Do not merely collect links.

The active design task must demonstrate that the literature was **consumed and incorporated** by explicitly documenting:

```text
Finding → Engineering implication → Design decision
```

Example:

```text
Finding:
Recent chopper EEG AFEs show residual ripple caused by switching artifacts and mismatch.

Engineering implication:
Chopper frequency, switch sizing, ripple-reduction technique, amplifier bandwidth, and post-chop filtering must be co-designed.

Design decision:
Benchmark nested-chopping/ripple-reduction against auto-zero and conventional chopper-stabilized alternatives before OTA sizing.
```

### Literature gate acceptance criteria

A block may proceed to design only after:

- the survey is saved in Git,
- major architecture families have been compared,
- at least one quantitative benchmark table exists,
- measured-silicon results are separated from simulations,
- unresolved contradictions are documented,
- the proposed architecture is justified,
- relevant requirement IDs are linked,
- the review is committed.

Recommended commit:

```text
research(<block>): complete state-of-art architecture survey
```

Only after this commit may the corresponding design work begin.

### Re-survey trigger

Repeat or update the survey if:

- the architecture changes materially,
- a new sensor/transducer type is introduced,
- the foundry/process changes,
- a major performance requirement changes,
- a newer relevant publication materially changes the design space,
- the previous survey is more than 12 months old before tapeout freeze.

---

## 0.8 Global optimization law — extreme area/volume/power optimization without quality or performance compromise

The design shall **always** optimize aggressively for:

1. minimum custom-die area,
2. minimum package area,
3. minimum package height/volume,
4. minimum external component count,
5. minimum average power,
6. minimum energy per sample/event/inference,
7. minimum leakage,
8. minimum quiescent current,
9. minimum data movement,
10. minimum inter-die/interconnect energy,
11. minimum wake-up overhead,
12. maximum functional density per mm² and mm³,

**subject to a hard constraint: required performance, signal quality, safety, reliability, manufacturability, and validation margin shall never be degraded merely to save space or power.**

Treat every design decision as a constrained multi-objective optimization problem:

```text
Minimize:
    die area
    package footprint
    package height
    average power
    leakage
    energy/sample
    energy/event
    energy/bit moved
    external BOM
    interconnect overhead

Subject to:
    measurement accuracy >= requirement
    input-referred noise <= limit
    dynamic range >= requirement
    bandwidth >= requirement
    linearity >= requirement
    timing/jitter <= limit
    safety requirements satisfied
    reliability requirements satisfied
    PVT margin satisfied
    Monte-Carlo yield target satisfied
    manufacturability acceptable
    thermal limits satisfied
```

### Non-negotiable design rule

If a smaller or lower-power implementation causes a required quality/performance/safety/reliability metric to fail, **reject that optimization** unless the corresponding system requirement is formally revised through a reviewed ADR supported by system-level evidence.

### Optimization techniques that must always be evaluated where applicable

- architecture-level duty cycling,
- current reuse,
- switched-capacitor reuse,
- shared references and bias generators,
- shared calibration resources,
- shared ADCs only where required simultaneity is preserved,
- simultaneous converters where cross-sensor timing demands them,
- inverter-based analog where noise/linearity/headroom remain adequate,
- subthreshold/near-threshold digital where robust across PVT,
- dynamic voltage/frequency scaling,
- aggressive clock gating,
- fine-grained power gating,
- retention only where justified,
- banked SRAM,
- event-driven acquisition,
- compressed/local processing to reduce memory movement,
- adaptive sample rate,
- adaptive LED current,
- adaptive TIA/PGA gain,
- adaptive integration time,
- autonomous wake/sleep,
- hardware filtering before host transfer,
- stacked dies,
- RDL/fan-out integration,
- embedded/co-packaged passives,
- elimination of redundant package interfaces,
- lowest viable supply voltage with adequate analog headroom,
- reuse of test/calibration infrastructure,
- physical co-design of die + package + transducers,
- source/sensor multiplexing only when leakage, settling, crosstalk, and concurrency remain acceptable.

### Quantified proof required for every optimization

Every substantial area/power optimization must include a before/after comparison:

| Metric | Before | After | Requirement | Pass? |
|---|---:|---:|---:|---|
| Area | | | | |
| Average power | | | | |
| Energy/event | | | | |
| Noise | | | | |
| SNR/SNDR | | | | |
| ENOB | | | | |
| Bandwidth | | | | |
| Dynamic range | | | | |
| Latency | | | | |
| Startup energy | | | | |
| PVT margin | | | | |
| Monte-Carlo yield | | | | |
| Reliability impact | | | | |

An optimization is not accepted because it “looks smaller.” It must prove that constrained specifications remain satisfied.

---

# 1. PROJECT OBJECTIVE

Create an extreme-density head-worn wearable electronics platform capable of sensing, stimulating, processing, storing, and wirelessly communicating a broad range of physiological information while remaining optimized for:

1. **Minimum PCB/package footprint**
2. **Minimum average power**
3. **Minimum analog input-referred noise**
4. **Maximum signal dynamic range**
5. **High simultaneous sensor capability**
6. **Cross-sensor timing determinism**
7. **Scalability to future sensing modalities**
8. **Manufacturability**
9. **Testability**
10. **Clinical/research-grade raw-data accessibility where feasible**
11. **High product reliability**
12. **Robust safety for body-connected interfaces**
13. **Long-term architectural flexibility**

The design must preserve approximately **10% uncommitted physical/resource headroom** for future functionality.

---

# 2. SYSTEM-LEVEL ARCHITECTURAL PRINCIPLE

## 2.1 One package, not necessarily one process

The preferred architecture is a **heterogeneous System-in-Package (SiP)** behaving externally as one physiological compute/sensing module.

Do not force all functions into one monolithic semiconductor process if doing so worsens:

- noise,
- leakage,
- power conversion efficiency,
- RF performance,
- MEMS performance,
- memory density,
- yield,
- schedule,
- NRE,
- reliability.

Preferred die partition:

```text
Heterogeneous Physiological Computing SiP
│
├── Die A: Nordic nRF-class MCU/RF die
├── Die B: platform BioSense mixed-signal ASIC
├── Die C: platform PowerAudio / PMIC / BMS ASIC
├── Die D: MEMS IMU die / packaged MEMS element
├── Die E: High-density NAND
├── Die F: Optional high-performance NOR
├── Embedded / co-packaged passives
└── Package RDL/substrate/interconnect
```

This partition may change after quantitative analysis.

---

# 3. CURRENT PLATFORM CONTEXT TO PRESERVE

The existing platform direction includes:

- head-worn wearable.
- Extremely small mechanical envelope.
- Metallic/mechanically constrained enclosure.
- Very small battery, approximately 8–14 mAh usable in current architecture.
- Existing MCU direction: Nordic nRF54LM20B-class device.
- Existing IMU direction: ST LSM6DSV16BX-class device.
- Existing optical AFE investigations include MAXM86161-class concepts.
- Existing physiological AFE investigations include AFE4510-class concepts.
- Existing flash direction includes small 1.8-V serial NOR.
- Existing power architecture uses multiple discrete buck/boost/regulator ICs.
- Existing piezo/haptic/audio experiments use boosted drive architectures.
- Existing SiP exploration is approximately an 8 mm × 8 mm class module.
- Existing thermal work includes skin + ambient temperature and heat-flux/thermopile concepts.
- Existing electrode work includes dry electrodes and QVAR/capacitive/on-body sensing.
- Existing sensor synchronization and multimodal physiology are strategically important.

These are starting-context constraints, not immutable implementation choices.

---

# 4. TOP-LEVEL FUNCTIONAL REQUIREMENTS

The platform shall be capable of interfacing with and/or processing:

## 4.1 Electrophysiology
- EEG
- ECG
- optional EMG-like future use
- electrode impedance
- reference/bias electrode management

## 4.2 Electrodermal / impedance
- EDA / GSR
- skin impedance
- bioimpedance
- contact quality
- capacitive/QVAR-like sensing
- hydration-related impedance research

## 4.3 Electrochemical / sweat / biochemical
- glucose-oriented electrodes
- hormone-oriented electrodes
- Na⁺ ion-selective electrodes
- K⁺ ion-selective electrodes
- sweat conductivity
- sweat rate auxiliary sensing interface
- pH-oriented electrodes
- lactate-oriented electrodes
- chloride or additional ion-selective electrodes
- future electrochemical biosensors
- potentiometric sensing
- amperometric sensing
- voltammetric sensing
- electrochemical impedance spectroscopy

## 4.4 Optical
- conventional PPG
- SpO₂-oriented red/NIR PPG
- multispectral PPG
- hemoglobin-related optical analysis
- melanin estimation
- carotenoid-related optical experiments
- AGE/autofluorescence-oriented UV/near-UV excitation + detection
- additional LEDs / laser-driver interfaces if future spectroscopy requires
- multiple photodiodes
- multiple source-detector separations
- reflectance spectroscopy
- fluorescence measurements
- future optical sensing modalities

## 4.5 Mechanical / inertial / acoustic
- IMU
- accelerometer
- gyroscope
- bone-conduction microphone
- contact microphone
- piezoelectric vibration sensor
- analog MEMS microphone
- digital PDM microphone
- bone-conduction speaker
- conventional miniature speaker/receiver interface if required
- full-range audio processing

## 4.6 Thermal
- skin temperature
- ambient temperature
- precision NTC interfaces
- silicon temperature sensing
- thermopile / heat-flux sensor interface
- future thermal-gradient sensors

## 4.7 Cardiovascular inference support
Provide high-quality synchronized raw acquisition suitable for:
- pulse-arrival-time research
- pulse-transit-time research where physically supportable
- ECG/PPG timing
- BCG/PPG/ECG fusion
- cuffless BP research
- heart-rate
- HRV
- pulse morphology
- peripheral perfusion metrics

No requirement shall imply that cuffless BP is inherently clinically accurate without validation/calibration.

---

# 5. RESERVED FUTURE CAPACITY — MANDATORY

The physical design shall deliberately preserve future capacity.

## 5.1 Die-area reserve
**TARGET:** Preserve at least **10% of usable custom-die core area** as intentionally uncommitted reserve at architecture freeze; finalize the denominator and feasibility after floorplan/PDK data.

The reserve shall not be consumed merely to improve placement density unless approved by architecture review.

## 5.2 Package reserve
**SHOULD:** Preserve:
- spare package/RDL routing channels,
- spare ground/power bumps where practical,
- at least several spare signal bumps/pads,
- substrate routing headroom,
- thermal headroom.

## 5.3 Analog reserve
**SHOULD:** Provide some combination of:
- 2–4 spare configurable analog inputs,
- 2 spare low-leakage electrode-capable inputs,
- 2 spare DAC/current-DAC outputs,
- spare ADC mux capacity,
- test-access routing that can later be repurposed.

## 5.4 Digital reserve
**MUST:** Maintain:
- ≥10% synthesis area headroom at subsystem signoff,
- ≥10% average memory-bandwidth headroom under worst supported concurrent use,
- spare interrupt/event IDs,
- spare register address space,
- spare DMA channel IDs or extensible descriptor architecture.

## 5.5 Power reserve
**SHOULD:** PMIC sizing shall include reasonable future transient-current headroom without degrading efficiency excessively.

---

# 6. ARCHITECTURE PARTITION

# 6.1 Die A — nRF MCU / RF

Preferred initial strategy:

- Use Nordic nRF54LM20B-class MCU/RF as a separate die or smallest practical package.
- If bare-die procurement is feasible, consider SiP integration.
- Do not attempt to recreate Nordic BLE/RF IP in Gen-1.
- Preserve a clean high-speed digital interface between nRF and BioSense ASIC.
- Preserve independent power gating/reset domains.
- Support OTA firmware and secure boot through the nRF ecosystem.

Functions assigned primarily to nRF:
- BLE / 2.4-GHz communication
- high-level product firmware
- user/application logic
- higher-level algorithms
- ML inference where appropriate
- storage management policy
- external communications
- secure OTA/update
- UI/event logic

---

# 6.2 Die B — BioSense ASIC

Primary proprietary sensor-computing die.

Main blocks:

```text
BIO8          EEG/ECG biopotential AFE
Z4            EDA/BioZ/capacitive AFE
ECHEM8        Electrochemical / ISE / sweat interface
OPT_RX12      Optical photodiode receive array
LED_TX16      Optical emitter current-driver array
PREC_AFE4+    Thermopile / NTC / precision auxiliary AFE
AUDIO_IN4     Bone/contact/analog microphone input
PDM_IF        Digital microphone interfaces
ADC_BANKS     Multiple precision and fast converters
DAC_BANKS     Precision DAC/current-DAC waveform generation
AON_CTRL      Always-on controller
DSP           Continuous low-power DSP accelerators
TIMEBASE      Global timestamp/synchronization engine
DMA/FIFO      Data movement and buffering
SRAM          Local sensor memory
OTP/eFuse     Calibration/trim/identity
TEST/BIST     Production test and self-test
HOST_IF       nRF host interface
```

---

# 6.3 Die C — PowerAudio ASIC

Candidate BCD/mixed-signal power die.

Functions:

- battery charger
- battery protection
- coulomb counter
- fuel gauge measurement front end
- power-path management
- ship mode
- storage mode
- multiple buck regulators
- optional buck-boost
- low-noise analog LDOs
- load switches
- LED boost
- optional piezo/high-voltage boost
- audio DAC power stage / Class-D
- bone-conduction transducer driver
- power sequencing
- hardware safety supervision
- thermal monitoring
- rail telemetry

---

# 6.4 Die D — IMU

Keep MEMS as specialized technology.

Requirements:
- accelerometer + gyroscope
- low-noise motion sensing
- low-power always-on capability
- FIFO
- programmable interrupts
- synchronization input/output if available
- precise timestamp relationship with the master timebase
- SPI preferred for high-rate data; I3C/I²C optional
- package orientation explicitly documented

---

# 6.5 Die E/F — Memory

Candidate hierarchy:

1. nRF internal NVM for boot/critical firmware.
2. Optional high-speed NOR for:
   - fast random access,
   - model storage,
   - fallback image,
   - deterministic reads.
3. NAND for:
   - long-duration physiological logging,
   - raw EEG,
   - audio,
   - optical research data,
   - event capture.

Architecture decision must compare:
- NOR-only
- NAND-only + nRF internal NVM
- NOR + NAND
- managed NAND vs raw NAND
- PSRAM/SRAM addition if required

---

# 7. BIOSIGNAL FRONT END — EEG / ECG

## 7.1 Channel count
**TARGET:** 8 simultaneous differential biopotential channels.

## 7.2 Supported use
Each channel should be software-configurable for:
- EEG
- ECG
- future low-frequency biopotential
- reference/measurement support

## 7.3 Input requirements
Targets to be validated during noise-budget phase:

- input impedance: **>1 GΩ**, preferably much higher at relevant frequency
- input bias/leakage: minimized; low enough not to corrupt dry-electrode measurements
- differential input range: sufficient for µV–mV physiological signals
- electrode DC offset tolerance: **TARGET ±300 mV or better**
- CMRR: **TARGET >100 dB**
- PSRR: high across physiological band and switching-noise frequencies
- input-referred noise:
  - EEG band target: **≤0.5–1 µVrms**
  - exact bandwidth must be stated with every noise result
- programmable gain:
  - nominal **×1 to ×128** or equivalent total path configurability
- programmable HP/LP path or digital equivalent
- anti-aliasing
- saturation detection
- electrode-open detection
- electrode impedance test

## 7.4 Bandwidth
Configurable profiles:
- EEG: ~0.1 Hz to 250 Hz baseline target
- ECG: ~0.05 Hz to 500 Hz baseline target
- research mode: extend to ~1 kHz if power permits

## 7.5 Sampling
Per-channel:
- 250 SPS
- 500 SPS
- 1 kSPS
- 2 kSPS
- 4 kSPS
- optional 8 kSPS research mode

## 7.6 ADC
Nominal:
- delta-sigma architecture
- “24-bit class” is acceptable as implementation label
- actual requirement shall be specified in:
  - input-referred noise
  - SNR
  - SNDR
  - ENOB
  - bandwidth
  - power

Do not accept bit-depth marketing without noise validation.

## 7.7 Input switching
Provide low-leakage analog crosspoint/mux to enable flexible electrode routing where feasible.

Mux leakage, charge injection, capacitance, ESD leakage, and crosstalk must be included in validation.

## 7.8 Body-connected safety
Hardware-limited currents.
No firmware state may permit unsafe electrode stimulation current.

---

# 8. EDA / GSR / BIOIMPEDANCE / CAPACITIVE SENSING

## 8.1 Channel count
**TARGET:** 4 configurable channels.

## 8.2 Modes
- DC conductance / EDA
- AC impedance
- electrode contact impedance
- tissue impedance research
- capacitive sensing
- on-body/off-body sensing
- QVAR-like measurement
- synchronous lock-in detection

## 8.3 Excitation
Provide programmable:
- voltage excitation
- current excitation if justified
- amplitude
- frequency
- phase
- waveform

Potential frequency range:
- **TARGET 0.1 Hz to 1 MHz**
- exact upper limit to be derived from architecture/power/noise analysis

## 8.4 Receive path
- programmable TIA / voltage receiver
- synchronous demodulator
- I/Q measurement desirable
- magnitude/phase calculation support
- saturation detection
- calibration loopback

---

# 9. ELECTROCHEMICAL / Na⁺ / K⁺ / SWEAT SENSING

This block must support both **potentiometric ion-selective electrodes** and **amperometric/voltammetric biosensors**.

A conventional potentiostat alone is insufficient for all Na⁺/K⁺ sensors.

## 9.1 Universal electrochemical channel target
**TARGET:** 8 configurable electrochemical channels.

Recommended internal structure:
- at least 4 full 3-electrode potentiostat-capable channels
- all 8 capable of high-input-impedance potentiometric measurement if feasible
- multiplexed/shared reference-electrode support configurable by firmware
- independent working-electrode paths

## 9.2 Supported sensor types
- glucose oxidase / amperometric research electrodes
- lactate
- cortisol/hormone electrodes
- Na⁺ ISE
- K⁺ ISE
- pH
- chloride
- other ion-selective membranes
- sweat conductivity
- generic future electrochemical sensors

## 9.3 Potentiometric / ISE mode
Need:
- very-high-input-impedance buffer
- ultra-low input bias current
- low leakage input protection
- low offset and low drift
- stable measurement over very slow timescales
- differential measurement against reference electrode
- programmable common-mode accommodation
- temperature compensation inputs

**TARGET input impedance:** ≥10¹² Ω, preferably ≥10¹³ Ω where process/ESD allows.  
**TARGET input bias:** pA-class or lower if feasible.  
Final values must be PDK-backed.

## 9.4 Na⁺ / K⁺ support
ISE outputs are approximately Nernstian and temperature-dependent.

The digital path shall support:
- 2-point and multi-point calibration
- slope calibration
- offset calibration
- temperature compensation
- reference electrode drift tracking
- cross-sensitivity metadata
- per-electrode calibration storage
- raw mV output retention
- concentration conversion in software, not hard-coded analog

## 9.5 Amperometric mode
Support large current range.

**TARGET measurable current span:** roughly **100 pA to 100 µA** through configurable TIA ranges.

Provide:
- programmable feedback resistance/capacitance
- low-bias input switching
- saturation recovery
- current polarity support if required
- auto-ranging
- guard structures for ultra-low currents

## 9.6 Potentiostat function
For selected channels:
- working electrode (WE)
- reference electrode (RE)
- counter electrode (CE)
- control amplifier
- programmable cell bias
- precision bias DAC
- TIA measurement
- open-circuit potential mode

## 9.7 Electrochemical techniques
Support waveform/sequencing primitives for:
- chronoamperometry
- chronopotentiometry where appropriate
- potentiometry
- cyclic voltammetry
- square-wave voltammetry
- differential-pulse voltammetry
- electrochemical impedance spectroscopy
- open-circuit potential
- pulsed cleaning/conditioning sequences within safety limits

## 9.8 Sweat-specific support
The platform should support research integration for:
- Na⁺
- K⁺
- pH
- chloride
- lactate
- glucose
- sweat conductivity
- temperature
- sweat-rate sensor input

Do not imply biomarker accuracy without transducer/chemistry validation.

## 9.9 Electrochemical waveform generation
Precision DAC requirements:
- low noise
- low glitch
- monotonic
- programmable slew
- calibration
- sufficient voltage span to support intended cell biases

## 9.10 Reference electrode considerations
Architecture must analyze:
- one shared reference vs multiple references
- leakage through muxes
- input protection leakage
- polarization
- common-mode range
- electrochemical cross-talk
- sequencing when multiple channels share a reference

---

# 10. OPTICAL / PPG / SPECTROSCOPY ENGINE

The optical subsystem shall be designed as a general **multispectral optical measurement engine**, not only a heart-rate PPG block.

## 10.1 Optical transmitter channels
**TARGET:** 16 programmable LED/current-driver outputs.

Potential sources include:
- UV / near-UV
- violet
- blue
- green
- amber
- red
- deep red
- NIR
- additional wavelengths TBD

External optical emitters remain outside CMOS.

## 10.2 LED driver requirements
Per channel:
- programmable peak current
- **TARGET 0–150 mA peak** subject to device/package/thermal limits
- fine current resolution, target ~10–12 effective bits
- µs-level or better timing control
- programmable pulse width
- programmable phase/order
- open/short detection
- current monitoring/calibration
- hardware max-current limit
- thermal/safety interlock
- independent enable
- support time-multiplexed wavelengths

## 10.3 Optical receive channels
**TARGET:** 12 photodiode receive channels.

At least 8 should support truly simultaneous acquisition if architecture permits.

## 10.4 Photodiode AFE
Each channel shall consider:
- programmable TIA
- low-noise input
- ambient cancellation
- programmable offset cancellation
- programmable integration time
- low leakage
- saturation detection
- dark measurement
- multiple gain ranges
- source-detector synchronization
- optional correlated double sampling
- shot-noise-aware gain control

**TARGET TIA equivalent range:** approximately 1 kΩ to >10 MΩ through switched R/C or equivalent architecture.

## 10.5 Optical modes
Must support:
- conventional PPG
- multiwavelength PPG
- red/NIR SpO₂ research
- reflectance spectroscopy
- fluorescence
- autofluorescence
- source-detector distance experiments
- dark/ambient subtraction
- multi-PD spatial measurements

## 10.6 Hemoglobin / melanin
Hardware should provide raw multispectral data and calibration support.

Do not hard-code biomarker algorithms into fixed analog circuitry unless there is overwhelming power benefit.

## 10.7 AGE/autofluorescence support
Provide:
- UV/near-UV LED drive capability
- weak fluorescence receiver mode
- high TIA gain
- dark subtraction
- reference optical measurement
- synchronous detection
- optical filter support at package/mechanical level

## 10.8 UV safety
**MUST:** implement hardware UV exposure limiting.

Track a calibrated electrical drive proxy for fault detection:

```text
Drive_proxy = Σ (calibrated electrical drive × pulse duration)
```

This proxy is **not** a radiometric exposure measurement or proof of photobiological safety. Before enabling a UV product mode, measure accessible spectral optical output in the actual optical/mechanical geometry, establish the applicable exposure criteria with qualified safety review, and translate the resulting safe limits into independently enforced hardware current, pulse, duty-cycle, and cumulative limits. Hardware must disable UV output on violation independent of MCU firmware. Record the safety assessment and applicable standards for the intended market and use; do not infer a universal safe electrical-current limit from this equation.

## 10.9 Carotenoid support
Do not assume a standard LED + PD channel is equivalent to Raman spectroscopy.

Provide electrical flexibility for:
- external narrow-line source driver
- high-sensitivity optical receive
- synchronous timing
- possible external spectrometer interface

Treat Raman implementation as a separate optical subproject.

## 10.10 Adaptive optical control
Hardware/firmware should dynamically optimize:
- LED current
- TIA gain
- integration time
- sample rate
- wavelength schedule
- PD selection

Objective:
maximize usable SNR per joule while avoiding saturation.

---

# 11. THERMAL / PRECISION AUXILIARY AFE

## 11.1 Temperature channels
**TARGET:** 4–8 low-speed precision channels.

Support:
- NTC
- resistive sensors
- silicon sensor interfaces
- auxiliary low-frequency voltage sensors

## 11.2 NTC measurement
Prefer:
- ratiometric excitation
- switchable excitation
- precision reference
- duty cycling
- self-heating minimization
- calibration coefficients stored digitally

## 11.3 Thermopile / heat-flux channel
Dedicated precision low-frequency path.

Existing use case:
- J30-like thermopile
- source resistance ~kΩ-class
- signal ~100 µV-class under representative heat flux

Target AFE:
- chopper/auto-zero architecture
- PGA
- very low 0.1–10 Hz noise
- very low offset
- low offset drift
- DC-capable
- low input current

Initial design targets:
- input offset: **<5 µV**, aspirational 1–2 µV
- drift: **<0.05 µV/°C** target
- 0.1–10 Hz noise: **<0.5–1 µVpp**
- PGA: ×1 / ×2 / ×4 / ×8 / ×16 / ×32 / ×64 / ×128 or equivalent
- bandwidth: DC to ~10 Hz configurable

These targets require PDK validation.

---

# 12. AUDIO / BONE-CONDUCTION INPUT

## 12.1 Input types
Support:
- analog MEMS microphone
- digital PDM microphone
- piezo contact microphone
- bone-conduction contact transducer
- auxiliary vibration sensor

## 12.2 Audio channels
**TARGET:** 4 input channels total, including analog/PDM combinations.

## 12.3 Analog audio ADC
Target:
- 24-bit class
- 48 kHz baseline
- 96 kHz optional
- high dynamic range
- low input-referred noise
- programmable gain
- microphone bias
- anti-aliasing

Again, effective performance matters more than nominal bits.

## 12.4 Piezo/contact input
Need:
- high-input-impedance path
- charge-amplifier option
- programmable gain
- DC protection
- wide dynamic range
- mechanical vibration bandwidth suitable for bone-conduction sensing

## 12.5 Digital microphone
Support:
- PDM
- configurable clock
- decimation
- stereo/multi-mic support if pins permit

---

# 13. AUDIO / BONE-CONDUCTION OUTPUT

## 13.1 Full-range audio objective
Electrical path should support approximately:
- 20 Hz to 20 kHz full-range output capability
- actual transducer bandwidth may be narrower

## 13.2 Output architectures
Support at least one or both:
- low-impedance electromagnetic bone-conduction actuator through Class-D
- piezoelectric actuator through high-voltage boost + H-bridge

## 13.3 Audio DAC
Target:
- 24-bit class digital audio path
- 48/96 kHz
- low idle noise
- mute/pop suppression
- programmable volume
- limiter

## 13.4 DSP support
Provide primitives for:
- biquad filters
- FIR
- EQ
- limiter
- compressor
- mixing
- sample-rate conversion
- optional beamforming primitives

## 13.5 Power reality
Audio shall be treated as a high-power mode.

For ~10 mAh battery class:
- continuous tens-of-mW audio cannot coexist with multi-day battery life.
- system firmware must enforce duty-cycle/product-mode policies.

---

# 14. IMU INTERFACE AND SYNCHRONIZATION

## 14.1 IMU remains specialized MEMS
Do not implement mechanical MEMS structures in the BioSense die.

## 14.2 Interface
Preferred:
- SPI
- optional I3C/I²C

## 14.3 Synchronization
Need:
- hardware interrupt input
- sample-ready trigger
- optional sync pulse output from the master timebase
- timestamp correction
- FIFO drain DMA support

## 14.4 Orientation
Physical axis mapping must be documented in package and product coordinate frames.

---

# 15. ADC ARCHITECTURE REQUIREMENTS

Initial target bank:

| Bank | Qty | Candidate architecture | Nominal class | Intended use |
|---|---:|---|---:|---|
| BIO ADC | 8 | ΔΣ | 24-bit class | EEG/ECG |
| ECHEM ADC | 4–8 | incremental/ΔΣ | 20–24-bit class | potentiostat / ISE |
| OPT ADC | 8 minimum simultaneous | ΔΣ/SAR/integrating | 18–20-bit class | PPG/spectroscopy |
| PREC ADC | 4 | precision ΔΣ | 20–24-bit class | thermopile/temp |
| FAST ADC | 2 | SAR | 14–16-bit | 1–5 MSPS research/aux |
| AUDIO ADC | up to 4 | audio ΔΣ | 24-bit class | microphones |
| PMIC ADC | separate on Power die | SAR | 14–16-bit class | battery/rails |

This is intentionally capability-rich and may be reduced after area/power modeling.

## 15.1 ADC specification methodology
Every ADC must be specified by:
- full-scale
- input common-mode
- bandwidth
- sample rate
- input-referred noise
- SNR
- SNDR
- THD
- INL
- DNL
- ENOB
- clock sensitivity
- reference sensitivity
- power
- startup time
- calibration
- PVT
- Monte Carlo
- area

---

# 16. DAC REQUIREMENTS

Initial target:

## 16.1 Precision voltage DAC
**TARGET:** 8 channels, 16–18-bit class.

Uses:
- electrochemical bias
- test stimulation
- calibration
- offset cancellation
- sensor excitation

## 16.2 LED current DAC
**TARGET:** 16 independently programmable current channels.

## 16.3 Fast waveform DAC
**TARGET:** 2–4 channels, 12–16-bit class.

Uses:
- impedance spectroscopy
- diagnostic waveform generation
- research stimulation within safe limits

## 16.4 DAC quality metrics
Specify:
- monotonicity
- INL/DNL
- noise
- settling
- glitch energy
- output range
- output drive
- power
- temperature drift

---

# 17. SENSOR TIMING ENGINE

## 17.1 Global timebase
All sensor streams shall map to one master monotonic timestamp domain.

**TARGET resolution:** ≤1 µs.  
**STRETCH:** substantially better if low-power clocking permits.

## 17.2 Timestamp width
**MUST:** avoid rollover during any realistic logging session.
Recommend 64-bit internal timestamp representation.

## 17.3 Hardware-trigger matrix
Provide programmable triggering between:
- LED pulse
- optical ADC sample
- EEG/ECG sample
- audio frame
- electrochemical waveform
- IMU sync
- GPIO event
- DMA event

## 17.4 Determinism
Document:
- trigger-to-sample latency
- jitter
- domain-crossing uncertainty

---

# 18. ALWAYS-ON CONTROLLER

A tiny always-on controller shall operate while main nRF and most sensor domains sleep.

Responsibilities:
- wake scheduling
- contact/on-body detection
- basic sensor-quality checks
- low-rate temperature
- battery supervision
- event detection
- power sequencing
- watchdog
- sensor duty cycling
- safe shutdown
- wake nRF only when necessary

Target power:
- **Aggressive target: single-digit to tens of µW**, dependent on enabled functions.

---

# 19. LOW-POWER DSP ACCELERATORS

Candidate hardware accelerators:
- CIC
- FIR
- IIR / biquad
- decimation/interpolation
- FFT
- correlation
- RMS
- mean/variance
- peak detection
- envelope detection
- lock-in amplifier
- synchronous demodulation
- I/Q accumulation
- PPG ambient subtraction
- LED adaptive-control statistics
- sensor-quality metrics
- matrix/vector MAC where area-efficient
- optional compression primitives

Do not implement a large generic AI accelerator if nRF NPU already covers high-level ML efficiently.

---

# 20. SENSOR QUALITY METADATA

Each sample/frame should support quality metadata where appropriate.

Examples:

## EEG/ECG
- saturation
- electrode-open
- electrode impedance
- motion contamination
- gain state
- overload recovery

## Optical
- wavelength ID
- LED current
- TIA gain
- integration time
- ambient level
- saturation
- dark level
- motion flag

## Electrochemical
- range
- cell bias
- TIA gain
- reference status
- saturation
- temperature
- calibration ID

## Thermal
- excitation state
- calibration state
- saturation
- settling state

---

# 21. LOCAL SRAM / FIFO

Initial target:
- **512 KB to 2 MB** local SRAM, final value to be derived.

Uses:
- sensor FIFO
- DMA buffering
- DSP workspace
- burst absorption
- nRF wake minimization

Requirements:
- banked power gating
- retention options
- ECC/parity evaluation
- BIST
- independent DMA access

---

# 22. FLASH / NAND ARCHITECTURE

## 22.1 NOR
Evaluate:
- 256 Mbit to 1 Gbit optional NOR
- high-speed serial interface
- execute/read throughput
- deep power-down
- 1.8 V preferred if compatible

## 22.2 NAND
Evaluate:
- 4–16 Gbit initial target
- raw NAND vs managed NAND
- stacked die feasibility
- ECC requirements
- endurance
- retention
- write power
- sustained logging throughput

## 22.3 NAND controller
If raw NAND:
- hardware ECC
- bad-block management support
- DMA
- scrambling if required
- wear-level support
- encryption/authentication integration
- integrity metadata

---

# 23. HOST INTERFACE TO nRF

Preferred host interface:
- high-speed SPI or equivalent
- optional secondary control bus

Requirements:
- DMA-friendly framing
- packet CRC
- flow control
- interrupt lines
- host wake
- ASIC wake
- reset
- boot status
- fault status
- bulk stream mode
- register mode
- debug access policy

Target bandwidth shall exceed worst-case practical sensor burst rate with ≥20% margin.

---

# 24. POWER / PMIC / BMS REQUIREMENTS

# 24.1 Battery class
Optimize for current 8–14 mAh-class battery while allowing somewhat larger future cells.

## 24.2 Battery voltage
Exact chemistry and operating window = TBD.

## 24.3 Charger
Target programmable charge current:
- ~0.1 mA to 20 mA

Modes:
- precharge
- constant current
- constant voltage
- termination
- recharge
- storage mode
- ship mode
- battery disconnect
- thermal derating
- battery presence/fault

## 24.4 Battery protection
Hardware protection:
- overvoltage
- undervoltage
- overcurrent
- short circuit
- reverse-current where relevant
- overtemperature
- undertemperature if required

## 24.5 Fuel gauge
Measure:
- battery voltage
- battery current
- battery temperature
- coulomb count
- internal resistance proxy

Estimate:
- SOC
- SOH
- remaining runtime
- cycle count

## 24.6 Regulators
Candidate:
- 2–3 high-efficiency bucks
- 1 configurable buck/buck-boost
- 4–6 low-noise LDOs
- optical LED boost
- optional piezo/audio boost
- multiple load switches

Exact rails derived later.

## 24.7 Inductors
Do not force µH inductors onto silicon.
Allow:
- external discrete inductors
- co-packaged inductors
- embedded passives if performance supports

## 24.8 Analog rail quality
Low-noise biosignal rails require:
- ripple limits
- PSRR budgeting
- startup sequencing
- regulator noise characterization
- switching-frequency placement away from sensitive bands where feasible

---

# 25. POWER DOMAINS

Initial conceptual domains:

```text
PD_AON
PD_BIO
PD_EDA_Z
PD_ECHEM
PD_OPT_RX
PD_LED_TX
PD_THERMAL
PD_AUDIO_IN
PD_AUDIO_OUT
PD_DSP
PD_SRAM
PD_HOST_IF
PD_IMU
PD_NAND
PD_NRF
```

Each domain must define:
- supply voltage
- retention requirement
- isolation requirement
- reset behavior
- clock state
- wake source
- entry latency
- exit latency
- power estimate

---

# 26. POWER BUDGET METHODOLOGY

Do not optimize only active current.

For every block record:
- active power
- idle power
- retention power
- shutdown leakage
- startup energy
- duty cycle
- average energy/sample
- average energy/event

System battery-life model:

```text
E_battery ≈ V_nominal × Ah_usable
P_average = Σ(P_state × duty_cycle)
Runtime = E_usable / P_average
```

Peak current and average energy must both be validated.

---

# 27. CLOCKING

Candidate clock domains:
- 32 kHz-class AON/RTC
- 1–8 MHz low-power sensor clock
- 16–64 MHz digital/DSP clock as required
- audio clocks
- high-speed host-interface clock
- ADC modulator clocks
- switching-regulator clocks

Requirements:
- clock gating
- glitch-free switching
- deterministic sensor timing
- low jitter for sensitive ADC/audio paths
- spread-spectrum only if it does not corrupt sensing
- clock-domain crossing verification

---

# 28. RESET / STARTUP / SAFE STATE

Define:
- POR
- brownout
- host reset
- watchdog reset
- analog reset
- digital reset
- PMIC fault reset

On reset:
- body-connected stimulation OFF
- UV OFF
- LED high-power paths OFF
- audio high-power OFF
- electrochemical drive OFF unless intentionally safe
- charger in safe state
- regulators enter defined sequence

---

# 29. HARDWARE SAFETY INTERLOCKS

Safety-critical limits shall not depend solely on firmware.

Hardware limiters for:
- UV exposure
- LED overcurrent
- electrochemical electrode current
- stimulation amplitude
- audio/piezo overdrive
- battery overcurrent
- overtemperature
- regulator overvoltage
- illegal power sequence where hazardous

---

# 30. ESD / EMC / BODY-CONNECTED INPUTS

Special pad classes required.

## 30.1 Low-leakage electrode pads
Generic high-leakage ESD cells may be unacceptable for:
- EEG
- ISE
- ultra-low-current electrochemical inputs

Need:
- custom/approved low-leakage ESD strategy
- external protection co-design
- RF/EMI filtering
- latch-up evaluation
- IEC-level system protection strategy

## 30.2 Optical/audio/high-current pads
Separate pad classes for:
- LED current
- speaker current
- boost voltage
- battery input
- digital I/O

---

# 31. REFERENCES / BIAS / CALIBRATION

BioSense shall include:
- low-noise reference(s)
- bias current/reference
- test DAC
- ADC calibration path
- TIA calibration
- offset calibration
- gain calibration
- loopback mux

Trim/calibration storage:
- OTP/eFuse or equivalent

Store:
- ADC gain/offset
- DAC gain/offset
- AFE offsets
- TIA gain calibration
- optical current calibration
- temperature coefficients
- oscillator trim
- chip ID
- lot/wafer metadata if available

---

# 32. SECURITY

At minimum:
- unique device identity
- secure boot chain coordinated with nRF
- authenticated firmware
- encrypted sensitive storage where appropriate
- debug lock
- test-mode access control
- rollback protection strategy
- key provisioning strategy
- secure factory flow

Do not expose unrestricted analog stimulation through unauthenticated commands in production mode.

---

# 33. DFT / BIST / PRODUCTION TEST

DFT is a first-class requirement.

## 33.1 Digital
- scan
- ATPG
- SRAM BIST
- logic BIST where useful
- JTAG/SWD/production access
- boundary-scan evaluation

## 33.2 Analog
Provide:
- analog test bus
- internal stimulus injection
- loopback
- reference measurement
- ADC self-test
- DAC-to-ADC loop
- TIA calibration path
- comparator test
- regulator telemetry

## 33.3 Production metrics
Every analog block shall have a defined:
- test method
- test time estimate
- pass/fail threshold
- calibration method
- trim method
- expected yield impact

---

# 34. PACKAGE / SiP REQUIREMENTS

Initial package target:
- approximately 6–8 mm × 6–8 mm aspirational system footprint
- approximately ≤1.2 mm height aspirational
- final target dependent on stacked memory/MEMS/passives

Evaluate:
- fan-out
- RDL
- laminate SiP
- embedded passive substrate
- die stacking
- memory-on-logic stacking
- thermal path
- warpage
- yield
- test access
- rework limits

## 34.1 Noise-aware placement
Physically separate:
- EEG/ISE analog
- switching regulators
- RF
- Class-D/audio power
- LED boost
- high-current return paths

Need:
- ground strategy
- substrate isolation
- guard rings
- deep-N-well/triple-well if available
- dedicated quiet references
- return-current planning

---

# 35. EXTERNAL COMPONENTS EXPECTED TO REMAIN

Do not force physical transducers onto CMOS.

Likely external/co-packaged:
- antenna
- battery
- LEDs
- photodiodes
- optical filters
- external laser if any
- EEG/ECG/EDA electrodes
- electrochemical electrodes and recognition chemistry
- Na⁺/K⁺ ISE membranes/electrodes
- reference electrode
- NTCs
- thermopile/heat-flux sensor
- acoustic transducer
- bone-conduction actuator
- inductors
- selected precision passives
- crystal/oscillator if required
- MEMS mechanical element

---

# 36. PERFORMANCE / SIZE / POWER PRIORITY LAW

The project must continuously pursue the **smallest and lowest-energy implementation that still satisfies every required performance and quality metric**.

Hard priorities:

1. Safety — never traded away.
2. Measurement validity / signal integrity — never traded away.
3. Required electrical/algorithmic performance — never traded away merely to save area or power.
4. Reliability / lifetime / PVT / Monte-Carlo margin — never traded away merely to save area or power.
5. Minimum average energy and energy/event.
6. Minimum die/package area and package height.
7. Minimum external BOM and interconnect overhead.
8. Peak-power feasibility.
9. Cost.
10. Convenience.

The optimization objective is:

> **Maximum quality and performance at the minimum physically achievable area/volume/power, with zero intentional compromise of required specifications.**

Every optimization must provide quantitative proof that all hard constraints remain satisfied.

---

# 37. INITIAL SYSTEM MODES

## 37.1 Deep sleep
- AON only
- battery supervision
- wake event detection

## 37.2 Daily health
- IMU
- temperature
- periodic PPG
- optional EDA

## 37.3 Sleep neuroscience
- EEG
- PPG
- IMU
- temperature
- low-power audio-event detection

## 37.4 Cardiovascular
- ECG
- PPG
- IMU/BCG
- multispectral optical

## 37.5 Sweat/biochemistry
- Na⁺/K⁺/pH/electrochemical channels
- temperature
- sweat-rate auxiliary
- intermittent PPG if desired

## 37.6 Optical spectroscopy
- selected high-power emitter
- high-gain PD
- short acquisition windows

## 37.7 Audio
- microphone
- DSP
- audio output
- nRF active

## 37.8 Research/raw logging
- broad simultaneous sensing
- NAND logging
- aggressive power budget accepted

---

# 38. REQUIREMENTS TRACEABILITY

Create:

```text
state/REQUIREMENTS_TRACEABILITY.csv
```

Fields:

```text
Req_ID,
Subsystem,
Requirement,
Priority,
Target_or_Limit,
Verification_Method,
Design_Artifact,
Test_Artifact,
Status,
Owner,
Notes
```

Requirement IDs:
- PRC-xxxx (program controls)
- SYS-xxxx
- BIO-xxxx
- EDA-xxxx
- ECH-xxxx
- OPT-xxxx
- THM-xxxx
- AUD-xxxx
- ADC-xxxx
- DAC-xxxx
- DSP-xxxx
- MEM-xxxx
- PMU-xxxx
- SEC-xxxx
- DFT-xxxx
- PKG-xxxx
- SAFE-xxxx
- TIM-xxxx, AON-xxxx, HIF-xxxx, CAL-xxxx, VAL-xxxx (cross-subsystem functions and validation)

No frozen requirement may exist only in prose without an ID once Chunk 1 is complete.

The CH01 register additionally classifies each row as `CANDIDATE`, `NEEDS_DEFINITION`, `RESEARCH_ONLY`, or `PROCESS_ACTIVE`. `MUST` and `SHOULD` express the intended priority; neither status nor priority is proof of technical feasibility or an approved product claim. The `Notes` field identifies the source section and open issue, while the design and test artifact paths are planned destinations until populated with evidence.

---

# 39. REPOSITORY STRUCTURE

Recommended:

```text
project-hummingbird/
│
├── README.md
├── MASTER_SPEC.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE                    # only after OI-008 owner decision; currently absent
├── .gitignore
├── .github/workflows/validate.yml
│
├── state/
│   ├── PROJECT_STATE.md
│   ├── CHUNK_STATUS.csv
│   ├── ASSUMPTIONS.md
│   ├── VERIFICATION_STATUS.md
│   ├── DECISIONS.md
│   ├── OPEN_ISSUES.md
│   ├── RISK_REGISTER.md
│   ├── REQUIREMENTS_TRACEABILITY.csv
│   ├── MILESTONES.md
│   └── CHANGELOG.md
│
├── docs/
│   ├── README.md
│   ├── REPOSITORY_MAP.md
│   ├── chunks/
│   ├── governance/
│   ├── inputs/
│   ├── architecture/
│   ├── adr/
│   ├── literature/
│   ├── interfaces/
│   ├── budgets/
│   ├── package/
│   ├── safety/
│   └── reviews/
│
├── specs/
│   ├── system/
│   ├── biosignal/
│   ├── eda_bioz/
│   ├── electrochem/
│   ├── optical/
│   ├── thermal/
│   ├── audio/
│   ├── adc_dac/
│   ├── digital/
│   ├── pmic/
│   ├── memory/
│   └── dft/
│
├── models/
│   ├── python/
│   ├── matlab_octave/
│   ├── veriloga/
│   ├── rnm/
│   ├── spice/
│   └── sensor_models/
│
├── rtl/
│   ├── top/
│   ├── aon/
│   ├── timestamp/
│   ├── host_if/
│   ├── dma/
│   ├── fifo/
│   ├── dsp/
│   ├── sensor_seq/
│   ├── power_ctrl/
│   ├── regfile/
│   └── common/
│
├── verification/
│   ├── unit/
│   ├── formal/
│   ├── uvm/
│   ├── ams/
│   ├── regressions/
│   └── coverage/
│
├── analog/
│   ├── bio/
│   ├── eda_bioz/
│   ├── electrochem/
│   ├── optical/
│   ├── thermal/
│   ├── audio/
│   ├── adc/
│   ├── dac/
│   ├── references/
│   └── test/
│
├── pmic/
│   ├── charger/
│   ├── bms/
│   ├── buck/
│   ├── ldo/
│   ├── boost/
│   ├── audio_power/
│   └── protection/
│
├── firmware/
│   ├── host_reference/
│   ├── calibration/
│   └── manufacturing/
│
├── physical/
│   ├── floorplan/
│   ├── io/
│   ├── power_grid/
│   ├── package/
│   ├── lef/
│   └── def/
│
├── constraints/
│   ├── sdc/
│   └── upf/
│
├── synthesis/
├── sta/
├── pnr/
├── pex/
├── drc/
├── lvs/
├── emir/
├── reliability/
│
├── scripts/
│   ├── setup/
│   ├── simulation/
│   ├── synthesis/
│   ├── verification/
│   └── reporting/
│
├── reports/
│   ├── block/
│   ├── subsystem/
│   ├── fullchip/
│   └── signoff/
│
└── tapeout/
    ├── release_checklists/
    └── release_candidates/
```

The tree is a **directory and ownership plan**, not evidence that reserved folders contain design artifacts. See `docs/REPOSITORY_MAP.md` for current contents. `LICENSE` is gated by OI-008; a public GitHub repository alone does not choose reuse terms. Keep only public and authorized inputs here as described in `docs/governance/DATA_POLICY.md`.

---

# 40. PROJECT STATE FILE FORMAT

`state/PROJECT_STATE.md` shall always include:

```text
# Current Baseline
Architecture version:
Canonical branch and live checkout commit:
Last reviewed baseline (if needed):
Current chunk:
Current subchunk:
Current status:

# Passed Gates
...

# Active Work
...

# Blocked Items
...

# Next Exact Action
...

# Required Inputs
...

# Latest Regression
Command:
Commit:
Result:
Timestamp:
```

This file is the first thing Astra should read in every new chat/session, together with `state/CHUNK_STATUS.csv`. Obtain the live commit from Git: a committed file cannot contain its own final merge SHA. A paused chunk remains paused until the user explicitly resumes it.

---

# 41. CHUNK EXECUTION PROTOCOL

Every chunk must follow:

## Step A — Read
Read relevant master requirements, decisions, risks, prior reports.

## Step B — Restate scope
Create/update chunk file:

```text
docs/chunks/CHxx_<name>.md
```

Include:
- scope
- non-scope
- inputs
- outputs
- assumptions
- applicable requirement IDs
- required literature/prior-art survey scope
- literature search date and recency window
- area/volume/power optimization targets
- performance/quality constraints that must not be compromised
- acceptance tests

## Step C — Literature and prior-art gate
Before architecture selection or implementation:
- perform the mandatory survey from Section 0.7,
- search recent peer-reviewed literature and authoritative technical sources,
- extract measured state-of-the-art benchmarks,
- compare architecture families quantitatively,
- identify best practices and known failure mechanisms,
- document the selected architecture and why alternatives were rejected,
- commit the literature review.

No design implementation may begin until this gate passes.

## Step D — First-principles model and numerical budget
Before RTL/transistor work:
- derive equations from first principles,
- calculate numerical budgets,
- build executable reference models where meaningful,
- benchmark proposed targets against the literature,
- identify where targets intentionally exceed current state of the art,
- quantify area/power/performance tradeoffs.

## Step E — Implement
Create source artifacts.

## Step F — Verify
Run automated tests.

## Step G — Review
Check:
- spec compliance,
- corner cases,
- safety,
- interfaces,
- noise/performance,
- reliability,
- PVT margin,
- area/volume optimization,
- power/energy optimization,
- confirmation that no required quality/performance metric was sacrificed.

## Step H — Save
Update reports/state/traceability.

## Step I — Commit
Atomic commit.

## Step J — Gate
Proceed only if PASS or explicit documented waiver.

---

# 42. DEVELOPMENT CHUNKS

The project shall be executed in the following major chunks.

**Mandatory rule for every design-oriented chunk below:** before executing design work, create or refresh the corresponding state-of-the-art literature/prior-art review required by Section 0.7. The review and architecture-selection rationale must be committed before implementation begins. For a large chunk, repeat the survey gate at sub-block level when the sub-block has materially different circuit physics or architecture choices.

---

## CH00 — Repository Bootstrap

### Goal
Create clean reproducible project structure.

### Outputs
- repo skeleton
- this `MASTER_SPEC.md`
- state files
- requirements-traceability template
- ADR template
- chunk template
- CI placeholder
- coding conventions
- naming conventions

### Acceptance
- repository builds/tests placeholder successfully
- no untracked critical files
- initial baseline commit traceable; create a version tag only if a real milestone has been approved

---

## CH01 — Requirements Normalization & Traceability

### Goal
Convert this document into atomic requirement IDs.

### Tasks
- decompose every MUST/SHOULD
- resolve duplicates
- mark TBDs
- identify contradictions
- establish verification method

### Outputs
- populated `REQUIREMENTS_TRACEABILITY.csv`
- requirements review report
- unresolved-requirement list

### Gate
No architecture freeze until high-risk requirements are traceable.

---

## CH02 — Use-Case / Concurrent-Mode Matrix

### Goal
Define what must operate simultaneously.

Examples:
- EEG + PPG + IMU + temp during sleep
- ECG + PPG + IMU during cardiovascular mode
- electrochem + temp during sweat mode
- audio + IMU + limited PPG
- research raw mode

### Outputs
- concurrency matrix
- peak bandwidth
- peak current
- ADC concurrency
- DMA requirements
- pin/resource conflict analysis

---

## CH03 — System Power/Energy Model

### Goal
Create executable battery-life model.

### Outputs
- Python model
- per-block state table
- mode-level energy
- 8/10/14/20 mAh scenarios
- sensitivity analysis
- peak-current analysis

### Gate
Architecture must fit realistic battery physics.

---

## CH04 — System Data-Rate / Memory Model

### Goal
Quantify raw and processed data.

Include:
- EEG
- ECG
- optical
- IMU
- audio
- electrochem
- temperature

### Outputs
- data-rate calculator
- FIFO sizing
- SRAM sizing
- NAND bandwidth/endurance
- host-interface requirement
- BLE transmission feasibility

---

## CH05 — Clock / Timestamp / Synchronization Architecture

### Goal
Freeze timing model.

### Outputs
- clock tree concept
- timebase spec
- trigger matrix
- CDC plan
- jitter budget
- timestamp RTL reference

### Tests
- rollover
- cross-domain events
- simultaneous triggers
- sleep/wake continuity

---

## CH06 — Register Map / Host Protocol

### Goal
Create stable software-visible hardware contract.

### Outputs
- register map
- host packet protocol
- error/status scheme
- interrupts
- DMA descriptor concept
- versioning strategy

### Gate
All subsequent digital blocks use this contract.

---

## CH07 — Biopotential Numerical Design

### Goal
Derive EEG/ECG channel from first principles.

### Work
- signal ranges
- electrode model
- noise budget
- CMRR budget
- offset tolerance
- input impedance
- anti-alias requirement
- ADC OSR
- power budget

### Outputs
- analytical notebook/script
- architecture comparison
- selected topology
- block spec

No transistor sizing until numerical targets are frozen.

---

## CH08 — Biopotential Behavioral Implementation

### Outputs
- Verilog-A/RNM model
- electrode model
- ADC behavioral model
- saturation/recovery behavior
- calibration model
- automated tests

### Gate
Behavioral channel passes all system requirements.

---

## CH09 — EDA/BioZ Architecture

### Tasks
- excitation analysis
- impedance range
- frequency range
- synchronous demodulation
- electrode model
- leakage/error analysis

### Outputs
- reference equations/model
- selected topology
- behavioral implementation
- test vectors

---

## CH10 — Electrochemical / Na⁺ / K⁺ / Sweat Architecture

### Critical scope
This chunk specifically includes the newly required Na⁺/K⁺/sweat functions.

### Subchunks
- CH10A: potentiometric/ISE requirements
- CH10B: amperometric/TIA requirements
- CH10C: potentiostat
- CH10D: waveform generation
- CH10E: Na⁺/K⁺ calibration model
- CH10F: sweat sensor multiplexing/reference architecture
- CH10G: EIS
- CH10H: behavioral verification

### Required analyses
- Nernst-response modeling
- temperature dependence
- electrode source impedance
- reference-electrode error
- input leakage error
- mux leakage
- ESD leakage
- drift
- noise
- ADC resolution
- DAC error
- TIA dynamic range
- auto-ranging
- cross-talk

### Gate
Demonstrate that leakage and offset do not dominate ISE measurements.

---

## CH11 — Optical System Physics & Noise Budget

### Goal
Quantitatively design optical architecture.

### Model:
- LED radiant power
- skin attenuation placeholder model
- PD responsivity
- shot noise
- ambient light
- TIA noise
- ADC noise
- dynamic range
- saturation
- wavelength sequencing
- duty cycle

### Outputs
- Python optical link-budget model
- receiver gain requirements
- LED current ranges
- SNR vs optical conditions

---

## CH12 — Optical AFE Behavioral Implementation

### Subchunks
- PD/TIA
- ambient cancellation
- gain switching
- dark subtraction
- ADC interface
- adaptive LED control
- multi-PD simultaneous mode
- UV exposure monitor

### Gate
Regression covers weak/strong signal, sunlight/ambient, dark skin model assumptions, saturation recovery, off-body.

---

## CH13 — Thermal / Thermopile AFE

### Tasks
- J30-like source model
- low-frequency noise model
- offset/drift budget
- chopper artifacts
- NTC ratiometric path
- self-heating analysis

### Outputs
- precision AFE reference model
- topology
- behavioral model
- calibration method

---

## CH14 — Audio Input Architecture

### Tasks
- analog MEMS mic
- PDM mic
- piezo/contact mic
- bone-conduction vibration
- gain/noise/dynamic range

### Outputs
- audio input spec
- ADC choice
- digital decimation
- test vectors

---

## CH15 — Audio Output Architecture

### Tasks
- Class-D
- bone-conduction transducer
- piezo HV alternative
- DAC
- limiter
- thermal/current safety
- battery impact

### Gate
Demonstrate safe peak current and acceptable battery energy in defined modes.

---

## CH16 — ADC Bank Architecture Study

### Goal
Determine which ADCs truly need separate hardware.

Compare:
- per-channel ΔΣ
- multiplexed ΔΣ
- incremental ADC
- SAR
- integrating ADC
- shared residue/reference
- audio-specific ADC

### Outputs
- area/power/noise matrix
- selected bank architecture
- concurrency proof

---

## CH17 — DAC / Excitation Architecture

### Outputs
- precision DAC architecture
- LED current DAC
- waveform DAC
- monotonicity/noise requirements
- behavioral models

---

## CH18 — DSP Accelerator Architecture

### Implement incrementally:
- CIC
- FIR
- biquad
- RMS
- peak
- lock-in
- I/Q accumulator
- correlation
- FFT if justified

### Requirements
- bit-true Python golden models
- synthesizable RTL
- unit tests
- fixed-point error analysis
- power gating

---

## CH19 — DMA / FIFO / SRAM Subsystem

### Implement
- FIFO architecture
- multi-source arbitration
- DMA descriptors
- backpressure
- overflow handling
- timestamp association

### Verification
- randomized traffic
- overflow
- simultaneous sensors
- host stall
- sleep/wake

---

## CH20 — Always-On Controller / Power FSM

### Implement
- sensor wake scheduler
- nRF wake control
- safe state
- watchdog
- domain sequencing
- fault escalation

### Formal properties
Use assertions for illegal power sequences and safety outputs.

---

## CH21 — Memory Architecture

### Evaluate
- nRF internal NVM only
- NOR
- raw NAND
- managed NAND
- NOR + NAND
- NAND stack in SiP

### Outputs
- selected memory hierarchy
- controller requirements
- ECC
- throughput/endurance model
- data-retention policy

---

## CH22 — PMIC System Architecture

### Tasks
- rail tree
- voltage requirements
- peak currents
- conversion topology
- switching-frequency plan
- analog rail isolation
- efficiency curves

### Outputs
- PMIC architecture
- operating-state table
- external inductor/cap requirements

---

## CH23 — Charger / BMS / Fuel Gauge

### Model
- tiny-cell charge behavior
- termination accuracy
- coulomb counting
- SOC
- OCV
- internal resistance
- temperature effects

### Outputs
- charger requirements
- fuel-gauge algorithm
- safety FSM
- battery telemetry map

---

## CH24 — LED Boost / High-Voltage / Power Audio

### Analyze
- separate vs shared boost
- optical/piezo concurrency
- noise injection
- efficiency
- transient behavior
- package current paths

### Gate
No shared boost if noise/safety/availability tradeoff is poor.

---

## CH25 — Security Architecture

### Outputs
- root-of-trust assumptions
- nRF/security boundary
- provisioning
- debug policy
- firmware authentication
- manufacturing access

---

## CH26 — DFT / Calibration Architecture

### Outputs
- scan plan
- SRAM BIST
- analog test mux
- calibration DAC
- loopbacks
- wafer-test sequence
- production-test sequence
- OTP programming flow

---

## CH27 — Top-Level Behavioral AMS Integration

### Goal
Connect all behavioral models.

Simulate representative use cases:
- sleep
- cardiovascular
- sweat/Na/K
- optical spectroscopy
- audio
- research logging

### Verify
- sequencing
- timing
- bandwidth
- faults
- power-state transitions
- cross-sensor synchronization

---

## CH28 — Digital RTL Integration

### Outputs
- synthesizable top
- complete register map
- clocks/resets
- host interface
- DMA
- sensor engines
- safety logic

### Verification
- lint
- CDC
- RDC
- formal
- unit regression
- integration regression
- coverage

---

## CH29 — Pre-PDK Architecture Freeze

### Goal
Freeze everything that can be frozen without foundry-specific data.

### Required review
- requirements
- interfaces
- power
- timing
- DFT
- pad classes
- die estimates
- package estimates
- 10% reserve compliance

---

## CH30 — Foundry / Process Selection

### Compare
Potential precision CMOS/BCD options.

Criteria:
- low leakage
- analog device quality
- MIM caps
- resistor options
- thick-oxide devices
- BCD availability
- SRAM
- OTP
- IO
- ESD
- wafer cost
- MPW
- packaging ecosystem
- schedule

### Output
Formal process selection ADR.

---

## CH31 — PDK Bring-Up

### Tasks
- verify toolchain
- simulate primitive devices
- create reusable PDK wrappers
- establish corners
- validate extraction
- validate DRC/LVS flow

### Gate
No transistor design until PDK smoke tests pass.

---

## CH32 — Analog Primitive Library

Implement and characterize reusable:
- OTA
- op-amp
- comparator
- switch
- current mirror
- bias
- bandgap/reference
- chopper
- low-leakage mux
- TIA primitives
- capacitor/resistor units

### Output
Characterization database.

---

## CH33 — Transistor-Level Biopotential AFE

For each design iteration:
1. schematic
2. DC
3. AC
4. transient
5. noise
6. PSRR
7. CMRR
8. PVT
9. Monte Carlo
10. startup
11. overload recovery
12. power

Do not proceed to layout before pre-layout pass.

---

## CH34 — Transistor-Level EDA/BioZ

Same discipline.

---

## CH35 — Transistor-Level Electrochemical / ISE

Critical:
- leakage
- input bias
- offset
- temperature drift
- ESD interaction
- guard structures

---

## CH36 — Transistor-Level Optical AFE

Critical:
- TIA stability across PD capacitance
- ambient cancellation range
- shot-noise-limited conditions
- gain switching
- recovery

---

## CH37 — Transistor-Level Thermal AFE

Critical:
- flicker noise
- chopping ripple
- offset
- drift
- low-frequency settling

---

## CH38 — Transistor-Level ADCs/DACs

Each converter receives independent:
- architecture spec
- behavioral proof
- transistor proof
- PVT
- Monte Carlo
- reference sensitivity
- clock sensitivity

---

## CH39 — PowerAudio ASIC Transistor Design

Includes:
- charger
- protection
- buck/LDO
- boost
- Class-D/piezo
- current sense

Requires power-device/reliability rules.

---

## CH40 — Macro Layout

Per analog macro:
- floorplan
- symmetry
- matching
- common-centroid where needed
- guard rings
- shielding
- routing
- parasitic awareness

Run:
- DRC
- LVS
- PEX
- post-layout PVT
- post-layout Monte Carlo where necessary

---

## CH41 — Digital Synthesis / STA

Outputs:
- synthesized netlist
- area
- timing
- power estimate
- constraints validation

Maintain ≥10% design reserve unless explicitly waived.

---

## CH42 — Full-Chip Floorplan

Must address:
- analog quiet zones
- substrate noise
- digital core
- pad ring
- power domains
- high-current LED/audio
- ESD
- clocking
- test
- 10% future reserve

---

## CH43 — Place & Route

Run:
- placement
- CTS
- routing
- optimization
- congestion
- IR analysis
- timing closure

---

## CH44 — Full-Chip DRC / LVS / ERC / Antenna

No hidden violations.

Every waiver:
- documented
- justified
- reviewed

---

## CH45 — Full-Chip PEX / Post-Layout AMS

Re-run:
- sensitive analog performance
- clock/timing
- switching-noise interaction
- power sequencing
- cross-talk scenarios

---

## CH46 — EM/IR / Reliability

Analyze:
- battery path
- LED path
- audio path
- boost path
- regulator current
- ESD structures
- thermal hotspots
- electromigration
- voltage overstress
- lifetime rules

---

## CH47 — Package Co-Design

Validate:
- bump map
- package parasitics
- high-current loops
- RF isolation
- analog isolation
- memory stack
- IMU placement
- thermal path
- warpage
- assembly

---

## CH48 — Final Verification Matrix

Every requirement ID must map to:
- analysis
- simulation
- formal proof
- measurement plan
- signoff report

No orphan requirements.

---

## CH49 — Tapeout Release Candidate

Create:

```text
tapeout/release_candidates/RC1/
```

Include:
- GDSII/OASIS
- final netlists
- CDL
- LEF/DEF as required
- SDF
- SPEF
- DRC report
- LVS report
- ERC
- antenna
- STA
- EM/IR
- reliability
- PVT summary
- Monte Carlo summary
- waiver list
- release manifest
- checksums
- version IDs

---

## CH50 — Tapeout Readiness Review

No tapeout unless:
- required signoff is clean
- waivers approved
- version hashes frozen
- package alignment confirmed
- test plan frozen
- mask options confirmed
- OTP/trim strategy frozen
- bring-up board planned
- lab characterization plan ready

---

# 43. VALIDATION PHILOSOPHY

Every analog block should pass:

```text
Typical
Fast/Fast
Slow/Slow
Fast/Slow
Slow/Fast
Voltage min/nom/max
Temperature min/room/max
Mismatch Monte Carlo
Process Monte Carlo where supported
Startup
Shutdown
Overload
Recovery
Power-domain transitions
```

Every digital block:
- lint
- unit tests
- randomized tests
- assertions
- formal where useful
- CDC
- reset analysis
- coverage

Every mixed-signal interface:
- RNM/Verilog-A co-sim
- timing
- saturation
- quantization
- fault injection

---

# 43A. BLOCK DESIGN ENTRY CHECKLIST

Before **every** new technical block or materially new sub-block is designed, confirm all of the following:

- [ ] Requirement IDs identified.
- [ ] Most recent relevant literature searched.
- [ ] Recent journal and conference papers reviewed.
- [ ] Relevant commercial/reference designs reviewed.
- [ ] Relevant patents/standards reviewed where applicable.
- [ ] Measured silicon benchmarks extracted.
- [ ] Area/power/noise/performance comparison table created.
- [ ] Best architecture candidates identified.
- [ ] Application-specific trade study completed.
- [ ] Recommended architecture justified.
- [ ] Rejected alternatives documented.
- [ ] Design targets benchmarked against state of the art.
- [ ] Area/volume/power optimization opportunities listed.
- [ ] Required performance/quality hard constraints identified.
- [ ] Literature review committed to Git.

Only then may first-principles modeling and design begin.

---

# 44. GOLDEN MODELS

Before implementation, create executable golden models for:

- battery life
- optical SNR
- EEG noise
- electrochemical TIA
- Na⁺/K⁺ Nernst response
- BioZ impedance
- thermopile noise
- ADC quantization/ENOB
- DSP fixed-point behavior
- data rate
- memory occupancy
- timestamp behavior

These models must remain in the repository and be regression-tested.

---

# 45. CI / AUTOMATED REGRESSION

As tooling allows, CI should run:

- Python unit tests
- golden model regressions
- RTL lint
- open-source RTL simulation where license permits
- formal checks where available
- documentation link checks
- requirement traceability consistency
- generated-register consistency

Commercial EDA regressions may run on internal infrastructure rather than public CI.

---

# 46. DESIGN REVIEW GATES

Mandatory reviews:

- SRR — System Requirements Review
- SAR — System Architecture Review
- PDR — Preliminary Design Review
- CDR — Critical Design Review
- Pre-layout Review
- Post-layout Review
- Tapeout Readiness Review

Each review generates:
- agenda
- inputs
- findings
- action items
- pass/conditional pass/fail
- closure log

---

# 47. RISK REGISTER — INITIAL HIGH-RISK ITEMS

At project start, enter at least:

1. EEG/ISE pad leakage vs ESD robustness
2. Optical AFE dynamic range
3. simultaneous sensor concurrency
4. switching-noise coupling into µV biosignals
5. ultra-small battery peak-current capability
6. audio energy budget
7. UV optical safety
8. electrochemical reference-electrode architecture
9. Na⁺/K⁺ sensor chemistry stability
10. hormone-sensor chemistry maturity
11. non-invasive glucose feasibility
12. cuffless BP validation
13. high-density package yield
14. stacked-memory thermal/mechanical risk
15. bare-die nRF commercial availability/licensing
16. process-node/IP availability
17. analog verification schedule
18. production test time
19. 10% future reserve erosion
20. SiP RF/analog coexistence

---

# 48. WHAT NOT TO DO

Do not:
- start architecture/circuit/RTL/transistor design before the mandatory literature/prior-art gate
- collect paper links without extracting quantitative engineering implications
- copy published architecture without checking application fit, process, area, power, noise, and measured results
- start transistor sizing before requirements/noise budgets
- accept an area/power optimization that violates required performance, quality, safety, reliability, or PVT margin
- claim 24-bit performance without ENOB/noise proof
- treat Na⁺/K⁺ ISE as a conventional low-impedance ADC input
- treat CGM as merely another PPG wavelength
- treat Raman as an LED+PD feature
- claim cuffless BP clinical accuracy from sensor availability
- integrate BLE RF into custom silicon Gen-1 without compelling reason
- fabricate µH inductors on-die just for integration
- run high-current return paths near EEG/ISE references
- depend on firmware for safety-critical current/exposure limits
- leave verification results only in chat
- continue after a failing gate without a documented waiver
- consume the 10% future reserve silently
- tape out an AI-generated GDS without independent signoff review

---

# 49. FIRST ACTIONS FOR A NEW GPT-6 ASTRA WORK SESSION

**Historical bootstrap recipe (completed):** this section describes the first session of a *new* repository. For this existing repository, use `state/PROJECT_STATE.md` and `state/CHUNK_STATUS.csv` to determine the current authorized scope. Do not run CH00 again merely because a new chat begins.

Exact first-session instruction:

```text
Read MASTER_SPEC.md completely.

Do not begin circuit design.

1. Create the repository structure defined in Section 39, including `docs/literature/`.
2. Copy this file to repository root as MASTER_SPEC.md.
3. Create all state files.
4. Create ADR and chunk templates.
5. Create REQUIREMENTS_TRACEABILITY.csv schema.
6. Create a minimal README explaining project goals and workflow.
7. Initialize Git if not already initialized.
8. Update PROJECT_STATE.md to set CH01 as the next action.
9. Make one clean initial commit.
10. If GitHub access is available, push the baseline.
11. Stop.

Return:
- files created,
- git commit hash,
- branch,
- tests/checks performed,
- exact next action.

Do not start CH01 in the same execution unless explicitly instructed.
```

---

# 50. SECOND SESSION

**Historical bootstrap recipe (completed):** CH01 was executed and merged as PR #1. The text below applies only to a hypothetical fresh program, not the next session of this repository.

Instruction:

```text
Resume from the repository, not chat memory.

Read:
- MASTER_SPEC.md
- PROJECT_STATE.md
- DECISIONS.md
- OPEN_ISSUES.md
- RISK_REGISTER.md

Execute CH01 Requirements Normalization & Traceability.

Do not modify architecture unless a contradiction forces an ADR.
Create atomic requirement IDs for the complete master specification.
Validate that every MUST/SHOULD/TARGET/TBD is represented.
Run consistency checks.
Commit and push.
Update PROJECT_STATE.md.
Stop after CH01.
```

---

# 51. GENERAL PROMPT FOR EVERY SUBSEQUENT SESSION

```text
Resume the Physiological Computing Platform project from Git.

Do not rely on chat memory as the authoritative project state.

First read:
1. MASTER_SPEC.md
2. state/PROJECT_STATE.md
3. state/DECISIONS.md
4. state/OPEN_ISSUES.md
5. state/RISK_REGISTER.md
6. state/REQUIREMENTS_TRACEABILITY.csv
7. the active chunk specification
8. relevant prior implementation and reports

Execute exactly the current active chunk/subchunk.

Before implementation:
- state scope,
- state assumptions,
- define acceptance criteria,
- identify required tests,
- if this is a new or materially changed block, complete/update the mandatory literature/prior-art survey first,
- explicitly search recent journals/conferences and authoritative technical sources,
- extract quantitative state-of-the-art benchmarks,
- document how literature findings change or confirm the intended design,
- select the architecture only after the survey,
- confirm the planned design minimizes area/volume/power without compromising required quality/performance.

Then:
- derive/model,
- implement,
- test,
- validate against requirements,
- save all artifacts,
- update traceability/state,
- commit atomically,
- push if available.

If acceptance criteria fail:
- do not silently proceed;
- debug within the chunk;
- if blocked, record the blocker and stop in a reproducible state.

At the end report:
- commit hash,
- files changed,
- tests run,
- pass/fail,
- requirement IDs addressed,
- open issues,
- next exact chunk/subchunk.

Do not begin the next chunk unless explicitly requested.
```

---

# 52. DEFINITION OF DONE FOR ANY CHUNK

A chunk is DONE only if:

- scope completed
- mandatory literature/prior-art gate completed where applicable
- literature findings are traceably incorporated into design decisions
- area/volume/power optimization is documented quantitatively
- no required quality/performance/safety/reliability metric was intentionally compromised
- all source files saved
- tests exist
- tests pass or waiver recorded
- results/reports saved
- requirements traceability updated
- decisions recorded
- risks updated
- no unexplained generated files
- working tree clean
- commit created
- remote push attempted if appropriate
- project state updated
- next action explicit

---

# 53. PRELIMINARY TOP-LEVEL TARGETS SUMMARY

These are architecture targets, not tapeout-guaranteed specs.

| Area | Initial target |
|---|---|
| Biopotential | 8 simultaneous EEG/ECG channels |
| EDA/BioZ | 4 configurable channels |
| Electrochemical | 8 universal channels; ≥4 full potentiostat |
| Na⁺/K⁺ | high-Z potentiometric/ISE support |
| Sweat | Na/K/pH/conductivity/lactate/glucose research support |
| Optical TX | 16 LED/current-driver channels |
| Optical RX | 12 PD inputs; ≥8 simultaneous desired |
| Thermal | 4–8 precision slow channels |
| Thermopile | dedicated chopper precision AFE |
| Audio input | up to 4 analog/PDM/contact channels |
| Audio output | full-range electrical path; Class-D and/or piezo HV |
| BIO ADC | 8 × 24-bit-class ΔΣ |
| Echem ADC | 4–8 × 20–24-bit-class |
| Optical ADC | ≥8 simultaneous 18–20-bit-class |
| Precision ADC | 4 × 20–24-bit-class |
| Fast ADC | 2 × 14–16-bit, ~1–5 MSPS target |
| Precision DAC | 8 × 16–18-bit-class |
| LED current DAC | 16 |
| Fast/waveform DAC | 2–4 |
| Local SRAM | ~512 KB–2 MB TBD |
| NOR | ~256 Mb–1 Gb optional |
| NAND | ~4–16 Gb target study |
| MCU/RF | nRF54LM20B-class retained externally/in-SiP |
| IMU | specialized MEMS retained |
| Charger | ~0.1–20 mA programmable target |
| Battery | optimized around current ~8–14 mAh class |
| Timestamp | ≤1 µs target |
| Future reserve | ≥10% usable custom-die core area |

---

# 54. CRITICAL ENGINEERING PRINCIPLE

The project is not fundamentally:

```text
EEG chip
+ PPG chip
+ ECG chip
+ glucose chip
+ hormone chip
```

The intended architecture is:

```text
TRANSDUCER PHYSICS
       ↓
programmable stimulation
       ↓
precision analog measurement
       ↓
high-quality conversion
       ↓
deterministic synchronization
       ↓
low-power DSP
       ↓
quality metadata
       ↓
MCU / ML / storage / radio
```

The custom silicon should be a **programmable human-body measurement computer**.

Its three core verbs are:

```text
STIMULATE → MEASURE → COMPUTE
```

---

# 55. FINAL PROGRAM RULE

At all times:

> Prefer a smaller verified engineering step committed to Git over a larger unverified step left in chat.

The repository is the memory of the project.

Every new chat/session must be able to recover the exact engineering state solely from the repository.


---

# 56. REQUIREMENT MATURITY, FEASIBILITY AND CHANGE CONTROL

This document mixes confirmed context, candidate capabilities and aspirational targets. **A TARGET is not a validated requirement.** CH01 shall classify each statement as product need, engineering constraint, candidate target, stretch goal, assumption or open question. A numerical target becomes frozen only when its operating conditions, measurement method, tolerance, owner and verification evidence are defined. Conflicting targets remain open issues; do not silently optimize to a convenient interpretation.

For every quantitative requirement record: minimum/maximum/nominal; units; bandwidth and filtering; sample rate; simultaneous channel count; supply and temperature range; transducer and electrode model; production versus research mode; lifetime/yield; method of verification; provenance; and confidence. Use `TBD` when the value depends on the PDK or vendor. Do not claim independent control of all nominal channels until the pad, ADC, clock, reference, power and data-rate budgets support their concurrent use.

Priority is safety and measured signal validity first, followed by reliable operation across manufacturing and lifetime, then energy, area, height and cost. A performance trade is admissible only by changing a reviewed requirement with system evidence. Absolute language about zero compromise shall not prevent explicit, evidence-backed requirement negotiation where physics makes the initial targets infeasible.

## 56.1 Feasibility gates before architecture freeze

| Gate | Required evidence | Failure response |
|---|---|---|
| Wearable energy | Mode duty cycles, usable cell energy, conversion losses, leakage and peak-current delivery | Revise concurrency or duty cycle with a reviewed requirement change |
| SiP geometry | Die footprints, spacing, routing, MEMS/optical apertures, passives, antenna and manufacturing rules | Revise package envelope or partition |
| Mixed-signal isolation | Quantitative supply/ground/substrate/EMI coupling budgets and representative switching modes | Revise domains, placement or concurrency |
| Measurement validity | Transducer physics, nuisance variables, ground truth and calibration protocol | Label research only or remove capability claim |
| Test access | Wafer/package test coverage, calibration time and escape risk | Add DFT access before pinout freeze |
| Supply chain | Actual die availability, licensing, PDK/IP rights and assembly access | Keep partition provisional |

# 57. REQUIRED SYSTEM-LEVEL NUMERICAL BUDGETS

Before freezing channel counts, build versioned executable models for every operating mode. Use battery usable capacity at discharge rate and temperature, not nameplate capacity; include battery internal resistance and rail efficiency. Report average power and peak current separately. Sweep worst-case simultaneous modes and record the Pareto frontier of performance, area and energy.

| Budget | Required calculation | Explicit corner |
|---|---|---|
| Energy | Σ(active/idle/sleep power × dwell), startup energy, regulator loss, logging and radio energy | Smallest usable cell, low temperature, end-of-life |
| Noise | Integrated input-referred sensor, electrode, amplifier, reference and ADC noise with bandwidth | Source impedance, 1/f noise, switching and motion |
| Dynamic range | Maximum artifact/ambient/DC offset plus wanted signal and recovery | Sunlight, electrode offset, contact transient |
| Throughput | Σ(bits/sample × samples/s × channels × framing), burst and concurrent logging | Host stall, NAND busy, radio unavailable |
| Timing | Clock drift, timestamp quantization, FIFO latency and trigger jitter | Sleep/wake, oscillator change and FIFO overflow |
| Area/package | Macros, pads, ESD, routing, analog spacing, DFT, reserve and assembly keepouts | PDK density and package rules |
| Thermal | LED/audio/RF burst heating, skin-facing thermal gradient and battery limit | Highest ambient and restricted heat flow |

Each estimate must state input data, equations, unit checks, uncertainty, sensitivity and whether evidence is measured, simulated, calculated or assumed. Avoid summing incompatible best-case published figures across different processes and test conditions.

# 58. SENSOR CLAIMS, CALIBRATION AND VALIDATION

Separate **electrical interface capability** from **biomarker accuracy**. Optical glucose, hormones, cortisol, UV autofluorescence/AGEs, carotenoids, hydration and cuffless blood pressure are research hypotheses until validated against suitable reference methods across users, skin tones, placement, temperature and motion. Store raw measurements and calibration metadata. Avoid medical or clinical performance claims without the appropriate study and regulatory work.

For each modality, write a verification plan with a traceable chain: reference instrument or assay; calibration samples; subjects and conditions; controlled perturbations; interference tests; repeatability/reproducibility; drift; population coverage; statistical metrics and confidence intervals. Split electrical bench tests, tissue/phantom tests and human validation. Define safety ownership for optical exposure, electrode drive and skin contact before implementing a drive path. Confirm applicable standards and regulatory scope with qualified specialists at the relevant market and date; do not infer numerical exposure limits from a generic proxy.

# 59. LITERATURE REVIEW AND SOURCE HYGIENE

For every new technical block, execute Section 0.7 before choosing a topology. Save the search date, databases, exact queries, inclusion/exclusion rules, DOI or primary URL, publication date, evidence type, operating conditions and limitations. Record whether full text or only an abstract was available. Compare figures only after normalizing bandwidth, supply, process, channel count, external components and test setup; otherwise mark them non-comparable. Preserve a compact `Finding → implication → design decision → requirement IDs` table. Cite published measurements distinctly from authors' simulations and vendor typical values. Mark patents as disclosures, not proof of measured performance. Re-check recent work before design freeze.

# 60. REPRODUCIBILITY, SECURITY AND REPOSITORY HYGIENE

Pin versions of public dependencies and scripts. Record command, inputs, seed, tool version, PDK corner, host environment and checksum for results. Public CI shall check Markdown links and structural integrity, requirement IDs and CSV schema, Python syntax, and available public tests; later EDA flows need independent validated checks. Proprietary PDKs, licensed IP, foundry decks, keys, personal/health data, restricted die documents and unlicensed paper PDFs shall never enter a public repository. Store references and access instructions instead. Use synthetic data by default. Keep bulky generated reports outside Git when reproducible; commit manifests, scripts, small evidence summaries and immutable hashes. A baseline is only `PASS` when a fresh clone can run its documented public checks. A placeholder check must be described as a repository structural check, not silicon verification.

# 61. CH00 SCOPE AND NEXT GATE

CH00 produced this specification, a tracked directory skeleton, templates, state records, traceability schema and a reproducible structural check. It did **not** freeze the proposed channel counts, approve the architecture, conduct individual block literature surveys or begin circuit design. CH01–CH03 are complete only at their limited register, scenario and synthetic-model gates. CH03 does **not** validate battery runtime or peak-current safety. The next planned chunk is CH04, paused pending user instruction; use the live state file for handoff. Do not mark a draft specification `verified` solely because Markdown/CSV/Python checks pass.
