# VM1 – Wazuh-Server (vorinstallierte OVA)

In dieser Umgebung wird der Wazuh-Server **nicht** per Installationsskript aufgebaut, sondern als
**vorinstallierte virtuelle Maschine (OVA)** importiert. Die OVA bringt Manager, Indexer und Dashboard
fertig konfiguriert mit (Singlenode, alles auf einer VM) und läuft auf **Amazon Linux 2023**.

> **Warum OVA statt `wazuh-install.sh`?** Die OVA spart die Zertifikatsgenerierung und das Kernel-Tuning und
> funktioniert direkt im selben VMware-NAT-Netz wie die anderen VMs. Der Installationsweg über das Skript
> (`curl -sO https://packages.wazuh.com/4.x/wazuh-install.sh && sudo bash ./wazuh-install.sh -a`) auf einem
> frischen Ubuntu Server wäre die Alternative – wird hier aber nicht verwendet.

## 1. OVA importieren

- Datei: `wazuh-4.14.7.ova` (von <https://packages.wazuh.com/4.x/vm/>)
- In VMware Workstation über **Datei → Öffnen** importieren.
- Die Warnung „erfüllt die OVF-Spezifikation nicht“ mit **Retry** übergehen (nur strikte Schemaprüfung).
- Netzwerkadapter auf **NAT (VMnet8)** stellen.

| Einstellung | Wert |
|---|---|
| Arbeitsspeicher | 8192 MB |
| Prozessoren | 4 |
| Festplatte | 50 GB |
| Netzwerk | NAT (VMnet8) |

## 2. Erster Start und Login

Anmeldung an der Konsole (oder per SSH):

| Zugang | Benutzer | Passwort |
|---|---|---|
| Konsole / SSH | `wazuh-user` | `wazuh` |
| Dashboard (Web) | `admin` | `admin` |

`wazuh-user` hat sudo-Rechte, der SSH-Login als root ist deaktiviert. IP-Adresse prüfen:

```bash
ip -4 a show eth0
```

In dieser Umgebung hat der Server die Adresse `192.168.179.129` (DHCP aus VMnet8).

> **Zeit prüfen:** Die Uhrzeit aller VMs muss übereinstimmen, sonst passen die Zeitstempel der Alerts nicht
> (`timedatectl`). Der Server läuft auf **UTC**, die Ubuntu-VM auf Europe/Zurich – das ist in Ordnung, solange
> die absolute Zeit (UTC) stimmt. Wazuh rechnet intern in UTC.

## 3. Dienste prüfen

```bash
sudo systemctl status wazuh-indexer wazuh-manager wazuh-dashboard filebeat --no-pager | grep -E "●|Active"
```

Alle vier müssen `active (running)` sein. Die einzelnen Manager-Prozesse:

```bash
sudo /var/ossec/bin/wazuh-control status
```

Offene Ports:

```bash
sudo ss -tlnp | grep -E '1514|1515|55000|9200|443'
```

## 4. Wichtiger Hinweis: langsamer Start des Indexers

Auf einer ressourcenschwachen VM (oder wenn mehrere VMs gleichzeitig laufen) braucht der **Indexer** beim Start
sehr lange – in dieser Umgebung über 5 Minuten. Das Standard-Zeitlimit von systemd (`TimeoutStartSec`) bricht
den Start dann ab, und `wazuh-indexer` meldet `failed (Result: timeout)`. Manager und Dashboard hängen vom
Indexer ab und starten dann gar nicht erst.

**Lösung:** Das Start-Zeitlimit des Indexers aufheben (einmalig):

```bash
sudo systemctl edit wazuh-indexer
```

Im Editor eintragen:

```ini
[Service]
TimeoutStartSec=infinity
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart wazuh-indexer
```

Danach ist der Indexer nach einigen Minuten `active`. Kontrolle:

```bash
sudo systemctl is-active wazuh-indexer
curl -sk -u admin:admin https://127.0.0.1:9200/_cluster/health
```

> Nach **jedem** Neustart der VM zeigt das Dashboard zunächst einige Minuten lang
> „Wazuh dashboard server is not ready yet“, bis der Indexer vollständig oben ist. Das ist normal.

## 5. Erster Login im Dashboard

1. Im Browser des Host-PCs öffnen: `https://192.168.179.129`
   (Das vorangestellte `https://` ist wichtig – ohne Protokoll versucht der Browser Port 80, auf dem nichts läuft.)
2. Zertifikatswarnung akzeptieren (selbstsigniertes Zertifikat der OVA).
3. Login mit `admin` / `admin`.

![Screenshot Dashboard Login](../screenshots/vm1_dashboard_login.png)

> **Sicherheitshinweis:** `admin/admin` ist der öffentlich dokumentierte OVA-Standard. In einer produktiven
> Umgebung wären diese Zugänge sofort zu ändern. Für die Laborumgebung bleiben sie bewusst stehen.

## 6. Agents anbinden

Die Agents werden auf VM2 und VM3 installiert:

- [VM2 – Agent installieren](../VM2_Ubuntu-Ziel/02_Installation_Wazuh-Agent.md)
- [VM3 – Agent installieren](../VM3_Kali-Angreifer/02_Installation_Wazuh-Agent.md)

Danach auf dem Server kontrollieren:

```bash
sudo /var/ossec/bin/agent_control -l
```

Erwartete Ausgabe:

```text
Wazuh agent_control. List of available agents:
   ID: 000, Name: wazuh-server (server), IP: 127.0.0.1, Active/Local
   ID: 001, Name: ubuntu-endpunkt, IP: any, Active
   ID: 002, Name: kali-attacker, IP: any, Active
```

Im Dashboard: **Agents management → Summary** → beide Agents müssen **active** sein.

![Screenshot Agents aktiv](../screenshots/vm1_agents_active.png)

## 7. Vulnerability Detection und SCA prüfen

Beide Module ([Vulnerability Detection](https://documentation.wazuh.com/current/user-manual/capabilities/vulnerability-detection/index.html),
[SCA](https://documentation.wazuh.com/current/user-manual/capabilities/sec-config-assessment/index.html)) sind in der OVA standardmässig aktiv. Prüfen in `/var/ossec/etc/ossec.conf`:

```xml
<vulnerability-detection>
  <enabled>yes</enabled>
  <index-status>yes</index-status>
  <feed-update-interval>60m</feed-update-interval>
</vulnerability-detection>
```

Ergebnisse im Dashboard:

- **Vulnerability Detection** → Agent `ubuntu-endpunkt` auswählen → Liste der CVEs
- **Configuration Assessment** → Agent auswählen → CIS-Benchmark für Ubuntu (bestandene / fehlgeschlagene Checks)

Diese Ergebnisse werden in [03_Auswertung_Wirksamkeit.md](../03_Auswertung_Wirksamkeit.md) ausgewertet
(Handlungsziel 1 und 2).

## 8. Fehlersuche

| Problem | Lösung |
|---|---|
| Dashboard „not ready yet“ | Indexer noch im Start – einige Minuten warten, `systemctl is-active wazuh-indexer` |
| `wazuh-indexer failed (timeout)` | `TimeoutStartSec=infinity` setzen (siehe Abschnitt 4), dann neu starten |
| Dashboard gar nicht erreichbar | `sudo ss -tlnp \| grep 443` – läuft der node-Prozess? ggf. `sudo systemctl restart wazuh-dashboard` |
| Agent wird nicht angezeigt | Port 1514/1515 offen? `sudo tail -f /var/ossec/logs/ossec.log` |
| „Wazuh API not reachable“ | `sudo systemctl restart wazuh-manager`, Port 55000 prüfen |
