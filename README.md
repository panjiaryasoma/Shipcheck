# Shipcheck

**Autonomous preflight for software submissions.**

Shipcheck turns explicit submission rules into inspectable checks, gathers repository
and deployment evidence, detects contradictions, ranks blockers, and returns a final
disposition: `READY`, `HOLD`, or `NEEDS_REVIEW`.

## MVP boundary

```text
Rules URL + Public GitHub Repo + Optional Deployment
                    ↓
               Shipcheck Agent
                    ↓
   requirements → evidence → findings → disposition
```

One agent. One inspection. One evidence-backed report.

## Stack

- Python 3.12
- Google ADK
- Google Gen AI SDK
- Gemini 3.5+ model selected through environment configuration
- FastAPI
- Google Cloud Run
- uv
- pytest

## Local setup

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

Health check:

```text
GET /health
```

## Tests

```powershell
uv run pytest
```

## First production milestone

```text
fixture rules
+ fixture repository
        ↓
extract three requirements
        ↓
inspect evidence
        ↓
detect one blocker
        ↓
return structured JSON report
```

Do not add P1 features before the first acceptance fixture passes.

## Important safety boundary

Shipcheck must not blindly execute arbitrary untrusted repositories. Reproduction
checks must remain bounded; unsupported execution paths are routed to manual review.
