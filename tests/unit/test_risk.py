from app.models.schemas import (
    EvidenceStatus,
    FinalDisposition,
    Finding,
    RequirementType,
    Severity,
)
from app.tools.risk import derive_final_disposition


def _finding(*, status: EvidenceStatus, severity: Severity) -> Finding:
    return Finding(
        requirement_id="REQ-001",
        requirement_text="Example requirement",
        requirement_type=RequirementType.CHECKABLE,
        status=status,
        severity=severity,
        evidence=[],
        reason="test",
        recommended_action=None,
    )


def test_critical_finding_holds_submission() -> None:
    assert derive_final_disposition(
        [_finding(status=EvidenceStatus.MISSING, severity=Severity.CRITICAL)]
    ) == FinalDisposition.HOLD


def test_manual_review_prevents_ready_state() -> None:
    assert derive_final_disposition(
        [_finding(status=EvidenceStatus.MANUAL_REVIEW, severity=Severity.WARNING)]
    ) == FinalDisposition.NEEDS_REVIEW


def test_high_unverified_finding_prevents_ready_state() -> None:
    assert derive_final_disposition(
        [_finding(status=EvidenceStatus.UNVERIFIED, severity=Severity.HIGH)]
    ) == FinalDisposition.NEEDS_REVIEW


def test_pass_only_findings_are_ready() -> None:
    assert derive_final_disposition(
        [_finding(status=EvidenceStatus.VERIFIED, severity=Severity.PASS)]
    ) == FinalDisposition.READY
