"""Strict black-box reproducer for TF_ENABLE_XLA int() conversion crash.

The test launches configure.py as a child process with TF_ENABLE_XLA set to
a non-numeric string and verifies the ValueError crash.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

from blackbox_configure_common import (
    base_environment,
    install_valid_bazel,
    make_workspace,
    print_process_evidence,
    require_target,
    run_configure,
)


def main() -> int:
    require_target()
    with tempfile.TemporaryDirectory(prefix="configure_blackbox_xla_") as temp:
        root = Path(temp)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        workspace = make_workspace(root)
        install_valid_bazel(bin_dir)

        env = base_environment(bin_dir)
        env["TF_ENABLE_XLA"] = "yes"

        result = run_configure(workspace, env)
        print_process_evidence(result)
        combined = result.stdout + "\n" + result.stderr

        if result.returncode != 0 and "ValueError" in combined and "invalid literal for int()" in combined:
            print(
                "DEFECT CONFIRMED: the public configure command crashed with an "
                "unhandled ValueError when TF_ENABLE_XLA was set to a non-numeric string"
            )
            return 0

        if result.returncode == 0:
            print("NO DEFECT OBSERVED: configure.py handled the non-numeric TF_ENABLE_XLA")
            return 1

        print("INCONCLUSIVE: configure.py failed, but not with the expected ValueError")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())