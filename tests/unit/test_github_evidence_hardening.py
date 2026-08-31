from app.tools.github_repo import derive_artifacts


def _types(artifacts):
    return {artifact.evidence_type for artifact in artifacts}


def test_fixture_architecture_does_not_count_as_production_evidence() -> None:
    paths = [
        "README.md",
        "fixtures/repos/compliant/docs/architecture.md",
    ]
    contents = {
        "README.md": "Setup: uv sync",
        "fixtures/repos/compliant/docs/architecture.md": "# Fake fixture architecture",
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)

    architecture = [
        artifact
        for artifact in artifacts
        if artifact.evidence_type == "architecture_artifact"
    ]
    assert architecture == []


def test_thin_production_architecture_is_candidate_not_verified_artifact() -> None:
    paths = ["docs/ARCHITECTURE.md"]
    contents = {"docs/ARCHITECTURE.md": "# Architecture"}

    artifacts = derive_artifacts(paths=paths, file_contents=contents)
    evidence_types = _types(artifacts)

    assert "architecture_candidate" in evidence_types
    assert "architecture_artifact" not in evidence_types


def test_production_architecture_with_topology_counts_as_verified_artifact() -> None:
    paths = ["docs/ARCHITECTURE.md"]
    contents = {
        "docs/ARCHITECTURE.md": (
            "# Architecture\n"
            "Web UI -> FastAPI service -> Agent -> Firestore database"
        )
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)

    assert "architecture_artifact" in _types(artifacts)


def test_dockerfile_is_not_live_cloud_run_proof() -> None:
    paths = ["Dockerfile"]
    contents = {
        "Dockerfile": (
            "FROM python:3.12-slim\n"
            'CMD ["uvicorn", "app.main:app"]'
        )
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)
    evidence_types = _types(artifacts)

    assert "container_build" in evidence_types
    assert "cloud_run_config" not in evidence_types
    assert "cloud_run_evidence" not in evidence_types


def test_explicit_cloud_run_config_is_config_not_runtime_proof() -> None:
    paths = ["README.md", "Dockerfile"]
    contents = {
        "README.md": "Deploy with: gcloud run deploy shipcheck",
        "Dockerfile": "FROM python:3.12-slim",
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)
    evidence_types = _types(artifacts)

    assert "cloud_run_config" in evidence_types
    assert "cloud_run_evidence" not in evidence_types


def test_primary_model_prefers_env_example() -> None:
    paths = [".env.example", "app/agent/root_agent.py"]
    contents = {
        ".env.example": (
            "SHIPCHECK_MODEL=gemini-3.7-flash\n"
            "SHIPCHECK_FALLBACK_MODELS=gemini-3.6-flash,gemini-3.5-flash\n"
        ),
        "app/agent/root_agent.py": "from google import genai",
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)

    primary = next(
        artifact
        for artifact in artifacts
        if artifact.evidence_type == "gemini_primary_model_config"
    )

    assert primary.path == ".env.example"
    assert primary.observed_value == "gemini-3.7-flash"
