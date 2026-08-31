# All Things Agentic Submission Checklist

Project: **Shipcheck**  
Category: **Taskmaster**  
Status: **Working checklist — not frozen**

This checklist separates repository-verifiable items from entrant declarations and final external submission steps.

## Core technology

- [x] Gemini 3.5 or newer is configured in the Shipcheck inspector model chain.
- [x] Google ADK is used for natural-language rules interpretation.
- [x] Google Cloud infrastructure is integrated through Firestore audit persistence.
- [x] The public repository documents the Google Cloud evidence boundary.

## Project and repository

- [x] Public GitHub repository is available.
- [x] README contains step-by-step local spin-up instructions.
- [x] Architecture diagram is present.
- [x] End-to-end flow diagram is present.
- [x] Operational flowchart is present.
- [x] English-language documentation is available.
- [x] Source code and submission description identify the main technologies used.
- [x] Bounded reproduction behavior is documented instead of claiming arbitrary code execution.

## Devpost text submission

- [x] Elevator pitch drafted.
- [x] Project story drafted.
- [x] Testing instructions drafted.
- [x] Technical/reference links sheet drafted.
- [ ] Copy final text into the Devpost form and re-check formatting.
- [ ] Select **Taskmaster** on the Devpost submission form.

## Demo video

- [x] Four-minute video plan drafted.
- [ ] Record the final demonstration.
- [ ] Show a real Shipcheck inspection in action.
- [ ] Show the architecture clearly.
- [ ] Show visible Google Cloud evidence in the video.
- [ ] Verify no credential or secret appears on screen.
- [ ] Keep the final video at or under four minutes.
- [ ] Provide English audio or English subtitles.
- [ ] Upload publicly to YouTube or Vimeo.
- [ ] Add the public video URL to Devpost and `submission/devpost/links.md`.

## Hosted project

- [ ] Add a hosted-project URL only if a real public hosted application is available.

A hosted project is encouraged but should not be fabricated. The local application plus documented spin-up path remains the current reproducible testing path unless a public deployment is created.

## Verification reports

- [ ] Run final Ruff verification and record the real output under `reports/v01/`.
- [ ] Run the final pytest suite and record the real output under `reports/v01/`.
- [ ] Run live rules smoke verification and record the real output.
- [ ] Run live repository smoke verification and record the real output.
- [ ] Run Firestore smoke verification and record the real output.
- [ ] Run final Shipcheck self-inspection and record JSON output.
- [ ] Export the final browser Markdown report and store it under `reports/v01/`.

No passing report should be created synthetically.

## Entrant declarations requiring human confirmation

- [ ] Confirm Shipcheck was newly created during the hackathon submission period.
- [ ] Confirm all submitted work and incorporated materials satisfy ownership and licensing requirements.
- [ ] Confirm all team members, if any, are added on Devpost.
- [ ] Confirm entrant eligibility under the official rules.
- [ ] Confirm any pre-existing work incorporated into the project is properly disclosed where required.
- [ ] Confirm all third-party libraries and services are used under their applicable terms/licenses.

Shipcheck cannot verify these declarations on behalf of the entrant.

## Final external links

- [ ] Public YouTube/Vimeo URL added.
- [ ] Public Devpost project URL added after publication.
- [ ] Optional final release tag created only after explicit final approval.
- [ ] Every link in `submission/devpost/links.md` opens correctly.

## Optional bonus contributions

- [ ] Public build article / podcast / video published with the required hackathon-purpose disclosure.
- [ ] Social post published with `#AllThingsAgentic`.
- [ ] Any optional Google AI integration claimed only if actually implemented.

## Freeze gate

Do not mark the submission frozen until:

```text
final verification evidence exists
+
required video is public
+
Devpost fields are complete
+
entrant declarations are confirmed
+
all final links are checked
+
explicit final approval is given
```
