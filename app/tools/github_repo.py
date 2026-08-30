"""Bounded public GitHub repository inspection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote, urlparse

import httpx

from app.core.config import settings
from app.models.repository_inspection import RepositoryArtifact

GITHUB_API = "https://api.github.com"
RAW_GITHUB = "https://raw.githubusercontent.com"
MAX_TREE_ENTRIES = 2500
MAX_SELECTED_FILE_BYTES = 350_000

_SELECTED_FILENAMES = {
    "readme.md",
    "pyproject.toml",
    "requirements.txt",
    "uv.lock",
    ".env.example",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "cloudbuild.yaml",
    "cloudbuild.yml",
    "app.yaml",
}

_ARCHITECTURE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".md",
    ".mmd",
    ".mermaid",
}

_EXCLUDED_EVIDENCE_PREFIXES = (
    "fixtures/",
    "tests/",
    "reports/",
)

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
    "gcloud run deploy",
    ".run.app",
    "cloud run service",
    "cloud run deployment",
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
        raise GitHubInspectionError(
            "Only public HTTPS GitHub repository URLs are supported."
        )

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise GitHubInspectionError(
            "GitHub repository URL must include owner and repository."
        )

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
        "User-Agent": "Shipcheck/0.4.1",
    }

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


def _raw_file_url(*, owner: str, repo: str, branch: str, path: str) -> str:
    encoded_branch = quote(branch, safe="")
    encoded_path = quote(path, safe="/")
    return f"{RAW_GITHUB}/{owner}/{repo}/{encoded_branch}/{encoded_path}"


async def _fetch_selected_file(
    client: httpx.AsyncClient,
    *,
    owner: str,
    repo: str,
    path: str,
    branch: str,
) -> str | None:
    """Fetch a selected public file without consuming GitHub REST core quota.

    The authenticated REST client is deliberately not reused here so an optional
    GitHub token is never forwarded to raw.githubusercontent.com.
    """

    raw_url = _raw_file_url(
        owner=owner,
        repo=repo,
        branch=branch,
        path=path,
    )

    async with client.stream("GET", raw_url) as response:
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise GitHubInspectionError(
                f"GitHub raw file host returned HTTP {response.status_code}."
            )

        payload = bytearray()
        async for chunk in response.aiter_bytes():
            payload.extend(chunk)
            if len(payload) > MAX_SELECTED_FILE_BYTES:
                return None

    return bytes(payload).decode("utf-8", errors="replace")


def _is_excluded_evidence_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return normalized.startswith(_EXCLUDED_EVIDENCE_PREFIXES)


def _is_architecture_path(path: str) -> bool:
    if _is_excluded_evidence_path(path):
        return False

    lowered = path.lower()
    name = lowered.rsplit("/", 1)[-1]

    if "architecture" not in name and "architecture" not in lowered:
        return False

    suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    return suffix in _ARCHITECTURE_EXTENSIONS


def _production_file_contents(
    file_contents: dict[str, str],
) -> dict[str, str]:
    return {
        path: content
        for path, content in file_contents.items()
        if not _is_excluded_evidence_path(path)
    }


def _extract_primary_model(file_contents: dict[str, str]) -> tuple[str, str] | None:
    for path, content in file_contents.items():
        if path.lower().endswith(".env.example"):
            match = re.search(
                r"(?mi)^\s*SHIPCHECK_MODEL\s*=\s*([A-Za-z0-9_.-]+)\s*$",
                content,
            )
            if match:
                return path, match.group(1)

    return None


def derive_artifacts(
    *,
    paths: list[str],
    file_contents: dict[str, str],
) -> list[RepositoryArtifact]:
    artifacts: list[RepositoryArtifact] = []

    production_paths = [
        path for path in paths if not _is_excluded_evidence_path(path)
    ]
    production_contents = _production_file_contents(file_contents)

    artifacts.append(
        RepositoryArtifact(
            evidence_type="repository_visibility",
            path="repository",
            observed_value="public repository",
        )
    )

    for path in production_paths:
        if _is_architecture_path(path):
            artifacts.append(
                RepositoryArtifact(
                    evidence_type="architecture_artifact",
                    path=path,
                    observed_value="architecture artifact present",
                )
            )

    lowered_paths = {path.lower(): path for path in production_paths}
    readme_path = next(
        (
            original
            for lower, original in lowered_paths.items()
            if lower == "readme.md"
        ),
        None,
    )

    if readme_path and readme_path in production_contents:
        readme = production_contents[readme_path].lower()
        setup_hits = [marker for marker in _SETUP_MARKERS if marker in readme]
        if setup_hits:
            artifacts.append(
                RepositoryArtifact(
                    evidence_type="readme_setup",
                    path=readme_path,
                    observed_value=", ".join(setup_hits[:5]),
                )
            )

    combined_text = "\n".join(production_contents.values()).lower()

    adk_hits = [marker for marker in _ADK_MARKERS if marker in combined_text]
    if adk_hits:
        path = next(
            (
                file_path
                for file_path, content in production_contents.items()
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

    primary_model = _extract_primary_model(production_contents)
    if primary_model:
        path, model_name = primary_model
        artifacts.append(
            RepositoryArtifact(
                evidence_type="gemini_primary_model_config",
                path=path,
                observed_value=model_name,
            )
        )
    else:
        gemini_hits = [
            marker for marker in _GEMINI_MARKERS if marker in combined_text
        ]
        if gemini_hits:
            path = next(
                (
                    file_path
                    for file_path, content in production_contents.items()
                    if any(marker in content.lower() for marker in _GEMINI_MARKERS)
                ),
                "repository",
            )
            artifacts.append(
                RepositoryArtifact(
                    evidence_type="gemini_model_reference",
                    path=path,
                    observed_value=", ".join(gemini_hits[:5]),
                )
            )

    cloud_hits = [
        marker for marker in _CLOUD_RUN_MARKERS if marker in combined_text
    ]
    if cloud_hits:
        path = next(
            (
                file_path
                for file_path, content in production_contents.items()
                if any(marker in content.lower() for marker in _CLOUD_RUN_MARKERS)
            ),
            "repository",
        )
        artifacts.append(
            RepositoryArtifact(
                evidence_type="cloud_run_config",
                path=path,
                observed_value=", ".join(cloud_hits[:4]),
            )
        )

    dockerfile = next(
        (
            path
            for path in production_paths
            if path.lower().rsplit("/", 1)[-1] == "dockerfile"
        ),
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

    # GitHub REST is used only for repository metadata and one recursive tree.
    # File bodies are fetched from the public raw host using a separate client.
    async with httpx.AsyncClient(
        timeout=timeout,
        headers=_headers(),
        follow_redirects=False,
    ) as api_client:
        repo_payload = await _get_json(api_client, f"/repos/{ref.owner}/{ref.repo}")

        if not isinstance(repo_payload, dict):
            raise GitHubInspectionError("Unexpected GitHub repository response.")

        if bool(repo_payload.get("private")):
            raise GitHubInspectionError(
                "Private GitHub repositories are not supported in v0.4.1."
            )

        default_branch = str(repo_payload.get("default_branch") or "main")

        tree_payload = await _get_json(
            api_client,
            f"/repos/{ref.owner}/{ref.repo}/git/trees/{default_branch}?recursive=1",
        )

    if not isinstance(tree_payload, dict):
        raise GitHubInspectionError("Unexpected GitHub tree response.")

    if tree_payload.get("truncated"):
        raise GitHubInspectionError(
            "Repository tree is too large for bounded v0.4.1 inspection."
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

        if (
            lowered_name in _SELECTED_FILENAMES
            or _is_architecture_path(path)
        ):
            selected_paths.append(path)
        elif lowered_name.endswith(".py") and len(selected_paths) < 45:
            selected_paths.append(path)

    selected_paths = list(dict.fromkeys(selected_paths))[:60]

    file_contents: dict[str, str] = {}
    async with httpx.AsyncClient(
        timeout=timeout,
        headers={"User-Agent": "Shipcheck/0.4.1"},
        follow_redirects=False,
    ) as raw_client:
        for path in selected_paths:
            lower = path.lower()

            if lower.endswith((".png", ".jpg", ".jpeg")):
                continue

            content = await _fetch_selected_file(
                raw_client,
                owner=ref.owner,
                repo=ref.repo,
                path=path,
                branch=default_branch,
            )
            if content is not None:
                file_contents[path] = content

    artifacts = derive_artifacts(
        paths=paths,
        file_contents=file_contents,
    )

    return {
        "repository_url": f"https://github.com/{ref.owner}/{ref.repo}",
        "owner": ref.owner,
        "repository": ref.repo,
        "default_branch": default_branch,
        "public": True,
        "artifacts": [
            artifact.model_dump(mode="json")
            for artifact in artifacts
        ],
        "inspected_files": sorted(file_contents),
        "notes": [
            f"Repository tree contained {len(paths)} bounded file entries.",
            f"Inspected {len(file_contents)} selected text files.",
            "Fixture/test paths are excluded from production evidence.",
            "Container configuration is not treated as proof of live Cloud Run deployment.",
            "GitHub REST is used only for metadata/tree; file bodies use the public raw host.",
        ],
    }
