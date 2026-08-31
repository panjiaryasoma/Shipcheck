# Shipcheck Inspection Scope

**Status:** Implementation-aligned draft  
**Runtime version:** 0.6.0

Shipcheck is a bounded pre-submission inspector. It deliberately verifies less than an unrestricted CI runner or human judge so that its evidence claims remain defensible.

## Inputs

Required:

```text
rules_url
repository_url
```

Optional:

```text
deployment_url
submission_claims[]
```

## Rules scope

Shipcheck may:

- retrieve public HTTP(S) rules pages;
- reject local/private/non-routable targets;
- validate redirects before following them;
- bound response size and extracted text;
- use Google ADK + Gemini to extract explicit requirements;
- classify subjective rules as `MANUAL_REVIEW`;
- cache extraction results by rules URL plus source-content digest.

Shipcheck does not claim that every competition policy, FAQ, external document, or organizer interpretation is automatically discovered.

## Repository scope

The current inspector supports public GitHub repositories over HTTPS.

It may inspect bounded metadata, tree entries, selected source/configuration files, README content, dependency manifests, architecture content, framework markers, model configuration, container configuration, and other deliberately sampled evidence.

Current source/config sampling covers common Python, JavaScript/TypeScript, Go, Java, and Kotlin paths.

Shipcheck does not:

- authenticate into private repositories;
- exhaustively read every repository file;
- execute arbitrary repository code;
- treat fixture/test/report paths as production implementation evidence;
- treat a Dockerfile or deployment command as proof of a live cloud runtime.

## Reproduction scope

Automated reproduction evidence is static-only in the current MVP.

Shipcheck may verify:

- documented setup/run markers;
- supported dependency-manifest presence;
- repository artifacts already gathered by the bounded inspector.

Actual command execution remains `MANUAL_REVIEW` until an explicitly sandboxed execution path exists.

## Deployment scope

When a deployment URL is supplied, Shipcheck may:

- validate that the target is public;
- follow a bounded number of validated redirects;
- require a final reachable HTTP success response;
- retain a bounded textual response sample when available;
- recognize scoped Google Cloud runtime signals such as a valid Cloud Run hostname.

Reachability does not prove every backend component or every submission claim.

## Human-only scope

The following commonly remain manual unless explicit observable evidence is supplied and a bounded checker exists:

- entrant identity, age, and geography;
- originality and disclosure declarations;
- deadline/submission-form state;
- category selection when not evidenced in inspectable artifacts;
- demonstration-video existence and duration;
- subjective judging criteria;
- innovation quality;
- organizer-specific interpretations.

## Safety boundary

Shipcheck favors abstention over fabricated certainty.

```text
not observed != false
not checkable != passed
configuration != live runtime
model interpretation != final verdict
```
