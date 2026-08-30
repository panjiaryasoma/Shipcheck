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
                    ↓
        optional Firestore audit record
```

One agent. One inspection. One evidence-backed report.

## Stack

- Python 3.12
- Google ADK
- Google Gen AI SDK
- Gemini 3.5+ model selected through environment configuration
- FastAPI
- server-rendered HTML + vanilla JavaScript inspection workspace
- Google Cloud Firestore for optional inspection audit persistence
- Cloud Run-compatible container configuration
- uv
- pytest

## Local setup

```powershell
uv sync
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

Open the inspection workspace:

```text
http://127.0.0.1:8000/
```

API documentation remains available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

## Using the inspection workspace

The web workspace accepts:

1. a public HTTPS rules page;
2. a public HTTPS GitHub repository;
3. an optional deployment URL;
4. optional submission claims, one per line.

`Run preflight` calls `POST /api/inspect` and renders the disposition, summary counts,
model provenance, requirement-level findings, evidence, and recommended actions. The
report can also be downloaded as JSON from the browser.

## Firestore audit persistence

Shipcheck can persist live inspection reports to the project's default Google Cloud
Firestore database without making Firestore a dependency of fixture tests.

Authenticate local Application Default Credentials once:

```powershell
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_GOOGLE_CLOUD_PROJECT
```

Then enable persistence before running a live inspection:

```powershell
$env:SHIPCHECK_FIRESTORE_ENABLED="true"
$env:SHIPCHECK_FIRESTORE_DATABASE="(default)"
$env:SHIPCHECK_FIRESTORE_COLLECTION="shipcheck_inspections"
```

A successful live inspection creates or updates a document whose ID matches the
`inspection_id`. Firestore persistence is disabled by default and, when explicitly
enabled, persistence errors fail loudly rather than being reported as success.

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
