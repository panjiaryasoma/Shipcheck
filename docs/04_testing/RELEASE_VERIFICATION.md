# Shipcheck Release Verification

**Status:** Pre-freeze checklist. No release freeze is implied by this document.  
**Runtime version:** 0.6.0

This checklist defines what should be captured before a final submission freeze. Results belong in `reports/`; they are not pre-filled here.

## Static verification

```text
[ ] uv run ruff check .
[ ] uv run pytest
[ ] git status --short is reviewed
[ ] README quick start matches the current runtime
[ ] .env remains untracked
[ ] .dockerignore excludes local secrets and caches
```

## Live rules verification

```text
[ ] public rules URL is fetched successfully
[ ] ADK extraction completes
[ ] actual Gemini model is recorded
[ ] fallback state is recorded
[ ] extracted source quotes are grounded
[ ] repeated run may use content-addressed cache without hiding source changes
```

## Repository verification

```text
[ ] public repository metadata/tree can be inspected
[ ] README setup evidence is detected
[ ] dependency-manifest evidence is detected
[ ] Google agent-framework evidence is detected when present
[ ] architecture evidence requires meaningful content
[ ] fixture/test/report paths do not become production evidence
```

## Deployment and cloud verification

```text
[ ] supplied deployment URL, if any, is validated and reachable
[ ] redirect targets are revalidated
[ ] configuration is not mislabeled as live runtime proof
[ ] Firestore audit write succeeds when persistence is enabled
[ ] Firestore evidence remains inspector-scoped for unrelated targets
[ ] Shipcheck self-inspection promotion is allowed only for the configured self repository
```

## Disposition verification

```text
[ ] CRITICAL finding -> HOLD
[ ] HIGH without CRITICAL -> NEEDS_REVIEW
[ ] MANUAL_REVIEW without CRITICAL -> NEEDS_REVIEW
[ ] fully clear inspected scope -> READY
```

## UI and report verification

```text
[ ] inspection form completes end to end
[ ] Evidence Register renders findings and provenance
[ ] model/fallback provenance is visible
[ ] final disposition is visible
[ ] Markdown export downloads from the completed report
[ ] exported Markdown preserves findings, actions, notes, timestamp, and version
```

## Evidence capture

Final verification outputs should be recorded under a versioned `reports/` directory. Do not fabricate or hand-edit a passing result to satisfy this checklist.
