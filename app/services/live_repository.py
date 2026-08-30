"""Live public GitHub inspection service."""

from app.models.repository_inspection import RepositoryInspectionOutput
from app.tools.github_repo import inspect_public_github_repository

_SELF_REFERENTIAL_CLOUD_EVIDENCE_PREFIXES = (
    "app/tools/",
    "tests/",
    "fixtures/",
)


def _remove_self_referential_cloud_evidence(payload: dict) -> dict:
    """Drop Cloud Run config hits that originate from Shipcheck's own scanners/tests.

    Generic source-code scanning can otherwise match literal evidence markers such as
    ``gcloud run deploy`` inside the inspection implementation itself. Those strings
    describe what Shipcheck searches for; they are not deployment evidence.
    """

    artifacts = payload.get("artifacts") or []
    payload["artifacts"] = [
        artifact
        for artifact in artifacts
        if not (
            artifact.get("evidence_type") == "cloud_run_config"
            and str(artifact.get("path") or "").lower().startswith(
                _SELF_REFERENTIAL_CLOUD_EVIDENCE_PREFIXES
            )
        )
    ]

    notes = payload.setdefault("notes", [])
    notes.append(
        "Self-referential Cloud Run markers in Shipcheck scanner/test paths are excluded."
    )
    return payload


async def inspect_live_repository(repository_url: str) -> RepositoryInspectionOutput:
    payload = await inspect_public_github_repository(repository_url)
    payload = _remove_self_referential_cloud_evidence(payload)
    return RepositoryInspectionOutput.model_validate(payload)
