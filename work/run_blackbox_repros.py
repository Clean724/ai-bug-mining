"""Run all configure.py black-box reproducers.

Exit code 0 means every applicable reproducer observed its expected defect.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TESTS = (
    ROOT / "repro_configure_pythonpath_split.py",
    ROOT / "repro_configure_empty_python_lib_paths.py",
    ROOT / "repro_configure_run_shell_non_utf8.py",
    ROOT / "repro_configure_xla_int_conversion.py",
)


def main() -> int:
    failures = []
    for test in TESTS:
        print(f"\n=== {test.name} ===")
        result = subprocess.run([sys.executable, str(test)], check=False)
        if result.returncode != 0:
            failures.append((test.name, result.returncode))

    if failures:
        print("\nBlack-box run did not complete:")
        for name, code in failures:
            print(f"- {name}: exit {code}")
        return 1

    print("\nAll applicable black-box reproducers observed their expected defects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
