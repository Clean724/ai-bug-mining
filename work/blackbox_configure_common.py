"""Shared process-level helpers for configure.py black-box reproducers."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


WORK_DIR = Path(__file__).resolve().parent
REPO = WORK_DIR.parent / "code" / "tensorflow_v2_11_0"
CONFIGURE = REPO / "configure.py"


def require_target() -> None:
    if not CONFIGURE.is_file():
        raise SystemExit(f"target entry point not found: {CONFIGURE}")


def write_python_launcher(bin_dir: Path, name: str, program: str) -> Path:
    """Create a command-line test double without importing target code."""
    helper = bin_dir / f"{name}_helper.py"
    helper.write_text(program, encoding="utf-8")
    launcher = bin_dir / f"{name}.cmd"
    launcher.write_text(
        f'@echo off\r\n"{sys.executable}" "{helper}" %*\r\n',
        encoding="utf-8",
    )
    return launcher


def make_workspace(root: Path) -> Path:
    workspace = root / "workspace"
    (workspace / "tools").mkdir(parents=True)
    return workspace


def base_environment(bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    env.update(
        {
            "USE_DEFAULT_PYTHON_LIB_PATH": "1",
            "TF_NEED_ROCM": "0",
            "TF_NEED_CUDA": "0",
            "TF_DOWNLOAD_CLANG": "0",
            "TF_SET_ANDROID_WORKSPACE": "0",
            "TF_ENABLE_XLA": "0",
            "CC_OPT_FLAGS": "/arch:AVX",
        }
    )
    return env


def install_valid_bazel(bin_dir: Path) -> None:
    write_python_launcher(bin_dir, "bazel", 'print("bazel 5.3.0")\n')


def run_configure(workspace: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONFIGURE), "--workspace", str(workspace)],
        cwd=REPO,
        env=env,
        input="",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=45,
        check=False,
    )


def print_process_evidence(result: subprocess.CompletedProcess[str]) -> None:
    print(f"command exit code: {result.returncode}")
    if result.stdout.strip():
        print("stdout:")
        print(result.stdout.strip())
    if result.stderr.strip():
        print("stderr:")
        print(result.stderr.strip())
