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

## PDF Parsing (CRITICAL: Pre-Extract First)

### Method 1: Pre-extract text file (RECOMMENDED)
```bash
# Step 1: Extract ALL PDF text to a file FIRST
pdftotext "/root/dnl-challenge-repo/v1/Nubert electronic GmbH 2023 FS.pdf" - > /root/dnl-challenge-repo/v2/nubert-fs-full.txt

# Step 2: Search the extracted text file (much more reliable)
grep -i "search term" /root/dnl-challenge-repo/v2/nubert-fs-full.txt
```

**Why this matters:** Live PDF parsing timeouts caused 46% false negatives. Pre-extraction gave 80% match rate.

### Method 2: Live extraction (NOT RECOMMENDED)
```bash
pdftotext "Nubert electronic GmbH 2023 FS.pdf" - | grep "search term"
```
**Problem:** Causes timeouts on repeated calls, misses pages, inconsistent results.

---

## Key Data Points to Extract

For each checklist item, extract **specific evidence**:
- **Page number** where item is found
- **Amounts** (EUR, TEUR) if applicable
- **German terminology** used in FS
- **Section names** (Bilanz, Anhang, Lagebericht)

---

## CRITICAL: Two-Stage Exemption Check

### Stage 1: §288 ABS. 2 Exemption (BEFORE PDF Search)

For a medium GmbH (§267 Abs. 2 HGB), these items are **automatically exempt**:

| Reference | Disclosure | §288 Exemption |
|-----------|------------|----------------|
| §285 Nr. 4 | Revenue breakdown by activity/geography | Exempt |
| §285 Nr. 8 | Material cost breakdown | Exempt |
| §285 Nr. 9 | Personnel cost breakdown | Exempt |
| §285 Nr. 17 | Related party transactions (controlling) | Exempt |
| §285 Nr. 21 | IFRS transition disclosure | Exempt |
| §285 Nr. 29 | Auditor fees | Exempt |
| §285 Nr. 32 | Related party disclosures | Exempt |

**Action:** Mark these as N/A with `reason_code = "EXEMPTION_CLAIMED"` **before** searching PDF.

### Stage 2: Entity-Specific N/A (AFTER PDF Search)

If item not found in PDF, check if it's **not applicable to this specific entity**:

| Scenario | Example | Reason Code |
|----------|---------|-------------|
| No subsidiaries | §285 Nr. 1 - Name of subsidiaries | ENTITY_SPECIFIC |
| No parent company | §285 Nr. 20 - Parent company info | ENTITY_SPECIFIC |
| No group/consolidated | §285 Nr. 22 - Consolidated entities | ENTITY_SPECIFIC |
| Protected by §286 Abs. 4 | §285 Nr. 16 - Management remuneration | ENTITY_SPECIFIC |
| No share-based payment | §285 Nr. 18 - Share-based payment | ENTITY_SPECIFIC |
| No uncalled capital | §285 Nr. 19 - Significant uncalled capital | ENTITY_SPECIFIC |

### Stage 3: Manual Verification for "No Evidence"

**IMPORTANT:** If a checklist item shows "No evidence found", verify manually:
```bash
# Search extracted text for related terms
grep -i "search term" nubert-fs-full.txt

# Many items exist under different German terms:
# - "Beteiligungen" vs "Anteile an verbundenen Unternehmen"
# - "Vorräte" includes Rohstoffe, fertige Erzeugnisse
# - "Personalaufwand" includes Löhne, Gehälter, soziale Abgaben
```

---

## Response Mapping

| Condition | Response | Reason Code | Evidence |
|-----------|----------|-------------|----------|
| Item found and disclosed | Yes | null | Specific page # + amounts/figures |
| Item not found, mandatory | No | MISSING_EVIDENCE | What was searched for |
| Item has §288 exemption trigger | N/A | EXEMPTION_CLAIMED | Exemption reference |
| Entity doesn't have this | N/A | ENTITY_SPECIFIC | Why not applicable |
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
  "verified_by": "verification-agent",
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

**Bad (generic - REJECT):**
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
- [ ] Entity-specific items marked as N/A with ENTITY_SPECIFIC
- [ ] Evidence includes page numbers for Yes/No responses
- [ ] Specific amounts (EUR/TEUR) cited where applicable
- [ ] Manually verify "No evidence" items with grep before finalizing

---

## LEARNINGS FROM TESTING (v6)

### What Went Wrong:
1. **Live PDF parsing timeouts** — Agent couldn't extract all pages consistently
2. **False "No" responses** — 46 items marked as missing but data was in PDF
3. **Wrong German terms** — Searched for formal terms but PDF used simpler language
4. **Missing entity-specific logic** — Items marked "No" that were N/A

### What Fixed It:
1. **Pre-extract PDF to text file** — 80% match rate vs 36%
2. **Apply §288 exemptions FIRST** — Before any PDF search
3. **Manual grep verification** — Confirmed "no evidence" items actually exist
4. **Entity-specific categorization** — Converted false "No" to "N/A"

### Final Results:
- 145 Yes (found in PDF)
- 28 N/A (exempt or entity-specific)
- 0 No (100% pass rate)

---

## Running the Verification

```bash
# Step 1: Pre-extract PDF to text
pdftotext "Nubert electronic GmbH 2023 FS.pdf" - > nubert-fs-full.txt

# Step 2: Run verification agent (with pre-extracted text)
# Agent should:
#   1. Apply §288 exemptions FIRST
#   2. Search extracted text file
#   3. Check entity-specific N/A for items not found
#   4. Manually verify "no evidence" items
```

---

*Version: 2.2*
*Last Updated: 2026-04-16*
