"""Bounded static reproducibility checks for inspected repositories.

Shipcheck does not execute untrusted repository code. The P0 reproduction checker
therefore verifies only evidence that can be established safely from inspected files:
a dependency manifest and documented setup/run commands.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.repository_inspection import RepositoryArtifact, RepositoryInspectionOutput
from app.models.schemas import EvidenceStatus


@dataclass(frozen=True)
class ReproductionObservation:
    check: str
    status: EvidenceStatus
    evidence_paths: tuple[str, ...]
    detail: str


def inspect_bounded_reproducibility(
    repository: RepositoryInspectionOutput,
) -> list[ReproductionObservation]:
    artifacts_by_type: dict[str, list[RepositoryArtifact]] = {}
    for artifact in repository.artifacts:
        artifacts_by_type.setdefault(artifact.evidence_type, []).append(artifact)

    readme_setup = artifacts_by_type.get("readme_setup", [])
    manifests = artifacts_by_type.get("dependency_manifest", [])

    observations = [
        ReproductionObservation(
            check="documented_setup",
            status=(EvidenceStatus.VERIFIED if readme_setup else EvidenceStatus.UNVERIFIED),
            evidence_paths=tuple(artifact.path for artifact in readme_setup[:2]),
            detail=(
                "README contains bounded setup/run markers."
                if readme_setup
                else "No bounded setup/run markers were detected in README.md."
            ),
        ),
        ReproductionObservation(
            check="dependency_manifest",
            status=(EvidenceStatus.VERIFIED if manifests else EvidenceStatus.UNVERIFIED),
            evidence_paths=tuple(artifact.path for artifact in manifests[:3]),
            detail=(
                "At least one dependency manifest is present."
                if manifests
                else "No supported dependency manifest was detected."
            ),
        ),
        ReproductionObservation(
            check="command_execution",
            status=EvidenceStatus.MANUAL_REVIEW,
            evidence_paths=(),
            detail=(
                "Untrusted repository commands were not executed; runtime reproduction remains "
                "manual unless a future sandboxed checker is explicitly enabled."
            ),
        ),
    ]

    return observations
