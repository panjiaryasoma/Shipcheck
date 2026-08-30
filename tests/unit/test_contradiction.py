from app.models.repository_inspection import (
    RepositoryArtifact,
    RepositoryInspectionOutput,
)
from app.models.schemas import EvidenceStatus, Severity
from app.tools.contradiction import detect_claim_contradictions
from app.tools.deployment import DeploymentObservation


def test_mismatched_gemini_claim_is_critical_contradiction() -> None:
    repository = RepositoryInspectionOutput(
        repository_url="https://github.com/example/demo",
        owner="example",
        repository="demo",
        default_branch="main",
        public=True,
        artifacts=[
            RepositoryArtifact(
                evidence_type="gemini_primary_model_config",
                path=".env.example",
                observed_value="gemini-3.7-flash",
            )
        ],
    )

    findings = detect_claim_contradictions(
        ["Uses Gemini 3.5 Flash as the primary model."],
        repository,
        DeploymentObservation(False, None, None),
    )

    assert len(findings) == 1
    assert findings[0].status == EvidenceStatus.CONTRADICTED
    assert findings[0].severity == Severity.CRITICAL
