"""Write one bounded audit record to the configured Firestore database."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from uuid import uuid4

from app.core.version import SHIPCHECK_VERSION
from app.models.live_inspection import InspectionSummary, LiveInspectionReport
from app.models.schemas import FinalDisposition
from app.storage.firestore import persist_live_inspection


async def main() -> None:
    report = LiveInspectionReport(
        inspection_id=f"firestore-smoke-{uuid4().hex[:10]}",
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        agent_version=SHIPCHECK_VERSION,
        rules_source="firestore-connectivity-smoke",
        repository_url="https://github.com/panjiaryasoma/Shipcheck",
        model_used=None,
        fallback_used=False,
        final_disposition=FinalDisposition.NEEDS_REVIEW,
        summary=InspectionSummary(),
        findings=[],
        notes=["Bounded Firestore connectivity smoke test."],
    )

    persisted = await persist_live_inspection(report)
    print(
        json.dumps(
            {
                "inspection_id": report.inspection_id,
                "persisted": persisted,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
