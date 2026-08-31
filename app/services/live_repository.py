"""Live public GitHub inspection service."""

from app.models.repository_inspection import RepositoryArtifact, RepositoryInspectionOutput
from app.models.schemas import EvidenceStatus
from app.tools.github_repo import inspect_public_github_repository
from app.tools.reproduction import inspect_bounded_reproducibility

_SELF_REFERENTIAL_CLOUD_EVIDENCE_PREFIXES = (
    "app/tools/",
    "tests/",
    "fixtures/",
)


def _remove_self_referential_cloud_evidence(payload: dict) -> dict:
    """Drop Cloud Run config hits that originate from scanner/test implementation paths."""

    artifacts = payload.get("artifacts") or []
    retained = [
        artifact
        for artifact in artifacts
        if not (
            artifact.get("evidence_type") == "cloud_run_config"
            and str(artifact.get("path") or "").lower().startswith(
                _SELF_REFERENTIAL_CLOUD_EVIDENCE_PREFIXES
            )
        )
    ]
    removed_count = len(artifacts) - len(retained)
    payload["artifacts"] = retained

    if removed_count:
        payload.setdefault("notes", []).append(
            "Self-referential Cloud Run markers in scanner/test paths were excluded."
        )
    return payload


def _attach_reproduction_observations(
    repository: RepositoryInspectionOutput,
) -> RepositoryInspectionOutput:
    observations = inspect_bounded_reproducibility(repository)

    for observation in observations:
        evidence = ", ".join(observation.evidence_paths) or "no executable evidence"
        repository.notes.append(
            f"Reproduction check {observation.check}: {observation.status.value}; "
            f"{observation.detail} Evidence: {evidence}."
        )

    static_checks = observations[:2]
    if static_checks and all(
        observation.status == EvidenceStatus.VERIFIED for observation in static_checks
    ):
        evidence_paths = [
            path
            for observation in static_checks
            for path in observation.evidence_paths
        ]
        repository.artifacts.append(
            RepositoryArtifact(
                evidence_type="bounded_reproduction",
                path=evidence_paths[0] if evidence_paths else "repository",
                observed_value=(
                    "README setup markers and a dependency manifest were verified; "
                    "untrusted commands were not executed."
                ),
            )
        )

    return repository


async def inspect_live_repository(repository_url: str) -> RepositoryInspectionOutput:
    payload = await inspect_public_github_repository(repository_url)
    payload = _remove_self_referential_cloud_evidence(payload)
    repository = RepositoryInspectionOutput.model_validate(payload)
    return _attach_reproduction_observations(repository)
