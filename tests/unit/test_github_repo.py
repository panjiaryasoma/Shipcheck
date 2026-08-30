import pytest

from app.tools.github_repo import (
    GitHubInspectionError,
    _raw_file_url,
    derive_artifacts,
    parse_github_repository_url,
)


def test_parse_public_github_repository_url() -> None:
    ref = parse_github_repository_url("https://github.com/example/demo")

    assert ref.owner == "example"
    assert ref.repo == "demo"


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/example/demo",
        "https://gitlab.com/example/demo",
        "https://github.com/example",
    ],
)
def test_invalid_repository_urls_are_rejected(url: str) -> None:
    with pytest.raises(GitHubInspectionError):
        parse_github_repository_url(url)


def test_raw_file_url_encodes_branch_without_leaking_path_structure() -> None:
    url = _raw_file_url(
        owner="example",
        repo="demo",
        branch="feature/rules",
        path="docs/My Architecture.md",
    )

    assert url == (
        "https://raw.githubusercontent.com/example/demo/"
        "feature%2Frules/docs/My%20Architecture.md"
    )


def test_derive_core_repository_artifacts() -> None:
    paths = [
        "README.md",
        "pyproject.toml",
        ".env.example",
        "Dockerfile",
        "docs/architecture.md",
        "app/agent.py",
    ]
    contents = {
        "README.md": "Setup: uv sync\nRun: uv run uvicorn app.main:app",
        "pyproject.toml": 'dependencies = ["google-adk"]',
        ".env.example": "SHIPCHECK_MODEL=gemini-3.7-flash\n",
        "Dockerfile": "FROM python:3.12-slim",
        "docs/architecture.md": "# Architecture",
        "app/agent.py": (
            "from google.adk.agents import Agent\n"
            "MODEL = 'gemini-3.7-flash'\n"
            "# deploy with gcloud run deploy"
        ),
    }

    artifacts = derive_artifacts(paths=paths, file_contents=contents)
    evidence_types = {artifact.evidence_type for artifact in artifacts}

    assert "repository_visibility" in evidence_types
    assert "architecture_artifact" in evidence_types
    assert "readme_setup" in evidence_types
    assert "google_adk" in evidence_types
    assert "gemini_primary_model_config" in evidence_types
    assert "cloud_run_config" in evidence_types
    assert "container_build" in evidence_types
    assert "cloud_run_evidence" not in evidence_types
