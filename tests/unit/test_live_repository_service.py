from app.services.live_repository import _remove_self_referential_cloud_evidence


def test_self_referential_cloud_run_config_is_removed() -> None:
    payload = {
        "artifacts": [
            {
                "evidence_type": "cloud_run_config",
                "path": "app/tools/contradiction.py",
                "observed_value": "gcloud run deploy",
            },
            {
                "evidence_type": "architecture_artifact",
                "path": "docs/ARCHITECTURE.md",
                "observed_value": "architecture artifact present",
            },
        ],
        "notes": [],
    }

    result = _remove_self_referential_cloud_evidence(payload)

    evidence_types = {
        artifact["evidence_type"] for artifact in result["artifacts"]
    }
    assert "cloud_run_config" not in evidence_types
    assert "architecture_artifact" in evidence_types


def test_real_readme_cloud_run_config_is_preserved() -> None:
    payload = {
        "artifacts": [
            {
                "evidence_type": "cloud_run_config",
                "path": "README.md",
                "observed_value": "gcloud run deploy shipcheck",
            }
        ],
        "notes": [],
    }

    result = _remove_self_referential_cloud_evidence(payload)

    assert result["artifacts"][0]["path"] == "README.md"
