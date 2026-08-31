# Shipcheck Cloud Evidence Boundary

**Status:** Implementation-aligned draft  
**Runtime version:** 0.6.0

This contract prevents Shipcheck's own infrastructure from contaminating evidence about the project being inspected.

## 1. Two evidence subjects

Shipcheck can observe evidence about two different subjects:

```text
A. inspector runtime
   infrastructure used by Shipcheck itself

B. target project
   repository/deployment currently being inspected
```

These subjects must remain separate by default.

## 2. Firestore audit persistence

When enabled, Shipcheck persists structured inspection records to Google Cloud Firestore using Application Default Credentials.

A successful write proves that **Shipcheck** performed a Firestore operation. Its default provenance is therefore:

```text
scope = inspector_runtime
```

It does not prove that an unrelated inspected repository uses Google Cloud.

## 3. Self-inspection exception

A Shipcheck Firestore operation may be promoted into target-project evidence only when all of the following are true:

1. Firestore persistence is enabled and the operation succeeds;
2. the inspected repository is Shipcheck itself;
3. the repository URL matches the explicitly configured `SHIPCHECK_SELF_REPOSITORY_URL`.

Expected configuration:

```dotenv
SHIPCHECK_SELF_REPOSITORY_URL=https://github.com/panjiaryasoma/Shipcheck
```

This exception is narrow by design because, during self-inspection, the inspector runtime and target project are the same software system.

## 4. Configuration is not runtime proof

Repository evidence such as:

```text
Dockerfile
gcloud run deploy
*.run.app text
Cloud Run documentation
Firestore configuration
```

may show implementation or deployment intent, but must not automatically become proof of a live cloud operation.

A requirement that specifically asks for a live Google Cloud-hosted backend remains unresolved until Shipcheck observes applicable runtime evidence.

## 5. Video/submission proof remains separate

Even when Shipcheck verifies a cloud operation programmatically, a competition may separately require the demonstration video or submission materials to visually show Google Cloud Console, Cloud Run, logs, or another specific proof surface.

That requirement remains `MANUAL_REVIEW` unless Shipcheck has a bounded checker for the required submission artifact.

## 6. Design rule

```text
inspector evidence cannot satisfy target evidence
unless subject identity is explicitly proven
```

This rule is part of Shipcheck's evidence-integrity contract, not merely a deployment detail.
