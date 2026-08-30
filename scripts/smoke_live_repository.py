"""One-shot live public GitHub inspection."""

from __future__ import annotations

import asyncio
import json
import sys

from app.services.live_repository import inspect_live_repository


async def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: smoke_live_repository.py <github_repo_url>")

    result = await inspect_live_repository(sys.argv[1])
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
