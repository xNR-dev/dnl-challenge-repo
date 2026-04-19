# HGB Disclosure Checklist - v2 Normative Specification

## Overview

This specification defines the normative design for `v2` of the HGB disclosure checklist system.

`v2` is a grounded, auditable workflow for generating and verifying disclosure checklists for a
scoped German GAAP use case. The design target is a checklist that is valid **as of a specified
financial year-end date**, with enough provenance for a reviewer to reconstruct the legal basis of
each row.

This is a breaking redesign of the documentation model. The focus is no longer "version-stamped"
in a loose descriptive sense; the focus is **historically grounded and reproducible**.

## Current Implementation Status

The following pieces are implemented in the current `v2` repo state:

- true checklist generation from source pages via `generate_true_checklist.py`
- packaged Codex skill for checklist generation at `v2/german-gaap-checklist-generator/SKILL.md`
- packaged Codex skill for filing verification at `v2/hgb-filing-verification/SKILL.md`
- reproducible filing verification runner via `run_hgb_verification.py`
- JSON and Excel exports for both checklist and verification results
- English-first checklist rendering using canonical `english_label` fields
- Bilanz/GuV line-item verification logic that distinguishes structural rows from fact-dependent leaf rows

This specification therefore describes both:

- the normative contract the system should satisfy
- the currently implemented artifact and workflow shape in the repo

## Scope

- **Entity type:** GmbH - Mittelgrose Kapitalgesellschaft (§ 267 Abs. 2 HGB)
- **Target FY example:** 31 December 2023
- **Framework:** German GAAP (HGB §§ 264 ff.)
- **Output language:** English checklist rows with required German-source traceability
- **Objective:** Auditor-facing disclosure checklist plus verification workflow

## Source Authority Model

### Normative source hierarchy

When a checklist is generated for a prior reporting date, source authority is defined as follows:

1. **Historical source of record:** [Buzer.de](https://www.buzer.de/)
2. **Official current-text cross-reference:** [Gesetze im Internet](https://www.gesetze-im-internet.de/hgb/)

### Why this hierarchy exists

- Buzer exposes prior versions of HGB provisions and change history, which is required for an
  "as of FY 2023" run.
- `gesetze-im-internet.de` exposes the current consolidated text with a current "Stand", which is
  useful for official cross-reference but is not sufficient on its own for historical grounding.

### Normative rule

If the run is time-bounded to a prior financial year, the legal grounding of the checklist MUST be
resolved from the historically valid provision version in Buzer. Any
`gesetze-im-internet.de` reference is supplementary and MUST NOT be treated as proof of historical
validity for that run.

## Required Run Artifacts

Each checklist-generation run MUST produce the following artifacts:

1. `source_manifest.json`
2. `checklist.json`
3. `results.json` if verification is performed
4. `output/checklist.xlsx`
5. `output/results.xlsx` if verification is performed
6. `run_summary.md`

The system is not considered auditable unless the source manifest exists.

### Current implementation note

The current repo provides explicit runnable entrypoints for the main artifacts:

- `generate_true_checklist.py` produces `checklist.json`, `source_manifest.json`, and `run_summary.md`
- `generate_excel.py` produces `output/checklist.xlsx`
- `run_hgb_verification.py` produces `results.json`
- `generate_results_excel.py` produces `output/results.xlsx`

The current `results.xlsx` workbook uses a two-layer layout:

- reviewer-facing section tabs (`Bilanz`, `GuV`, `Anhang`, `Lagebericht`) optimized for practical review
- a separate `Traceability` tab for provenance, workflow, and verifier-control fields
- an `Issues - No Review` tab that isolates unresolved reviewer follow-up items

The reviewer-facing section tabs currently contain:

- `ID`
- `Sub-section`
- `Checklist Item`
- `HGB Ref`
- `Source Text (DE)`
- `Obligation`
- `Trigger Condition`
- `Evidence Location`
- `Response`
- `Reason Code`
- `Confidence`
- `Evidence`
- `Audit Notes`

The `Traceability` tab currently contains:

- `ID`
- `Section`
- `Sub-section`
- `Checklist Item`
- `HGB Ref`
- `Effective Version Date`
- `Historical Source URL`
- `Official Reference URL`
- `Verification Mode`
- `Presence Inference Rule`
- `Cross Evidence Sources`
- `Verified By`
- `Verification Date`

## Source Manifest

### Purpose

`source_manifest.json` is the run-level provenance artifact. It records how the historical legal
basis was resolved for the specific target FY.

### Required contents

The manifest MUST capture:

- target FY / effective date used for grounding
- entity profile and scope assumptions
- source system used for each provision family or section
- exact historical source URL used for grounding
- official cross-reference URL where available
- retrieval timestamp
- source title / paragraph reference
- source-effective-date metadata as shown or inferred from the historical source
- workflow version / spec version
- workflow or agent configuration used for the run
- run date

Optional if local source capture is implemented:

- checksum or hash of stored fetched source text
- local file path for stored source snapshots

### Current implementation note

The current `source_manifest.json` implementation records:

- target FY and effective date
- entity profile
- source hierarchy
- workflow and spec versions
- per-section source URLs and effective notes
- per-reference source URLs and retrieval timestamps

It does not currently persist a model identifier.

### Normative rule

The manifest MUST be sufficient for a reviewer to answer:

- which source grounded the run
- which provision versions were used
- when they were retrieved
- which workflow configuration generated the output

## Checklist Schema

### `checklist.json`

Every checklist row MUST include the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier, e.g. `HGB-BIL-10000` |
| `section` | string | Yes | `Bilanz`, `GuV`, `Anhang`, `Lagebericht` |
| `sub_section` | string | Yes | Logical grouping within section |
| `english_label` | string | Yes | Canonical English disclosure label used for rendering and verification context |
| `english_label_status` | string | Yes | Label quality state; currently `approved` for production-ready rows |
| `disclosure_item` | string | Yes | Auditor-facing question in English |
| `hgb_reference` | string | Yes | German statutory reference |
| `effective_version_date` | string | Yes | Historical effective date used for the legal basis |
| `historical_source_url` | string | Yes | Buzer URL used to ground the row |
| `official_reference_url` | string | Yes | Official current-text cross-reference URL |
| `source_text_de` | string | Yes | German source wording or excerpt sufficient for review |
| `obligation` | string | Yes | `M` (Mandatory) or `C` (Conditional) |
| `trigger_condition` | string | No | Condition or exemption rationale for `C` items |
| `verification_mode` | string | Yes | Verification behavior such as `presentation_required`, `line_item_if_present`, or `fact_conditioned` |
| `presence_inference_rule` | string | Yes | Short rule telling the verifier how to reason about absent items |
| `cross_evidence_sources` | string[] | Yes | Ordered list of sections the verifier should inspect when primary-statement evidence is absent |
| `evidence_location` | string | Yes | Semantic location in FS |
| `completeness_prompt` | string | Yes | Verification instruction that includes the English target, German anchor term, likely search area, and evidence threshold |

### Normative row-validity rule

A checklist row is invalid unless it contains enough provenance for a reviewer to:

- reconstruct the historical legal basis
- inspect the relevant German wording
- understand how the English phrasing maps back to the German source
- identify the canonical English label used for rendering and verification

### Translation control

English output is permitted only with explicit German traceability:

- each `disclosure_item` MUST be generated from a controlled `english_label`, not from mixed
  German-English phrase substitution
- each English row MUST remain reviewable against the German source wording in `source_text_de`
- German statutory wording SHOULD remain in provenance fields and workbook columns, not inline in
  the user-facing checklist question
- if a canonical English label is not yet approved, the run SHOULD flag the row for refinement
  rather than silently emitting degraded mixed-language text

### Wording model

The current `v2` checklist contract uses an English-first rendering layer:

- `english_label` is the canonical user-facing concept
- `disclosure_item` is rendered from `english_label` using section-specific question templates
- `source_text_de` remains the German legal anchor for provenance and verification
- `completeness_prompt` carries both the English target and the German anchor term for the
  verification agent

This separation is intentional: readability for an English-speaking reviewer and legal traceability
for verification are treated as distinct concerns.

### Applicability model for statement line items

The checklist MUST distinguish between structural statement checks and fact-dependent leaf rows:

- `presentation_required`
  - use for structural rows such as `§266 Abs. 1 HGB` and `§275 Abs. 1 HGB`
  - absence or layout failure may justify `No`
- `line_item_if_present`
  - use for most Bilanz and GuV leaf rows under `§266` and `§275`
  - absence alone is not enough for `No`
  - `No` requires affirmative evidence elsewhere in the filing that the underlying fact exists
  - if no such evidence exists, the verifier SHOULD return `N/A`
- `fact_conditioned`
  - use for notes and management-report rows that depend on triggers, exemptions, or entity facts

### Checklist metadata

The checklist-level `metadata` object SHOULD include at least:

- `entity_type`
- `size_class`
- `reporting_framework`
- `pl_format`
- `target_fy`
- `target_fy_effective_date`
- `framework_version`
- `generated_date`
- `schema_version`
- `workflow_version`
- `generation_mode`

The current implementation also includes:

- `applicable_date`
- `version`

## Verification Result Schema

### `results.json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Matches checklist item ID |
| `response` | string | Yes | `Yes`, `No`, `N/A`, or `Review` |
| `reason_code` | string | No | Reason code taxonomy |
| `confidence` | string | No | `High`, `Medium`, or `Low` |
| `evidence` | string | No | Specific evidence including page number, term, amount, or applicability basis |
| `audit_notes` | string | No | Auditor or agent judgment notes |
| `verified_by` | string | Yes | Agent or reviewer identifier |
| `verification_date` | string | Yes | ISO date (`YYYY-MM-DD`) |

### Current implementation note

The current verifier writes `results.json` as a flat list of result rows keyed by checklist `id`.

## ID Convention

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`

| Component | Format | Example |
|-----------|--------|---------|
| Framework | 2-4 chars | `HGB`, `IFRS`, `UKG` |
| Section | 3-letter | `BIL`, `GUV`, `ANH`, `LAG` |
| Sequence | 5-digit, padded | `10000`, `20000`, `30000` |

### Block reservation

| Section | Block | Range | Rationale |
|---------|-------|-------|-----------|
| BIL | Balance Sheet | 10000-19999 | Bilanz disclosures and structure |
| GUV | P&L | 20000-29999 | Profit & loss line items |
| ANH | Notes | 30000-39999 | Notes disclosures, exemptions, and applicability |
| LAG | Management Report | 40000-49999 | §289 sub-sections |

Insertion rule: use the next available slot in the allocated block. No decimals.

## Runtime Applicability and Exemption Resolution

### Normative rule

§288 and other applicability logic MUST be resolved at runtime from the historically grounded
source set. The system MUST NOT rely on a static exemption table as the normative source of truth.

### Required workflow stage

The run MUST include an `Applicability Resolver` stage before checklist rows are finalized.

### Applicability Resolver responsibilities

- confirm size-class assumptions from scope
- inspect the historically valid HGB text for the target FY
- derive whether specific items are mandatory, conditional, exempt, or not applicable
- persist the resolution in the manifest and/or a generated applicability artifact
- populate `obligation` and `trigger_condition` from the resolved runtime result

### Non-normative note

Static exemption lists may appear in examples or appendices for orientation, but actual runs MUST
derive exemptions from the historically grounded source set.

## Reason Code Taxonomy

| Code | Definition | Example |
|------|------------|---------|
| `MISSING_EVIDENCE` | Required disclosure not found in FS | Required note not located |
| `PARTIAL_DISCLOSURE` | Some elements present, others missing | Partial policy disclosure |
| `JUDGMENT_REQUIRED` | Requires auditor interpretation | Materiality threshold unclear |
| `AMBIGUOUS_LANGUAGE` | FS language unclear | Statement too generic to verify |
| `EXEMPTION_CLAIMED` | Historically grounded exemption applies | Medium GmbH exemption under §288 |
| `LINE_ITEM_NOT_PRESENT` | Statement leaf not evidenced as relevant for this entity | No evidence of goodwill, raw materials, or similar underlying fact |
| `PUBLICATION_RELIEF` | Published filing may omit the specific Bilanz sub-line under medium-company disclosure relief | `§327 Nr. 1 HGB` allows abbreviated published balance sheet presentation |
| `AGGREGATION_RELIEF` | Published GuV may lawfully aggregate the detailed line item | `§276 HGB` allows `Umsatzerlöse` and the next GKV lines to be rolled into `Rohergebnis` |
| `REPEALED_ITEM` | The statutory item is repealed and should not be treated as an active verification requirement | `(weggefallen)` rows in `§285` or `§289` |
| `POST_BS_EVENT` | Post-balance-sheet event | Appointment after FY-end |
| `PDF_EXTRACTION_LIMIT` | Source filing extraction issue | Table not captured in text extraction |
| `ENTITY_SPECIFIC` | Not applicable to entity type or facts | No subsidiaries, no parent, no group |

## Confidence Levels

| Level | Definition |
|-------|------------|
| `High` | Specific page, term, amount, or applicability basis cited |
| `Medium` | Evidence present but not fully pinned down |
| `Low` | Inferred, ambiguous, or extraction-limited |

## Workflow

```text
INPUT: scope.md
        |
        v
1. Load scope manifest and assumptions
        |
        v
2. Resolve historical source set from Buzer for target FY
        |
        v
3. Build source_manifest.json
        |
        v
4. Run Applicability Resolver
        |
        v
5. Generate checklist items by section
        |
        v
6. Normalize into canonical schema
        |
        v
7. Run QA gates
        |
        v
8. Run verification against filing
        |
        v
9. Export JSON, Excel, and run_summary.md
```

### Current implementation note

The current repo supports this workflow as separate explicit phases rather than a single unified
orchestrator:

1. generate checklist artifacts from source
2. export checklist workbook
3. run filing verification
4. export results workbook

This is consistent with the modular `v2` direction, even though it is not yet a single-command
runner for the full end-to-end flow.

## QA Gates

The normalized checklist MUST pass the following checks:

- citation existence validation
- source URL class validation (`historical_source_url` vs `official_reference_url`)
- source-effective-date validation
- required German provenance field validation
- applicability/exemption consistency checks
- duplicate ID detection
- duplicate meaning detection
- section/block numbering validation
- scope drift detection
- canonical English label completeness checks
- mixed-language checklist wording checks

If any gate fails, the run MUST be flagged for correction or review before being treated as
audit-ready.

## Authoritative Sources

| Purpose | Source | Role |
|---------|--------|------|
| Historical source of record | Buzer.de | Historical grounding for target-FY runs |
| Official current-text cross-reference | Gesetze im Internet | Reviewer convenience and current official reference |

## Separation of Normative Spec vs Run Reports

This specification is normative. It defines:

- what the system must do
- which artifacts must exist
- which fields are required
- which validation gates must pass

Point-in-time outputs such as checklist counts, pass rates, token usage, and entity-specific run
results belong in separate run-report documents and MUST NOT be treated as normative requirements.

## Limitations and Human Oversight

- English output still requires informed review when legal nuance is high.
- Historical grounding quality depends on the completeness and stability of the historical source.
- The current `obligation` split between `M` and `C` is reliable for explicit statutory exemptions and scope gates such as §288, §286, and capital-markets-related §289 triggers, but it does not yet fully classify every materiality-conditioned, fact-conditioned, or circumstance-dependent disclosure embedded inside otherwise mandatory provisions.
- PDF extraction can miss complex tables or formatting-heavy disclosures.
- Human sign-off is required for material `No` findings and unresolved `Review` items.
- This spec defines one scoped use case; extension to other frameworks requires separate design.

## Extending Beyond the Current Scope

To adapt this architecture for IFRS, UK GAAP, or other entity types, the following must be
redesigned rather than assumed interchangeable:

- source hierarchy
- applicability logic
- canonical reference fields
- evidence-location conventions
- verification heuristics

## Related Documents

- `v2/scope.md` - scoped assumptions and generation constraints
- `v2/german-gaap-checklist-generator/SKILL.md` - generator workflow contract
- `v2/hgb-filing-verification/SKILL.md` - verification workflow contract
- `v2/run-report-nubert-2023.md` - example non-normative run report

*Specification version: 2.0*
*Last updated: 2026-04-19*
