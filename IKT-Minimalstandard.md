# Arbeitsauftrag B1B – IKT-Minimalstandard

**Quellen:**
- Medienmitteilung BWL/admin.ch (27.08.2018): <https://www.admin.ch/gov/de/start/dokumentation/medienmitteilungen.msg-id-71944.html>
- BACS/NCSC – IKT-Minimalstandards: <https://www.bacs.admin.ch/de/ikt-minimalstandards>
- Dokument «Minimalstandard zur Verbesserung der IKT-Resilienz» (Version 2018, Kap. 1.4–1.7 und Management Summary)

---

## Allgemeine Fragen

### 1. Was ist IKT-Resilienz?
**IKT-Resilienz** ist die Widerstandsfähigkeit der Informations- und Kommunikationstechnik (IKT) einer Organisation. Sie soll trotz Störungen, Ausfällen oder Cyberangriffen die kritischen Geschäftsprozesse aufrechterhalten. Falls doch etwas ausfällt, soll sie den Normalbetrieb schnell wiederherstellen.

Resilienz heisst also nicht «nie angegriffen werden», sondern: Angriffe abwehren, erkennen, darauf reagieren und sich davon erholen. Der Standard will Unternehmen ein Hilfsmittel geben, «individuell die Resilienz ihrer IKT-Infrastruktur» zu verbessern. Das ist wichtig, weil die Versorgung der Schweiz mit lebenswichtigen Gütern und Dienstleistungen von funktionierender IKT abhängt.

### 2. Die fünf Funktionen des IKT-Minimalstandards
Der Standard basiert auf dem NIST Cybersecurity Framework Core. Er umfasst diese fünf Funktionen (insgesamt 106 Massnahmen):

| # | Funktion | Englisch | Inhalt |
|---|----------|----------|--------|
| 1 | Identifizieren | Identify | Assets, Geschäftsumfeld, Vorgaben, Risiken kennen |
| 2 | Schützen | Protect | Zugriffskontrolle, Schulung, Datensicherheit, Schutztechnologie |
| 3 | Erkennen | Detect | Auffälligkeiten und Vorfälle erkennen, Überwachung |
| 4 | Reagieren | Respond | Reaktionsplanung, Kommunikation, Analyse, Schadensminderung |
| 5 | Wiederherstellen | Recover | Wiederherstellungsplanung, Verbesserungen, Kommunikation |

---

## Dokument: Minimalstandard zur Verbesserung der IKT-Resilienz

### 3. Management Summary (Zusammenfassung)
- Der IKT-Minimalstandard ist eine **Empfehlung und mögliche Richtschnur** zur Verbesserung der IKT-Resilienz.
- Er richtet sich vor allem an **Betreiber kritischer Infrastrukturen**, insbesondere an IKT-Verantwortliche und Geschäftsleitungsmitglieder. Er ist aber für jedes Unternehmen anwendbar und frei verfügbar.
- Das Dokument hat **drei Teile**:
  1. **Grundlagen:** Nachschlagewerk mit Hintergrundinformationen zur IKT-Sicherheit.
  2. **Framework:** 106 konkrete Massnahmen, gegliedert in die fünf Themenbereiche Identifizieren, Schützen, Detektieren, Reagieren, Wiederherstellen.
  3. **Self-Assessment** mit Bewertungstool (Excel): Die Organisation beurteilt den Umsetzungsstand selbst oder lässt ihn extern prüfen (Audit). Die Ergebnisse dienen auch dem Benchmarking.

### Einführung in den IKT-Minimalstandard

### 4. Wann müssen die IKT-Sicherheitsgrundsätze festgelegt werden?
**Bevor IKT-Sicherheit operativ umgesetzt wird.** Sie gehören also an den Anfang, in die Planungs- und Konzeptphase, vor die Umsetzung von Massnahmen und Strategien (z. B. Defense-in-Depth). Laut Dokument müssen die Grundsätze Folgendes festlegen:
- Was wird getan?
- Wie wird es getan?
- Wer ist dafür verantwortlich?
- Wie wird es gemessen?

### 5. Begründung
- Die Grundsätze definieren **Regeln, Prozesse, Metriken und organisatorische Strukturen**, die für effektive Planung und Steuerung nötig sind. Ohne sie fehlt der Rahmen für die Umsetzung.
- Ohne klare Zuständigkeiten und Ziele lassen sich Massnahmen weder steuern noch messen.
- Die Sicherheitsorganisation braucht Kompetenzen von der Geschäftsleitung und muss die Ressourcen klären, bevor umgesetzt wird.
- Eine spätere Festlegung führt zu unkoordinierten Massnahmen und Nachbesserungen.
- Das Dokument nennt auch: Bevor eine IKT-Sicherheitsstrategie umgesetzt werden kann, müssen Richtlinien, Prozesse und Arbeitsanweisungen identifiziert oder definiert sein (Kap. 1.5.3).

---

## Defense-in-Depth

### 6. Defense-in-Depth in einfachen Worten
Defense-in-Depth heisst **«mehrschichtige Verteidigung»**. Man verlässt sich nicht auf eine einzige Schutzmassnahme, sondern setzt **mehrere Sicherheitsmassnahmen koordiniert** ein. Wer eine Schicht überwindet, steht sofort vor der nächsten.

Das Prinzip stammt aus dem Militär: Ein Feind überwindet ein komplexes, mehrschichtiges Abwehrsystem schwerer als eine einzelne Barriere. Vergleich: eine Burg mit Wassergraben, Mauer, Tor und Wachen.

Ziel ist, Sicherheitsverletzungen zu **erkennen**, darauf zu **reagieren** und die **Folgen zu minimieren**. Der Ansatz schützt ganzheitlich Personen, Prozesse, Objekte, Daten und Geräte. Die Massnahmen müssen laufend überwacht und an neue Bedrohungen angepasst werden.

### 7. Abkürzungen ICS und APT
- **ICS** = *Industrial Control Systems*, auf Deutsch **industrielle Kontrollsysteme** (z. B. Steuerung von Kraftwerken, Anlagen, Netzen).
- **APT** = *Advanced Persistent Threat*, auf Deutsch etwa **fortgeschrittene, andauernde Bedrohung**. Gemeint sind gezielte, hochentwickelte Angriffe, bei denen sich der Angreifer über lange Zeit im System festsetzt.

### 8. Was heisst «lang unentdeckt bleiben»?
Laut Dokument können Verwundbarkeiten in ICS wegen deren **komplexer Architektur** «schlimmstenfalls sehr lange unentdeckt bleiben». Eine Schwachstelle oder ein Angriff wird also über einen langen Zeitraum (Wochen, Monate, Jahre) nicht bemerkt. Das gibt einem Angreifer Zeit, Zugriff aufzubauen und Exploits auszunutzen.

Dass Angriffe lange unentdeckt bleiben, ist typisch für APTs. Deshalb sind Überwachung und frühzeitiges Erkennen (Detect) wichtig.

### 9. Typische ICS-Angriffsmethoden
- Angriffe aus dem Internet auf ein online erreichbares ICS, um einen **dauerhaften Fernzugriff** zu etablieren.
- **Fernzugriffe** unter Ausnutzung **gestohlener Zugangsdaten**.
- Angriffe durch Ausnutzen von **Schwachstellen des Webinterfaces**.
- Einschleusen von **Malware über kompromittierte Datenträger** (z. B. USB-Sticks, Smartphones).
- Angriffe auf die **Büroautomation** (z. B. Phishing-Mails, Drive-by-Infektionen), um über Schnittstellen ins ICS vorzudringen.

### 10. Faktoren bei der Anwendung eines Defense-in-Depth-Konzeptes (im ICS)
- **Kosten**, um alte Systeme nach zeitgemässen Bedürfnissen abzusichern.
- Der wachsende Trend, **ICS mit Geschäftsnetzwerken zu verbinden**.
- Die Möglichkeit, **Fernzugriffe** für Anwender zu ermöglichen, sowohl im IKT- als auch im ICS-Umfeld.
- Die Notwendigkeit, der eigenen **Zulieferkette (Supply Chain) vertrauen** zu müssen.
- Zeitgemässe Möglichkeiten, **ICS-spezifische Protokolle zu überwachen und zu schützen**.
- Die Möglichkeit, das **Fachwissen über neue Bedrohungen** gegenüber ICS aktuell zu halten.

*Zusatz: Typische Elemente einer Defense-in-Depth-Strategie sind Risk-Management-Programm, Cybersecurity-Architektur, physische Sicherheit, Netzwerk-Architektur, Perimeter Security, Host Security, Security-Monitoring, Lieferantenmanagement und das Element Mensch.*

---

## NIST Framework

### 11. Was bedeutet NIST?
**NIST** = **National Institute of Standards and Technology** (US-Behörde für Normen und Technologie). Gemeint ist das **NIST Cybersecurity Framework (CSF)**. Der Minimalstandard basiert auf dem *NIST Cybersecurity Framework Core* und ergänzt ihn mit dem NIST Guide to ICS Security (SP 800-82) sowie ISO 2700x, COBIT, ENISA und BSI 100-2.

### 12. Ziel des NIST-Frameworks
Das Framework soll Betreibern kritischer Infrastrukturen und anderen IKT-abhängigen Organisationen ein **Instrument** geben, mit dem sie **selbständig und eigenverantwortlich ihre Resilienz gegenüber IKT-Sicherheitsrisiken erhöhen** können.

Es beruht auf bestehenden Standards, Richtlinien und Best Practices und ist **technologieneutral** und **risikobasiert**. Es besteht aus den fünf Funktionen (Identify, Protect, Detect, Respond, Recover). Vier **Implementation Tiers** beschreiben das erreichte Schutzniveau: Tier 1 partiell, Tier 2 risiko-informiert, Tier 3 reproduzierbar, Tier 4 dynamisch.
