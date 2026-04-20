# HGB Disclosure Checklist — AI-Driven Workflow

**DNL Take-Home Challenge · German GAAP (HGB) · Medium GmbH · Naushad Ali R**

---

This repository is my submission for the Deep Neuron Lab professional practice take-home challenge. The task was to build an AI-driven disclosure checklist for German GAAP (HGB) reporting — and to do it in a way that demonstrates how a content workflow for an AI checklist product should actually be designed: auditable, legally grounded, and scalable across entity types and frameworks.

The result is `v2`: a historically grounded, auditor-traceable checklist system for a medium-sized GmbH, verified against Nubert electronic GmbH's FY2023 financial statements.

---

## What This Is

A working pipeline that takes a scoped entity profile and produces:

- a disclosure checklist grounded in the historically valid HGB law for the target financial year
- a structured verification of a real filing against that checklist
- full provenance for every row — statutory reference, German source wording, historical source URL, English canonical label, and applicability basis
- Excel outputs formatted for auditor review, with reviewer-facing tabs and a separate traceability layer

The checklist covers the four mandatory reporting components for a medium GmbH: Balance Sheet (Bilanz) (§266 HGB), Income Statement (GuV) (§275 HGB, Gesamtkostenverfahren format), Notes to the Financial Statements (Anhang) (§§284–288 HGB), and Management Report (Lagebericht) (§289 HGB).
---

## Scope

| Parameter | Decision |
|-----------|----------|
| Entity type | Limited Liability Company (GmbH) — Medium-Sized Company (Mittelgroße Kapitalgesellschaft) |
| Size class | §267 Abs. 2 HGB |
| Framework | HGB §§264 ff. — standalone Individual Financial Statements (Einzelabschluss) only |
| P&L format | Total Cost Method (Gesamtkostenverfahren) (§275 Abs. 1 HGB) |
| Target FY | 31 December 2023 |
| Reference entity | Nubert electronic GmbH, Schwäbisch Gmünd |
| Out of scope | Consolidated Financial Statements (Konzernabschluss) · Cash Flow Statement (Kapitalflussrechnung) · CSRD · sector-specific formats |

Nubert was chosen as the reference entity after ruling out candidates with financial-services complexity (RechKredV applicability) and group-accounts risk (§315e IFRS consolidated accounts). It is a clean, standalone medium GmbH with publicly available FY2023 financials.

---

## How It Works

The workflow is split into four explicit phases, each producing auditable artifacts before the next phase begins.

### Phase 1 — Historical Source Resolution

Before any checklist row is generated, the system resolves which version of HGB was in force on the target effective date.

**Buzer.de** is the normative historical source of record. It exposes prior versions of statutory provisions and their change history, which is required to confirm the legal basis for a prior-year run. `gesetze-im-internet.de` is used as an official current-text cross-reference only — it is not sufficient on its own to prove historical validity.

This distinction matters. A checklist that pulls from current consolidated law without confirming the historically valid provision is not legally grounded. For FY2023, most HGB provisions are stable, but the architecture enforces the discipline regardless.

### Phase 2 — source_manifest.json

The manifest is the run-level provenance artifact. It records:

- the target FY and effective date
- the entity profile and scope assumptions
- the historical source URL used for each section
- retrieval timestamps
- workflow and spec version

**A run is not considered auditable unless the manifest exists.** This is a hard gate, not a convention.

### Phase 3 — Applicability Resolution and Checklist Generation

Exemptions and conditional applicability are resolved at runtime from the historically valid source set — not from a static lookup table. §288 Abs. 2 relief for medium entities, §286 Abs. 4 exemptions, and §289 triggers are all derived from the live HGB text retrieved in Phase 1.

Checklist rows are generated section by section (BIL / GUV / ANH / LAG) and normalised into a canonical schema. Every row requires:

- a unique ID (`HGB-BIL-10000` format)
- a canonical English label (`english_label`) that controls how the audit question is rendered
- the German statutory wording (`source_text_de`) as the legal anchor
- obligation classification (`M` mandatory, `C` conditional) with trigger condition where applicable
- a `verification_mode` that tells the verifier how to reason about absent evidence
- a `completeness_prompt` — a structured instruction combining the English target, the German anchor term, the likely filing area to search, and the evidence threshold

Eleven QA gates run before any output is treated as audit-ready. A failed gate blocks the run.

### Phase 4 — Filing Verification

The verifier reads `checklist.json` and `source_manifest.json` as its authority for applicability. It does not re-decide exemptions ad hoc.

For each checklist row, the `verification_mode` field controls the reasoning:

- **`presentation_required`** — structural rows (§266 Abs. 1, §275 Abs. 1); absence or layout failure justifies `No`
- **`line_item_if_present`** — Bilanz and GuV leaf rows; absence from the primary statement alone does not justify `No`; a `No` requires affirmative evidence elsewhere in the filing that the underlying fact exists; absent that, the result is `N/A` with reason code `LINE_ITEM_NOT_PRESENT`
- **`fact_conditioned`** — notes and Lagebericht rows; applicability determined by triggers, exemptions, or entity-specific facts resolved in the manifest

Results are classified as `Yes` / `No` / `N/A` / `Review`, with an expanded reason code taxonomy that distinguishes between `MISSING_EVIDENCE`, `EXEMPTION_CLAIMED`, `PUBLICATION_RELIEF`, `AGGREGATION_RELIEF`, `REPEALED_ITEM`, `PDF_EXTRACTION_LIMIT`, and `ENTITY_SPECIFIC` — among others.

---

## Verification Results — Nubert electronic GmbH FY2023

The v2 checklist produced **134 items** across four sections, reflecting the expanded schema coverage compared to v1:

| Section | Total | Yes | No | N/A | Review | Pass Rate |
|---------|-------|-----|----|-----|--------|-----------|
| Bilanz | 50 | 20 | 0 | 30 | 0 | 100.0% |
| GuV | 21 | 12 | 0 | 9 | 0 | 100.0% |
| Anhang | 52 | 11 | 0 | 34 | 7 | 100.0% |
| Lagebericht | 11 | 6 | 0 | 5 | 0 | 100.0% |
| **Total** | **134** | **49** | **0** | **78** | **7** | **100.0%** |

The pass rate is calculated as Yes / (Yes + No) — items classified as N/A or Review are excluded from the denominator. The 100% pass rate reflects zero confirmed missing disclosures against applicable items.

The 78 N/A results are not omissions — they are a feature of the v2 verification model. The `line_item_if_present` and `fact_conditioned` verification modes ensure that absent Bilanz and GuV leaf rows are only marked `No` where affirmative evidence exists elsewhere in the filing that the underlying fact applies to the entity. Absent that evidence, the correct result is `N/A`. The N/A breakdown includes `LINE_ITEM_NOT_PRESENT` (line items with no evidence of the underlying fact), `PUBLICATION_RELIEF` (sub-lines lawfully omitted under §327 Nr. 1 HGB for medium companies), `AGGREGATION_RELIEF` (GuV lines aggregated into *Rohergebnis* under §276 HGB), `EXEMPTION_CLAIMED`, `REPEALED_ITEM`, and `ENTITY_SPECIFIC`.

The 7 Review items are concentrated in the Anhang and fall into two categories: `JUDGMENT_REQUIRED` (rows where the filing evidence is ambiguous and human interpretation is needed) and `PDF_EXTRACTION_LIMIT` (rows dependent on the *Anlagenspiegel*, which is referenced in the Anhang as *Anlage 1* but was not captured in the extracted filing text). These are not false negatives — they are correctly flagged rather than silently resolved.

Human sign-off is required before any `Review` item can be treated as cleared.

---

## Artifacts

Each run produces the following:

| Artifact | Description |
|----------|-------------|
| `source_manifest.json` | Run-level provenance — the auditability gate |
| `checklist.json` | Canonical checklist in the v2 schema |
| `results.json` | Per-row verification results |
| `output/checklist.xlsx` | Reviewer-facing checklist workbook |
| `output/results.xlsx` | Results workbook with section tabs, issues tab, and traceability tab |
| `run_summary.md` | Non-normative run report — counts, pass rates, token usage |

The Excel outputs use a two-layer layout: reviewer-facing section tabs optimised for practical use, and a separate Traceability tab carrying provenance, workflow, and verifier-control fields. These concerns are deliberately separated.

---

## Packaged Skills

The workflow is packaged as two reusable SKILL.md files for agent execution environments (Kilo Code / Codex):

- **`v2/german-gaap-checklist-generator/SKILL.md`** — checklist generation workflow contract
- **`v2/hgb-filing-verification/SKILL.md`** — filing verification workflow contract

Each skill references the normative spec and scope document rather than re-stating them inline. The design intention is that a new run for a different entity or target year is a scope change, not a rebuild.

---

## Cost

The full pipeline — checklist generation plus filing verification — runs at approximately **$2–4 at standard API rates** for a single entity and FY. The v2 Nubert run was executed via the Codex. No incremental cost was incurred and the usage was around 2% of the 5hr quota. 

Cost consciousness was a deliberate design constraint, not an afterthought: the architecture is optimised for minimal redundant context and parallel section-agent execution after a shared provenance stage.

---

## Extending This

v2 is scoped to one entity type and one framework. Extension to IFRS, UK GAAP, or other entity types requires a deliberate redesign of the source hierarchy, applicability logic, canonical reference fields, and verification heuristics — not a find-and-replace on the existing schema. The spec documents this explicitly.

Planned extension points:

- **Other frameworks** — swap `scope.md`, redesign source hierarchy and applicability resolver, re-prompt section agents per standard
- **Entity variants** — large GmbH (§285 Nr. 9 full remuneration), AG (Aufsichtsrat disclosures, §289a), small entities (§288 Abs. 1 exemption set), group accounts (§§290 ff. agent)
- **Product integration** — `checklist.json` is ingestible by a checklist product API; `completeness_prompt` is designed as a direct validator agent input; `results.json` is structured for an audit evidence store

---

## What Changed from v1

v1 established the parallel agent architecture, the JSON-as-source-of-truth model, and the four-section scope. v2 is a breaking redesign of the documentation and provenance model:

- **Historical grounding** — v1 had no mechanism to confirm which law version applied to the target FY; v2 makes Buzer the normative source with a formal source hierarchy
- **source_manifest.json** — new required artifact; without it, the run is not auditable
- **Runtime applicability resolution** — v1 used a static exemption approach; v2 derives exemptions from the historically valid source set
- **verification_mode** — v1 conflated structural and leaf-row verification; v2 enforces `presentation_required` / `line_item_if_present` / `fact_conditioned` per row in the schema
- **english_label layer** — v1 had mixed-language rows; v2 separates the canonical English rendering layer from German statutory provenance
- **QA gates** — v1 had no formal validation stage; v2 has 11 explicit gates that block audit-ready status on failure
- **Expanded reason codes** — v2 adds `PUBLICATION_RELIEF`, `AGGREGATION_RELIEF`, `REPEALED_ITEM`, `POST_BS_EVENT`, and `PDF_EXTRACTION_LIMIT` to the taxonomy

---

## Repo Structure

```
dnl-challenge-repo/
├── v2/
│   ├── v2-spec.md                          # Normative specification
│   ├── scope.md                            # Scoped assumptions and constraints
│   ├── generate_true_checklist.py          # Phase 1–3 runner
│   ├── generate_excel.py                   # Checklist Excel export
│   ├── run_hgb_verification.py             # Phase 4 runner
│   ├── generate_results_excel.py           # Results Excel export
│   ├── source_manifest.json                # Run provenance artifact
│   ├── checklist.json                      # Canonical checklist output
│   ├── results.json                        # Verification results
│   ├── run-report-nubert-2023.md           # Non-normative run report
│   ├── output/
│   │   ├── checklist.xlsx
│   │   └── results.xlsx
│   ├── german-gaap-checklist-generator/
│   │   └── SKILL.md
│   └── hgb-filing-verification/
│       └── SKILL.md
└── README.md
```

---

*Naushad Alir · [github.com/xNR-dev/dnl-challenge-repo](https://github.com/xNR-dev/dnl-challenge-repo)*
