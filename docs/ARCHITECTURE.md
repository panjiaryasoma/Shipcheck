# Shipcheck Architecture

```text
Web UI / CLI
   |
   v
FastAPI inspection service
   |
   v
Google ADK Root Agent
   |
   +-- Rules Tool
   +-- Repository Inspector
   +-- Reproduction Checker
   +-- Deployment Verifier
   +-- Evidence Mapper
   +-- Contradiction Detector
   `-- Risk Planner
           |
           v
    Structured Inspection Report
           |
           v
 Google Cloud Firestore
 optional audit persistence
```

## Google Cloud boundary

The current zero-billing demo path uses the project's default Google Cloud Firestore
database as a persistent audit backend. Each enabled live inspection writes the
structured report under `shipcheck_inspections/{inspection_id}` using Application
Default Credentials.

The container remains Cloud Run-compatible, but repository configuration alone is not
treated as proof that a live Cloud Run runtime exists.

## Design constraints

- one agent for MVP;
- every automated verdict requires evidence;
- unavailable evidence never silently becomes PASS;
- Firestore persistence is opt-in and fails loudly when explicitly enabled;
- arbitrary repository execution is not allowed;
- model ID is environment-configured until the hackathon-supported Gemini 3.5+
  identifier is confirmed.
