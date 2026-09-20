# Risikoanalyse in einem fiktiven Unternehmensumfeld

> **Kompetenz:** A1I · **Bloom:** Analysieren · **Rolle:** IT-Sicherheitsbeauftragte/r in einem mittelständischen Unternehmen (ca. 50 Mitarbeitende)

---

## Aufgabe 1: Risikoanalyse für drei Systeme

Die Bewertung folgt dem Risikographen (Eintrittswahrscheinlichkeit × Schweregrad). Die Werte sind begründete Annahmen, da das Szenario keine konkreten Daten liefert.

| # | System | Bedrohung | Schwachstelle | Eintrittswahrscheinlichkeit | Schweregrad bei Eintritt | Betroffene Schutzziele (C / I / A) | Risikobewertung |
|---|---|---|---|---|---|---|---|
| 1 | Webserver | Angriff auf den Shop (z. B. SQL-Injection, Ausnutzen bekannter Lücken) mit Übernahme des Servers | Veraltete Shop-Software oder Plugins, unzureichende Eingabevalidierung, unregelmässiges Patchen | wahrscheinlich | kritisch | C, I, A | **inakzeptabel** |
| 2 | Webserver | DDoS-Angriff, der den Shop lahmlegt | Kein Schutz vor Lastspitzen (kein WAF/CDN, keine Rate-Limits), Einzelserver ohne Redundanz | gelegentlich | geringfügig bis kritisch (Umsatzausfall, Imageschaden) | A | **ALARP** |
| 3 | Datenbankserver | Unbefugter Zugriff und Datendiebstahl (über den kompromittierten Webserver oder durch Insider) | Flaches Netz ohne Segmentierung, zu weitreichende Zugriffsrechte, unverschlüsselte Kundendaten | gelegentlich | katastrophal (DSG/DSGVO-Verstoss, Bussgelder, Vertrauensverlust) | C, I | **inakzeptabel** |
| 4 | Datenbankserver | Datenverlust oder -verschlüsselung (Ransomware, Hardwaredefekt) | Backups nicht offline oder nicht regelmässig getestet, kein Notfallkonzept | entfernt vorstellbar | katastrophal | A, I | **ALARP** |
| 5 | Notebook Support | Diebstahl oder Verlust des Geräts | Festplatte nicht verschlüsselt, schwacher Anmeldeschutz | gelegentlich | kritisch (Kundendaten, VPN-Zugangsdaten) | C | **ALARP** |
| 6 | Notebook Support | Malware über Phishing-Mail oder unsichere WLANs, danach Angriff auf das interne Netz via VPN | Fehlendes Sicherheitsbewusstsein, kein Endpoint-Schutz, VPN ohne MFA, unzureichend eingeschränkte Zugriffsrechte | wahrscheinlich | kritisch | C, I, A | **inakzeptabel** |

---

## Aufgabe 2: Massnahmendefinition

Gewählt wurden Risiko 1 (Webserver) und Risiko 3 (Datenbankserver), beide "inakzeptabel".

| System | Identifiziertes Risiko | Schutzmassnahme | Erwartete Wirkung |
|---|---|---|---|
| Webserver | Ausnutzen von Schwachstellen (Risiko 1) | **Technisch:** Patch-Management mit festen Fristen für kritische Updates, Web Application Firewall (WAF), regelmässige Schwachstellenscans und Pentests, Härtung des Servers. Die Webserver-Zone kommt in eine DMZ, und der Server läuft mit minimalen Rechten. **Organisatorisch:** Verantwortlichkeit für Updates festlegen, Change-Prozess, Logging und Monitoring. | Die **Eintrittswahrscheinlichkeit** sinkt von "wahrscheinlich" auf "entfernt vorstellbar". WAF und DMZ begrenzen zusätzlich den **Schweregrad**, weil der Angreifer nicht direkt ins interne Netz gelangt. Das Risiko sinkt auf ALARP bzw. akzeptabel. |
| Datenbankserver | Unbefugter Zugriff und Datendiebstahl (Risiko 3) | **Technisch:** Netzwerksegmentierung (nur der Webserver darf auf einem Port zugreifen), Verschlüsselung der Daten (at rest und in transit), Least-Privilege-Konten, MFA für Administratoren, Audit-Logging mit Alarmierung. **Organisatorisch:** Berechtigungskonzept mit regelmässiger Rezertifizierung, Datenminimierung (nicht benötigte Daten löschen). | Die **Eintrittswahrscheinlichkeit** sinkt auf "unwahrscheinlich". Bei einem Einbruch sind die verschlüsselten Daten kaum verwertbar, was den **Schweregrad** von "katastrophal" auf "kritisch" senkt. Das Risiko sinkt auf ALARP. |

---

## Aufgabe 3: Diskussion und Bewertung

### 1. Bei welchem System sehen Sie den grössten Handlungsbedarf?

Am grössten ist der Handlungsbedarf beim **Webserver**, mit dem Notebook als engem Zweitplatzierten.

- Der Webserver ist **öffentlich erreichbar** und damit permanent Angriffen ausgesetzt. Die Wahrscheinlichkeit ist deshalb am höchsten.
- Er ist der **Einstiegspunkt** zum Datenbankserver. Ist er kompromittiert, wird aus einem kritischen Risiko rasch ein katastrophales.
- Die Datenbank hat zwar den höchsten Schaden, ist aber nur indirekt erreichbar und mit vertretbarem Aufwand gut schützbar. Wer den Webserver zuerst absichert, senkt auch das Datenbankrisiko.

### 2. Wie verändert sich die Risikobewertung, wenn eine Schwachstelle vollständig behoben wird, die Bedrohung jedoch weiterhin besteht?

Risiko ergibt sich aus Eintrittswahrscheinlichkeit und Schweregrad. Fällt eine ausnutzbare Schwachstelle weg, kann die Bedrohung diesen Weg nicht mehr nutzen, und die **Eintrittswahrscheinlichkeit sinkt deutlich**. Der Schweregrad bleibt zunächst gleich, weil der potenzielle Schaden derselbe ist. Das Gesamtrisiko wird also kleiner, etwa von "inakzeptabel" auf "ALARP" oder "akzeptabel".

Es wird aber **nie null**:

- Die Bedrohung existiert weiter und sucht andere Wege (weitere oder unbekannte Schwachstellen, Zero-Days, Social Engineering).
- Es bleibt ein **Restrisiko**, das man beobachten und regelmässig neu bewerten muss.

### 3. Warum sind auch organisatorische Massnahmen wichtig?

- **Der Mensch ist oft das schwächste Glied.** Phishing, schwache Passwörter oder Fehlkonfigurationen umgehen jede Technik. Schulungen und Awareness senken die Wahrscheinlichkeit solcher Vorfälle.
- **Technik braucht Prozesse.** Ein Patch nützt nichts, wenn niemand für das Einspielen zuständig ist. Auch Backups helfen nur, wenn ihre Wiederherstellung regelmässig getestet wird.
- **Rollen und Rechte sind Organisationsfragen.** Berechtigungskonzepte, Vier-Augen-Prinzip und Offboarding-Prozesse verhindern Insider-Risiken, die keine Firewall abfängt.
- **Reaktionsfähigkeit.** Ein Incident-Response-Plan und Meldewege begrenzen den Schaden, wenn trotzdem etwas passiert (Schweregrad sinkt).
- **Mehrschichtiger Schutz (Defense in Depth).** Technische und organisatorische Massnahmen ergänzen sich, und zusammen kompensieren sie das Versagen einzelner Schichten.
- **Compliance.** Datenschutzgesetze (DSG/DSGVO) verlangen ausdrücklich technische *und* organisatorische Massnahmen.
