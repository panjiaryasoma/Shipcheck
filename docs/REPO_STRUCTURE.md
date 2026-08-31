# Repository Structure

```text
shipcheck/
├── app/
│   ├── agent/
│   │   └── root_agent.py          # Google ADK rules agent
│   ├── core/
│   │   ├── config.py              # environment-backed settings
│   │   └── version.py             # runtime version single source of truth
│   ├── models/                    # structured contracts
│   ├── services/
│   │   ├── inspection.py          # end-to-end inspection orchestrator
│   │   ├── live_repository.py
│   │   └── live_rules.py
│   ├── storage/
│   │   └── firestore.py           # optional audit persistence
│   ├── tools/
│   │   ├── live_rules.py          # bounded public rules fetcher
│   │   ├── github_repo.py         # bounded public GitHub inspection
│   │   ├── reproduction.py        # bounded static reproduction checks
│   │   ├── deployment.py          # public deployment verification
│   │   ├── live_evidence.py       # requirement/evidence mapping
│   │   ├── contradiction.py       # declared-claim evidence checks
│   │   └── risk.py                # final disposition logic
│   ├── web/
│   │   ├── templates/
│   │   └── static/
│   │       ├── asset/
│   │       ├── css/
│   │       └── js/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
├── fixtures/
│   ├── rules/
│   └── repos/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROBLEM_BRIEF.md
│   ├── REPO_STRUCTURE.md
│   └── SIMPLE_PRD.md
├── reports/
├── scripts/
├── submission/
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
- `app/services/inspection.py` owns application orchestration.
- `app/tools/` owns bounded deterministic inspection operations.
- `app/models/` owns structured data contracts.
- `app/storage/` owns optional audit persistence.
- `app/web/` owns the non-chat inspection workspace.
- `tests/` and `fixtures/` are first-class evidence for deterministic behavior.

The agent does not directly own repository inspection, deployment verification,
claim checking, or risk disposition. Those operations remain isolated deterministic
services around the ADK rules agent.
