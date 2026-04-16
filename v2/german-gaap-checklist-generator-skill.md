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

## Section Agents (Parallel Execution)

### Coordination Layer
When running agents in parallel:

1. **Output format:** Each agent outputs a JSON array of checklist items
2. **Merge:** Combine all arrays, check for duplicate IDs
3. **Deduplicate:** If same ID appears, keep the first occurrence
4. **Validate:** Run schema validation on combined output

### Bilanz Agent
- Generates: BIL-10000 to BIL-29999
- Coverage: §266 HGB (balance sheet structure)

### GuV Agent
- Generates: GUV-30000 to GUV-39999
- Coverage: §275 HGB (P&L formats and line items)
- **Note:** If `pl_format = Umsatzkostenverfahren`, generate §275 Abs. 2 items instead of Abs. 1

### Anhang Agent
- Generates: ANH-40000 to ANH-59999
- Coverage: §§ 284-288 HGB (notes disclosures)

### Lagebericht Agent
- Generates: LAG-60000 to LAG-69999
- Coverage: §289 HGB (management report)

---

## Version Stamping (INSTRUCTIONAL)

The version_info field must be **derived**, not hallucinated.

### How to Derive Version Info:

1. **Fetch from Buzer.de:**
   ```
   https://www.buzer.de/[PARAGRAPH]_HGB.htm
   ```
   Look for the version date at the top of the page.

2. **Fetch from Gesetze im Internet:**
   ```
   https://www.gesetze-im-internet.de/hgb/__[PARAGRAPH].html
   ```
   Note the "Stand" (as of date) at the top.

3. **Format the version_info:**
   ```
   HGB (as of DD Mon YYYY)
   ```
   Examples:
   - "HGB (as of 31 Dec 2023)"
   - "§266 Abs. 2 (as of 1 Jan 2024)"
   - "BilRUG (23.07.2015)" - for specific amendment laws

4. **For each item:** Copy the specific provision's version date as version_info

### Example:
```json
{
  "hgb_reference": "§266 Abs. 2 HGB",
  "version_info": "HGB (as of 31 Dec 2023)",
  "source_url": "https://www.gesetze-im-internet.de/hgb/__266.html"
}
```

---

## §288 Abs. 2 Exemptions (VERIFIED)

**For medium GmbH (§267 Abs. 2), these §285 items are EXEMPT:**

| §285 Ref | Disclosure | Notes |
|----------|-------------|-------|
| Nr. 4 | Revenue breakdown by activity/geography | |
| Nr. 17 | Related party (controlling) | |
| Nr. 21 | IFRS transition | |
| Nr. 29 | Auditor fees | |
| Nr. 32 | Related party disclosures | |
| Nr. 33 | Key management compensation | |

**Action for exempt items:**
```json
{
  "obligation": "C",
  "trigger_condition": "Exempt for medium GmbH per §288 Abs. 2 HGB"
}
```

---

## pl_format Gating

The `pl_format` parameter **MUST** gate which §275 items are included:

### If Gesamtkostenverfahren (§275 Abs. 1):
- Generate items for total cost method (items 1-21)
- Include: Materialaufwand, Personalaufwand, etc.

### If Umsatzkostenverfahren (§275 Abs. 2):
- Generate items for cost of sales method (items 1-21)
- Include: Herstellungskosten, Vertriebskosten, etc.

**The GuV agent MUST check this parameter and select the appropriate HGB reference.**

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
| `version_info` | string | Yes | Derived version metadata |
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
- Version metadata is **derived** (fetched, not hallucinated)

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

### Process:
1. Fetch HGB text from Buzer.de/Gesetze im Internet for target FY
2. Spawn 4 section agents in parallel
3. Each agent generates items with derived version_info
4. Merge outputs (keep first on duplicates), validate schema
5. Output checklist.json with metadata

### Output:
- `checklist.json` — item count varies by entity profile and pl_format
- Metadata includes entity context and version info

---

## Limitations

- Entity type is fixed to medium GmbH
- Single financial year (no comparative FY)
- No group accounts (Konzernabschluss)
- No large entity requirements

To extend: Fork for AG, large GmbH, or group scenarios.

---

*Skill Version: 1.2*
*Last Updated: 2026-04-16*
