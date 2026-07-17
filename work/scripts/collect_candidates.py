#!/usr/bin/env python3
"""Collect candidate vulnerability hotspots from a large source tree."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


RISK_DIR_PARTS = (
    "tensorflow/core/kernels",
    "tensorflow/core/ops",
    "tensorflow/lite",
    "tensorflow/python/kernel_tests",
)

RISK_PATTERNS = [
    (re.compile(r"\bCHECK(_[A-Z]+)?\s*\("), "process-aborting CHECK"),
    (re.compile(r"\bDCHECK(_[A-Z]+)?\s*\("), "debug-only DCHECK"),
    (re.compile(r"/\s*[A-Za-z_][A-Za-z0-9_]*"), "possible division"),
    (re.compile(r"\bFastBoundsCheck\b|\bbounds_check\b", re.I), "bounds check"),
    (re.compile(r"\bflat<|\btensor<|\bvec<"), "tensor flattening"),
    (re.compile(r"\bdim_size\s*\(|\bNumElements\s*\("), "shape/size handling"),
    (re.compile(r"\bOP_REQUIRES\b|\bInvalidArgument\b"), "input validation"),
    (re.compile(r"\bmemcpy\b|\bmemmove\b|\bstrncpy\b"), "raw memory copy"),
    (re.compile(r"\bint32\b|\bint64\b|\bsize_t\b"), "integer size arithmetic"),
]

SOURCE_SUFFIXES = {".cc", ".h", ".c", ".cu", ".py"}


def is_risk_path(path: Path) -> bool:
    normalized = path.as_posix()
    return any(part in normalized for part in RISK_DIR_PARTS)


def collect(repo: Path, max_per_file: int) -> list[tuple[Path, int, str, str]]:
    findings: list[tuple[Path, int, str, str]] = []
    for root, _, files in os.walk(repo):
        root_path = Path(root)
        if ".git" in root_path.parts:
            continue
        for name in files:
            path = root_path / name
            if path.suffix not in SOURCE_SUFFIXES or not is_risk_path(path):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            per_file = 0
            for index, line in enumerate(lines, start=1):
                stripped = line.strip()
                if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                    continue
                for regex, reason in RISK_PATTERNS:
                    if regex.search(stripped):
                        findings.append((path.relative_to(repo), index, reason, stripped[:220]))
                        per_file += 1
                        break
                if per_file >= max_per_file:
                    break
    return findings


def write_markdown(findings: list[tuple[Path, int, str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("# Candidate Vulnerability Hotspots\n\n")
        f.write("This file is an intermediate candidate list. Each item still needs LLM review and runtime validation.\n\n")
        for path, line_no, reason, code in findings:
            f.write(f"## {path}:{line_no}\n\n")
            f.write(f"- Reason: {reason}\n")
            f.write(f"- Code: `{code}`\n\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Path to the target source tree")
    parser.add_argument("--out", default="work/candidate_findings.md")
    parser.add_argument("--max-per-file", type=int, default=12)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"repository path does not exist: {repo}")

    findings = collect(repo, args.max_per_file)
    write_markdown(findings, Path(args.out))
    print(f"collected {len(findings)} candidate lines into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

