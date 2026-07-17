"""Strict black-box reproducer for an empty Python library candidate list."""

from __future__ import annotations

from pathlib import Path
import tempfile

from blackbox_configure_common import (
    base_environment,
    install_valid_bazel,
    make_workspace,
    print_process_evidence,
    require_target,
    run_configure,
    write_python_launcher,
)


def main() -> int:
    require_target()
    with tempfile.TemporaryDirectory(prefix="configure_blackbox_empty_") as temp:
        root = Path(temp)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        workspace = make_workspace(root)
        install_valid_bazel(bin_dir)

        missing_library = root / "does-not-exist" / "site-packages"
        fake_python = write_python_launcher(
            bin_dir,
            "python_probe",
            f"print({str(missing_library)!r})\n",
        )

        env = base_environment(bin_dir)
        env.pop("PYTHONPATH", None)
        env.pop("PYTHON_LIB_PATH", None)
        env["PYTHON_BIN_PATH"] = str(fake_python)

        result = run_configure(workspace, env)
        print_process_evidence(result)
        combined = result.stdout + "\n" + result.stderr

        if result.returncode != 0 and "IndexError: list index out of range" in combined:
            print(
                "DEFECT CONFIRMED: the public configure command crashed with an "
                "unhandled IndexError when discovery returned no usable library path"
            )
            return 0

        if result.returncode == 0:
            print("NO DEFECT OBSERVED: configure.py handled the empty result")
            return 1

        print("INCONCLUSIVE: configure.py failed, but not with the expected IndexError")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
