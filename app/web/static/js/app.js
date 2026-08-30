const form = document.querySelector("#inspection-form");
const submitButton = document.querySelector("#submit-button");
const resetButton = document.querySelector("#reset-button");
const inspectionState = document.querySelector("#inspection-state");
const stateCopy = document.querySelector("#state-copy");
const emptyReport = document.querySelector("#empty-report");
const reportContent = document.querySelector("#report-content");
const reportPanel = document.querySelector("#report-panel");
const findingsList = document.querySelector("#findings-list");
const downloadButton = document.querySelector("#download-report");

let latestReport = null;

function setState(state, copy) {
  inspectionState.dataset.state = state;
  stateCopy.textContent = copy;
}

function text(elementId, value) {
  document.querySelector(`#${elementId}`).textContent = value ?? "—";
}

function link(elementId, value) {
  const element = document.querySelector(`#${elementId}`);
  element.textContent = value ?? "—";
  if (value) {
    element.href = value;
    element.removeAttribute("aria-disabled");
  } else {
    element.href = "#";
    element.setAttribute("aria-disabled", "true");
  }
}

function evidenceLabel(evidence) {
  const source = evidence.source || "evidence";
  const location = evidence.path_or_url ? ` · ${evidence.path_or_url}` : "";
  const observed = evidence.observed_value ? ` · ${evidence.observed_value}` : "";
  return `${source}${location}${observed}`;
}

function renderFinding(finding) {
  const article = document.createElement("article");
  article.className = "finding";
  article.dataset.status = finding.status;

  const code = document.createElement("div");
  code.className = "finding-code";

  const requirementId = document.createElement("strong");
  requirementId.textContent = finding.requirement_id;
  const status = document.createElement("span");
  status.textContent = finding.status;
  code.append(requirementId, status);

  const body = document.createElement("div");
  body.className = "finding-body";

  const title = document.createElement("p");
  title.className = "finding-title";
  title.textContent = finding.requirement_text;

  const reason = document.createElement("p");
  reason.className = "finding-reason";
  reason.textContent = finding.reason;

  body.append(title, reason);

  if (Array.isArray(finding.evidence) && finding.evidence.length) {
    const evidenceBlock = document.createElement("div");
    evidenceBlock.className = "evidence-list";

    const evidenceHeading = document.createElement("strong");
    evidenceHeading.textContent = "Evidence";
    const list = document.createElement("ul");

    finding.evidence.forEach((item) => {
      const listItem = document.createElement("li");
      listItem.textContent = evidenceLabel(item);
      list.append(listItem);
    });

    evidenceBlock.append(evidenceHeading, list);
    body.append(evidenceBlock);
  }

  if (finding.recommended_action) {
    const action = document.createElement("p");
    action.className = "finding-action";

    const heading = document.createElement("strong");
    heading.textContent = "Recommended action";
    action.append(heading, document.createTextNode(` · ${finding.recommended_action}`));
    body.append(action);
  }

  article.append(code, body);
  return article;
}

function renderReport(report) {
  latestReport = report;
  emptyReport.hidden = true;
  reportContent.hidden = false;
  reportPanel.querySelector(".error-message")?.remove();

  const disposition = document.querySelector("#disposition");
  disposition.textContent = report.final_disposition;
  disposition.dataset.disposition = report.final_disposition;

  text("inspection-id", report.inspection_id);
  text("summary-passed", report.summary?.passed ?? 0);
  text("summary-manual", report.summary?.manual_review ?? 0);
  text("summary-warning", report.summary?.warning ?? 0);
  text("summary-critical", report.summary?.critical ?? 0);
  text("model-used", report.model_used || "not reported");
  text("fallback-used", report.fallback_used ? "yes" : "no");
  link("report-repository", report.repository_url);
  link("report-rules", report.rules_source);

  findingsList.replaceChildren();
  (report.findings || []).forEach((finding) => {
    findingsList.append(renderFinding(finding));
  });

  setState(
    "success",
    `Inspection complete · ${report.final_disposition} · ${report.inspection_id}`,
  );
}

function renderError(message) {
  latestReport = null;
  emptyReport.hidden = true;
  reportContent.hidden = true;
  reportPanel.querySelector(".error-message")?.remove();

  const error = document.createElement("div");
  error.className = "error-message";
  error.textContent = message;
  reportPanel.append(error);
  setState("error", "Inspection failed. Review the manifest and try again.");
}

function normalizeClaims(rawClaims) {
  return rawClaims
    .split("\n")
    .map((claim) => claim.trim())
    .filter(Boolean);
}

async function runInspection(event) {
  event.preventDefault();

  if (!form.reportValidity()) {
    return;
  }

  const formData = new FormData(form);
  const deploymentUrl = String(formData.get("deployment_url") || "").trim();
  const payload = {
    rules_url: String(formData.get("rules_url") || "").trim(),
    repository_url: String(formData.get("repository_url") || "").trim(),
    deployment_url: deploymentUrl || null,
    submission_claims: normalizeClaims(String(formData.get("submission_claims") || "")),
  };

  submitButton.disabled = true;
  submitButton.querySelector("span:first-child").textContent = "Inspecting";
  setState("running", "Inspecting rules, repository evidence, and cloud actions…");

  try {
    const response = await fetch("/api/inspect", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });

    let body = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }

    if (!response.ok) {
      const detail = body?.detail;
      throw new Error(
        typeof detail === "string"
          ? detail
          : `Inspection failed with HTTP ${response.status}.`,
      );
    }

    renderReport(body);
    reportPanel.scrollIntoView({behavior: "smooth", block: "start"});
  } catch (error) {
    renderError(error instanceof Error ? error.message : "Inspection failed unexpectedly.");
  } finally {
    submitButton.disabled = false;
    submitButton.querySelector("span:first-child").textContent = "Run preflight";
  }
}

function resetWorkspace() {
  latestReport = null;
  reportContent.hidden = true;
  emptyReport.hidden = false;
  findingsList.replaceChildren();
  reportPanel.querySelector(".error-message")?.remove();
  setState("idle", "Awaiting manifest.");
}

function downloadReport() {
  if (!latestReport) {
    return;
  }

  const blob = new Blob([JSON.stringify(latestReport, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${latestReport.inspection_id || "shipcheck-report"}.json`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

form.addEventListener("submit", runInspection);
resetButton.addEventListener("click", resetWorkspace);
downloadButton.addEventListener("click", downloadReport);
