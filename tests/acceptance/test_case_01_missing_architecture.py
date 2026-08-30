from app.models.schemas import EvidenceStatus, FinalDisposition, Severity
from app.services.inspection import inspect_fixture


def test_broken_fixture_is_held_for_missing_architecture() -> None:
    report = inspect_fixture(
        rules_path="fixtures/rules/minimal_hackathon_rules.md",
        repository_path="fixtures/repos/broken",
    )

    architecture = next(
        finding
        for finding in report.findings
        if "architecture diagram" in finding.requirement_text.lower()
    )

    assert architecture.status == EvidenceStatus.MISSING
    assert architecture.severity == Severity.CRITICAL
    assert report.final_disposition == FinalDisposition.HOLD
