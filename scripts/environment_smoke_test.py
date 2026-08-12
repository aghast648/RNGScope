#!/usr/bin/env python3
"""Verify that the active Python environment matches RNGScope's frozen reference.

Run this script from any directory. It locates ``requirements-frozen.txt``
relative to the repository, compares Python and package versions exactly,
checks the core imports, and performs a tiny NumPy binary-array operation.
"""

from __future__ import annotations

import importlib
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILE = REPOSITORY_ROOT / "requirements-frozen.txt"

IMPORT_NAMES = {
    "numpy": "numpy",
    "scipy": "scipy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scikit-learn": "sklearn",
}


def load_reference_versions(path: Path) -> tuple[str, dict[str, str]]:
    """Read the frozen Python and package versions from a pip requirements file."""
    expected_python: str | None = None
    expected_packages: dict[str, str] = {}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"cannot read reference file {path}: {exc}") from exc

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("# python=="):
            expected_python = line.removeprefix("# python==").strip()
            continue
        if not line or line.startswith("#") or line.startswith("-e "):
            continue
        if "==" not in line:
            raise RuntimeError(
                f"reference entry must use an exact '==' pin: {raw_line!r}"
            )
        name, expected = (part.strip() for part in line.split("==", maxsplit=1))
        if not name or not expected:
            raise RuntimeError(f"invalid reference entry: {raw_line!r}")
        expected_packages[name] = expected

    if expected_python is None:
        raise RuntimeError("reference file does not declare '# python==<version>'")
    if not expected_packages:
        raise RuntimeError("reference file contains no frozen package versions")

    return expected_python, expected_packages


def report_version(label: str, expected: str, actual: str | None) -> bool:
    """Print one exact-version result and return whether it passed."""
    if actual is None:
        print(f"[FAIL] {label}: expected {expected}, but it is not installed")
        return False
    if actual != expected:
        print(f"[FAIL] {label}: expected {expected}, found {actual}")
        return False
    print(f"[PASS] {label}: {actual}")
    return True


def main() -> int:
    print("RNGScope environment smoke test")
    print(f"Platform: {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print(f"Reference: {REFERENCE_FILE}")
    print()

    try:
        expected_python, expected_packages = load_reference_versions(REFERENCE_FILE)
    except RuntimeError as exc:
        print(f"[FAIL] Reference configuration: {exc}")
        print("Environment smoke test: FAIL")
        return 1

    checks: list[bool] = []
    checks.append(
        report_version("Python", expected_python, platform.python_version())
    )

    for package_name, expected in expected_packages.items():
        try:
            installed = version(package_name)
        except PackageNotFoundError:
            installed = None
        checks.append(report_version(package_name, expected, installed))

    print()
    imported_modules: dict[str, object] = {}
    for package_name, import_name in IMPORT_NAMES.items():
        try:
            imported_modules[package_name] = importlib.import_module(import_name)
        except Exception as exc:  # Smoke tests should report any import-time failure.
            print(f"[FAIL] import {import_name}: {type(exc).__name__}: {exc}")
            checks.append(False)
        else:
            print(f"[PASS] import {import_name}")
            checks.append(True)

    try:
        rngscope = importlib.import_module("rngscope")
    except Exception as exc:
        print(f"[FAIL] import rngscope: {type(exc).__name__}: {exc}")
        checks.append(False)
    else:
        print(f"[PASS] import rngscope: {getattr(rngscope, '__version__', 'unknown')}")
        checks.append(True)

    numpy_module = imported_modules.get("numpy")
    if numpy_module is not None:
        try:
            sample = numpy_module.array([0, 1, 0, 1], dtype=numpy_module.uint8)
            assert sample.shape == (4,)
            assert bool(numpy_module.all((sample == 0) | (sample == 1)))
        except Exception as exc:
            print(f"[FAIL] tiny binary-array operation: {type(exc).__name__}: {exc}")
            checks.append(False)
        else:
            print("[PASS] tiny binary-array operation")
            checks.append(True)

    print()
    if all(checks):
        print("Environment smoke test: PASS")
        return 0

    print("Environment smoke test: FAIL")
    print("The active environment does not exactly match the frozen reference.")
    print("Install the pinned packages with:")
    print("  python -m pip install -r requirements-frozen.txt")
    print("A Python mismatch must be corrected with a matching Python interpreter.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
