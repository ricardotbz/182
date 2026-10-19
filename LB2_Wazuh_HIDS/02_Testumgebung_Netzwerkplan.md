# 2. Testumgebung und Netzwerkplan

## 2.1 Übersicht der VMs

| VM | Rolle | Betriebssystem | IP-Adresse | vCPU | RAM | Disk |
|---|---|---|---|---|---|---|
| **VM1** | Wazuh-Server (Manager, Indexer, Dashboard) | Ubuntu Server 24.04 LTS | `192.168.56.10` | 2–4 | 8 GB (min. 4 GB) | 50 GB |
| **VM2** | Überwachtes Zielsystem (Agent) | Ubuntu Server 24.04 LTS | `192.168.56.20` | 1–2 | 2 GB | 20 GB |
| **VM3** | Angreifer (Agent) | Kali Linux (aktuell) | `192.168.56.30` | 2 | 2–4 GB | 30 GB |

> Die IP-Adressen sind Beispiele. Wer andere Adressen verwendet, muss sie in **allen** Befehlen und Konfigurationen
> ersetzen.

**Warum zwei Agents?** Die Ubuntu-VM ist das eigentliche Ziel. Auf Kali läuft ebenfalls ein Agent, damit (a) die
Anforderung „mindestens zwei Agents“ erfüllt ist und (b) wir sehen, welche Informationen Wazuh auf einem
Angreifer-System sammelt (SCA, Vulnerability Detection, Prozesse).

## 2.2 Netzwerk

Alle VMs hängen in einem **isolierten Netzwerk**. Für Paket-Updates braucht jede VM zusätzlich Internet.

**VirtualBox:**

| Adapter | Typ | Zweck |
|---|---|---|
| Adapter 1 | NAT | Internet für Updates und Installation |
| Adapter 2 | Host-only-Adapter (`vboxnet0`, 192.168.56.0/24, DHCP aus) | Kommunikation zwischen den VMs |

**VMware Workstation:** Analog mit „NAT“ + „Host-only“ (VMnet1) oder einem eigenen LAN-Segment.

```text
                 Host-only-Netz 192.168.56.0/24
   ┌───────────────────┬─────────────────────┬────────────────────┐
   │                   │                     │                    │
┌──┴────────────┐  ┌───┴───────────────┐  ┌──┴────────────────┐
│ VM1 Wazuh     │  │ VM2 Ubuntu-Ziel   │  │ VM3 Kali          │
│ 192.168.56.10 │  │ 192.168.56.20     │  │ 192.168.56.30     │
│ Manager       │◀─│ wazuh-agent       │◀─│ nmap, hydra       │
│ Indexer       │  │ sshd, iptables    │  │ wazuh-agent       │
│ Dashboard     │◀─┼───────────────────┼──│                   │
└───────────────┘  └───────────────────┘  └───────────────────┘
      ▲  Browser https://192.168.56.10 (vom Host-PC aus)
```

## 2.3 Statische IP setzen (Ubuntu, Netplan)

Datei `/etc/netplan/50-m182.yaml` (Interface-Namen mit `ip a` prüfen, z. B. `enp0s8`):

```yaml
network:
  version: 2
  ethernets:
    enp0s8:
      dhcp4: no
      addresses: [192.168.56.10/24]   # VM1 = .10, VM2 = .20
```

```bash
sudo chmod 600 /etc/netplan/50-m182.yaml
sudo netplan apply
ip a show enp0s8
```

Für Kali siehe [VM3_Kali-Angreifer/01_Vorbereitung_Kali.md](VM3_Kali-Angreifer/01_Vorbereitung_Kali.md).

## 2.4 Benötigte Ports

| Port | Protokoll | Richtung | Zweck |
|---|---|---|---|
| 1514 | TCP | Agent → Manager | Übertragung der Ereignisse (verschlüsselt) |
| 1515 | TCP | Agent → Manager | Registrierung (Enrollment) der Agents |
| 55000 | TCP | → Manager | Wazuh-Server-API |
| 9200 | TCP | intern | Wazuh Indexer |
| 443 | TCP | Browser → Dashboard | Weboberfläche |
| 22 | TCP | Kali → Ubuntu | SSH (Angriffsziel) |

## 2.5 Hostnamen

```bash
sudo hostnamectl set-hostname wazuh-server    # VM1
sudo hostnamectl set-hostname ubuntu-target   # VM2
sudo hostnamectl set-hostname kali-attacker   # VM3
```

Optional `/etc/hosts` auf allen VMs:

```text
192.168.56.10  wazuh-server
192.168.56.20  ubuntu-target
192.168.56.30  kali-attacker
```

## 2.6 Verbindungstest

```bash
ping -c 3 192.168.56.10
ping -c 3 192.168.56.20
ping -c 3 192.168.56.30
```

## 2.7 Ablauf des Projekts

```text
1. Netzwerk + VMs  →  2. Wazuh-Server  →  3. Agents anbinden  →  4. Überwachung konfigurieren
        →  5. Angriffe von Kali  →  6. Alerts auswerten  →  7. Eigene Regeln + Active Response
        →  8. Angriffe wiederholen  →  9. Wirksamkeit bewerten
```

## 2.8 Snapshots

Vor jedem grösseren Schritt einen Snapshot erstellen:

| Snapshot | Zeitpunkt |
|---|---|
| `01_basis` | Nach OS-Installation und Updates |
| `02_wazuh_installiert` | Nach Wazuh-Installation / Agent-Anbindung |
| `03_konfiguriert` | Nach Regeln und Active Response, **vor** den Angriffen |

So kann man nach jedem Test wieder auf einen sauberen Stand zurück.
