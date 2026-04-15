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
| Serial numbers | Sequential (BIL-001) | `HGB-ANH-042` format with block reservation |
| Response methodology | Undefined | Defined reason_code taxonomy |
| Language | Mixed DE/EN | English-only (with source trace) |

## Language Assumption

> "This checklist is designed for English-speaking audit teams working with German HGB source material. The `hgb_reference` field provides the German statutory citation for cross-verification. Output is in English; source text is German. Reviewers should cross-check English prompts against German source where fidelity is critical."

---

## Feedback Point Mapping

| # | Feedback Point | v2 Solution |
|---|----------------|--------------|
| 1 | No grounding of standards | Version-stamped sources via Buzer.de + official source |
| 2 | Mix of English/German | English-only output with DE source trace |
| 3 | Serial numbers unclear | `HGB-ANH-042` format with block reservation |
| 4 | Yes/No/Review undefined | 8-code reason_code taxonomy + confidence levels |
| 5 | Limited skill.md testing | Testing protocol included |

---

## Data Schema

### Field Definitions

#### checklist.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `HGB-BIL-001`) |
| `section` | string | Yes | Reporting section (`Bilanz`, `GuV`, `Anhang`, `Lagebericht`) |
| `sub_section` | string | Yes | Logical grouping within section |
| `disclosure_item` | string | Yes | Audit question in English |
| `hgb_reference` | string | Yes | German statutory reference (e.g., `§266 Abs. 1 HGB`) |
| `version_info` | string | Yes | Amendment metadata (e.g., `BilRUG (23.07.2015)`) |
| `source_url` | string | Yes | Official statute URL (gesetze-im-internet.de) |
| `version_url` | string | No | Buzer.de navigation link for version |
| `obligation` | string | Yes | `M` (Mandatory) or `C` (Conditional) |
| `trigger_condition` | string | No | Condition that triggers C items |
| `completeness_prompt` | string | Yes | Verification instruction for checking agent |

#### results.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Matches checklist item ID |
| `response` | string | Yes | `Yes`, `No`, `N/A`, or `Review` |
| `reason_code` | string | No | Taxonomy code (see Reason Code Taxonomy) |
| `confidence` | string | No | `High`, `Medium`, or `Low` |
| `evidence` | string | No | Specific evidence from FS |
| `audit_notes` | string | No | Auditor judgment notes |
| `verified_by` | string | Yes | Agent or auditor name |
| `verification_date` | string | Yes | ISO date (YYYY-MM-DD) |

---

## Serial Number Convention

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`

| Component | Format | Example |
|-----------|--------|---------|
| Framework | Variable (2-4 chars) | `HGB`, `IFRS`, `UKG`, `IAS` |
| Section | 3-letter | `BIL`, `GUV`, `ANH`, `LAG` |
| Sequence | 3-digit, padded | `001`, `042` |

**Full ID examples:** 
- `HGB-ANH-042` (German GAAP)
- `IFRS-ANN-042` (IAS/IFRS)
- `UKG-PLN-042` (UK GAAP)

### Block Reservation (No Decimals)

To ensure stable IDs across FYs and avoid decimal accumulation, sequence blocks are reserved per sub-section:

| Section | Sub-Section | ID Range | Slots |
|---------|-------------|----------|-------|
| BIL | Form und Gliederung | BIL-001 to BIL-050 | 50 |
| BIL | Anlagevermögen | BIL-051 to BIL-100 | 50 |
| BIL | Umlaufvermögen | BIL-101 to BIL-150 | 50 |
| BIL | Eigenkapital | BIL-151 to BIL-200 | 50 |
| BIL | Rückstellungen | BIL-201 to BIL-250 | 50 |
| BIL | Verbindlichkeiten | BIL-251 to BIL-300 | 50 |
| BIL | Latente Steuern | BIL-301 to BIL-350 | 50 |
| GUV | Darstellungsform | GUV-001 to GUV-050 | 50 |
| GUV | Pflichtpositionen | GUV-051 to GUV-100 | 50 |
| GUV | Anhangangaben zur GuV | GUV-101 to GUV-150 | 50 |
| ANH | §284 | ANH-001 to ANH-050 | 50 |
| ANH | §285 | ANH-051 to ANH-100 | 50 |
| ANH | §286 | ANH-101 to ANH-150 | 50 |
| ANH | §287 | ANH-151 to ANH-200 | 50 |
| ANH | §288 | ANH-201 to ANH-250 | 50 |
| LAG | Allgemeine Anforderungen | LAG-001 to LAG-050 | 50 |
| LAG | Geschäftsverlauf | LAG-051 to LAG-100 | 50 |
| LAG | Risikobericht | LAG-101 to LAG-150 | 50 |
| LAG | Prognosebericht | LAG-151 to LAG-200 | 50 |

**Insertion rule:** Use the next available slot within the allocated block. No decimals. Sorting and downstream tooling remain stable.

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
| `High` | Clear evidence, unambiguous |
| `Medium` | Evidence present but some interpretation required |
| `Low` | Ambiguous or insufficient evidence |

---

## Agent Workflow

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
│ - Fetch English terminology from gesetze-im-internet.de                   │
│ - Flag amendments POST_FY as NOT_APPLICABLE                               │
│ - Freeze version_info into metadata                                       │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: SECTION DRAFTER AGENTS (4x parallel)                               │
│ - Generate checklist items with:                                           │
│   • hgb_reference (German source)                                          │
│   • version_info (amendment metadata)                                      │
│   • source_url (official) + version_url (Buzer navigation)                │
│   • completeness_prompt (verification instruction)                        │
│ - Use serial number convention (HGB-XXX-XXX)                              │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: MERGE & VALIDATE                                                   │
│ - Schema validation                                                       │
│ - Version diff check (post-FY amendments flagged)                                │
│ - Citation validation: regex check paragraph format, verify URL resolves │
│ - Serial number formatting                                                │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 4: VERIFICATION AGENT                                                 │
│ - Receives: checklist item + completeness_prompt + FS text                │
│ - Outputs: response + reason_code + confidence + evidence                 │
│ - Uses defined taxonomy for Review items                                  │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 5: EXCEL FORMATTER                                                    │
│ - Generates audit-ready .xlsx                                             │
│ - Includes: version, reason_code, confidence, source_url columns          │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 6: HUMAN REVIEW                                                      │
│ - SME reviews reason_code items                                           │
│ - Verifies version metadata for FY accuracy                              │
│ - Sign-off on "No" findings                                                │
└─────────────────────────────────────────────────────────────────────────────┘
        │
        ▼
OUTPUT: Grounded checklist + verification results + audit trail
```

---

## Authoritative Sources

| Purpose | Source | URL |
|---------|--------|-----|
| Primary (statute text) | Gesetze im Internet | https://www.gesetze-im-internet.de/hgb/ |
| Navigation (version lookup) | Buzer.de | https://www.buzer.de/ |
| Historical versions | Buzer.de | https://www.buzer.de/266_HGB.htm |

**Note:** Buzer.de is used as a navigation aid for version-specific lookups. The `source_url` field points to the official statute for audit defensibility.

---

## Cost Profile

v1 was ~$0.08/run. v2 adds incremental token costs:

| Component | v1 Tokens | v2 Additional | Rationale |
|-----------|-----------|---------------|-----------|
| Step 1: Version fetch | +0 | +2k input | Scoping agent fetches Buzer @ FY |
| Step 3: Citation validation | +0 | +1.5k input | Regex check + URL resolution |
| Step 4: reason_code output | +0 | +1.5k output | Adds 2 fields per item (~87 items) |
| **Total delta** | — | **+5k tokens** | |

**Revised estimate:**
- v1: ~78k in / 38k out → **$0.08**
- v2: ~83k in / 43k out → **$0.10-0.12** per run

At scale: 100 entities/year ≈ $10-12 (vs $8 for v1)

---

## Testing Protocol

v1 feedback point 5 noted limited testing of the skill.md file. v2 includes a formal testing protocol:

### Test Categories

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| Schema validation | All checklist items conform to field types | 0 validation errors |
| Citation format | HGB references match `§### Abs. # Nr. # HGB` pattern | 100% match |
| Source URL resolution | All `source_url` fields return HTTP 200 | 100% pass |
| Version snapshot | Metadata `version_info` matches FY cut-off | No post-FY amendments |
| Reason code coverage | All Review responses have valid reason_code | No null codes on Review |
| Confidence distribution | Mix of High/Medium/Low across results | At least 2 levels present |

### Test Execution

```bash
# 1. Schema validation
python validate_schema.py checklist.json

# 2. Citation format check
python validate_citations.py checklist.json

# 3. URL resolution
python validate_urls.py checklist.json

# 4. Version snapshot check
python validate_version.py checklist.json --fy 2023-12-31

# 5. Reason code coverage
python validate_reason_codes.py results.json
```

---

## Limitations & Human Oversight

- **Source fidelity:** English output introduces translation gap from German source
- **Version drift:** Checklist version frozen at generation; re-generate for new FY
- **PDF extraction:** Complex tables (Anlagenspiegel) may not be captured
- **Human sign-off:** Always required for "No" findings and Review items

---

## Extending to Other Frameworks

To adapt for IFRS or UK GAAP:
1. Update `hgb_reference` → `standard_reference`
2. Change framework code (e.g., `IFR-ANN-042`)
3. Update source URLs for target framework
4. Adjust size class thresholds as needed

---

*Specification version: 2.1*
*Last updated: 2026-04-15*
