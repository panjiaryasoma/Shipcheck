# Repository Structure

```text
shipcheck/
├── app/
│   ├── agent/
│   │   └── root_agent.py
│   ├── tools/
│   │   ├── rules.py
│   │   ├── repository.py
│   │   ├── reproduction.py
│   │   ├── deployment.py
│   │   ├── evidence.py
│   │   ├── contradiction.py
│   │   └── risk.py
│   ├── services/
│   │   └── inspection.py
│   ├── models/
│   │   └── schemas.py
│   ├── core/
│   │   └── config.py
│   ├── web/
│   │   ├── templates/
│   │   └── static/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
├── fixtures/
│   ├── rules/
│   └── repos/
├── docs/
├── reports/
├── submission/
├── pyproject.toml
├── .python-version
├── .env.example
├── Dockerfile
└── README.md
```

`agent/` owns orchestration, `tools/` owns bounded external actions, `services/`
connects application flow, and `models/` is the structured contract.

Tests and fixtures are first-class because Shipcheck itself is supposed to inspect
evidence. A hand-wavy demo would be particularly embarrassing here.
