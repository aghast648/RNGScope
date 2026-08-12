#!/usr/bin/env python3
"""Check RNGScope's minimum supported Python environment.

The requirements are read directly from ``pyproject.toml`` so this smoke test
cannot drift from the package metadata.  It checks ``requires-python`` and the
core ``project.dependencies``, imports those dependencies and RNGScope, and
performs a tiny NumPy operation.

This is intentionally a minimum-version check: newer releases pass.  It is not
a substitute for the test suite or a claim that every newer release is
compatible.
"""

from __future__ import annotations

import importlib
import platform
import re
import sys
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_FILE = REPOSITORY_ROOT / "pyproject.toml"

IMPORT_NAME_OVERRIDES = {
    "scikit-learn": "sklearn",
}
NAME_PATTERN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]+\])?(.*)$")
RELEASE_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")


def load_project_requirements(path: Path) -> tuple[str, dict[str, str]]:
    """Return the Python and core dependency lower bounds from pyproject.toml."""
    try:
        with path.open("rb") as pyproject:
            configuration: dict[str, Any] = tomllib.load(pyproject)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"cannot read {path}: {exc}") from exc

    project = configuration.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("pyproject.toml has no [project] table")

    python_specifier = project.get("requires-python")
    if not isinstance(python_specifier, str):
        raise RuntimeError("[project].requires-python must be a string")
    python_minimum = extract_minimum(python_specifier, "requires-python")

    dependency_entries = project.get("dependencies")
    if not isinstance(dependency_entries, list) or not dependency_entries:
        raise RuntimeError("[project].dependencies must be a non-empty list")

    dependencies: dict[str, str] = {}
    for entry in dependency_entries:
        if not isinstance(entry, str):
            raise RuntimeError("every [project].dependencies entry must be a string")
        name, minimum = parse_dependency(entry)
        dependencies[name] = minimum

    return python_minimum, dependencies


def parse_dependency(requirement: str) -> tuple[str, str]:
    """Extract a distribution name and inclusive lower bound from a requirement."""
    requirement_without_marker = requirement.split(";", maxsplit=1)[0].strip()
    match = NAME_PATTERN.fullmatch(requirement_without_marker)
    if match is None:
        raise RuntimeError(f"cannot parse dependency requirement {requirement!r}")

    name, specifier = match.groups()
    if "@" in specifier:
        raise RuntimeError(
            f"dependency {name!r} uses a URL; a minimum version is required"
        )
    minimum = extract_minimum(specifier.strip(), f"dependency {name!r}")
    return name, minimum


def extract_minimum(specifier: str, label: str) -> str:
    """Extract the strongest ``>=`` lower bound from a comma-separated specifier."""
    minimums = [
        clause.strip().removeprefix(">=").strip()
        for clause in specifier.split(",")
        if clause.strip().startswith(">=")
    ]
    if not minimums:
        raise RuntimeError(f"{label} must declare an inclusive '>=' minimum")

    parsed = [(parse_release(item, label), item) for item in minimums]
    return max(parsed, key=lambda item: item[0])[1]


def parse_release(value: str, label: str) -> tuple[int, ...]:
    """Parse the numeric release versions used by RNGScope's lower bounds."""
    if not RELEASE_PATTERN.fullmatch(value):
        raise RuntimeError(
            f"{label} has unsupported version {value!r}; use a numeric release such as 2.0"
        )
    return tuple(int(part) for part in value.split("."))


def meets_minimum(actual: str, minimum: str) -> bool:
    """Compare numeric release versions, padding omitted trailing components with zero."""
    actual_release = parse_release(actual, "installed version")
    minimum_release = parse_release(minimum, "minimum version")
    width = max(len(actual_release), len(minimum_release))
    return actual_release + (0,) * (width - len(actual_release)) >= minimum_release + (
        0,
    ) * (width - len(minimum_release))


def report_version(label: str, minimum: str, actual: str | None) -> bool:
    """Print one minimum-version result and return whether it passed."""
    if actual is None:
        print(f"[FAIL] {label}: requires >={minimum}, but it is not installed")
        return False
    try:
        compatible = meets_minimum(actual, minimum)
    except RuntimeError as exc:
        print(f"[FAIL] {label}: cannot compare installed version {actual!r}: {exc}")
        return False
    if not compatible:
        print(f"[FAIL] {label}: requires >={minimum}, found {actual}")
        return False
    print(f"[PASS] {label}: found {actual} (minimum {minimum})")
    return True


def import_name(distribution_name: str) -> str:
    """Return the usual Python import name for a distribution."""
    normalized = distribution_name.lower().replace("_", "-")
    return IMPORT_NAME_OVERRIDES.get(normalized, normalized.replace("-", "_"))


def main() -> int:
    print("RNGScope environment smoke test")
    print(f"Platform: {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print(f"Requirements: {PYPROJECT_FILE}")
    print()

    try:
        python_minimum, dependencies = load_project_requirements(PYPROJECT_FILE)
    except RuntimeError as exc:
        print(f"[FAIL] Requirement configuration: {exc}")
        print("Environment smoke test: FAIL")
        return 1

    checks: list[bool] = [
        report_version("Python", python_minimum, platform.python_version())
    ]

    for package_name, minimum in dependencies.items():
        try:
            installed = version(package_name)
        except PackageNotFoundError:
            installed = None
        checks.append(report_version(package_name, minimum, installed))

    print()
    imported_modules: dict[str, object] = {}
    for package_name in dependencies:
        module_name = import_name(package_name)
        try:
            imported_modules[package_name] = importlib.import_module(module_name)
        except Exception as exc:  # Smoke tests should report any import-time failure.
            print(f"[FAIL] import {module_name}: {type(exc).__name__}: {exc}")
            checks.append(False)
        else:
            print(f"[PASS] import {module_name}")
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
    print(
        "The active environment does not meet the minimum requirements "
        "in pyproject.toml."
    )
    print("Install or update RNGScope and its core dependencies with:")
    print("  python -m pip install -e .")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
