# VM1 – Wazuh-Server

| Eigenschaft | Wert |
|---|---|
| Hostname | `wazuh-server` |
| IP | `192.168.56.10` |
| OS | Ubuntu Server 24.04 LTS |
| Ressourcen | 2–4 vCPU, 8 GB RAM (min. 4 GB), 50 GB Disk |
| Komponenten | Wazuh Manager, Wazuh Indexer, Wazuh Dashboard (All-in-One) |
| Rolle | Empfängt Daten der Agents, erzeugt Alerts, steuert Active Response |

## Dateien in diesem Ordner

| Datei | Inhalt |
|---|---|
| [01_Installation_Wazuh-Server.md](01_Installation_Wazuh-Server.md) | Installation aller Server-Komponenten, erster Login |
| [02_Eigene_Regeln_und_Decoder.md](02_Eigene_Regeln_und_Decoder.md) | Eigene Regeln für SSH-Brute-Force, Portscan und kritische Dateien |
| [03_Active_Response.md](03_Active_Response.md) | Automatisches Sperren der Angreifer-IP |
| [config/local_rules.xml](config/local_rules.xml) | Fertige Regeldatei zum Kopieren |
| [config/ossec_manager_active-response.xml](config/ossec_manager_active-response.xml) | Active-Response-Block für `ossec.conf` |

## Wichtige Pfade auf dem Server

| Pfad | Bedeutung |
|---|---|
| `/var/ossec/etc/ossec.conf` | Hauptkonfiguration des Managers |
| `/var/ossec/etc/rules/local_rules.xml` | Eigene Regeln |
| `/var/ossec/etc/decoders/local_decoder.xml` | Eigene Decoder |
| `/var/ossec/ruleset/rules/` | Mitgelieferte Regeln (nicht ändern!) |
| `/var/ossec/logs/alerts/alerts.json` | Alle Alerts im JSON-Format |
| `/var/ossec/logs/ossec.log` | Log des Managers (Fehlersuche) |
| `/var/ossec/bin/wazuh-logtest` | Tool zum Testen von Decodern und Regeln |
| `/var/ossec/bin/agent_control` | Agents auflisten, Active Response manuell auslösen |
