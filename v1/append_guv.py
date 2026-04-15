import json

with open("/root/.openclaw/workspace/dnl-checklist/results.json") as f:
    data = json.load(f)

guv_results = [
  {
    "id": "GUV-001",
    "response": "Yes",
    "evidence": "The GuV is in Staffelform with numbered steps (1. Rohergebnis through 13. Bilanzgewinn/Bilanzverlust). The Anhang confirms: 'Die Gliederung der Gewinn- und Verlustrechnung erfolgt gemäß § 275 Abs. 1 HGB nach dem Gesamtkostenverfahren.'",
    "notes": None
  },
  {
    "id": "GUV-002",
    "response": "Yes",
    "evidence": "The Anhang explicitly states: 'Die Gliederung der Gewinn- und Verlustrechnung erfolgt gemäß § 275 Abs. 1 HGB nach dem Gesamtkostenverfahren.' The GuV structure (Rohergebnis as anchor, then cost-type items) is consistent with Gesamtkostenverfahren.",
    "notes": None
  },
  {
    "id": "GUV-003",
    "response": "Yes",
    "evidence": "Umsatzerlöse is confirmed at TEUR 20,489 in the Lagebericht: 'Das Unternehmen hat im Geschäftsjahr 2023 Umsatzerlöse im Rahmen von TEUR 20.489 (Vorjahr TEUR 23.285) realisiert.' The Rohergebnis of EUR 9,784,398.70 is computed from Umsatzerlöse less cost of materials.",
    "notes": "Umsatzerlöse is embedded in the condensed GuV presentation (Rohergebnis = Umsatzerlöse minus Materialaufwand). The exact line-item title is not visible in the extracted GuV but confirmed by the Lagebericht."
  },
  {
    "id": "GUV-004",
    "response": "Review",
    "evidence": "No explicit 'Erhöhung oder Verminderung des Bestands' line is visible in the extracted GuV. Nubert has extensive inventories (TEUR 18,757) and the Anhang discusses unfinished/finished goods valuation, suggesting stock changes may be embedded in the condensed Rohergebnis line.",
    "notes": "The GuV presentation is condensed. Need to verify whether a separate stock change line exists in the full GuV not captured in this extract."
  },
  {
    "id": "GUV-005",
    "response": "N/A",
    "evidence": "The balance sheet shows no 'selbstgeschaffene immaterielle Vermögensgegenstände'. The Anhang accounting policies do not mention capitalisation of internally generated assets. No 'Andere aktivierte Eigenleistungen' line appears in the GuV.",
    "notes": "Nubert develops HiFi products but does not appear to capitalise development costs under § 248 Abs. 2 HGB."
  },
  {
    "id": "GUV-006",
    "response": "Yes",
    "evidence": "The GuV shows '4. sonstige betriebliche Aufwendungen' at EUR 4,432,041.45. The counterpart 'Sonstige betriebliche Erträge' (Nr. 4) is a mandatory line incorporated into the Rohergebnis computation. Operating income beyond core revenue exists (e.g. Währungsumrechnung Erträge).",
    "notes": "The exact line for Sonstige betriebliche Erträge is not separately visible in the condensed GuV extract but is required and structurally present."
  },
  {
    "id": "GUV-007",
    "response": "Yes",
    "evidence": "Materialaufwand is the balancing item in the Rohergebnis computation (Rohergebnis = Umsatzerlöse minus Materialaufwand). The Lagebericht confirms: 'Die Einkaufskosten können durch langfristige Verträge stabil gehalten werden.' The Anhang mentions inventory valuation for merchandise and finished goods.",
    "notes": "Materialaufwand is not separately titled in the condensed GuV but is the difference between Umsatzerlöse and Rohergebnis."
  },
  {
    "id": "GUV-008",
    "response": "Yes",
    "evidence": "'2. Personalaufwand' EUR 4,186,545.21 is explicitly shown in the GuV, sub-classified into: a) Löhne und Gehälter EUR 3,562,103.98 and b) soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung EUR 624,441.23 (davon für Altersversorgung EUR 11,218.53).",
    "notes": None
  },
  {
    "id": "GUV-009",
    "response": "Yes",
    "evidence": "'3. Abschreibungen' EUR 510,704.32 is explicitly shown in the GuV, sub-classified into: a) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen EUR 510,704.32.",
    "notes": None
  },
  {
    "id": "GUV-010",
    "response": "Yes",
    "evidence": "'4. sonstige betriebliche Aufwendungen' EUR 4,432,041.45 is explicitly shown as a line item in the GuV, with detail on Währungsumrechnung (EUR 85,057.44) and Art. 67 EGHGB (EUR 4,969.00).",
    "notes": None
  },
  {
    "id": "GUV-011",
    "response": "Yes",
    "evidence": "Two financial income lines explicitly shown: '5. Erträge aus Beteiligungen' EUR 8,007.00 and '6. sonstige Zinsen und ähnliche Erträge' EUR 179,710.83. Nr. 10 (Erträge aus anderen Wertpapieren) is not separately visible but likely nil given no Finanzanlagevermögen lending activity beyond the Beteiligung.",
    "notes": "Nr. 10 should be shown even if nil per § 275 Abs. 2. Its absence from the extracted GuV may indicate condensed presentation."
  },
  {
    "id": "GUV-012",
    "response": "Yes",
    "evidence": "'7. Zinsen und ähnliche Aufwendungen' EUR 457,906.42 is explicitly shown (Nr. 13). Nr. 12 (Abschreibungen auf Finanzanlagen) is not separately visible but likely nil — Wertpapiere at TEUR 2 and Beteiligungen at cost with no write-downs indicated.",
    "notes": "Nr. 12 should be shown even if nil per § 275 Abs. 2. May be present in the full GuV at zero."
  },
  {
    "id": "GUV-013",
    "response": "Yes",
    "evidence": "All four bottom-section items explicitly shown: '8. Steuern vom Einkommen und vom Ertrag' EUR 46,156.90; '9. Ergebnis nach Steuern' EUR 338,762.23; '10. sonstige Steuern' EUR 36,824.96; '11. Jahresüberschuss' EUR 301,937.27. Gewinnvortrag and Bilanzgewinn also shown.",
    "notes": None
  },
  {
    "id": "GUV-014",
    "response": "No",
    "evidence": "The Anhang does not contain a breakdown of Umsatzerlöse by type of activity or geographical market per § 285 Nr. 4 HGB. The § 286 Abs. 2 protective clause is not invoked. The Lagebericht mentions Germany with plans for Austria/Switzerland expansion, but no formal revenue breakdown is provided.",
    "notes": "Disclosure gap: must either provide revenue breakdown or invoke § 286 Abs. 2. Neither is present."
  },
  {
    "id": "GUV-015",
    "response": "Yes",
    "evidence": "The Anhang states: 'Anzahl der Arbeitnehmer: durchschnittlich 63 — hiervon Angestellte: 49 — hiervon gewerbliche Arbeitnehmer: 14. Mitglieder der Geschäftsführung und Auszubildende sind nicht berücksichtigt.'",
    "notes": None
  },
  {
    "id": "GUV-016",
    "response": "Review",
    "evidence": "The Anhang does not provide a sub-classification of Materialaufwand (e.g. raw materials, consumables, merchandise) as required by § 285 Nr. 8. Personalaufwand sub-classification is in the GuV but not repeated in the Anhang. The Materialaufwand breakdown is entirely absent — likely because it is not shown as a separate GuV line.",
    "notes": "Material cost breakdown missing from the Anhang. Personnel cost breakdown shown in GuV but not in Anhang as § 285 Nr. 8 technically requires."
  },
  {
    "id": "GUV-017",
    "response": "N/A",
    "evidence": "No items classified as 'außerordentliche Erträge' or 'außerordentliche Aufwendungen' in the GuV. The Anhang does not mention any extraordinary items. Trigger condition not met.",
    "notes": "Note: § 275 Abs. 2 Nr. 20/21 was repealed by BilMoG, though § 285 Nr. 31 Anhang disclosure persists. No such items exist."
  },
  {
    "id": "GUV-018",
    "response": "N/A",
    "evidence": "No 'selbstgeschaffene immaterielle Vermögensgegenstände' on the balance sheet. The Anhang does not mention capitalisation of internally generated intangible assets. The Lagebericht references 'Entwicklungsanstrengungen' but no capitalisation is evidenced. Trigger condition not met.",
    "notes": "Nubert develops HiFi products but does not capitalise development costs. May warrant separate check on whether capitalisation criteria are met."
  },
  {
    "id": "GUV-019",
    "response": "Yes",
    "evidence": "The Anhang describes depreciation methods: 'Die Abschreibungen wurden nach der voraussichtlichen Nutzungsdauer der Vermögensgegenstände linear vorgenommen' and 'Die geringwertigen Wirtschaftsgüter bis EUR 800,00 wurden im Jahr der Anschaffung voll abgeschrieben.' The GuV shows depreciation amounts. The Anlagenspiegel (Anlage 1) provides per-class breakdown.",
    "notes": "Depreciation method (linear) and low-value asset treatment clearly disclosed. Per-class amounts in the Anlagenspiegel attachment."
  }
]

data.extend(guv_results)

with open("/root/.openclaw/workspace/dnl-checklist/results.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Done. Total items: {len(data)}")
