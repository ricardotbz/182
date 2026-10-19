# VM3 – Kali-Linux (Angreifer)

| Eigenschaft | Wert |
|---|---|
| Hostname | `kali-attacker` |
| IP | `192.168.56.30` |
| OS | Kali Linux (aktuelle Version) |
| Ressourcen | 2 vCPU, 2–4 GB RAM, 30 GB Disk |
| Werkzeuge | `nmap`, `hydra` (vorinstalliert in Kali), Wazuh-Agent |
| Rolle | Führt die Angriffe gegen die Ubuntu-VM aus. Trägt selbst einen Agent (zweiter überwachter Host). |

## Dateien in diesem Ordner

| Datei | Inhalt |
|---|---|
| [01_Vorbereitung_Kali.md](01_Vorbereitung_Kali.md) | Netzwerk, Werkzeuge, Wortliste |
| [02_Installation_Wazuh-Agent.md](02_Installation_Wazuh-Agent.md) | Wazuh-Agent auf Kali installieren |
| [03_Angriffsszenarien.md](03_Angriffsszenarien.md) | Die drei Angriffe Schritt für Schritt |

> **Rechtlicher Hinweis:** Alle Angriffe werden ausschliesslich in der isolierten Testumgebung gegen die
> eigene Ubuntu-VM durchgeführt. Angriffe auf fremde Systeme sind nach **StGB Art. 143bis** (unbefugtes Eindringen
> in ein Datenverarbeitungssystem) strafbar.
