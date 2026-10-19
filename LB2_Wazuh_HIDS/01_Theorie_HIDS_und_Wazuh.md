# 1. Theorie: HIDS und Wazuh

## 1.1 Was ist ein IDS?

Ein **Intrusion Detection System (IDS)** erkennt Angriffe und verdächtige Aktivitäten auf Systemen oder im Netzwerk.
Es meldet diese als **Alarm (Alert)**. Ein IDS greift grundsätzlich nicht selbst ein. Wenn es zusätzlich automatisch
reagiert (z. B. eine IP sperrt), spricht man von einem **Intrusion Prevention System (IPS)**.

Ein IDS arbeitet mit zwei Methoden:

| Methode | Funktionsweise | Vorteil | Nachteil |
|---|---|---|---|
| **Signaturbasiert** | Vergleicht Ereignisse mit bekannten Mustern (Regeln) | Wenig Fehlalarme bei bekannten Angriffen | Erkennt neue, unbekannte Angriffe schlecht |
| **Anomaliebasiert** | Erkennt Abweichungen vom Normalverhalten | Kann unbekannte Angriffe erkennen | Mehr Fehlalarme (False Positives) |

## 1.2 HIDS vs. NIDS

| Kriterium | HIDS (Host-based IDS) | NIDS (Network-based IDS) |
|---|---|---|
| Standort | Läuft **auf dem einzelnen System** (Agent) | Läuft an einem **Netzwerkpunkt** (z. B. Switch-Mirror-Port) |
| Datenquelle | Logdateien, Dateisystem, Prozesse, Registry, Konfiguration | Netzwerkpakete |
| Sieht verschlüsselten Verkehr? | Ja, nach der Entschlüsselung auf dem Host (z. B. SSH-Login im auth.log) | Nein, nur Metadaten |
| Erkennt Dateiänderungen? | Ja (File Integrity Monitoring) | Nein |
| Erkennt Netzwerkscans? | Nur, wenn der Host sie loggt (z. B. Firewall-Logs) | Ja, sehr gut |
| Aufwand | Agent auf jedem Host nötig | Ein Sensor für viele Hosts |
| Beispiele | **Wazuh**, OSSEC, Tripwire, AIDE | Snort, Suricata, Zeek |

**Fazit:** HIDS und NIDS ergänzen sich. Ein HIDS sieht genau, *was auf dem Host passiert*. Ein NIDS sieht, *was im
Netzwerk passiert*.

## 1.3 Was ist Wazuh?

Wazuh ist eine kostenlose **Open-Source-Plattform für Security Monitoring**. Sie ist aus OSSEC entstanden und
kombiniert HIDS, SIEM-Funktionen (Log-Sammlung und -Auswertung) und XDR (automatische Reaktion).

### Funktionen von Wazuh

| Funktion | Beschreibung |
|---|---|
| **Log-Analyse** | Sammelt und analysiert Logs (z. B. `/var/log/auth.log`, Syslog, Windows Event Log) |
| **File Integrity Monitoring (FIM)** | Erkennt Änderungen, Neuanlage und Löschung wichtiger Dateien (Modul `syscheck`) |
| **Vulnerability Detection** | Vergleicht installierte Pakete mit CVE-Datenbanken |
| **Security Configuration Assessment (SCA)** | Prüft die Konfiguration gegen CIS-Benchmarks |
| **Rootkit-Erkennung** | Sucht nach versteckten Prozessen und Dateien (Modul `rootcheck`) |
| **Active Response** | Führt automatisch Gegenmassnahmen aus (z. B. IP per Firewall sperren) |
| **MITRE ATT&CK-Zuordnung** | Ordnet Alerts bekannten Angriffstechniken zu |

## 1.4 Aufbau (Architektur) von Wazuh

```text
 ┌──────────────────────┐        ┌──────────────────────┐
 │  Ubuntu-VM (Agent)   │        │   Kali-VM (Agent)    │
 │  wazuh-agent         │        │   wazuh-agent        │
 └──────────┬───────────┘        └───────────┬──────────┘
            │  verschlüsselt, Port 1514/TCP   │
            │  Registrierung,  Port 1515/TCP  │
            ▼                                 ▼
 ┌─────────────────────────────────────────────────────┐
 │                Wazuh-Server (VM1)                   │
 │  ┌──────────────────┐   Filebeat   ┌──────────────┐ │
 │  │  Wazuh Manager   │ ───────────▶ │ Wazuh Indexer│ │
 │  │ Decoder → Regeln │   Port 9200  │ (OpenSearch) │ │
 │  │ → Alerts         │              └──────┬───────┘ │
 │  └──────────────────┘                     │         │
 │                                  ┌────────▼───────┐ │
 │                                  │ Wazuh Dashboard│ │
 │                                  │ Port 443/HTTPS │ │
 │                                  └────────────────┘ │
 └─────────────────────────────────────────────────────┘
```

| Komponente | Aufgabe |
|---|---|
| **Wazuh Agent** | Läuft auf jedem überwachten System. Sammelt Logs, prüft Dateien, führt Scans aus und sendet alles verschlüsselt an den Manager. Führt Active-Response-Befehle aus. |
| **Wazuh Manager (Server)** | Empfängt die Daten der Agents, dekodiert sie, prüft sie gegen Regeln und erzeugt Alerts. Steuert Active Response. |
| **Wazuh Indexer** | Speichert und indexiert die Alerts (basiert auf OpenSearch). Ermöglicht schnelle Suche. |
| **Wazuh Dashboard** | Weboberfläche (basiert auf OpenSearch Dashboards) zur Anzeige von Alerts, Agents, Statistiken und Konfiguration. |

## 1.5 Funktionsweise: Vom Log zum Alert

```text
Logzeile  →  Pre-Decoding  →  Decoder  →  Regeln  →  Alert (Level 0–15)  →  ggf. Active Response
```

1. **Log-Erfassung:** Der Agent liest z. B. diese Zeile aus `/var/log/auth.log`:
   ```text
   Oct 19 14:12:01 ubuntu-target sshd[1234]: Failed password for testuser from 192.168.56.30 port 51234 ssh2
   ```
2. **Pre-Decoding:** Wazuh erkennt Zeitstempel, Hostname und Programmname (`sshd`).
3. **Decoder:** Ein Decoder extrahiert Felder, z. B. `srcip = 192.168.56.30`, `dstuser = testuser`.
4. **Regeln:** Wazuh prüft die Felder gegen Regeln. Regel **5760** passt: *"sshd: authentication failed"*.
   Kommen viele solche Ereignisse von derselben IP, greift eine **Frequenzregel** (z. B. **5763**, *Brute Force*).
5. **Alert:** Jede Regel hat ein **Level von 0 bis 15**. Ab Level 3 (Standard) wird ein Alert gespeichert.
6. **Active Response:** Ist für die Regel eine Reaktion konfiguriert, sendet der Manager dem Agent einen Befehl
   (z. B. `firewall-drop` → IP wird per iptables gesperrt).

### Regel-Level (Auswahl)

| Level | Bedeutung |
|---|---|
| 0 | Ignoriert, kein Alert |
| 3 | Erfolgreiche / normale Ereignisse |
| 5 | Benutzerfehler (z. B. falsches Passwort) |
| 7 | "Bad word"-Treffer, wichtige Änderungen (z. B. FIM) |
| 10 | Mehrfache Fehler (z. B. Brute Force) |
| 12 | Wichtiges Ereignis mit hoher Priorität |
| 15 | Schwerer Angriff, sofort reagieren |

### Aufbau einer Regel (Beispiel)

```xml
<rule id="100100" level="10" frequency="5" timeframe="60">
  <if_matched_group>authentication_failed</if_matched_group>
  <same_source_ip />
  <description>M182: SSH-Brute-Force von $(srcip)</description>
  <mitre><id>T1110</id></mitre>
  <group>m182,authentication_failures,</group>
</rule>
```

- `id` – eindeutige Nummer (eigene Regeln: **100000–120000**)
- `level` – Schweregrad
- `frequency` / `timeframe` – wie oft in welcher Zeit (Sekunden)
- `if_sid` / `if_matched_sid` / `if_matched_group` – baut auf anderen Regeln auf
- `same_source_ip` – Ereignisse müssen von derselben Quell-IP kommen

## 1.6 Begriffe

| Begriff | Erklärung |
|---|---|
| **Alert** | Meldung, dass eine Regel ausgelöst wurde |
| **False Positive** | Fehlalarm: Alert, obwohl kein Angriff vorliegt |
| **False Negative** | Angriff, der **nicht** erkannt wurde |
| **Decoder** | Liest Felder aus einer Logzeile aus |
| **FIM** | File Integrity Monitoring – Prüfsummenvergleich von Dateien |
| **SCA** | Security Configuration Assessment – Prüfung gegen Härtungsrichtlinien (CIS) |
| **CVE** | Common Vulnerabilities and Exposures – öffentliche Liste bekannter Schwachstellen |
| **Active Response** | Automatische Reaktion auf einen Alert |
| **MITRE ATT&CK** | Wissensdatenbank zu Angriffstechniken (z. B. T1110 = Brute Force, T1046 = Network Service Discovery) |
