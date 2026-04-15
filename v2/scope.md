# DNL Disclosure Checklist — v2 Scope Manifest

## SYSTEM CONTEXT
You are an expert in German commercial law and HGB financial reporting. You are acting as a
Checklist Drafter agent in a multi-agent audit workflow. Your task is to generate a
version-stamped, grounded disclosure checklist for auditors.

This v2 scope replaces the hardcoded year references in v1 with **relative versioning** — the
checklist is generated for a specific financial year, and amendments post-dating that year are
flagged as NOT_APPLICABLE.

---

## EXECUTION ARCHITECTURE

### Parallel Agent Execution (Recommended)
To mitigate token cost and processing time, run section drafter agents in parallel:

- **Bilanz Agent** — generates BIL-1xx items
- **GuV Agent** — generates GUV-1xx items
- **Anhang Agent** — generates ANH-3xx, 5xx items
- **Lagebericht Agent** — generates LAG-6xx items

Each agent fetches the relevant HGB sections independently, reducing the input token load per agent.
A merge step combines outputs and performs schema validation.

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

**The critical difference from v1:** Every checklist item must be traceable to a specific version
of the HGB as it existed at the target FY date.

- **Primary source:** [Buzer.de](https://www.buzer.de/) — use for version-stamped HGB text at target FY date
- **Secondary source:** [Gesetze im Internet](https://www.gesetze-im-internet.de/hgb/) — validate against official consolidated text; acknowledge that provisions may have been amended post-FY
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
- **Components in scope:** Bilanz (Balance Sheet), Gewinn- und Verlustrechnung (Profit & Loss
  Account), Anhang (Notes), Lagebericht (Management Report)
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

The agent should resolve §288 Abs. 2 exemptions at runtime by fetching the HGB text as of the target FY date. The exemptions are NOT hardcoded — they are derived from the source at generation time.

**Runtime resolution logic:**
- For each disclosure item, check if the applicable HGB paragraph includes a §288 Abs. 2 exemption clause
- If an exemption applies, mark the item as **Conditional (C)** with trigger condition: "Entity invokes §288 Abs. 2 exemption"
- This ensures the checklist reflects the exemptions valid for the target FY, not a static list

---

## YOUR TASK

Generate a version-stamped disclosure checklist with the following structure:

### Sections

1. **Bilanz (Balance Sheet)** (§ 266 HGB)
2. **Gewinn- und Verlustrechnung (Profit & Loss Account / P&L)** (§ 275 HGB)
3. **Anhang (Notes / Annex)** (§§ 284–288 HGB)
4. **Lagebericht (Management Report)** (§ 289 HGB)

> **Note on item counts:** Do NOT target a specific number. Focus on 100% extraction of statutory obligations from the grounded source. The validation script will flag if items fall below expected ranges.

### Lagebericht Sub-Section Breakdown (§ 289 HGB)

The Lagebericht must be itemised across its distinct statutory requirements — do not flatten into
a single block:

| Sub-Section | Reference | Coverage |
|-------------|-----------|----------|
| Situation report | §289 Abs. 1 HGB | Business position, performance, results |
| Risk and opportunity report | §289 Abs. 2 Nr. 1 HGB | Material risks and opportunities |
| R&D activities | §289 Abs. 2 Nr. 2 HGB | Research and development disclosure |
| Branch offices | §289 Abs. 2 Nr. 3 HGB | Existence and nature of branches |
| Forward-looking statements | §289 Abs. 2 Nr. 4 HGB | Expected developments and outlook |
| Internal control system (ICS) | §289 Abs. 4 HGB | Only where applicable to entity |

---

## OUTPUT SCHEMA (v2)

For each checklist item, output:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Serial number per convention | `HGB-ANH-042` |
| `section` | Reporting section | `Bilanz`, `GuV`, `Anhang`, `Lagebericht` |
| `sub_section` | Logical grouping | `Form und Gliederung`, `Rückstellungen` |
| `disclosure_item` | Audit question in English | "Has the balance sheet been prepared in account form?" |
| `hgb_reference` | German statutory reference | `§266 Abs. 1 HGB` |
| `version_info` | Amendment metadata | `HGB (as of 31 Dec 2023)` |
| `source_url` | Official statute URL (Gesetze im Internet) | `https://www.gesetze-im-internet.de/hgb/__266.html` |
| `obligation` | M (Mandatory) or C (Conditional) | `M` or `C` |
| `trigger_condition` | Condition for C items; null for M items | "Only if pension provisions exist" |
| `evidence_location` | Where to look in the financial statements | "Anhang, notes to provisions section" |
| `completeness_prompt` | Verification instruction for checking agent | "Verify the balance sheet is in two-column account form..." |

> **Note on `evidence_location`:** This field should describe the **semantic** section (e.g.,
> "Notes on provisions", "Management Report: Risk section") rather than assuming a specific
> numbered heading. German Mittelstand Anhang (Notes) structures vary — some follow the balance
> sheet sequence, others group by theme. Semantic descriptions are more robust against
> structural variation.

> **Note on translation:** For highly specific technical accounting terms, the English
> `disclosure_item` MUST include the original German term in parentheses. Example:
> "Are provisions for pensions (Pensionsrückstellungen) disclosed per §285 Nr. 24?"
> This provides a safety net against translation ambiguity (e.g., "Provisions" vs
> "Wertberichtigungen").

---

## SERIAL NUMBER CONVENTION

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`

| Component | Format | Example |
|-----------|--------|---------|
| Framework | 2-4 chars | `HGB`, `IFRS`, `UKG` |
| Section | 3-letter | `BIL`, `GUV`, `ANH`, `LAG` |
| Sequence | 3-digit, padded | `001`, `042`, `100` |

**Examples:**
- `HGB-BIL-001` — German GAAP, Bilanz (Balance Sheet) section
- `HGB-ANH-042` — German GAAP, Anhang (Notes) section
- `HGB-ANH-300` — German GAAP, Anhang (Notes) section, upper block

**1000-series accounting taxonomy:**

| Section | Block | Rationale |
|---------|-------|-----------|
| BIL (Assets) | 100-199 | Anlagevermögen (Fixed Assets), Umlaufvermögen (Current Assets) |
| BIL (Equity & Liab) | 200-299 | Eigenkapital (Equity), Rückstellungen (Provisions), Verbindlichkeiten (Liabilities) |
| GUV | 100-199 | P&L line items |
| ANH (§284-286) | 300-499 | Notes disclosures — §285 has 33+ numbered items, dense |
| ANH (§287-288) | 500-599 | Additional notes, exemptions |
| LAG | 600-699 | Management Report sections |

Where a block is exhausted, reserve the next 100-block for that sub-section.

---

## QUALITY REQUIREMENTS

### Grounding
- Every item must have a valid HGB reference traced to the version-stamped source
- Primary citation: Buzer.de (`https://www.buzer.de/`) — fetch HGB text @ target FY
- Secondary lookup: Gesetze im Internet (`https://www.gesetze-im-internet.de/hgb/`) — validate against official consolidated text; note provisions may have been amended post-FY
- Cross-check that the cited provision existed and was in force as of 31 December 2023

### Completeness
- Phrase all items as closed questions (Yes / No / N/A / Review)
- Include all mandatory disclosures for medium GmbH
- Include conditional items for commonly occurring scenarios
- Mark items affected by §288 Abs. 2 as Conditional (C)
- **Thoroughness over count:** do not compress distinct requirements into a single item to
  meet a target; if two statutory sub-clauses carry independent disclosure obligations, they
  are two checklist items

### Verification Integration
- Each item must include a `completeness_prompt` — the verification instruction for the
  checking agent
- Each item must include an `evidence_location` — the specific part of the financial
  statements where the evidence is expected
- The `completeness_prompt` should specify what to look for; `evidence_location` specifies
  where to look

### Validation
- After generating, perform self-check:
  - All items have valid `hgb_reference`
  - All items have `source_url` resolving to Gesetze im Internet
  - No mixing of sections in sequence blocks
  - `trigger_condition` is populated for all C items and null for all M items
  - `evidence_location` is populated for every item
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

---

## SEPARATION OF CONCERNS NOTE

This file (`scope.md`) defines parameters and configuration only. Agent system prompts,
orchestration logic, and tool definitions are maintained separately. If adapting this scope
for a different framework (IFRS, UK GAAP) or entity type, only this file requires updating —
agent instructions remain unchanged.

---

## LANGUAGE ASSUMPTION

> This checklist is designed for English-speaking audit teams working with German HGB source
> material. The `hgb_reference` field provides the German statutory citation for
> cross-verification. Output is in English; source text is German.
