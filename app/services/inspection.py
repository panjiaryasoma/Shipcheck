"""Deterministic first vertical slice for Shipcheck."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from app.models.schemas import InspectionReport
from app.tools.deployment import verify_fixture_deployment
from app.tools.evidence import map_fixture_evidence
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
