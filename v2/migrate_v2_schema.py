#!/usr/bin/env python3
"""Migrate legacy v2 checklist/results artifacts to the current schema."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECKLIST_PATH = ROOT / "checklist.json"
RESULTS_PATH = ROOT / "results.json"
SOURCE_MANIFEST_PATH = ROOT / "source_manifest.json"
RUN_SUMMARY_PATH = ROOT / "run_summary.md"

SECTION_PREFIX = {
    "Bilanz": ("BIL", 10000),
    "GuV": ("GUV", 20000),
    "Anhang": ("ANH", 30000),
    "Lagebericht": ("LAG", 40000),
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def iso_date(value: str) -> str:
    month_map = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12",
    }
    parts = value.split()
    if len(parts) == 3:
        day, month, year = parts
        return f"{year}-{month_map[month]}-{int(day):02d}"
    return value


def law_from_item(item: dict) -> str:
    ref = item.get("hgb_reference", "")
    url = item.get("source_url", "")
    if "GmbHG" in ref or "/gmbhg/" in url:
        return "GmbHG"
    return "HGB"


def paragraph_from_ref(ref: str) -> str | None:
    match = re.search(r"§\s*([\d]+[a-zA-Z]?)", ref)
    return match.group(1) if match else None


def historical_source_url(item: dict) -> str:
    law = law_from_item(item)
    paragraph = paragraph_from_ref(item.get("hgb_reference", ""))
    if paragraph:
        return f"https://www.buzer.de/{paragraph}_{law}.htm"
    return ""


def build_new_id(section: str, index: int) -> str:
    prefix, base = SECTION_PREFIX[section]
    return f"HGB-{prefix}-{base + index:05d}"


def migrate_checklist() -> dict:
    data = load_json(CHECKLIST_PATH)
    metadata = data.get("metadata", {})
    items = data["checklist"]

    target_fy_iso = iso_date(metadata.get("applicable_date", "31 December 2023"))
    section_counts = defaultdict(int)
    old_occurrences = defaultdict(int)
    id_map = {}
    migrated_items = []

    for item in items:
        section = item["section"]
        section_counts[section] += 1
        new_id = build_new_id(section, section_counts[section])

        old_id = item["id"]
        old_occurrences[old_id] += 1
        id_map[(old_id, old_occurrences[old_id])] = new_id

        migrated_items.append(
            {
                "id": new_id,
                "section": section,
                "sub_section": item.get("sub_section", ""),
                "disclosure_item": item.get("disclosure_item", ""),
                "hgb_reference": item.get("hgb_reference", ""),
                "effective_version_date": target_fy_iso,
                "historical_source_url": historical_source_url(item),
                "official_reference_url": item.get("source_url", ""),
                "source_anchor": item.get("hgb_reference", ""),
                "source_text_de": f"Normanker: {item.get('hgb_reference', '')}. Historischer Volltext ist in der Quellreferenz nachzuladen.",
                "translation_status": "normalized",
                "translation_note": "Migrated from legacy v2 artifact; German source excerpt not yet backfilled.",
                "obligation": item.get("obligation", ""),
                "trigger_condition": item.get("trigger_condition"),
                "evidence_location": item.get("evidence_location", ""),
                "completeness_prompt": item.get("completeness_prompt", ""),
            }
        )

    migrated_metadata = {
        **metadata,
        "schema_version": "v3-migrated",
        "target_fy": metadata.get("applicable_date", ""),
        "target_fy_effective_date": target_fy_iso,
        "workflow_version": "legacy-v2-schema-migration",
    }

    dump_json(CHECKLIST_PATH, {"metadata": migrated_metadata, "checklist": migrated_items})
    return {"metadata": migrated_metadata, "items": migrated_items, "id_map": id_map}


def migrate_results(id_map: dict) -> list[dict]:
    results = load_json(RESULTS_PATH)
    old_occurrences = defaultdict(int)
    migrated_results = []

    for row in results:
        old_id = row["id"]
        old_occurrences[old_id] += 1
        new_id = id_map[(old_id, old_occurrences[old_id])]

        migrated_results.append(
            {
                "id": new_id,
                "response": row.get("response", "Review"),
                "reason_code": row.get("reason_code"),
                "confidence": row.get("confidence"),
                "evidence": row.get("evidence", ""),
                "audit_notes": row.get("audit_notes", ""),
                "verified_by": row.get("verified_by", ""),
                "verification_date": row.get("verification_date", ""),
            }
        )

    dump_json(RESULTS_PATH, migrated_results)
    return migrated_results


def build_source_manifest(metadata: dict, items: list[dict]):
    unique_sources = {}
    for item in items:
        key = (item["source_anchor"], item["historical_source_url"], item["official_reference_url"])
        unique_sources[key] = {
            "source_anchor": item["source_anchor"],
            "historical_source_url": item["historical_source_url"],
            "official_reference_url": item["official_reference_url"],
            "effective_version_date": item["effective_version_date"],
        }

    manifest = {
        "schema_version": "v3-migrated",
        "target_fy": metadata.get("target_fy", ""),
        "target_fy_effective_date": metadata.get("target_fy_effective_date", ""),
        "entity_profile": {
            "entity_type": metadata.get("entity_type", ""),
            "size_class": metadata.get("size_class", ""),
            "reporting_framework": metadata.get("reporting_framework", ""),
            "pl_format": metadata.get("pl_format", ""),
        },
        "source_hierarchy": {
            "historical_source_of_record": "Buzer.de",
            "official_cross_reference": "Gesetze im Internet",
        },
        "workflow_version": metadata.get("workflow_version", ""),
        "spec_version": "3.0",
        "run_date": metadata.get("generated_date", ""),
        "migration_note": "Migrated from legacy v2 artifacts. Historical source URLs were derived from legacy statutory references; German source excerpts still require backfill from the historical source set.",
        "sources": list(unique_sources.values()),
    }
    dump_json(SOURCE_MANIFEST_PATH, manifest)


def build_run_summary(metadata: dict, items: list[dict], results: list[dict]):
    by_response = defaultdict(int)
    for row in results:
        by_response[row["response"]] += 1

    lines = [
        "# Run Summary",
        "",
        "## Status",
        "",
        "This artifact set was migrated from legacy `v2` outputs into the current schema.",
        "",
        "## Scope",
        "",
        f"- Entity type: {metadata.get('entity_type', '')}",
        f"- Size class: {metadata.get('size_class', '')}",
        f"- Framework: {metadata.get('reporting_framework', '')}",
        f"- P&L format: {metadata.get('pl_format', '')}",
        f"- Target FY: {metadata.get('target_fy', '')}",
        "",
        "## Artifact Summary",
        "",
        f"- Checklist items: {len(items)}",
        f"- Yes: {by_response.get('Yes', 0)}",
        f"- No: {by_response.get('No', 0)}",
        f"- N/A: {by_response.get('N/A', 0)}",
        f"- Review: {by_response.get('Review', 0)}",
        "",
        "## Migration Notes",
        "",
        "- IDs were renumbered to match the current section block scheme.",
        "- Legacy `version_info` and `source_url` fields were migrated into the new provenance fields.",
        "- `source_text_de` values are placeholders pending historical-source excerpt backfill.",
    ]
    RUN_SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    checklist_state = migrate_checklist()
    results = migrate_results(checklist_state["id_map"])
    build_source_manifest(checklist_state["metadata"], checklist_state["items"])
    build_run_summary(checklist_state["metadata"], checklist_state["items"], results)
    print("Migrated checklist.json, results.json, source_manifest.json, and run_summary.md")


if __name__ == "__main__":
    main()
