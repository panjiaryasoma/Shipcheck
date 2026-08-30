"""Fixture deployment verifier.

The deterministic fixture uses a tiny JSON artifact instead of performing network I/O.
Live HTTP verification is a later vertical slice.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DeploymentObservation:
    reachable: bool
    url: str | None
    status_code: int | None


def verify_fixture_deployment(repo_path: str | Path) -> DeploymentObservation:
    fixture_path = Path(repo_path) / "fixture_deployment.json"

    if not fixture_path.exists():
        return DeploymentObservation(reachable=False, url=None, status_code=None)

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    return DeploymentObservation(
        reachable=bool(payload.get("reachable", False)),
        url=payload.get("url"),
        status_code=payload.get("status_code"),
    )
