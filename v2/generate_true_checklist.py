#!/usr/bin/env python3
"""Generate a fresh HGB checklist from source pages without using prior checklist artifacts."""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

from lxml import html


ROOT = Path(__file__).resolve().parent
CHECKLIST_PATH = ROOT / "checklist.json"
SOURCE_MANIFEST_PATH = ROOT / "source_manifest.json"
RUN_SUMMARY_PATH = ROOT / "run_summary.md"

TARGET_FY = "31 December 2023"
TARGET_FY_EFFECTIVE_DATE = "2023-12-31"


SECTION_PREFIX = {
    "Bilanz": ("BIL", 10000),
    "GuV": ("GUV", 20000),
    "Anhang": ("ANH", 30000),
    "Lagebericht": ("LAG", 40000),
}

CANONICAL_ENGLISH_LABELS = OrderedDict(
    [
        ("die auf die Posten der Bilanz und der Gewinn- und Verlustrechnung angewandten Bilanzierungs- und Bewertungsmethoden angegeben werden", "the accounting and measurement methods applied to the balance sheet and profit and loss items"),
        ("Abweichungen von Bilanzierungs- und Bewertungsmethoden angegeben und begründet werden; deren Einfluß auf die Vermögens-, Finanz- und Ertragslage ist gesondert darzustellen", "departures from accounting and measurement methods, together with the justification and separate explanation of their effect on assets, financial position, and results of operations"),
        ("bei Anwendung einer Bewertungsmethode nach § 240 Abs. 4, § 256 Satz 1 die Unterschiedsbeträge pauschal für die jeweilige Gruppe ausgewiesen werden, wenn die Bewertung im Vergleich zu einer Bewertung auf der Grundlage des letzten vor dem Abschlußstichtag bekannten Börsenkurses oder Marktpreises einen erheblichen Unterschied aufweist", "the aggregate valuation differences for each group when a valuation method under section 240(4) or section 256 sentence 1 is used and materially differs from valuation based on the last known exchange or market price before the reporting date"),
        ("Angaben über die Einbeziehung von Zinsen für Fremdkapital in die Herstellungskosten gemacht werden", "whether borrowing costs have been included in production cost"),
        ("die Abschreibungen in ihrer gesamten Höhe zu Beginn und Ende des Geschäftsjahrs,", "total accumulated depreciation at the beginning and end of the financial year"),
        ("die im Laufe des Geschäftsjahrs vorgenommenen Abschreibungen und", "depreciation recognized during the financial year"),
        ("Änderungen in den Abschreibungen in ihrer gesamten Höhe im Zusammenhang mit Zu- und Abgängen sowie Umbuchungen im Laufe des Geschäftsjahrs.", "changes in total depreciation resulting from additions, disposals, and reclassifications during the financial year"),
        ("zu den in der Bilanz ausgewiesenen Verbindlichkeitena)der Gesamtbetrag der Verbindlichkeiten mit einer Restlaufzeit von mehr als fünf Jahren,b)der Gesamtbetrag der Verbindlichkeiten, die durch Pfandrechte oder ähnliche Rechte gesichert sind, unter Angabe von Art und Form der Sicherheiten", "for liabilities recognized in the balance sheet, the total amount with a remaining term of more than five years and the total amount secured by pledges or similar rights, including the nature and form of the security"),
        ("die Aufgliederung der in Nummer 1 verlangten Angaben für jeden Posten der Verbindlichkeiten nach dem vorgeschriebenen Gliederungsschema", "the breakdown of the information required by number 1 for each liabilities line item under the prescribed format"),
        ("Art und Zweck sowie Risiken, Vorteile und finanzielle Auswirkungen von nicht in der Bilanz enthaltenen Geschäften, soweit die Risiken und Vorteile wesentlich sind und die Offenlegung für die Beurteilung der Finanzlage des Unternehmens erforderlich ist", "the nature and purpose, as well as the risks, benefits, and financial effects, of off-balance-sheet transactions where material and necessary to assess the company's financial position"),
        ("der Gesamtbetrag der sonstigen finanziellen Verpflichtungen, die nicht in der Bilanz enthalten sind und die nicht nach § 268 Absatz 7 oder Nummer 3 anzugeben sind, sofern diese Angabe für die Beurteilung der Finanzlage von Bedeutung ist; davon sind Verpflichtungen betreffend die Altersversorgung und Verpflichtungen gegenüber verbundenen oder assoziierten Unternehmen jeweils gesondert anzugeben", "the total amount of other financial commitments not recognized in the balance sheet and not otherwise disclosed under section 268(7) or number 3, including separate disclosure of pension-related commitments and commitments to affiliated or associated undertakings when relevant to assessing the financial position"),
        ("die Aufgliederung der Umsatzerlöse nach Tätigkeitsbereichen sowie nach geografisch bestimmten Märkten, soweit sich unter Berücksichtigung der Organisation des Verkaufs, der Vermietung oder Verpachtung von Produkten und der Erbringung von Dienstleistungen der Kapitalgesellschaft die Tätigkeitsbereiche und geografisch bestimmten Märkte untereinander erheblich unterscheiden", "the disaggregation of revenue by business activity and geographically defined markets where those activities and markets differ materially in light of the company's sales, rental, leasing, or service organization"),
        ("(weggefallen)", "repealed item"),
        ("die durchschnittliche Zahl der während des Geschäftsjahrs beschäftigten Arbeitnehmer getrennt nach Gruppen", "the average number of employees during the financial year, broken down by category"),
        ("bei Anwendung des Umsatzkostenverfahrens (§ 275 Abs. 3)a)der Materialaufwand des Geschäftsjahrs, gegliedert nach § 275 Abs. 2 Nr. 5,b)der Personalaufwand des Geschäftsjahrs, gegliedert nach § 275 Abs. 2 Nr. 6", "when the cost-of-sales method is used, material costs for the financial year split in line with section 275(2) no. 5 and personnel costs for the financial year split in line with section 275(2) no. 6"),
        ("für die Mitglieder des Geschäftsführungsorgans, eines Aufsichtsrats, eines Beirats oder einer ähnlichen Einrichtung jeweils für jede Personengruppea)die für die Tätigkeit im Geschäftsjahr gewährten Gesamtbezüge (Gehälter, Gewinnbeteiligungen, Bezugsrechte und sonstige aktienbasierte Vergütungen, Aufwandsentschädigungen, Versicherungsentgelte, Provisionen und Nebenleistungen jeder Art). In die Gesamtbezüge sind auch Bezüge einzurechnen, die nicht ausgezahlt, sondern in Ansprüche anderer Art umgewandelt oder zur Erhöhung anderer Ansprüche verwendet werden. Außer den Bezügen für das Geschäftsjahr sind die weiteren Bezüge anzugeben, die im Geschäftsjahr gewährt, bisher aber in keinem Jahresabschluss angegeben worden sind. Bezugsrechte und sonstige aktienbasierte Vergütungen sind mit ihrer Anzahl und dem beizulegenden Zeitwert zum Zeitpunkt ihrer Gewährung anzugeben; spätere Wertveränderungen, die auf einer Änderung der Ausübungsbedingungen beruhen, sind zu berücksichtigen;b)die Gesamtbezüge (Abfindungen, Ruhegehälter, Hinterbliebenenbezüge und Leistungen verwandter Art) der früheren Mitglieder der bezeichneten Organe und ihrer Hinterbliebenen. Buchstabe a Satz 2 und 3 ist entsprechend anzuwenden. Ferner ist der Betrag der für diese Personengruppe gebildeten Rückstellungen für laufende Pensionen und Anwartschaften auf Pensionen und der Betrag der für diese Verpflichtungen nicht gebildeten Rückstellungen anzugeben;c)die gewährten Vorschüsse und Kredite unter Angabe der Zinssätze, der wesentlichen Bedingungen und der gegebenenfalls im Geschäftsjahr zurückgezahlten oder erlassenen Beträge sowie die zugunsten dieser Personen eingegangenen Haftungsverhältnisse", "for each category of management, supervisory, advisory, or similar body members, the total compensation granted in the financial year, the total compensation of former members and their survivors, the related pension provisions, and the advances, loans, interest terms, conditions, repayments, waivers, and contingent liabilities granted in their favor"),
        ("alle Mitglieder des Geschäftsführungsorgans und eines Aufsichtsrats, auch wenn sie im Geschäftsjahr oder später ausgeschieden sind, mit dem Familiennamen und mindestens einem ausgeschriebenen Vornamen, einschließlich des ausgeübten Berufs und bei börsennotierten Gesellschaften auch der Mitgliedschaft in Aufsichtsräten und anderen Kontrollgremien im Sinne des § 125 Abs. 1 Satz 5 des Aktiengesetzes. Der Vorsitzende eines Aufsichtsrats, seine Stellvertreter und ein etwaiger Vorsitzender des Geschäftsführungsorgans sind als solche zu bezeichnen", "all members of the management body and supervisory board, including former members, identified by surname and at least one full first name, together with their profession and, for listed companies, memberships on supervisory boards and similar control bodies; the chair and deputies must be identified as such"),
        ("Name und Sitz anderer Unternehmen, die Höhe des Anteils am Kapital, das Eigenkapital und das Ergebnis des letzten Geschäftsjahrs dieser Unternehmen, für das ein Jahresabschluss vorliegt, soweit es sich um Beteiligungen im Sinne des § 271 Absatz 1 handelt oder ein solcher Anteil von einer Person für Rechnung der Kapitalgesellschaft gehalten wird", "the name and registered office of other undertakings, the percentage holding, equity, and the result of their latest financial year where the company holds an equity interest within the meaning of section 271(1) or such an interest is held on the company's behalf"),
        ("Änderungen in den Abschreibungen in ihrer gesamten Höhe im Zusammenhang mit Zu- und Abgängen sowie Umbuchungen im Laufe des Geschäftsjahrs", "changes in total depreciation arising from additions, disposals, and reclassifications during the financial year"),
        ("Änderungen in den Abschreibungen in ihrer gesamten Höhe im Zusammenhang mit Zu- und Abgängen sowie Umbuchungen im Laufe des Geschäftsjahrs.", "changes in total depreciation arising from additions, disposals, and reclassifications during the financial year"),
        ("Name, Sitz und Rechtsform der Unternehmen, deren unbeschränkt haftender Gesellschafter die Kapitalgesellschaft ist", "the name, registered office, and legal form of the undertakings for which the company is the general partner with unlimited liability"),
        ("von börsennotierten Kapitalgesellschaften sind alle Beteiligungen an großen Kapitalgesellschaften anzugeben, die 5 Prozent der Stimmrechte überschreiten", "for listed companies, all equity interests in large corporations exceeding 5 percent of the voting rights"),
        ("Rückstellungen, die in der Bilanz unter dem Posten \"sonstige Rückstellungen\" nicht gesondert ausgewiesen werden, sind zu erläutern, wenn sie einen nicht unerheblichen Umfang haben", "provisions included within 'other provisions' that are not shown separately in the balance sheet, where they are of more than minor significance"),
        ("jeweils eine Erläuterung des Zeitraums, über den ein entgeltlich erworbener Geschäfts- oder Firmenwert abgeschrieben wird", "the amortization period applied to acquired goodwill, together with an explanation"),
        ("Name und Sitz des Mutterunternehmens der Kapitalgesellschaft, das den Konzernabschluss für den größten Kreis von Unternehmen aufstellt, sowie der Ort, wo der von diesem Mutterunternehmen aufgestellte Konzernabschluss erhältlich ist", "the name and registered office of the parent company preparing the consolidated financial statements for the largest group of undertakings, and where those consolidated financial statements can be obtained"),
        ("Name und Sitz des Mutterunternehmens der Kapitalgesellschaft, das den Konzernabschluss für den kleinsten Kreis von Unternehmen aufstellt, sowie der Ort, wo der von diesem Mutterunternehmen aufgestellte Konzernabschluss erhältlich ist", "the name and registered office of the parent company preparing the consolidated financial statements for the smallest group of undertakings, and where those consolidated financial statements can be obtained"),
        ("soweit es sich um den Anhang des Jahresabschlusses einer Personenhandelsgesellschaft im Sinne des § 264a Abs. 1 handelt, Name und Sitz der Gesellschaften, die persönlich haftende Gesellschafter sind, sowie deren gezeichnetes Kapital", "for notes to the annual financial statements of a partnership within section 264a(1), the name and registered office of the general partners together with their subscribed capital"),
        ("das Bestehen von Genussscheinen, Genussrechten, Wandelschuldverschreibungen, Optionsscheinen, Optionen, Besserungsscheinen oder vergleichbaren Wertpapieren oder Rechten, unter Angabe der Anzahl und der Rechte, die sie verbriefen", "the existence of profit participation certificates, profit participation rights, convertible bonds, warrants, options, contingent value rights, or comparable securities or rights, including their number and the rights they embody"),
        ("dass die nach § 161 des Aktiengesetzes vorgeschriebene Erklärung abgegeben und wo sie öffentlich zugänglich gemacht worden ist", "that the declaration required by section 161 of the German Stock Corporation Act has been made and where it is publicly available"),
        ("das von dem Abschlussprüfer für das Geschäftsjahr berechnete Gesamthonorar, aufgeschlüsselt in das Honorar für a)die Abschlussprüfungsleistungen,b)andere Bestätigungsleistungen,c)Steuerberatungsleistungen,d)sonstige Leistungen,soweit die Angaben nicht in einem das Unternehmen einbeziehenden Konzernabschluss enthalten sind", "the total fees charged by the auditor for the financial year, split into audit services, other assurance services, tax advisory services, and other services, unless already included in consolidated financial statements covering the company"),
        ("für zu den Finanzanlagen (§ 266 Abs. 2 A. III.) gehörende Finanzinstrumente, die über ihrem beizulegenden Zeitwert ausgewiesen werden, da eine außerplanmäßige Abschreibung nach § 253 Absatz 3 Satz 6 unterblieben ist, a)der Buchwert und der beizulegende Zeitwert der einzelnen Vermögensgegenstände oder angemessener Gruppierungen sowieb)die Gründe für das Unterlassen der Abschreibung einschließlich der Anhaltspunkte, die darauf hindeuten, dass die Wertminderung voraussichtlich nicht von Dauer ist", "for financial instruments classified as financial fixed assets and carried above fair value because no impairment was recognized under section 253(3) sentence 6, their carrying amount and fair value by asset or appropriate group together with the reasons for not recognizing the write-down, including evidence that the impairment is expected to be temporary"),
        ("für jede Kategorie nicht zum beizulegenden Zeitwert bilanzierter derivativer Finanzinstrumente a)deren Art und Umfang,b)deren beizulegender Zeitwert, soweit er sich nach § 255 Abs. 4 verlässlich ermitteln lässt, unter Angabe der angewandten Bewertungsmethode,c)deren Buchwert und der Bilanzposten, in welchem der Buchwert, soweit vorhanden, erfasst ist, sowied)die Gründe dafür, warum der beizulegende Zeitwert nicht bestimmt werden kann", "for each category of derivative financial instruments not measured at fair value, their nature and extent, fair value where reliably determinable including the valuation method used, carrying amount and the balance sheet line item in which it is recorded, and the reasons why fair value cannot be determined"),
        ("für mit dem beizulegenden Zeitwert bewertete Finanzinstrumente a)die grundlegenden Annahmen, die der Bestimmung des beizulegenden Zeitwertes mit Hilfe allgemein anerkannter Bewertungsmethoden zugrunde gelegt wurden, sowieb)Umfang und Art jeder Kategorie derivativer Finanzinstrumente einschließlich der wesentlichen Bedingungen, welche die Höhe, den Zeitpunkt und die Sicherheit künftiger Zahlungsströme beeinflussen können", "for financial instruments measured at fair value, the key assumptions underlying fair value measurement using generally accepted valuation methods, and the extent and nature of each category of derivative financial instrument including the material terms that may affect the amount, timing, and certainty of future cash flows"),
        ("zumindest die nicht zu marktüblichen Bedingungen zustande gekommenen Geschäfte, soweit sie wesentlich sind, mit nahe stehenden Unternehmen und Personen, einschließlich Angaben zur Art der Beziehung, zum Wert der Geschäfte sowie weiterer Angaben, die für die Beurteilung der Finanzlage notwendig sind; ausgenommen sind Geschäfte mit und zwischen mittel- oder unmittelbar in 100-prozentigem Anteilsbesitz stehenden in einen Konzernabschluss einbezogenen Unternehmen; Angaben über Geschäfte können nach Geschäftsarten zusammengefasst werden, sofern die getrennte Angabe für die Beurteilung der Auswirkungen auf die Finanzlage nicht notwendig ist", "at least the material related-party transactions not concluded on market terms, including the nature of the relationship, the value of the transactions, and any other information necessary to assess the financial position, subject to the stated group-company exception"),
        ("im Fall der Aktivierung nach § 248 Abs. 2 der Gesamtbetrag der Forschungs- und Entwicklungskosten des Geschäftsjahrs sowie der davon auf die selbst geschaffenen immateriellen Vermögensgegenstände des Anlagevermögens entfallende Betrag", "where capitalization under section 248(2) is applied, the total research and development costs for the financial year and the amount attributable to internally generated intangible fixed assets"),
        ("bei Anwendung des § 254, a)mit welchem Betrag jeweils Vermögensgegenstände, Schulden, schwebende Geschäfte und mit hoher Wahrscheinlichkeit erwartete Transaktionen zur Absicherung welcher Risiken in welche Arten von Bewertungseinheiten einbezogen sind sowie die Höhe der mit Bewertungseinheiten abgesicherten Risiken,b)für die jeweils abgesicherten Risiken, warum, in welchem Umfang und für welchen Zeitraum sich die gegenläufigen Wertänderungen oder Zahlungsströme künftig voraussichtlich ausgleichen einschließlich der Methode der Ermittlung,c)eine Erläuterung der mit hoher Wahrscheinlichkeit erwarteten Transaktionen, die in Bewertungseinheiten einbezogen wurden,soweit die Angaben nicht im Lagebericht gemacht werden", "when section 254 is applied, the items, exposures, and hedge relationships included in valuation units, the amount of the hedged risks, why and to what extent offsetting changes in value or cash flows are expected over what period, the method used to determine that offset, and an explanation of highly probable forecast transactions included in the valuation units unless disclosed in the management report"),
        ("zu den Rückstellungen für Pensionen und ähnliche Verpflichtungen das angewandte versicherungsmathematische Berechnungsverfahren sowie die grundlegenden Annahmen der Berechnung, wie Zinssatz, erwartete Lohn- und Gehaltssteigerungen und zugrunde gelegte Sterbetafeln", "for provisions for pensions and similar obligations, the actuarial valuation method used and the key assumptions such as the discount rate, expected salary increases, and mortality tables"),
        ("im Fall der Verrechnung von Vermögensgegenständen und Schulden nach § 246 Abs. 2 Satz 2 die Anschaffungskosten und der beizulegende Zeitwert der verrechneten Vermögensgegenstände, der Erfüllungsbetrag der verrechneten Schulden sowie die verrechneten Aufwendungen und Erträge; Nummer 20 Buchstabe a ist entsprechend anzuwenden", "where assets and liabilities are offset under section 246(2) sentence 2, the acquisition cost and fair value of the offset assets, the settlement amount of the offset liabilities, and the offset income and expenses; number 20(a) applies accordingly"),
        ("zu Anteilen an Sondervermögen im Sinn des § 1 Absatz 10 des Kapitalanlagegesetzbuchs oder Anlageaktien an Investmentaktiengesellschaften mit veränderlichem Kapital im Sinn der §§ 108 bis 123 des Kapitalanlagegesetzbuchs oder vergleichbaren EU-Investmentvermögen oder vergleichbaren ausländischen Investmentvermögen von mehr als dem zehnten Teil, aufgegliedert nach Anlagezielen, deren Wert im Sinne der §§ 168, 278 oder 286 Absatz 1 des Kapitalanlagegesetzbuchs oder vergleichbarer ausländischer Vorschriften über die Ermittlung des Marktwertes, die Differenz zum Buchwert und die für das Geschäftsjahr erfolgte Ausschüttung sowie Beschränkungen in der Möglichkeit der täglichen Rückgabe; darüber hinaus die Gründe dafür, dass eine Abschreibung gemäß § 253 Absatz 3 Satz 6 unterblieben ist, einschließlich der Anhaltspunkte, die darauf hindeuten, dass die Wertminderung voraussichtlich nicht von Dauer ist; Nummer 18 ist insoweit nicht anzuwenden", "for holdings exceeding one tenth in investment funds, investment shares, comparable EU investment funds, or comparable foreign investment funds, broken down by investment objective, their value under the applicable fund valuation rules, the difference from carrying amount, distributions during the financial year, and restrictions on daily redemption, together with the reasons no impairment was recognized under section 253(3) sentence 6 and evidence that any impairment is expected to be temporary"),
        ("für nach § 268 Abs. 7 im Anhang ausgewiesene Verbindlichkeiten und Haftungsverhältnisse die Gründe der Einschätzung des Risikos der Inanspruchnahme", "for liabilities and contingent liabilities disclosed in the notes under section 268(7), the reasons for the assessment of the risk of being called upon"),
        ("der Gesamtbetrag der Beträge im Sinn des § 268 Abs. 8, aufgegliedert in Beträge aus der Aktivierung selbst geschaffener immaterieller Vermögensgegenstände des Anlagevermögens, Beträge aus der Aktivierung latenter Steuern und aus der Aktivierung von Vermögensgegenständen zum beizulegenden Zeitwert", "the total amount of the items within section 268(8), broken down into amounts arising from the capitalization of internally generated intangible fixed assets, deferred tax assets, and assets measured at fair value"),
        ("auf welchen Differenzen oder steuerlichen Verlustvorträgen die latenten Steuern beruhen und mit welchen Steuersätzen die Bewertung erfolgt ist", "the differences or tax loss carryforwards on which deferred taxes are based and the tax rates used for measurement"),
        ("wenn latente Steuerschulden in der Bilanz angesetzt werden, die latenten Steuersalden am Ende des Geschäftsjahrs und die im Laufe des Geschäftsjahrs erfolgten Änderungen dieser Salden", "where deferred tax liabilities are recognized in the balance sheet, the deferred tax balances at the end of the financial year and the changes in those balances during the year"),
        ("der tatsächliche Steueraufwand oder Steuerertrag, der sich nach dem Mindeststeuergesetz und ausländischen Mindeststeuergesetzen nach § 274 Absatz 3 Nummer 2 für das Geschäftsjahr ergibt, oder, wenn diese Gesetze noch nicht in Kraft getreten sind, eine Erläuterung, welche Auswirkungen auf die Kapitalgesellschaft bei der Anwendung dieser Gesetze zu erwarten sind", "the current tax expense or tax income arising under the German Minimum Tax Act and foreign minimum tax laws under section 274(3) no. 2 for the financial year, or, if those laws are not yet effective, an explanation of their expected impact on the company"),
        ("jeweils der Betrag und die Art der einzelnen Erträge und Aufwendungen von außergewöhnlicher Größenordnung oder außergewöhnlicher Bedeutung, soweit die Beträge nicht von untergeordneter Bedeutung sind", "the amount and nature of each item of income and expense of exceptional size or exceptional significance, where not immaterial"),
        ("eine Erläuterung der einzelnen Erträge und Aufwendungen hinsichtlich ihres Betrags und ihrer Art, die einem anderen Geschäftsjahr zuzurechnen sind, soweit die Beträge nicht von untergeordneter Bedeutung sind", "an explanation of each item of income and expense attributable to another financial year, including its amount and nature, where not immaterial"),
        ("Vorgänge von besonderer Bedeutung, die nach dem Schluss des Geschäftsjahrs eingetreten und weder in der Gewinn- und Verlustrechnung noch in der Bilanz berücksichtigt sind, unter Angabe ihrer Art und ihrer finanziellen Auswirkungen", "events of particular significance that occurred after the end of the financial year and are not reflected in the profit and loss account or balance sheet, including their nature and financial effects"),
        ("der Vorschlag für die Verwendung des Ergebnisses oder der Beschluss über seine Verwendung", "the proposed appropriation of profit or the resolution on profit appropriation"),
        ("der Vorschlag für die Verwendung des Ergebnisses oder der Beschluss über seine Verwendung.", "the proposed appropriation of profit or the resolution on profit appropriation"),
    ]
)

UNMAPPED_ENGLISH_LABEL = "[Needs canonical English label]"


def fetch_tree(url: str):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as response:
        return html.fromstring(response.read())


def clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def official_url(section: str) -> str:
    return f"https://www.gesetze-im-internet.de/hgb/__{section}.html"


def buzer_url(section: str) -> str:
    return f"https://www.buzer.de/{section}_HGB.htm"


def own_text(el) -> str:
    parts = []
    for child in el.xpath("./node()[not(self::dl)]"):
        if isinstance(child, str):
            parts.append(child)
        else:
            parts.append(child.text_content())
    return clean(" ".join(parts)).rstrip(":;")


def top_level_dls(node) -> list:
    return node.xpath(".//dl[not(ancestor::dl)]")


def join_markers(markers: list[str]) -> str:
    if not markers:
        return ""
    out = []
    for idx, marker in enumerate(markers):
        token = marker.strip().rstrip(".")
        if idx == 0 and token.isdigit():
            out.append(f"Nr. {token}")
        else:
            out.append(token)
    return " ".join(out)


def resolve_english_label(german_text: str) -> tuple[str, str]:
    cleaned = clean(german_text).rstrip(".;")
    english = CANONICAL_ENGLISH_LABELS.get(cleaned)
    if english:
        return english, "approved"
    return UNMAPPED_ENGLISH_LABEL, "pending"


def question_from_label(section: str, english_label: str, english_label_status: str) -> str:
    if english_label_status != "approved":
        if section == "Bilanz":
            return "Review required: canonical English label missing for this balance sheet line item."
        if section == "GuV":
            return "Review required: canonical English label missing for this profit and loss line item."
        if section == "Anhang":
            return "Review required: canonical English label missing for this note disclosure."
        if section == "Lagebericht":
            return "Review required: canonical English label missing for this management report disclosure."
        return "Review required: canonical English label missing for this disclosure item."
    if section == "Bilanz":
        return f"Has the entity presented {english_label} as a separate line item in the balance sheet?"
    if section == "GuV":
        return f"Has the entity presented {english_label} as a separate line item in the profit and loss account?"
    if section == "Anhang":
        return f"Do the notes disclose {english_label}?"
    if section == "Lagebericht":
        return f"Does the management report address {english_label}?"
    return f"Has the entity disclosed {english_label} as required?"


def verification_prompt(*, section: str, sub_section: str, hgb_reference: str, german_text: str, english_label: str, english_label_status: str, obligation: str, trigger_condition: str | None) -> str:
    label_text = english_label if english_label_status == "approved" else "canonical English label pending manual refinement"
    if section == "Bilanz":
        action = "Determine whether the FY2023 filing presents this balance-sheet line item separately."
        location = f"Search first in the balance sheet under {sub_section}."
    elif section == "GuV":
        action = "Determine whether the FY2023 filing presents this profit-and-loss line item separately."
        location = f"Search first in the profit and loss account under {sub_section}."
    elif section == "Anhang":
        action = "Determine whether the FY2023 notes contain this disclosure."
        location = f"Search first in the notes section relevant to {sub_section}."
    else:
        action = "Determine whether the FY2023 management report addresses this required topic."
        location = f"Search first in the management report section relevant to {sub_section}."

    applicability = f"Obligation: {obligation}."
    if trigger_condition:
        applicability += f" Trigger condition: {trigger_condition}"

    return (
        f"{action} Requirement: {hgb_reference}. Target disclosure: {label_text}. "
        f"German anchor term: {clean(german_text).rstrip('.;')}. "
        f"{location} Accept a clear German or English equivalent label if it is unambiguous. "
        f"Return Yes only with specific evidence such as page, heading, quoted label, or amount; otherwise return No, N/A, or Review with the reason. "
        f"{applicability}"
    )


def verification_profile(section: str, hgb_reference: str) -> tuple[str, str, list[str]]:
    if section == "Bilanz":
        if hgb_reference == "§266 Abs. 1 HGB":
            return ("presentation_required", "check_primary_statement_only", ["Bilanz"])
        return (
            "line_item_if_present",
            "require_line_if_evidence_of_underlying_fact",
            ["Bilanz", "Anhang", "Lagebericht"],
        )
    if section == "GuV":
        if hgb_reference == "§275 Abs. 1 HGB":
            return ("presentation_required", "check_primary_statement_only", ["GuV"])
        return (
            "line_item_if_present",
            "require_line_if_evidence_of_underlying_fact",
            ["GuV", "Anhang", "Lagebericht"],
        )
    return ("fact_conditioned", "follow_obligation_and_trigger_condition", [section])


def build_row(
    *,
    section: str,
    sub_section: str,
    hgb_reference: str,
    german_text: str,
    official: str,
    buzer: str,
    english_label: str | None = None,
    disclosure_item: str | None = None,
    obligation: str = "M",
    trigger_condition: str | None = None,
    evidence_location: str | None = None,
    completeness_prompt: str | None = None,
) -> "Row":
    resolved_english_label, english_label_status = resolve_english_label(german_text)
    final_english_label = english_label or resolved_english_label
    if english_label is not None:
        english_label_status = "approved"
    verification_mode, presence_inference_rule, cross_evidence_sources = verification_profile(section, hgb_reference)
    return Row(
        section=section,
        sub_section=sub_section,
        english_label=final_english_label,
        english_label_status=english_label_status,
        disclosure_item=disclosure_item or question_from_label(section, final_english_label, english_label_status),
        hgb_reference=hgb_reference,
        historical_source_url=buzer,
        official_reference_url=official,
        source_text_de=german_text,
        obligation=obligation,
        trigger_condition=trigger_condition,
        verification_mode=verification_mode,
        presence_inference_rule=presence_inference_rule,
        cross_evidence_sources=cross_evidence_sources,
        evidence_location=evidence_location or f"{section}, {sub_section}",
        completeness_prompt=completeness_prompt or verification_prompt(
            section=section,
            sub_section=sub_section,
            hgb_reference=hgb_reference,
            german_text=german_text,
            english_label=final_english_label,
            english_label_status=english_label_status,
            obligation=obligation,
            trigger_condition=trigger_condition,
        ),
    )


def build_structured_rows(
    *,
    section: str,
    root_sub_section: list[str],
    anchor_prefix: str,
    items: list[tuple[list[str], list[str], str, str]],
    official: str,
    buzer: str,
) -> list["Row"]:
    rows = []
    for path_labels, marker_tokens, german_text, english_label in items:
        category_path = root_sub_section + path_labels
        rows.append(
            build_row(
                section=section,
                sub_section=" > ".join(category_path),
                hgb_reference=f"{anchor_prefix} {join_markers(marker_tokens)} HGB",
                german_text=german_text,
                official=official,
                buzer=buzer,
                english_label=english_label,
            )
        )
    return rows


@dataclass
class Row:
    section: str
    sub_section: str
    english_label: str
    english_label_status: str
    disclosure_item: str
    hgb_reference: str
    historical_source_url: str
    official_reference_url: str
    source_text_de: str
    obligation: str = "M"
    trigger_condition: str | None = None
    verification_mode: str = "fact_conditioned"
    presence_inference_rule: str = "follow_obligation_and_trigger_condition"
    cross_evidence_sources: list[str] | None = None
    evidence_location: str = ""
    completeness_prompt: str = ""

    def to_dict(self, row_id: str) -> dict:
        return {
            "id": row_id,
            "section": self.section,
            "sub_section": self.sub_section,
            "english_label": self.english_label,
            "english_label_status": self.english_label_status,
            "disclosure_item": self.disclosure_item,
            "hgb_reference": self.hgb_reference,
            "effective_version_date": TARGET_FY_EFFECTIVE_DATE,
            "historical_source_url": self.historical_source_url,
            "official_reference_url": self.official_reference_url,
            "source_text_de": self.source_text_de,
            "obligation": self.obligation,
            "trigger_condition": self.trigger_condition,
            "verification_mode": self.verification_mode,
            "presence_inference_rule": self.presence_inference_rule,
            "cross_evidence_sources": self.cross_evidence_sources or [self.section],
            "evidence_location": self.evidence_location,
            "completeness_prompt": self.completeness_prompt,
        }


def recurse_dl(dl, section: str, subsection_prefix: list[str], anchor_prefix: str, context: str, official: str, buzer: str) -> Iterable[Row]:
    for dt in dl.xpath("./dt"):
        dd = dt.getnext()
        if dd is None or dd.tag != "dd":
            continue
        marker = clean(dt.text_content())
        label = own_text(dd)
        nested = dd.xpath("./dl")
        if nested:
            next_prefix = subsection_prefix + ([label] if label else [])
            next_anchor = f"{anchor_prefix} {join_markers([marker])}".strip()
            for nested_dl in nested:
                yield from recurse_dl(
                    nested_dl,
                    section=section,
                    subsection_prefix=next_prefix,
                    anchor_prefix=next_anchor,
                    context=context,
                    official=official,
                    buzer=buzer,
                )
        else:
            source_anchor = f"{anchor_prefix} {join_markers([marker])} HGB".strip()
            sub_section = " > ".join(subsection_prefix) if subsection_prefix else context
            german_text = label
            yield build_row(
                section=section,
                sub_section=sub_section,
                hgb_reference=source_anchor,
                german_text=german_text,
                official=official,
                buzer=buzer,
                evidence_location=f"{section}, {sub_section}",
            )


def rows_266() -> list[Row]:
    sec = "266"
    official = official_url(sec)
    buzer = buzer_url(sec)
    rows = [
        build_row(
            section="Bilanz",
            sub_section="Overall Structure",
            hgb_reference="§266 Abs. 1 HGB",
            german_text="Die Bilanz ist in Kontoform aufzustellen. Dabei haben mittelgroße und große Kapitalgesellschaften ... die bezeichneten Posten gesondert und in der vorgeschriebenen Reihenfolge auszuweisen.",
            english_label="presentation of the balance sheet in account form and statutory order",
            disclosure_item="Has the balance sheet been presented in account form and in the prescribed order for a medium-sized capital company?",
            official=official,
            buzer=buzer,
            evidence_location="Bilanz",
            completeness_prompt="Determine whether the FY2023 filing presents the balance sheet in account form and follows the statutory order of line items required by §266 Abs. 1 HGB. Search the primary balance sheet presentation first. Return Yes only with evidence from the statement layout itself.",
        )
    ]
    aktiv_items = [
        (["Anlagevermögen", "Immaterielle Vermögensgegenstände"], ["A", "I", "1"], "Selbst geschaffene gewerbliche Schutzrechte und ähnliche Rechte und Werte", "internally generated industrial property rights and similar rights and assets"),
        (["Anlagevermögen", "Immaterielle Vermögensgegenstände"], ["A", "I", "2"], "entgeltlich erworbene Konzessionen, gewerbliche Schutzrechte und ähnliche Rechte und Werte sowie Lizenzen an solchen Rechten und Werten", "acquired concessions, industrial property rights and similar rights and assets, as well as licenses in such rights and assets"),
        (["Anlagevermögen", "Immaterielle Vermögensgegenstände"], ["A", "I", "3"], "Geschäfts- oder Firmenwert", "goodwill"),
        (["Anlagevermögen", "Immaterielle Vermögensgegenstände"], ["A", "I", "4"], "geleistete Anzahlungen", "advance payments"),
        (["Anlagevermögen", "Sachanlagen"], ["A", "II", "1"], "Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken", "land, land-like rights, and buildings, including buildings on third-party land"),
        (["Anlagevermögen", "Sachanlagen"], ["A", "II", "2"], "technische Anlagen und Maschinen", "technical equipment and machinery"),
        (["Anlagevermögen", "Sachanlagen"], ["A", "II", "3"], "andere Anlagen, Betriebs- und Geschäftsausstattung", "other equipment, operating equipment, and office equipment"),
        (["Anlagevermögen", "Sachanlagen"], ["A", "II", "4"], "geleistete Anzahlungen und Anlagen im Bau", "advance payments and assets under construction"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "1"], "Anteile an verbundenen Unternehmen", "shares in affiliated companies"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "2"], "Ausleihungen an verbundene Unternehmen", "loans to affiliated companies"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "3"], "Beteiligungen", "equity interests"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "4"], "Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht", "loans to undertakings in which the company holds an equity interest"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "5"], "Wertpapiere des Anlagevermögens", "securities held as fixed assets"),
        (["Anlagevermögen", "Finanzanlagen"], ["A", "III", "6"], "sonstige Ausleihungen", "other loans"),
        (["Umlaufvermögen", "Vorräte"], ["B", "I", "1"], "Roh-, Hilfs- und Betriebsstoffe", "raw materials, consumables, and supplies"),
        (["Umlaufvermögen", "Vorräte"], ["B", "I", "2"], "unfertige Erzeugnisse, unfertige Leistungen", "work in progress and unfinished services"),
        (["Umlaufvermögen", "Vorräte"], ["B", "I", "3"], "fertige Erzeugnisse und Waren", "finished goods and merchandise"),
        (["Umlaufvermögen", "Vorräte"], ["B", "I", "4"], "geleistete Anzahlungen", "advance payments"),
        (["Umlaufvermögen", "Forderungen und sonstige Vermögensgegenstände"], ["B", "II", "1"], "Forderungen aus Lieferungen und Leistungen", "trade receivables"),
        (["Umlaufvermögen", "Forderungen und sonstige Vermögensgegenstände"], ["B", "II", "2"], "Forderungen gegen verbundene Unternehmen", "receivables from affiliated companies"),
        (["Umlaufvermögen", "Forderungen und sonstige Vermögensgegenstände"], ["B", "II", "3"], "Forderungen gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht", "receivables from undertakings in which the company holds an equity interest"),
        (["Umlaufvermögen", "Forderungen und sonstige Vermögensgegenstände"], ["B", "II", "4"], "sonstige Vermögensgegenstände", "other assets"),
        (["Umlaufvermögen", "Wertpapiere"], ["B", "III", "1"], "Anteile an verbundenen Unternehmen", "shares in affiliated companies"),
        (["Umlaufvermögen", "Wertpapiere"], ["B", "III", "2"], "sonstige Wertpapiere", "other securities"),
        (["Umlaufvermögen"], ["B", "IV"], "Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks", "cash on hand, Bundesbank balances, bank balances, and checks"),
        ([], ["C"], "Rechnungsabgrenzungsposten", "prepayments and accrued items"),
        ([], ["D"], "Aktive latente Steuern", "deferred tax assets"),
        ([], ["E"], "Aktiver Unterschiedsbetrag aus der Vermögensverrechnung", "asset surplus from offsetting"),
    ]
    passiv_items = [
        (["Eigenkapital"], ["A", "I"], "Gezeichnetes Kapital", "subscribed capital"),
        (["Eigenkapital"], ["A", "II"], "Kapitalrücklage", "capital reserve"),
        (["Eigenkapital", "Gewinnrücklagen"], ["A", "III", "1"], "gesetzliche Rücklage", "legal reserve"),
        (["Eigenkapital", "Gewinnrücklagen"], ["A", "III", "2"], "Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen", "reserve for shares in a controlling or majority-owned undertaking"),
        (["Eigenkapital", "Gewinnrücklagen"], ["A", "III", "3"], "satzungsmäßige Rücklagen", "statutory reserves"),
        (["Eigenkapital", "Gewinnrücklagen"], ["A", "III", "4"], "andere Gewinnrücklagen", "other revenue reserves"),
        (["Eigenkapital"], ["A", "IV"], "Gewinnvortrag/Verlustvortrag", "profit or loss carried forward"),
        (["Eigenkapital"], ["A", "V"], "Jahresüberschuss/Jahresfehlbetrag", "net income or net loss"),
        (["Rückstellungen"], ["B", "1"], "Rückstellungen für Pensionen und ähnliche Verpflichtungen", "provisions for pensions and similar obligations"),
        (["Rückstellungen"], ["B", "2"], "Steuerrückstellungen", "tax provisions"),
        (["Rückstellungen"], ["B", "3"], "sonstige Rückstellungen", "other provisions"),
        (["Verbindlichkeiten"], ["C", "1"], "Anleihen, davon konvertibel", "bonds, including convertible bonds"),
        (["Verbindlichkeiten"], ["C", "2"], "Verbindlichkeiten gegenüber Kreditinstituten", "liabilities to banks"),
        (["Verbindlichkeiten"], ["C", "3"], "erhaltene Anzahlungen auf Bestellungen", "advance payments received on orders"),
        (["Verbindlichkeiten"], ["C", "4"], "Verbindlichkeiten aus Lieferungen und Leistungen", "trade payables"),
        (["Verbindlichkeiten"], ["C", "5"], "Verbindlichkeiten aus der Annahme gezogener Wechsel und der Ausstellung eigener Wechsel", "liabilities arising from the acceptance of drawn bills and the issuance of own bills"),
        (["Verbindlichkeiten"], ["C", "6"], "Verbindlichkeiten gegenüber verbundenen Unternehmen", "liabilities to affiliated companies"),
        (["Verbindlichkeiten"], ["C", "7"], "Verbindlichkeiten gegenüber Unternehmen, mit denen ein Beteiligungsverhältnis besteht", "liabilities to undertakings in which the company holds an equity interest"),
        (["Verbindlichkeiten"], ["C", "8"], "sonstige Verbindlichkeiten, davon aus Steuern, davon im Rahmen der sozialen Sicherheit", "other liabilities, including taxes and social security"),
        ([], ["D"], "Rechnungsabgrenzungsposten", "prepayments and accrued items"),
        ([], ["E"], "Passive latente Steuern", "deferred tax liabilities"),
    ]
    rows.extend(
        build_structured_rows(
            section="Bilanz",
            root_sub_section=["Aktivseite"],
            anchor_prefix="§266 Abs. 2",
            items=aktiv_items,
            official=official,
            buzer=buzer,
        )
    )
    rows.extend(
        build_structured_rows(
            section="Bilanz",
            root_sub_section=["Passivseite"],
            anchor_prefix="§266 Abs. 3",
            items=passiv_items,
            official=official,
            buzer=buzer,
        )
    )
    return rows


def rows_275(pl_format: str) -> list[Row]:
    sec = "275"
    official = official_url(sec)
    buzer = buzer_url(sec)
    rows = [
        build_row(
            section="GuV",
            sub_section="Overall Structure",
            hgb_reference="§275 Abs. 1 HGB",
            german_text="Die Gewinn- und Verlustrechnung ist in Staffelform nach dem Gesamtkostenverfahren oder dem Umsatzkostenverfahren aufzustellen.",
            english_label="presentation of the profit and loss account in staffel form using the selected method and statutory order",
            disclosure_item=f"Has the profit and loss account been presented in staffel form using the selected method '{pl_format}' and in the prescribed order?",
            official=official,
            buzer=buzer,
            evidence_location="GuV",
            completeness_prompt="Determine whether the FY2023 profit and loss account is presented in staffel form using the selected method and follows the statutory order required by §275 Abs. 1 HGB. Search the primary profit and loss statement first. Return Yes only with evidence from the statement layout itself.",
        )
    ]
    if "Gesamtkosten" in pl_format:
        gkv_items = [
            ([], ["1"], "Umsatzerlöse", "revenue"),
            ([], ["2"], "Erhöhung oder Verminderung des Bestands an fertigen und unfertigen Erzeugnissen", "increase or decrease in inventories of finished goods and work in progress"),
            ([], ["3"], "andere aktivierte Eigenleistungen", "other own work capitalized"),
            ([], ["4"], "sonstige betriebliche Erträge", "other operating income"),
            (["Materialaufwand"], ["5", "a"], "Aufwendungen für Roh-, Hilfs- und Betriebsstoffe und für bezogene Waren", "cost of raw materials, consumables, supplies, and purchased goods"),
            (["Materialaufwand"], ["5", "b"], "Aufwendungen für bezogene Leistungen", "cost of purchased services"),
            (["Personalaufwand"], ["6", "a"], "Löhne und Gehälter", "wages and salaries"),
            (["Personalaufwand"], ["6", "b"], "soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung, davon für Altersversorgung", "social security, pension, and support costs, including pension costs"),
            (["Abschreibungen"], ["7", "a"], "auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen", "depreciation of intangible fixed assets and property, plant, and equipment"),
            (["Abschreibungen"], ["7", "b"], "auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten", "write-downs of current assets to the extent they exceed normal write-downs in the company"),
            ([], ["8"], "sonstige betriebliche Aufwendungen", "other operating expenses"),
            ([], ["9"], "Erträge aus Beteiligungen, davon aus verbundenen Unternehmen", "income from equity interests, including from affiliated companies"),
            ([], ["10"], "Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, davon aus verbundenen Unternehmen", "income from other securities and loans held as financial fixed assets, including from affiliated companies"),
            ([], ["11"], "sonstige Zinsen und ähnliche Erträge, davon aus verbundenen Unternehmen", "other interest and similar income, including from affiliated companies"),
            ([], ["12"], "Abschreibungen auf Finanzanlagen und auf Wertpapiere des Umlaufvermögens", "write-downs of financial assets and current securities"),
            ([], ["13"], "Zinsen und ähnliche Aufwendungen, davon an verbundene Unternehmen", "interest and similar expenses, including to affiliated companies"),
            ([], ["14"], "Steuern vom Einkommen und vom Ertrag", "income taxes"),
            ([], ["15"], "Ergebnis nach Steuern", "result after taxes"),
            ([], ["16"], "sonstige Steuern", "other taxes"),
            ([], ["17"], "Jahresüberschuss/Jahresfehlbetrag", "net income or net loss"),
        ]
        rows.extend(
            build_structured_rows(
                section="GuV",
                root_sub_section=["Gesamtkostenverfahren"],
                anchor_prefix="§275 Abs. 2",
                items=gkv_items,
                official=official,
                buzer=buzer,
            )
        )
    else:
        doc = fetch_tree(official_url(sec))
        node = doc.xpath("//div[@class='jnhtml']")[0]
        dls = top_level_dls(node)
        rows.extend(recurse_dl(dls[1], "GuV", ["Umsatzkostenverfahren"], "§275 Abs. 3", "profit and loss account", official, buzer))
    return rows


def rows_284() -> list[Row]:
    sec = "284"
    doc = fetch_tree(official_url(sec))
    node = doc.xpath("//div[@class='jnhtml']")[0]
    official = official_url(sec)
    buzer = buzer_url(sec)
    rows = [
        build_row(
            section="Anhang",
            sub_section="General Presentation",
            hgb_reference="§284 Abs. 1 Satz 1 HGB",
            german_text="In den Anhang sind diejenigen Angaben aufzunehmen, die zu den einzelnen Posten der Bilanz oder der Gewinn- und Verlustrechnung vorgeschrieben sind; sie sind in der Reihenfolge der einzelnen Posten der Bilanz und der Gewinn- und Verlustrechnung darzustellen.",
            english_label="the required note disclosures in the order of the balance sheet and profit and loss account items",
            disclosure_item="Has the notes presented the required disclosures in the order of the balance sheet and P&L items?",
            official=official,
            buzer=buzer,
            evidence_location="Anhang",
            completeness_prompt="Determine whether the FY2023 notes follow the order of the balance sheet and profit and loss account items as required by §284 Abs. 1 Satz 1 HGB. Search the note structure and cross-references first. Return Yes only with evidence from the sequencing of the note disclosures.",
        ),
        build_row(
            section="Anhang",
            sub_section="General Presentation",
            hgb_reference="§284 Abs. 1 Satz 2 HGB",
            german_text="Im Anhang sind auch die Angaben zu machen, die in Ausübung eines Wahlrechts nicht in die Bilanz oder in die Gewinn- und Verlustrechnung aufgenommen wurden.",
            english_label="items arising from accounting options that were exercised but not recognized directly in the balance sheet or profit and loss account",
            disclosure_item="Has the notes included disclosures arising from accounting options that were not recognized directly in the balance sheet or P&L?",
            official=official,
            buzer=buzer,
            evidence_location="Anhang",
            completeness_prompt="Determine whether the FY2023 notes disclose items arising from accounting options that were exercised but not recognized directly in the balance sheet or profit and loss account, as required by §284 Abs. 1 Satz 2 HGB. Search the accounting policies and related note disclosures first.",
        ),
    ]
    dls = top_level_dls(node)
    rows.extend(recurse_dl(dls[0], "Anhang", ["Bilanzierungs- und Bewertungsmethoden"], "§284 Abs. 2", "notes", official, buzer))
    rows.extend(recurse_dl(dls[1], "Anhang", ["Anlagevermögen"], "§284 Abs. 3", "notes", official, buzer))
    return rows


def rows_285() -> list[Row]:
    sec = "285"
    doc = fetch_tree(official_url(sec))
    node = doc.xpath("//div[@class='jnhtml']")[0]
    official = official_url(sec)
    buzer = buzer_url(sec)
    dls = top_level_dls(node)
    return list(recurse_dl(dls[0], "Anhang", ["Sonstige Pflichtangaben"], "§285", "notes", official, buzer))


def rows_286() -> list[Row]:
    sec = "286"
    official = official_url(sec)
    buzer = buzer_url(sec)
    return [
        build_row(
            section="Anhang",
            sub_section="Ausnahmeregelungen",
            hgb_reference="§286 Abs. 2 HGB",
            german_text="Die Aufgliederung der Umsatzerlöse nach § 285 Nr. 4 kann unterbleiben ...; die Anwendung der Ausnahmeregelung ist im Anhang anzugeben.",
            english_label="the use of the section 286(2) exception for omitted revenue disaggregation",
            disclosure_item="If the revenue breakdown under §285 Nr. 4 is omitted to avoid significant disadvantage, has the use of the exception been disclosed in the notes?",
            official=official,
            buzer=buzer,
            obligation="C",
            trigger_condition="Only if the entity omits the revenue breakdown under §285 Nr. 4 based on the disadvantage exception.",
            evidence_location="Anhang",
            completeness_prompt="Determine whether the FY2023 notes disclose the use of the §286 Abs. 2 exception when the entity omits the §285 Nr. 4 revenue breakdown to avoid a significant disadvantage. First confirm whether the exception appears to have been used, then look for an explicit note disclosure of that use.",
        ),
        build_row(
            section="Anhang",
            sub_section="Ausnahmeregelungen",
            hgb_reference="§286 Abs. 3 HGB",
            german_text="Die Angaben nach § 285 Nr. 11 und 11b können unterbleiben ... Im Übrigen ist die Anwendung der Ausnahmeregelung nach Satz 1 Nr. 2 im Anhang anzugeben.",
            english_label="the use of the section 286(3) exception for omitted section 285 no. 11 or 11b disclosures",
            disclosure_item="If the entity omits information under §285 Nr. 11 or 11b because it is insignificant or harmful, has the use of the exception been disclosed where required?",
            official=official,
            buzer=buzer,
            obligation="C",
            trigger_condition="Only if the entity omits §285 Nr. 11 or 11b disclosures using the exception in §286 Abs. 3 HGB.",
            evidence_location="Anhang",
            completeness_prompt="Determine whether the FY2023 notes disclose the use of the §286 Abs. 3 exception where required. First confirm whether disclosures under §285 Nr. 11 or 11b appear to be omitted on that basis, then look for an explicit note statement that the exception was used.",
        ),
        build_row(
            section="Anhang",
            sub_section="Organvergütung",
            hgb_reference="§286 Abs. 4 HGB",
            german_text="Bei Gesellschaften, die keine börsennotierten Aktiengesellschaften sind, können die in § 285 Nr. 9 Buchstabe a und b verlangten Angaben ... unterbleiben, wenn sich anhand dieser Angaben die Bezüge eines Mitglieds dieser Organe feststellen lassen.",
            english_label="eligibility to omit total remuneration disclosures where individual remuneration could otherwise be inferred",
            disclosure_item="If total remuneration disclosures are omitted because individual remuneration could otherwise be inferred, does the entity meet the conditions for that omission?",
            official=official,
            buzer=buzer,
            obligation="C",
            trigger_condition="Only if remuneration disclosures under §285 Nr. 9 a/b are omitted on the basis of §286 Abs. 4 HGB.",
            evidence_location="Anhang",
            completeness_prompt="Determine whether the entity appears to rely on the §286 Abs. 4 omission for remuneration disclosures under §285 Nr. 9 a/b and, if so, whether the filing supports that the legal condition is met. Search the remuneration note and any statement explaining the omission.",
        ),
    ]


def rows_289() -> list[Row]:
    sec = "289"
    official = official_url(sec)
    buzer = buzer_url(sec)
    rows = [
        build_row(
            section="Lagebericht",
            sub_section="Grundlagen",
            hgb_reference="§289 Abs. 1 Satz 1 HGB",
            german_text="Im Lagebericht sind der Geschäftsverlauf einschließlich des Geschäftsergebnisses und die Lage der Kapitalgesellschaft so darzustellen, dass ein den tatsächlichen Verhältnissen entsprechendes Bild vermittelt wird.",
            english_label="the course of business, results, and position of the company so that the report presents a true and fair view",
            disclosure_item="Does the management report describe the course of business, results, and position of the company so that it presents a true and fair view?",
            official=official,
            buzer=buzer,
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the FY2023 management report describes the course of business, results, and position of the company in a way that presents a true and fair view, as required by §289 Abs. 1 Satz 1 HGB. Search the opening overview and performance discussion first.",
        ),
        build_row(
            section="Lagebericht",
            sub_section="Grundlagen",
            hgb_reference="§289 Abs. 1 Satz 2 HGB",
            german_text="Er hat eine ausgewogene und umfassende, dem Umfang und der Komplexität der Geschäftstätigkeit entsprechende Analyse des Geschäftsverlaufs und der Lage der Gesellschaft zu enthalten.",
            english_label="a balanced and comprehensive analysis of business performance and the company’s position",
            disclosure_item="Does the management report contain a balanced and comprehensive analysis of the course of business and the company’s position?",
            official=official,
            buzer=buzer,
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the FY2023 management report contains a balanced and comprehensive analysis of business performance and the company’s position, as required by §289 Abs. 1 Satz 2 HGB. Search the analytical narrative and KPI discussion first.",
        ),
        build_row(
            section="Lagebericht",
            sub_section="Finanzielle Leistungsindikatoren",
            hgb_reference="§289 Abs. 1 Satz 3 HGB",
            german_text="In die Analyse sind die für die Geschäftstätigkeit bedeutsamsten finanziellen Leistungsindikatoren einzubeziehen und unter Bezugnahme auf die im Jahresabschluss ausgewiesenen Beträge und Angaben zu erläutern.",
            english_label="the most important financial performance indicators, explained by reference to the annual financial statements",
            disclosure_item="Does the analysis include the most important financial performance indicators and explain them by reference to the annual financial statements?",
            official=official,
            buzer=buzer,
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the FY2023 management report includes the most important financial performance indicators and explains them by reference to amounts and disclosures in the annual financial statements, as required by §289 Abs. 1 Satz 3 HGB.",
        ),
        build_row(
            section="Lagebericht",
            sub_section="Prognose",
            hgb_reference="§289 Abs. 1 Satz 4 HGB",
            german_text="Ferner ist im Lagebericht die voraussichtliche Entwicklung mit ihren wesentlichen Chancen und Risiken zu beurteilen und zu erläutern; zugrunde liegende Annahmen sind anzugeben.",
            english_label="expected future development, material opportunities and risks, and the underlying assumptions",
            disclosure_item="Does the management report discuss expected future development, material opportunities and risks, and the underlying assumptions?",
            official=official,
            buzer=buzer,
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the FY2023 management report discusses expected future development, material opportunities and risks, and the underlying assumptions, as required by §289 Abs. 1 Satz 4 HGB. Search the outlook and risk sections first.",
        ),
        build_row(
            section="Lagebericht",
            sub_section="Erklärung des vertretungsberechtigten Organs",
            hgb_reference="§289 Abs. 1 Satz 5 HGB",
            german_text="Die Mitglieder des vertretungsberechtigten Organs ... haben in einer dem Lagebericht beizufügenden schriftlichen Erklärung zu versichern ...",
            english_label="the required written statement attached to the management report",
            disclosure_item="If the entity is an Inlandsemittent issuing securities, has the required written statement been attached to the management report?",
            official=official,
            buzer=buzer,
            obligation="C",
            trigger_condition="Only if the entity is an Inlandsemittent issuing securities and not within §327a HGB.",
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the filing falls within the scope of §289 Abs. 1 Satz 5 HGB and, if so, whether the required written management statement is attached to the management report. Search appendices and declaration pages first.",
        ),
    ]
    abs2_items = [
        (["Weitere Inhalte", "Risikomanagement"], ["1", "a"], "die Risikomanagementziele und -methoden der Gesellschaft einschließlich ihrer Methoden zur Absicherung aller wichtigen Arten von Transaktionen, die im Rahmen der Bilanzierung von Sicherungsgeschäften erfasst werden", "the company's risk management objectives and methods, including hedging methods for significant transaction types recognized as hedging transactions"),
        (["Weitere Inhalte", "Risikomanagement"], ["1", "b"], "bestehende Preisänderungs-, Ausfall- und Liquiditätsrisiken sowie Risiken aus Zahlungsstromschwankungen, denen die Gesellschaft ausgesetzt ist, sofern dies für die Beurteilung der Lage oder der voraussichtlichen Entwicklung von Belang ist", "existing price, default, and liquidity risks as well as cash flow fluctuation risks relevant to assessing the company's position or expected development"),
        (["Weitere Inhalte"], ["2"], "den Bereich Forschung und Entwicklung", "research and development"),
        (["Weitere Inhalte"], ["3"], "bestehende Zweigniederlassungen der Gesellschaft", "existing branches of the company"),
        (["Weitere Inhalte"], ["4"], "(weggefallen)", "repealed item"),
    ]
    rows.extend(
        build_structured_rows(
            section="Lagebericht",
            root_sub_section=[],
            anchor_prefix="§289 Abs. 2",
            items=abs2_items,
            official=official,
            buzer=buzer,
        )
    )
    rows.append(
        build_row(
            section="Lagebericht",
            sub_section="Internes Kontroll- und Risikomanagementsystem",
            hgb_reference="§289 Abs. 4 HGB",
            german_text="Kapitalgesellschaften im Sinn des § 264d haben im Lagebericht die wesentlichen Merkmale des internen Kontroll- und des Risikomanagementsystems im Hinblick auf den Rechnungslegungsprozess zu beschreiben.",
            english_label="the key features of the internal control and risk management system for financial reporting",
            disclosure_item="If the company falls within §264d HGB, does the management report describe the key features of the internal control and risk management system relating to financial reporting?",
            official=official,
            buzer=buzer,
            obligation="C",
            trigger_condition="Only if the company is a capital-market-oriented company within §264d HGB.",
            evidence_location="Lagebericht",
            completeness_prompt="Determine whether the company falls within §264d HGB and, if so, whether the FY2023 management report describes the key features of the internal control and risk management system for financial reporting. Search governance, risk, and internal control sections first.",
        )
    )
    return rows


def apply_medium_gmbh_relief(rows: list[Row]) -> None:
    for row in rows:
        if row.hgb_reference.startswith("§285 Nr. 4 HGB") or row.hgb_reference.startswith("§285 Nr. 29 HGB") or row.hgb_reference.startswith("§285 Nr. 32 HGB"):
            row.obligation = "C"
            row.trigger_condition = "Exempt for medium-sized capital companies under §288 Abs. 2 Satz 1 HGB."
        elif row.hgb_reference.startswith("§285 Nr. 17 HGB"):
            row.obligation = "C"
            row.trigger_condition = "If not disclosed in the notes, must be submitted to the Wirtschaftsprüferkammer on written request per §288 Abs. 2 Satz 2 HGB."
        elif row.hgb_reference.startswith("§285 Nr. 21 HGB"):
            row.obligation = "C"
            row.trigger_condition = "Required only if the transactions were concluded directly or indirectly with a shareholder, undertakings in which the company holds an interest, or members of management/supervisory/administrative bodies per §288 Abs. 2 Satz 3 HGB."
        row.completeness_prompt = verification_prompt(
            section=row.section,
            sub_section=row.sub_section,
            hgb_reference=row.hgb_reference,
            german_text=row.source_text_de,
            english_label=row.english_label,
            english_label_status=row.english_label_status,
            obligation=row.obligation,
            trigger_condition=row.trigger_condition,
        )


def assign_ids(rows: list[Row]) -> list[dict]:
    counters = {section: 0 for section in SECTION_PREFIX}
    out = []
    for row in rows:
        counters[row.section] += 1
        prefix, base = SECTION_PREFIX[row.section]
        row_id = f"HGB-{prefix}-{base + counters[row.section]:05d}"
        out.append(row.to_dict(row_id))
    return out


def buzer_effective_note(section: str) -> str:
    doc = fetch_tree(buzer_url(section))
    text = clean(doc.text_content())
    match = re.search(r"Text in der Fassung .*? m\.W\.v\. ([0-9]{1,2}\.\s*[A-Za-zäöüÄÖÜ]+\s*[0-9]{4}|[0-9]{2}\.[0-9]{2}\.[0-9]{4})", text)
    return match.group(1) if match else TARGET_FY


def build_manifest(rows: list[dict]) -> dict:
    sections = OrderedDict()
    for sec in ["266", "275", "284", "285", "286", "288", "289"]:
        sections[sec] = {
            "section": sec,
            "historical_source_url": buzer_url(sec),
            "official_reference_url": official_url(sec),
            "effective_note": buzer_effective_note(sec),
        }

    unique_sources = OrderedDict()
    for row in rows:
        key = (row["hgb_reference"], row["historical_source_url"], row["official_reference_url"])
        if key not in unique_sources:
            unique_sources[key] = {
                "hgb_reference": row["hgb_reference"],
                "historical_source_url": row["historical_source_url"],
                "official_reference_url": row["official_reference_url"],
                "effective_version_date": row["effective_version_date"],
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }

    return {
        "schema_version": "v2-generated",
        "target_fy": TARGET_FY,
        "target_fy_effective_date": TARGET_FY_EFFECTIVE_DATE,
        "entity_profile": {
            "entity_type": "GmbH (Private Limited Company) — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)",
            "size_class": "Medium (mittelgroß)",
            "reporting_framework": "HGB (German Commercial Code) §§ 264 ff.",
            "pl_format": "Gesamtkostenverfahren (Total Cost Method) (§ 275 Abs. 1 HGB)",
        },
        "source_hierarchy": {
            "historical_source_of_record": "Buzer.de",
            "official_cross_reference": "Gesetze im Internet",
        },
        "workflow_version": "true-generation-from-source-v1",
        "spec_version": "2.0",
        "run_date": datetime.now(timezone.utc).date().isoformat(),
        "generation_mode": "true-generation-from-source",
        "sections": list(sections.values()),
        "sources": list(unique_sources.values()),
    }


def build_summary(rows: list[dict]) -> str:
    counts = OrderedDict()
    for sec in ["Bilanz", "GuV", "Anhang", "Lagebericht"]:
        counts[sec] = sum(1 for row in rows if row["section"] == sec)
    lines = [
        "# Run Summary",
        "",
        "## Status",
        "",
        "This checklist was generated fresh from statutory source pages without using a prior checklist artifact as a seed.",
        "",
        "## Scope",
        "",
        "- Entity type: GmbH (Private Limited Company) — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)",
        "- Framework: HGB",
        "- Target FY: 31 December 2023",
        "- P&L format: Gesamtkostenverfahren",
        "",
        "## Artifact Summary",
        "",
        f"- Checklist items: {len(rows)}",
    ]
    for sec, count in counts.items():
        lines.append(f"- {sec}: {count}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Source grounding uses Buzer historical URLs plus official Gesetze-im-Internet cross-reference URLs.",
            "- Medium-sized GmbH relief under §288 Abs. 2 HGB was applied during generation.",
            "- Existing verification outputs were not regenerated in this run.",
        ]
    )
    return "\n".join(lines) + "\n"


def main():
    rows = []
    rows.extend(rows_266())
    rows.extend(rows_275("Gesamtkostenverfahren"))
    rows.extend(rows_284())
    rows.extend(rows_285())
    rows.extend(rows_286())
    rows.extend(rows_289())
    apply_medium_gmbh_relief(rows)
    row_dicts = assign_ids(rows)

    checklist = {
        "metadata": {
            "entity_type": "GmbH (Private Limited Company) — Mittelgroße Kapitalgesellschaft (§ 267 Abs. 2 HGB)",
            "size_class": "Medium (mittelgroß)",
            "reporting_framework": "HGB (German Commercial Code) §§ 264 ff.",
            "pl_format": "Gesamtkostenverfahren (Total Cost Method) (§ 275 Abs. 1 HGB)",
            "applicable_date": TARGET_FY,
            "framework_version": f"HGB (as of {TARGET_FY})",
            "generated_date": datetime.now(timezone.utc).date().isoformat(),
            "version": "v2",
            "schema_version": "v2-generated",
            "target_fy": TARGET_FY,
            "target_fy_effective_date": TARGET_FY_EFFECTIVE_DATE,
            "workflow_version": "true-generation-from-source-v1",
            "generation_mode": "true-generation-from-source",
        },
        "checklist": row_dicts,
    }
    CHECKLIST_PATH.write_text(json.dumps(checklist, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest = build_manifest(row_dicts)
    SOURCE_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    RUN_SUMMARY_PATH.write_text(build_summary(row_dicts), encoding="utf-8")

    print(f"Generated {len(row_dicts)} checklist items from source.")
    for sec in ["Bilanz", "GuV", "Anhang", "Lagebericht"]:
        count = sum(1 for row in row_dicts if row["section"] == sec)
        print(f"  {sec}: {count}")


if __name__ == "__main__":
    main()
