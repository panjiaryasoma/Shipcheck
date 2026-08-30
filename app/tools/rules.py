"""Deterministic rules fixture parser for the first Shipcheck vertical slice.

Production URL ingestion is deliberately deferred. This parser proves the structured
requirement contract before Gemini or live web retrieval is introduced.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.models.schemas import Requirement, RequirementType

_NUMBERED_RULE = re.compile(r"^\s*\d+\.\s+(?P<text>.+?)\s*$")


def _classify(text: str) -> RequirementType:
    lowered = text.lower()

    subjective_markers = (
        "should demonstrate",
        "should be innovative",
        "should provide social value",
        "compelling",
        "creative",
    )
    if any(marker in lowered for marker in subjective_markers):
        return RequirementType.MANUAL_REVIEW

    return RequirementType.CHECKABLE


def _expected_evidence(text: str) -> list[str]:
    lowered = text.lower()

    if "google adk" in lowered:
        return ["dependency", "source_usage"]
    if "architecture diagram" in lowered:
        return ["architecture_artifact"]
    if "cloud deployment" in lowered:
        return ["deployment_reachability"]

    return ["manual_evidence"]


def extract_fixture_requirements(path: str | Path) -> list[Requirement]:
    rules_path = Path(path)

    if not rules_path.exists():
        raise FileNotFoundError(f"Rules fixture not found: {rules_path}")

    requirements: list[Requirement] = []

    for raw_line in rules_path.read_text(encoding="utf-8").splitlines():
        match = _NUMBERED_RULE.match(raw_line)
        if not match:
            continue

        text = match.group("text").strip()
        requirement_type = _classify(text)

        requirements.append(
            Requirement(
                requirement_id=f"REQ-{len(requirements) + 1:03d}",
                source_section="fixture",
                requirement_text=text,
                requirement_type=requirement_type,
                evidence_expected=_expected_evidence(text),
            )
        )

    if not requirements:
        raise ValueError(f"No numbered requirements found in {rules_path}")

    return requirements
