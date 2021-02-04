"""Nox sessions."""

import nox
from nox.sessions import Session
import nox_poetry.patch

locations = "src", "tests", "noxfile.py"
nox.options.stop_on_first_error = True
nox.options.sessions = (
    "lint",
    "mypy",
    "safety",
    "unit_tests",
    "integration_tests",
    "contract_tests",
)


@nox.session
def unit_tests(session: Session) -> None:
    """Run the unit test suite."""
    args = session.posargs
    session.install(".")
    session.install(
        "pytest",
        "pytest-mock",
        "pytest-aiohttp",
    )
    session.run(
        "pytest",
        "-m unit",
        "-rfE",
        *args,
        env={},
    )


@nox.session
def integration_tests(session: Session) -> None:
    """Run the integration test suite."""
    args = session.posargs or ["--cov"]
    session.install(".")
    session.install(
        "coverage[toml]",
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-aiohttp",
    )
    session.run(
        "pytest",
        "-m integration",
        "-rfE",
        *args,
        env={},
    )


@nox.session
def contract_tests(session: Session) -> None:
    """Run the contract test suite."""
    args = session.posargs
    session.install(".")
    session.install(
        "pytest",
        "pytest-docker",
        "pytest_mock",
        "pytest-asyncio",
    )
    session.run(
        "pytest",
        "-m contract",
        "-rfE",
        *args,
        env={},
    )


@nox.session
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-annotations",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
        "pep8-naming",
    )
    session.run("flake8", *args)


@nox.session
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = nox_poetry.export_requirements(session)
    session.install("safety")
    session.run("safety", "check", f"--file={requirements}", "--bare")


@nox.session
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install("mypy")
    session.run("mypy", *args)


@nox.session
def coverage(session: Session) -> None:
    """Upload coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
