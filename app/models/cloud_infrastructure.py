"""Typed evidence for verified Google Cloud infrastructure operations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleCloudObservation:
    service: str
    verified: bool
    project_id: str | None = None
    resource: str | None = None
    detail: str | None = None
    scope: str = "inspector_runtime"
