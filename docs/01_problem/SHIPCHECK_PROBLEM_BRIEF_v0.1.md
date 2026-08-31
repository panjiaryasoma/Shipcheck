# SHIPCHECK — PROBLEM BRIEF

**Version:** 0.1  
**Status:** Scope Lock Draft  
**Project:** Shipcheck  
**Hackathon:** All Things Agentic Hackathon  
**Primary Track:** Taskmaster  
**Date:** 30 August 2026

---

## 1. Problem Summary

Software submissions can fail even when the underlying project works.

The failure may happen because a required artifact is missing, a README cannot reproduce the project, a deployment is unreachable, a submission claim is not supported by repository evidence, or one mandatory rule is overlooked.

These failures are easy to miss because submission requirements are usually spread across rule pages, FAQs, README files, repository contents, deployment environments, and final submission forms.

The problem is therefore not only:

> “Does the software work?”

It is also:

> “Can the submission prove that it satisfies the rules?”

---

## 2. Core Problem Statement

> How can a builder verify, before submission, that a software project is reproducible, evidence-backed, internally consistent, and compliant with the requirements that can be checked automatically?

Shipcheck is intended to act as a preflight inspection layer between a finished project and the final submission button.

---

## 3. Primary User

The primary user is a developer or hackathon participant preparing a software project for a rule-bound submission.

The user may already have:

- a public GitHub repository;
- a deployed application;
- a README;
- architecture documentation;
- a project description;
- a set of competition rules.

The user does not need another generic project-management assistant. The user needs an inspection result.

---

## 4. User Situation

A typical user believes a project is ready to submit.

However, the project may still contain failures such as:

- a required architecture diagram is missing;
- the README references a command that does not work;
- the deployed service is unreachable;
- the submission claims Gemini 3.5 while the repository uses a different model;
- a required framework is not evidenced in the codebase;
- an important deliverable exists but cannot be traced to a requirement;
- the project is technically functional but lacks proof for a mandatory rule.

The user needs to know which failures can block submission and which issues are merely lower-priority improvements.

---

## 5. Current User Workaround

Without Shipcheck, users usually rely on some combination of:

- manually rereading the competition rules;
- maintaining a checklist;
- searching the repository by hand;
- asking teammates to review deliverables;
- testing deployment manually;
- rereading the README;
- comparing submission claims against code;
- discovering missing evidence at the last minute.

This workflow is fragmented and error-prone.

Shipcheck does not assume that every failed submission is caused by compliance mistakes. It only targets the subset of failures that can be discovered through structured inspection.

---

## 6. Product Opportunity

Shipcheck turns rule-bound submission review into an agentic inspection workflow.

The user provides:

```text
Competition / rules URL
+
Public GitHub repository
+
Optional deployed application URL
```

Shipcheck then:

```text
reads requirements
        ↓
extracts checkable obligations
        ↓
inspects repository artifacts
        ↓
runs reproducibility checks
        ↓
verifies deployment
        ↓
maps requirements to evidence
        ↓
detects contradictions
        ↓
prioritizes blockers
        ↓
produces a final disposition
```

The primary output is not a conversational answer.

It is an inspection report.

---

## 7. Product Thesis

> **A submission should be inspected before it is shipped.**

Software competitions often evaluate not only whether a project exists, but whether the participant can demonstrate that required technologies, artifacts, deployment, documentation, and claims are actually present.

Rules can therefore be treated as a set of inspectable obligations.

Repository files, runtime behavior, deployment state, and documentation become evidence.

Shipcheck connects the two.

---

## 8. Core Interaction

```text
User enters rules URL
        +
GitHub repository
        +
optional deployment URL
        ↓
RUN INSPECTION
        ↓
Shipcheck agent extracts requirements
        ↓
Shipcheck calls inspection tools
        ↓
Evidence is collected
        ↓
Claims and requirements are cross-checked
        ↓
Final report
```

Example output:

```text
FINAL DISPOSITION

HOLD
NOT CLEARED TO SHIP

CRITICAL
- Architecture evidence missing
- Claimed model does not match repository evidence

HIGH
- README reproduction incomplete

PASSED
- Repository reachable
- Build configuration found
- Google Cloud deployment reachable
- Required agent framework detected
```

---

## 9. Agentic Role

Shipcheck is designed as one agent with scoped tools.

The agent is responsible for:

1. interpreting submission requirements;
2. deciding which checks are relevant;
3. selecting the appropriate tools;
4. collecting evidence;
5. reconciling rules, claims, artifacts, and runtime state;
6. ranking findings by severity;
7. producing the final inspection disposition.

The agent should not invent evidence when a requirement cannot be verified.

Unknown or ambiguous conditions must remain unresolved.

---

## 10. Proposed Tool Boundary

### Rules Tool
Extracts explicit requirements from rule or FAQ pages.

### Repository Inspector
Finds implementation evidence such as dependencies, framework usage, configuration, documentation, tests, diagrams, and deployment artifacts.

### Reproduction Checker
Executes or validates documented setup / build / test commands where safely supported.

### Deployment Verifier
Checks whether the supplied deployed service is reachable and returns expected responses.

### Evidence Mapper
Links each checkable requirement to supporting or missing evidence.

### Contradiction Detector
Finds mismatches between claims and observed evidence.

### Risk Planner
Classifies findings into blocker, high-risk, warning, or pass states and recommends remediation order.

---

## 11. Key Differentiator

Shipcheck is not a checklist generator.

The differentiating workflow is:

> **rule → check → evidence → contradiction → disposition**

A checklist can say:

> “Architecture diagram required.”

Shipcheck should instead be able to say:

```text
Requirement:
Architecture diagram required.

Inspection:
No matching architecture artifact found.

Evidence:
README.md contains no architecture section.
docs/ contains no diagram file.

Verdict:
MISSING EVIDENCE

Severity:
CRITICAL
```

Likewise:

```text
Submission claim:
Uses Gemini 3.5.

Observed repository evidence:
gemini-2.5-flash

Verdict:
CLAIM CONTRADICTION
```

---

## 12. MVP Scope

### P0 — Must Have

1. Accept a rules / competition URL.
2. Accept a public GitHub repository.
3. Accept an optional deployed-app URL.
4. Extract explicit, checkable requirements.
5. Inspect repository structure and key files.
6. Detect required implementation evidence.
7. Perform basic reproducibility checks.
8. Verify deployment reachability when provided.
9. Map requirements to evidence.
10. Detect unsupported or contradictory claims.
11. Rank findings by severity.
12. Produce `READY` or `HOLD / BLOCKED` disposition.
13. Produce recommended next actions.
14. Show an inspectable report in the web interface.
15. Run on Google Cloud infrastructure required by the hackathon.

### P1 — Only If P0 Is Stable

- automatic GitHub Issue creation;
- generated `SUBMISSION_EVIDENCE.md`;
- deadline-aware remediation ordering;
- exportable inspection report.

---

## 13. Explicit Non-Goals

Shipcheck v0.1 is not:

- a project-management suite;
- a generic coding assistant;
- a chatbot for hackathon advice;
- a multi-agent platform;
- a replacement for judges;
- a guarantee of eligibility;
- a guarantee of acceptance or winning;
- an automated legal-compliance system;
- a security audit platform;
- a code-quality scoring service;
- a private-repository management platform;
- a team collaboration system.

The MVP does not require:

- authentication;
- user accounts;
- database history;
- vector database;
- Slack or email integration;
- browser extension;
- analytics dashboard.

---

## 14. Claim Boundary

Shipcheck can verify only what its tools can observe.

It must not claim:

> “This project is guaranteed to satisfy every competition rule.”

Preferred framing:

> “Shipcheck found no unresolved blockers among the requirements and evidence it was able to inspect.”

A `READY` result therefore means:

```text
No unresolved blocker was found
within the inspected scope.
```

It does not mean:

```text
Guaranteed valid submission.
Guaranteed judge acceptance.
Guaranteed eligibility.
```

---

## 15. Failure and Abstention Behavior

Shipcheck should not fabricate certainty.

Examples:

### Rule cannot be interpreted confidently

```text
STATUS: NEEDS REVIEW
Reason: Requirement language is ambiguous.
```

### Repository evidence is inaccessible

```text
STATUS: UNVERIFIED
Reason: Required artifact could not be inspected.
```

### Deployment URL is unavailable

```text
STATUS: BLOCKER
Reason: Runtime evidence could not be confirmed.
```

### Requirement requires human judgment

```text
STATUS: MANUAL REVIEW
Reason: Requirement is not machine-verifiable.
```

---

## 16. Success Criteria

The MVP is successful if:

### Product
- a user can submit a rules URL and repository;
- the system returns a structured inspection report;
- the result clearly distinguishes passes, blockers, contradictions, and unknowns;
- a user can understand the next action without reading raw agent logs.

### Agent
- the agent uses tools to gather evidence;
- the agent does not rely only on language-model reasoning;
- materially different findings produce different remediation priorities;
- missing evidence is never silently treated as a pass.

### Engineering
- the system runs end-to-end on the required Google stack;
- the deployed service is reproducible from the repository;
- core inspection tools have deterministic or bounded behavior where possible;
- intentionally broken fixture repositories trigger expected findings.

### Demo
The demo can show:

```text
broken submission
        ↓
Shipcheck inspection
        ↓
specific blocker found
        ↓
evidence shown
        ↓
issue fixed
        ↓
rerun
        ↓
READY / CLEARED
```

---

## 17. Primary Risks

### Risk 1 — Rule extraction becomes too broad
Natural-language rules may contain subjective judging criteria that cannot be converted into deterministic checks.

**Mitigation:** classify requirements as `CHECKABLE`, `MANUAL_REVIEW`, or `INFORMATIONAL`.

### Risk 2 — Agent hallucinates compliance
The model may infer that a requirement is satisfied without evidence.

**Mitigation:** every automated pass must point to explicit evidence.

### Risk 3 — Repository execution is unsafe or too expensive
Blindly executing arbitrary repositories is inappropriate for a fast hackathon MVP.

**Mitigation:** constrain reproducibility checks to a safe, bounded set and clearly mark unsupported execution paths.

### Risk 4 — Product becomes a generic AI reviewer
If output is only prose, Shipcheck loses its differentiator.

**Mitigation:** enforce structured requirement/evidence/finding objects and a final disposition.

### Risk 5 — Scope grows into full CI/CD
The project could easily expand into CI pipelines, security analysis, release management, or enterprise governance.

**Mitigation:** v0.1 remains strictly focused on pre-submission inspection.

---

## 18. Current Assumptions

### Reasonably Supported

- software submissions contain explicit requirements that can often be extracted from rule pages;
- repository and deployment artifacts can provide evidence for some requirements;
- missing or contradictory evidence can be discovered automatically;
- late-stage manual checking is vulnerable to human oversight.

### Still Assumptions

- users will trust an agentic preflight report enough to change their submission;
- a useful percentage of hackathon requirements can be machine-verified;
- the inspection can finish quickly enough for an interactive workflow;
- the severity ranking will match user expectations.

These remain validation debt.

---

## 19. Scope Decision

Shipcheck v0.1 will be built as:

> **An autonomous preflight agent that turns software-submission rules into inspectable checks, verifies repository and deployment evidence, detects contradictions, and blocks shipment when critical evidence is missing.**

The product remains intentionally narrow:

```text
ONE RULESET
ONE REPOSITORY
ONE INSPECTION
ONE DISPOSITION
```

---

## 20. Problem Brief Gate

| Question | Status |
|---|---|
| Problem is specific? | PASS |
| Primary user is clear? | PASS |
| Agentic workflow is necessary? | PASS |
| Core input/output is clear? | PASS |
| Differentiator is explicit? | PASS |
| Scope is realistic for a hackathon sprint? | PASS |
| Non-goals are strict? | PASS |
| Claim boundary is defined? | PASS |
| Tool contracts are fully specified? | PENDING |
| Fixture evaluation cases are defined? | PENDING |
| Architecture is locked? | PENDING |

### Gate Decision

**PASS TO SIMPLE PRD + ARCHITECTURE LOCK**

Production implementation should begin only after the P0 tool contracts, architecture, and a minimal set of expected inspection cases are locked.
