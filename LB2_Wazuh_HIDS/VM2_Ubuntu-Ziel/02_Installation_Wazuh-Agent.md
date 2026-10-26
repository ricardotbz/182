# VM2 – Installation Wazuh-Agent (Ubuntu)

## Variante A: Über das Dashboard (empfohlen für Einsteiger)

1. Dashboard öffnen → **Agents management → Summary → Deploy new agent**
2. Betriebssystem: **Linux → DEB amd64**
3. Server-Adresse: `192.168.179.129`
4. Agent-Name: `ubuntu-endpunkt`
5. Der angezeigte Befehl wird auf der Ubuntu-VM ausgeführt (Version passt automatisch zum Server).

## Variante B: DEB-Paket direkt (in dieser Umgebung verwendet)

Der Server läuft mit **Wazuh 4.14.7**. Das passende DEB-Paket in genau dieser Version direkt installieren:

```bash
cd /tmp
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.7-1_amd64.deb

sudo WAZUH_MANAGER='192.168.179.129' WAZUH_AGENT_GROUP='default' WAZUH_AGENT_NAME='ubuntu-endpunkt' \
  dpkg -i ./wazuh-agent_4.14.7-1_amd64.deb
```

> Die Agent-Version darf **nicht neuer** sein als die Manager-Version. Deshalb hier die feste Version `4.14.7-1`
> passend zum Server.

## Agent starten

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
sudo systemctl status wazuh-agent
```

Automatische Updates des Agents verhindern:

```bash
sudo sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list
sudo apt update
```

## Verbindung prüfen

Auf dem Agent:

```bash
sudo grep -i "connected to the server" /var/ossec/logs/ossec.log
```

Erwartet:

```text
wazuh-agentd: INFO: (4102): Connected to the server ([192.168.179.129]:1514/tcp).
```

Auf dem Manager:

```bash
sudo /var/ossec/bin/agent_control -l
```

Im Dashboard muss `ubuntu-endpunkt` mit Status **active** erscheinen.

![Screenshot Agent ubuntu-endpunkt aktiv](../screenshots/vm2_agent_active.png)

## Fehlersuche

| Problem | Lösung |
|---|---|
| `Unable to connect to enrollment service` | Port 1515 auf dem Server offen? IP korrekt in `/var/ossec/etc/ossec.conf` → `<address>`? |
| Agent „disconnected“ | Port 1514 prüfen: `nc -zv 192.168.179.129 1514` |
| Agent doppelt / falscher Name | Auf dem Manager `/var/ossec/bin/manage_agents` → Agent entfernen, neu registrieren |
