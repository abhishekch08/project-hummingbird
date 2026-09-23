# CH02 gate: Concurrent modes and shared-resource accounting

Date: 2026-09-23. Input baseline: merged CH01 `03ffe313f2325d26455e741416bbf821346c5118`.

## What the model establishes

Eight §37 candidate modes and two deliberate stress probes are in the versioned configuration. The standard-library model computes integer sample and traffic counts, channel occupancy, logical producer/event pressure, selected LED load current and illustrative contact scenarios. It checks that every attached requirement ID exists in the CH01 register and that reports regenerate exactly. The full mode-by-mode table is in `docs/budgets/CH02_CONCURRENCY_REVIEW.md`; machine output is in `reports/subsystem/CH02_RESOURCE_SUMMARY.json`.

| Scenario | Raw payload | Framed scenario | 20% guarded host demand | Concurrency finding |
|---|---:|---:|---:|---|
| Sleep neuroscience | 0.378 Mb/s | 1.626 Mb/s | 1.951 Mb/s | BIO8 at full candidate occupancy; optical4; audio event path assumed to stream raw continuously. |
| Optical spectroscopy | 0.490 Mb/s | 0.838 Mb/s | 1.006 Mb/s | 12 PD ports scanned through eight ADC paths in two slots; not 12 simultaneous PD samples. |
| Research raw | 6.385 Mb/s | 12.386 Mb/s | 14.863 Mb/s | Seven logical producers; all selected ADC banks at candidate channel capacity. |
| Fast research stress | 38.385 Mb/s | 124.386 Mb/s | 149.263 Mb/s | Eight producers and 1,059,010 stream groups/s; no 8–64 MHz illustrative single-data-line bus at assumed 70% efficiency meets demand. |
| Intentional conflict probe | 0.624 Mb/s | 1.104 Mb/s | 1.325 Mb/s | BIO10 >8 and instantaneous optical12 >8 are both flagged. |

These values are **conditional on the explicitly assumed rates and unusually heavy per-sample timestamp framing**. In particular, fast-ADC raw payload rises by exactly 32 Mb/s, but repeated 64-bit timestamps raise the modeled framed demand much further. The model neither defines a protocol maximum nor proves that 4 kSPS analog accuracy is feasible. CH04 must compare block timestamps, DMA batching, FIFO depth, local DSP, radio/data policy and real host-interface capability.

## Pin and current interpretation

- The illustrative sensor-to-ASIC signal contact envelope is 78 with aggressive sharing or 94 with independent electrochemical reference/counter and more thermal wiring. A separate 20 internal logical nets represent host/IMU/memory. These **are not package ball counts**, and exclude power, grounds, test, RF and other essential nets. Only vendor partition and pin-mapping work can prove SiP fit.
- The per-port 150 mA optical target implies 150 mA of candidate LED *output* in a one-emitter mode, 300 mA for two enabled emitters, and 2400 mA if sixteen candidate outputs could all be enabled in a fault probe. Neither the battery peak nor the energy cost follows without LED voltage, rail topology, efficiency, duty cycle, other loads and cell impedance.
- Count-level fits for eight candidate modes do **not** approve sample rate, ADC settling, shared reference, low noise, RF coexistence, thermal load, battery duration, UV safety or product claims. Safe source enable combinations need independent hardware bounds.

## Gate decision and remaining work

**CH02 PASS for reproducible scenario coverage and transparent conflict accounting; architecture/product feasibility HOLD.** No mode is promoted to a frozen product requirement. OI-001/OI-003/OI-007/OI-012 remain open, with new host and optical coherence questions in `state/OPEN_ISSUES.md`.

CH03 may begin after this commit. CH03 must model actual cell energy and peak current *with inputs explicitly identified*; if cell measurements or LED voltage/efficiency are unavailable, report sensitivity ranges rather than a runtime verdict. CH04 then develops real data framing and backpressure. No circuit design or literature-first block gate was executed in CH02.

## Reproduction

```sh
python3 models/python/ch02_concurrency.py --check
python3 -m unittest discover -s verification/unit -p 'test_ch02_*.py'
python3 scripts/verification/check_bootstrap.py
python3 scripts/verification/check_requirements.py
git diff --check
```

Result at gate: PASS, seven focused unit tests, deterministic report comparison, CH00/CH01 repository checks, and whitespace check. These tests validate accounting and intentionally flagged conflicts, not silicon or medical performance.
