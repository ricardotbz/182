# VM2 – Vorbereitung Ubuntu-Zielsystem

## 1. Grundinstallation

- Ubuntu 24.04 (Desktop) installieren, **OpenSSH server** aktivieren
- Netzwerk: VMware-Adapter auf **NAT (VMnet8)** – Internet und VM-zu-VM in einem Netz (siehe [Netzwerkplan](../02_Testumgebung_Netzwerkplan.md#22-netzwerk))
- IP-Adresse per DHCP (`192.168.179.128`), prüfen mit `ip -4 a show ens33`

```bash
sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname hardening-lab
sudo timedatectl set-timezone Europe/Zurich
sudo apt install -y openssh-server iptables auditd curl gnupg
```

## 2. Logging prüfen

Ubuntu 24.04 protokolliert über **systemd-journald**. Die SSH-Ereignisse liegen im Journal, nicht (nur) in
`/var/log/auth.log`. Wazuh 4.14 liest journald von sich aus – es muss also keine Logdatei extra eingerichtet
werden.

```bash
systemctl status systemd-journald
journalctl -u ssh --no-pager | tail -n 5     # Beispiel: letzte sshd-Ereignisse
```

## 3. SSH für den Test konfigurieren

Damit der Brute-Force-Angriff möglich ist, muss die **Passwort-Anmeldung** erlaubt sein:

```bash
sudo nano /etc/ssh/sshd_config.d/50-m182.conf
```

```text
PasswordAuthentication yes
PermitRootLogin no
MaxAuthTries 6
LogLevel VERBOSE
```

```bash
sudo sshd -t && sudo systemctl restart ssh
```

> Dies ist eine **bewusste Schwächung für den Test**. In der Praxis sollte man nur Schlüssel-Login erlauben
> (siehe Massnahmen in [04_Handlungsziele_und_Fazit.md](../04_Handlungsziele_und_Fazit.md)).

## 4. Testbenutzer mit schwachem Passwort

```bash
sudo adduser testuser
# Passwort z. B.: sommer2026   (bewusst schwach, steht in der Wortliste des Angreifers)
```

> Den Benutzer **nur in der Testumgebung** anlegen und nach dem Projekt wieder löschen:
> `sudo deluser --remove-home testuser`

## 5. Testdateien für File Integrity Monitoring

```bash
sudo mkdir -p /opt/m182-wichtig
echo "Konfiguration v1" | sudo tee /opt/m182-wichtig/app.conf
```

## 6. Snapshot

Snapshot `01_basis` erstellen.
