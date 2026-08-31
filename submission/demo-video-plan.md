# Shipcheck Demo Video Plan

Target: **under 4 minutes**  
Language: **English**  
Platform: **Public YouTube or Vimeo**  
Category: **Taskmaster**

The video must show Shipcheck performing a real inspection and must visibly demonstrate the Google Cloud infrastructure used by the project.

## Recording principle

Keep the proof-of-action segment continuous. Avoid edits that hide the live execution path. If playback speed is changed uniformly, disclose it on screen.

Do not claim a public hosted Shipcheck deployment unless one exists. The current Google Cloud integration to demonstrate is the Firestore-backed inspection audit path.

## Suggested timeline

### 0:00–0:25 — Problem

Opening line:

> A project can work perfectly and still fail at submission because the evidence is incomplete, contradictory, or buried across rules, repositories, and deployment state.

Show the Shipcheck interface and the final-disposition area.

### 0:25–0:45 — Value proposition

> Shipcheck is an evidence-first preflight agent. It reads submission rules, inspects the project, preserves uncertainty where automation cannot prove compliance, and returns READY, NEEDS_REVIEW, or HOLD.

Briefly show the Evidence Register.

### 0:45–1:05 — Architecture

Show `docs/05_arch/Architecture.png`.

Explain:

> Google ADK and Gemini handle natural-language rule interpretation. Repository inspection, reproduction checks, deployment verification, evidence mapping, claim checks, and the final disposition are bounded deterministic services around the agent. Google Cloud Firestore stores optional inspection audit records.

### 1:05–2:25 — Live proof of action

Use a real inspection.

Suggested input:

```text
Rules URL:
https://allthingsagentichackathon.devpost.com/rules

Repository:
https://github.com/panjiaryasoma/Shipcheck
```

Leave deployment blank unless a real public deployment is available.

Show, without hiding the execution:

1. the manifest inputs;
2. **Run preflight**;
3. the inspection progress/wait;
4. the resulting final disposition;
5. model provenance and fallback state;
6. at least two concrete requirement findings;
7. evidence paths/URLs and recommended action;
8. Markdown report download.

Important narrative point:

> The model interprets the rules, but it does not get to invent the final verdict. Every automated finding has to resolve through observable evidence and deterministic disposition rules.

### 2:25–3:05 — Google Cloud proof

Show Google Cloud Console and the Firestore database used by Shipcheck.

Use the inspection ID from the live run and show the corresponding audit document if persistence is enabled.

Narration:

> This inspection is also persisted as a structured audit record in Google Cloud Firestore. Shipcheck explicitly scopes this as inspector-runtime evidence so its own cloud infrastructure cannot falsely prove Google Cloud usage for unrelated repositories.

Do not expose credentials, API keys, access tokens, or private account information.

### 3:05–3:30 — Evidence contract

Show either the UI or `docs/03_evaluation/EVIDENCE_DECISION_CONTRACT.md`.

Explain the distinction:

```text
missing proof != direct contradiction
manual review != pass
configuration != live runtime proof
```

Then show:

```text
CRITICAL -> HOLD
HIGH / MANUAL_REVIEW -> NEEDS_REVIEW
no unresolved gate -> READY
```

### 3:30–3:50 — Reproducibility

Show the public GitHub repository, README quick start, and architecture diagram.

Mention that Shipcheck does not execute arbitrary third-party repositories; reproduction inspection is deliberately bounded and static in this prototype.

### 3:50–4:00 — Close

> Shipcheck turns submission rules into evidence-backed preflight checks, so the last question before shipping is not "I think it is ready." It is "can I prove it?" Shipcheck. Not cleared until proven.

## Required visual checklist

- Shipcheck UI
- live inspection execution
- resulting Evidence Register
- actual model provenance
- architecture diagram
- public GitHub repository
- README spin-up instructions
- Google Cloud Console
- Firestore inspection document or visibly successful cloud audit operation

## Do not show

- Gemini API key
- GitHub token
- Google credentials
- local `.env`
- private account identifiers that are not necessary for the demo
- fabricated hosted URLs or fabricated passing evidence

## After recording

1. Upload publicly to YouTube or Vimeo.
2. Confirm the video is no longer than four minutes.
3. Confirm English audio or English subtitles are present.
4. Replace the video `TODO` in `submission/devpost/links.md`.
5. Add the public video link to the Devpost submission form.
