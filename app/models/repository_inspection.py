from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl


class LiveRepositoryRequest(BaseModel):
    repository_url: HttpUrl


class RepositoryArtifact(BaseModel):
    evidence_type: str
    path: str
    observed_value: str | None = None


class RepositoryInspectionOutput(BaseModel):
    repository_url: str
    owner: str
    repository: str
    default_branch: str
    public: bool
    artifacts: list[RepositoryArtifact] = Field(default_factory=list)
    inspected_files: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
