"""Strict black-box reproducer for non-UTF-8 command output handling."""

from __future__ import annotations

from pathlib import Path
import tempfile

from blackbox_configure_common import (
    base_environment,
    make_workspace,
    print_process_evidence,
    require_target,
    run_configure,
    write_python_launcher,
)


def main() -> int:
    require_target()
    with tempfile.TemporaryDirectory(prefix="configure_blackbox_encoding_") as temp:
        root = Path(temp)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        workspace = make_workspace(root)

        write_python_launcher(
            bin_dir,
            "bazel",
            "import sys\n"
            "sys.stdout.buffer.write('编译器版本'.encode('gbk'))\n",
        )
        env = base_environment(bin_dir)

        result = run_configure(workspace, env)
        print_process_evidence(result)
        combined = result.stdout + "\n" + result.stderr

        if result.returncode != 0 and "UnicodeDecodeError" in combined:
            print(
                "DEFECT CONFIRMED: the public configure command crashed while decoding "
                "a tool's non-UTF-8 output"
            )
            return 0

        if result.returncode == 0:
            print("NO DEFECT OBSERVED: configure.py tolerated non-UTF-8 tool output")
            return 1

        print("INCONCLUSIVE: configure.py failed, but not with UnicodeDecodeError")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
