"""Finding prioritization and final-disposition logic."""

from app.models.schemas import EvidenceStatus, FinalDisposition, Finding, Severity


def derive_final_disposition(findings: list[Finding]) -> FinalDisposition:
    if any(finding.severity == Severity.CRITICAL for finding in findings):
        return FinalDisposition.HOLD

    if any(
        finding.severity == Severity.HIGH
        or finding.status == EvidenceStatus.MANUAL_REVIEW
        for finding in findings
    ):
        return FinalDisposition.NEEDS_REVIEW

    return FinalDisposition.READY
