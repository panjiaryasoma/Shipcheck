# Devpost Form Fields

Paste-ready working copy for the All Things Agentic Hackathon submission form.

## Project name

**Shipcheck**

## Category

**Taskmaster**

## Tagline

**Not cleared until proven.**

## Elevator pitch

Shipcheck is an evidence-first preflight agent that reads submission rules, inspects a software project, and tells builders what is proven, what is missing, and what still needs human review before they ship.

## Repository

https://github.com/panjiaryasoma/Shipcheck

## Hosted project

TODO — add only if a real public hosted application is available. Otherwise leave the hosted-project field unused if Devpost permits it.

## Demo video

TODO — public YouTube or Vimeo URL, maximum four minutes.

## Architecture diagram

https://github.com/panjiaryasoma/Shipcheck/blob/main/docs/05_arch/Architecture.png

## Features and functionality

Shipcheck accepts a public rules URL, public GitHub repository, optional deployment URL, and optional declared submission claims. A Google ADK rules agent uses Gemini structured output to turn explicit rules into typed requirements. Bounded deterministic services then inspect repository evidence, static reproduction signals, optional deployment evidence, framework/model configuration, architecture artifacts, and declared claims. Findings are resolved into traceable evidence statuses and severity levels before a deterministic disposition engine returns `READY`, `NEEDS_REVIEW`, or `HOLD`.

The web interface presents the result as an Evidence Register with requirement-level evidence, reasoning, recommended actions, model provenance, and Markdown report export. Optional Google Cloud Firestore persistence stores structured inspection audit records.

## Technologies used

- Python 3.12
- Google ADK
- Gemini through the Google Gen AI SDK
- FastAPI
- Google Cloud Firestore
- httpx
- Beautiful Soup
- Pydantic
- HTML / CSS / vanilla JavaScript
- uv
- pytest
- Ruff
- Docker
- GitHub

## Google technology requirement mapping

**Gemini:** Gemini 3.5 or newer through the Gemini API / Google Gen AI SDK. The configured model chain currently includes Gemini 3.7 Flash with Gemini 3.6 Flash and Gemini 3.5 Flash fallbacks.

**Google agent framework:** Google ADK is used for natural-language rules interpretation.

**Google Cloud infrastructure:** Google Cloud Firestore is used for optional structured inspection audit persistence.

## Data sources

Shipcheck does not train on a proprietary dataset. Its primary external input is the public submission/rules page supplied by the user. It also inspects public GitHub repository metadata, repository trees, and bounded selected public file contents. When a deployment URL is provided, Shipcheck may inspect bounded public reachability/runtime evidence.

The system does not treat its own cache or Firestore audit data as external truth about unrelated target projects.

## Findings and learnings

The central engineering lesson was that rule interpretation and compliance verification are different problems. Gemini is useful for translating messy natural-language rules into structured requirements, but compliance claims need observable evidence and conservative semantics.

During development we found several places where a superficially convenient implementation could overclaim: a plausible model quote was not necessarily present in the source, an architecture filename did not prove meaningful architecture content, a Dockerfile did not prove a live deployment, missing evidence did not prove contradiction, and Shipcheck's own Firestore usage could not be allowed to satisfy Google Cloud requirements for arbitrary repositories.

Those failures shaped the final architecture: grounded rules extraction, bounded inspection, explicit uncertainty, deterministic evidence mapping, and a strict inspector/target evidence boundary.

## Reproducibility / spin-up instructions

https://github.com/panjiaryasoma/Shipcheck#quick-start

## Testing instructions

https://github.com/panjiaryasoma/Shipcheck/blob/main/submission/devpost/testing-instructions.md

## Full project story

https://github.com/panjiaryasoma/Shipcheck/blob/main/submission/devpost/project-story.md

## Final fields still requiring external completion

- public YouTube/Vimeo demo URL;
- hosted-project URL, only if one exists;
- final Devpost public project URL after publication;
- entrant eligibility / ownership / new-project declarations;
- optional final release tag after explicit final approval.
