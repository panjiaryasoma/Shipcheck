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


def _req(text: str) -> ExtractedRequirement:
    return ExtractedRequirement(
        requirement_id="REQ-001",
        source_section="rules",
        source_quote=text,
        requirement_text=text,
        requirement_type=RequirementType.CHECKABLE,
        evidence_expected=[],
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
