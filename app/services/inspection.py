"""Fixture and live end-to-end inspection orchestration."""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from app.models.cloud_infrastructure import GoogleCloudObservation
from app.models.live_inspection import InspectionSummary, LiveInspectionReport
from app.models.repository_inspection import RepositoryInspectionOutput
from app.models.rules_extraction import RulesExtractionOutput
from app.models.schemas import EvidenceStatus, InspectionReport, InspectionRequest, Severity
from app.services.live_repository import inspect_live_repository
from app.services.live_rules import extract_requirements_with_adk
from app.storage.firestore import (
    persist_live_inspection,
    persist_live_inspection_with_evidence,
)
from app.tools.contradiction import detect_claim_contradictions
from app.tools.deployment import (
    DeploymentObservation,
    verify_fixture_deployment,
    verify_live_deployment,
)
from app.tools.evidence import map_fixture_evidence
from app.tools.live_evidence import map_live_requirement
from app.tools.repository import inspect_fixture_repository
from app.tools.risk import derive_final_disposition
from app.tools.rules import extract_fixture_requirements


def inspect_fixture(
    *,
    rules_path: str | Path,
    repository_path: str | Path,
) -> InspectionReport:
    requirements = extract_fixture_requirements(rules_path)
    repo_observations = inspect_fixture_repository(repository_path)
    deployment = verify_fixture_deployment(repository_path)

    findings = [
        map_fixture_evidence(requirement, repo_observations, deployment)
        for requirement in requirements
    ]

    return InspectionReport(
        inspection_id=f"fixture-{uuid4().hex[:10]}",
        final_disposition=derive_final_disposition(findings),
        findings=findings,
    )


def _summarize(findings) -> InspectionSummary:
    return InspectionSummary(
        critical=sum(f.severity == Severity.CRITICAL for f in findings),
        high=sum(f.severity == Severity.HIGH for f in findings),
        warning=sum(f.severity == Severity.WARNING for f in findings),
        passed=sum(f.severity == Severity.PASS for f in findings),
        manual_review=sum(f.status == EvidenceStatus.MANUAL_REVIEW for f in findings),
    )


def _live_findings(
    *,
    rules: RulesExtractionOutput,
    repository: RepositoryInspectionOutput,
    deployment: DeploymentObservation,
    submission_claims: list[str],
    cloud_infrastructure: GoogleCloudObservation | None = None,
):
    findings = [
        map_live_requirement(
            requirement,
            repository,
            deployment,
            cloud_infrastructure=cloud_infrastructure,
        )
        for requirement in rules.requirements
    ]
    findings.extend(
        detect_claim_contradictions(
            submission_claims,
            repository,
            deployment,
        )
    )
    return findings


async def inspect_live_submission(
    request: InspectionRequest,
) -> LiveInspectionReport:
    rules_task = extract_requirements_with_adk(str(request.rules_url))
    repo_task = inspect_live_repository(str(request.repository_url))

    rules, repository = await asyncio.gather(rules_task, repo_task)
    deployment = await verify_live_deployment(
        str(request.deployment_url) if request.deployment_url else None
    )

    findings = _live_findings(
        rules=rules,
        repository=repository,
        deployment=deployment,
        submission_claims=request.submission_claims,
    )

    report = LiveInspectionReport(
        inspection_id=f"live-{uuid4().hex[:10]}",
        rules_source=rules.source_url,
        repository_url=repository.repository_url,
        deployment_url=deployment.url,
        model_used=rules.model_used,
        fallback_used=rules.fallback_used,
        final_disposition=derive_final_disposition(findings),
        summary=_summarize(findings),
        findings=findings,
        notes=[
            *rules.notes,
            *repository.notes,
            "READY means ready within the evidence Shipcheck could inspect.",
        ],
    )

    cloud_observation = await persist_live_inspection_with_evidence(report)
    if cloud_observation:
        findings = _live_findings(
            rules=rules,
            repository=repository,
            deployment=deployment,
            submission_claims=request.submission_claims,
            cloud_infrastructure=cloud_observation,
        )
        report.findings = findings
        report.final_disposition = derive_final_disposition(findings)
        report.summary = _summarize(findings)
        report.notes.append(
            "Persisted this live inspection as an audit record in Google Cloud Firestore."
        )

        # Rewrite the same document so the stored audit record contains the final
        # verdict after the successful Firestore operation becomes inspectable evidence.
        await persist_live_inspection(report)

    return report
