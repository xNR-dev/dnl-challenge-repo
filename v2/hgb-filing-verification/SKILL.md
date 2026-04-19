---
name: hgb-filing-verification
description: Verify a financial statement filing against a historically grounded HGB disclosure checklist. Use when Codex needs to create or review `results.json`, assess `Yes`/`No`/`N/A`/`Review` responses, or verify a PDF or extracted filing text using `checklist.json` and `source_manifest.json` while preserving manifest-resolved applicability and evidence-quality rules.
---

# HGB Filing Verification

Verify a filing against an already-generated HGB checklist. Treat the checklist and source manifest
as the authority for applicability, provenance, and verification scope.

## Read First

Before verifying anything:

1. Read [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md) for the normative result schema, reason codes, and validation rules.
2. Read [scope.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/scope.md) if scope assumptions or entity boundaries matter.
3. Read [german-gaap-checklist-generator/SKILL.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/german-gaap-checklist-generator/SKILL.md) only if the checklist artifacts look inconsistent or need regeneration.

Do not restate the full spec inside the run. Use it as the source of truth.

## Required Inputs

Collect or confirm:

- `checklist.json`
- `source_manifest.json`
- filing PDF or extracted filing text

If the filing is a PDF, pre-extract text once before row-level verification.

## Workflow

### 1. Load run artifacts

- Read `checklist.json` and `source_manifest.json` first.
- Trust manifest-resolved applicability.
- Do not invent historical exemptions during verification.

Treat these fields as the row-level contract:

- `disclosure_item`
- `source_text_de`
- `obligation`
- `trigger_condition`
- `verification_mode`
- `presence_inference_rule`
- `cross_evidence_sources`
- `evidence_location`
- `completeness_prompt`

### 2. Prepare the filing text

- Extract the PDF to searchable text before verifying rows.
- Keep the extracted text available for repeated searches.
- Use the original PDF for page references, table context, and formatting-sensitive checks.

### 3. Execute the row check

For each checklist row:

- use `completeness_prompt` as the primary instruction
- use `disclosure_item` to understand the English disclosure target
- use `source_text_de` as the German anchor term for search and traceability
- use `evidence_location` to prioritize the likely filing area
- honor `verification_mode` when deciding whether absence means `No` or `N/A`

If a row is already resolved as exempt or not applicable from run artifacts:

- do not search the filing for proof of a disclosure that was not required
- return `N/A` with the applicability basis in `evidence`

### 4. Map the response

Use this result mapping:

- `Yes`: specific evidence found
- `No`: still applicable, and there is affirmative evidence that the underlying fact exists or should exist, but the required presentation is missing
- `N/A`: exempt or not applicable based on run artifacts
- `Review`: judgment, ambiguity, or extraction quality prevents a reliable conclusion

Use the reason codes defined in [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md).

### 5. Apply the negative-finding backstop

Before finalizing `No`:

- search likely German variants and close terminology equivalents
- for Bilanz and GuV leaf rows, search the configured cross-evidence sources for affirmative evidence that the underlying fact exists
- confirm the row was not pre-resolved as exempt or entity-specific
- confirm the issue is not only a PDF extraction failure

### 6. Validate and export

Reject the results set if any of these checks fail:

- missing response for any checklist row
- `No` used for a row already resolved as exempt or not applicable
- generic evidence such as `not found` or `item disclosed`
- missing applicability basis for `N/A`
- `Review` without a clear ambiguity or extraction rationale

Save output to `results.json` in the same directory as the checklist.

## Evidence Rules

- `Yes` must cite concrete evidence such as page number, heading, amount, or quoted filing term
- `No` must state what was searched and why the row still appears applicable
- `N/A` must cite the applicability basis from run artifacts
- `Review` must explain whether the blocker is judgment, ambiguity, or extraction quality

For Bilanz and GuV leaf rows with `verification_mode = line_item_if_present`:

- absence in the primary statement alone is not enough for `No`
- use `No` only when the filing gives affirmative contradictory evidence elsewhere
- if no contradictory evidence is found, use `N/A` with `LINE_ITEM_NOT_PRESENT`

## Guardrails

- Do not decide §288 or other historical exemptions ad hoc during verification.
- Do not treat `Checklist Item` alone as sufficient context when `completeness_prompt` adds search and evidence instructions.
- Do not mark a row `No` when extraction quality is the real blocker.
- Do not mark a Bilanz or GuV leaf row `No` just because the line is absent from the primary statement.
- Do not collapse `historically exempt` and `entity-specific not applicable` into the same explanation.
- Do not emit `results.json` until every row has a valid response and evidence rationale.

## When To Load Adjacent Docs

- Load [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md) for result schema, reason codes, confidence rules, or final validation requirements.
- Load [scope.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/scope.md) when a filing raises questions about scope assumptions or entity profile.
- Load [german-gaap-checklist-generator/SKILL.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/german-gaap-checklist-generator/SKILL.md) only when upstream checklist regeneration or provenance review is needed.
