---
name: german-gaap-checklist-generator
description: Generate a historically grounded HGB disclosure checklist for a medium-sized GmbH. Use when Codex needs to create or regenerate `checklist.json`, `source_manifest.json`, or checklist Excel outputs for German GAAP (`HGB`) reporting as of a target financial year, especially when the workflow must preserve Buzer-based historical grounding, runtime applicability resolution, and German-to-English source traceability.
---

# German GAAP Checklist Generator

Generate a scoped HGB disclosure checklist for a medium-sized GmbH with historical grounding and
reviewer-traceable provenance.

## Read First

Before generating anything:

1. Read [scope.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/scope.md) for scope assumptions.
2. Read [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md) for the normative schema and workflow contract.
3. If verification outputs are involved, read [hgb-filing-verification/SKILL.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/hgb-filing-verification/SKILL.md).

Do not restate the full spec inside the run. Use the spec as the source of truth.

## Inputs

Collect or confirm:

- `entity_name`
- `target_fy`
- `pl_format`

Assume this fixed profile unless the user explicitly changes it:

- entity type: medium-sized GmbH
- framework: HGB
- components in scope: Bilanz, GuV, Anhang, Lagebericht

## Workflow

### 1. Resolve historical sources

- Use Buzer as the historical source of record for the target FY.
- Record `gesetze-im-internet.de` only as the official current-text cross-reference.
- Build `source_manifest.json` before finalizing checklist rows.

### 2. Resolve applicability

- Determine mandatory, conditional, exempt, and entity-specific items from the historically valid
  source set.
- Resolve §288 relief at runtime.
- Store applicability decisions in the run artifacts; do not guess them later during verification.

### 3. Draft by section

Generate rows by section using the standard ID blocks:

- `BIL` 10000-19999
- `GUV` 20000-29999
- `ANH` 30000-39999
- `LAG` 40000-49999

Parallel drafting is allowed only after source and applicability resolution are complete.

### 4. Normalize

Normalize every row into the canonical schema defined in [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md).

Preserve:

- historical effective date
- historical and official URLs
- German source text
- obligation and trigger condition
- verification mode, presence inference rule, and cross-evidence sources

### 5. Validate

Reject output that fails any of these checks:

- missing historical grounding
- missing German provenance fields
- missing applicability logic for conditional items
- duplicate IDs
- duplicate meaning
- block-number mismatch
- translation traceability gaps

### 6. Export

Emit:

- `source_manifest.json`
- `checklist.json`
- `output/checklist.xlsx`
- `run_summary.md`

If verification is part of the same run, hand off to the verification workflow after checklist
validation succeeds.

## Output Rules

Treat a checklist row as incomplete unless a reviewer can:

- identify the HGB provision
- inspect the German source wording
- see the historical source URL used for grounding
- understand how the English question maps back to the German text

Keep English audit phrasing concise. Preserve the German term inline or in translation metadata
when the accounting meaning could drift.

## Guardrails

- Do not treat `gesetze-im-internet.de` as sufficient proof of historical validity for prior-FY runs.
- Do not use a static exemption table as the normative source of truth.
- Do not compress distinct statutory obligations into one checklist row just to reduce item count.
- Do not emit checklist rows before `source_manifest.json` exists.
- Do not treat the run as audit-ready until the validation gates in the spec pass.

## When To Load Adjacent Docs

- Load [scope.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/scope.md) when confirming assumptions, P&L format, or scope boundaries.
- Load [v2-spec.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/v2-spec.md) when you need required fields, QA gates, artifact definitions, or source hierarchy rules.
- Load [hgb-filing-verification/SKILL.md](/Users/naushadalir/Library/Mobile%20Documents/com~apple~CloudDocs/DNL%20challenge/dnl-challenge-repo/v2/hgb-filing-verification/SKILL.md) only when the task includes verifying a filing.
