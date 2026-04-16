# German GAAP Checklist Generator Skill

## Scope
Generates version-stamped HGB disclosure checklist for **medium GmbH** (§267 Abs. 2).

This skill is pre-configured for the most common German audit scenario and produces audit-ready checklists grounded in German statute text.

---

## Entity Context (Fixed)

| Parameter | Value |
|-----------|-------|
| Framework | HGB (German Commercial Code) §§ 264 ff. |
| Entity type | GmbH (Private Limited Company) |
| Size class | Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB) |
| Exemptions | §288 Abs. 2 apply |

---

## User Parameters (Required)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `entity_name` | Company name | Nubert electronic GmbH |
| `target_fy` | Financial year end date | 31 December 2023 |
| `pl_format` | P&L format | Gesamtkostenverfahren |

---

## ID Convention (10K Series)

| Section | Block | Range |
|---------|-------|-------|
| Bilanz (Assets) | Fixed Assets | 10000-19999 |
| Bilanz (Equity & Liab) | Equity & Liabilities | 20000-29999 |
| GuV | Profit & Loss | 30000-39999 |
| Anhang (§284-286) | Notes Part 1 | 40000-49999 |
| Anhang (§287-288) | Notes Part 2 | 50000-59999 |
| Lagebericht | Management Report | 60000-69999 |

**Format:** `{FRAMEWORK}-{SECTION}-{SEQUENCE}`
- Example: `HGB-BIL-10001`, `HGB-ANH-40420`, `HGB-LAG-60001`

---

## Section Agents

Run these agents in parallel:

### Bilanz Agent
- Generates: BIL-10000 to BIL-29999
- Coverage: §266 HGB (balance sheet structure)

### GuV Agent
- Generates: GUV-30000 to GUV-39999
- Coverage: §275 HGB (P&L formats and line items)

### Anhang Agent
- Generates: ANH-40000 to ANH-59999
- Coverage: §§ 284-288 HGB (notes disclosures)

### Lagebericht Agent
- Generates: LAG-60000 to LAG-69999
- Coverage: §289 HGB (management report)

---

## Version Stamping

Each checklist item must be traceable to a specific version of the HGB as of the target FY date.

- **Primary source:** Buzer.de (version-stamped text)
- **Secondary source:** Gesetze im Internet (official consolidated)
- **Version metadata:** Store as `version_info` field (e.g., "HGB (as of 31 Dec 2023)")

---

## §288 Abs. 2 Exemptions

For medium GmbH, these items are exempt from disclosure:

| §285 Ref | Disclosure |
|----------|-------------|
| Nr. 4 | Revenue breakdown by activity/geography |
| Nr. 8 | Material cost breakdown |
| Nr. 9 | Personnel cost breakdown |
| Nr. 17 | Related party (controlling entity) |
| Nr. 21 | IFRS transition disclosure |
| Nr. 29 | Auditor fees |
| Nr. 32 | Related party disclosures |

**Action:** Mark these as `obligation: "C"` with `trigger_condition: "Exempt for medium GmbH per §288 Abs. 2"`

---

## Output Schema

### checklist.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID (e.g., `HGB-BIL-10001`) |
| `section` | string | Yes | Bilanz, GuV, Anhang, Lagebericht |
| `sub_section` | string | Yes | Logical grouping |
| `disclosure_item` | string | Yes | Audit question in English |
| `hgb_reference` | string | Yes | German statutory reference |
| `version_info` | string | Yes | Amendment metadata |
| `source_url` | string | Yes | Gesetze im Internet URL |
| `obligation` | string | Yes | M (Mandatory) or C (Conditional) |
| `trigger_condition` | string | No | Condition for C items |
| `evidence_location` | string | Yes | Semantic location in FS |
| `completeness_prompt` | string | Yes | Verification instruction |

### results.json

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Matches checklist item ID |
| `response` | string | Yes | Yes, No, N/A, Review |
| `reason_code` | string | No | Reason code taxonomy |
| `confidence` | string | No | High, Medium, Low |
| `evidence` | string | No | Specific evidence |
| `verified_by` | string | Yes | Agent name |
| `verification_date` | string | Yes | YYYY-MM-DD |

---

## Reason Code Taxonomy

| Code | Definition |
|------|------------|
| `MISSING_EVIDENCE` | Required disclosure not found |
| `PARTIAL_DISCLOSURE` | Some elements present, others missing |
| `JUDGMENT_REQUIRED` | Requires auditor interpretation |
| `AMBIGUOUS_LANGUAGE` | FS language unclear |
| `EXEMPTION_CLAIMED` | Entity invoked §288 exemption |
| `POST_BS_EVENT` | Post-balance-sheet event |
| `PDF_EXTRACTION_LIMIT` | Data not in text extract |
| `ENTITY_SPECIFIC` | Not applicable to entity type |

---

## Quality Requirements

### Grounding
- Every item has valid HGB reference
- Source URL resolves to Gesetze im Internet
- Version metadata matches target FY

### Completeness
- All mandatory disclosures for medium GmbH included
- §288 exemptions marked as Conditional (C)
- Each item has evidence_location and completeness_prompt

### Validation
- All items have valid hgb_reference
- No mixing of sections in ID blocks
- C items have trigger_condition populated

---

## Running the Generator

### Input:
```json
{
  "entity_name": "Nubert electronic GmbH",
  "target_fy": "31 December 2023",
  "pl_format": "Gesamtkostenverfahren"
}
```

### Output:
- `checklist.json` — 173 items (typical for medium GmbH)
- Metadata includes entity context and version info

---

## Limitations

- Entity type is fixed to medium GmbH
- Single financial year (no comparative FY)
- No group accounts (Konzernabschluss)
- No large entity requirements

To extend: Fork for AG, large GmbH, or group scenarios.

---

*Skill Version: 1.0*
*Last Updated: 2026-04-16*
