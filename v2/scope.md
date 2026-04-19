# DNL Disclosure Checklist - v2 Scope Manifest

## System Context

You are acting inside a multi-stage HGB checklist workflow for auditors. Your task is not just to
draft checklist rows. Your task is to produce checklist rows that are historically grounded,
traceable, and reviewable.

This scope file defines the run assumptions for a specific use case. The actual run MUST also
produce a `source_manifest.json` that records how historical grounding was resolved.

## Scope Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Entity type | GmbH - Mittelgrose Kapitalgesellschaft (§ 267 Abs. 2 HGB) | scope.md |
| Target FY | 31 December 2023 | scope.md |
| Reporting framework | HGB (German Commercial Code) §§ 264 ff. | scope.md |
| P&L format | Gesamtkostenverfahren (§ 275 Abs. 1 HGB) | scope.md |
| Output language | English with required German-source traceability | scope.md |

## Source Hierarchy

Historical grounding for this scope MUST follow this source hierarchy:

1. **Primary historical source:** [Buzer.de](https://www.buzer.de/)
2. **Official current-text cross-reference:** [Gesetze im Internet](https://www.gesetze-im-internet.de/hgb/)

Normative rule:

- if the run is grounded "as of" a prior FY, historical validity MUST come from Buzer
- `gesetze-im-internet.de` MAY be recorded as an official cross-reference, but MUST NOT be used as
  the sole proof of historical validity for this 2023-targeted run

## Execution Architecture

### Required stages

1. Load this scope manifest
2. Resolve historical source set from Buzer
3. Build `source_manifest.json`
4. Run Applicability Resolver
5. Generate checklist items by section
6. Normalize into canonical schema
7. Run QA gates
8. Verify against filing if verification is in scope
9. Export outputs and `run_summary.md`

### Parallel section drafting

Section drafting MAY run in parallel after historical sources and applicability decisions have been
resolved:

- **Bilanz Agent** - BIL-10000 items
- **GuV Agent** - GUV-20000 items
- **Anhang Agent** - ANH-30000 items
- **Lagebericht Agent** - LAG-40000 items

Section agents MUST consume the resolved source/applicability context; they MUST NOT invent their
own grounding model.

## Entity and Reporting Scope

### Entity and size

- Entity type: GmbH
- Size class: medium (`mittelgrose`) under § 267 Abs. 2 HGB
- Small entity exemptions under § 288 Abs. 1 HGB: out of scope
- Medium-entity relief under § 288 Abs. 2 HGB: resolved at runtime

### Reporting framework

- Framework: German GAAP (HGB §§ 264 ff.)
- P&L format: Gesamtkostenverfahren
- Components in scope: Bilanz, GuV, Anhang, Lagebericht
- Focus: disclosure requirements only, not recognition or measurement

### Out of scope

- Konzernabschluss (§§ 290 ff.)
- Kapitalflussrechnung
- Segmentberichterstattung
- sector-specific formats
- listed-company overlays outside this profile
- large-entity and AG-specific disclosure regimes unless they are needed only as exclusions

## Runtime Applicability and Exemptions

Applicability MUST be resolved at runtime from the historically grounded HGB source set.

### Applicability Resolver responsibilities

- confirm that the entity profile matches this scope
- inspect historically valid HGB text for the target FY
- derive whether a disclosure item is mandatory, conditional, exempt, or entity-specific
- persist the decision in the run-level provenance artifacts
- populate `obligation` and `trigger_condition` accordingly

The workflow MUST NOT rely on a fixed exemption table as the normative source of truth.

## Required Checklist Fields

Each generated checklist item MUST include:

- `id`
- `section`
- `sub_section`
- `disclosure_item`
- `hgb_reference`
- `effective_version_date`
- `historical_source_url`
- `official_reference_url`
- `source_anchor`
- `source_text_de`
- `translation_status`
- `obligation`
- `trigger_condition` when conditional
- `evidence_location`
- `completeness_prompt`

## Translation Requirements

English wording is allowed only when traceability is preserved:

- every English row must point back to the German source wording
- highly technical accounting terms SHOULD retain the German term inline or be explained in
  `translation_note`
- `translation_status` MUST indicate whether the wording is direct, normalized, or reviewed

## Quality Requirements

### Grounding

- every item must map to a historically valid HGB provision for the target FY
- every item must include both historical and official reference URLs
- every item must include German source traceability fields

### Completeness

- include all mandatory disclosures for the scoped entity
- include conditional items where applicability depends on entity facts or legal relief
- do not compress separate statutory obligations into one row solely for convenience

### Validation

At minimum, the generated output must be checked for:

- citation existence
- source URL class correctness
- effective-date plausibility
- required provenance fields
- applicability/exemption consistency
- block numbering consistency
- duplicate meaning
- translation completeness

## Output Artifacts

Required outputs for a full run:

1. `source_manifest.json`
2. `checklist.json`
3. `results.json` if verification is run
4. `output/checklist.xlsx`
5. `output/results.xlsx` if verification is run
6. `run_summary.md`

## Separation of Concerns

This file defines scope assumptions and constraints. It does not replace the normative
specification. If adapting the workflow for a different framework or entity type, update this file
and the associated source hierarchy, applicability rules, and schema requirements together.
