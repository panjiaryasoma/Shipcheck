from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_serves_inspection_workspace() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Not cleared until proven." in response.text
    assert 'id="inspection-form"' in response.text
    assert 'id="report-panel"' in response.text
    assert 'src="/static/js/app.js"' in response.text


def test_health_reports_current_ui_version() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["version"] == "0.5.0"
