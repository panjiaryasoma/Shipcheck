"""Map live extracted requirements to repository and deployment evidence."""

from __future__ import annotations

import re

from app.models.repository_inspection import RepositoryArtifact, RepositoryInspectionOutput
from app.models.rules_extraction import ExtractedRequirement
from app.models.schemas import Evidence, EvidenceStatus, Finding, RequirementType, Severity
from app.tools.deployment import DeploymentObservation


def _artifact_index(
    repository: RepositoryInspectionOutput,
) -> dict[str, list[RepositoryArtifact]]:
    result: dict[str, list[RepositoryArtifact]] = {}
    for artifact in repository.artifacts:
        result.setdefault(artifact.evidence_type, []).append(artifact)
    return result


def _evidence_from_artifact(artifact: RepositoryArtifact) -> Evidence:
    return Evidence(
        source="repository",
        path_or_url=artifact.path,
        observed_value=artifact.observed_value,
    )


def _manual(requirement: ExtractedRequirement, reason: str) -> Finding:
    return Finding(
        requirement_id=requirement.requirement_id,
        requirement_text=requirement.requirement_text,
        requirement_type=requirement.requirement_type,
        status=EvidenceStatus.MANUAL_REVIEW,
        severity=Severity.WARNING,
        evidence=[],
        reason=reason,
        recommended_action="Review this requirement manually before submission.",
    )


def _verified(
    requirement: ExtractedRequirement,
    artifact: RepositoryArtifact,
    reason: str,
) -> Finding:
    return Finding(
        requirement_id=requirement.requirement_id,
        requirement_text=requirement.requirement_text,
        requirement_type=requirement.requirement_type,
        status=EvidenceStatus.VERIFIED,
        severity=Severity.PASS,
        evidence=[_evidence_from_artifact(artifact)],
        reason=reason,
        recommended_action=None,
    )


def _missing(
    requirement: ExtractedRequirement,
    reason: str,
    action: str,
    *,
    status: EvidenceStatus = EvidenceStatus.MISSING,
) -> Finding:
    return Finding(
        requirement_id=requirement.requirement_id,
        requirement_text=requirement.requirement_text,
        requirement_type=requirement.requirement_type,
        status=status,
        severity=Severity.CRITICAL,
        evidence=[],
        reason=reason,
        recommended_action=action,
    )


def map_live_requirement(
    requirement: ExtractedRequirement,
    repository: RepositoryInspectionOutput,
    deployment: DeploymentObservation,
) -> Finding:
    text = requirement.requirement_text.lower()
    artifacts = _artifact_index(repository)

    if requirement.requirement_type == RequirementType.INFORMATIONAL:
        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.NOT_APPLICABLE,
            severity=Severity.PASS,
            evidence=[],
            reason="Informational rule; no automated compliance verdict is required.",
            recommended_action=None,
        )

    if requirement.requirement_type == RequirementType.MANUAL_REVIEW:
        return _manual(
            requirement,
            "The extracted rule explicitly requires human or subjective judgment.",
        )

    manual_markers = (
        "age of majority",
        "resident of",
        "team member",
        "representative",
        "intellectual property",
        "original work",
        "submission period",
        "newly created",
        "select one category",
        "text description",
        "video",
        "youtube",
        "vimeo",
        "subtitle",
        "judges",
        "judging",
    )
    if any(marker in text for marker in manual_markers):
        return _manual(
            requirement,
            "This mandatory rule cannot be proven from repository/runtime evidence alone.",
        )

    if "gemini" in text and ("3.5" in text or "newer" in text):
        candidates = artifacts.get("gemini_primary_model_config", [])
        if not candidates:
            return _missing(
                requirement,
                "No explicit primary Gemini model configuration was found.",
                "Declare the primary Gemini model in public configuration and rerun inspection.",
            )

        artifact = candidates[0]
        value = (artifact.observed_value or "").lower()
        match = re.search(r"gemini-([0-9]+)\.([0-9]+)", value)
        if not match:
            return _missing(
                requirement,
                "Gemini model evidence exists but its version could not be verified.",
                "Use an explicit Gemini model identifier such as gemini-3.7-flash.",
                status=EvidenceStatus.UNVERIFIED,
            )

        major, minor = int(match.group(1)), int(match.group(2))
        if (major, minor) < (3, 5):
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.CONTRADICTED,
                severity=Severity.CRITICAL,
                evidence=[_evidence_from_artifact(artifact)],
                reason=(
                    f"Primary model {artifact.observed_value} is below the required "
                    "Gemini 3.5 minimum."
                ),
                recommended_action="Upgrade the primary Gemini model to 3.5 or newer.",
            )

        return _verified(
            requirement,
            artifact,
            f"Primary Gemini model {artifact.observed_value} satisfies the 3.5+ requirement.",
        )

    if "google agent framework" in text or "google adk" in text:
        candidates = artifacts.get("google_adk", [])
        if candidates:
            return _verified(
                requirement,
                candidates[0],
                "Google ADK implementation evidence was found in the repository.",
            )
        return _missing(
            requirement,
            "No supported Google agent framework evidence was found.",
            "Add and use a supported Google agent framework, then rerun inspection.",
        )

    if "google cloud" in text and (
        "infrastructure" in text or "backend" in text or "cloud run" in text
    ):
        if deployment.reachable and deployment.google_cloud_runtime:
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.VERIFIED,
                severity=Severity.PASS,
                evidence=[
                    Evidence(
                        source="deployment",
                        path_or_url=deployment.url,
                        observed_value=f"HTTP {deployment.status_code} on *.run.app",
                    )
                ],
                reason="A reachable Google Cloud Run runtime was verified.",
                recommended_action=None,
            )

        repo_config = artifacts.get("cloud_run_config", [])
        evidence = (
            [_evidence_from_artifact(repo_config[0])]
            if repo_config
            else []
        )
        return Finding(
            requirement_id=requirement.requirement_id,
            requirement_text=requirement.requirement_text,
            requirement_type=requirement.requirement_type,
            status=EvidenceStatus.UNVERIFIED,
            severity=Severity.CRITICAL,
            evidence=evidence,
            reason=(
                "Google Cloud configuration may exist, but no reachable Google Cloud "
                "runtime was verified."
            ),
            recommended_action=(
                "Deploy the backend to Google Cloud Run and provide its *.run.app URL."
            ),
        )

    if "architecture diagram" in text:
        candidates = artifacts.get("architecture_artifact", [])
        if candidates:
            return _verified(
                requirement,
                candidates[0],
                "Production architecture evidence was found.",
            )
        return _missing(
            requirement,
            "The rules require an architecture diagram, but none was found.",
            "Add a production architecture diagram and reference it from the README.",
        )

    if "readme" in text and ("set up" in text or "setup" in text or "run" in text):
        candidates = artifacts.get("readme_setup", [])
        if candidates:
            return _verified(
                requirement,
                candidates[0],
                "README setup/run instructions were detected.",
            )
        return _missing(
            requirement,
            "README setup/run instructions were not detected.",
            "Add step-by-step local or cloud setup instructions to README.md.",
        )

    if "repository" in text or "github" in text or "gitlab" in text or "bitbucket" in text:
        candidates = artifacts.get("repository_visibility", [])
        if candidates:
            return _verified(
                requirement,
                candidates[0],
                "A public repository is available for inspection.",
            )

    if "working project" in text or "access to" in text:
        if deployment.reachable:
            return Finding(
                requirement_id=requirement.requirement_id,
                requirement_text=requirement.requirement_text,
                requirement_type=requirement.requirement_type,
                status=EvidenceStatus.VERIFIED,
                severity=Severity.PASS,
                evidence=[
                    Evidence(
                        source="deployment",
                        path_or_url=deployment.url,
                        observed_value=f"HTTP {deployment.status_code}",
                    )
                ],
                reason="A reachable project deployment was verified.",
                recommended_action=None,
            )
        return _manual(
            requirement,
            "Project-access requirements need a deployment or submission-form review.",
        )

    return _manual(
        requirement,
        "No bounded automated checker is available for this rule yet.",
    )
