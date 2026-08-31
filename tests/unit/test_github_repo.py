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
        ".env.example": "PRIMARY_MODEL=gemini-3.7-flash\n",
        "Dockerfile": "FROM python:3.12-slim",
        "docs/architecture.md": (
            "# Architecture\nWeb UI -> FastAPI service -> Agent -> Firestore database"
        ),
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
    assert "google_agent_framework" in evidence_types
    assert "gemini_primary_model_config" in evidence_types
    assert "dependency_manifest" in evidence_types
    assert "cloud_run_config" in evidence_types
    assert "container_build" in evidence_types
    assert "cloud_run_evidence" not in evidence_types


def test_architecture_filename_alone_is_not_automatic_proof() -> None:
    artifacts = derive_artifacts(
        paths=["docs/architecture.md"],
        file_contents={"docs/architecture.md": "# Architecture\nTODO"},
    )
    evidence_types = {artifact.evidence_type for artifact in artifacts}

    assert "architecture_candidate" in evidence_types
    assert "architecture_artifact" not in evidence_types


def test_genai_sdk_is_detected_as_supported_google_framework() -> None:
    artifacts = derive_artifacts(
        paths=["package.json", "src/agent.ts"],
        file_contents={
            "package.json": '{"dependencies":{"@google/genai":"latest"}}',
            "src/agent.ts": 'import { GoogleGenAI } from "@google/genai";',
        },
    )
    evidence_types = {artifact.evidence_type for artifact in artifacts}

    assert "google_genai_sdk" in evidence_types
    assert "google_agent_framework" in evidence_types
