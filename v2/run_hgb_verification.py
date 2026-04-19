#!/usr/bin/env python3
"""Run a fresh HGB filing verification pass against the current checklist."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = ROOT.parent.parent
CHECKLIST_PATH = ROOT / "checklist.json"
RESULTS_PATH = ROOT / "results.json"
OUTPUT_DIR = ROOT / "output"
EXTRACTED_TEXT_PATH = OUTPUT_DIR / "nubert_2023_fs_extracted.txt"
PDF_PATH = WORKSPACE_ROOT / "Nubert electronic GmbH 2023 FS.pdf"

VERIFIED_BY = "hgb-filing-verification-v1"
VERIFICATION_DATE = date.today().isoformat()

MEDIUM_PUBLICATION_REQUIRED_BILANZ_REFERENCES = {
    "§266 Abs. 2 A I 1 HGB",
    "§266 Abs. 2 A I 3 HGB",
    "§266 Abs. 2 A II 1 HGB",
    "§266 Abs. 2 A II 2 HGB",
    "§266 Abs. 2 A II 3 HGB",
    "§266 Abs. 2 A II 4 HGB",
    "§266 Abs. 2 A III 1 HGB",
    "§266 Abs. 2 A III 2 HGB",
    "§266 Abs. 2 A III 3 HGB",
    "§266 Abs. 2 A III 4 HGB",
    "§266 Abs. 2 B II 2 HGB",
    "§266 Abs. 2 B II 3 HGB",
    "§266 Abs. 2 B III 1 HGB",
    "§266 Abs. 3 C 1 HGB",
    "§266 Abs. 3 C 2 HGB",
    "§266 Abs. 3 C 6 HGB",
    "§266 Abs. 3 C 7 HGB",
}

GUV_AGGREGATION_RELIEF_REFERENCES = {
    "§275 Abs. 2 Nr. 1 HGB",
    "§275 Abs. 2 Nr. 2 HGB",
    "§275 Abs. 2 Nr. 3 HGB",
    "§275 Abs. 2 Nr. 4 HGB",
    "§275 Abs. 2 Nr. 5 HGB",
}

SECTION_PAGE_MAP = {
    "Bilanz": [2, 3],
    "GuV": [4],
    "Anhang": [5, 6, 7],
    "Lagebericht": [0, 1, 2],
}

STOPWORDS = {
    "der",
    "die",
    "das",
    "und",
    "oder",
    "sowie",
    "mit",
    "von",
    "für",
    "im",
    "in",
    "den",
    "des",
    "dem",
    "ein",
    "eine",
    "einer",
    "eines",
    "einem",
    "als",
    "auf",
    "an",
    "aus",
    "unter",
    "über",
    "bei",
    "bis",
    "zu",
    "zum",
    "zur",
    "davon",
    "mehr",
    "einem",
    "einer",
    "eines",
    "sind",
    "ist",
    "wird",
    "wurden",
    "soweit",
    "sofern",
}

GENERIC_STEMS = {
    "sonstig",
    "ander",
    "gesamt",
    "betrag",
    "post",
    "ausweis",
    "gesellschaft",
    "unternehm",
    "gegenub",
}

MANUAL_KEYWORDS = {
    "HGB-BIL-10001": [
        "Bilanz",
        "Aktiva",
        "Passiva",
    ],
    "HGB-BIL-10036": ["Gewinnvortrag"],
    "HGB-BIL-10037": ["Jahresüberschuss"],
    "HGB-GUV-20001": [
        "Gewinn- und Verlustrechnung",
        "1.1.2023 - 31.12.2023",
    ],
    "HGB-GUV-20013": ["Erträge aus Beteiligungen"],
    "HGB-GUV-20015": ["sonstige Zinsen und ähnliche Erträge"],
    "HGB-GUV-20017": ["Zinsen und ähnliche Aufwendungen"],
    "HGB-GUV-20021": ["Jahresüberschuss"],
    "HGB-ANH-30001": [
        "Anhang zum Jahresabschluss 2023",
        "I. Allgemeine Angaben",
        "II. Bilanzierungs- und Bewertungsmethoden",
        "IV. Angaben zur Gewinn- und Verlustrechnung",
        "V. Sonstige Angaben",
        "VI. Ergebnisverwendungsvorschlag",
    ],
    "HGB-ANH-30003": ["Bilanzierungs- und Bewertungsmethoden"],
    "HGB-ANH-30006": ["Fremdkapitalzinsen werden nicht in die Herstellungskosten einbezogen"],
    "HGB-ANH-30010": ["Restlaufzeit mehr als 5 Jahre", "gesichert"],
    "HGB-ANH-30011": ["Art der Verbindlichkeit", "Verbindlichkeiten Gesamt"],
    "HGB-ANH-30013": ["Sonstige finanzielle Verpflichtungen"],
    "HGB-ANH-30017": ["Anzahl der Arbeitnehmer"],
    "HGB-ANH-30020": ["Geschäftsführer im Berichtszeitraum"],
    "HGB-ANH-30024": ["sonstigen Rückstellungen beinhalten im Wesentlichen"],
    "HGB-ANH-30049": ["Die Geschäftsführung schlägt vor"],
    "HGB-ANH-30052": ["vom Schutzrecht gemäß § 286 Abs. 4 HGB Gebrauch gemacht"],
    "HGB-LAG-40001": ["Geschäftsverlauf und Lage", "Ertragslage", "Finanzlage", "Vermögenslage"],
    "HGB-LAG-40002": ["Gesamtwirtschaftliche und branchenbezogene Rahmenbedingungen", "Gesamtaussage"],
    "HGB-LAG-40003": ["EBIT beträgt", "Liquidität zum Bilanzstichtag"],
    "HGB-LAG-40004": ["Für das Jahr 2024 geht die Geschäftsleitung", "Chancen und Risiken der künftigen Entwicklung"],
    "HGB-LAG-40006": ["Risikomanagement", "Währungsrisiko"],
    "HGB-LAG-40007": ["Währungsrisiko", "Markt- und Kundenrisiken", "Liquidität zum Bilanzstichtag"],
}

MANUAL_RESPONSES = {
    "HGB-ANH-30014": (
        "N/A",
        "EXEMPTION_CLAIMED",
        "High",
        "Checklist trigger condition states that §285 Nr. 4 HGB is exempt for medium-sized capital companies under §288 Abs. 2 Satz 1 HGB.",
    ),
    "HGB-ANH-30018": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The filing states that the profit and loss account is presented under §275 Abs. 1 HGB using the Gesamtkostenverfahren, so the cost-of-sales disclosure in §285 Nr. 8 HGB does not apply.",
    ),
    "HGB-ANH-30019": (
        "N/A",
        "EXEMPTION_CLAIMED",
        "High",
        "Page 8 states that the company makes use of the protection right under §286 Abs. 4 HGB for managing-director remuneration disclosures.",
    ),
    "HGB-ANH-30022": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No indication was found that the company is a general partner with unlimited liability in another undertaking; the filing does not describe such a structure.",
    ),
    "HGB-ANH-30023": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The company is a private GmbH, not a listed company, so the listed-company voting-right disclosure in §285 Nr. 11b HGB does not apply.",
    ),
    "HGB-ANH-30025": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No goodwill line item was identified in the balance sheet, so a goodwill amortization-period disclosure is not evidenced as relevant for this filing.",
    ),
    "HGB-ANH-30026": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found that the company has a parent preparing consolidated financial statements for a largest group.",
    ),
    "HGB-ANH-30027": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found that the company has a parent preparing consolidated financial statements for a smallest group.",
    ),
    "HGB-ANH-30028": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The company is a GmbH, not a partnership within §264a Abs. 1 HGB.",
    ),
    "HGB-ANH-30029": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of Genussrechte, options, convertible instruments, or similar rights.",
    ),
    "HGB-ANH-30030": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The filing concerns a GmbH, so the §161 AktG declaration disclosure does not apply.",
    ),
    "HGB-ANH-30031": (
        "N/A",
        "EXEMPTION_CLAIMED",
        "High",
        "Checklist trigger condition states that medium-sized capital companies need not disclose auditor fees in the notes under §288 Abs. 2 Satz 2 HGB.",
    ),
    "HGB-ANH-30032": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of financial fixed assets carried above fair value without impairment recognition.",
    ),
    "HGB-ANH-30033": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of derivative financial instruments requiring a dedicated note disclosure.",
    ),
    "HGB-ANH-30034": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of financial instruments measured at fair value requiring the §285 Nr. 20 HGB disclosure set.",
    ),
    "HGB-ANH-30035": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No off-market related-party transaction disclosure was found and the row is fact-conditioned in practice.",
    ),
    "HGB-ANH-30036": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No capitalization of internally generated intangible fixed assets was identified in the filing.",
    ),
    "HGB-ANH-30037": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No valuation-unit disclosure or hedge-accounting narrative was found in the filing.",
    ),
    "HGB-ANH-30038": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "The filing gives pension provision amounts but no sign that a detailed actuarial-assumption disclosure set was triggered here; this row remains fact-conditioned in practice.",
    ),
    "HGB-ANH-30039": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No offsetting under §246 Abs. 2 Satz 2 HGB was identified in the filing.",
    ),
    "HGB-ANH-30040": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of investment-fund holdings requiring the §285 Nr. 26 HGB disclosure.",
    ),
    "HGB-ANH-30041": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No contingent-liability disclosure under §268 Abs. 7 HGB was identified.",
    ),
    "HGB-ANH-30042": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No evidence was found of restricted-distribution amounts under §268 Abs. 8 HGB.",
    ),
    "HGB-ANH-30043": (
        "N/A",
        "EXEMPTION_CLAIMED",
        "High",
        "Checklist trigger condition states that deferred-tax-basis disclosure under §285 Nr. 29 HGB is exempt for medium-sized capital companies under §288 Abs. 2 Satz 1 HGB.",
    ),
    "HGB-ANH-30044": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No deferred-tax liability recognition was identified in the filing.",
    ),
    "HGB-ANH-30045": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No minimum-tax disclosure was identified and the filing gives no indication that this row was triggered.",
    ),
    "HGB-ANH-30046": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No separate item of exceptional size or exceptional significance was identified beyond the normal results discussion.",
    ),
    "HGB-ANH-30047": (
        "N/A",
        "EXEMPTION_CLAIMED",
        "High",
        "Checklist trigger condition states that §285 Nr. 32 HGB is exempt for medium-sized capital companies under §288 Abs. 2 Satz 1 HGB.",
    ),
    "HGB-ANH-30048": (
        "N/A",
        "ENTITY_SPECIFIC",
        "Medium",
        "No post-balance-sheet event disclosure was identified in the notes.",
    ),
    "HGB-ANH-30050": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The filing does not indicate use of the §286 Abs. 2 disadvantage exception for revenue disaggregation.",
    ),
    "HGB-ANH-30015": (
        "N/A",
        "REPEALED_ITEM",
        "High",
        "§285 Nr. 5 HGB is repealed (`weggefallen`) and should not be treated as an active disclosure requirement.",
    ),
    "HGB-ANH-30016": (
        "N/A",
        "REPEALED_ITEM",
        "High",
        "§285 Nr. 6 HGB is repealed (`weggefallen`) and should not be treated as an active disclosure requirement.",
    ),
    "HGB-LAG-40005": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The filing does not indicate that the company is an Inlandsemittent issuing securities, so §289 Abs. 1 Satz 5 HGB does not apply.",
    ),
    "HGB-BIL-10046": (
        "N/A",
        "LINE_ITEM_NOT_PRESENT",
        "Medium",
        "The filing shows liabilities to shareholders and liabilities to undertakings with which a participation relationship exists, but it does not provide affirmative evidence of liabilities to affiliated companies (`verbundene Unternehmen`).",
    ),
    "HGB-LAG-40010": (
        "N/A",
        "REPEALED_ITEM",
        "High",
        "§289 Abs. 2 Nr. 4 HGB is repealed (`weggefallen`) and should not be treated as an active disclosure requirement.",
    ),
    "HGB-LAG-40011": (
        "N/A",
        "ENTITY_SPECIFIC",
        "High",
        "The filing does not indicate that the company is a capital-market-oriented company within §264d HGB, so §289 Abs. 4 HGB does not apply.",
    ),
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def candidate_terms(source_text: str) -> list[str]:
    terms = {source_text.strip()}
    for chunk in re.split(r"[;,]", source_text):
        chunk = chunk.strip()
        if chunk:
            terms.add(chunk)
    if "/" in source_text:
        for part in source_text.split("/"):
            part = part.strip()
            if part:
                terms.add(part)
    if "davon" in source_text.lower():
        terms.add(source_text.lower().split("davon", 1)[0].strip())
    cleaned = []
    for term in terms:
        norm = normalize(term)
        words = [w for w in norm.split() if len(w) >= 4 and w not in STOPWORDS]
        if len(words) >= 1 and len(norm) >= 6:
            cleaned.append(term.strip())
    cleaned.sort(key=len, reverse=True)
    return cleaned


def stem_token(token: str) -> str:
    token = normalize(token)
    if len(token) <= 4:
        return token
    for suffix in ("ungen", "lichen", "heiten", "keiten", "ungen", "ern", "ern", "ung", "lich", "keit", "heit", "chen", "ern", "en", "er", "es", "e", "n", "s"):
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def significant_stems(text: str) -> list[str]:
    stems = []
    for token in normalize(text).split():
        if len(token) < 4 or token in STOPWORDS:
            continue
        stem = stem_token(token)
        if len(stem) < 4 or stem in GENERIC_STEMS:
            continue
        if stem not in stems:
            stems.append(stem)
    return stems


def find_keyword_evidence(text: str, keywords: list[str]) -> str | None:
    for keyword in keywords:
        if normalize(keyword) in normalize(text):
            return keyword
    return None


def page_blob(pages: list[str], section: str) -> str:
    return "\n".join(pages[i] for i in SECTION_PAGE_MAP[section])


def section_blob(pages: list[str], section: str) -> str:
    return "\n".join(pages[i] for i in SECTION_PAGE_MAP[section])


def detect_exactish(item: dict, pages: list[str]) -> tuple[bool, str | None, int | None]:
    relevant_pages = SECTION_PAGE_MAP[item["section"]]
    for term in candidate_terms(item["source_text_de"]):
        norm_term = normalize(term)
        for idx in relevant_pages:
            page_text = pages[idx]
            if norm_term and norm_term in normalize(page_text):
                return True, term, idx + 1
    return False, None, None


def detect_cross_evidence(item: dict, section_blobs: dict[str, str], primary_section: str) -> tuple[bool, str | None]:
    sources = [s for s in item.get("cross_evidence_sources", []) if s in section_blobs and s != primary_section]
    if not sources:
        return False, None

    exact_terms = candidate_terms(item["source_text_de"])
    phrase_stems = significant_stems(item["source_text_de"])
    first_two = phrase_stems[:2] if len(phrase_stems) >= 2 else []

    for source in sources:
        source_text = section_blobs[source]
        normalized_source = normalize(source_text)
        for term in exact_terms:
            if normalize(term) in normalized_source:
                return True, f"{source}: matched German anchor term '{term}' outside the primary statement."

        if first_two:
            source_stems = [stem_token(tok) for tok in normalized_source.split()]
            matched = False
            first_stem, second_stem = first_two
            for idx, stem in enumerate(source_stems):
                if stem != first_stem:
                    continue
                window = source_stems[idx + 1 : idx + 5]
                if second_stem in window:
                    matched = True
                    break
            if matched:
                return True, f"{source}: matched ordered cross-evidence stems '{' '.join(first_two)}' derived from '{item['source_text_de']}'."

    return False, None


def is_medium_sized(metadata: dict) -> bool:
    size_class = normalize(metadata.get("size_class", ""))
    entity_type = normalize(metadata.get("entity_type", ""))
    return "medium" in size_class or "mittelgross" in size_class or "medium" in entity_type or "mittelgross" in entity_type


def publication_relief_applies(item: dict, metadata: dict) -> bool:
    if item.get("section") != "Bilanz":
        return False
    if item.get("verification_mode") != "line_item_if_present":
        return False
    if not is_medium_sized(metadata):
        return False
    return item.get("hgb_reference") not in MEDIUM_PUBLICATION_REQUIRED_BILANZ_REFERENCES


def uses_gesamtkostenverfahren(metadata: dict) -> bool:
    return "gesamtkostenverfahren" in normalize(metadata.get("pl_format", ""))


def guv_aggregation_relief_applies(item: dict, metadata: dict, primary_section_text: str) -> bool:
    if item.get("section") != "GuV":
        return False
    if item.get("verification_mode") != "line_item_if_present":
        return False
    if not is_medium_sized(metadata):
        return False
    if not uses_gesamtkostenverfahren(metadata):
        return False
    if item.get("hgb_reference") not in GUV_AGGREGATION_RELIEF_REFERENCES:
        return False
    return "rohergebnis" in normalize(primary_section_text)


def has_anlagenspiegel_attachment(section_blobs: dict[str, str]) -> bool:
    anhang = normalize(section_blobs.get("Anhang", ""))
    return "anlagenspiegel" in anhang and "anlage 1" in anhang


def result_row(item_id: str, response: str, reason_code: str | None, confidence: str, evidence: str, audit_notes: str = "") -> dict:
    return {
        "id": item_id,
        "response": response,
        "reason_code": reason_code,
        "confidence": confidence,
        "evidence": evidence,
        "audit_notes": audit_notes,
        "verified_by": VERIFIED_BY,
        "verification_date": VERIFICATION_DATE,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    checklist = json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))
    metadata = checklist.get("metadata", {})
    items = checklist["checklist"]

    reader = PdfReader(str(PDF_PATH))
    pages = [page.extract_text() or "" for page in reader.pages]
    EXTRACTED_TEXT_PATH.write_text(
        "\n\n".join(f"--- PAGE {i + 1} ---\n{page}" for i, page in enumerate(pages)),
        encoding="utf-8",
    )

    results = []
    section_blobs = {section: page_blob(pages, section) for section in SECTION_PAGE_MAP}

    for item in items:
        item_id = item["id"]

        if item_id in MANUAL_RESPONSES:
            response, reason_code, confidence, evidence = MANUAL_RESPONSES[item_id]
            results.append(result_row(item_id, response, reason_code, confidence, evidence))
            continue

        section_text = section_blobs[item["section"]]
        manual_keywords = MANUAL_KEYWORDS.get(item_id)
        if manual_keywords:
            matched = find_keyword_evidence(section_text, manual_keywords)
            if matched:
                page = next(
                    (
                        idx + 1
                        for idx in SECTION_PAGE_MAP[item["section"]]
                        if normalize(matched) in normalize(pages[idx])
                    ),
                    None,
                )
                evidence = f"Page {page}: matched filing text '{matched}' in the expected {item['section']} section."
                results.append(result_row(item_id, "Yes", None, "High", evidence))
                continue

        if item["obligation"] == "C":
            trigger = item.get("trigger_condition") or ""
            if "§286 Abs. 3" in item["hgb_reference"]:
                results.append(
                    result_row(
                        item_id,
                        "Review",
                        "JUDGMENT_REQUIRED",
                        "Medium",
                        "The filing does not explicitly state whether §286 Abs. 3 HGB was used to omit §285 Nr. 11 or 11b disclosures. Manual follow-up is needed because the row is conditional and omission-based.",
                    )
                )
            elif "§285 Nr. 21" in item["hgb_reference"]:
                results.append(
                    result_row(
                        item_id,
                        "N/A",
                        "ENTITY_SPECIFIC",
                        "Medium",
                        "No disclosure of off-market related-party transactions was found, and no affirmative evidence in the filing shows that the specific fact pattern in the trigger condition exists.",
                    )
                )
            else:
                results.append(
                    result_row(
                        item_id,
                        "N/A",
                        "ENTITY_SPECIFIC",
                        "Medium",
                        f"Conditional row not triggered based on the current filing context. Trigger condition: {trigger}",
                    )
                )
            continue

        found, term, page = detect_exactish(item, pages)
        if found:
            evidence = f"Page {page}: matched German anchor term '{term}' in the {item['section']} section."
            results.append(result_row(item_id, "Yes", None, "High", evidence))
            continue

        if guv_aggregation_relief_applies(item, metadata, section_blobs.get("GuV", "")):
            evidence = (
                "The published GuV uses the aggregated line item 'Rohergebnis'. For a medium-sized capital company using the "
                "Gesamtkostenverfahren, §276 HGB permits aggregation of §275 Abs. 2 Nr. 1 bis 5 HGB into 'Rohergebnis'."
            )
            results.append(result_row(item_id, "N/A", "AGGREGATION_RELIEF", "High", evidence))
            continue

        if item_id in {"HGB-ANH-30007", "HGB-ANH-30008", "HGB-ANH-30009"} and has_anlagenspiegel_attachment(section_blobs):
            evidence = (
                "The notes state that the Anlagenspiegel is provided as 'Anlage 1 zum Anhang'. The current extracted filing text does not "
                "contain that attachment detail, so this row cannot be fully verified from the available text extraction alone."
            )
            results.append(result_row(item_id, "Review", "PDF_EXTRACTION_LIMIT", "Medium", evidence))
            continue

        if item_id == "HGB-ANH-30002":
            evidence = (
                "No indication was found that accounting options were exercised outside the balance sheet or profit and loss account in a way "
                "that required a separate note disclosure under §284 Abs. 1 Satz 2 HGB."
            )
            results.append(result_row(item_id, "N/A", "ENTITY_SPECIFIC", "Medium", evidence))
            continue

        if item_id == "HGB-ANH-30012":
            evidence = (
                "No off-balance-sheet transactions requiring a dedicated §285 Nr. 3 HGB disclosure were identified in the filing."
            )
            results.append(result_row(item_id, "N/A", "ENTITY_SPECIFIC", "Medium", evidence))
            continue

        if item_id == "HGB-LAG-40008":
            evidence = (
                "The filing does not evidence a distinct research-and-development function or activity requiring separate discussion under "
                "§289 Abs. 2 Nr. 2 HGB."
            )
            results.append(result_row(item_id, "N/A", "ENTITY_SPECIFIC", "Medium", evidence))
            continue

        if item_id == "HGB-LAG-40009":
            evidence = (
                "The filing does not evidence existing Zweigniederlassungen within the meaning of §289 Abs. 2 Nr. 3 HGB. References to stores "
                "or sales locations alone do not clearly establish reportable branch establishments."
            )
            results.append(result_row(item_id, "N/A", "ENTITY_SPECIFIC", "Medium", evidence))
            continue

        if item.get("verification_mode") == "line_item_if_present":
            contradictory, contradiction_evidence = detect_cross_evidence(item, section_blobs, item["section"])
            if contradictory:
                if publication_relief_applies(item, metadata):
                    evidence = (
                        f"The underlying fact is evidenced elsewhere in the filing, but this specific Bilanz sub-line is not among "
                        f"the additional separate disclosures required for a medium-sized company in the published balance sheet under §327 Nr. 1 HGB. "
                        f"{contradiction_evidence}"
                    )
                    results.append(result_row(item_id, "N/A", "PUBLICATION_RELIEF", "High", evidence))
                    continue
                evidence = (
                    f"The required line item was not found in the primary {item['section']} statement, but affirmative evidence of the underlying fact was found elsewhere in the filing. "
                    f"{contradiction_evidence}"
                )
                results.append(result_row(item_id, "No", "MISSING_EVIDENCE", "Medium", evidence))
                continue

            evidence = (
                f"The required line item was not found in the primary {item['section']} statement, and the configured cross-evidence sources "
                f"({', '.join(item.get('cross_evidence_sources', []))}) did not show affirmative evidence that the underlying fact exists for this entity."
            )
            results.append(result_row(item_id, "N/A", "LINE_ITEM_NOT_PRESENT", "Medium", evidence))
            continue

        if item["section"] in {"Bilanz", "GuV"}:
            searched = "; ".join(candidate_terms(item["source_text_de"])[:3])
            evidence = (
                f"Searched pages {', '.join(str(i + 1) for i in SECTION_PAGE_MAP[item['section']])} for "
                f"the line-item anchor '{searched}' in the {item['section']} section but did not find a matching presentation."
            )
            results.append(result_row(item_id, "No", "MISSING_EVIDENCE", "Medium", evidence))
            continue

        if item["section"] == "Lagebericht":
            evidence = (
                f"Searched management-report pages {', '.join(str(i + 1) for i in SECTION_PAGE_MAP['Lagebericht'])} "
                f"for the target topic and German anchor term '{item['source_text_de'][:120]}' but could not confirm the disclosure."
            )
            results.append(result_row(item_id, "No", "MISSING_EVIDENCE", "Medium", evidence))
            continue

        evidence = (
            f"Searched note pages {', '.join(str(i + 1) for i in SECTION_PAGE_MAP['Anhang'])} for the German anchor term "
            f"'{item['source_text_de'][:120]}' and did not find a reliable match. This may indicate either a missing disclosure or a fact-conditioned item "
            f"that needs human review."
        )
        results.append(result_row(item_id, "Review", "JUDGMENT_REQUIRED", "Low", evidence))

    RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
