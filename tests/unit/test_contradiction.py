from app.models.repository_inspection import (
    RepositoryArtifact,
    RepositoryInspectionOutput,
)
from app.models.schemas import EvidenceStatus, Severity
from app.tools.contradiction import detect_claim_contradictions
from app.tools.deployment import DeploymentObservation


def _repository(*artifacts: RepositoryArtifact) -> RepositoryInspectionOutput:
    return RepositoryInspectionOutput(
        repository_url="https://github.com/example/demo",
        owner="example",
        repository="demo",
        default_branch="main",
        public=True,
        artifacts=list(artifacts),
    )


def test_mismatched_gemini_claim_is_critical_contradiction() -> None:
    findings = detect_claim_contradictions(
        ["Uses Gemini 3.5 Flash as the primary model."],
        _repository(
            RepositoryArtifact(
                evidence_type="gemini_primary_model_config",
                path=".env.example",
                observed_value="gemini-3.7-flash",
            )
        ),
        DeploymentObservation(False, None, None),
    )

    assert len(findings) == 1
    assert findings[0].status == EvidenceStatus.CONTRADICTED
    assert findings[0].severity == Severity.CRITICAL


def test_missing_adk_evidence_is_unverified_not_contradicted() -> None:
    findings = detect_claim_contradictions(
        ["The project uses Google ADK."],
        _repository(),
        DeploymentObservation(False, None, None),
    )

    assert len(findings) == 1
    assert findings[0].status == EvidenceStatus.UNVERIFIED
    assert findings[0].severity == Severity.HIGH


def test_missing_cloud_run_runtime_is_unverified_not_contradicted() -> None:
    findings = detect_claim_contradictions(
        ["The backend runs on Google Cloud Run."],
        _repository(),
        DeploymentObservation(
            True,
            "https://example.vercel.app",
            200,
            google_cloud_runtime=False,
        ),
    )

    assert len(findings) == 1
    assert findings[0].status == EvidenceStatus.UNVERIFIED
    assert findings[0].severity == Severity.HIGH
