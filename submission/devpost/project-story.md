# Shipcheck

**Not cleared until proven.**

## Inspiration

Software projects do not only fail because the code is broken. They also fail at the point of submission.

A required architecture diagram is missing. A README cannot reproduce the project. A deployment URL is unreachable. A submission claims a framework or model that the repository does not actually evidence. One mandatory rule is buried in a long rules page and gets overlooked five minutes before the deadline.

The frustrating part is that these failures are often discoverable before submission, but the evidence is scattered across rule pages, repositories, deployment state, documentation, and submission claims.

Shipcheck started from a simple question:

> **Can this submission prove that it satisfies the rules?**

The goal was not to build another chatbot that reads a rules page and produces advice. The goal was to build a preflight inspection workflow that turns rules into obligations, obligations into checks, checks into evidence, and evidence into a disposition.

## What it does

Shipcheck is an evidence-first preflight agent for software submissions.

A user provides:

1. a public competition or submission-rules URL;
2. a public GitHub repository;
3. an optional deployment URL; and
4. optional declared submission claims.

Shipcheck then interprets the rules, inspects bounded repository and runtime evidence, checks claims, preserves requirements that still need human judgment, and returns one of three dispositions:

- `READY`
- `NEEDS_REVIEW`
- `HOLD`

The result is presented as an Evidence Register rather than a conversational answer. Each finding contains the requirement, evidence status, severity, observed evidence, reasoning, and a recommended action when remediation is needed.

A `READY` result is deliberately scoped. It means Shipcheck found no unresolved `CRITICAL`, `HIGH`, or `MANUAL_REVIEW` gate within the evidence it could inspect. It does not claim guaranteed eligibility, organizer acceptance, or competition success.

## How we built it

Shipcheck uses a hybrid agentic architecture.

The semantic part of the workflow is handled by a **Google ADK rules agent** using Gemini structured output. The agent retrieves the supplied public rules page through a bounded fetch path and converts explicit language into structured requirements.

The rest of the inspection remains deterministic application logic around the agent:

- a bounded public GitHub inspector gathers metadata, repository-tree entries, and selected source/configuration/documentation files;
- a static reproduction checker looks for safely observable setup and dependency evidence without executing arbitrary repository code;
- an optional deployment verifier checks public reachability and bounded runtime evidence;
- an evidence mapper connects structured requirements to concrete repository/runtime observations;
- a claim checker distinguishes unsupported claims from direct contradictions;
- a deterministic disposition engine produces `READY`, `NEEDS_REVIEW`, or `HOLD`;
- optional Google Cloud Firestore persistence stores structured inspection audit records.

This boundary is intentional. Gemini is useful for interpreting natural-language rules, but a model response should not be allowed to manufacture compliance evidence or independently decide that a project is safe to submit.

### End-to-end inspection flow

![Shipcheck end-to-end inspection flow](../../docs/05_arch/E2E_Diagram.png)

The pipeline fans out after input preparation. Rules interpretation, repository evidence, deployment evidence, reproduction checks, and declared-claim checks become separate evidence channels. They converge before the final disposition.

### Operational flow

![Shipcheck operational flowchart](../../docs/05_arch/Flowchart.png)

The operational flow shows one inspection from input validation through model fallback, source-quote grounding, repository/runtime inspection, evidence classification, disposition, reporting, and optional Firestore persistence.

### Architecture

![Shipcheck runtime architecture](../../docs/05_arch/Architecture.png)

The architecture keeps one ADK agent surrounded by bounded deterministic services. This gives the agent a real job without pretending every HTTP request, repository check, or risk decision is somehow an LLM tool call.

## Gemini and source grounding

Rules extraction is not accepted merely because Gemini returns valid JSON.

For uncached extraction, Shipcheck validates each extracted `source_quote` against the fetched rules text. Formatting-only differences such as smart quotes, Unicode dashes, HTML entities, and whitespace normalization are tolerated, while invented or paraphrased evidence is rejected.

The inspector uses an explicit model chain configured through the environment. The default configuration currently includes Gemini 3.7 Flash with Gemini 3.6 Flash and Gemini 3.5 Flash as bounded fallbacks.

The report records the model that actually completed the extraction and whether fallback was used.

## Evidence is not the same as a claim

One of the core design decisions was to separate missing proof from contradiction.

If a project claims it uses Google ADK and Shipcheck cannot find supporting evidence, that is an `UNVERIFIED` claim. It is not automatically a contradiction.

If the project claims one model while observable configuration explicitly points to a conflicting model, that can become `CONTRADICTED`.

Likewise, configuration is not runtime proof. A Dockerfile or deployment command can show intent, but it does not prove a service is live.

This distinction makes the report less dramatic, but much more useful.

## Google Cloud integration

Shipcheck uses **Google Cloud Firestore** for optional inspection audit persistence.

A persisted inspection stores structured report data under the inspection ID. The cloud evidence is explicitly scoped so Shipcheck cannot use its own infrastructure to falsely prove that an unrelated inspected repository uses Google Cloud.

During configured Shipcheck self-inspection, the Firestore operation may be promoted into target-project evidence only when the inspected repository matches the configured self-repository URL. For any unrelated project, it remains inspector-runtime evidence only.

This boundary became important because an inspector that checks evidence should not quietly contaminate the evidence it is trying to inspect.

## Challenges we ran into

### Natural-language rules are not clean specifications

Hackathon rules mix mandatory technical requirements, eligibility statements, judging criteria, examples, recommendations, legal language, and subjective requirements on the same page.

Trying to treat all of that as machine-verifiable produced bad results. Shipcheck therefore classifies requirements into checkable, manual-review, and informational categories instead of forcing everything through one automated pass/fail path.

### Model output needed its own evidence discipline

Structured output solved formatting, not truthfulness. A model could still return a plausible quote that was not actually present in the source.

We added source-quote grounding, normalization for harmless formatting differences, bounded fallback behavior, and explicit failure when extraction cannot be grounded.

### Repository evidence was easy to overclaim

A filename such as `architecture.png` is not automatically proof of a valid architecture diagram. A Dockerfile is not automatically proof of live Cloud Run. A README sentence is not automatically proof that the underlying implementation exists.

The repository inspection rules became more conservative as the project hardened.

### Missing evidence is not contradiction

Early claim logic risked treating "not found" as "false." That is too strong. The final evidence contract separates `UNVERIFIED`, `MISSING`, and `CONTRADICTED` so uncertainty remains visible.

### The inspector itself can contaminate evidence

Firestore created a subtle problem. Shipcheck genuinely uses Google Cloud, but that fact should not allow every inspected project to satisfy a Google Cloud requirement.

We added an explicit inspector/target evidence boundary and only allow self-generated Firestore evidence to count for Shipcheck itself under configured self-inspection.

### Arbitrary reproduction is unsafe

A submission reviewer might want to prove that another repository's setup commands actually work, but blindly executing untrusted repositories is not appropriate for this prototype.

Shipcheck therefore performs bounded static reproduction checks and leaves arbitrary command execution as `MANUAL_REVIEW` until a deliberately sandboxed runner exists.

## Accomplishments that we're proud of

The part we are most proud of is that Shipcheck does not pretend the LLM is an oracle.

The project combines:

- Google ADK + Gemini rules interpretation;
- grounded source quotes;
- bounded public repository inspection;
- multi-language source/config sampling;
- static reproduction evidence;
- optional deployment verification;
- explicit claim and contradiction semantics;
- deterministic severity and disposition rules;
- a non-chat Evidence Register interface;
- Markdown report export;
- optional Google Cloud Firestore audit persistence;
- unit, integration, and acceptance test coverage;
- deliberately broken and compliant fixtures for deterministic behavior checks.

The application can inspect its own submission materials, which is appropriately circular for a project whose job is to ask whether a project is actually ready to ship.

## What we learned

The biggest lesson was that **rule interpretation and compliance verification are different problems**.

An LLM can interpret language well, but verification needs observable evidence and conservative semantics. A repository artifact can support a claim without proving runtime behavior. A missing artifact can be a blocker without proving dishonesty. A human-only requirement can remain unresolved without being treated as system failure.

We also learned that agentic design does not require turning every function into an agent. Giving one agent a narrow semantic responsibility and surrounding it with deterministic services made the system easier to test, easier to reason about, and harder to fool with its own assumptions.

## What's next

Shipcheck is still a hackathon prototype.

The next steps would be to add a deliberately sandboxed reproduction runner, richer rule-source support for JavaScript-heavy pages and attached documents, authenticated private-repository inspection, stronger deployment provenance, CI integration, and reusable competition-specific evidence adapters.

A longer-term version could act as a pre-submission gate for hackathons, grants, coursework, open-source releases, or any workflow where the question is not merely "does it work?" but "can you prove it meets the submission contract?"

## Built with

- Python 3.12
- Google ADK
- Gemini through the Google Gen AI SDK
- FastAPI
- httpx
- Beautiful Soup
- Google Cloud Firestore
- HTML / CSS / vanilla JavaScript
- Pydantic
- uv
- pytest
- Ruff
- Docker
- GitHub

---

**Shipcheck**  
*Autonomous preflight for software submissions.*  
**Not cleared until proven.**
