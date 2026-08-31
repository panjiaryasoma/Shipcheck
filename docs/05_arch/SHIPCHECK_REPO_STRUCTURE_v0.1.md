# Shipcheck Repository Structure

```text
Shipcheck/
├── app/
│   ├── agent/                     # Google ADK rules agent
│   ├── core/                      # runtime settings + version
│   ├── models/                    # structured inspection contracts
│   ├── services/                  # orchestration services
│   ├── storage/                   # optional Firestore persistence
│   ├── tools/                     # bounded deterministic inspection operations
│   ├── web/                       # templates, CSS, JS, brand assets
│   └── main.py                    # FastAPI application
├── docs/
│   ├── README.md
│   ├── 01_problem/
│   │   └── SHIPCHECK_PROBLEM_BRIEF_v0.1.md
│   ├── 02_product/
│   │   └── SHIPCHECK_SIMPLE_PRD_v0.2.md
│   ├── 03_evaluation/
│   │   ├── EVIDENCE_DECISION_CONTRACT.md
│   │   ├── INSPECTION_SCOPE.md
│   │   └── CLOUD_EVIDENCE_BOUNDARY.md
│   ├── 04_testing/
│   │   ├── ACCEPTANCE_TESTS.md
│   │   └── RELEASE_VERIFICATION.md
│   └── 05_arch/
│       ├── SHIPCHECK_ARCHITECTURE_v0.1.md
│       ├── SHIPCHECK_REPO_STRUCTURE_v0.1.md
│       ├── E2E_Diagram.png
│       ├── Flowchart.png
│       └── Architecture.png
├── fixtures/                      # deterministic rules/repository fixtures
├── reports/
│   ├── README.md
│   └── v01/                       # first formal verification report set
├── scripts/                       # live smoke utilities
├── submission/                    # submission-specific materials
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Ownership

- `app/agent/` owns natural-language rules interpretation through Google ADK.
- `app/services/inspection.py` owns end-to-end application orchestration.
- `app/tools/` owns bounded deterministic inspection operations.
- `app/models/` owns structured data contracts.
- `app/storage/` owns optional audit persistence.
- `app/web/` owns the inspection workspace and browser-side report export.
- `docs/` owns design intent, contracts, architecture, and verification methodology.
- `reports/` owns recorded outputs from actual verification runs.
- `tests/` and `fixtures/` are first-class evidence for deterministic behavior.

The ADK agent does not directly own repository inspection, deployment verification, claim checking, or final risk disposition. Those operations remain isolated deterministic services around the rules agent.
