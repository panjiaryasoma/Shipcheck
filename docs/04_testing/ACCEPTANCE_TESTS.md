# Shipcheck Acceptance Test Contract

**Status:** Active test contract  
**Runtime version:** 0.6.0

Shipcheck testing is split across unit, integration, and acceptance layers. Acceptance tests focus on externally meaningful disposition behavior rather than implementation details.

## Current executable acceptance coverage

The repository currently contains executable acceptance cases for:

### CASE-01 — Missing architecture evidence

A submission that requires architecture evidence but does not provide sufficient evidence must not be cleared.

Expected behavior:

```text
MISSING / unresolved architecture evidence
-> CRITICAL where mandatory
-> HOLD
```

### CASE-06 — Clear inspected scope vs subjective rule

The acceptance suite distinguishes two important states:

```text
fully checkable rules + compliant fixture
-> READY

otherwise compliant fixture + subjective/manual requirement
-> NEEDS_REVIEW
```

This prevents `READY` from swallowing a human-review gate.

## Supporting regression coverage

Unit and integration tests cover additional contracts including:

- evidence status and contradiction semantics;
- requirement severity and disposition logic;
- Google framework/model evidence detection;
- bounded GitHub repository inspection;
- exclusion of fixtures/tests from production evidence;
- architecture-content hardening;
- static reproduction checks;
- deployment validation and redirect safety;
- rules-page retrieval safety;
- Gemini fallback behavior;
- source-quote grounding;
- Firestore persistence and cloud-evidence scope;
- runtime version reporting;
- API behavior and end-to-end fixture orchestration.

## Required local commands

```bash
uv run ruff check .
uv run pytest
```

A release report must record the actual outputs of those commands. This document does not claim a pass count by itself.

## Acceptance principles

1. A missing artifact cannot silently become `VERIFIED`.
2. A filename alone cannot prove meaningful architecture content.
3. Missing proof cannot be mislabeled as direct contradiction.
4. `MANUAL_REVIEW` must block `READY`.
5. Inspector infrastructure cannot satisfy unrelated target-project cloud requirements.
6. Unsafe repository execution is not performed merely to obtain a prettier demo result.
7. Provider or persistence failure cannot silently become a pass.
