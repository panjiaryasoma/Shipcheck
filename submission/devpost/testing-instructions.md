# Testing Instructions

Shipcheck can be run locally from the public repository. No account is required for the web interface itself.

## Requirements

- Python 3.12.x
- `uv`
- a Gemini API key

Google Cloud Firestore is optional for the normal local path. It is only required if the reviewer wants to exercise audit persistence.

## Local setup

```bash
git clone https://github.com/panjiaryasoma/Shipcheck.git
cd Shipcheck
uv sync
```

Create the local environment file.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Add a Gemini API key:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Start the application:

```bash
uv run uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Suggested evaluation path

Use:

```text
Rules URL:
https://allthingsagentichackathon.devpost.com/rules

Repository URL:
https://github.com/panjiaryasoma/Shipcheck
```

The deployment URL is optional and may be left blank.

Select **Run preflight**. Shipcheck should return a structured Evidence Register containing requirement-level status, severity, observed evidence, reasoning, recommended actions, model provenance, and a final disposition.

The final disposition is intentionally evidence-scoped:

```text
READY         no CRITICAL, HIGH, or MANUAL_REVIEW gate remains
NEEDS_REVIEW  no CRITICAL remains, but HIGH or MANUAL_REVIEW remains
HOLD          at least one CRITICAL finding remains
```

A `READY` result is not a guarantee of organizer acceptance or eligibility.

## Automated checks

```bash
uv run ruff check .
uv run pytest
```

The repository contains unit, integration, and acceptance tests for the core inspection contracts.

## Optional Google Cloud Firestore path

To exercise audit persistence, authenticate Application Default Credentials:

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_GOOGLE_CLOUD_PROJECT
```

Then configure:

```text
GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT
SHIPCHECK_FIRESTORE_ENABLED=true
SHIPCHECK_FIRESTORE_DATABASE=(default)
SHIPCHECK_FIRESTORE_COLLECTION=shipcheck_inspections
SHIPCHECK_SELF_REPOSITORY_URL=https://github.com/panjiaryasoma/Shipcheck
```

A successful persisted inspection creates or updates a Firestore document keyed by the inspection ID.

The Firestore operation is normally evidence about the **Shipcheck inspector runtime**, not the repository being inspected. It may only be promoted into target-project evidence during explicitly configured Shipcheck self-inspection.

## Safety note

Shipcheck does not clone and execute arbitrary third-party repository code. Repository inspection and reproduction checks are bounded and static by design.
