"""One-shot live ADK smoke test."""

from __future__ import annotations

import asyncio
import json
import sys

from app.services.live_rules import extract_requirements_with_adk


async def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: smoke_live_rules.py <rules_url>")

    result = await extract_requirements_with_adk(sys.argv[1])
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
