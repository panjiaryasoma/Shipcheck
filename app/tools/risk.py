"""Finding prioritization and final-disposition logic."""

from app.models.schemas import FinalDisposition, Finding, Severity


def derive_final_disposition(findings: list[Finding]) -> FinalDisposition:
    if any(finding.severity == Severity.CRITICAL for finding in findings):
        return FinalDisposition.HOLD

    # Manual-review findings remain surfaced, but READY still means
    # "ready within inspected scope", not guaranteed submission validity.
    return FinalDisposition.READY
