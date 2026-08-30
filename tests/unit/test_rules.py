from app.models.schemas import RequirementType
from app.tools.rules import extract_fixture_requirements


def test_fixture_rules_extract_four_requirements() -> None:
    requirements = extract_fixture_requirements(
        "fixtures/rules/minimal_hackathon_rules.md"
    )

    assert len(requirements) == 4
    assert requirements[0].requirement_id == "REQ-001"
    assert requirements[-1].requirement_type == RequirementType.MANUAL_REVIEW
