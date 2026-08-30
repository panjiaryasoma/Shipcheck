from app.models.rules_extraction import RulesExtractionOutput


def test_structured_rules_output_validates() -> None:
    payload = {
        "source_url": "https://example.com/rules",
        "page_title": "Rules",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "source_section": "Submission",
                "source_quote": "The project must include an architecture diagram.",
                "requirement_text": "The submission must include an architecture diagram.",
                "requirement_type": "CHECKABLE",
                "evidence_expected": ["architecture_artifact"],
            }
        ],
        "notes": [],
    }

    parsed = RulesExtractionOutput.model_validate(payload)

    assert parsed.requirements[0].requirement_id == "REQ-001"
    assert parsed.requirements[0].requirement_type.value == "CHECKABLE"
