# Shipcheck Inspection Report

> Final disposition: **NEEDS\_REVIEW**

## Inspection

- **Inspection ID:** `live-346be905ab`
- **Timestamp:** `2026-08-31T17:29:13.376637Z`
- **Agent version:** `0.6.0`
- **Rules source:** `https://allthingsagentichackathon.devpost.com/rules?_gl=1*1xdnglq*_gcl_au*MjIwMjQ5Njg1LjE3ODcxMjUwMjg.*_ga*MzYzMTc2MTMzLjE3ODcxMjUwMjg.*_ga_0YHJK3Y10M*czE3ODgxNTMyODIkbzMxJGcxJHQxNzg4MTU0ODE2JGoyNCRsMCRoMA..`
- **Repository:** `https://github.com/panjiaryasoma/Shipcheck`
- **Deployment:** Not provided
- **Inspector model:** `gemini-3.6-flash`
- **Fallback used:** No

## Summary

- **Passed:** 7
- **Manual review:** 13
- **High:** 0
- **Warnings:** 13
- **Critical:** 0

## Requirement Findings

### REQ-001 · MANUAL\_REVIEW

Entrants must be above the age of majority in their jurisdiction of residence (or at least 20 years old in Taiwan) at the time of entry.

- **Type:** MANUAL\_REVIEW
- **Severity:** WARNING

**Reason**

The extracted rule explicitly requires human or subjective judgment.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-002 · MANUAL\_REVIEW

Entrants must not be residents of Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, Russia, or any country subject to US export controls or OFAC sanctions.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

No bounded automated checker is available for this rule yet.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-003 · MANUAL\_REVIEW

Submissions must be submitted during the Submission Period, ending August 31, 2026 at 5:00 P.M. PT.

- **Type:** INFORMATIONAL
- **Severity:** WARNING

**Reason**

Submission timing or deadline requirements depend on current competition and submission-state evidence, which Shipcheck does not verify automatically.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-004 · VERIFIED

Projects must leverage Gemini 3.5 or newer accessed through the Gemini API or Vertex AI.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

Primary Gemini model gemini-3.7-flash satisfies the 3.5+ requirement.

**Evidence**

- **Source:** repository
  - Location: `.env.example`
  - Observed: gemini-3.7-flash

---

### REQ-005 · VERIFIED

Projects must use at least one Google Agent Framework: Google ADK, GenAI SDK, Antigravity SDK, or GenKit.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

Google ADK implementation evidence was found in the repository.

**Evidence**

- **Source:** repository
  - Location: `app/agent/root_agent.py`
  - Observed: from google.adk, google-adk, import google.adk

---

### REQ-006 · VERIFIED

Projects must utilize at least one Google Cloud infrastructure service (such as Cloud Run, Cloud SQL, Firestore, GKE, or Pub/Sub).

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

A live Google Cloud Firestore operation was verified. The inspector-runtime observation is accepted as target-project evidence only for this caller-established self-inspection scope.

**Evidence**

- **Source:** google\_cloud
  - Location: `projects/gen-lang-client-0594234746/databases/(default)/documents/shipcheck_inspections/live-346be905ab`
  - Observed: Verified firestore operation in project gen-lang-client-0594234746: HTTP 200 document write to Cloud Firestore; inspector-runtime observation accepted as target-project evidence only for the caller-established self-inspection scope

---

### REQ-007 · MANUAL\_REVIEW

Entrants must select one project category (Taskmaster, Collaborative Partner, or Fortified Enterprise Fleet) for their submission.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

No bounded automated checker is available for this rule yet.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-008 · MANUAL\_REVIEW

Projects must be newly created during the Submission Period, and any pre-existing code or work incorporated into the Project must be disclosed.

- **Type:** MANUAL\_REVIEW
- **Severity:** WARNING

**Reason**

Submission timing or deadline requirements depend on current competition and submission-state evidence, which Shipcheck does not verify automatically.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-009 · MANUAL\_REVIEW

Submissions must include a text description detailing features, functionality, technologies used, data sources, and findings/learnings.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

This mandatory rule cannot be proven from repository/runtime evidence alone.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-010 · VERIFIED

Submissions must include a URL to a public or private code repository on GitHub, GitLab, or Bitbucket.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

A public repository is available for inspection.

**Evidence**

- **Source:** repository
  - Location: `repository`
  - Observed: public repository

---

### REQ-011 · NOT\_APPLICABLE

If the code repository is private, access must be granted to testing@devpost.com and cloudhackathons@google.com.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

This rule applies only when the submitted code repository is private; the inspected repository is public.

**Evidence**

- None recorded.

---

### REQ-012 · VERIFIED

The repository must contain a README.md file with step-by-step instructions on setting up and running the project locally or deploying it to the cloud.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

README setup/run instructions were detected.

**Evidence**

- **Source:** repository
  - Location: `README.md`
  - Observed: uv sync, uv run

---

### REQ-013 · VERIFIED

Submissions must include an Architecture Diagram illustrating system components and connections.

- **Type:** CHECKABLE
- **Severity:** PASS

**Reason**

Architecture content with multiple system/flow signals was found.

**Evidence**

- **Source:** repository
  - Location: `docs/05_arch/SHIPCHECK_ARCHITECTURE_v0.1.md`
  - Observed: Architecture content contains multiple system/flow signals.

---

### REQ-014 · MANUAL\_REVIEW

Submissions must include a link to a demonstration video uploaded and publicly visible on YouTube or Vimeo.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

This mandatory rule cannot be proven from repository/runtime evidence alone.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-015 · MANUAL\_REVIEW

The demonstration video must not exceed 4 minutes in length.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

This mandatory rule cannot be proven from repository/runtime evidence alone.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-016 · MANUAL\_REVIEW

The demonstration video must visually demonstrate that the backend is running on Google Cloud.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

This mandatory rule cannot be proven from repository/runtime evidence alone.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-017 · MANUAL\_REVIEW

The demonstration video must be spoken in English or include English subtitles.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

This mandatory rule cannot be proven from repository/runtime evidence alone.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-018 · MANUAL\_REVIEW

The application must support English, and non-English submission materials must include an English translation.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

No bounded automated checker is available for this rule yet.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-019 · MANUAL\_REVIEW

Submissions must be the entrant's original work, solely owned by the entrant, and free of IP infringement.

- **Type:** MANUAL\_REVIEW
- **Severity:** WARNING

**Reason**

The extracted rule explicitly requires human or subjective judgment.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

---

### REQ-020 · MANUAL\_REVIEW

To be eligible for the Startup Excellence prize category, the entrant must submit on behalf of an incorporated organization and provide a corporate email address.

- **Type:** CHECKABLE
- **Severity:** WARNING

**Reason**

No bounded automated checker is available for this rule yet.

**Evidence**

- None recorded.

**Recommended action**

Review this requirement manually before submission.

## Inspection Notes

- Rules extraction loaded from content-addressed local cache.
- Repository tree contained 115 bounded file entries.
- Inspected 64 selected text files.
- Fixture/test paths are excluded from production evidence.
- Architecture filenames alone do not receive an automatic pass.
- Container configuration is not treated as proof of live Cloud Run deployment.
- GitHub REST is used only for metadata/tree; file bodies use the public raw host.
- Reproduction check documented\_setup: VERIFIED; README contains bounded setup/run markers. Evidence: README.md.
- Reproduction check dependency\_manifest: VERIFIED; At least one dependency manifest is present. Evidence: pyproject.toml.
- Reproduction check command\_execution: MANUAL\_REVIEW; Untrusted repository commands were not executed; runtime reproduction remains manual unless a future sandboxed checker is explicitly enabled. Evidence: no executable evidence.
- READY means ready within the evidence Shipcheck could inspect.
- Persisted this live inspection as an audit record in Google Cloud Firestore.
- The Firestore operation is eligible as target-project evidence because the inspected repository matches SHIPCHECK\_SELF\_REPOSITORY\_URL.

---

Generated by Shipcheck. READY means ready within the evidence Shipcheck could inspect.
