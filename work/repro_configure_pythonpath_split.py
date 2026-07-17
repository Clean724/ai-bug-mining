"""Strict black-box reproducer for Windows PYTHONPATH propagation.

The test launches configure.py as a child process and only checks its generated
Bazel configuration. It does not import or replace any target function.
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
    if sys.platform != "win32":
        print("SKIP: this reproducer targets Windows PYTHONPATH syntax")
        return 0

    require_target()
    with tempfile.TemporaryDirectory(prefix="configure_blackbox_path_") as temp:
        root = Path(temp)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        workspace = make_workspace(root)
        install_valid_bazel(bin_dir)

        first = root / "python-extra"
        second = root / "python-vendor"
        first.mkdir()
        second.mkdir()
        supplied_pythonpath = os.pathsep.join((str(first), str(second)))

        env = base_environment(bin_dir)
        env.update(
            {
                "PYTHON_BIN_PATH": sys.executable,
                "PYTHON_LIB_PATH": str(first),
                "PYTHONPATH": supplied_pythonpath,
            }
        )
        result = run_configure(workspace, env)
        print_process_evidence(result)

        if result.returncode != 0:
            print("INCONCLUSIVE: configure.py failed before evidence could be checked")
            return 2

        bazelrc = (workspace / ".tf_configure.bazelrc").read_text(
            encoding="utf-8"
        )
        expected = f'build --action_env PYTHONPATH="{supplied_pythonpath}"'
        print("expected generated line:", expected)
        print("line present:", expected in bazelrc)

        if expected not in bazelrc:
            print(
                "DEFECT CONFIRMED: a selected library directory belongs to PYTHONPATH, "
                "but configure.py omitted PYTHONPATH from the generated Bazel environment"
            )
            return 0

        print("NO DEFECT OBSERVED: PYTHONPATH was propagated to Bazel")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
