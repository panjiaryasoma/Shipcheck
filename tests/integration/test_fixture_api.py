from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_broken_fixture_api_returns_hold() -> None:
    response = client.get("/api/fixtures/broken/inspect")

    assert response.status_code == 200
    payload = response.json()

    assert payload["final_disposition"] == "HOLD"
    assert any(
        finding["status"] == "MISSING"
        and "architecture diagram" in finding["requirement_text"].lower()
        for finding in payload["findings"]
    )
