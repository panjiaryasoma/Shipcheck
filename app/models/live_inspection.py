from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.schemas import FinalDisposition, Finding


class InspectionSummary(BaseModel):
    critical: int = 0
    high: int = 0
    warning: int = 0
    passed: int = 0
    manual_review: int = 0


class LiveInspectionReport(BaseModel):
    inspection_id: str
    timestamp: str
    agent_version: str
    rules_source: str
    repository_url: str
    deployment_url: str | None = None
    model_used: str | None = None
    fallback_used: bool = False
    final_disposition: FinalDisposition
    summary: InspectionSummary
    findings: list[Finding]
    notes: list[str] = Field(default_factory=list)
