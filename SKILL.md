---
name: hgb-disclosure-checklist
description: Agent-based workflow for generating machine-readable audit disclosure checklists
version: 1.0.0
author: DNL Professional Practice Team
framework: German GAAP (HGB)
applicable_date: 2023-12-31
---

# HGB Disclosure Checklist Skill

This skill defines a structured, reproducible, agent-based workflow for generating machine-readable disclosure checklists for auditors. While primarily implemented for German GAAP (HGB) for a medium-sized GmbH, the methodology is framework-agnostic.

## 1. Skill Overview
The `hgb-disclosure-checklist` skill uses a multi-agent orchestration pattern to draft, validate, and verify financial statement disclosures against statutory requirements.

- **Objective:** Generate a structured, machine-readable disclosure checklist (JSON)
- **Primary Deliverable:** Excel workbook (.xlsx) with status (Yes/No/N/A/Review), evidence, and notes
- **Strategy:** Decomposition into reporting components (Bilanz, GuV, Anhang, Lagebericht)

## 2. Prerequisites
- **Language:** Python 3.x
- **Libraries:** `openpyxl`
- **AI Access:** LLM API (Claude Sonnet 3.5 recommended for accuracy with statutory references)
- **Input Data:** Target entity's financial statements (text or PDF)
- **Knowledge Base:** Statute list for chosen framework (e.g., HGB §§ 264 ff.)

## 3. Inputs
- `scope.md` — Defines entity type, size class, reporting components, and framework boundaries.
- `schema.json` — Enforces the checklist data structure (ID, section, question, citation, obligation, trigger condition).
- Target Financial Statements — Extracted text file of the target entity's FS.
- Statute List — Precise mapping of disclosure items to statutory paragraphs.

## 4. Agent Workflow
1. **Scoping Agent:** Validates and finalises `scope.md` against framework statute lists.
2. **Section Drafter Agents (Parallel):** Four agents, each responsible for one section (Bilanz, GuV, Anhang, Lagebericht), write JSON items following `schema.json`.
3. **Merge & Validate:** Aggregation script combines JSON outputs, enforces schema, and flags [REVIEW] items.
4. **Verification Agent:** Cross-checks `checklist.json` items against FS text; outputs `results.json` (Yes/No/N/A/Review, evidence, notes).
5. **Excel Formatter:** Executes `generate_excel.py` and `generate_results_excel.py` for audit-ready deliverables.
6. **Human Review:** Auditor signs off [REVIEW] flags and verifies genuine "No" audit findings.

## 5. Quality Gates
| Gate | Criteria |
|---|---|
| **Schema Validation** | All 7 fields populated; obligation is M/C; trigger_condition present for all C items. |
| **Citation Validity** | Every item has a valid HGB reference; no [REVIEW] flags unresolved. |
| **Verification Coverage** | All mandatory items must have a Yes/No response; no blanks in results.json. |
| **Human Sign-off** | Subject matter expert (SME) must review all "No" findings and [REVIEW] flags before live deployment. |

## 6. Key Prompts

### Section Drafter Prompt Pattern
> "You are an HGB disclosure agent. Write the [SECTION] section for a medium-sized GmbH. Use the schema in schema.json. Phrasing must be closed (Yes/No/N/A). Include only items with valid § citations. Flag uncertain ones with [REVIEW]."

### Verification Agent Prompt Pattern
> "Verify these checklist items against the provided FS text. For each: Yes (cited evidence), No (missing), N/A (trigger not met), or Review (uncertain). Be specific — quote the FS section as evidence."

## 7. Extending to Other Frameworks
To adapt for IFRS or UK GAAP:
1. **Update Statutes:** Replace HGB references in scope.md with target framework equivalents (e.g., IAS 1).
2. **Re-prompt:** Run Section Drafter agents with the new statute list.
3. **Refactor Schema:** Rename `hgb_reference` to `standard_reference` in schema.json.
4. **Size Logic:** Adjust size class thresholds (note: IFRS/UK GAAP often use different materiality concepts rather than hard size classes).

## 8. Cost Estimate
*(Based on Claude 3.5 Sonnet pricing: $3 input / $15 output per 1M tokens)*
- Scoping Agent: ~2k tokens
- 4x Section Drafters: ~8k tokens each
- Verification Agent: ~15k tokens (includes full FS text)
- **Total:** < $0.50 per checklist run for a medium entity.

## 9. Repository Structure
```
repo/
├── checklist.json      # Living checklist (source of truth)
├── results.json        # Verification results
├── schema.json         # Validation schema
├── scope.md            # Scope manifest
├── generate_excel.py   # Excel generator
└── ...
```

## 10. Limitations & Human Oversight
- **Citations:** AI-generated citations require verification; always perform a spot-check.
- **Scope:** Disclosure-only scope; does not replace substantive testing.
- **PDF Extraction:** Text-based extraction from PDF can fail on complex tables (e.g., Anlagenspiegel).
- **Human Expert:** This tool *aids* the auditor, it does not *replace* the auditor. Final sign-off must always come from a qualified SME.
