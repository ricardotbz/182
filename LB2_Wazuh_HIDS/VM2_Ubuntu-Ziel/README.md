# VM2 – Ubuntu-Zielsystem (überwachter Host)

| Eigenschaft | Wert |
|---|---|
| Hostname | `hardening-lab` |
| Agent-Name in Wazuh | `ubuntu-endpunkt` |
| IP | `192.168.179.128` |
| OS | Ubuntu 24.04 Desktop |
| Ressourcen | 2 vCPU, 4 GB RAM, 80 GB Disk |
| Software | OpenSSH-Server, iptables, auditd, Wazuh-Agent |
| Rolle | Wird von Kali angegriffen und von Wazuh überwacht. Hier greift Active Response (IP-Sperre). |

## Dateien in diesem Ordner

| Datei | Inhalt |
|---|---|
| [01_Vorbereitung_Ubuntu.md](01_Vorbereitung_Ubuntu.md) | Grundinstallation, SSH, Testbenutzer |
| [02_Installation_Wazuh-Agent.md](02_Installation_Wazuh-Agent.md) | Agent installieren und am Manager anmelden |
| [03_Konfiguration_Ueberwachung.md](03_Konfiguration_Ueberwachung.md) | Log-Sammlung, File Integrity Monitoring, Firewall-Logging für Portscans |
| [config/ossec_agent_ubuntu.xml](config/ossec_agent_ubuntu.xml) | Konfigurationsblöcke für die Agent-`ossec.conf` |

## Was wird auf dieser VM überwacht?

| Bereich | Quelle | Wazuh-Modul |
|---|---|---|
| SSH-Anmeldungen | journald (`sshd`) | Log-Analyse (logcollector) |
| Systemmeldungen, Kernel/Firewall | journald (`kernel`, iptables `M182-SCAN:`) | Log-Analyse |
| Änderungen an Dateien | `/etc`, `/usr/bin`, `/usr/sbin`, `/root`, `/home` | FIM (syscheck) |
| Installierte Pakete / CVEs | Paketliste | Syscollector + Vulnerability Detection |
| Härtung (CIS Benchmark) | Systemkonfiguration | SCA |
| Rootkits | Dateisystem, Prozesse | Rootcheck |
| Wer hat eine Datei geändert? | auditd | FIM whodata |
