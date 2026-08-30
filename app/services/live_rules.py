"""Programmatic ADK runner with bounded model failover."""

from __future__ import annotations

import asyncio
import json
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import errors as genai_errors
from google.genai import types

from app.agent.root_agent import APP_NAME, build_rules_agent
from app.core.config import settings
from app.models.rules_extraction import RulesExtractionOutput

USER_ID = "shipcheck-api"


class AgentExtractionError(RuntimeError):
    """Raised when all configured rules-extraction model attempts fail."""


def _model_chain() -> list[str]:
    candidates = [settings.shipcheck_model]
    candidates.extend(
        model.strip()
        for model in settings.shipcheck_fallback_models.split(",")
        if model.strip()
    )
    return list(dict.fromkeys(model for model in candidates if model))


async def _run_agent_once(*, rules_url: str, model_name: str) -> RulesExtractionOutput:
    session_service = InMemorySessionService()
    session_id = f"rules-{uuid4().hex}"

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    runner = Runner(
        agent=build_rules_agent(model_name),
        app_name=APP_NAME,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Inspect this rules page and extract its explicit requirements: "
                    f"{rules_url}"
                )
            )
        ],
    )

    final_text: str | None = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if not event.is_final_response():
            continue
        if not event.content or not event.content.parts:
            continue

        text_parts = [
            part.text
            for part in event.content.parts
            if getattr(part, "text", None)
        ]
        if text_parts:
            final_text = "".join(text_parts)

    if not final_text:
        raise AgentExtractionError(
            f"ADK agent returned no final response using {model_name}."
        )

    try:
        payload = json.loads(final_text)
        return RulesExtractionOutput.model_validate(payload)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AgentExtractionError(
            f"ADK agent returned invalid structured output using {model_name}."
        ) from exc


async def extract_requirements_with_adk(rules_url: str) -> RulesExtractionOutput:
    models = _model_chain()

    for index, model_name in enumerate(models):
        try:
            result = await _run_agent_once(
                rules_url=rules_url,
                model_name=model_name,
            )
            return result.model_copy(
                update={
                    "model_used": model_name,
                    "fallback_used": index > 0,
                }
            )
        except genai_errors.ServerError as exc:
            if index < len(models) - 1:
                await asyncio.sleep(1.0)
                continue

            raise AgentExtractionError(
                "All configured Gemini models were temporarily unavailable."
            ) from exc

    raise AgentExtractionError("No Gemini model was configured.")
