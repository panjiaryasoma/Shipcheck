from app.core.config import settings
from app.services.inspection import _cloud_evidence_applies_to_target


def test_firestore_evidence_applies_only_to_configured_self_repository(monkeypatch) -> None:
    monkeypatch.setattr(
        settings,
        "shipcheck_self_repository_url",
        "https://github.com/panjiaryasoma/Shipcheck",
    )

    assert _cloud_evidence_applies_to_target(
        "https://github.com/panjiaryasoma/Shipcheck/"
    )
    assert not _cloud_evidence_applies_to_target(
        "https://github.com/panjiaryasoma/Afterlife-AI"
    )


def test_firestore_evidence_is_never_target_evidence_without_self_repo_config(monkeypatch) -> None:
    monkeypatch.setattr(settings, "shipcheck_self_repository_url", None)

    assert not _cloud_evidence_applies_to_target(
        "https://github.com/panjiaryasoma/Shipcheck"
    )
