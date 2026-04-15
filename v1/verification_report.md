# HGB Disclosure Checklist — Verification Report

**Date:** 2026-03-28  
**Checklist file:** `/root/.openclaw/workspace/dnl-checklist/checklist.json`  
**Entity:** GmbH — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)  
**Reporting date:** 31 December 2023  
**Total items verified:** 87 (BIL: 20, GUV: 19, ANH: 32, LAG: 16)

---

## Check 1: Valid HGB Paragraph References

**Result: FAIL**

Four items have incorrect or unclear citations:

| Item | Cited Reference | Issue | Correct Reference |
|------|----------------|-------|-------------------|
| **BIL-019** | §266 Abs. 3 A.III.2 HGB | A.III.2 is "Andere Gewinnrücklagen", not Beteiligungen | §266 Abs. 3 **A.IV.2** HGB |
| **ANH-030** | §285 Nr. 6 HGB | Nr. 6 covers depreciation/amortisation methods, not Kapitalertragsteuer treatment | Likely §285 Nr. 16 HGB or §285 Nr. 4 HGB (requires contextual determination) |
| **ANH-025** | §286 Abs. 2/3 HGB | Slash notation is ambiguous — should cite each Absatz separately | §286 Abs. 2 HGB and/or §286 Abs. 3 HGB |
| **BIL-002** | §266 Abs. 2 HGB | Completeness prompt says "all **four** mandatory Aktiva categories" but the item text lists **five** (including "Aktive latente Steuern" as a category). Aktive latente Steuern is NOT a mandatory Aktiva category under §266 Abs. 2 — it is an optional line item within Umlaufvermögen | §266 Abs. 2 HGB lists four categories: A. Anlagevermögen, B. Umlaufvermögen, C. Rechnungsabgrenzungsposten, D. Aktiver Unterschiedsbetrag aus der Vermögensrechnung |

All other 83 items have valid, correct HGB paragraph references.

---

## Check 2: HGB as of 31 December 2023 (No Post-2024 Changes)

**Result: PASS**

All items reference HGB provisions applicable to financial years ending 31 December 2023. No items incorporate post-2024 legislative changes (e.g., no references to the 2024 CSR-Richtlinie-Umsetzungsgesetz changes to §289b ff.). The CSR reporting exclusion in LAG-015 correctly cites §289 Abs. 3 HGB as not applicable for medium-sized GmbH, consistent with the 2023 legal position.

---

## Check 3: Disclosure Items Phrased as Closed Yes/No/N/A Questions

**Result: PASS**

All 87 items use closed question phrasing beginning with "Has the entity...", "Does the...", or "Does the P&L..." — all answerable with Yes, No, or N/A. No open-ended or narrative prompts.

---

## Check 4: All Conditional (C) Items Have trigger_condition

**Result: PASS**

All 38 items with obligation "C" have a non-null, specific `trigger_condition`. All 49 items with obligation "M" have `trigger_condition: null`. No conditional items are missing triggers.

---

## Check 5: Completeness Prompts Specific and Evidence-Based

**Result: PASS**

All 87 completeness prompts reference specific documents (Anhang, Lagebericht, balance sheet), named line items, sub-categories, or legal provisions. No vague prompts detected (e.g., none say "check if it looks right" or "verify compliance").

---

## Check 6: Items Correctly Grouped by Section

**Result: PASS**

- **Bilanz** (20 items): All under balance sheet sub-sections (Form und Gliederung, Anlagevermögen, Umlaufvermögen, Eigenkapital, Rückstellungen, Verbindlichkeiten, Latente Steuern, Geschäftswert, Haftungsverhältnisse, Forderungen, Finanzanlagen, Gesellschafterforderungen)
- **GuV** (19 items): All under P&L sub-sections (Darstellungsform, Pflichtpositionen, Anhangangaben zur GuV)
- **Anhang** (32 items): All under note sub-sections (Bilanzierungs- und Bewertungsmethoden, Allgemeine Angaben, Organ- und Gesellschafterangaben, etc.)
- **Lagebericht** (16 items): All under management report sub-sections (Allgemeine Anforderungen, Risikomanagement, etc.)

No items are misclassified across the four main sections.

---

## Check 7: No Duplicate Disclosure Items Across Sections

**Result: PASS**

Cross-referencing items with the same or overlapping HGB references:

| Same Reference | Items | Assessment |
|---------------|-------|------------|
| §285 Nr. 7 HGB (employees) | GUV-015, ANH-004 | **Not a duplicate** — GUV-015 is the Anhang disclosure requirement listed under GuV section for cross-referencing; ANH-004 is the same item under Anhang section. However, having the same requirement appear in two sections is a **design concern** (see [REVIEW] below). |
| §285 Nr. 13 HGB (goodwill) | BIL-016, ANH-014 | **Not a duplicate** — BIL-016 covers the existence of goodwill on the balance sheet; ANH-014 covers the detailed amortisation period disclosure in the notes. Complementary. |
| §268 Abs. 7 HGB (Haftungsverhältnisse) | BIL-017, ANH-018 | **Not a duplicate** — Same distinction: balance sheet presentation vs. detailed note disclosure. |
| §285 Nr. 1a/1b/2 HGB (liabilities) | BIL-012/013/014, ANH-029/031 | **Not a duplicate** — Same pattern: balance sheet line items vs. detailed note disclosures. |

**[REVIEW] — Design concern:** GUV-015 and ANH-004 both reference §285 Nr. 7 HGB (average employees) with virtually identical content. While both carry obligation "M", having the same requirement as two separate checklist items creates redundancy. Consider consolidating or clearly marking one as a cross-reference.

---

## Check 8: §286 Abs. 4 Protective Clause for GmbH MD Remuneration

**Result: PASS**

Two items address this:

- **ANH-005** (obligation: C, trigger: "Always applicable for GmbH") — Covers the either/or nature: disclose per §285 Nr. 9a **or** invoke §286 Abs. 4
- **ANH-024** (obligation: C, trigger: "Only if the entity chooses not to disclose managing director remuneration") — Specifically covers the invocation of the protective clause

Both are correctly flagged as conditional. The trigger conditions are appropriate and complementary.

---

## Check 9: Art. 67 EGHGB BilMoG Transitional Item

**Result: PASS**

**ANH-026** covers this:
- Reference: "Art. 67 EGHGB"
- Obligation: C
- Trigger: "Only if the entity still applies BilMoG transition rules for goodwill or pension provisions"
- Prompt: Mentions Art. 67 Abs. 3 EGHGB specifically for goodwill

---

## Check 10: §42 GmbHG GmbH-Specific Item

**Result: PASS**

Two items reference §42 GmbHG:

- **ANH-023** — Disclosure of Stammeinlage and additional Einlagen per §42 GmbHG (obligation: M)
- **ANH-032** — Forderungen gegen Gesellschafter per §42 Abs. 3 GmbHG i.V.m. §268 Abs. 5 HGB (obligation: C)

---

## Check 11: §288 Abs. 1 Size Exemption NOT Applicable

**Result: PASS**

**ANH-027** correctly addresses this:
- Item text: "Has the entity confirmed that it has NOT applied the small-entity size exemptions under § 288 Abs. 1 HGB?"
- Obligation: M (mandatory — the entity must confirm non-application)
- Prompt: "Verify that the Anhang does not claim small-entity size exemptions under § 288 Abs. 1 HGB, confirming full compliance with all medium-GmbH disclosure requirements."

---

## Gap Analysis: Missing Items

**Result: MINOR GAPS IDENTIFIED**

| Missing Requirement | Reference | Severity | Notes |
|---------------------|-----------|----------|-------|
| Abschlussprüferhonorar — disclosure that auditor's fees include VAT (Umsatzsteuer) or are stated net | §285 Nr. 17 HGB (last sentence) | Low | ANH-019 covers the fee breakdown but does not explicitly mention the VAT/net distinction requirement |
| Disclosure that individual financial statements were NOT prepared voluntarily under IFRS | §285 Nr. 32 HGB | Low | Not relevant if entity doesn't have an IFRS option, but could serve as a positive confirmation item |
| Währungsumrechnungsmethoden für GuV (currency translation methods for P&L specifically) | §285 Nr. 5 HGB | Low | ANH-002 covers §284 Abs. 2 Nr. 2 (Bilanz currency translation); §285 Nr. 5 is specifically for GuV translation methods — could be split out |
| Im Konzern einbezogene Unternehmen — naming of group entities | §285 Nr. 11 HGB (last clause) | Very Low | Only relevant if entity is a group parent; out of scope per metadata |

**Overall assessment:** No critical gaps. The checklist covers all major mandatory and most conditional HGB disclosure requirements for a medium-sized GmbH.

---

## Obligation Flags (M/C) Check

**Result: PASS (with one observation)**

All M-flagged items are genuinely mandatory under HGB. All C-flagged items are genuinely conditional (dependent on the existence of the relevant transaction, instrument, or policy choice).

**Observation:** ANH-019 (auditor's fees per §285 Nr. 17 HGB) is flagged M but should arguably be C — if no statutory auditor was appointed (which is possible for some GmbHs), the disclosure is not required. However, for a *mittelgroße Kapitalgesellschaft*, a statutory audit IS required (§316 HGB), so M is technically correct in this context.

---

## Summary of [REVIEW] Flags

| # | Item | Issue |
|---|------|-------|
| 1 | BIL-019 | Wrong sub-reference: A.III.2 should be A.IV.2 |
| 2 | ANH-030 | Wrong reference: §285 Nr. 6 HGB is for depreciation methods, not Kapitalertragsteuer |
| 3 | ANH-025 | Ambiguous slash: "§286 Abs. 2/3 HGB" should specify each Absatz |
| 4 | BIL-002 | Inconsistency: text says "five mandatory Aktiva categories" but §266 Abs. 2 only defines four (Aktive latente Steuern is not a mandatory category) |
| 5 | GUV-015 + ANH-004 | Duplicate requirement: both cover §285 Nr. 7 HGB (employees) — consider consolidating |

---

## Overall Assessment

| Check | Result |
|-------|--------|
| 1. Valid HGB paragraph references | **FAIL** — 4 items need correction |
| 2. HGB as of 31 Dec 2023 | **PASS** |
| 3. Closed Yes/No/N/A questions | **PASS** |
| 4. Conditional items have trigger_condition | **PASS** |
| 5. Completeness prompts specific | **PASS** |
| 6. Correct section grouping | **PASS** |
| 7. No duplicates | **PASS** (with one design concern) |
| 8. §286 Abs. 4 protective clause | **PASS** |
| 9. Art. 67 EGHGB BilMoG | **PASS** |
| 10. §42 GmbHG item | **PASS** |
| 11. §288 Abs. 1 exemption noted | **PASS** |
| Gap analysis | **PASS** — no critical gaps |
| Obligation flags | **PASS** |

**Overall: CONDITIONAL PASS — 10 of 11 checks pass. Check 1 (valid citations) fails due to 4 items needing correction. The checklist is well-structured, comprehensive, and largely accurate. Fixing the 4 flagged citation issues would bring it to full compliance.**
