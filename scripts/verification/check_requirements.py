#!/usr/bin/env python3
"""CH01 register consistency and source coverage, not silicon verification."""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = (ROOT / "MASTER_SPEC.md").read_text()
CSV = ROOT / "state/REQUIREMENTS_TRACEABILITY.csv"
FIELDS = [
    "Req_ID", "Subsystem", "Requirement", "Priority", "Target_or_Limit",
    "Verification_Method", "Design_Artifact", "Test_Artifact", "Status", "Owner", "Notes",
]
PRIORITY = {"MUST", "SHOULD", "MAY", "STRETCH"}
STATUS = {"CANDIDATE", "NEEDS_DEFINITION", "RESEARCH_ONLY", "PROCESS_ACTIVE"}
SOURCE_RE = re.compile(r"source=MASTER_SPEC\.md §([0-9,–]+); issue=(none|OI-[0-9]{3})$")


def sections(expr):
    for part in expr.split(","):
        if "–" in part:
            left, right = map(int, part.split("–"))
            assert left <= right, part
            yield from range(left, right + 1)
        else:
            yield int(part)


with CSV.open(newline="") as handle:
    reader = csv.DictReader(handle)
    assert reader.fieldnames == FIELDS, "Unexpected register schema"
    rows = list(reader)

assert len(rows) >= 150, "Register is still a scaffold"
ids = [r["Req_ID"] for r in rows]
assert len(ids) == len(set(ids)), "Duplicate requirement IDs"
assert len([r["Requirement"] for r in rows]) == len(set(r["Requirement"] for r in rows)), "Duplicated requirement wording"
known_issues = set(re.findall(r"OI-[0-9]{3}", (ROOT / "state/OPEN_ISSUES.md").read_text()))
covered = set()
counts = {}
for row in rows:
    assert all(row[field].strip() for field in FIELDS), f"Blank field: {row['Req_ID']}"
    assert re.fullmatch(r"[A-Z]{3,4}-[0-9]{4}", row["Req_ID"]), row["Req_ID"]
    assert row["Priority"] in PRIORITY, row["Req_ID"]
    assert row["Status"] in STATUS, row["Req_ID"]
    assert row["Design_Artifact"].endswith("/"), row["Req_ID"]
    assert row["Test_Artifact"].endswith("/"), row["Req_ID"]
    match = SOURCE_RE.fullmatch(row["Notes"])
    assert match, f"Missing or invalid master source: {row['Req_ID']}"
    assert match[2] == "none" or match[2] in known_issues, row["Req_ID"]
    covered.update(sections(match[1]))
    prefix, number = row["Req_ID"].split("-")
    counts.setdefault(prefix, []).append(int(number))

for prefix, numbers in counts.items():
    assert numbers == list(range(1, len(numbers) + 1)), f"Noncontiguous IDs: {prefix}"
headings = {int(s) for s in re.findall(r"^# (\d+)\.", MASTER, re.M)}
assert set(range(0, 62)).issubset(headings), "Master section numbering changed"
missing = (set(range(0, 53)) | set(range(55, 62))) - covered
assert not missing, f"Unclassified source sections: {sorted(missing)}"
assert {"BIO", "EDA", "ECH", "OPT", "THM", "AUD", "PMU", "SAFE", "DFT", "PKG"} <= counts.keys()
assert "Temple" not in MASTER and "temple" not in MASTER
print(f"CH01 register consistency PASS: {len(rows)} candidate/process IDs; all nonduplicate source sections classified")
