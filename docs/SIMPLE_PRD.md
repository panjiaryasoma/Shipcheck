# SHIPCHECK — SIMPLE PRODUCT REQUIREMENTS DOCUMENT

**Version:** 0.1  
**Status:** Scope Locked for MVP  
**Project:** Shipcheck  
**Hackathon:** All Things Agentic Hackathon  
**Primary Track:** Taskmaster  
**Date:** 30 August 2026  
**Source:** `SHIPCHECK_PROBLEM_BRIEF_v0.1.md`

---

## 1. Product Summary

Shipcheck is an autonomous preflight agent for software submissions.

A user provides:

```text
1. Competition / rules URL
2. Public GitHub repository
3. Optional deployed application URL
```

Shipcheck converts explicit submission rules into inspectable checks, gathers evidence from the repository and runtime, detects missing or contradictory evidence, ranks findings by severity, and returns a final disposition:

```text
READY
or
HOLD / BLOCKED
```

Shipcheck does not decide whether a project deserves to win. It checks whether the submission can prove what it claims and whether machine-verifiable requirements appear satisfied.

---

## 2. Primary User

A developer or hackathon participant preparing a software project for submission.

The user already has a project and needs to answer:

> “Is this submission actually ready to ship?”

---

## 3. Core Job To Be Done

> Before I submit my software project, inspect the rules, repository, and deployment; tell me what is proven, what is missing, what contradicts my claims, and what I must fix first.

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
submission_claims
```

### Initial constraints

- repository must be public;
- rules must be retrievable from a public page;
- only bounded repository inspection is supported;
- private repository authentication is out of scope.

---

## 5. MVP Output Contract

Shipcheck returns one inspection report containing:

### Metadata

```text
inspection_id
rules_source
repository
deployment
timestamp
agent_version
```

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

### Findings

Each finding must contain:

```text
requirement_id
requirement_text
requirement_type
status
severity
evidence
reason
recommended_action
```

### Evidence status

Allowed values:

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

Every extracted rule must be classified as one of:

### CHECKABLE

Can be evaluated using available tools.

Examples:

```text
Architecture diagram required
Repository must be public
Required framework must be used
Cloud deployment must be reachable
README must contain setup instructions
```

### MANUAL_REVIEW

Requires subjective or human judgment.

Examples:

```text
Project should be innovative
Demo should be compelling
Submission should provide social value
```

### INFORMATIONAL

Useful context but not a pass/fail requirement.

Examples:

```text
Prize information
Organizer description
Workshop schedule
```

Only `CHECKABLE` requirements may produce automated compliance verdicts.

---

## 7. Agent Architecture

The MVP uses one Google ADK agent with scoped tools.

```text
Web UI
   ↓
Cloud Run API
   ↓
Shipcheck ADK Agent
   ↓
Gemini 3.5+
   │
   ├── Rules Tool
   ├── Repository Inspector
   ├── Reproduction Checker
   ├── Deployment Verifier
   ├── Evidence Mapper
   ├── Contradiction Detector
   └── Risk Planner
```

No multi-agent architecture is required for v0.1.

---

## 8. Tool Contracts

## 8.1 Rules Tool

### Purpose

Retrieve rule pages and extract explicit requirements.

### Input

```text
rules_url
```

### Output

```text
requirement_id
source_section
requirement_text
requirement_type
evidence_expected
```

### Must

- preserve source wording where practical;
- distinguish explicit rules from model inference;
- classify ambiguous requirements as `MANUAL_REVIEW`;
- never invent a mandatory requirement.

---

## 8.2 Repository Inspector

### Purpose

Inspect repository structure and implementation evidence.

### Input

```text
repository_url
requirements
```

### Inspectable evidence

```text
README
dependency files
source tree
Dockerfile
deployment configs
tests
architecture files
framework imports
model configuration
documentation
```

### Output

```text
artifact
path
evidence_type
observed_value
```

### Must

- point every observation to a concrete repository artifact;
- mark unavailable evidence as `UNVERIFIED`;
- avoid treating filenames alone as proof when content is required.

---

## 8.3 Reproduction Checker

### Purpose

Test bounded reproducibility claims.

### Candidate checks

```text
README setup command exists
dependency manifest exists
build/test command exists
basic project command can be invoked safely
```

### Output

```text
command
status
stdout_summary
stderr_summary
evidence
```

### Constraint

The MVP must not blindly execute arbitrary untrusted code without bounded safeguards.

Unsupported execution paths become:

```text
MANUAL_REVIEW
```

---

## 8.4 Deployment Verifier

### Purpose

Verify runtime evidence when a deployment URL is supplied.

### Input

```text
deployment_url
```

### Checks

```text
URL reachable
HTTP success
expected app response exists
optional health endpoint
```

### Output

```text
reachable
status_code
observed_response
```

If a deployment is required by rules but cannot be verified:

```text
severity = CRITICAL
status = MISSING / UNVERIFIED
```

---

## 8.5 Evidence Mapper

### Purpose

Connect requirements to observed evidence.

### Output example

```text
Requirement:
Must use Google ADK

Evidence:
pyproject.toml → google-adk dependency
app/agent.py → Agent(...) usage

Status:
VERIFIED
```

Every automated pass must include explicit evidence.

---

## 8.6 Contradiction Detector

### Purpose

Detect inconsistencies between claims and evidence.

### Example

```text
Claim:
Uses Gemini 3.5

Observed:
gemini-2.5-flash

Status:
CONTRADICTED

Severity:
CRITICAL
```

### Must

- use concrete evidence;
- distinguish `missing proof` from `direct contradiction`;
- never infer fraud or intent.

---

## 8.7 Risk Planner

### Purpose

Prioritize findings.

### Severity order

```text
CRITICAL
HIGH
WARNING
PASS
```

### Default interpretation

#### CRITICAL
Likely submission blocker or explicit mandatory requirement failure.

#### HIGH
Significant readiness issue that should be fixed before submission.

#### WARNING
Non-blocking weakness or incomplete evidence.

#### PASS
Requirement supported by evidence.

---

## 9. Final Disposition Logic

### HOLD

Return `HOLD` if one or more unresolved `CRITICAL` findings exist.

### NEEDS_REVIEW

Return `NEEDS_REVIEW` if:

- no critical automated failure exists;
- but important mandatory requirements remain human-verifiable only.

### READY

Return `READY` only if:

- no unresolved critical findings exist;
- all machine-checkable mandatory requirements are verified;
- remaining manual-review items are explicitly surfaced.

Preferred UI wording:

```text
READY WITHIN INSPECTED SCOPE
```

Not:

```text
GUARANTEED VALID SUBMISSION
```

---

## 10. P0 Functional Requirements

### FR-01 — Rules ingestion

System accepts one public rules URL and extracts structured requirements.

### FR-02 — Requirement typing

System classifies requirements into:

```text
CHECKABLE
MANUAL_REVIEW
INFORMATIONAL
```

### FR-03 — Repository inspection

System accepts one public GitHub repository and inspects relevant artifacts.

### FR-04 — Evidence mapping

Every automated pass or failure points to concrete evidence or explicitly states that evidence is missing.

### FR-05 — Deployment verification

When deployment evidence is relevant and a URL is supplied, system checks reachability.

### FR-06 — Reproducibility inspection

System performs bounded reproducibility checks where safely supported.

### FR-07 — Contradiction detection

System detects material mismatches between submitted claims and observed evidence.

### FR-08 — Severity ranking

System ranks findings as critical, high, warning, or pass.

### FR-09 — Final disposition

System returns:

```text
READY
HOLD
NEEDS_REVIEW
```

### FR-10 — Recommended action

Every critical or high finding includes one concrete next action.

### FR-11 — Structured result UI

User can inspect:

```text
requirement
status
evidence
reason
recommended action
```

without reading raw agent traces.

### FR-12 — Deterministic demo fixtures

The repository includes intentionally broken fixture cases with expected findings.

---

## 11. Initial Acceptance Cases

### CASE-01 — Missing architecture evidence

```text
Rule:
Architecture diagram required

Repository:
No architecture artifact found

Expected:
CRITICAL
MISSING
HOLD
```

### CASE-02 — Required framework verified

```text
Rule:
Must use Google ADK

Repository:
Dependency and source usage found

Expected:
PASS
VERIFIED
```

### CASE-03 — Model claim contradiction

```text
Claim:
Gemini 3.5

Repository:
Gemini 2.5 configuration

Expected:
CRITICAL
CONTRADICTED
HOLD
```

### CASE-04 — Deployment unreachable

```text
Rule:
Working cloud deployment required

Deployment URL:
unreachable

Expected:
CRITICAL
UNVERIFIED
HOLD
```

### CASE-05 — Subjective judging rule

```text
Rule:
Project should demonstrate strong innovation

Expected:
MANUAL_REVIEW
No automated pass/fail claim
```

### CASE-06 — Fully compliant fixture

```text
All checkable requirements verified
No contradiction
No blocker

Expected:
READY WITHIN INSPECTED SCOPE
```

---

## 12. P1 — Only If P0 Is Stable

```text
GitHub Issue creation
SUBMISSION_EVIDENCE.md generation
deadline-aware remediation ordering
export report
```

None of these may block P0 release.

---

## 13. Non-Goals

Do not build for v0.1:

```text
multi-agent orchestration
authentication
database
project history
private repo OAuth
Slack
email
browser extension
vector database
analytics
security scanner
code-quality scoring
generic CI/CD
automatic submission
judge prediction
```

---

## 14. Technology Lock

### Required hackathon stack

```text
Gemini 3.5+
Google ADK
Google Cloud
```

### Proposed implementation

```text
Python 3.12
Google ADK
Gemini API / Google GenAI
FastAPI
Cloud Run
HTML / CSS / JavaScript
uv
pytest
GitHub
```

Exact Gemini 3.5 model identifier must be confirmed against currently available hackathon-supported models before deployment.

---

## 15. UX Direction

The interface should behave like an industrial inspection system rather than a chatbot.

Primary states:

```text
INSPECTION READY
INSPECTING
HOLD
NEEDS REVIEW
CLEARED
```

Primary result visual:

```text
FINAL DISPOSITION

HOLD
NOT CLEARED TO SHIP
```

or:

```text
FINAL DISPOSITION

READY
CLEARED WITHIN INSPECTED SCOPE
```

Visual language:

```text
industrial inspection plate
technical typography
evidence table
minimal status colors
limited rounded UI
```

---

## 16. Non-Functional Requirements

### NFR-01 — Traceability

Every automated verdict must point to evidence.

### NFR-02 — Safe failure

Tool failure must not silently become a pass.

### NFR-03 — Bounded execution

Repository execution must be constrained.

### NFR-04 — Reproducibility

Repository must document local setup.

### NFR-05 — Demo speed

Reference inspection should complete within a practical interactive demo window.

### NFR-06 — Cloud evidence

The production demo must visibly run through Google Cloud infrastructure required by the hackathon.

### NFR-07 — Structured agent state

Requirements, evidence, findings, and final disposition must use structured objects rather than free-form prose only.

---

## 17. Release Gate

P0 is ready when:

```text
[ ] Rules page can be parsed
[ ] Requirements are typed
[ ] Public repo can be inspected
[ ] Evidence is traceable
[ ] Missing evidence is detected
[ ] One contradiction case is detected
[ ] Deployment verification works
[ ] Severity ranking works
[ ] HOLD disposition works
[ ] READY fixture works
[ ] Manual-review requirement does not receive fake certainty
[ ] Cloud Run deployment works
[ ] README is reproducible
[ ] Core tests pass
```

---

## 18. Scope Lock

Shipcheck v0.1 is:

> **One agent performing one pre-submission inspection over one ruleset, one repository, and an optional deployment, producing one evidence-backed disposition.**

Anything that does not strengthen that workflow is deferred.

---

## 19. Simple PRD Gate

| Question | Status |
|---|---|
| Core user flow is explicit? | PASS |
| Inputs and outputs are locked? | PASS |
| One-agent architecture is locked? | PASS |
| P0 tools have bounded contracts? | PASS |
| Evidence requirement is enforced? | PASS |
| Claim boundary is explicit? | PASS |
| Acceptance cases exist? | PASS |
| Non-goals are strict? | PASS |
| Exact Google model ID confirmed? | PENDING |
| Repo scaffold created? | PENDING |
| Production vertical slice works? | PENDING |

### Gate Decision

**PASS TO REPO SCAFFOLD + VERTICAL SLICE**

No additional product features should be added until the first end-to-end inspection fixture passes.
