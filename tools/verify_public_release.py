#!/usr/bin/env python3
"""Offline verification gate for the bounded ECL public release."""

from __future__ import annotations

import compileall
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md", ".py", ".toml", ".cff", ".json", ".yml", ".yaml", ".txt"
}
EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", "outputs", "build", "dist"}

FORBIDDEN_PATTERNS = {
    "private Windows path": re.compile(r"[A-Za-z]:\\\\Users\\\\|[A-Za-z]:\\Users\\", re.IGNORECASE),
    "private Unix home path": re.compile(r"/(?:home|Users)/[^/\s]+/", re.IGNORECASE),
    "credential assignment": re.compile(
        r"(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"]+['\"]",
        re.IGNORECASE,
    ),
    "forbidden framework naming": re.compile(
        r"(?:dabas\s*[-–—]?\s*generalized\s+euler|generalized\s+euler|dabas\s+euler)",
        re.IGNORECASE,
    ),
}

REQUIRED_IDENTITY = {
    "LICENSE": ["Monty Dabas"],
    "CITATION.cff": ["given-names: \"Monty\"", "family-names: \"Dabas\"", "0009-0005-6948-209X"],
    "pyproject.toml": ["Monty Dabas"],
    "README.md": ["Monty Dabas", "0009-0005-6948-209X"],
}


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def scan_files() -> list[str]:
    failures: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{relative}: detected {label}")
    return failures


def verify_identity() -> list[str]:
    failures: list[str] = []
    for filename, required_values in REQUIRED_IDENTITY.items():
        path = ROOT / filename
        if not path.is_file():
            failures.append(f"missing required metadata file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        for value in required_values:
            if value not in text:
                failures.append(f"{filename}: missing required identity value {value!r}")
    return failures


def run_tests() -> int:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode


def main() -> int:
    failures = scan_files() + verify_identity()
    if not compileall.compile_dir(ROOT / "src", quiet=1):
        failures.append("Python source compilation failed")
    if not compileall.compile_dir(ROOT / "tests", quiet=1):
        failures.append("Python test compilation failed")

    test_code = run_tests()
    if test_code != 0:
        failures.append(f"unit tests failed with exit code {test_code}")

    if failures:
        print("PUBLIC RELEASE VERIFICATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PUBLIC RELEASE VERIFICATION: PASS")
    print(f"scanned_files={len(iter_text_files())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
