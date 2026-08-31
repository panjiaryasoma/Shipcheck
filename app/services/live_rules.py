"""Programmatic ADK runner with bounded model failover and rules caching."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from pathlib import Path
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import errors as genai_errors
from google.genai import types

from app.agent.root_agent import APP_NAME, build_rules_agent
from app.core.config import settings
from app.models.rules_extraction import RulesExtractionOutput
from app.tools.live_rules import fetch_rules_page

USER_ID = "shipcheck-api"
_CACHE_SCHEMA_VERSION = "v2"
_CACHE_ROOT = Path(".shipcheck_cache") / "rules"


class AgentExtractionError(RuntimeError):
    """Raised when rules extraction cannot complete safely."""


def _model_chain() -> list[str]:
    candidates = [settings.shipcheck_model]
    candidates.extend(
        model.strip()
        for model in settings.shipcheck_fallback_models.split(",")
        if model.strip()
    )
    return list(dict.fromkeys(model for model in candidates if model))


def _model_attempt_timeout_seconds() -> int:
    """Return the bounded timeout for one Gemini model attempt."""
    return max(5, settings.shipcheck_model_timeout_seconds)


def _is_retryable_model_error(exc: BaseException) -> bool:
    """Return True only for provider capacity/quota failures worth failing over."""
    current: BaseException | None = exc
    seen: set[int] = set()

    while current is not None and id(current) not in seen:
        seen.add(id(current))

        if isinstance(current, TimeoutError):
            return True

        if isinstance(current, genai_errors.ServerError):
            return True

        if isinstance(current, genai_errors.ClientError):
            status_code = getattr(current, "code", None) or getattr(
                current, "status_code", None
            )
            if status_code == 429:
                return True

        error_text = f"{type(current).__name__}: {current}".upper()
        if "RESOURCEEXHAUSTED" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            return True

        current = current.__cause__ or current.__context__

    return False


def _source_digest(source_text: str) -> str:
    return hashlib.sha256(source_text.encode()).hexdigest()


def _cache_path(rules_url: str, source_digest: str) -> Path:
    cache_key = hashlib.sha256(
        f"{_CACHE_SCHEMA_VERSION}:{rules_url}:{source_digest}".encode()
    ).hexdigest()
    return _CACHE_ROOT / f"{cache_key}.json"


def _load_cached_result(
    rules_url: str,
    source_digest: str,
) -> RulesExtractionOutput | None:
    ttl_seconds = max(0, settings.shipcheck_rules_cache_ttl_seconds)
    if ttl_seconds == 0:
        return None

    path = _cache_path(rules_url, source_digest)
    if not path.exists():
        return None

    try:
        age_seconds = time.time() - path.stat().st_mtime
        if age_seconds > ttl_seconds:
            path.unlink(missing_ok=True)
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        result = RulesExtractionOutput.model_validate(payload)
        return result.model_copy(
            update={
                "notes": [
                    *result.notes,
                    "Rules extraction loaded from content-addressed local cache.",
                ]
            }
        )
    except (OSError, json.JSONDecodeError, ValueError):
        path.unlink(missing_ok=True)
        return None


def _save_cached_result(
    rules_url: str,
    source_digest: str,
    result: RulesExtractionOutput,
) -> None:
    try:
        _CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        path = _cache_path(rules_url, source_digest)
        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )
        temp_path.replace(path)
    except OSError:
        # Caching is an optimization. Read-only filesystems must not break inspection.
        return


def _normalize_source_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _validate_source_quotes(result: RulesExtractionOutput, source_text: str) -> None:
    normalized_source = _normalize_source_text(source_text)

    for requirement in result.requirements:
        normalized_quote = _normalize_source_text(requirement.source_quote)
        if not normalized_quote or normalized_quote not in normalized_source:
            raise AgentExtractionError(
                "ADK output contained a source_quote that could not be found in the "
                f"fetched rules text ({requirement.requirement_id})."
            )


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
            part.text for part in event.content.parts if getattr(part, "text", None)
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
    source_snapshot = await fetch_rules_page(rules_url)
    source_text = str(source_snapshot.get("text") or "")
    digest = _source_digest(source_text)

    cached = _load_cached_result(rules_url, digest)
    if cached is not None:
        return cached

    if not settings.gemini_api_key:
        raise AgentExtractionError(
            "GEMINI_API_KEY is required for a rules page that is not already cached."
        )

    models = _model_chain()
    failures: list[str] = []
    attempt_timeout_seconds = _model_attempt_timeout_seconds()

    for index, model_name in enumerate(models):
        try:
            result = await asyncio.wait_for(
                _run_agent_once(
                    rules_url=rules_url,
                    model_name=model_name,
                ),
                timeout=attempt_timeout_seconds,
            )
            _validate_source_quotes(result, source_text)
            result = result.model_copy(
                update={
                    "source_url": str(source_snapshot.get("source_url") or rules_url),
                    "page_title": result.page_title or source_snapshot.get("page_title"),
                    "model_used": model_name,
                    "fallback_used": index > 0,
                }
            )
            _save_cached_result(rules_url, digest, result)
            return result
        except Exception as exc:
            if not _is_retryable_model_error(exc):
                raise

            if isinstance(exc, TimeoutError):
                failures.append(f"{model_name}: timeout after {attempt_timeout_seconds}s")
            else:
                failures.append(f"{model_name}: {type(exc).__name__}")

            if index < len(models) - 1:
                await asyncio.sleep(1.0)
                continue

            raise AgentExtractionError(
                "All configured Gemini models timed out, exhausted quota, or were "
                f"temporarily unavailable. Attempts: {', '.join(failures)}"
            ) from exc

    raise AgentExtractionError("No Gemini model was configured.")
