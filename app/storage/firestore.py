"""Optional Firestore persistence for live inspection audit records."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from urllib.parse import quote

import google.auth
import httpx
from google.auth.transport.requests import Request

from app.core.config import settings
from app.models.live_inspection import LiveInspectionReport

_FIRESTORE_SCOPE = "https://www.googleapis.com/auth/datastore"


class FirestorePersistenceError(RuntimeError):
    """Raised when enabled Firestore persistence cannot complete safely."""


def _access_token_and_project() -> tuple[str, str]:
    credentials, discovered_project = google.auth.default(scopes=[_FIRESTORE_SCOPE])

    if not credentials.valid:
        credentials.refresh(Request())

    token = credentials.token
    project = settings.google_cloud_project or discovered_project

    if not token:
        raise FirestorePersistenceError("Application Default Credentials did not yield a token.")
    if not project:
        raise FirestorePersistenceError(
            "GOOGLE_CLOUD_PROJECT is required when Firestore persistence is enabled."
        )

    return token, project


def _firestore_fields(report: LiveInspectionReport) -> dict[str, dict]:
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "inspection_id": {"stringValue": report.inspection_id},
        "rules_source": {"stringValue": report.rules_source},
        "repository_url": {"stringValue": report.repository_url},
        "deployment_url": {"stringValue": report.deployment_url or ""},
        "model_used": {"stringValue": report.model_used or ""},
        "fallback_used": {"booleanValue": report.fallback_used},
        "final_disposition": {"stringValue": report.final_disposition.value},
        "summary_json": {"stringValue": report.summary.model_dump_json()},
        "report_json": {"stringValue": report.model_dump_json()},
        "created_at": {"timestampValue": created_at},
    }


async def persist_live_inspection(report: LiveInspectionReport) -> bool:
    """Persist one live report when Firestore is explicitly enabled.

    Returns False without touching Google Cloud when persistence is disabled.
    When enabled, failures are raised rather than silently claiming persistence.
    """

    if not settings.shipcheck_firestore_enabled:
        return False

    token, project = await asyncio.to_thread(_access_token_and_project)
    database = quote(settings.shipcheck_firestore_database, safe="()")
    collection = quote(settings.shipcheck_firestore_collection, safe="")
    document_id = quote(report.inspection_id, safe="")
    project_id = quote(project, safe="")

    url = (
        "https://firestore.googleapis.com/v1/"
        f"projects/{project_id}/databases/{database}/documents/{collection}/{document_id}"
    )

    timeout = httpx.Timeout(
        float(settings.shipcheck_request_timeout_seconds),
        connect=min(10.0, float(settings.shipcheck_request_timeout_seconds)),
    )

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        response = await client.patch(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={"fields": _firestore_fields(report)},
        )

    if response.status_code >= 400:
        detail = response.text[:500]
        raise FirestorePersistenceError(
            f"Firestore returned HTTP {response.status_code}: {detail}"
        )

    return True
