#!/usr/bin/env python3
"""CH00 structural validation; not a circuit or requirements test."""
from pathlib import Path
import csv
ROOT = Path(__file__).resolve().parents[2]
required = ['MASTER_SPEC.md', 'README.md', 'state/PROJECT_STATE.md', 'state/DECISIONS.md', 'state/OPEN_ISSUES.md', 'state/RISK_REGISTER.md', 'state/MILESTONES.md', 'state/CHANGELOG.md', 'state/REQUIREMENTS_TRACEABILITY.csv', 'docs/adr/ADR_TEMPLATE.md', 'docs/chunks/CH_TEMPLATE.md', 'docs/literature/REVIEW_TEMPLATE.md']
for name in required:
    assert (ROOT / name).is_file(), name
with (ROOT / 'state/REQUIREMENTS_TRACEABILITY.csv').open(newline='') as f:
    columns = next(csv.reader(f))
assert columns == ['Req_ID','Subsystem','Requirement','Priority','Target_or_Limit','Verification_Method','Design_Artifact','Test_Artifact','Status','Owner','Notes']
master = (ROOT / 'MASTER_SPEC.md').read_text()
assert all(f'## CH{i:02d}' in master for i in range(51))
assert 'Temple' not in master and 'temple' not in master
assert 'CH01' in (ROOT / 'state/PROJECT_STATE.md').read_text()
print('CH00 structural check PASS (no design requirements verified)')
