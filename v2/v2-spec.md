# HGB Disclosure Checklist — v2 Specification

## Overview
v2 of the HGB disclosure checklist addresses five feedback points from the v1 submission and introduces a version-stamped, grounded methodology for audit-ready disclosure verification.

## Scope
- **Entity type:** GmbH — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)
- **Target FY:** 31 December 2023
- **Framework:** German GAAP (HGB §§ 264 ff.)
- **Output language:** English (with explicit documentation of German source fidelity)

---

## v1 vs v2 Summary

| Aspect | v1 | v2 |
|--------|----|----|
| Source grounding | AI-generated citations | Version-stamped, source-verified |
| Authoritative source | Not specified | gesetze-im-internet.de (Buzer for navigation) |
| Versioning | None | Frozen at generation time |
| Serial numbers | Sequential (BIL-001) | `HGB-BIL-10000` format (5-digit, 10K series) |
| Response methodology | Undefined | Defined reason_code taxonomy |
| Language | Mixed DE/EN | English-only (with DE source trace) |
| Exemption handling | None | §288 Abs. 2 triggers for conditional items |
| Evidence extraction | Generic | Specific page numbers + amounts |

---

## Language Assumption

> "This checklist is designed for English-speaking audit teams working with German HGB source material. The `hgb_reference` field provides the German statutory citation for cross-verification. Output is in English; source text is German. Reviewers should cross-check English prompts against German source where fidelity is critical."

---

## Feedback Point Mapping

| # | Feedback Point | v2 Solution |
|---|----------------|--------------|
| 1 | No grounding of standards | Version-stamped sources via Buzer.de + official source |
| 2 | Mix of English/German | English-only output with DE source trace |
| 3 | Serial numbers unclear | `HGB-BIL-10000` format with 5-digit block reservation |
| 4 | Yes/No/Review undefined | 8-code reason_code taxonomy + confidence levels |
| 5 | Limited skill.md testing | Full end-to-end workflow tested with Nubert FS |

---

## Data Schema

### Field Definitions

#### checklist.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `HGB-BIL-10000`) |
| `section` | string | Yes | Reporting section (`Bilanz`, `GuV`, `Anhang`, `Lagebericht`) |
| `sub_section` | string | Yes | Logical grouping within section |
| `disclosure_item` | string | Yes | Audit question in English |
| `hgb_reference` | string | Yes | German statutory reference (e.g., `§266 Abs. 1 HGB`) |
| `version_info` | string | Yes | Amendment metadata (e.g., `HGB (as of 31 Dec 2023)`) |
| `source_url` | string | Yes | Official statute URL (gesetze-im-internet.de) |
| `obligation` | string | Yes | `M` (Mandatory) or `C` (Conditional) |
| `trigger_condition` | string | No | Condition for C items (e.g., §288 Abs. 2 exemption) |
| `evidence_location` | string | Yes | Semantic location in FS |
| `completeness_prompt` | string | Yes | Verification instruction for checking agent |

#### results.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Matches checklist item ID |
| `response` | string | Yes | `Yes`, `No`, `N/A`, or `Review` |
| `reason_code` | string | No | Taxonomy code (see Reason Code Taxonomy) |
| `confidence` | string | No | `High`, `Medium`, or `Low` |
| `evidence` | string | No | Specific evidence (page #, amounts, German terms) |
| `audit_notes` | string | No | Auditor judgment notes |
| `verified_by` | string | Yes | Agent or auditor name |
| `verification_date` | string | Yes | ISO date (YYYY-MM-DD) |

---

## Serial Number Convention (v2 - 10K Series)

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`

| Component | Format | Example |
|-----------|--------|---------|
| Framework | 2-4 chars | `HGB`, `IFRS`, `UKG` |
| Section | 3-letter | `BIL`, `GUV`, `ANH`, `LAG` |
| Sequence | 5-digit, padded | `10000`, `20000`, `30000` |

**Full ID examples:** 
- `HGB-BIL-10000` — German GAAP, Bilanz (Assets section)
- `HGB-ANH-40420` — German GAAP, Anhang (§284-286 section)
- `HGB-LAG-60001` — German GAAP, Lagebericht

### Block Reservation (v2 - 10K Series)

| Section | Block | Range | Rationale |
|---------|-------|-------|-----------|
| BIL (Assets) | Fixed Assets | 10000-19999 | Anlagevermögen, Umlaufvermögen |
| BIL (Equity & Liab) | Equity & Liab | 20000-29999 | Eigenkapital, Rückstellungen, Verbindlichkeiten |
| GUV | P&L | 30000-39999 | Profit & Loss line items |
| ANH (§284-286) | Notes Part 1 | 40000-49999 | §284-286 disclosures (dense, 33+ items) |
| ANH (§287-288) | Notes Part 2 | 50000-59999 | Additional notes, exemptions |
| LAG | Management Report | 60000-69999 | §289 sub-sections |

**Insertion rule:** Use the next available slot within the allocated block. No decimals. Sorting and downstream tooling remain stable.

---

## §288 Abs. 2 Exemption Handling

For medium GmbH (§267 Abs. 2 HGB), certain §285 disclosures are exempt:

| §285 Reference | Disclosure | Trigger Condition |
|----------------|------------|-------------------|
| Nr. 4 | Revenue breakdown by activity/geography | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 8 | Material cost breakdown | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 9 | Personnel cost breakdown | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 17 | Related party (controlling) | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 21 | IFRS transition | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 29 | Auditor fees | "Exempt for medium GmbH per §288 Abs. 2" |
| Nr. 32 | Related party disclosures | "Exempt for medium GmbH per §288 Abs. 2" |

These items are marked as `obligation: "C"` (Conditional) with `trigger_condition` explaining the exemption.

---

## Reason Code Taxonomy

| Code | Definition | Example |
|------|------------|---------|
| `MISSING_EVIDENCE` | Required disclosure not found in FS | Deferred tax policy silent |
| `PARTIAL_DISCLOSURE` | Some elements present, others missing | Revenue disclosed, geography missing |
| `JUDGMENT_REQUIRED` | Requires auditor interpretation | "Material" not quantified |
| `AMBIGUOUS_LANGUAGE` | FS language unclear | "We comply with regulations" |
| `EXEMPTION_CLAIMED` | Entity invoked §288 Abs. 2 | Revenue breakdown waived |
| `POST_BS_EVENT` | Post-balance-sheet event | MD appointment 11/2024 |
| `PDF_EXTRACTION_LIMIT` | Data not in text extract | Anlagenspiegel not captured |
| `ENTITY_SPECIFIC` | Not applicable to entity type | AG-only requirement on GmbH |

---

## Confidence Levels

| Level | Definition |
|-------|------------|
| `High` | Specific page #, amounts, German terminology cited |
| `Medium` | Evidence present but no specific details |
| `Low` | Inferred or uncertain |

---

## Agent Workflow (v2)

```
INPUT: scope.md
        │
        │ (contains: entity type, FY, framework, size class)
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: SCOPING AGENT                                                      │
│ - Parse scope.md for target FY                                            │
│ - Fetch German source from Buzer.de @ FY date (snapshot)                  │
│ - Flag amendments POST_FY as NOT_APPLICABLE                               │
│ - Freeze version_info into metadata                                       │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: SECTION DRAFTER AGENTS (4x parallel)                               │
│ - Bilanz Agent: HGB-BIL-10000 to 29999                                     │
│ - GuV Agent: HGB-GUV-30000 to 39999                                        │
│ - Anhang Agent: HGB-ANH-40000 to 59999                                     │
│ - Lagebericht Agent: HGB-LAG-60000 to 69999                               │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: MERGE & VALIDATE                                                   │
│ - Schema validation                                                       │
│ - §288 exemption trigger validation                                      │
│ - Citation format check (regex)                                            │
│ - Serial number range validation                                          │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: VERIFICATION AGENT (via verification-scope.md)                    │
│ - Check §288 exemption BEFORE PDF search                                 │
│ - Extract text using pdftotext                                             │
│ - Cite specific page numbers + amounts                                    │
│ - Apply response mapping                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: EXCEL FORMATTER                                                    │
│ - Generates audit-ready .xlsx                                             │
│ - Includes: version_info, source_url, reason_code, confidence, evidence  │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
OUTPUT: checklist.json + results.json + Excel exports
```

---

## Authoritative Sources

| Purpose | Source | URL |
|---------|--------|-----|
| Primary (statute text) | Gesetze im Internet | https://www.gesetze-im-internet.de/hgb/ |
| Navigation (version lookup) | Buzer.de | https://www.buzer.de/ |
| Historical versions | Buzer.de | https://www.buzer.de/266_HGB.htm |

---

## Test Run Results (Nubert electronic GmbH 2023)

Real verification against actual financial statements:

| Metric | Value |
|--------|-------|
| Checklist items | 173 |
| Yes (compliant) | 83 |
| No (gaps) | 46 |
| N/A (§288 exempt) | 21 |
| Review (PDF limits) | 23 |
| Pass rate | 64.3% |

**Findings:**
- Balance sheet properly structured per §266
- GuV uses Gesamtkostenverfahren correctly per §275
- §288 exemptions applied for medium GmbH disclosures
- True gaps: detailed inventory breakdown, deferred tax details, capital reserve changes

---

## Cost Profile

| Component | Tokens | Estimated Cost |
|-----------|--------|----------------|
| Checklist generation (4 agents) | ~120k in / 40k out | $0.12 |
| Verification (1 agent) | ~100k in / 25k out | $0.08 |
| **Total per entity** | ~220k tokens | **$0.20** |

At scale: 100 entities/year ≈ $20

---

## Files Generated

| File | Description |
|------|-------------|
| `v2/scope.md` | Scoping parameters and agent configuration |
| `v2/verification-scope.md` | Verification agent instructions |
| `v2/checklist.json` | 173 disclosure items |
| `v2/results.json` | Verification results |
| `v2/output/checklist.xlsx` | Checklist Excel export |
| `v2/output/results.xlsx` | Results Excel export |
| `v2/generate_excel.py` | Checklist to Excel |
| `v2/generate_results_excel.py` | Results to Excel |

---

## Limitations & Human Oversight

- **Source fidelity:** English output introduces translation gap from German source
- **Version drift:** Checklist version frozen at generation; re-generate for new FY
- **PDF extraction:** Complex tables (Anlagenspiegel) may not be fully captured
- **Human sign-off:** Always required for "No" findings and Review items
- **§288 exemptions:** Must verify entity qualifies as medium GmbH

---

## Extending to Other Frameworks

To adapt for IFRS or UK GAAP:
1. Update `hgb_reference` → `standard_reference`
2. Change framework code (e.g., `IFR-ANN-40420`)
3. Update serial number blocks for new framework
4. Adjust exemption logic for entity size classes

---

*Specification version: 2.2*
*Last updated: 2026-04-15*
