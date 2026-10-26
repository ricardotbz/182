# VM3 – Wazuh-Agent auf Kali installieren

Kali basiert auf Debian, deshalb funktioniert das DEB-Paket wie bei Ubuntu. Der Server läuft mit **Wazuh 4.14.7**.
Damit die Versionen zusammenpassen, wird das DEB-Paket in **genau dieser Version** direkt installiert (der Agent
darf nie neuer als der Manager sein).

```bash
# Passendes DEB-Paket herunterladen (Version = Server-Version 4.14.7)
cd /tmp
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.7-1_amd64.deb

# Installieren und dabei Manager-Adresse + Agent-Name setzen
sudo WAZUH_MANAGER='192.168.179.129' WAZUH_AGENT_GROUP='default' WAZUH_AGENT_NAME='kali-attacker' \
  dpkg -i ./wazuh-agent_4.14.7-1_amd64.deb
```

Agent starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
sudo systemctl status wazuh-agent
```

Verbindung prüfen:

```bash
sudo grep -i "connected to the server" /var/ossec/logs/ossec.log
```

Auf dem Manager müssen jetzt **beide** Agents erscheinen:

```bash
sudo /var/ossec/bin/agent_control -l
```

```text
   ID: 001, Name: ubuntu-endpunkt,  IP: any, Active
   ID: 002, Name: kali-attacker,  IP: any, Active
```

![Screenshot beide Agents aktiv](../screenshots/vm3_agent_active.png)

> **Zweck des Agents auf Kali:** Damit ist die Anforderung „mindestens zwei Agents“ erfüllt. Ausserdem
> sammelt Wazuh auch hier SCA-, Schwachstellen- und Prozessdaten. Für die Angriffserkennung ist aber der
> Agent auf der **Ubuntu-VM** entscheidend.
