"""Shipcheck Google ADK rules agent."""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types

from app.core.config import settings
from app.models.rules_extraction import RulesExtractionOutput
from app.tools.live_rules import fetch_rules_page

if settings.gemini_api_key:
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "FALSE"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

AGENT_NAME = "shipcheck_rules_agent"
APP_NAME = "shipcheck"

_AGENT_INSTRUCTION = """
You are Shipcheck's rules-inspection agent.

PROCESS
1. ALWAYS call fetch_rules_page with the exact URL supplied by the user.
2. Read only the content returned by that tool.
3. Extract explicit obligations, prohibitions, required deliverables, eligibility
   constraints, technology requirements, and submission conditions.
4. Preserve subjective judging requirements as MANUAL_REVIEW.
5. Keep irrelevant prize/background text out unless it materially affects submission.

STRICT EVIDENCE RULES
- Never invent a requirement that is not supported by fetched text.
- Never upgrade optional language into a mandatory rule.
- If wording is subjective or not machine-verifiable, classify MANUAL_REVIEW.
- Every extracted requirement must contain a short verbatim source_quote.
- source_quote must come from the fetched page.
- requirement_text may normalize wording but must preserve meaning.

REQUIREMENT TYPES
- CHECKABLE: plausibly checkable using repository/runtime/artifact evidence.
- MANUAL_REVIEW: requires subjective or human judgment.
- INFORMATIONAL: relevant context, not a pass/fail obligation.

Use concise evidence categories such as repository_visibility, dependency,
source_usage, architecture_artifact, deployment_reachability, readme_setup,
demo_video, cloud_evidence, submission_field, team_eligibility, deadline,
manual_judgment.

Do not attempt to determine or report the model name. Runtime provenance is added
by Shipcheck after your structured response is validated.

Return the structured output only.
"""


def build_rules_agent(model_name: str) -> Agent:
    return Agent(
        name=AGENT_NAME,
        model=Gemini(
            model=model_name,
            # Shipcheck owns cross-model failover. Keeping provider retries to one
            # prevents a single model attempt from consuming the whole request budget.
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
        instruction=_AGENT_INSTRUCTION,
        tools=[fetch_rules_page],
        output_schema=RulesExtractionOutput,
    )


# Keep a discovery-friendly root agent without requiring credentials at import time.
# Live requests validate GEMINI_API_KEY immediately before model execution.
root_agent = build_rules_agent(settings.shipcheck_model)
