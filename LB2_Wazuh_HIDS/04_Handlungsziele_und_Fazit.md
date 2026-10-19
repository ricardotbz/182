# 4. Abdeckung der Handlungsziele und Fazit

## 4.1 Abdeckung der Handlungsziele M182

| Handlungsziel | Umsetzung im Projekt | Nachweis / Kapitel |
|---|---|---|
| **1. Systeme auf Sicherheitslücken untersuchen** | Vulnerability Detection (CVE-Abgleich) und SCA (CIS-Benchmark) auf `ubuntu-target` | [03_Auswertung](03_Auswertung_Wirksamkeit.md#33-schwachstellen--und-konfigurationsanalyse) |
| **2. Sicherheitsvorkehrungen entwickeln** | Aus Scan-Ergebnissen abgeleitete Massnahmen (SSH-Key-Login, Härtung) | Abschnitt 4.2 |
| **3. Massnahmen implementieren und dokumentieren** | Umsetzung auf den Agents (FIM, Firewall-Logging, Active Response), vollständige MD-Doku | [VM2](VM2_Ubuntu-Ziel/03_Konfiguration_Ueberwachung.md), [VM1 AR](VM1_Wazuh-Server/03_Active_Response.md) |
| **4. HIDS installieren und konfigurieren** | Wazuh-Server + 2 Agents installiert und konfiguriert | [VM1 Installation](VM1_Wazuh-Server/01_Installation_Wazuh-Server.md) |
| **5. Wirksamkeit prüfen** | 3 Angriffe simuliert, Alerts und Logs ausgewertet, Grenzen beschrieben | [03_Auswertung](03_Auswertung_Wirksamkeit.md) |
| **6. Systemsicherheit überwachen** | Dashboard, Alerts, Active Response, laufende Überwachung | [VM1](VM1_Wazuh-Server/README.md), Dashboard |

## 4.2 Abgeleitete Sicherheitsmassnahmen (Ziel 2)

Aus den Scan- und Angriffsergebnissen ergeben sich folgende Massnahmen für `ubuntu-target`:

| Problem | Massnahme | Umgesetzt in |
|---|---|---|
| SSH-Passwort-Login erlaubt → Brute-Force möglich | Nur SSH-Key-Login (`PasswordAuthentication no`) | nach dem Test |
| Schwache Passwörter | Passwort-Policy, lange Passwörter | Dokumentiert |
| Angriffe nicht automatisch gestoppt | Active Response `firewall-drop` | [VM1 AR](VM1_Wazuh-Server/03_Active_Response.md) |
| Manipulation kritischer Dateien unbemerkt | FIM (realtime + whodata) | [VM2](VM2_Ubuntu-Ziel/03_Konfiguration_Ueberwachung.md) |
| Portscans unsichtbar für HIDS | iptables-Logging + eigene Regel | VM2 / VM1 |
| Offene / veraltete Pakete | Updates, unnötige Dienste deaktivieren | Dokumentiert |

## 4.3 Zusammenfassung des Projekts

- Es wurde ein vollständiges HIDS mit **Wazuh** aufgebaut: ein Server und **zwei Agents**.
- Drei typische Angriffe (**SSH-Brute-Force, Portscan, Dateimanipulation**) wurden simuliert und von Wazuh erkannt.
- Eigene **Regeln** (IDs 100100–100122) und **Active Response** (automatische IP-Sperre) wurden erstellt und getestet.
- Mit **Vulnerability Detection** und **SCA** wurden Schwachstellen und Konfigurationsmängel gefunden.
- Die **Grenzen** eines HIDS wurden aufgezeigt (langsame Angriffe, Abhängigkeit von Logs, NIDS als Ergänzung).

## 4.4 Fazit

[AUSFÜLLEN – eigene Worte, z. B.:]

- Was hat gut funktioniert?
- Was war schwierig (Installation, Regeln, Decoder, Active Response)?
- Was haben wir über HIDS und Angriffserkennung gelernt?
- Wie würden wir ein solches System in einem echten Betrieb einsetzen?

## 4.5 Arbeitsaufteilung im Team

| Aufgabe | Rewan | Ricardo | Samuele |
|---|---|---|---|
| Theorie | [AUSFÜLLEN] | | |
| Wazuh-Server (VM1) | | | |
| Ubuntu-Agent (VM2) | | | |
| Kali / Angriffe (VM3) | | | |
| Auswertung & Doku | | | |
