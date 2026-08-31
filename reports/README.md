# Shipcheck Reports

`reports/` contains recorded outputs from actual verification runs.

It is intentionally separate from [`docs/`](../docs/):

```text
docs/     -> contracts, architecture, methodology, intended behavior
reports/  -> observed outputs and verification evidence
```

## Versioned reports

Runtime v0.6.x verification artifacts belong under [`v06/`](v06/).

Expected artifact types may include:

```text
ruff.txt
pytest.txt
live_rules.json
live_repository.json
firestore_smoke.json
self_inspection.json
self_inspection.md
```

Files should only be added when the corresponding command or UI workflow has actually been run. Do not create synthetic passing reports merely to fill the directory.

## Provenance

A report should make its origin obvious from either the file contents or accompanying notes. Useful provenance includes:

- runtime version;
- timestamp;
- rules URL;
- inspected repository;
- deployment URL when supplied;
- actual Gemini model and fallback state;
- inspection ID;
- command used to generate the artifact.

## Release use

The final pre-submission evidence set should be captured only after the release-verification checklist is explicitly approved and run. This directory existing does not mean the project is frozen.
