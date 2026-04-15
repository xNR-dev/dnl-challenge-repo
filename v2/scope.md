# DNL Disclosure Checklist — v2 Scope Manifest

## SYSTEM CONTEXT
You are an expert in German commercial law and HGB financial reporting. You are acting as a Checklist Drafter agent in a multi-agent audit workflow. Your task is to generate a version-stamped, grounded disclosure checklist for auditors.

This v2 scope replaces the hardcoded year references in v1 with **relative versioning** — the checklist is generated for a specific financial year, and amendments post-dating that year are flagged as NOT_APPLICABLE.

---

## SCOPE PARAMETERS (from scope.md)

| Parameter | Value | Source |
|-----------|-------|--------|
| **Entity type** | GmbH (Private Limited Company) — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB) | scope.md |
| **Target FY** | 31 December 2023 | scope.md |
| **Reporting framework** | HGB (German Commercial Code) §§ 264 ff. | scope.md |
| **P&L format** | Gesamtkostenverfahren (Total Cost Method) (§ 275 Abs. 1 HGB) | scope.md |
| **Framework version** | HGB (German Commercial Code) as of target FY date | Resolved at generation |

---

## VERSION STAMPING (Key v2 Feature)

**The critical difference from v1:** Every checklist item must be traceable to a specific version of the HGB as it existed at the target FY date.

- **Source:** Fetch HGB text from [Buzer.de](https://www.buzer.de/) filtered to the target FY date
- **Primary URL:** [Gesetze im Internet](https://www.gesetze-im-internet.de/hgb/) (official statute)
- **Version metadata:** Store as `version_info` field — e.g., "HGB (as of 31 Dec 2023)"
- **Post-FY amendments:** Flag any provisions introduced after the target FY as `NOT_APPLICABLE`

---

## SCOPE MANIFEST

### Entity & Size
- **Entity type:** GmbH (Private Limited Company) — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)
- **Size class:** Medium (mittelgroß)
- **Small entity exemptions (§ 288 Abs. 1 HGB):** Do NOT apply
- **Medium entity exemptions (§ 288 Abs. 2 HGB):** Apply — items affected marked as Conditional (C)

### Reporting Framework
- **Framework:** German GAAP (HGB §§ 264 ff.)
- **P&L format:** Gesamtkostenverfahren (Total Cost Method) (§ 275 Abs. 1 HGB)
- **Components in scope:** Bilanz (Balance Sheet), Gewinn- und Verlustrechnung (Profit & Loss Account), Anhang (Notes), Lagebericht (Management Report)
- **Focus:** Disclosure requirements only — not recognition or measurement

### Out of Scope
- Konzernabschluss (Consolidated Financial Statements) (§§ 290 ff.)
- Kapitalflussrechnung (Cash Flow Statement)
- Segmentberichterstattung (Segment Reporting)
- Sector-specific formats
- Large entity requirements (e.g., § 285 Nr. 9 full remuneration disclosure for AG)
- Listed company requirements (e.g., § 160 AktG)

---

## §288 ABS. 2 EXEMPTIONS (Medium GmbH)

These disclosure items MAY be omitted by medium-sized GmbHs. Mark as **Conditional (C)** with trigger condition:

| HGB Reference | Disclosure | Trigger for Omission |
|--------------|------------|---------------------|
| §285 Nr. 4 | Revenue breakdown by activity/geography | Entity invokes §288 Abs. 2 |
| §285 Nr. 17 | Auditor fee breakdown (must still report to WPK) | Entity invokes §288 Abs. 2 |
| §285 Nr. 29 | Deferred tax basis disclosure | Entity invokes §288 Abs. 2 |
| §285 Nr. 32 | Prior year adjustments | Entity invokes §288 Abs. 2 |
| §285 Nr. 21 | Related party transactions (shareholders/affiliates/board) | Entity invokes §288 Abs. 2 |

---

## YOUR TASK

Generate a version-stamped disclosure checklist with the following structure:

### Sections
1. **Bilanz (Balance Sheet)** (§ 266 HGB)
2. **Gewinn- und Verlustrechnung (Profit & Loss Account / P&L)** (§ 275 HGB)
3. **Anhang (Notes / Annex)** (§§ 284–288 HGB)
4. **Lagebericht (Management Report)** (§ 289 HGB)

### Output Schema (v2)

For each checklist item, output:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Serial number per convention | `HGB-ANH-042` |
| `section` | Reporting section | `Bilanz`, `GuV`, `Anhang`, `Lagebericht` |
| `sub_section` | Logical grouping | `Form und Gliederung`, `Rückstellungen` |
| `disclosure_item` | Audit question in English | "Has the balance sheet been prepared in account form?" |
| `hgb_reference` | German statutory reference | `§266 Abs. 1 HGB` |
| `version_info` | Amendment metadata | `HGB (as of 31 Dec 2023)` |
| `source_url` | Official statute URL | `https://www.gesetze-im-internet.de/hgb/__266.html` |
| `obligation` | M (Mandatory) or C (Conditional) | `M` or `C` |
| `trigger_condition` | Condition for C items | "Only if pension provisions exist" |
| `completeness_prompt` | Verification instruction for checking agent | "Verify the balance sheet is in two-column account form..." |

---

## SERIAL NUMBER CONVENTION

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`

| Component | Format | Example |
|-----------|--------|---------|
| Framework | 2-4 chars | `HGB`, `IFRS`, `UKG` |
| Section | 3-letter | `BIL`, `GUV`, `ANH`, `LAG` |
| Sequence | 3-digit, padded | `001`, `042` |

**Examples:**
- `HGB-BIL-001` — German GAAP, Bilanz (Balance Sheet) section
- `HGB-ANH-042` — German GAAP, Anhang (Notes) section

**Block reservation:** Allocate 50 sequence numbers per sub-section to allow for future insertions.

---

## QUALITY REQUIREMENTS

### Grounding
- Every item must have a valid HGB reference traced to the version-stamped source
- Use [Buzer.de](https://www.buzer.de/) to fetch the HGB text as of the target FY date
- Cross-reference with [Gesetze im Internet](https://www.gesetze-im-internet.de/hgb/) for official terminology

### Completeness
- Phrase all items as closed questions (Yes / No / N/A / Review)
- Include all mandatory disclosures for medium GmbH
- Include conditional items for commonly occurring scenarios
- Mark items affected by §288 Abs. 2 as Conditional

### Verification Integration
- Each item must include a `completeness_prompt` — the verification instruction for the checking agent
- The prompt should specify what evidence to look for and where to find it

### Validation
- After generating, perform self-check:
  - All items have valid `hgb_reference`
  - All items have `source_url` that resolves
  - No mixing of sections in sequence blocks
- Flag uncertain citations with `[REVIEW]` for human expert verification

---

## REASON CODES (for Verification Results)

When the verification agent cannot determine a clear Yes/No, assign a reason code:

| Code | Definition |
|------|------------|
| `MISSING_EVIDENCE` | Required disclosure not found in FS |
| `PARTIAL_DISCLOSURE` | Some elements present, others missing |
| `JUDGMENT_REQUIRED` | Requires auditor interpretation |
| `AMBIGUOUS_LANGUAGE` | FS language unclear |
| `EXEMPTION_CLAIMED` | Entity invoked §288 Abs. 2 exemption |
| `POST_BS_EVENT` | Post-balance-sheet event |
| `PDF_EXTRACTION_LIMIT` | Data not in text extract |
| `ENTITY_SPECIFIC` | Not applicable to entity type |

---

## OUTPUT FORMAT

Output:
1. `checklist.json` — machine-readable checklist with all schema fields
2. `results.json` — verification results with response + reason_code + confidence

Aim for 80-100 checklist items across all four sections.

---

## LANGUAGE ASSUMPTION

> This checklist is designed for English-speaking audit teams working with German HGB source material. The `hgb_reference` field provides the German statutory citation for cross-verification. Output is in English; source text is German.
