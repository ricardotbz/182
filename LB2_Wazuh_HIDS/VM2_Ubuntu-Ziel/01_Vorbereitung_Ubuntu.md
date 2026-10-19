# VM2 – Vorbereitung Ubuntu-Zielsystem

## 1. Grundinstallation

- Ubuntu Server 24.04 LTS installieren, bei der Installation **OpenSSH server** anwählen
- Netzwerk: Adapter 1 = NAT, Adapter 2 = Host-only
- Statische IP `192.168.56.20` (Netplan, siehe [Netzwerkplan](../02_Testumgebung_Netzwerkplan.md#23-statische-ip-setzen-ubuntu-netplan))

```bash
sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname ubuntu-target
sudo timedatectl set-timezone Europe/Zurich
sudo apt install -y openssh-server iptables auditd curl gnupg apt-transport-https
```

## 2. Logging prüfen

Ubuntu Server 24.04 schreibt SSH-Ereignisse über **rsyslog** nach `/var/log/auth.log`:

```bash
systemctl status rsyslog
ls -l /var/log/auth.log /var/log/syslog /var/log/kern.log
```

Falls rsyslog fehlt:

```bash
sudo apt install -y rsyslog
sudo systemctl enable --now rsyslog
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
