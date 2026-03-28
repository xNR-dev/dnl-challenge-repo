# HGB Disclosure Checklist — DNL Take-Home Challenge

**AI-driven disclosure checklist for auditors under German GAAP (HGB), scoped to a medium-sized GmbH.**

This repository contains a structured, machine-readable disclosure checklist built using an agent-based AI workflow, along with a proof-of-concept verification against real financial statements.

---

## Quick Start

**View the checklist:**
- [`output/checklist.xlsx`](output/checklist.xlsx) — the blank checklist (87 items across 4 sections)
- [`checklist.json`](checklist.json) — source of truth (machine-readable)

**View verification results:**
- [`output/results.xlsx`](output/results.xlsx) — results from running the checklist against Nubert electronic GmbH 2023 FS
- [`results.json`](results.json) — raw verification results

**Reproduce the outputs:**
```bash
pip install openpyxl
python3 generate_excel.py          # regenerates output/checklist.xlsx
python3 generate_results_excel.py  # regenerates output/results.xlsx
```

---

## Scope & Assumptions

| Dimension | Choice |
|---|---|
| **Entity type** | GmbH — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB) |
| **Reporting framework** | HGB §§ 264 ff. |
| **P&L format** | Gesamtkostenverfahren (§ 275 Abs. 1 HGB) |
| **Reporting components** | Bilanz, Gewinn- und Verlustrechnung, Anhang, Lagebericht |
| **Applicable date** | Financial years ending 31 December 2023 |
| **Focus** | Disclosure requirements only — not recognition or measurement |

**Out of scope:** Konzernabschluss, Kapitalflussrechnung, Segmentberichterstattung, sector-specific formats, requirements introduced after 1 January 2024 (including revised § 267 size thresholds and CSRD-related disclosures).

**Size exemptions:** § 288 Abs. 1 HGB (small entity) does not apply.

---

## Repository Structure

```
dnl-challenge-repo/
│
├── checklist.json              # 87 checklist items (source of truth)
├── schema.json                 # JSON schema for validation
├── scope.md                    # Detailed scope manifest with system context
│
├── generate_excel.py           # JSON → Excel converter (checklist)
├── generate_results_excel.py   # JSON + results → Excel converter (verification)
│
├── results.json                # Verification results (87 items, Y/N/N/A/Review)
├── verification_report.md      # Quality assurance report from verification agent
│
├── nubert_fs_2023.txt          # Extracted text of Nubert electronic GmbH 2023 FS
├── Nubert electronic GmbH 2023 FS.pdf  # Source PDF
│
├── output/
│   ├── checklist.xlsx          # Blank checklist (deliverable A)
│   └── results.xlsx            # Verification results against Nubert FS
│
└── README.md                   # This file
```

### Key files explained

| File | Role |
|---|---|
| `checklist.json` | The living checklist. Every item has: `id`, `section`, `sub_section`, `disclosure_item` (audit question), `hgb_reference`, `obligation` (M/C), `trigger_condition`, `completeness_prompt` |
| `schema.json` | Validates checklist.json structure. Enforces required fields, obligation enum (M/C), and requires trigger_condition for conditional items |
| `results.json` | Output of running the checklist against a target entity. Each item has: `id`, `response` (Yes/No/N/A/Review), `evidence`, `notes` |
| `generate_excel.py` | Converts checklist.json into a formatted Excel workbook with Overview, per-section sheets, and a combined All Items sheet |
| `generate_results_excel.py` | Combines checklist.json + results.json into a results workbook with Summary, per-section sheets (colour-coded responses), and an Issues sheet |

---

## How the Checklist Was Built

### Agent-based workflow

The checklist was built using 4 parallel sub-agents, each responsible for one section:

```
scope.md + schema.json
        │
        ├──► Bilanz Agent    (20 items: BIL-001 to BIL-020)
        ├──► GuV Agent       (19 items: GUV-001 to GUV-019)
        ├──► Anhang Agent    (32 items: ANH-001 to ANH-032)
        └──► Lagebericht Agent (16 items: LAG-001 to LAG-016)
                │
                ▼
        checklist.json (87 items)
                │
                ▼
        generate_excel.py
                │
                ▼
        output/checklist.xlsx
```

**Why this approach:**
- **Task decomposition:** Each section is a distinct domain — separate agents can work in parallel with focused context
- **Scalability:** Adding a new section (e.g., Konzernabschluss) means adding one more agent
- **Staggered writes:** Agents were time-delayed (30s/60s/90s) to avoid write conflicts on the shared JSON file
- **Schema enforcement:** All agents wrote to the same schema, ensuring consistency

### Quality assurance

1. **Schema validation** — every item checked against schema.json
2. **Verification agent** — reviewed all 87 items for: valid HGB citations, completeness, no duplicates, correct obligation flags
3. **[REVIEW] flags** — items where the citation was uncertain were flagged for human expert verification

---

## Checklist Structure

### Distribution by section

| Section | Items | Mandatory | Conditional |
|---|---|---|---|
| Bilanz (Balance Sheet) | 20 | 11 | 9 |
| GuV (P&L) | 19 | 13 | 6 |
| Anhang (Notes) | 32 | 8 | 24 |
| Lagebericht (Management Report) | 16 | 12 | 4 |
| **Total** | **87** | **44** | **43** |

### Item format

Every checklist item contains:

```json
{
  "id": "BIL-001",
  "section": "Bilanz",
  "sub_section": "Form und Gliederung",
  "disclosure_item": "Has the balance sheet been prepared in account form (Kontoform) per §266 Abs. 1 HGB?",
  "hgb_reference": "§266 Abs. 1 HGB",
  "obligation": "M",
  "trigger_condition": null,
  "completeness_prompt": "Verify the balance sheet is presented in two-column account form with Aktiva and Passiva."
}
```

- **disclosure_item** — closed audit question answerable Yes / No / N/A
- **obligation** — M (always required) or C (conditional on trigger)
- **trigger_condition** — what triggers the C item (e.g., "Only if pension provisions exist")
- **completeness_prompt** — tells a validator agent what evidence to look for in the financial statements

### Notable items included

| Item | Description | Reference |
|---|---|---|
| MD remuneration protective clause | GmbH-specific disclosure waiver | § 286 Abs. 4 HGB |
| BilMoG transitional provisions | Unamortised BilMoG adjustment | Art. 67 EGHGB |
| GmbH capital contributions | Registered capital payment confirmation | § 42 GmbHG |
| Size exemption non-applicability | Verification that § 288 Abs. 1 is not used | § 288 Abs. 1 HGB |

---

## Proof of Concept: Nubert electronic GmbH

### What we did

Ran the 87-item checklist against the actual 2023 financial statements of Nubert electronic GmbH, a medium-sized GmbH in Schwäbisch Gmünd (HiFi manufacturer, direct sales model). The FS includes Bilanz, GuV (Gesamtkostenverfahren), Anhang, Lagebericht, and an unqualified audit opinion.

### Verification workflow

```
checklist.json + nubert_fs_2023.txt
        │
        ├──► Verify Bilanz Agent   (20 items)
        ├──► Verify GuV Agent      (19 items)
        ├──► Verify Anhang Agent   (32 items)
        └──► Verify Lagebericht Agent (16 items)
                │
                ▼
        results.json (87 results)
                │
                ▼
        generate_results_excel.py
                │
                ▼
        output/results.xlsx
```

### Results

| Metric | Value |
|---|---|
| Total items checked | 87 |
| Yes (disclosed) | 47 |
| No (missing) | 6 |
| N/A (not applicable) | 21 |
| Review (uncertain) | 13 |
| **Pass rate** | **88.7%** (47 of 53 applicable items) |

### Disclosure gaps identified (6 items marked No)

| ID | Gap | Reference |
|---|---|---|
| GUV-014 | No revenue breakdown by activity or geography; §286(2) protective clause not invoked | § 285 Nr. 4, § 286 Abs. 2 |
| ANH-002 | Currency translation methods not disclosed despite EUR 85k FX expenses | § 284 Abs. 2 Nr. 2 |
| ANH-003 | Deferred tax policy completely silent | § 284 Abs. 2 Nr. 3, § 274 |
| ANH-010 | Participations not identified by name and registered office | § 285 Nr. 11 |
| ANH-019 | Auditor's fees not broken down into four categories | § 285 Nr. 17 |
| ANH-028 | No deferred tax recognition despite material temporary differences (pensions, BilMoG, discount rate) | § 274 |

### Items flagged for Review (13)

The Review flag was applied where:
- The disclosure was present but potentially incomplete (e.g., risk management too brief)
- A key attachment was missing from the extracted text (e.g., Anlagenspiegel)
- The FS made a structural change without quantification (e.g., inventory valuation method change)
- An event occurred post-balance-sheet that wasn't discussed (e.g., new MD appointments in 11/2024)

See [`results.json`](results.json) for the full evidence and notes on each item.

---

## Reproducing the Results

### Prerequisites
```bash
pip install openpyxl
```

### Regenerate the blank checklist
```bash
python3 generate_excel.py
# Output: output/checklist.xlsx
```

### Regenerate the verification results
```bash
python3 generate_results_excel.py
# Output: output/results.xlsx
```

### Run the checklist against a different entity

1. Extract the target entity's financial statements to text (e.g., `pdftotext target.pdf target.txt`)
2. Update `results.json` with new verification results (one JSON object per checklist item with `id`, `response`, `evidence`, `notes`)
3. Run `generate_results_excel.py` to produce the new results workbook

The checklist itself (`checklist.json`) is entity-agnostic and can be reused across any medium-sized GmbH.

---

## Limitations & Trade-offs

### Scope decisions
- **Disclosure only:** This checklist covers disclosure requirements, not recognition or measurement. An auditor would use separate procedures for those.
- **Single entity type:** Scoped to GmbH only. AG (Aktiengesellschaft) would require additional items (§ 285 Nr. 9 full remuneration disclosure, Aufsichtsrat, etc.).
- **No Konzernabschluss:** Group accounts (§§ 290 ff.) are a separate, significantly larger scope.

### AI-related considerations
- **Citation accuracy:** HGB paragraph references were generated by AI and verified by a verification agent, but some may contain errors. One item (ANH-030) has a [REVIEW] flag for expert verification.
- **Completeness prompts:** Designed to guide a validator agent, but real-world verification requires human audit judgment.
- **PDF extraction:** Text extraction from PDF may miss structured data (tables, diagrams). The Nubert FS's Anlagenspiegel (Anlage 1) was referenced but not included in the extracted text.

### Scalability
- **Other frameworks:** The same JSON → agent → Excel pipeline can be adapted to IFRS, UK GAAP, or other frameworks by changing the scope manifest and section agents.
- **Different entity sizes:** Small entities (§ 288 Abs. 1) would require removing items; large entities or AG would require adding items.
- **Product integration:** The JSON structure is designed to be machine-readable and could power an automated disclosure checking tool in a product like DNL's ai/checklists.

---

## Contact

Built as part of the DNL Professional Practice Team take-home challenge.

Submission: Livia (livia.jansen-winkeln@dnl.ai) and Andreas (andreas.schindler@dnl.ai)
