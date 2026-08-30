"""Map structured requirements to deterministic fixture evidence."""

from __future__ import annotations

from app.models.schemas import (
    Evidence,
    EvidenceStatus,
    Finding,
    Requirement,
    RequirementType,
    Severity,
)
from app.tools.deployment import DeploymentObservation
from app.tools.repository import RepositoryObservation


def map_fixture_evidence(
    requirement: Requirement,
    repo_observations: dict[str, RepositoryObservation],
    deployment: DeploymentObservation,
) -> Finding:
    text = requirement.requirement_text.lower()

    if requirement.requirement_type == RequirementType.MANUAL_REVIEW:
        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.MANUAL_REVIEW,
            severity=Severity.WARNING,
            evidence=[],
            reason="This requirement requires human judgment and is not auto-verified.",
            recommended_action="Review this requirement manually before submission.",
        )

    if "google adk" in text:
        observation = repo_observations["google_adk_dependency"]
        if observation.found:
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.VERIFIED,
                severity=Severity.PASS,
                evidence=[
                    Evidence(
                        source="repository",
                        path_or_url=observation.path,
                        observed_value=observation.observed_value,
                    )
                ],
                reason="Google ADK dependency evidence was found in the repository.",
                recommended_action=None,
            )

        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.MISSING,
            severity=Severity.CRITICAL,
            evidence=[],
            reason="No Google ADK dependency evidence was found.",
            recommended_action="Add and use Google ADK, then rerun inspection.",
        )

    if "architecture diagram" in text:
        observation = repo_observations["architecture_artifact"]
        if observation.found:
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.VERIFIED,
                severity=Severity.PASS,
                evidence=[
                    Evidence(
                        source="repository",
                        path_or_url=observation.path,
                        observed_value=observation.observed_value,
                    )
                ],
                reason="Architecture evidence was found.",
                recommended_action=None,
            )

        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.MISSING,
            severity=Severity.CRITICAL,
            evidence=[],
            reason="The rules require an architecture diagram, but none was found.",
            recommended_action="Add an architecture diagram and reference it from the README.",
        )

    if "cloud deployment" in text:
        if deployment.reachable:
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.VERIFIED,
                severity=Severity.PASS,
                evidence=[
                    Evidence(
                        source="deployment_fixture",
                        path_or_url=deployment.url,
                        observed_value=f"HTTP {deployment.status_code}",
                    )
                ],
                reason="Deployment evidence is reachable in the deterministic fixture.",
                recommended_action=None,
            )

        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.UNVERIFIED,
            severity=Severity.CRITICAL,
            evidence=[],
            reason="A required working cloud deployment could not be verified.",
            recommended_action="Provide a reachable deployment and rerun inspection.",
        )

    return Finding(
        requirement_id=requirement.requirement_id,
        requirement_text=requirement.requirement_text,
        requirement_type=requirement.requirement_type,
        status=EvidenceStatus.UNVERIFIED,
        severity=Severity.WARNING,
        evidence=[],
        reason="No deterministic fixture checker exists for this requirement yet.",
        recommended_action="Review this requirement manually.",
    )
