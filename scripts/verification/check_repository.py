#!/usr/bin/env python3
"""Check public documentation links and chunk handoff consistency, not design correctness."""

import ast
import csv
import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
MD_LINK = re.compile(r"\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
REQUIRED = (
    "AGENTS.md", "CONTRIBUTING.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/validate.yml", "docs/README.md", "docs/REPOSITORY_MAP.md",
    "docs/governance/DATA_POLICY.md", "docs/governance/LICENSE_STATUS.md",
    "docs/inputs/REQUIRED_INPUTS.md", "docs/literature/README.md",
    "state/ASSUMPTIONS.md", "state/CHUNK_STATUS.csv",
    "state/VERIFICATION_STATUS.md", "state/PROJECT_STATE.md",
)


def slugs(markdown):
    counts = {}
    found = set()
    for title in HEADING.findall(markdown):
        title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", title)
        title = unicodedata.normalize("NFKC", title).lower()
        title = re.sub(r"[^\w\s-]", "", title)
        title = re.sub(r"\s+", "-", title.strip())
        slug = title + (f"-{counts[title]}" if title in counts else "")
        counts[title] = counts.get(title, 0) + 1
        found.add(slug)
    return found


def check_links():
    count = 0
    for source in sorted(ROOT.rglob("*.md")):
        # No hidden vendor or generated dirs should be linked from public docs.
        if ".git" in source.relative_to(ROOT).parts:
            continue
        data = source.read_text(encoding="utf-8")
        assert not re.search("Tem" + "ple", data, re.IGNORECASE), source
        for link in MD_LINK.findall(data):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue  # External URLs are not fetched by a structural check.
            target = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
            assert target.is_relative_to(ROOT), f"Link escapes repository: {source}: {link}"
            assert target.is_file(), f"Broken relative link: {source}: {link}"
            if parsed.fragment and target.suffix.lower() == ".md":
                fragment = unquote(parsed.fragment).lower()
                assert fragment in slugs(target.read_text(encoding="utf-8")), (
                    f"Broken heading anchor: {source}: {link}"
                )
            count += 1
    return count


def check_chunks():
    master = (ROOT / "MASTER_SPEC.md").read_text(encoding="utf-8")
    titles = dict((f"CH{number}", title.strip()) for number, title in re.findall(
        r"^## CH(\d{2}) — (.+)$", master, re.MULTILINE
    ))
    with (ROOT / "state/CHUNK_STATUS.csv").open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == [
            "Chunk", "Title", "Status", "Gate_Result", "Evidence", "Prerequisite_or_Blocker"
        ]
        rows = list(reader)
    assert [row["Chunk"] for row in rows] == [f"CH{i:02d}" for i in range(51)]
    assert len(titles) == 51, "Master chunk titles missing or duplicated"
    statuses = [row["Status"] for row in rows]
    assert set(statuses) <= {"COMPLETE", "ACTIVE", "PAUSED", "PLANNED"}
    first_not_complete = next((i for i, status in enumerate(statuses) if status != "COMPLETE"), 51)
    assert first_not_complete >= 3, "Previously reviewed CH00–CH02 must remain represented"
    assert statuses[first_not_complete + 1:] == ["PLANNED"] * (50 - first_not_complete)
    assert statuses[first_not_complete:first_not_complete + 1] in (
        ["ACTIVE"], ["PAUSED"], ["PLANNED"], []
    ), "Only the next uncompleted chunk may be active or paused"
    for i, row in enumerate(rows):
        assert row["Title"] == titles[row["Chunk"]], row
        assert all(row.values()), row
        if i > 0:
            assert f"CH{i-1:02d}" in row["Prerequisite_or_Blocker"], row
        if row["Status"] == "COMPLETE":
            assert row["Gate_Result"] != "NOT_RUN", row
            assert (ROOT / row["Evidence"]).is_file(), row
        elif row["Status"] == "PAUSED" and row["Gate_Result"] != "NOT_RUN":
            # A reviewed partial gate can be paused for owner inputs without
            # falsely being marked complete or losing its evidence link.
            assert (ROOT / row["Evidence"]).is_file(), row
        else:
            assert row["Gate_Result"] == "NOT_RUN" and row["Evidence"] == "none", row
    state = (ROOT / "state/PROJECT_STATE.md").read_text(encoding="utf-8")
    if first_not_complete < 51 and statuses[first_not_complete] == "PAUSED":
        assert f"CH{first_not_complete:02d} is paused" in state
    assert "Canonical branch: `main`" in state
    assert "draft PR" not in state
    return len(rows)


def check_python_syntax():
    count = 0
    for folder in ("models", "scripts", "verification"):
        for source in sorted((ROOT / folder).rglob("*.py")):
            ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            count += 1
    return count


def main():
    for name in REQUIRED:
        assert (ROOT / name).is_file(), f"Missing repository artifact: {name}"
    n_links = check_links()
    n_chunks = check_chunks()
    n_python = check_python_syntax()
    print(f"Repository readiness PASS: {n_links} relative links; {n_chunks} chunk statuses; {n_python} Python files parse (no silicon checks)")


if __name__ == "__main__":
    main()
