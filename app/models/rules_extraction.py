from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from app.models.schemas import RequirementType


class LiveRulesRequest(BaseModel):
    rules_url: HttpUrl


class ExtractedRequirement(BaseModel):
    requirement_id: str = Field(description="Sequential identifier such as REQ-001.")
    source_section: str | None = Field(
        default=None,
        description="Heading or section where the requirement appears, if identifiable.",
    )
    source_quote: str = Field(
        description="Short verbatim supporting quote from the fetched rules."
    )
    requirement_text: str = Field(
        description="Normalized statement of the explicit requirement."
    )
    requirement_type: RequirementType
    evidence_expected: list[str] = Field(default_factory=list)


class RulesExtractionOutput(BaseModel):
    source_url: str
    page_title: str | None = None
    requirements: list[ExtractedRequirement]
    notes: list[str] = Field(default_factory=list)
    model_used: str | None = None
    fallback_used: bool = False
