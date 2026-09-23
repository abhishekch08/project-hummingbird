# Current Baseline
Architecture version: unselected; candidate requirements and mode scenarios only
Active branch: feature/CH02-concurrent-modes (to be published)
Last reviewed baseline: `03ffe313f2325d26455e741416bbf821346c5118` (CH01 merged into main)
Current chunk: CH02 concurrent modes (scenario gate complete)
Current subchunk: complete
Current status: eight candidate modes and two stress probes analyzed; architecture, battery current and product modes not frozen

# Passed Gates
- CH00 scaffold: PASS.
- CH01 provisional 223-ID register and review: merged as PR #1.
- CH02 resource accounting and intentionally infeasible scenarios: PASS in `docs/reviews/CH02_GATE.md`.

# Active Work
- Publish the CH02 feature branch and draft review. No circuit implementation or block literature survey underway.

# Blocked Items
- Product priority and concurrency approval; cell voltage/impedance; optical source radiometry; actual nRF host throughput; pinout/package rules; foundry/IP availability. See `state/OPEN_ISSUES.md` and the CH02 gate.

# Next Exact Action
- CH03 only: create a parameterized energy, runtime and peak-current model for 8/10/14/20 mAh cases. Use measured cell and component data when available; leave unknown quantities explicit and bound assumptions. Do not proceed to CH04 or circuit architecture until the CH03 gate is reviewed.

# Required Inputs
- Cell chemistry, voltage window, impedance and capacity-versus-load/temperature; PPG source voltage/current and rail efficiencies; MCU/RF, sensor and audio state currents; product duty cycles. The CH03 model can be built with clearly labeled sensitivities while these are missing.

# Latest Regression
Command: `python3 models/python/ch02_concurrency.py --check && python3 -m unittest discover -s verification/unit -p 'test_ch02_*.py' && python3 scripts/verification/check_bootstrap.py && python3 scripts/verification/check_requirements.py`
Commit: CH02 content commit on published feature branch; inspect Git HEAD
Result: PASS (scenario arithmetic and consistency only, no silicon performance verified)
Timestamp: 2026-09-23 UTC
