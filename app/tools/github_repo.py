"""Bounded public GitHub repository inspection."""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.models.repository_inspection import RepositoryArtifact

GITHUB_API = "https://api.github.com"
MAX_TREE_ENTRIES = 2500
MAX_SELECTED_FILE_BYTES = 350_000

_SELECTED_FILENAMES = {
    "readme.md",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "cloudbuild.yaml",
    "cloudbuild.yml",
    "app.yaml",
}

_ARCHITECTURE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".md", ".mmd", ".mermaid"}

_SETUP_MARKERS = (
    "uv sync",
    "pip install",
    "python -m",
    "uv run",
    "docker build",
    "docker compose",
    "gcloud run deploy",
)

_ADK_MARKERS = (
    "google-adk",
    "from google.adk",
    "import google.adk",
)

_GEMINI_MARKERS = (
    "gemini-3.7",
    "gemini-3.6",
    "gemini-3.5",
    "google.genai",
    "from google import genai",
)

_CLOUD_RUN_MARKERS = (
    "cloud run",
    "gcloud run",
    "run.app",
)


class GitHubInspectionError(RuntimeError):
    """Raised when a public GitHub repository cannot be inspected safely."""


@dataclass(frozen=True)
class GitHubRepoRef:
    owner: str
    repo: str


def parse_github_repository_url(url: str) -> GitHubRepoRef:
    parsed = urlparse(url)

    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
        raise GitHubInspectionError("Only public HTTPS GitHub repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise GitHubInspectionError("GitHub repository URL must include owner and repository.")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    safe = re.compile(r"^[A-Za-z0-9_.-]+$")
    if not safe.fullmatch(owner) or not safe.fullmatch(repo):
        raise GitHubInspectionError("GitHub owner or repository name is invalid.")

    return GitHubRepoRef(owner=owner, repo=repo)


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Shipcheck/0.3",
    }

    # Optional. Public repositories work without a token, but a token raises the
    # GitHub API rate limit. It is never returned in output.
    token = getattr(settings, "github_token", None)
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


async def _get_json(client: httpx.AsyncClient, path: str) -> dict | list:
    response = await client.get(f"{GITHUB_API}{path}")

    if response.status_code == 404:
        raise GitHubInspectionError("GitHub repository or artifact was not found.")
    if response.status_code == 403 and "rate limit" in response.text.lower():
        raise GitHubInspectionError(
            "GitHub API rate limit reached. Configure GITHUB_TOKEN or retry later."
        )
    if response.status_code >= 400:
        raise GitHubInspectionError(
            f"GitHub API returned HTTP {response.status_code}."
        )

    return response.json()


async def _fetch_selected_file(
    client: httpx.AsyncClient,
    *,
    owner: str,
    repo: str,
    path: str,
    branch: str,
) -> str | None:
    payload = await _get_json(
        client,
        f"/repos/{owner}/{repo}/contents/{path}?ref={branch}",
    )

    if not isinstance(payload, dict):
        return None

    size = int(payload.get("size") or 0)
    if size > MAX_SELECTED_FILE_BYTES:
        return None

    content = payload.get("content")
    encoding = payload.get("encoding")

    if not content or encoding != "base64":
        return None

    try:
        raw = base64.b64decode(content, validate=False)
    except ValueError:
        return None

    if len(raw) > MAX_SELECTED_FILE_BYTES:
        return None

    return raw.decode("utf-8", errors="replace")


def _is_architecture_path(path: str) -> bool:
    lowered = path.lower()
    name = lowered.rsplit("/", 1)[-1]

    if "architecture" not in name and "architecture" not in lowered:
        return False

    suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    return suffix in _ARCHITECTURE_EXTENSIONS


def derive_artifacts(
    *,
    paths: list[str],
    file_contents: dict[str, str],
) -> list[RepositoryArtifact]:
    artifacts: list[RepositoryArtifact] = []

    lowered_paths = {path.lower(): path for path in paths}

    for path in paths:
        if _is_architecture_path(path):
            artifacts.append(
                RepositoryArtifact(
                    evidence_type="architecture_artifact",
                    path=path,
                    observed_value="architecture artifact present",
                )
            )

    readme_path = next(
        (original for lower, original in lowered_paths.items() if lower.endswith("readme.md")),
        None,
    )
    if readme_path and readme_path in file_contents:
        readme = file_contents[readme_path].lower()
        setup_hits = [marker for marker in _SETUP_MARKERS if marker in readme]
        if setup_hits:
            artifacts.append(
                RepositoryArtifact(
                    evidence_type="readme_setup",
                    path=readme_path,
                    observed_value=", ".join(setup_hits[:5]),
                )
            )

    combined_text = "\n".join(file_contents.values()).lower()

    adk_hits = [marker for marker in _ADK_MARKERS if marker in combined_text]
    if adk_hits:
        path = next(
            (
                file_path
                for file_path, content in file_contents.items()
                if any(marker in content.lower() for marker in _ADK_MARKERS)
            ),
            "repository",
        )
        artifacts.append(
            RepositoryArtifact(
                evidence_type="google_adk",
                path=path,
                observed_value=", ".join(adk_hits[:4]),
            )
        )

    gemini_hits = [marker for marker in _GEMINI_MARKERS if marker in combined_text]
    if gemini_hits:
        path = next(
            (
                file_path
                for file_path, content in file_contents.items()
                if any(marker in content.lower() for marker in _GEMINI_MARKERS)
            ),
            "repository",
        )
        artifacts.append(
            RepositoryArtifact(
                evidence_type="gemini_model",
                path=path,
                observed_value=", ".join(gemini_hits[:5]),
            )
        )

    cloud_hits = [marker for marker in _CLOUD_RUN_MARKERS if marker in combined_text]
    cloud_paths = [
        path
        for path in paths
        if path.lower().endswith(("dockerfile", "cloudbuild.yaml", "cloudbuild.yml"))
    ]
    if cloud_hits or cloud_paths:
        artifacts.append(
            RepositoryArtifact(
                evidence_type="cloud_run_evidence",
                path=(cloud_paths[0] if cloud_paths else "repository"),
                observed_value=", ".join(cloud_hits[:4]) if cloud_hits else "deployment config present",
            )
        )

    dockerfile = next(
        (path for path in paths if path.lower().endswith("dockerfile")),
        None,
    )
    if dockerfile:
        artifacts.append(
            RepositoryArtifact(
                evidence_type="container_build",
                path=dockerfile,
                observed_value="Dockerfile present",
            )
        )

    return artifacts


async def inspect_public_github_repository(url: str) -> dict:
    ref = parse_github_repository_url(url)

    timeout = httpx.Timeout(
        float(settings.shipcheck_request_timeout_seconds),
        connect=min(10.0, float(settings.shipcheck_request_timeout_seconds)),
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        headers=_headers(),
        follow_redirects=False,
    ) as client:
        repo_payload = await _get_json(client, f"/repos/{ref.owner}/{ref.repo}")

        if not isinstance(repo_payload, dict):
            raise GitHubInspectionError("Unexpected GitHub repository response.")

        if bool(repo_payload.get("private")):
            raise GitHubInspectionError("Private GitHub repositories are not supported in v0.3.")

        default_branch = str(repo_payload.get("default_branch") or "main")

        tree_payload = await _get_json(
            client,
            f"/repos/{ref.owner}/{ref.repo}/git/trees/{default_branch}?recursive=1",
        )

        if not isinstance(tree_payload, dict):
            raise GitHubInspectionError("Unexpected GitHub tree response.")

        if tree_payload.get("truncated"):
            raise GitHubInspectionError(
                "Repository tree is too large for bounded v0.3 inspection."
            )

        tree = tree_payload.get("tree") or []
        paths = [
            str(item.get("path"))
            for item in tree[:MAX_TREE_ENTRIES]
            if item.get("type") == "blob" and item.get("path")
        ]

        selected_paths: list[str] = []
        for path in paths:
            lowered_name = path.rsplit("/", 1)[-1].lower()
            if lowered_name in _SELECTED_FILENAMES or _is_architecture_path(path) or lowered_name.endswith(".py") and len(selected_paths) < 45:
                selected_paths.append(path)

        selected_paths = list(dict.fromkeys(selected_paths))[:60]

        file_contents: dict[str, str] = {}
        for path in selected_paths:
            lower = path.lower()
            # Images can prove presence as architecture evidence but are not decoded as text.
            if lower.endswith((".png", ".jpg", ".jpeg")):
                continue

            content = await _fetch_selected_file(
                client,
                owner=ref.owner,
                repo=ref.repo,
                path=path,
                branch=default_branch,
            )
            if content is not None:
                file_contents[path] = content

    artifacts = derive_artifacts(paths=paths, file_contents=file_contents)

    return {
        "repository_url": f"https://github.com/{ref.owner}/{ref.repo}",
        "owner": ref.owner,
        "repository": ref.repo,
        "default_branch": default_branch,
        "public": True,
        "artifacts": [artifact.model_dump(mode="json") for artifact in artifacts],
        "inspected_files": sorted(file_contents),
        "notes": [
            f"Repository tree contained {len(paths)} bounded file entries.",
            f"Inspected {len(file_contents)} selected text files.",
        ],
    }
