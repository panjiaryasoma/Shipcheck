# Shipcheck v01 Verification Artifacts

This directory is reserved for **recorded** verification outputs for Shipcheck's first formal project/report version.

`v01` is the report-set version. It is intentionally separate from the internal package/runtime version declared in `pyproject.toml`.

No passing result is implied by this README.

When final verification is approved, capture the real outputs of the relevant checks here. Suggested filenames:

```text
ruff.txt
pytest.txt
live_rules.json
live_repository.json
firestore_smoke.json
self_inspection.json
self_inspection.md
```

`self_inspection.md` should preferably come from the browser's actual Markdown export so the UI/reporting path is represented in addition to service-level smoke output.

Keep secrets, API keys, access tokens, and credential material out of every report artifact.
