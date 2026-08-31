# Shipcheck Submission Package

This directory contains working submission materials for **All Things Agentic Hackathon**.

**Category:** Taskmaster  
**Project:** Shipcheck  
**Status:** Working submission draft — not frozen

The official submission requires a category, project description, repository, architecture diagram, demonstration video, and supporting links. A hosted project URL is encouraged but optional. The demo video must be public on YouTube or Vimeo, no longer than four minutes, and must visibly demonstrate Google Cloud usage.

## Structure

```text
submission/
├── README.md
├── checklist.md
├── demo-video-plan.md
├── devpost/
│   ├── form-fields.md
│   ├── elevator-pitch.md
│   ├── project-story.md
│   ├── links.md
│   └── testing-instructions.md
└── screenshots/
    └── README.md
```

## Devpost working copy

- [`devpost/form-fields.md`](devpost/form-fields.md) contains paste-ready field text.
- [`devpost/elevator-pitch.md`](devpost/elevator-pitch.md) contains long, short, and one-line positioning.
- [`devpost/project-story.md`](devpost/project-story.md) contains the full narrative submission draft.
- [`devpost/testing-instructions.md`](devpost/testing-instructions.md) contains reproducible judge/testing instructions.
- [`devpost/links.md`](devpost/links.md) tracks required and supporting URLs without inventing missing external links.

The video workflow is tracked separately in [`demo-video-plan.md`](demo-video-plan.md), while [`checklist.md`](checklist.md) records official-submission completion state and entrant-only confirmations.

## Source-of-truth references

Submission claims must remain aligned with the implementation and evidence contracts in the repository:

- [`../README.md`](../README.md)
- [`../docs/README.md`](../docs/README.md)
- [`../docs/03_evaluation/EVIDENCE_DECISION_CONTRACT.md`](../docs/03_evaluation/EVIDENCE_DECISION_CONTRACT.md)
- [`../docs/03_evaluation/CLOUD_EVIDENCE_BOUNDARY.md`](../docs/03_evaluation/CLOUD_EVIDENCE_BOUNDARY.md)
- [`../docs/05_arch/SHIPCHECK_ARCHITECTURE_v0.1.md`](../docs/05_arch/SHIPCHECK_ARCHITECTURE_v0.1.md)

## Submission discipline

Do not claim a hosted deployment, passing release verification, public video, release tag, or Devpost URL until the corresponding artifact actually exists.

Google Cloud Firestore is the current Google Cloud infrastructure integration. Shipcheck's application service may be demonstrated locally, while the video should visibly show the Firestore-backed audit write and its resulting document in Google Cloud Console. This does not convert Shipcheck's own cloud usage into evidence for unrelated repositories.

No final freeze is implied by this directory. The submission package remains editable until explicit final approval.
