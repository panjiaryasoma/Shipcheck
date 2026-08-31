# Shipcheck

**Autonomous preflight for software submissions.**

Shipcheck turns explicit submission rules into inspectable checks, gathers bounded
repository and deployment evidence, evaluates declared claims, ranks unresolved issues,
and returns a final disposition: `READY`, `HOLD`, or `NEEDS_REVIEW`.

`READY` means no unresolved blocker or review gate was found within the evidence
Shipcheck could inspect. It is not a guarantee of eligibility, judge acceptance, or
competition success.

## Quick start

### 1. Clone the repository

```powershell
git clone https://github.com/panjiaryasoma/Shipcheck.git
cd Shipcheck
```

### 2. Install dependencies

Shipcheck uses Python 3.12 and `uv`.

```powershell
uv sync
```

### 3. Create local configuration

```powershell
Copy-Item .env.example .env
```

Open `.env` and add a Gemini API key:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

The default inspector model and fallback chain are already defined in `.env.example`,
so no additional model configuration is required for the normal local path.

### 4. Start Shipcheck

```powershell
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

Then provide:

1. a public competition rules URL;
2. a public GitHub repository URL;
3. an optional live deployment URL;
4. optional submission claims, one per line.

Select **Run preflight** to generate the evidence register and final disposition.
Completed reports can be downloaded as Markdown (`.md`).

API docs remain available at:

```text
http://127.0.0.1:8000/docs
```

> Firestore is optional for the local quick start. Enable it only when you want
> Google Cloud audit persistence.

## Runtime architecture

```text
Web UI / API
    |
    v
FastAPI inspection orchestrator
    |
    +-- Google ADK rules agent
    |      `-- bounded public rules-page tool
    |
    +-- bounded public GitHub inspector
    +-- static reproduction checker
    +-- deployment verifier
    +-- evidence mapper
    +-- claim evidence checker
    `-- disposition engine
             |
             v
      structured inspection report
             |
             v
      optional Firestore audit record
```

The ADK agent is responsible for rules interpretation. Repository inspection,
deployment verification, evidence mapping, claim checks, risk disposition, and audit
persistence are deterministic application services around that agent.

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
- pytest + Ruff

## Local setup

Install dependencies and create local configuration:

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` and set at least:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

`SHIPCHECK_MODEL` defaults to `gemini-3.7-flash`; bounded fallback models remain
configurable in `.env`.

Run the application:

```powershell
uv run uvicorn app.main:app --reload
```

Open the inspection workspace:

```text
http://127.0.0.1:8000/
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

## Using the inspection workspace

The web workspace accepts:

1. a public rules page;
2. a public HTTPS GitHub repository;
3. an optional deployment URL;
4. optional submission claims, one per line.

`Run preflight` calls `POST /api/inspect` and renders the disposition, summary counts,
inspector-model provenance, requirement-level findings, evidence, and recommended
actions. The rendered report can be downloaded from the browser as Markdown (`.md`).

## Disposition semantics

```text
HOLD
  At least one CRITICAL finding remains.

NEEDS_REVIEW
  No CRITICAL finding remains, but at least one HIGH or MANUAL_REVIEW finding remains.

READY
  No CRITICAL, HIGH, or MANUAL_REVIEW gate remains within inspected scope.
```

## Bounded repository and reproduction inspection

Shipcheck does not execute arbitrary untrusted repositories. The current reproduction
checker verifies only safely observable static evidence such as:

- documented setup/run markers in `README.md`;
- supported dependency manifests;
- bounded repository artifacts already fetched by the inspector.

Actual command execution remains `MANUAL_REVIEW` until a deliberately sandboxed
execution path exists.

The repository inspector samples common Python, JavaScript/TypeScript, Go, Java, and
Kotlin source/configuration files. It recognizes evidence for Google ADK, Google GenAI
SDK, GenKit, and conservative Antigravity SDK markers. Architecture filenames alone do
not receive an automatic pass; binary architecture images are surfaced as candidates
for review.

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
$env:GOOGLE_CLOUD_PROJECT="YOUR_GOOGLE_CLOUD_PROJECT"
$env:SHIPCHECK_FIRESTORE_ENABLED="true"
$env:SHIPCHECK_FIRESTORE_DATABASE="(default)"
$env:SHIPCHECK_FIRESTORE_COLLECTION="shipcheck_inspections"
```

A successful inspection creates or updates a Firestore document whose ID matches the
`inspection_id`. Persistence is disabled by default and enabled persistence fails loudly
rather than being silently reported as success.

### Cloud-evidence boundary

A Firestore write performed by Shipcheck is normally **inspector-runtime evidence**. It
must not be used to prove that an unrelated repository uses Google Cloud.

Only Shipcheck self-inspection may promote that operation into target-project evidence,
and only when the inspected repository matches:

```dotenv
SHIPCHECK_SELF_REPOSITORY_URL=https://github.com/panjiaryasoma/Shipcheck
```

A Cloud Run-compatible `Dockerfile` is repository configuration, not proof of a live
Cloud Run deployment. A rule that specifically requires a Google Cloud-hosted runtime
remains unresolved until a reachable Google Cloud runtime is verified.

## Tests

```powershell
uv run ruff check .
uv run pytest
```

The repository also includes deterministic unit, integration, and acceptance tests.

## Safety boundary

- public repository inspection is bounded by file count and file size;
- GitHub REST is used for metadata/tree while selected public file bodies use the raw
  host so core API quota is not consumed per file;
- local/private rules and deployment targets are rejected;
- rules-page redirects and deployment redirects are validated before following;
- arbitrary repository code is not executed;
- `.dockerignore` excludes local `.env` files and development caches from container
  build context;
- rule extraction records the actual inspector model and fallback state;
- extracted `source_quote` values are validated against the fetched rules text before
  an uncached extraction is accepted.
