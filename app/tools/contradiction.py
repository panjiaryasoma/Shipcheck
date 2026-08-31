"""Bounded evidence checks for explicit submission claims."""

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


def _unsupported_claim(
    *,
    index: int,
    claim: str,
    reason: str,
    evidence: list[Evidence] | None = None,
) -> Finding:
    return Finding(
        requirement_id=f"CLAIM-{index:03d}",
        requirement_text=claim,
        requirement_type=RequirementType.CHECKABLE,
        status=EvidenceStatus.UNVERIFIED,
        severity=Severity.HIGH,
        evidence=evidence or [],
        reason=reason,
        recommended_action="Provide matching evidence or narrow the submission claim.",
    )


def detect_claim_contradictions(
    claims: list[str],
    repository: RepositoryInspectionOutput,
    deployment: DeploymentObservation,
) -> list[Finding]:
    """Return direct contradictions and explicitly unsupported claims.

    Missing proof is not a contradiction. A claim is marked CONTRADICTED only when
    Shipcheck has concrete evidence that conflicts with it; absent evidence is surfaced
    as UNVERIFIED/HIGH instead.
    """

    artifacts = _artifact_map(repository)
    findings: list[Finding] = []

    primary = artifacts.get("gemini_primary_model_config", [])
    primary_value = (primary[0].observed_value or "").lower() if primary else ""

    for index, claim in enumerate(claims, start=1):
        lowered = claim.lower()

        version_match = re.search(r"gemini[-\s]?([0-9]+\.[0-9]+)", lowered)
        if version_match:
            claimed_version = version_match.group(1)
            if primary_value:
                if claimed_version not in primary_value:
                    artifact = primary[0]
                    findings.append(
                        Finding(
                            requirement_id=f"CLAIM-{index:03d}",
                            requirement_text=claim,
                            requirement_type=RequirementType.CHECKABLE,
                            status=EvidenceStatus.CONTRADICTED,
                            severity=Severity.CRITICAL,
                            evidence=[
                                Evidence(
                                    source="repository",
                                    path_or_url=artifact.path,
                                    observed_value=artifact.observed_value,
                                )
                            ],
                            reason=(
                                f"Claim references Gemini {claimed_version}, but repository "
                                f"primary model evidence is {artifact.observed_value}."
                            ),
                            recommended_action=(
                                "Correct the claim or change the primary model configuration."
                            ),
                        )
                    )
                    continue
            else:
                findings.append(
                    _unsupported_claim(
                        index=index,
                        claim=claim,
                        reason=(
                            "The claim names a Gemini version, but no explicit primary-model "
                            "configuration was found in the inspected repository."
                        ),
                    )
                )
                continue

        if "google adk" in lowered and not artifacts.get("google_adk"):
            findings.append(
                _unsupported_claim(
                    index=index,
                    claim=claim,
                    reason=(
                        "The claim says Google ADK is used, but Shipcheck found no matching "
                        "repository evidence. Absence of proof is not treated as a contradiction."
                    ),
                )
            )
            continue

        if ("cloud run" in lowered or ".run.app" in lowered) and not (
            deployment.reachable and deployment.google_cloud_runtime
        ):
            deployment_evidence = []
            if deployment.url:
                deployment_evidence.append(
                    Evidence(
                        source="deployment",
                        path_or_url=deployment.url,
                        observed_value=(
                            f"HTTP {deployment.status_code}"
                            if deployment.status_code is not None
                            else "Deployment was not verified as Cloud Run"
                        ),
                    )
                )

            findings.append(
                _unsupported_claim(
                    index=index,
                    claim=claim,
                    reason=(
                        "The claim references Google Cloud Run, but no reachable *.run.app "
                        "runtime was verified. This is missing proof, not direct contradiction."
                    ),
                    evidence=deployment_evidence,
                )
            )

    return findings
