# Shipcheck Evidence Decision Contract

**Status:** Implementation-aligned draft  
**Runtime version:** 0.6.0

Shipcheck does not treat an LLM response as a compliance verdict. The rules agent interprets explicit requirements; deterministic services gather observable evidence and produce structured findings.

## 1. Requirement classes

### `CHECKABLE`
A bounded automated checker can plausibly evaluate the requirement from repository, deployment, or other observable evidence.

### `MANUAL_REVIEW`
The requirement depends on identity, eligibility, subjective judgment, submission-form state, video quality, intent, or other evidence Shipcheck cannot safely establish automatically.

### `INFORMATIONAL`
The extracted item is relevant context but should not create a pass/fail obligation.

## 2. Evidence statuses

| Status | Contract |
|---|---|
| `VERIFIED` | Observable evidence supports the requirement. |
| `UNVERIFIED` | The requirement is checkable, but sufficient proof was not observed. |
| `MISSING` | A specifically expected artifact or value is absent. |
| `CONTRADICTED` | Observable evidence directly conflicts with a requirement or declared claim. |
| `MANUAL_REVIEW` | Automation cannot safely resolve the requirement. |
| `NOT_APPLICABLE` | No automated compliance verdict is required. |

### Missing proof is not contradiction

Shipcheck must not convert absence of support into a contradiction.

```text
claim present + no supporting evidence
    -> UNVERIFIED

claim present + conflicting observed evidence
    -> CONTRADICTED
```

Direct contradiction requires direct evidence of conflict.

## 3. Severity

Severity is independent from evidence status.

```text
CRITICAL
HIGH
WARNING
PASS
```

Typical interpretation:

- `CRITICAL`: unresolved mandatory blocker that prevents clearance;
- `HIGH`: material readiness issue requiring resolution or human review;
- `WARNING`: unresolved or manual item that should remain visible;
- `PASS`: no release gate is created by the finding.

Severity must be derived from the requirement and observed evidence, not from persuasive model prose.

## 4. Final disposition

The deterministic disposition contract is:

```text
if any CRITICAL finding exists:
    HOLD
else if any HIGH finding or MANUAL_REVIEW gate exists:
    NEEDS_REVIEW
else:
    READY
```

### `HOLD`
At least one unresolved critical finding remains.

### `NEEDS_REVIEW`
No critical blocker remains, but a high-severity issue or human-verification gate remains.

### `READY`
No `CRITICAL`, `HIGH`, or `MANUAL_REVIEW` gate remains within inspected scope.

`READY` means ready within the evidence Shipcheck could inspect. It is not a guarantee of eligibility, organizer acceptance, judging outcome, or legal compliance.

## 5. Evidence provenance

Every automated positive finding must point to observable evidence such as a repository path, deployment URL, or scoped runtime operation.

Evidence must retain enough provenance to answer:

```text
What was observed?
Where was it observed?
Which requirement did it support or contradict?
```

A filename alone is not sufficient proof when content is required. For example, an architecture-looking filename cannot automatically prove that a meaningful architecture artifact exists.

## 6. Rules-agent grounding

Every uncached extracted requirement includes a short `source_quote`.

Shipcheck accepts formatting-only normalization such as whitespace, smart quotes, Unicode dashes, and HTML entities, but the quote must still be grounded in contiguous source wording. Paraphrased or invented evidence must be rejected.

## 7. Model boundary

Gemini is used for natural-language rules interpretation. Gemini does not own:

- repository evidence collection;
- deployment reachability verification;
- reproduction checks;
- claim contradiction semantics;
- severity ordering;
- final disposition.

Those operations remain deterministic application services.

## 8. Failure behavior

Provider failure, inaccessible evidence, unsupported automation, or persistence failure must never silently become a pass.

Shipcheck may fail, abstain, return `UNVERIFIED`, or preserve `MANUAL_REVIEW`, but it must not manufacture clearance.
