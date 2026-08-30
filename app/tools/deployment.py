"""Fixture and live deployment verification."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.tools.live_rules import _validate_public_url


@dataclass(frozen=True)
class DeploymentObservation:
    reachable: bool
    url: str | None
    status_code: int | None
    google_cloud_runtime: bool = False


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
    )


async def verify_live_deployment(url: str | None) -> DeploymentObservation:
    if not url:
        return DeploymentObservation(reachable=False, url=None, status_code=None)

    await _validate_public_url(url)

    timeout = httpx.Timeout(
        float(settings.shipcheck_request_timeout_seconds),
        connect=min(10.0, float(settings.shipcheck_request_timeout_seconds)),
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": "Shipcheck/0.4"},
    ) as client:
        response = await client.get(url)

    final_url = str(response.url)
    hostname = (urlparse(final_url).hostname or "").lower()

    return DeploymentObservation(
        reachable=response.status_code < 500,
        url=final_url,
        status_code=response.status_code,
        google_cloud_runtime=hostname.endswith(".run.app"),
    )
