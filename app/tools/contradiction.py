"""Bounded contradiction detection for explicit submission claims."""

from __future__ import annotations

import re

from app.models.repository_inspection import RepositoryInspectionOutput
from app.models.schemas import Evidence, EvidenceStatus, Finding, RequirementType, Severity
from app.tools.deployment import DeploymentObservation


def _artifact_map(repository: RepositoryInspectionOutput) -> dict[str, list]:
    result: dict[str, list] = {}
    for artifact in repository.artifacts:
        result.setdefault(artifact.evidence_type, []).append(artifact)
    return result


def detect_claim_contradictions(
    claims: list[str],
    repository: RepositoryInspectionOutput,
    deployment: DeploymentObservation,
) -> list[Finding]:
    artifacts = _artifact_map(repository)
    findings: list[Finding] = []

    primary = artifacts.get("gemini_primary_model_config", [])
    primary_value = (
        (primary[0].observed_value or "").lower()
        if primary
        else ""
    )

    for index, claim in enumerate(claims, start=1):
        lowered = claim.lower()
        evidence: list[Evidence] = []
        contradiction_reason: str | None = None

        version_match = re.search(r"gemini[-\s]?([0-9]+\.[0-9]+)", lowered)
        if version_match and primary_value:
            claimed_version = version_match.group(1)
            if claimed_version not in primary_value:
                artifact = primary[0]
                evidence.append(
                    Evidence(
                        source="repository",
                        path_or_url=artifact.path,
                        observed_value=artifact.observed_value,
                    )
                )
                contradiction_reason = (
                    f"Claim references Gemini {claimed_version}, but repository "
                    f"primary model evidence is {artifact.observed_value}."
                )

        if "google adk" in lowered and not artifacts.get("google_adk"):
            contradiction_reason = (
                "Claim says Google ADK is used, but no Google ADK repository evidence "
                "was found."
            )

        if (
            "cloud run" in lowered or ".run.app" in lowered
        ) and not deployment.google_cloud_runtime:
            contradiction_reason = (
                "Claim says the project runs on Google Cloud Run, but no reachable "
                "Cloud Run runtime was verified."
            )

        if contradiction_reason:
            findings.append(
                Finding(
                    requirement_id=f"CLAIM-{index:03d}",
                    requirement_text=claim,
                    requirement_type=RequirementType.CHECKABLE,
                    status=EvidenceStatus.CONTRADICTED,
                    severity=Severity.CRITICAL,
                    evidence=evidence,
                    reason=contradiction_reason,
                    recommended_action=(
                        "Correct the claim or provide matching implementation evidence."
                    ),
                )
            )

    return findings
