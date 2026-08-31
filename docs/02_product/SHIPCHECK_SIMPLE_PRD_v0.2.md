# SHIPCHECK — SIMPLE PRODUCT REQUIREMENTS DOCUMENT

**Version:** 0.2  
**Status:** MVP Contract — Implementation Aligned  
**Project:** Shipcheck  
**Hackathon:** All Things Agentic Hackathon  
**Primary Track:** Taskmaster  
**Date:** 31 August 2026  
**Source:** `docs/PROBLEM_BRIEF.md`

---

## 1. Product Summary

Shipcheck is an autonomous preflight inspector for software submissions.

A user provides:

```text
1. Competition / rules URL
2. Public GitHub repository
3. Optional deployed application URL
4. Optional declared submission claims
```

Shipcheck converts explicit submission rules into structured requirements, gathers
bounded repository/runtime evidence, distinguishes missing proof from direct
contradiction, ranks findings, and returns one disposition:

```text
READY
HOLD
NEEDS_REVIEW
```

Shipcheck does not decide whether a project deserves to win and does not guarantee
submission eligibility. `READY` means no unresolved release gate was found within the
scope Shipcheck could inspect.

---

## 2. Primary User

A developer or hackathon participant preparing a software project for submission.

Core question:

> “Is this submission actually ready to ship, and what evidence supports that answer?”

---

## 3. Core Job To Be Done

> Before I submit my software project, inspect the rules, repository, deployment, and
> declared claims; tell me what is proven, what is missing, what is directly
> contradicted, what still needs a human, and what I must fix first.

---

## 4. MVP Input Contract

### Required

```text
rules_url
repository_url
```

### Optional

```text
deployment_url
submission_claims[]
```

### Constraints

- repository must be public GitHub over HTTPS;
- rule targets must resolve to public HTTP(S) addresses;
- local/private targets are rejected;
- repository inspection is bounded by file count and file size;
- private-repository authentication is out of scope;
- untrusted repository code is not executed.

---

## 5. MVP Output Contract

### Metadata

```text
inspection_id
timestamp
agent_version
rules_source
repository_url
deployment_url
model_used
fallback_used
```

`model_used` means the **Shipcheck inspector model used for rules extraction**, not the
model used by the inspected target project.

### Summary

```text
final_disposition:
  READY
  HOLD
  NEEDS_REVIEW
```

### Counts

```text
critical
high
warning
passed
manual_review
```

### Finding

Each finding contains:

```text
requirement_id
requirement_text
requirement_type
status
severity
evidence[]
reason
recommended_action
```

### Evidence status

```text
VERIFIED
MISSING
CONTRADICTED
UNVERIFIED
MANUAL_REVIEW
NOT_APPLICABLE
```

---

## 6. Requirement Classification

### CHECKABLE

Can receive an automated evidence verdict from a bounded checker.

Examples:

```text
Repository must be public
Required Google framework must be evidenced
Gemini minimum version must be evidenced
README must contain setup instructions
Cloud deployment must be reachable
Architecture evidence must exist
```

### MANUAL_REVIEW

Requires a human or subjective judgment.

Examples:

```text
Eligibility declarations
Original-work declarations
Video/subtitle requirements
Judging criteria
Innovation quality
```

### INFORMATIONAL

Context that should not create a pass/fail obligation.

Only `CHECKABLE` requirements may receive automated compliance claims.

---

## 7. Runtime Architecture

Shipcheck uses one Google ADK rules agent surrounded by deterministic application
services.

```text
Web UI / API
    |
    v
FastAPI Inspection Orchestrator
    |
    +-- Google ADK Rules Agent
    |      +-- Gemini 3.5+
    |      `-- bounded rules fetch tool
    |
    +-- Public GitHub Inspector
    +-- Static Reproduction Checker
    +-- Deployment Verifier
    +-- Evidence Mapper
    +-- Claim Evidence Checker
    +-- Disposition Engine
    `-- Optional Firestore Audit Persistence
```

The ADK agent owns natural-language rules interpretation. It does **not** pretend to own
repository inspection, deployment verification, risk logic, or database persistence.
Those remain isolated deterministic services coordinated by the FastAPI inspection
orchestrator.

No multi-agent architecture is required for the MVP.

---

## 8. Tool and Service Contracts

### 8.1 Rules Tool + ADK Rules Agent

Purpose: retrieve a public rules page and extract explicit requirements.

Must:

- use the bounded public-page tool;
- preserve a short `source_quote` for every extracted requirement;
- validate uncached `source_quote` values against the fetched rules text;
- distinguish mandatory language from optional/informational text;
- route subjective requirements to `MANUAL_REVIEW`;
- record the actual Gemini model and fallback state;
- never invent evidence or requirements.

Caching:

- cache is an optimization, not evidence;
- cache key includes rules URL plus fetched-content digest;
- stale content therefore does not silently reuse a prior extraction.

### 8.2 Repository Inspector

Purpose: inspect bounded public GitHub evidence without executing repository code.

Inspectable evidence includes:

```text
README
Python manifests/source
JavaScript / TypeScript manifests/source
Go manifests/source
Java / Kotlin manifests/source
Docker/container config
architecture text/diagram candidates
framework imports/dependencies
model configuration
documentation
```

Must:

- point observations to concrete paths;
- exclude fixture/test/report paths from production evidence;
- avoid forwarding an optional GitHub token to the raw-file host;
- avoid treating container configuration as live deployment proof;
- avoid treating architecture filenames alone as an automatic pass.

Supported Google-framework evidence includes bounded markers for:

```text
Google ADK
Google GenAI SDK
GenKit
Antigravity SDK markers
```

### 8.3 Reproduction Checker

Purpose: perform only reproducibility checks that are safe without running untrusted
code.

Current P0 checks:

```text
README setup/run markers
supported dependency manifest presence
```

Current command-execution status:

```text
MANUAL_REVIEW
```

The MVP does not claim that setup commands were executed. A future command runner must
be explicitly sandboxed before it can produce automated runtime reproduction evidence.

### 8.4 Deployment Verifier

Purpose: verify supplied runtime evidence.

Checks:

```text
public target validation
bounded redirect handling
validation of every redirect target
final HTTP 2xx success
bounded textual response sample when available
Cloud Run hostname recognition (*.run.app)
```

A redirect is not itself treated as final success. A rule specifically requiring a
Google Cloud-hosted backend/runtime remains unresolved until such runtime evidence is
verified.

### 8.5 Evidence Mapper

Purpose: connect requirements to concrete evidence.

Every automated `PASS` must point to explicit evidence. Missing evidence must remain
`MISSING`, `UNVERIFIED`, or `MANUAL_REVIEW` rather than becoming a pass.

Binary architecture files that cannot be inspected become review candidates rather than
automatic passes.

### 8.6 Claim Evidence Checker

Purpose: evaluate declared submission claims against observed evidence.

Direct conflict example:

```text
Claim: Gemini 3.5
Observed primary model: Gemini 3.7
Status: CONTRADICTED
Severity: CRITICAL
```

Missing-proof example:

```text
Claim: project uses Google ADK
Observed evidence: none found
Status: UNVERIFIED
Severity: HIGH
```

Must:

- distinguish missing proof from direct contradiction;
- never infer fraud or intent;
- provide a concrete remediation action for high/critical findings.

### 8.7 Disposition Engine

Severity order:

```text
CRITICAL
HIGH
WARNING
PASS
```

Disposition rules:

```text
if any CRITICAL:
    HOLD
else if any HIGH or MANUAL_REVIEW:
    NEEDS_REVIEW
else:
    READY
```

This prevents unresolved high-risk or human-verification gates from being presented as
`READY`.

### 8.8 Firestore Audit Persistence

Purpose: optionally persist a structured audit record in Google Cloud Firestore.

Must:

- remain disabled by default;
- fail loudly when explicitly enabled and a write fails;
- use Application Default Credentials rather than browser-exposed secrets;
- store report timestamp, agent version, model provenance, summary, and full report;
- label the write as `inspector_runtime` evidence.

Inspector/target boundary:

- a Shipcheck Firestore write is not evidence that an unrelated inspected project uses
  Google Cloud;
- it may be used as target-project evidence only during configured Shipcheck
  self-inspection where the inspected repository matches
  `SHIPCHECK_SELF_REPOSITORY_URL`.

---

## 9. Final Disposition Semantics

### HOLD

At least one unresolved `CRITICAL` finding exists.

### NEEDS_REVIEW

No critical finding exists, but at least one of the following remains:

- a `HIGH` readiness issue;
- a `MANUAL_REVIEW` requirement.

### READY

Return `READY` only when no `CRITICAL`, `HIGH`, or `MANUAL_REVIEW` gate remains within
the inspected scope.

Preferred interpretation:

```text
READY WITHIN INSPECTED SCOPE
```

Never:

```text
GUARANTEED VALID SUBMISSION
```

---

## 10. P0 Functional Requirements

| ID | Requirement | Current implementation |
|---|---|---|
| FR-01 | Public rules ingestion | Implemented |
| FR-02 | Requirement typing | Implemented |
| FR-03 | Public GitHub inspection | Implemented |
| FR-04 | Evidence mapping | Implemented with bounded mappings |
| FR-05 | Deployment verification | Implemented with safe redirects |
| FR-06 | Bounded reproducibility inspection | Implemented as static-only checks |
| FR-07 | Claim contradiction / missing-proof detection | Implemented |
| FR-08 | Severity ranking | Implemented |
| FR-09 | READY / HOLD / NEEDS_REVIEW | Implemented |
| FR-10 | Recommended action for high/critical | Implemented on current high/critical paths |
| FR-11 | Structured result UI | Implemented |
| FR-12 | Deterministic fixtures/tests | Implemented; acceptance coverage remains release work |

---

## 11. Acceptance Cases

### CASE-01 — Missing architecture evidence

Expected:

```text
CRITICAL
MISSING
HOLD
```

If an architecture-like binary candidate exists but content cannot be inspected:

```text
HIGH
UNVERIFIED
NEEDS_REVIEW
```

### CASE-02 — Required Google framework verified

Expected:

```text
PASS
VERIFIED
```

### CASE-03 — Direct model claim contradiction

Expected:

```text
CRITICAL
CONTRADICTED
HOLD
```

### CASE-04 — Required deployment unavailable

Expected:

```text
CRITICAL
UNVERIFIED
HOLD
```

### CASE-05 — Subjective/human-only rule

Expected:

```text
WARNING
MANUAL_REVIEW
NEEDS_REVIEW
```

### CASE-06 — Fully clear inspected scope

Expected:

```text
READY
```

---

## 12. P1 / Deferred Scope

Deferred unless it directly strengthens submission readiness:

```text
GitHub Issue creation
SUBMISSION_EVIDENCE.md generation
deadline-aware remediation ordering
sandboxed command execution
private repository OAuth
persistent user/project history
```

Markdown report export is already implemented and is no longer a deferred P1 item.

---

## 13. Non-Goals

The current MVP does not become:

```text
multi-agent orchestration platform
generic coding assistant
project-management suite
security scanner
code-quality score
full CI/CD system
automatic hackathon submission system
judge prediction system
legal/eligibility guarantee
```

---

## 14. Technology Lock

Required hackathon stack:

```text
Gemini 3.5+
Google Agent Framework
Google Cloud infrastructure
```

Shipcheck implementation:

```text
Python 3.12
Google ADK
Google Gen AI SDK
Gemini 3.7 primary with explicit fallback chain
FastAPI
HTML / CSS / JavaScript
Google Cloud Firestore audit persistence
Cloud Run-compatible Dockerfile
uv
pytest
Ruff
GitHub
```

A Cloud Run-compatible Dockerfile is not represented as a live Cloud Run deployment.

---

## 15. UX Direction

The interface behaves like an industrial shipping/preflight inspection system, not a
chatbot.

Primary states:

```text
AWAITING MANIFEST
INSPECTING
HOLD
NEEDS REVIEW
READY
```

Visual language:

```text
shipping-container inspection plate
technical typography
evidence register
minimal status colors
limited rounded UI
prominent final disposition
visible Markdown report export
```

The current UI identity is considered frozen unless a functional defect is found.

---

## 16. Non-Functional Requirements

### NFR-01 — Traceability

Every automated pass/failure must point to evidence or explicitly state that evidence is
missing.

### NFR-02 — Safe failure

Tool/provider/persistence failure must not silently become a pass.

### NFR-03 — Bounded execution

Untrusted repository code is not executed in the current MVP.

### NFR-04 — Reproducibility

README local setup must be complete enough to install dependencies, configure the Gemini
key, and start the application.

### NFR-05 — Demo speed

Reference inspection should complete within a practical interactive demo window; rule
content caching should reduce repeated Gemini calls without hiding source changes.

### NFR-06 — Cloud evidence provenance

Inspector cloud infrastructure and target-project cloud evidence must remain distinct.

### NFR-07 — Structured state

Requirements, findings, evidence, summary, disposition, model provenance, and audit
metadata use structured objects rather than free-form prose alone.

### NFR-08 — Container secret hygiene

Local `.env` files and development caches must not enter Docker build context.

---

## 17. Release Gate

```text
[x] Rules page can be fetched and parsed
[x] Extracted quotes are validated against fetched text
[x] Requirements are typed
[x] Public GitHub repository can be inspected
[x] Evidence is traceable
[x] Fixture/test evidence is excluded from production evidence
[x] Architecture filename alone cannot auto-pass
[x] Missing proof is distinguished from direct contradiction
[x] Bounded static reproduction checker exists
[x] Deployment redirect handling is bounded and revalidated
[x] Severity ranking works
[x] HOLD disposition works
[x] NEEDS_REVIEW disposition works
[x] READY disposition is gated
[x] Firestore evidence scope is explicit
[x] Inspector Firestore evidence cannot satisfy unrelated target projects
[x] README local setup documents GEMINI_API_KEY
[x] Markdown report export is documented
[x] .dockerignore excludes local secrets
[x] Runtime version has a single source of truth
[ ] Live Google Cloud-hosted application/backend evidence is available if the final
    competition interpretation specifically requires it
[ ] Full test suite and Ruff pass after the final hardening patchset
```

---

## 18. Scope Lock

Shipcheck is:

> **One ADK-powered pre-submission inspection workflow over one ruleset, one public
> repository, and an optional deployment, producing one evidence-backed disposition.**

The agent interprets rules. Deterministic services gather and evaluate bounded evidence.
Anything that does not strengthen that workflow remains deferred.

---

## 19. Simple PRD Gate

| Question | Status |
|---|---|
| Core user flow is explicit? | PASS |
| Inputs and outputs are locked? | PASS |
| Actual runtime architecture is documented? | PASS |
| P0 tools have bounded contracts? | PASS |
| Evidence requirement is enforced? | PASS |
| Claim boundary is explicit? | PASS |
| Inspector/target cloud boundary is explicit? | PASS |
| Model provenance is explicit? | PASS |
| Non-goals are strict? | PASS |
| Production vertical slice works locally? | PASS |
| Final cloud-hosted runtime proof resolved? | PENDING EXTERNAL DEPLOYMENT DECISION |
| Final post-hardening test run complete? | PENDING |

### Gate Decision

**HOLD FOR FINAL VERIFICATION ONLY.**

Do not add product features. Complete the post-hardening test run, resolve any regression,
and separately close the competition-specific live Google Cloud runtime proof question
before submission freeze.
