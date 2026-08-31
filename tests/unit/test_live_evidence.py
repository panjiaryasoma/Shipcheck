from app.models.cloud_infrastructure import GoogleCloudObservation
from app.models.repository_inspection import (
    RepositoryArtifact,
    RepositoryInspectionOutput,
)
from app.models.rules_extraction import ExtractedRequirement
from app.models.schemas import EvidenceStatus, RequirementType, Severity
from app.tools.deployment import DeploymentObservation
from app.tools.live_evidence import map_live_requirement


def _repo(*artifacts: RepositoryArtifact) -> RepositoryInspectionOutput:
    return RepositoryInspectionOutput(
        repository_url="https://github.com/example/demo",
        owner="example",
        repository="demo",
        default_branch="main",
        public=True,
        artifacts=list(artifacts),
    )


def _req(
    text: str,
    requirement_type: RequirementType = RequirementType.CHECKABLE,
) -> ExtractedRequirement:
    return ExtractedRequirement(
        requirement_id="REQ-001",
        source_section="rules",
        source_quote=text,
        requirement_text=text,
        requirement_type=requirement_type,
        evidence_expected=[],
    )


def _firestore() -> GoogleCloudObservation:
    return GoogleCloudObservation(
        service="firestore",
        verified=True,
        project_id="demo-project",
        resource=(
            "projects/demo-project/databases/(default)/documents/"
            "shipcheck_inspections/live-123"
        ),
        detail="HTTP 200 document write to Cloud Firestore",
    )


def test_gemini_37_satisfies_35_plus_requirement() -> None:
    finding = map_live_requirement(
        _req("Projects must use Gemini 3.5 or newer."),
        _repo(
            RepositoryArtifact(
                evidence_type="gemini_primary_model_config",
                path=".env.example",
                observed_value="gemini-3.7-flash",
            )
        ),
        DeploymentObservation(False, None, None),
    )

    assert finding.status == EvidenceStatus.VERIFIED
    assert finding.severity == Severity.PASS


def test_missing_cloud_runtime_blocks_submission() -> None:
    finding = map_live_requirement(
        _req("Projects must use at least one Google Cloud infrastructure service."),
        _repo(
            RepositoryArtifact(
                evidence_type="container_build",
                path="Dockerfile",
                observed_value="Dockerfile present",
            )
        ),
        DeploymentObservation(False, None, None),
    )

    assert finding.status == EvidenceStatus.UNVERIFIED
    assert finding.severity == Severity.CRITICAL


def test_reachable_cloud_run_runtime_passes_cloud_requirement() -> None:
    finding = map_live_requirement(
        _req("Projects must use at least one Google Cloud infrastructure service."),
        _repo(),
        DeploymentObservation(
            True,
            "https://shipcheck-abc.a.run.app",
            200,
            google_cloud_runtime=True,
        ),
    )

    assert finding.status == EvidenceStatus.VERIFIED
    assert finding.severity == Severity.PASS


def test_verified_firestore_write_passes_infrastructure_requirement() -> None:
    finding = map_live_requirement(
        _req("Projects must use at least one Google Cloud infrastructure service."),
        _repo(),
        DeploymentObservation(False, None, None),
        cloud_infrastructure=_firestore(),
    )

    assert finding.status == EvidenceStatus.VERIFIED
    assert finding.severity == Severity.PASS
    assert finding.evidence[0].source == "google_cloud"
    observed = (finding.evidence[0].observed_value or "").lower()
    assert "firestore" in observed
    assert "self-inspection" in observed
    assert "scope=inspector_runtime" not in observed


def test_firestore_does_not_impersonate_cloud_hosted_backend() -> None:
    finding = map_live_requirement(
        _req("The backend must be running on Google Cloud."),
        _repo(),
        DeploymentObservation(False, None, None),
        cloud_infrastructure=_firestore(),
    )

    assert finding.status == EvidenceStatus.UNVERIFIED
    assert finding.severity == Severity.CRITICAL
    assert finding.evidence[0].source == "google_cloud"
    assert "backend/runtime" in finding.reason


def test_public_repository_makes_private_access_rule_not_applicable() -> None:
    finding = map_live_requirement(
        _req(
            "If the code repository is private, access must be granted to "
            "testing@devpost.com and cloudhackathons@google.com."
        ),
        _repo(
            RepositoryArtifact(
                evidence_type="repository_visibility",
                path="repository",
                observed_value="public repository",
            )
        ),
        DeploymentObservation(False, None, None),
    )

    assert finding.status == EvidenceStatus.NOT_APPLICABLE
    assert finding.severity == Severity.PASS
    assert "repository is public" in finding.reason.lower()


def test_submission_deadline_is_manual_even_if_extracted_as_informational() -> None:
    finding = map_live_requirement(
        _req(
            "Submissions must be submitted during the Submission Period, ending "
            "August 31, 2026 at 5:00 P.M. PT.",
            RequirementType.INFORMATIONAL,
        ),
        _repo(),
        DeploymentObservation(False, None, None),
    )

    assert finding.status == EvidenceStatus.MANUAL_REVIEW
    assert finding.severity == Severity.WARNING
    assert "timing" in finding.reason.lower() or "deadline" in finding.reason.lower()
