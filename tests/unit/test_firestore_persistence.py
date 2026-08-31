import pytest

from app.core.config import settings
from app.models.live_inspection import InspectionSummary, LiveInspectionReport
from app.models.schemas import FinalDisposition
from app.storage.firestore import _firestore_fields, persist_live_inspection


def _report() -> LiveInspectionReport:
    return LiveInspectionReport(
        inspection_id="live-firestore01",
        timestamp="2026-08-31T07:00:00Z",
        agent_version="0.6.0",
        rules_source="https://example.com/rules",
        repository_url="https://github.com/example/demo",
        model_used="gemini-3.7-flash",
        fallback_used=False,
        final_disposition=FinalDisposition.READY,
        summary=InspectionSummary(passed=3),
        findings=[],
    )


def test_firestore_fields_preserve_audit_identity() -> None:
    fields = _firestore_fields(_report())

    assert fields["inspection_id"]["stringValue"] == "live-firestore01"
    assert fields["timestamp"]["timestampValue"] == "2026-08-31T07:00:00Z"
    assert fields["agent_version"]["stringValue"] == "0.6.0"
    assert fields["final_disposition"]["stringValue"] == "READY"
    assert fields["model_used"]["stringValue"] == "gemini-3.7-flash"
    assert fields["fallback_used"]["booleanValue"] is False
    assert fields["created_at"]["timestampValue"] == "2026-08-31T07:00:00Z"


@pytest.mark.asyncio
async def test_disabled_firestore_is_a_true_noop(monkeypatch) -> None:
    monkeypatch.setattr(settings, "shipcheck_firestore_enabled", False)

    persisted = await persist_live_inspection(_report())

    assert persisted is False
