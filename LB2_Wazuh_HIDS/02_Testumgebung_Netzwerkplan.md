# 2. Testumgebung und Netzwerkplan

## 2.1 Übersicht der VMs

| VM | Rolle | Betriebssystem | Hostname | IP-Adresse | vCPU | RAM | Disk |
|---|---|---|---|---|---|---|---|
| **VM1** | Wazuh-Server (Manager, Indexer, Dashboard) | Amazon Linux 2023 (Wazuh-OVA 4.14.7) | `wazuh-server` | `192.168.179.129` | 4 | 8 GB | 50 GB |
| **VM2** | Überwachtes Zielsystem (Agent) | Ubuntu 24.04 Desktop | `hardening-lab` | `192.168.179.128` | 2 | 4 GB | 80 GB |
| **VM3** | Angreifer (Agent) | Kali Linux Rolling | `kali` | `192.168.179.130` | 2 | 4 GB | 80 GB |

> **IP-Adressen:** Die VMs beziehen ihre Adresse per DHCP aus dem VMware-NAT-Netz (VMnet8, `192.168.179.0/24`).
> Die hier genannten Adressen sind die in dieser Umgebung tatsächlich vergebenen. Nach einem längeren Stillstand
> kann der DHCP-Server andere Adressen vergeben; dann mit `ip -4 a` die aktuelle Adresse prüfen und in den
> Befehlen ersetzen. Die Manager-IP `192.168.179.129` ist in den Agents fest hinterlegt — ändert sie sich,
> müssen die Agents angepasst werden.
>
> **Server-Login (OVA):** Benutzer `wazuh-user`, Passwort `wazuh` (Konsole/SSH). **Dashboard:** `admin` / `admin`.

**Warum zwei Agents?** Die Ubuntu-VM ist das eigentliche Ziel. Auf Kali läuft ebenfalls ein Agent, damit (a) die
Anforderung „mindestens zwei Agents“ erfüllt ist und (b) wir sehen, welche Informationen Wazuh auf einem
Angreifer-System sammelt (SCA, Vulnerability Detection, Prozesse).

## 2.2 Netzwerk

In dieser Umgebung läuft **VMware Workstation** auf einem Windows-Host. Alle drei VMs hängen am selben
**NAT-Netz VMnet8** (`192.168.179.0/24`). Dieses eine Netz deckt beide Anforderungen ab:

- **Internet** für Paket-Updates und Agent-Download (über das NAT-Gateway `192.168.179.2`).
- **Kommunikation untereinander**, da alle VMs im selben Subnetz liegen und sich direkt erreichen.

| Rolle | Wert |
|---|---|
| Virtualisierung | VMware Workstation (Windows-Host) |
| Netz | NAT, VMnet8, `192.168.179.0/24` |
| Adresszuweisung | DHCP durch VMware |
| NAT-Gateway (Internet) | `192.168.179.2` |
| Host-PC (VMnet8-Adapter) | `192.168.179.1` |

> Ein eigener Host-only-Adapter wie bei VirtualBox ist hier nicht nötig: Über VMnet8 sehen sich die VMs
> gegenseitig **und** kommen ins Internet. Ein Bridged-Adapter wäre im Schulnetz unzuverlässig (DHCP, Client-Isolation).

```text
                 VMware NAT-Netz VMnet8  192.168.179.0/24
   ┌───────────────────┬─────────────────────┬────────────────────┐
   │                   │                     │                    │
┌──┴──────────────┐  ┌─┴─────────────────┐  ┌┴──────────────────┐
│ VM1 Wazuh       │  │ VM2 hardening-lab │  │ VM3 kali          │
│ 192.168.179.129 │  │ 192.168.179.128   │  │ 192.168.179.130   │
│ Manager         │◀─│ wazuh-agent       │◀─│ nmap, hydra       │
│ Indexer         │  │ sshd, iptables    │  │ wazuh-agent       │
│ Dashboard       │◀─┼───────────────────┼──│                   │
└─────────────────┘  └───────────────────┘  └───────────────────┘
      ▲  Browser https://192.168.179.129 (vom Host-PC aus)
```

## 2.3 IP-Adressen (DHCP)

Die VMs beziehen ihre Adresse automatisch per DHCP aus dem VMnet8-Netz. Eine manuelle statische Konfiguration
ist nicht nötig. Die aktuelle Adresse einer VM prüft man mit:

```bash
ip -4 a show eth0     # Server (Amazon Linux) und Kali: eth0
ip -4 a show ens33    # Ubuntu-VM: ens33
```

> **Wichtig:** Die Manager-IP `192.168.179.129` ist in beiden Agents fest hinterlegt. Bekäme der Server nach
> einem Neustart eine andere DHCP-Adresse, würden die Agents die Verbindung verlieren. In dieser Umgebung
> ist die Adresse über die DHCP-Lease stabil geblieben. Für einen dauerhaften Betrieb wäre eine DHCP-Reservierung
> oder eine statische Adresse sinnvoll.

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
sudo hostnamectl set-hostname hardening-lab   # VM2
sudo hostnamectl set-hostname kali   # VM3
```

Optional `/etc/hosts` auf allen VMs:

```text
192.168.179.129  wazuh-server
192.168.179.128  hardening-lab
192.168.179.130  kali
```

## 2.6 Verbindungstest

```bash
ping -c 3 192.168.179.129
ping -c 3 192.168.179.128
ping -c 3 192.168.179.130
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
