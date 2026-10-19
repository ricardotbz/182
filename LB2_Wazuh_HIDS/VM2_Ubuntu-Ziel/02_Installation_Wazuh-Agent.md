# VM2 – Installation Wazuh-Agent (Ubuntu)

## Variante A: Über das Dashboard (empfohlen für Einsteiger)

1. Dashboard öffnen → **Agents management → Summary → Deploy new agent**
2. Betriebssystem: **Linux → DEB amd64**
3. Server-Adresse: `192.168.56.10`
4. Agent-Name: `ubuntu-target`
5. Der angezeigte Befehl wird auf der Ubuntu-VM ausgeführt (Version passt automatisch zum Server).

## Variante B: Manuell über das Wazuh-Repository

```bash
# GPG-Schlüssel importieren
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | \
  sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
sudo chmod 644 /usr/share/keyrings/wazuh.gpg

# Repository hinzufügen
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | \
  sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt update

# Agent installieren und Manager-Adresse direkt setzen
sudo WAZUH_MANAGER="192.168.56.10" WAZUH_AGENT_NAME="ubuntu-target" apt install -y wazuh-agent
```

> Die Agent-Version darf **nicht neuer** sein als die Manager-Version. Bei Bedarf eine bestimmte Version
> installieren: `apt install wazuh-agent=4.12.0-1`

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
wazuh-agentd: INFO: (4102): Connected to the server ([192.168.56.10]:1514/tcp).
```

Auf dem Manager:

```bash
sudo /var/ossec/bin/agent_control -l
```

Im Dashboard muss `ubuntu-target` mit Status **active** erscheinen.

![Screenshot Agent ubuntu-target aktiv](../screenshots/vm2_agent_active.png)

## Fehlersuche

| Problem | Lösung |
|---|---|
| `Unable to connect to enrollment service` | Port 1515 auf dem Server offen? IP korrekt in `/var/ossec/etc/ossec.conf` → `<address>`? |
| Agent „disconnected“ | Port 1514 prüfen: `nc -zv 192.168.56.10 1514` |
| Agent doppelt / falscher Name | Auf dem Manager `/var/ossec/bin/manage_agents` → Agent entfernen, neu registrieren |
