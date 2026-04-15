# Verification Agent Scope — v2

## Purpose
This document defines the verification workflow for Step 4 of the v2 HGB disclosure checklist. It guides the verification agent in checking financial statements against the generated checklist.

---

## Entity Context

| Parameter | Value |
|-----------|-------|
| Entity | Nubert electronic GmbH |
| FY | 31 December 2023 |
| Entity Type | GmbH — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB) |
| Size | Medium (mittelgroß) |
| P&L Format | Gesamtkostenverfahren (§ 275 Abs. 1 HGB) |

---

## Input Files

| File | Path | Description |
|------|------|-------------|
| Checklist | `/root/dnl-challenge-repo/v2/checklist.json` | 173 items (BIL, GuV, Anhang, LAG) |
| Financial Statements | `/root/dnl-challenge-repo/v1/Nubert electronic GmbH 2023 FS.pdf` | Source PDF |

---

## PDF Parsing

### Tool
Use `pdftotext` (poppler-utils) to extract text:

```bash
pdftotext "Nubert electronic GmbH 2023 FS.pdf" - | less
```

### Key Data Points to Extract
For each checklist item, extract **specific evidence**:
- **Page number** where item is found
- **Amounts** (EUR, TEUR) if applicable
- **German terminology** used in FS
- **Section names** (Bilanz, Anhang, Lagebericht)

### Example Extraction
```
Input: Is Umsatzerlöse (revenue) disclosed?
Extracted: "Das Unternehmen hat im Geschäftsjahr 2023 Umsatzerlöse im Rahmen von TEUR 20.489 realisiert"
Page: 1 (Lagebericht)
Confidence: High
```

---

## CRITICAL: §288 ABS. 2 Exemption Check

**BEFORE** searching the PDF for any evidence, check this:

### Step 1: Identify Exempt Items
```python
if item['obligation'] == 'C' and '§288' in item.get('trigger_condition', ''):
    # This item is exempt for medium GmbH
```

### Step 2: Apply Exemption Logic
For a medium GmbH (§267 Abs. 2 HGB), these items are exempt:

| Reference | Disclosure | §288 Exemption |
|-----------|------------|----------------|
| §285 Nr. 4 | Revenue breakdown by activity/geography | Exempt |
| §285 Nr. 8 | Material cost breakdown | Exempt |
| §285 Nr. 9 | Personnel cost breakdown | Exempt |
| §285 Nr. 17 | Related party transactions (controlling) | Exempt |
| §285 Nr. 21 | IFRS transition disclosure | Exempt |
| §285 Nr. 29 | Auditor fees | Exempt |
| §285 Nr. 32 | Related party disclosures | Exempt |

### Step 3: Set Response for Exempt Items
```python
if is_exempt and entity_is_medium_gmbh:
    response = "N/A"
    reason_code = "EXEMPTION_CLAIMED"
    evidence = "Exempt for medium GmbH per §288 Abs. 2 HGB"
    skip PDF search
else:
    proceed with normal verification
```

---

## Response Mapping

| Condition | Response | Reason Code | Evidence |
|-----------|----------|-------------|----------|
| Item found and disclosed | Yes | null | Specific page # + amounts/figures |
| Item not found, mandatory | No | MISSING_EVIDENCE | What was searched for |
| Item has §288 exemption trigger | N/A | EXEMPTION_CLAIMED | Exemption reference |
| Conditional item, trigger not met | N/A | ENTITY_SPECIFIC | Why not applicable |
| Cannot determine from PDF | Review | PDF_EXTRACTION_LIMIT | What's missing |

---

## Evidence Quality Standards

### Required Fields per Result
```json
{
  "id": "HGB-BIL-10001",
  "response": "Yes",
  "reason_code": null,
  "confidence": "High",
  "evidence": "Page X: Found [specific German term] EUR [amount]",
  "audit_notes": "Any additional context",
  "verified_by": "verification-agent-v2",
  "verification_date": "2026-04-15"
}
```

### Evidence Examples

**Good (specific):**
```json
{
  "id": "HGB-BIL-10001",
  "response": "Yes",
  "evidence": "Page 3, Bilanz: Anlagevermögen EUR 2,675,839.98 includes immaterielle Vermögensgegenstände EUR 0",
  "confidence": "High"
}
```

**Bad (generic):**
```json
{
  "id": "HGB-BIL-10001",
  "response": "Yes", 
  "evidence": "Item disclosed in financial statements",
  "confidence": "Low"
}
```

---

## Confidence Levels

| Level | Definition |
|-------|------------|
| **High** | Specific page #, amounts, German terminology cited |
| **Medium** | Item found but no specific details |
| **Low** | Inferred or uncertain |

---

## Output

| File | Path |
|------|------|
| Results JSON | `/root/dnl-challenge-repo/v2/results.json` |
| Results Excel | `/root/dnl-challenge-repo/v2/output/results.xlsx` |

---

## Validation Checklist

Before completing, verify:
- [ ] All 173 items have a response
- [ ] No "Review" responses (should be resolved to Yes/No/N/A)
- [ ] §288 exempt items marked as N/A with EXEMPTION_CLAIMED
- [ ] Evidence includes page numbers for Yes/No responses
- [ ] Specific amounts (EUR/TEUR) cited where applicable

---

## Running the Verification

```bash
# 1. Parse PDF to text (if needed)
pdftotext "Nubert electronic GmbH 2023 FS.pdf" - > /tmp/nubert-fs.txt

# 2. Run verification agent
# (uses subagent spawned with this scope)
```

---

*Version: 2.1*
*Last Updated: 2026-04-15*
