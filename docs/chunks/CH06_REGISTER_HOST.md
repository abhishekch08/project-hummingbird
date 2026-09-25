# CH06: Register map and host protocol

Status: **entry charter and candidate model complete; physical ABI held**. Date: 2026-09-25 UTC. Entry baseline: CH05 conditional gate merged as PR #8 (`bbbebb0cd16e41fa8efe3eea2cbd4abc01ada5b3`). This acceptance plan is committed alongside the [dated host-interface survey](../literature/host_interface/2026-09-25_STATE_OF_ART_REVIEW.md) **before** register/packet architecture work.

## Scope and gate boundary

`MASTER_SPEC.md` §§21–23, 32, 42; `HIF-0001`–`HIF-0003`, `MEM-0001`–`MEM-0003`, `TIM-0001/0004`, `SEC-0003/0004`. Consume CH02 candidate modes, CH04 source/sample-group rates and CH05 64-bit *candidate* timestamp semantics. Do not treat CH04's invented host clock, 70% efficiency, BLE or packet fields as measurements. CH05 physical continuity remains held. No chosen host die revision, pins, SPI polarity/phase, maximum SCK, clock startup, actual BLE, on-chip SRAM macro, DMA controller or safety authorization policy has been approved.

The resulting [candidate contract](../interfaces/CH06_REGISTER_PROTOCOL.md) and [limited gate](../reviews/CH06_GATE.md) implement a **versioned candidate software-visible contract** and a deterministic transport/transaction model. Stable numeric register offsets and on-wire field widths may be exercised in software, but remain provisional until host/ASIC and safety owners approve them and measured interface data are provided. The intended CH06 'all later digital blocks use this contract' gate cannot freeze physical software ABI from an invented host link.

## Acceptance before implementation

1. Define explicit register address, width, reset, access policy, read/write side effects, reserved bits and atomic 64-bit time snapshot behavior; one source of truth generates a readable map. Check no overlap, no accidental write to RO, no undefined write semantics, no software access to actuator enable without a separately reviewed safety authority.
2. Define a bounded framed stream and command envelope with byte order, magic/version, type/length, sequence, data timestamp validity, CRC, parser recovery, integrity versus authentication distinction, and explicit unsupported-version behavior. Retain a loss/gap sequence marker; a CRC is not an authenticity guarantee.
3. Define register, interrupt, wake, reset, boot/fault, FIFO credit/overflow and descriptor-ownership state transitions. Preserve packet bytes across retry or return explicit error, do not acknowledge uncommitted data; allow a host timeout without consuming FIFO. Model wrap and corrupted/duplicate/out-of-order frames. No DMA hardware is implemented here.
4. Recompute candidate payload versus physical transfer bytes and 20% guard from CH04's unframed group bytes, keeping CH04's earlier *alternative* packetization visibly separate. Classify modes as average-rate probe pass/fail/unknown under invented SCK/duty; use CH04's timed queue to avoid declaring a burst feasibility pass. Track header/CRC, chip-select turnaround, dummy, command and service duty as separate terms; physical throughput/power/area remain unknown.
5. Produce reproducible config, executable Python reference and independent tests for golden bytes, CRC/error, partial/malformed frames, reset, snapshot, reserved bits, credit/overflow, descriptor lifecycle, sequence rollover and invalid provenance. `python3 scripts/verification/check_all.py`, `git diff --check` and published CI must pass. Publish a gate separating **contract model pass** from **frozen hardware/software ABI hold**. Stop before CH07 until this limited gate is reviewed.

## Deliverables

`specs/system/CH06_HOST_CONTRACT.json`, `models/python/ch06_host.py`, `verification/unit/test_ch06_host.py`, deterministic `reports/subsystem/CH06_HOST_SUMMARY.json`, `docs/interfaces/CH06_REGISTER_PROTOCOL.md`, `docs/reviews/CH06_GATE.md`, and updated state, risk, requirement links and checks. All config numbers must carry sources/ranges/evidence class; physical inputs remain explicit `null` until measured. If actual interface constraints contradict the proposal, revise this charter, contract and downstream models through review rather than freezing a false requirement.
