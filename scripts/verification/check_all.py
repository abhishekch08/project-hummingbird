#!/usr/bin/env python3
"""Run the public checks from a fresh checkout with only Python 3 installed."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STEPS = [
    ["scripts/verification/check_bootstrap.py"],
    ["scripts/verification/check_requirements.py"],
    ["models/python/ch02_concurrency.py", "--check"],
    ["models/python/ch03_energy.py", "--check"],
    ["models/python/ch04_dataflow.py", "--check"],
    ["models/python/ch05_timing.py", "--check"],
    ["-m", "unittest", "discover", "-s", "verification/unit", "-p", "test_ch*.py"],
    ["scripts/verification/check_repository.py"],
]


def main():
    for args in STEPS:
        print(f"Running {sys.executable} {' '.join(args)}", flush=True)
        subprocess.run([sys.executable, *args], cwd=ROOT, check=True)
    print("Public regression PASS (structure, provisional requirements, CH02–CH05 conditional models)")


if __name__ == "__main__":
    main()
