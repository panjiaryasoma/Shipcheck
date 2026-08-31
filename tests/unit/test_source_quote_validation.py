import pytest

from app.models.rules_extraction import RulesExtractionOutput
from app.services.live_rules import AgentExtractionError, _validate_source_quotes


def _result(source_quote: str) -> RulesExtractionOutput:
    return RulesExtractionOutput.model_validate(
        {
            "source_url": "https://example.com/rules",
            "requirements": [
                {
                    "requirement_id": "REQ-001",
                    "source_section": "Rules",
                    "source_quote": source_quote,
                    "requirement_text": "The submission must include English materials.",
                    "requirement_type": "CHECKABLE",
                    "evidence_expected": ["submission_field"],
                }
            ],
        }
    )


def test_source_quote_accepts_smart_punctuation_and_whitespace_normalization() -> None:
    source = "Submission materials — including the video — must be in English."
    result = _result("Submission materials - including the video - must be in English.")

    _validate_source_quotes(result, source)


def test_source_quote_accepts_contiguous_words_despite_punctuation_changes() -> None:
    source = "Entrants must provide: a public repository, README, and architecture diagram."
    result = _result("Entrants must provide a public repository README and architecture diagram")

    _validate_source_quotes(result, source)


def test_source_quote_rejects_paraphrase_or_invented_evidence() -> None:
    source = "Entrants must provide a public repository and README."
    result = _result("Every entrant must deploy the backend on Google Cloud Run.")

    with pytest.raises(AgentExtractionError):
        _validate_source_quotes(result, source)
