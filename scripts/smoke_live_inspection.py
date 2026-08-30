"""One-shot end-to-end Shipcheck inspection."""

from __future__ import annotations

import asyncio
import json
import sys

from app.models.schemas import InspectionRequest
from app.services.inspection import inspect_live_submission


async def main() -> None:
    if len(sys.argv) not in {3, 4}:
        raise SystemExit(
            "Usage: smoke_live_inspection.py <rules_url> <github_repo_url> [deployment_url]"
        )

    request = InspectionRequest(
        rules_url=sys.argv[1],
        repository_url=sys.argv[2],
        deployment_url=sys.argv[3] if len(sys.argv) == 4 else None,
    )

    result = await inspect_live_submission(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
