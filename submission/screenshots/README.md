# Submission Screenshot Plan

This directory contains final or near-final screenshots used in Devpost and supporting submission materials.

Each image should communicate one distinct part of Shipcheck. Do not add screenshots merely to fill the folder.

## Current capture set

### 01 — Manifest / preflight input

`01_manifest.png`

Show the Shipcheck inspection workspace before execution with:

- rules URL;
- repository URL;
- optional deployment field;
- declared-claims field;
- **Run preflight** action.

### 02 — Final disposition + evidence register

`02_evidence_register.png`

Show the canonical completed self-inspection with:

- `NEEDS_REVIEW` final disposition;
- summary counts;
- inspector model provenance;
- repository and rules-source provenance;
- visible requirement findings.

For the All Things Agentic self-inspection, `NEEDS_REVIEW` is the expected conservative result when human-only submission requirements remain unresolved while no critical blocker exists.

### 03 — Mandatory technology evidence

`03_requirement_evidence.png`

Show the strongest requirement-level technology evidence in one application frame where possible, including:

- Gemini 3.5 or newer → `VERIFIED`;
- supported Google Agent Framework / Google ADK → `VERIFIED`;
- Google Cloud infrastructure / Firestore → `VERIFIED` when visible;
- concrete repository or cloud evidence;
- requirement text and reason.

### 04 — Google Cloud Firestore audit proof

`04_firestore_audit.png`

Show Google Cloud Console with:

- the Shipcheck Google Cloud project;
- Cloud Firestore;
- collection `shipcheck_inspections`;
- the persisted document for the canonical self-inspection;
- visible fields such as inspection ID, final disposition, model used, repository URL, or timestamp when practical.

This console capture is the strongest visual proof that the live inspection produced a real Google Cloud audit record. Hide or crop unrelated account information and credentials.

## Canonical architecture assets

Architecture visuals remain in `docs/05_arch/` and should not be duplicated here unless the submission upload flow specifically requires a second local copy:

```text
docs/05_arch/E2E_Diagram.png
docs/05_arch/Flowchart.png
docs/05_arch/Architecture.png
```

## Screenshot rules

- Use actual application state.
- Do not mock a passing result.
- Recapture evidence screenshots after changes that affect requirement classification, evidence wording, or disposition semantics.
- Do not expose API keys, tokens, `.env`, authentication material, billing details, or unnecessary account identifiers.
- Keep browser chrome only when it helps demonstrate provenance such as GitHub or Google Cloud Console.
- Prefer readable evidence over decorative screenshots.
