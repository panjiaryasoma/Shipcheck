from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class RequirementType(StrEnum):
    CHECKABLE = "CHECKABLE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    INFORMATIONAL = "INFORMATIONAL"


class EvidenceStatus(StrEnum):
    VERIFIED = "VERIFIED"
    MISSING = "MISSING"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIED = "UNVERIFIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Severity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    WARNING = "WARNING"
    PASS = "PASS"


class FinalDisposition(StrEnum):
    READY = "READY"
    HOLD = "HOLD"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class InspectionRequest(BaseModel):
    rules_url: HttpUrl
    repository_url: HttpUrl
    deployment_url: HttpUrl | None = None
    submission_claims: list[str] = Field(default_factory=list)


class Requirement(BaseModel):
    requirement_id: str
    source_section: str | None = None
    requirement_text: str
    requirement_type: RequirementType
    evidence_expected: list[str] = Field(default_factory=list)


class Evidence(BaseModel):
    source: str
    path_or_url: str | None = None
    observed_value: str | None = None


class Finding(BaseModel):
    requirement_id: str
    requirement_text: str
    requirement_type: RequirementType
    status: EvidenceStatus
    severity: Severity
    evidence: list[Evidence] = Field(default_factory=list)
    reason: str
    recommended_action: str | None = None


class InspectionReport(BaseModel):
    inspection_id: str
    final_disposition: FinalDisposition
    findings: list[Finding]
