from app.models.schemas import FinalDisposition, Severity
from app.services.inspection import inspect_fixture


def test_compliant_fixture_is_ready_within_inspected_scope() -> None:
    report = inspect_fixture(
        rules_path="fixtures/rules/minimal_hackathon_rules.md",
        repository_path="fixtures/repos/compliant",
    )

    assert not any(f.severity == Severity.CRITICAL for f in report.findings)
    assert report.final_disposition == FinalDisposition.READY
