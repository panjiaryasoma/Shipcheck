from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.rules_extraction import LiveRulesRequest
from app.services.inspection import inspect_fixture
from app.services.live_rules import AgentExtractionError, extract_requirements_with_adk
from app.tools.live_rules import RulesFetchError

app = FastAPI(
    title="Shipcheck",
    version="0.2.0",
    description="Autonomous preflight inspection for software submissions.",
)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
templates = Jinja2Templates(directory="app/web/templates")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "shipcheck", "version": "0.2.0"}


@app.get("/api/fixtures/{fixture_name}/inspect")
async def inspect_fixture_endpoint(fixture_name: str):
    if fixture_name not in {"broken", "compliant"}:
        raise HTTPException(status_code=404, detail="Unknown fixture.")

    report = inspect_fixture(
        rules_path=PROJECT_ROOT / "fixtures" / "rules" / "minimal_hackathon_rules.md",
        repository_path=PROJECT_ROOT / "fixtures" / "repos" / fixture_name,
    )
    return report.model_dump(mode="json")


@app.post("/api/rules/extract")
async def extract_rules_endpoint(payload: LiveRulesRequest):
    try:
        result = await extract_requirements_with_adk(str(payload.rules_url))
    except RulesFetchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AgentExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Live rules extraction failed: {type(exc).__name__}",
        ) from exc

    return result.model_dump(mode="json")
