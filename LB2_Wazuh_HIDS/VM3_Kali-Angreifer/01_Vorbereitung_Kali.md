# VM3 – Vorbereitung Kali Linux

## 1. Netzwerk

- VMware-Adapter auf **NAT (VMnet8)** – Internet und VM-zu-VM in einem Netz (siehe [Netzwerkplan](../02_Testumgebung_Netzwerkplan.md#22-netzwerk))
- IP-Adresse per DHCP (`192.168.179.130`)

Kali bezieht die Adresse automatisch über NetworkManager. Prüfen:

```bash
ip -4 a show eth0
```

In dieser Umgebung ist das die Adresse `192.168.179.130`.

> **Zeitzone:** Das verwendete Kali-Image stand auf `America/New_York`. Für einheitliche Zeitstempel kann man
> auf Europe/Zurich stellen (siehe nächster Abschnitt). Für die Angriffe selbst ist das nicht entscheidend,
> da die Erkennung auf der Ubuntu-VM stattfindet.

## 2. System aktualisieren und Werkzeuge

```bash
sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname kali
sudo timedatectl set-timezone Europe/Zurich
```

`nmap` und `hydra` sind in Kali vorinstalliert. Prüfen bzw. nachinstallieren:

```bash
which nmap hydra
sudo apt install -y nmap hydra curl gnupg
```

## 3. Verbindung zum Ziel testen

```bash
ping -c 3 192.168.179.128
ping -c 3 192.168.179.129
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
