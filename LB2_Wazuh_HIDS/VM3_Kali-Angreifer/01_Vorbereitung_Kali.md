# VM3 – Vorbereitung Kali Linux

## 1. Netzwerk

- Adapter 1 = NAT (Internet), Adapter 2 = Host-only
- Statische IP `192.168.56.30`

Kali nutzt meist NetworkManager. Statische IP über die GUI (Settings → Network) oder per Datei:

```bash
sudo nano /etc/network/interfaces
```

```text
auto eth1
iface eth1 inet static
    address 192.168.56.30
    netmask 255.255.255.0
```

```bash
sudo systemctl restart networking
ip -br a
```

Interface-Name mit `ip -br a` prüfen (oft `eth1` oder `enp0s8`).

## 2. System aktualisieren und Werkzeuge

```bash
sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname kali-attacker
sudo timedatectl set-timezone Europe/Zurich
```

`nmap` und `hydra` sind in Kali vorinstalliert. Prüfen bzw. nachinstallieren:

```bash
which nmap hydra
sudo apt install -y nmap hydra curl gnupg
```

## 3. Verbindung zum Ziel testen

```bash
ping -c 3 192.168.56.20
ping -c 3 192.168.56.10
```

## 4. Wortliste (Passwortliste) für den Brute-Force

Für den Test eine kleine, eigene Liste anlegen, die das schwache Testpasswort enthält:

```bash
cat > ~/m182-passwords.txt <<'EOF'
123456
password
admin
root
qwerty
letmein
sommer2026
EOF

echo "testuser" > ~/m182-users.txt
```

> So dauert der Test nur wenige Sekunden. Die grosse Liste `rockyou.txt`
> (`/usr/share/wordlists/rockyou.txt`) ist für diesen Zweck nicht nötig.

## 5. Snapshot

Snapshot `01_basis` erstellen.
