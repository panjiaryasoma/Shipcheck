# Shipcheck Architecture

```text
Web UI
   |
   v
Cloud Run / FastAPI
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
```

## Design constraints

- one agent for MVP;
- every automated verdict requires evidence;
- unavailable evidence never silently becomes PASS;
- arbitrary repository execution is not allowed;
- model ID is environment-configured until the hackathon-supported Gemini 3.5+
  identifier is confirmed.
