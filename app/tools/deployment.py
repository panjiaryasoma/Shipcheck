"""Fixture and live deployment verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

from app.core.config import settings
from app.core.version import SHIPCHECK_USER_AGENT
from app.tools.live_rules import _validate_public_url

MAX_DEPLOYMENT_REDIRECTS = 3
MAX_RESPONSE_SAMPLE_CHARS = 800


class DeploymentVerificationError(RuntimeError):
    """Raised when a deployment cannot be verified safely."""


@dataclass(frozen=True)
class DeploymentObservation:
    reachable: bool
    url: str | None
    status_code: int | None
    google_cloud_runtime: bool = False
    observed_response: str | None = None


def verify_fixture_deployment(repo_path: str | Path) -> DeploymentObservation:
    fixture_path = Path(repo_path) / "fixture_deployment.json"

    if not fixture_path.exists():
        return DeploymentObservation(reachable=False, url=None, status_code=None)

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    return DeploymentObservation(
        reachable=bool(payload.get("reachable", False)),
        url=payload.get("url"),
        status_code=payload.get("status_code"),
        google_cloud_runtime=bool(payload.get("google_cloud_runtime", False)),
        observed_response=payload.get("observed_response"),
    )


def _response_sample(response: httpx.Response) -> str | None:
    content_type = response.headers.get("content-type", "").lower()
    if not any(kind in content_type for kind in ("text/", "json", "xml", "javascript")):
        return None

    sample = " ".join(response.text[:MAX_RESPONSE_SAMPLE_CHARS].split())
    return sample or None


async def verify_live_deployment(url: str | None) -> DeploymentObservation:
    if not url:
        return DeploymentObservation(reachable=False, url=None, status_code=None)

    current_url = url
    timeout = httpx.Timeout(
        float(settings.shipcheck_request_timeout_seconds),
        connect=min(10.0, float(settings.shipcheck_request_timeout_seconds)),
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        headers={"User-Agent": SHIPCHECK_USER_AGENT},
    ) as client:
        for redirect_index in range(MAX_DEPLOYMENT_REDIRECTS + 1):
            await _validate_public_url(current_url)
            response = await client.get(current_url)

            if 300 <= response.status_code < 400:
                location = response.headers.get("location")
                if not location:
                    return DeploymentObservation(
                        reachable=False,
                        url=str(response.url),
                        status_code=response.status_code,
                        observed_response=_response_sample(response),
                    )
                if redirect_index >= MAX_DEPLOYMENT_REDIRECTS:
                    raise DeploymentVerificationError(
                        "Deployment exceeded Shipcheck's redirect limit."
                    )
                current_url = urljoin(current_url, location)
                continue

            final_url = str(response.url)
            hostname = (urlparse(final_url).hostname or "").lower()
            return DeploymentObservation(
                reachable=200 <= response.status_code < 300,
                url=final_url,
                status_code=response.status_code,
                google_cloud_runtime=hostname.endswith(".run.app"),
                observed_response=_response_sample(response),
            )

    raise DeploymentVerificationError("Deployment could not be verified.")
