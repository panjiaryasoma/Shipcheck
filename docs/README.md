# Shipcheck Documentation

Shipcheck documentation is organized by engineering concern rather than by implementation chronology.

```text
docs/
├── 01_problem/       # problem definition and scope
├── 02_product/       # product requirements and runtime contract
├── 03_evaluation/    # evidence, uncertainty, and decision semantics
├── 04_testing/       # acceptance and release-verification contracts
└── 05_arch/          # runtime architecture, repository structure, and diagrams
```

## 01_problem

- [`SHIPCHECK_PROBLEM_BRIEF_v0.1.md`](01_problem/SHIPCHECK_PROBLEM_BRIEF_v0.1.md) defines the user problem, product thesis, scope, non-goals, and original pre-production gate.

## 02_product

- [`SHIPCHECK_SIMPLE_PRD_v0.2.md`](02_product/SHIPCHECK_SIMPLE_PRD_v0.2.md) defines the implementation-aligned MVP contract, service boundaries, acceptance cases, and release gate.

## 03_evaluation

- [`EVIDENCE_DECISION_CONTRACT.md`](03_evaluation/EVIDENCE_DECISION_CONTRACT.md) defines requirement statuses, severity, uncertainty handling, and final disposition semantics.
- [`INSPECTION_SCOPE.md`](03_evaluation/INSPECTION_SCOPE.md) defines what Shipcheck may inspect automatically and what must remain unresolved or manual.
- [`CLOUD_EVIDENCE_BOUNDARY.md`](03_evaluation/CLOUD_EVIDENCE_BOUNDARY.md) defines the boundary between Shipcheck's own Google Cloud infrastructure and evidence about an inspected target project.

## 04_testing

- [`ACCEPTANCE_TESTS.md`](04_testing/ACCEPTANCE_TESTS.md) documents the behavioral acceptance contract and the executable coverage currently present in the repository.
- [`RELEASE_VERIFICATION.md`](04_testing/RELEASE_VERIFICATION.md) defines the final verification checklist without claiming results that have not actually been recorded.

## 05_arch

- [`SHIPCHECK_ARCHITECTURE_v0.1.md`](05_arch/SHIPCHECK_ARCHITECTURE_v0.1.md) documents the runtime topology and responsibility boundaries.
- [`SHIPCHECK_REPO_STRUCTURE_v0.1.md`](05_arch/SHIPCHECK_REPO_STRUCTURE_v0.1.md) documents repository ownership and layout.
- [`E2E_Diagram.png`](05_arch/E2E_Diagram.png) shows the end-to-end evidence pipeline.
- [`Flowchart.png`](05_arch/Flowchart.png) shows the operational inspection decision flow.
- [`Architecture.png`](05_arch/Architecture.png) shows the runtime component architecture.

## Documentation principle

`docs/` describes what Shipcheck is designed and required to do. Recorded runtime outputs and verification artifacts belong under [`reports/`](../reports/).
