# Verification Agent Skill

## Purpose
Verify financial statements against an HGB disclosure checklist. This skill is entity-agnostic and reusable for any German GAAP audit verification.

---

## Pre-requisites

| Input | Description |
|-------|-------------|
| `checklist.json` | Generated checklist with items, obligations, triggers |
| FS PDF | Financial statements to verify against |

---

## Step 1: PDF Text Extraction

**CRITICAL:** Always pre-extract the PDF to a text file before verification.

```bash
# Extract all pages to text file
pdftotext "[PATH_TO_FS_PDF]" - > extracted-fs.txt
```

**Why:** Live PDF parsing causes timeouts and inconsistent results. Pre-extraction gives 80%+ match rate.

---

## Step 2: Exemption Resolution (BEFORE PDF Search)

For each checklist item, check exemption status FIRST:

### Decision Tree:

```
START
  │
  ├─► Is obligation = "C"?
  │     │
  │     ├─► YES → Does trigger_condition contain "§288" or "exempt"?
  │     │         │
  │     │         ├─► YES → Response = "N/A", reason_code = "EXEMPTION_CLAIMED"
  │     │         │         Evidence = "Exempt per §288 Abs. 2 for medium GmbH"
  │     │         │
  │     │         └─► NO → Continue to Step 3
  │     │
  │     └─► NO → Continue to Step 3
  │
  ▼
STEP 3: Search PDF
```

### §288 Abs. 2 Exemptions (Medium GmbH)

These items are automatically exempt for medium GmbH:

| §285 Ref | Disclosure |
|----------|-------------|
| Nr. 4 | Revenue breakdown |
| Nr. 8 | Material cost breakdown |
| Nr. 9 | Personnel cost breakdown |
| Nr. 17 | Related party (controlling) |
| Nr. 21 | IFRS transition |
| Nr. 29 | Auditor fees |
| Nr. 32 | Related party disclosures |

---

## Step 3: PDF Search & Verification

For each non-exempt item:

### Search Strategy:
1. Extract German term from `disclosure_item` parentheses
2. Also search variant terms (e.g., "Beteiligungen" vs "Anteile an verbundenen Unternehmen")
3. Look for amounts (EUR, TEUR) near the term

### Response Mapping:

| Condition | Response | Reason Code |
|-----------|----------|-------------|
| Found specific evidence | Yes | null |
| Not found, mandatory | No | MISSING_EVIDENCE |
| §288 exempt | N/A | EXEMPTION_CLAIMED |
| Not applicable to this entity | N/A | ENTITY_SPECIFIC |
| Cannot determine from PDF | Review | PDF_EXTRACTION_LIMIT |

---

## Step 4: Manual Verification (For "No" Responses)

Before finalizing any "No" response:

```bash
# Verify the item truly doesn't exist
grep -i "[related search term]" extracted-fs.txt
```

### Common False Negatives:

| Checklist Asks | PDF May Say |
|---------------|-------------|
| Anteile an verbundenen Unternehmen | Beteiligungen |
| Personalaufwand | Löhne und Gehälter |
| Vorräte | Rohstoffe, fertige Erzeugnisse |
| Forderungen | Lieferungen und Leistungen |

If found via grep → Change response to "Yes"

---

## Step 5: Entity-Specific N/A Check

For items not found, check if applicable:

| Scenario | Reason Code |
|----------|-------------|
| No subsidiaries | ENTITY_SPECIFIC |
| No parent company | ENTITY_SPECIFIC |
| No group | ENTITY_SPECIFIC |
| Protected remuneration (§286 Abs. 4) | ENTITY_SPECIFIC |
| No share-based payment | ENTITY_SPECIFIC |

---

## Evidence Quality Standards

### Required Fields:
```json
{
  "id": "HGB-XXX-00000",
  "response": "Yes" | "No" | "N/A",
  "reason_code": null | "MISSING_EVIDENCE" | "EXEMPTION_CLAIMED" | "ENTITY_SPECIFIC" | "PDF_EXTRACTION_LIMIT",
  "confidence": "High" | "Medium" | "Low",
  "evidence": "Page X: [German term] [amount]",
  "verified_by": "verification-agent",
  "verification_date": "YYYY-MM-DD"
}
```

### Evidence Rules:
- **Yes** MUST include: Page number OR amount OR German term
- **No** MUST include: What was searched for
- **N/A** MUST include: Exemption reason or why not applicable

**REJECT** generic evidence:
- ❌ "Item disclosed"
- ❌ "Not found in FS"
- ❌ "Mandatory item"

---

## Output

Save results to `results.json` in the same directory as checklist.

---

## Validation Checklist

Before completing, verify:
- [ ] All checklist items have a response
- [ ] No "Review" responses remain
- [ ] All "No" responses manually verified with grep
- [ ] §288 exempt items have EXEMPTION_CLAIMED
- [ ] Entity-specific items have ENTITY_SPECIFIC
- [ ] Evidence meets quality standards

---

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Timeout on PDF parsing | Pre-extract to text file first |
| False "No" for exempt items | Apply §288 check before PDF search |
| "No evidence" but item exists | Grep for variant German terms |
| Generic evidence only | Require page#/amount in prompt |

---

*Skill Version: 2.0*
*Last Updated: 2026-04-16*
