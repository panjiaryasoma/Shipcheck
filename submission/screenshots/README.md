# Submission Screenshot Plan

This directory is reserved for final screenshots used in Devpost or supporting submission materials.

Do not add screenshots merely to fill the folder. Each image should communicate one distinct part of the product.

## Recommended captures

### 01 — Manifest / preflight input

Show the Shipcheck inspection workspace before execution with:

- rules URL;
- repository URL;
- optional deployment field;
- declared-claims field;
- **Run preflight** action.

Suggested filename:

```text
01_manifest.png
```

### 02 — Final disposition + evidence register

Show a completed inspection with:

- `READY`, `NEEDS_REVIEW`, or `HOLD`;
- summary counts;
- inspector model provenance;
- visible requirement findings.

Suggested filename:

```text
02_evidence_register.png
```

### 03 — Requirement evidence detail

Show one strong evidence example where the UI exposes:

- requirement text;
- evidence status;
- severity;
- concrete repository path or URL;
- reason;
- recommended action when applicable.

Suggested filename:

```text
03_requirement_evidence.png
```

### 04 — Architecture

The canonical architecture image already exists at:

```text
docs/05_arch/Architecture.png
```

Do not duplicate it here unless Devpost upload workflow requires a separate local asset.

### 05 — Google Cloud Firestore proof

Show Google Cloud Console with the Shipcheck Firestore collection and a real persisted inspection record.

Hide or crop unrelated account information and credentials.

Suggested filename:

```text
05_firestore_audit.png
```

## Screenshot rules

- Use actual application state.
- Do not mock a passing result.
- Do not expose API keys, tokens, `.env`, authentication material, billing details, or unnecessary account identifiers.
- Keep browser chrome only when it helps demonstrate provenance such as GitHub or Google Cloud Console.
- Prefer readable evidence over decorative screenshots.
