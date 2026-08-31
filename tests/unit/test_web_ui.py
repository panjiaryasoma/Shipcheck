from fastapi.testclient import TestClient

from app.core.version import SHIPCHECK_VERSION
from app.main import app

client = TestClient(app)


def test_root_serves_inspection_workspace() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Not cleared until proven." in response.text
    assert "READY / REVIEW / HOLD" in response.text
    assert "Inspector model" in response.text
    assert 'id="inspection-form"' in response.text
    assert 'id="report-panel"' in response.text
    assert 'id="download-report"' in response.text
    assert "Download report" in response.text
    assert ".MD ↓" in response.text
    assert 'href="/static/css/report-actions.css"' in response.text
    assert 'href="/static/css/identity.css"' in response.text
    assert 'src="/static/js/app.js"' in response.text


def test_report_export_uses_markdown_with_provenance_and_high_count() -> None:
    response = client.get("/static/js/app.js")

    assert response.status_code == 200
    assert "text/markdown;charset=utf-8" in response.text
    assert 'anchor.download = `${latestReport.inspection_id || "shipcheck-report"}.md`' in response.text
    assert "# Shipcheck Inspection Report" in response.text
    assert "**Agent version:**" in response.text
    assert "**Inspector model:**" in response.text
    assert "**High:**" in response.text
    assert 'highWarningLabel.textContent = "High / warning"' in response.text


def test_report_findings_include_evidence_trace_markers() -> None:
    response = client.get("/static/js/app.js")

    assert response.status_code == 200
    assert 'trace.className = "finding-trace"' in response.text
    assert 'trace.textContent = `EVD-${String(index + 1).padStart(2, "0")}`' in response.text


def test_health_reports_current_runtime_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["version"] == SHIPCHECK_VERSION
