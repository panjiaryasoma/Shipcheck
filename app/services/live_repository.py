"""Live public GitHub inspection service."""

from app.models.repository_inspection import RepositoryInspectionOutput
from app.tools.github_repo import inspect_public_github_repository


async def inspect_live_repository(repository_url: str) -> RepositoryInspectionOutput:
    payload = await inspect_public_github_repository(repository_url)
    return RepositoryInspectionOutput.model_validate(payload)
