"""Bounded local-repository inspector for deterministic fixture evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepositoryObservation:
    key: str
    found: bool
    path: str | None = None
    observed_value: str | None = None


_ARCHITECTURE_NAMES = {
    "architecture.md",
    "architecture.mmd",
    "architecture.mermaid",
    "architecture.png",
    "architecture.jpg",
    "architecture.jpeg",
    "architecture.svg",
}


def inspect_fixture_repository(path: str | Path) -> dict[str, RepositoryObservation]:
    repo = Path(path)

    if not repo.exists() or not repo.is_dir():
        raise FileNotFoundError(f"Fixture repository not found: {repo}")

    observations: dict[str, RepositoryObservation] = {}

    # Google ADK dependency evidence.
    pyproject = repo / "pyproject.toml"
    pyproject_text = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
    has_adk_dependency = "google-adk" in pyproject_text.lower()

    observations["google_adk_dependency"] = RepositoryObservation(
        key="google_adk_dependency",
        found=has_adk_dependency,
        path=str(pyproject) if pyproject.exists() else None,
        observed_value="google-adk" if has_adk_dependency else None,
    )

    # Architecture artifact evidence.
    architecture_match: Path | None = None
    for candidate in repo.rglob("*"):
        if candidate.is_file() and candidate.name.lower() in _ARCHITECTURE_NAMES:
            architecture_match = candidate
            break

    observations["architecture_artifact"] = RepositoryObservation(
        key="architecture_artifact",
        found=architecture_match is not None,
        path=str(architecture_match) if architecture_match else None,
        observed_value=architecture_match.name if architecture_match else None,
    )

    return observations
