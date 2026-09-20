# Monitoring der Endpunkte mit Wazuh – Dokumentation

**Auftrag:** Monitoring der Endpunkte mit wazuh
**Kompetenzband:** D – HIDS in Betrieb nehmen
**Angestrebte Stufe:** **A (D1A)** – umfasst B und I
**Bearbeitet von:** Rewan Ezzeldin
**Datum:** _______________

---

## Inhaltsverzeichnis

1. [Umgebung und Aufbau](#1-umgebung-und-aufbau)
2. [Installation der zentralen Komponenten](#2-installation-der-zentralen-komponenten)
3. [Installation des Agenten](#3-installation-des-agenten)
4. [Analyse des Dashboards (Stufe B)](#4-analyse-des-dashboards-stufe-b)
5. [Härten des eigenen Systems (Stufe I)](#5-härten-des-eigenen-systems-stufe-i)
6. [Werkzeugwahl begründen (Stufe I)](#6-werkzeugwahl-begründen-stufe-i)
7. [Wazuh auf die Systemsituation konfigurieren (Stufe I)](#7-wazuh-auf-die-systemsituation-konfigurieren-stufe-i)
8. [Grenzen von Wazuh beurteilen (Stufe A)](#8-grenzen-von-wazuh-beurteilen-stufe-a)
9. [Reflexionsfragen (Stufe A)](#9-reflexionsfragen-stufe-a)
10. [KI-Log](#10-ki-log)
11. [Anhang: Troubleshooting und Befehlsübersicht](#11-anhang-troubleshooting-und-befehlsübersicht)

---

## 1. Umgebung und Aufbau

### 1.1 Eingesetzte Systeme

| Rolle | System | Version | IP-Adresse |
|---|---|---|---|
| Host | Windows + VMware Workstation Pro 17 | 17.5.x | – |
| Zentrale Komponenten | VM «Wazuh-Server» (OVA, Amazon Linux 2023) | Wazuh 4.14.7 | `______________` |
| Überwachter Endpunkt | VM «Ubuntu-Endpunkt» | Ubuntu 24.04.2 Desktop | `______________` |
| Agent | wazuh-agent (DEB amd64) | 4.14.7 | – |

> **Entscheid Singlenode:** Für diesen Auftrag wird ein Singlenode-Cluster eingesetzt. Ein Multinode-Cluster dient der Ausfallsicherheit und der Lastverteilung bei vielen hundert Agenten – bei einem einzelnen Endpunkt wäre das reiner Overhead.

> **Entscheid VM statt Docker:** Die OVA bringt Manager, Indexer und Dashboard fertig konfiguriert mit (keine Zertifikatsgenerierung, kein Kernel-Tuning). Ausserdem liegt der überwachte Endpunkt bereits als VM in VMware – so stehen beide Maschinen im selben virtuellen Netz und erreichen sich direkt. Bei Docker Desktop unter Windows läge der Server hinter dem WSL2-NAT, was die Agent-Verbindung aus einer anderen VM unnötig verkompliziert.

> **Entscheid VM statt Arbeitsgerät:** Überwacht wird eine Test-VM und nicht das Geschäftsgerät. Gründe: Active Response greift aktiv in die Firewall ein, Härtungsmassnahmen verändern Systemeinstellungen, und auf einem Firmengerät wäre beides ohne Absprache nicht zulässig. Der Auftrag lässt diese Variante ausdrücklich zu.

### 1.2 Netzwerkaufbau

![Netzwerk-Topologie des Laboraufbaus](Bilder/Monitoring-Wazuh/netzwerk-topologie.svg)

Beide VMs hängen am NAT-Netz **VMnet8**. Damit sind sie im selben Subnetz und können ohne Portweiterleitung miteinander sprechen. Bridged wäre im Schulnetz riskant, weil DHCP oder Client-Isolation die Verbindung verhindern können.

**Verwendete Ports:**

| Port | Protokoll | Zweck |
|---|---|---|
| 1514 | TCP | Agent → Manager: Übermittlung der Events (verschlüsselt) |
| 1515 | TCP | Agent → Manager: Enrollment, Bezug des Agent-Schlüssels |
| 443 | TCP | Browser → Dashboard |
| 55000 | TCP | Wazuh-Server-API (wird vom Dashboard genutzt) |

### 1.3 Architektur der zentralen Komponenten

| Komponente | Aufgabe |
|---|---|
| **wazuh-manager** | Nimmt Agent-Daten entgegen, dekodiert sie, gleicht sie gegen das Regelwerk ab und löst Alarme sowie Active Responses aus |
| **wazuh-indexer** | Speichert und indexiert die Alarme (OpenSearch-basiert) |
| **wazuh-dashboard** | Web-Oberfläche zur Auswertung |
| **wazuh-agent** | Läuft als Dienst auf dem Endpunkt, sammelt Logs, Inventar und Konfigurationsprüfungen |

---

## 2. Installation der zentralen Komponenten

### 2.1 OVA herunterladen und importieren

Download: `https://packages.wazuh.com/4.x/vm/wazuh-4.14.7.ova` (rund 2 GB)

In VMware Workstation: **Datei → Öffnen** → `.ova` auswählen → Namen vergeben → **Import**. Die Meldung zur OVF-Spezifikation mit **Retry** bestätigen.

> Nicht über *New Virtual Machine Wizard* gehen – der erstellt eine leere VM ohne Betriebssystem.

### 2.2 VM-Einstellungen anpassen

| Einstellung | Standard der OVA | Gewählter Wert | Begründung |
|---|---|---|---|
| Arbeitsspeicher | 8 GB | `______` | 8 GB bei 32 GB Host-RAM, sonst 6 GB. Unter 6 GB wird der Indexer zäh |
| Prozessoren | 4 | `______` | – |
| Festplatte | 50 GB | 50 GB | unverändert |
| Netzwerkadapter | Bridged | **NAT (VMnet8)** | siehe 1.2 |

<!-- Screenshot: VM-Einstellungen mit Netzwerkadapter auf NAT -->
![VM-Einstellungen](Bilder/Monitoring-Wazuh/01-vm-einstellungen.png)

### 2.3 VM starten und IP ermitteln

Anmeldung an der VM-Konsole:

```
user: wazuh-user
password: wazuh
```

```bash
ip a
```

**Erwartete Ausgabe** (Auszug):

```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:0c:29:ab:cd:ef brd ff:ff:ff:ff:ff:ff
    inet 192.168.184.130/24 brd 192.168.184.255 scope global dynamic noprefixroute eth0
```

Die Adresse hinter `inet` ist die Server-IP. **Notieren – sie wird mehrfach gebraucht.**

> Der SSH-Login als root ist deaktiviert. `wazuh-user` hat sudo-Rechte; mit `sudo -i` wechselt man zu root.

### 2.4 Dienste prüfen

```bash
sudo systemctl status wazuh-manager wazuh-indexer wazuh-dashboard --no-pager
```

**Erwartete Ausgabe:** Bei allen drei Diensten steht `Active: active (running)`.

### 2.5 Dashboard öffnen

Im Browser des Hosts: `https://<WAZUH_IP>`

```
user: admin
password: admin
```

Die Zertifikatswarnung ist erwartet (selbstsigniertes Zertifikat) und wird bestätigt. Die Initialisierung dauert nach dem ersten Start einige Minuten.

> **Beobachtung für die Doku:** Der Auftrag nennt als Standardzugang `admin` / `SecretPassword`. Das ist der Default der **Docker**-Variante; die OVA verwendet `admin` / `admin`. In einer produktiven Umgebung wären beide Zugänge sofort zu ändern – im Labor wird bewusst darauf verzichtet und dieser Punkt stattdessen hier festgehalten.

<!-- Screenshot: Dashboard-Startseite nach dem ersten Login -->
![Wazuh Dashboard Startseite](Bilder/Monitoring-Wazuh/02-dashboard-start.png)

---

## 3. Installation des Agenten

### 3.1 Vorbereitung auf der Ubuntu-VM

SSH aktivieren (erleichtert die Arbeit vom Host aus erheblich):

```bash
sudo apt update
sudo apt install -y openssh-server
ip a
```

Erreichbarkeit des Servers prüfen:

```bash
ping -c 3 <WAZUH_IP>
nc -zv <WAZUH_IP> 1514
nc -zv <WAZUH_IP> 1515
```

**Erwartete Ausgabe:**

```
3 packets transmitted, 3 received, 0% packet loss
Connection to 192.168.184.130 1514 port [tcp/*] succeeded!
Connection to 192.168.184.130 1515 port [tcp/*] succeeded!
```

Schlägt das fehl, stehen die VMs nicht im selben Netz oder eine Firewall blockiert die Ports.

### 3.2 Agent über das Dashboard hinzufügen

Im Dashboard: **Agents → Deploy new agent**

| Feld | Wert |
|---|---|
| Package | DEB amd64 |
| Server address | `<WAZUH_IP>` |
| Agent name | `ubuntu-endpunkt` |
| Agent group | `default` |

Das Dashboard generiert daraus den passenden Installationsbefehl.

> **Warum der generierte Befehl und nicht eine Anleitung aus dem Netz:** So ist sichergestellt, dass die Agent-Version zur Server-Version passt. Der Agent darf gleich alt oder älter als die zentralen Komponenten sein, aber **nie neuer** – ein neuerer Manager ist rückwärtskompatibel, umgekehrt gilt das nicht.

<!-- Screenshot: Deploy-new-agent-Assistent mit generiertem Befehl -->
![Agent-Assistent](Bilder/Monitoring-Wazuh/03-deploy-new-agent.png)

### 3.3 Agent installieren

```bash
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.7-1_amd64.deb
sudo WAZUH_MANAGER='<WAZUH_IP>' WAZUH_AGENT_NAME='ubuntu-endpunkt' dpkg -i ./wazuh-agent_4.14.7-1_amd64.deb
```

**Erwartete Ausgabe:**

```
Selecting previously unselected package wazuh-agent.
Preparing to unpack .../wazuh-agent_4.14.7-1_amd64.deb ...
Unpacking wazuh-agent (4.14.7-1) ...
Setting up wazuh-agent (4.14.7-1) ...
```

Dienst starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

### 3.4 Verbindung kontrollieren

```bash
sudo systemctl status wazuh-agent --no-pager
sudo tail -n 20 /var/ossec/logs/ossec.log
```

**Erwartete Ausgabe im Log:**

```
INFO: Requesting a key from server: 192.168.184.130
INFO: Valid key received
INFO: Connected to the server (192.168.184.130:1514/tcp).
```

Im Dashboard steht der Agent unter **Agents** nach ein bis zwei Minuten auf **Active**.

<!-- Screenshot: Agentenübersicht mit Status Active -->
![Agent aktiv](Bilder/Monitoring-Wazuh/04-agent-active.png)

### 3.5 Logquelle prüfen – Besonderheit bei Ubuntu 24.04

Ubuntu 24.04 protokolliert standardmässig über **journald**; die Datei `/var/log/auth.log` existiert je nach Installation nicht mehr. Die Standardkonfiguration des Agenten liest aber genau diese Datei. Wird das übersehen, kommen später **keine SSH-Ereignisse** beim Manager an und die eigene Regel feuert nie.

Prüfen:

```bash
ls -l /var/log/auth.log
```

Existiert die Datei nicht, in `/var/ossec/etc/ossec.conf` auf dem **Agenten** ergänzen:

```xml
<localfile>
  <log_format>journald</log_format>
  <location>journald</location>
</localfile>
```

```bash
sudo systemctl restart wazuh-agent
```

---

## 4. Analyse des Dashboards (Stufe B)

Durchzuklicken sind vor allem die Bereiche **ENDPOINT SECURITY** und **THREAT INTELLIGENCE**.

### 4.1 Welche Informationen sammelt Wazuh über das Gerät?

| Modul | Gesammelte Informationen | Konkreter Befund auf meinem System |
|---|---|---|
| **Inventory / Syscollector** | Hardware, Betriebssystem, Netzwerkschnittstellen, offene Ports, installierte Pakete, laufende Prozesse | `______________________` |
| **Configuration Assessment** | Abweichungen von den CIS-Benchmarks | `_____` Checks, davon `_____` failed |
| **Vulnerability Detection** | Installierte Software mit bekannten CVEs, nach Kritikalität sortiert | `_____` Critical / `_____` High |
| **File Integrity Monitoring** | Änderungen an überwachten Dateien und Verzeichnissen | `______________________` |
| **MITRE ATT&CK** | Zuordnung der Alarme zu Angriffstechniken | `______________________` |
| **Threat Hunting** | Durchsuchbare Roh-Events aller Agenten | `______________________` |

<!-- Screenshots: je eine Kachel aus ENDPOINT SECURITY und THREAT INTELLIGENCE -->
![Inventory](Bilder/Monitoring-Wazuh/05-inventory.png)
![Threat Intelligence](Bilder/Monitoring-Wazuh/06-mitre.png)

### 4.2 Eigene Einschätzung

> **Auszufüllen:** Was hat überrascht? Wie detailliert ist das Inventar? Wie viele Daten entstehen bereits bei einem einzigen Agenten – und was würde das bei 500 Endpunkten bedeuten (Speicher, Alarmflut, Datenschutz)?

`_______________________________________________________________`

---

## 5. Härten des eigenen Systems (Stufe I)

### 5.1 Configuration Assessment auswerten

**Dashboard → Endpoint Security → Configuration Assessment → Agent auswählen**

Alternativ auf dem Agenten:

```bash
sudo grep -A5 '"sca"' /var/ossec/logs/alerts/alerts.json | tail -n 40
```

Gesamtergebnis eintragen:

| Kennzahl | Wert vorher | Wert nachher |
|---|---|---|
| Score in % | `______` | `______` |
| Passed | `______` | `______` |
| Failed | `______` | `______` |
| Not applicable | `______` | `______` |

<!-- Screenshot: SCA-Übersicht VOR den Massnahmen -->
![SCA vorher](Bilder/Monitoring-Wazuh/07-sca-vorher.png)

### 5.2 Kritische Prüfung der Empfehlungen

Nicht jede Empfehlung ist sinnvoll umzusetzen. Für jeden bearbeiteten Befund wird dokumentiert, ob er in dieser Situation relevant ist:

| # | CIS-Check | Bewertung | Entscheid | Begründung |
|---|---|---|---|---|
| 1 | z. B. „Ensure cramfs kernel module is not available" | Failed | umgesetzt | Dateisystem wird nicht benötigt, Angriffsfläche sinkt ohne Funktionsverlust |
| 2 | z. B. „Ensure GDM is removed" | Failed | **verworfen** | Es handelt sich um ein Desktop-System; ohne grafische Oberfläche wäre es unbrauchbar. Die Empfehlung stammt aus dem Server-Benchmark |
| 3 | z. B. „Ensure auditd is installed" | Failed | umgesetzt | Liefert zusätzlich verwertbare Events für Wazuh |
| 4 | `______________` | `______` | `______` | `______________` |
| 5 | `______________` | `______` | `______` | `______________` |

> **Kernaussage für die Doku:** Ein Score von 100 % ist kein Ziel. Die CIS-Benchmarks sind für gehärtete Server geschrieben; auf einem Desktop-System sind Teile davon schlicht unpassend. Wichtig ist, dass **jeder** Befund einmal bewertet wurde – umgesetzt oder begründet verworfen. Ein unbewerteter Befund ist das eigentliche Risiko.

**Analog zum Windows-Beispiel im Auftrag:** Dort meldet Wazuh unsichere Registry-Einstellungen zu gar nicht aktivierten Windows-Features – irrelevant, solange das Feature deaktiviert ist. Das Gegenstück unter Ubuntu sind Checks zu Diensten, die gar nicht installiert sind, oder Server-Vorgaben auf einem Desktop.

### 5.3 Beispielhafte Härtungsmassnahmen

> **Vorher Snapshot erstellen:** VMware → VM → *Snapshot → Take Snapshot*. Damit lässt sich jede Änderung zurücknehmen.

Nicht benötigte Kernelmodule deaktivieren:

```bash
echo "install cramfs /bin/false" | sudo tee /etc/modprobe.d/cramfs.conf
echo "blacklist cramfs" | sudo tee -a /etc/modprobe.d/cramfs.conf
```

SSH härten (`/etc/ssh/sshd_config`):

```bash
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?MaxAuthTries.*/MaxAuthTries 4/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl restart ssh
```

**Erwartete Ausgabe:** `sshd -t` gibt bei korrekter Syntax nichts aus.

Kernelparameter setzen:

```bash
echo "net.ipv4.conf.all.accept_redirects = 0" | sudo tee /etc/sysctl.d/60-hardening.conf
sudo sysctl --system
```

Scan erneut auslösen und Ergebnis vergleichen:

```bash
sudo systemctl restart wazuh-agent
```

<!-- Screenshot: SCA-Übersicht NACH den Massnahmen -->
![SCA nachher](Bilder/Monitoring-Wazuh/08-sca-nachher.png)

### 5.4 Vulnerability Detection auswerten

**Dashboard → Endpoint Security → Vulnerability Detection**

| Schweregrad | Anzahl vorher | Anzahl nachher |
|---|---|---|
| Critical | `______` | `______` |
| High | `______` | `______` |
| Medium | `______` | `______` |
| Low | `______` | `______` |

Auffällige Pakete:

| Paket | Version | CVE | Schweregrad | Massnahme |
|---|---|---|---|---|
| `______` | `______` | `______` | `______` | `______` |

Updates einspielen:

```bash
sudo apt update && sudo apt upgrade -y
sudo systemctl restart wazuh-agent
```

> Nach dem Update dauert es einige Minuten, bis der neue Inventarstand indexiert ist und die Liste schrumpft.

<!-- Screenshot: Vulnerability Detection vorher/nachher -->
![Vulnerabilities](Bilder/Monitoring-Wazuh/09-vulnerabilities.png)

---

## 6. Werkzeugwahl begründen (Stufe I)

**Szenario:** Zu überwachen ist der öffentlich erreichbare Webserver eines Unternehmens.

### 6.1 Warum Wazuh?

| Anforderung im Szenario | Antwort von Wazuh |
|---|---|
| Wer meldet sich am Server an, wer scheitert dabei? | Log-Analyse mit fertigem Regelwerk für SSH, Apache/Nginx, sudo |
| Wurden Dateien im Webroot verändert (Defacement, Webshell)? | File Integrity Monitoring |
| Läuft verwundbare Software auf dem Server? | Vulnerability Detection gegen CVE-Feeds |
| Entspricht die Konfiguration den Vorgaben? | Configuration Assessment mit CIS-Benchmarks |
| Lässt sich das Ganze zentral auswerten und aufbewahren? | Indexer und Dashboard, Nachweis für Audits |
| Kann automatisch reagiert werden? | Active Response |

**Begründung in Worten:** Ein öffentlich erreichbarer Webserver wird permanent automatisiert angegriffen. Entscheidend ist nicht ein einzelner dieser Aspekte, sondern deren Kombination auf dem Host selbst: Wazuh deckt Log-Analyse, Integritätsüberwachung, Schwachstellen- und Konfigurationsmanagement in einem Werkzeug ab und hält die Ergebnisse zentral und nachvollziehbar vor. Die Alternativen decken jeweils nur einen Ausschnitt ab.

### 6.2 Abgrenzung zu den anderen Werkzeugen

| Tool | Was es tut | Warum es hier allein nicht reicht |
|---|---|---|
| **Fail2Ban** | Sperrt IPs nach fehlgeschlagenen Anmeldungen | Reagiert nur auf Logmuster, keine Integritätsprüfung, keine Schwachstellen, keine zentrale Auswertung |
| **Suricata** | NIDS/NIPS, analysiert Netzwerkverkehr | Sieht den Verkehr, nicht das Geschehen auf dem Host. Bei TLS-verschlüsseltem Datenverkehr ohne Aufbruch stark eingeschränkt |
| **Velociraptor** | DFIR-Werkzeug für gezieltes Hunting und Forensik | Auf den Einzelfall ausgelegt, nicht auf den Dauerbetrieb mit Alarmierung |
| **Zabbix** | Verfügbarkeits- und Performance-Monitoring | Beantwortet „läuft der Dienst?", nicht „wurde er kompromittiert?" |

### 6.3 Situation, in der ein anderes Tool die bessere Wahl wäre

**Suricata statt Wazuh:** Soll ein Netzsegment mit Druckern, Kameras und IoT-Geräten überwacht werden, scheidet Wazuh aus – auf diesen Geräten lässt sich kein Agent installieren. Suricata hängt stattdessen am Spiegelport des Switches und sieht den Verkehr aller Geräte, ohne dass auf ihnen irgendetwas installiert werden muss.

**Zabbix statt Wazuh:** Geht es um die Zusicherung einer Verfügbarkeit gegenüber dem Kunden (Antwortzeiten, Speicherplatz, Ausfälle inklusive Trendauswertung), ist Zabbix das richtige Werkzeug. Sicherheit und Verfügbarkeit sind unterschiedliche Fragestellungen.

---

## 7. Wazuh auf die Systemsituation konfigurieren (Stufe I)

### 7.1 Passende SCA-Policy zuweisen

Verfügbare Policies auf dem Agenten anzeigen:

```bash
ls -l /var/ossec/ruleset/sca/
```

**Erwartete Ausgabe** (Auszug):

```
cis_ubuntu22-04.yml
cis_ubuntu24-04.yml
sca_unix_audit.yml
```

Aktive Policy prüfen: **Dashboard → Configuration Assessment**, dort steht der Name der ausgeführten Policy.

Stimmt sie nicht mit dem System überein, in `/var/ossec/etc/ossec.conf` auf dem **Agenten** explizit setzen:

```xml
<sca>
  <enabled>yes</enabled>
  <scan_on_start>yes</scan_on_start>
  <interval>12h</interval>
  <policies>
    <policy>/var/ossec/ruleset/sca/cis_ubuntu24-04.yml</policy>
  </policies>
</sca>
```

```bash
sudo systemctl restart wazuh-agent
```

| Feld | Eintrag |
|---|---|
| Vorgefundene Policy | `______________________` |
| Passend zum System? | `______________________` |
| Vorgenommene Änderung | `______________________` |
| Begründung | Eine Policy für die falsche Distribution oder Version prüft Pfade und Dienste, die es hier gar nicht gibt – das erzeugt Fehlalarme und übersieht gleichzeitig echte Abweichungen |

### 7.2 Alarmschwelle festlegen

Wazuh bewertet jede Regel mit einem Level von 0 bis 16. Die Schwelle wird auf dem **Manager** in `/var/ossec/etc/ossec.conf` gesetzt:

```xml
<alerts>
  <log_alert_level>3</log_alert_level>
  <email_alert_level>12</email_alert_level>
</alerts>
```

```bash
sudo systemctl restart wazuh-manager
```

| Parameter | Gewählter Wert | Bedeutung |
|---|---|---|
| `log_alert_level` | `______` | Ab diesem Level wird ein Alarm geschrieben und im Dashboard angezeigt |
| `email_alert_level` | `______` | Ab diesem Level ginge zusätzlich eine E-Mail raus |

**Begründung (anzupassen):** Level 3 als Schwelle für das Dashboard behält auch erfolgreiche Anmeldungen und Systemereignisse im Blick, was im Labor für das Nachvollziehen der Regelkette nützlich ist. Die Benachrichtigungsschwelle liegt deutlich höher, damit nur wirklich handlungsbedürftige Ereignisse jemanden aus der Arbeit reissen.

**Was passiert bei einer zu tiefen Schwelle?** Es entstehen so viele Alarme, dass die wichtigen darin untergehen. Das Team gewöhnt sich an rote Meldungen und schaut irgendwann nicht mehr hin – Alarmmüdigkeit. Zusätzlich wächst der Indexer schnell.

**Was passiert bei einer zu hohen Schwelle?** Frühe Anzeichen eines Angriffs – einzelne fehlgeschlagene Anmeldungen, Konfigurationsänderungen – erzeugen gar keinen Alarm mehr. Gemeldet wird erst, wenn der Schaden bereits eingetreten ist.

### 7.3 Eigene Regel erstellen

#### Schritt 1: Eigener Entwurf

> **Zuerst selbst schreiben.** Die KI-Review-Schleife aus dem Auftrag verlangt einen eigenen ersten Entwurf. Hier eintragen, wie die Regel im ersten Versuch aussah und woran sie noch scheiterte:

```xml
<!-- Eigener erster Entwurf: -->

```

#### Schritt 2: Regel eintragen

Auf dem **Manager** in `/var/ossec/etc/rules/local_rules.xml`:

```xml
<group name="local,syslog,sshd,">

  <rule id="100100" level="10" frequency="5" timeframe="60" ignore="60">
    <if_matched_sid>5760</if_matched_sid>
    <same_source_ip />
    <description>Mehrfach fehlgeschlagene SSH-Anmeldungen von derselben IP ($(srcip)) innerhalb einer Minute</description>
    <group>authentication_failures,</group>
    <mitre>
      <id>T1110</id>
    </mitre>
  </rule>

</group>
```

| Element | Bedeutung |
|---|---|
| `id="100100"` | Eigene Regeln ab 100000 – dieser Bereich ist für lokale Regeln reserviert und wird bei Updates nicht überschrieben |
| `level="10"` | Liegt über der Alarmschwelle, gilt als „mehrfacher Authentifizierungsfehler" |
| `frequency="5"` / `timeframe="60"` | Korrelation: Erst die Häufung in kurzer Zeit ist verdächtig, ein Tippfehler nicht |
| `if_matched_sid="5760"` | Baut auf der mitgelieferten Regel für fehlgeschlagene SSH-Passwörter auf, statt das Logformat selbst zu parsen |
| `same_source_ip` | Zählt pro Quell-IP. Ohne diese Zeile würden Fehlversuche verschiedener Benutzer aus dem ganzen Netz zusammenaddiert |
| `ignore="60"` | Unterdrückt Wiederholungsalarme für 60 Sekunden |

Regelwerk neu laden:

```bash
sudo systemctl restart wazuh-manager
sudo tail -n 20 /var/ossec/logs/ossec.log
```

**Erwartete Ausgabe:** Keine Zeilen mit `ERROR` – ein Syntaxfehler in `local_rules.xml` verhindert den Start des Managers.

#### Schritt 3: Regel trocken testen

```bash
sudo /var/ossec/bin/wazuh-logtest
```

Eingabe:

```
Sep 20 14:22:31 ubuntu-endpunkt sshd[2345]: Failed password for rewan from 192.168.184.130 port 51234 ssh2
```

**Erwartete Ausgabe:**

```
**Phase 2: Completed decoding.
        name: 'sshd'
        dstuser: 'rewan'
        srcip: '192.168.184.130'

**Phase 3: Completed filtering (rules).
        id: '5760'
        level: '5'
        description: 'sshd: authentication failed.'
```

Die eigene Regel erscheint erst, wenn dieselbe Zeile mehrfach eingegeben wird – dann springt die ID auf `100100` und das Level auf `10`.

#### Schritt 4: Regel scharf auslösen

> **Wichtig:** Den Angriff **von der Wazuh-Server-VM aus** starten und nicht von der Verbindung, über die du selbst arbeitest. Sonst sperrt die Active Response im nächsten Abschnitt deine eigene Sitzung aus.

Auf der Wazuh-Server-VM:

```bash
for i in $(seq 1 6); do ssh rewan@<UBUNTU_IP> -o PreferredAuthentications=password -o PubkeyAuthentication=no; done
```

Jeweils ein falsches Passwort eingeben.

Kontrolle auf dem Manager:

```bash
sudo grep 100100 /var/ossec/logs/alerts/alerts.log
```

**Erwartete Ausgabe:**

```
** Alert 1758377134.123456: - local,syslog,sshd,authentication_failures,
2026 Sep 20 14:25:34 (ubuntu-endpunkt) 192.168.184.140->journald
Rule: 100100 (level 10) -> 'Mehrfach fehlgeschlagene SSH-Anmeldungen von derselben IP (192.168.184.130) innerhalb einer Minute'
```

<!-- Screenshot: Alarm mit Rule-ID 100100 im Dashboard -->
![Eigene Regel greift](Bilder/Monitoring-Wazuh/10-regel-100100.png)

> **Stolperstein, der zu dokumentieren ist:** `frequency` zählt in Wazuh die Treffer *zusätzlich* zum ersten Ereignis. In der Praxis löst eine Regel mit `frequency="5"` daher erst beim sechsten Ereignis aus. Deshalb oben sechs Versuche. Diese Abweichung zwischen erwartetem und tatsächlichem Verhalten gehört in die Dokumentation – sie zeigt, dass die Regel tatsächlich getestet und nicht nur abgeschrieben wurde.

### 7.4 Active Response konfigurieren

Auf dem **Manager** in `/var/ossec/etc/ossec.conf` ergänzen (der Block `<command>` für `firewall-drop` ist bereits vorhanden):

```xml
<active-response>
  <disabled>no</disabled>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>100100</rules_id>
  <timeout>180</timeout>
</active-response>
```

| Parameter | Bedeutung |
|---|---|
| `command` | Mitgeliefertes Skript, das die Quell-IP über iptables blockiert |
| `location: local` | Ausführung auf dem Agenten, auf dem das Ereignis auftrat |
| `rules_id` | Reaktion nur auf die eigene Regel 100100 |
| `timeout` | Sperre wird nach 180 Sekunden automatisch aufgehoben |

```bash
sudo systemctl restart wazuh-manager
```

**Test:** Den Angriff aus 7.3 wiederholen. Danach auf der **Ubuntu-VM**:

```bash
sudo iptables -L INPUT -n --line-numbers
sudo tail -n 20 /var/ossec/logs/active-responses.log
```

**Erwartete Ausgabe:**

```
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination
1    DROP       all  --  192.168.184.130      0.0.0.0/0
```

```
2026/09/20 14:25:35 active-response/bin/firewall-drop: Starting
2026/09/20 14:25:35 active-response/bin/firewall-drop: {"version":1,"origin":{...},"command":"add",...}
```

Nach Ablauf des Timeouts erscheint ein zweiter Eintrag mit `"command":"delete"` und die iptables-Regel verschwindet wieder.

Sperre bei Bedarf manuell aufheben:

```bash
sudo iptables -D INPUT -s <IP> -j DROP
```

<!-- Screenshot: iptables-Eintrag und active-responses.log -->
![Active Response greift](Bilder/Monitoring-Wazuh/11-active-response.png)

### 7.5 Wo wird aus dem HIDS ein HIPS?

![Alarmkette vom Event bis zur Active Response](Bilder/Monitoring-Wazuh/alarmkette-hids-hips.svg)

Bis und mit Schritt 5 arbeitet Wazuh als **HIDS**: Es sammelt Ereignisse auf dem Host, erkennt Muster und meldet sie. Ein Alarm verhindert nichts – der Angreifer kann in Ruhe weiterprobieren, solange niemand reagiert.

Mit dem Schritt 6, der Active Response, wird daraus ein **HIPS**: Das System greift selbst ein und blockiert die Quell-IP auf dem Endpunkt. Genau an dieser Stelle verläuft die Grenze zwischen Erkennung und Prävention.

Der Preis dafür ist ein neues Risiko: Jede Fehlauslösung sperrt nun echte Benutzer aus. Bei einer Regel auf fehlgeschlagene Anmeldungen genügt ein Kollege, der sein Passwort dreimal falsch eintippt – oder ein NAT-Gateway, hinter dem ein ganzer Standort hängt und dessen Sperrung alle trifft.

---

## 8. Grenzen von Wazuh beurteilen (Stufe A)

> Mindestens zwei Grenzen müssen für das eigene Setup tatsächlich relevant sein. Nachstehend drei Kandidaten – zwei davon für die Reflexionsfragen auswählen.

### Grenze 1: Hostbasiert statt netzwerkbasiert

Der Agent sieht ausschliesslich, was auf der Ubuntu-VM selbst passiert. Der Verkehr im VMnet8-Segment bleibt ihm verborgen. Ein Portscan gegen die VM erzeugt nur dann ein Ereignis, wenn ein Dienst ihn protokolliert – ein reiner SYN-Scan tut das nicht. Ein Exploit gegen einen Dienst, der sauber abstürzt und neu startet, hinterlässt womöglich nur einen unauffälligen Log-Eintrag.

### Grenze 2: Nur Geräte mit Agent sind überwachte Geräte

In diesem Setup ist genau **ein** Endpunkt überwacht. Der Windows-Host, auf dem beide VMs laufen, ist es nicht – obwohl eine Kompromittierung des Hosts sämtliche VMs mitnimmt. Im Unternehmenskontext gilt dasselbe für BYOD-Geräte, Drucker, IoT-Hardware und Schatten-IT, von der die IT-Abteilung gar nichts weiss.

### Grenze 3: Erkennen ist nicht verhindern

Die Active Response greift erst, nachdem die Regel ausgelöst hat – also nach fünf bis sechs Fehlversuchen plus Verarbeitungszeit. Ein Angreifer mit **gültigen** Zugangsdaten aus einem Phishing-Angriff löst gar nichts aus: Er meldet sich beim ersten Versuch erfolgreich an. Für Wazuh ist das eine normale Anmeldung.

| Für die Reflexion gewählte Grenzen | |
|---|---|
| Grenze A | `______________________` |
| Grenze B | `______________________` |

---

## 9. Reflexionsfragen (Stufe A)

### 9.1 Zwei Grenzen mit konkretem Angriffsszenario

**Grenze A – Nur Geräte mit Agent werden überwacht**

*Szenario (anzupassen):* Der Windows-Host trägt keinen Agenten. Über einen manipulierten Download fängt sich der Benutzer dort einen Infostealer ein. Die Schadsoftware liest die gespeicherten SSH-Schlüssel und Browser-Sessions aus und greift damit auf die Ubuntu-VM zu – mit gültigen Schlüsseln, über eine reguläre Sitzung. Im Dashboard erscheint eine erfolgreiche Anmeldung. Der eigentliche Angriff fand auf einem System statt, von dem Wazuh nichts weiss.

**Grenze B – Hostbasiert statt netzwerkbasiert**

*Szenario (anzupassen):* Ein Angreifer im selben Netzsegment führt ARP-Spoofing durch und leitet den Verkehr zwischen der Ubuntu-VM und dem Wazuh-Server über seine eigene Maschine. Beide Endpunkte funktionieren normal weiter, auf beiden Systemen passiert nichts Protokollierbares. Ein NIDS wie Suricata würde die gefälschten ARP-Antworten sofort sehen; der hostbasierte Agent sieht nichts, weil auf dem Host nichts Auffälliges geschieht.

### 9.2 Zwei Zusatzmassnahmen

**Technische Massnahme: Multi-Faktor-Authentifizierung für SSH**

| Punkt | Antwort |
|---|---|
| Geschlossene Lücke | Grenze A: Gestohlene Zugangsdaten oder Schlüssel allein genügen nicht mehr für eine Anmeldung |
| Erwartete Wirkung | Ein Angreifer mit korrekten Credentials scheitert am zweiten Faktor. Zusätzlich entsteht ein neues, auswertbares Signal: fehlgeschlagene MFA-Prüfungen bei korrektem Passwort sind ein starker Hinweis auf kompromittierte Zugangsdaten – darauf lässt sich wiederum eine Wazuh-Regel bauen |
| Neue Nachteile und Risiken | Einrichtungs- und Betriebsaufwand, Prozess für verlorene Token nötig, Ausschluss bei defektem Zweitgerät, Widerstand bei Benutzern |

**Organisatorische Massnahme: Sensibilisierung mit Phishing-Simulation**

| Punkt | Antwort |
|---|---|
| Geschlossene Lücke | Grenze A beziehungsweise „der Mensch als Angriffsziel": Der Angriff wird verhindert, bevor Zugangsdaten überhaupt abfliessen |
| Erwartete Wirkung | Messbar sinkende Klickraten, und vor allem: gemeldete Vorfälle. Ein Mitarbeiter, der eine verdächtige Mail meldet, liefert eine Frühwarnung, die kein Agent erzeugen kann |
| Neue Nachteile und Risiken | Wiederkehrender Zeitaufwand, Kosten für die Plattform, Vertrauensschaden wenn Simulationen als Falle statt als Übung wahrgenommen werden. Schulung wirkt nie zu 100 % – sie senkt die Wahrscheinlichkeit, beseitigt das Risiko nicht |

### 9.3 Warum lösen zusätzliche Tools das Problem nie allein?

Jedes Werkzeug hat einen definierten Blickwinkel: Wazuh sieht den Host, Suricata das Netz, MFA schützt die Anmeldung, Schulung adressiert den Menschen. Kein einzelnes Werkzeug deckt alle Ebenen ab, und jedes lässt sich umgehen, wenn es allein steht.

**Defense-in-Depth** beantwortet das mit gestaffelten, voneinander unabhängigen Schichten: Fällt eine aus, greift die nächste. Der Angreifer muss alle überwinden, der Verteidiger nur an einer Stelle erfolgreich sein. Genau deshalb ist die Frage nach den Grenzen eines Tools wichtiger als die nach seinem Funktionsumfang – nur wer die Lücke kennt, kann sie mit einer anderen Schicht schliessen. Ein Monitoring, dem man blind vertraut, ist gefährlicher als gar keines: Es erzeugt ein Sicherheitsgefühl, das weitere Massnahmen verhindert.

Dazu kommt: Jede zusätzliche Schicht bringt eigene Kosten, eigene Fehlerquellen und eigene Angriffsfläche mit. Mehr Tools sind nicht automatisch mehr Sicherheit – entscheidend ist, dass die Schichten bewusst gewählt sind, sich ergänzen statt zu überlappen, und dass jemand die Alarme tatsächlich auswertet.

### 9.4 KI-Einsatz bei der eigenen Regel

> **Selbst auszufüllen** – siehe KI-Log im nächsten Abschnitt. Konkret zu beantworten: Welchen Fehlalarm oder blinden Fleck hat die KI aufgezeigt, den du selbst übersehen hattest? Und welchen ihrer Vorschläge hast du nach dem Test verworfen?

`_______________________________________________________________`

---

## 10. KI-Log

| # | Wofür eingesetzt | Vorschlag der KI | Übernommen / Verworfen | Begründung |
|---|---|---|---|---|
| 1 | Aufbau der Regel 100100 | `______________` | `______` | `______________` |
| 2 | Review auf Fehlalarme | z. B. „ohne `same_source_ip` werden Fehlversuche verschiedener Quellen zusammengezählt" | `______` | `______________` |
| 3 | Active Response | z. B. „`location: all` würde die IP auf allen Agenten sperren" | `______` | `______________` |
| 4 | `______________` | `______________` | `______` | `______________` |

> Ein begründet verworfener Vorschlag zählt mehr als ein unbegründet übernommener. Eine von der KI vorgeschlagene Regel gilt erst als eigene, wenn sie getestet wurde und man erklären kann, warum sie so aussieht.

---

## 11. Anhang: Troubleshooting und Befehlsübersicht

### 11.1 Häufige Probleme

| Symptom | Ursache | Lösung |
|---|---|---|
| VM startet nicht: „The guest operating system has disabled the CPU" | AMD-Prozessor mit VMware | `.vmx`-Datei ergänzen (siehe 11.2) |
| Agent bleibt auf *Never connected* | Ports 1514/1515 blockiert oder falsche Manager-IP | `nc -zv <IP> 1514`, `grep -A3 '<client>' /var/ossec/etc/ossec.conf` |
| Agent *Disconnected* nach IP-Wechsel | DHCP hat dem Server eine neue Adresse gegeben | Manager-IP in `ossec.conf` des Agenten korrigieren, Agent neu starten |
| Manager startet nach Regeländerung nicht | Syntaxfehler in `local_rules.xml` | `sudo /var/ossec/bin/wazuh-logtest -t` und `tail /var/ossec/logs/ossec.log` |
| Keine SSH-Events im Dashboard | Ubuntu 24.04 loggt über journald | journald-`localfile` ergänzen (siehe 3.5) |
| Regel löst nicht aus | `frequency` zählt ab dem zweiten Ereignis | Ein Ereignis mehr erzeugen als erwartet |
| Eigene Verbindung tot nach AR-Test | Selbstsperrung durch firewall-drop | Über VMware-Konsole: `sudo iptables -D INPUT -s <IP> -j DROP` |

### 11.2 Workaround für AMD-CPUs

In die `.vmx`-Datei der importierten VM anhängen:

```
cpuid.0.eax = "0000:0000:0000:0000:0000:0000:0000:1011"
cpuid.0.ebx = "0111:0101:0110:1110:0110:0101:0100:0111"
cpuid.0.ecx = "0110:1100:0110:0101:0111:0100:0110:1110"
cpuid.0.edx = "0100:1001:0110:0101:0110:1110:0110:1001"
cpuid.1.eax = "0000:0000:0000:0001:0000:0110:0111:0001"
cpuid.1.ebx = "0000:0010:0000:0001:0000:1000:0000:0000"
cpuid.1.ecx = "1000:0010:1001:1000:0010:0010:0000:0011"
cpuid.1.edx = "0000:0111:1000:1011:1111:1011:1111:1111"
featureCompat.enable = "FALSE"
```

### 11.3 Wichtige Pfade

| Pfad | Inhalt |
|---|---|
| `/var/ossec/etc/ossec.conf` | Hauptkonfiguration (Manager und Agent) |
| `/var/ossec/etc/rules/local_rules.xml` | Eigene Regeln (Manager) |
| `/var/ossec/etc/decoders/local_decoder.xml` | Eigene Decoder (Manager) |
| `/var/ossec/ruleset/sca/` | Mitgelieferte SCA-Policies |
| `/var/ossec/logs/ossec.log` | Betriebslog von Agent und Manager |
| `/var/ossec/logs/alerts/alerts.log` | Ausgelöste Alarme (Manager) |
| `/var/ossec/logs/active-responses.log` | Protokoll der Active Responses (Agent) |

### 11.4 Befehlsübersicht

```bash
# Status
sudo systemctl status wazuh-manager --no-pager      # auf dem Server
sudo systemctl status wazuh-agent --no-pager        # auf dem Endpunkt
sudo /var/ossec/bin/wazuh-control status

# Agenten auflisten (auf dem Server)
sudo /var/ossec/bin/agent_control -l

# Regeln testen
sudo /var/ossec/bin/wazuh-logtest

# Konfiguration auf Syntaxfehler prüfen
sudo /var/ossec/bin/wazuh-logtest -t

# Logs verfolgen
sudo tail -f /var/ossec/logs/ossec.log
sudo tail -f /var/ossec/logs/alerts/alerts.log
```

---

## Abgabe-Checkliste

- [ ] Gewählte Stufe im Dokument festgehalten (Kapitel 1)
- [ ] Agent im Dashboard auf *Active*, Screenshot vorhanden
- [ ] Erkenntnisse aus dem Dashboard dokumentiert (Kapitel 4)
- [ ] SCA-Befunde bewertet, Härtungsmassnahmen mit Vorher/Nachher belegt (Kapitel 5)
- [ ] Werkzeugwahl begründet, Alternative genannt (Kapitel 6)
- [ ] SCA-Policy geprüft, Alarmschwelle begründet gesetzt (Kapitel 7.1, 7.2)
- [ ] Eigene Regel erstellt, getestet, Screenshot des Alarms (Kapitel 7.3)
- [ ] Active Response konfiguriert und getestet, HIDS/HIPS-Grenze erklärt (Kapitel 7.4, 7.5)
- [ ] Mindestens zwei Grenzen des Setups beurteilt (Kapitel 8)
- [ ] Reflexionsfragen 1–4 beantwortet (Kapitel 9)
- [ ] KI-Log ausgefüllt (Kapitel 10)
