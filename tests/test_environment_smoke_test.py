"""Focused tests for the repository environment smoke test."""

from __future__ import annotations

import importlib.util
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "environment_smoke_test.py"
SPEC = importlib.util.spec_from_file_location("environment_smoke_test", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


def write_pyproject(path: Path, dependencies: list[str] | None = None) -> Path:
    """Write the smallest valid project table used by the smoke test."""
    entries = dependencies or ["numpy>=2.0", "fake-package>=1.5"]
    dependency_lines = ",\n".join(f'  "{entry}"' for entry in entries)
    path.write_text(
        "[project]\n"
        'requires-python = ">=3.11"\n'
        "dependencies = [\n"
        f"{dependency_lines}\n"
        "]\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    ("actual", "minimum", "expected"),
    [
        ("2.0", "2.0", True),
        ("2.1", "2.0", True),
        ("1.9.9", "2.0", False),
        ("2.0rc1", "2.0", False),
        ("2.0.post1", "2.0", True),
        ("2.0+local.1", "2.0", True),
    ],
)
def test_meets_minimum_uses_pep_440(
    actual: str, minimum: str, expected: bool
) -> None:
    assert smoke.meets_minimum(actual, minimum) is expected


def test_meets_minimum_rejects_invalid_installed_version() -> None:
    with pytest.raises(RuntimeError, match="invalid PEP 440 version"):
        smoke.meets_minimum("not-a-version", "2.0")


def test_extract_minimum_chooses_strongest_lower_bound() -> None:
    assert smoke.extract_minimum(">=1.5,!=1.6,>=2.0rc1", "demo") == "2.0rc1"


def test_parse_dependency_supports_extras_and_markers() -> None:
    assert smoke.parse_dependency('Demo_Package[fast]>=1.2; python_version >= "3.11"') == (
        "Demo_Package",
        "1.2",
    )


@pytest.mark.parametrize(
    "requirement",
    ["demo==1.2", "demo @ https://example.invalid/demo.whl"],
)
def test_parse_dependency_rejects_missing_minimum(requirement: str) -> None:
    with pytest.raises(RuntimeError):
        smoke.parse_dependency(requirement)


def test_load_project_requirements(tmp_path: Path) -> None:
    pyproject = write_pyproject(tmp_path / "pyproject.toml")
    assert smoke.load_project_requirements(pyproject) == (
        "3.11",
        {"numpy": "2.0", "fake-package": "1.5"},
    )


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("not valid = [", "cannot read"),
        ("[build-system]\n", r"no \[project\] table"),
        ("[project]\nrequires-python = 3.11\ndependencies = []\n", "must be a string"),
        (
            '[project]\nrequires-python = ">=3.11"\ndependencies = []\n',
            "must be a non-empty list",
        ),
    ],
)
def test_load_project_requirements_rejects_bad_configuration(
    tmp_path: Path, content: str, message: str
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(content, encoding="utf-8")
    with pytest.raises(RuntimeError, match=message):
        smoke.load_project_requirements(pyproject)


@pytest.mark.parametrize(
    ("minimum", "actual", "expected", "message"),
    [
        ("2.0", "2.0", True, "[PASS] demo"),
        ("2.0", "1.9", False, "requires >=2.0, found 1.9"),
        ("2.0", None, False, "it is not installed"),
        ("2.0", "invalid", False, "cannot compare installed version"),
    ],
)
def test_report_version_outputs_result(
    minimum: str,
    actual: str | None,
    expected: bool,
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert smoke.report_version("demo", minimum, actual) is expected
    assert message in capsys.readouterr().out


def test_import_name_normalizes_distribution_names() -> None:
    assert smoke.import_name("scikit_learn") == "sklearn"
    assert smoke.import_name("Demo-Package") == "demo_package"


def configure_successful_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pyproject = write_pyproject(tmp_path / "pyproject.toml")
    monkeypatch.setattr(smoke, "PYPROJECT_FILE", pyproject)
    monkeypatch.setattr(smoke.platform, "python_version", lambda: "3.11.9")
    monkeypatch.setattr(
        smoke,
        "version",
        lambda name: {"numpy": "2.0.post1", "fake-package": "1.5+local"}[name],
    )

    def import_module(name: str) -> object:
        modules = {
            "numpy": np,
            "fake_package": SimpleNamespace(),
            "rngscope": SimpleNamespace(__version__="0.1.0"),
        }
        return modules[name]

    monkeypatch.setattr(smoke.importlib, "import_module", import_module)


def test_main_success_returns_zero(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_successful_main(monkeypatch, tmp_path)
    assert smoke.main() == 0
    output = capsys.readouterr().out
    assert "[PASS] tiny binary-array operation" in output
    assert output.rstrip().endswith("Environment smoke test: PASS")


def test_main_missing_package_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_successful_main(monkeypatch, tmp_path)
    original_version = smoke.version

    def missing_package(name: str) -> str:
        if name == "fake-package":
            raise PackageNotFoundError(name)
        return original_version(name)

    monkeypatch.setattr(smoke, "version", missing_package)
    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert "fake-package: requires >=1.5, but it is not installed" in output
    assert "Environment smoke test: FAIL" in output


def test_main_import_failure_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_successful_main(monkeypatch, tmp_path)
    original_import = smoke.importlib.import_module

    def failed_import(name: str) -> object:
        if name == "fake_package":
            raise ImportError("simulated import failure")
        return original_import(name)

    monkeypatch.setattr(smoke.importlib, "import_module", failed_import)
    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert "[FAIL] import fake_package: ImportError: simulated import failure" in output
    assert "Environment smoke test: FAIL" in output


def test_main_bad_configuration_returns_one(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[build-system]\n", encoding="utf-8")
    monkeypatch.setattr(smoke, "PYPROJECT_FILE", pyproject)
    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert "[FAIL] Requirement configuration" in output
    assert output.rstrip().endswith("Environment smoke test: FAIL")
