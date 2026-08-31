from app.models.repository_inspection import RepositoryArtifact, RepositoryInspectionOutput
from app.models.schemas import EvidenceStatus
from app.tools.reproduction import inspect_bounded_reproducibility


def _repository(*artifacts: RepositoryArtifact) -> RepositoryInspectionOutput:
    return RepositoryInspectionOutput(
        repository_url="https://github.com/example/demo",
        owner="example",
        repository="demo",
        default_branch="main",
        public=True,
        artifacts=list(artifacts),
    )


def test_static_reproduction_checks_verify_setup_and_manifest_without_execution() -> None:
    observations = inspect_bounded_reproducibility(
        _repository(
            RepositoryArtifact(
                evidence_type="readme_setup",
                path="README.md",
                observed_value="uv sync, uv run",
            ),
            RepositoryArtifact(
                evidence_type="dependency_manifest",
                path="pyproject.toml",
                observed_value="Dependency manifest present",
            ),
        )
    )

    assert observations[0].status == EvidenceStatus.VERIFIED
    assert observations[1].status == EvidenceStatus.VERIFIED
    assert observations[2].status == EvidenceStatus.MANUAL_REVIEW
    assert "not executed" in observations[2].detail


def test_missing_static_reproduction_evidence_stays_unverified() -> None:
    observations = inspect_bounded_reproducibility(_repository())

    assert observations[0].status == EvidenceStatus.UNVERIFIED
    assert observations[1].status == EvidenceStatus.UNVERIFIED
