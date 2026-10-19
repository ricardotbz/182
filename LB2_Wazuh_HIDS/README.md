# LB2 – M182: Wazuh als Host-basiertes Intrusion Detection System

**Namen:** Rewan, Ricardo und Samuele
**Klasse:** PE23F
**Datum Themenwunsch:** 21.09.2026
**Format:** Dokumentation (Markdown)

---

## Ziel der Arbeit

Wir bauen in einer virtuellen Umgebung ein Host-basiertes Intrusion Detection System (HIDS) mit **Wazuh** auf.
Eine **Kali-Linux-VM** greift eine **Ubuntu-VM** an. Die Ubuntu-VM wird von Wazuh überwacht. Wazuh soll die Angriffe
erkennen, Alerts erzeugen und die angreifende IP-Adresse per **Active Response** automatisch sperren.

Die Dokumentation ist so geschrieben, dass andere Lernende die Umgebung Schritt für Schritt nachbauen können.

## Aufbau der Dokumentation

| Nr. | Datei / Ordner | Inhalt |
|---|---|---|
| 1 | [01_Theorie_HIDS_und_Wazuh.md](01_Theorie_HIDS_und_Wazuh.md) | HIDS vs. NIDS, Aufbau und Funktionsweise von Wazuh |
| 2 | [02_Testumgebung_Netzwerkplan.md](02_Testumgebung_Netzwerkplan.md) | VMs, IP-Adressen, Netzwerk, Ports, Ablauf |
| 3 | [VM1_Wazuh-Server/](VM1_Wazuh-Server/README.md) | Installation Manager/Indexer/Dashboard, eigene Regeln, Active Response |
| 4 | [VM2_Ubuntu-Ziel/](VM2_Ubuntu-Ziel/README.md) | Ubuntu vorbereiten, Agent installieren, Log-Sammlung, FIM, Firewall-Logging |
| 5 | [VM3_Kali-Angreifer/](VM3_Kali-Angreifer/README.md) | Kali vorbereiten, Agent installieren, Angriffsszenarien |
| 6 | [03_Auswertung_Wirksamkeit.md](03_Auswertung_Wirksamkeit.md) | Was wurde erkannt, was nicht? Grenzen und Verbesserungen |
| 7 | [04_Handlungsziele_und_Fazit.md](04_Handlungsziele_und_Fazit.md) | Abdeckung der Handlungsziele, Massnahmen, Fazit |
| 8 | [05_Quellen.md](05_Quellen.md) | Quellen und Links |

## Ordnerstruktur

```text
M182/
├── README.md
├── 01_Theorie_HIDS_und_Wazuh.md
├── 02_Testumgebung_Netzwerkplan.md
├── 03_Auswertung_Wirksamkeit.md
├── 04_Handlungsziele_und_Fazit.md
├── 05_Quellen.md
├── VM1_Wazuh-Server/
│   ├── README.md
│   ├── 01_Installation_Wazuh-Server.md
│   ├── 02_Eigene_Regeln_und_Decoder.md
│   ├── 03_Active_Response.md
│   └── config/
│       ├── local_rules.xml
│       └── ossec_manager_active-response.xml
├── VM2_Ubuntu-Ziel/
│   ├── README.md
│   ├── 01_Vorbereitung_Ubuntu.md
│   ├── 02_Installation_Wazuh-Agent.md
│   ├── 03_Konfiguration_Ueberwachung.md
│   └── config/
│       └── ossec_agent_ubuntu.xml
├── VM3_Kali-Angreifer/
│   ├── README.md
│   ├── 01_Vorbereitung_Kali.md
│   ├── 02_Installation_Wazuh-Agent.md
│   └── 03_Angriffsszenarien.md
└── screenshots/          (hier eure Screenshots ablegen)
```

## Empfohlene Reihenfolge zum Nachbauen

1. Theorie lesen (Kapitel 1)
2. Netzwerk und VMs anlegen (Kapitel 2)
3. Wazuh-Server installieren (VM1, Datei 01)
4. Ubuntu vorbereiten und Agent anbinden (VM2, Dateien 01–03)
5. Kali vorbereiten und Agent anbinden (VM3, Dateien 01–02)
6. Eigene Regeln und Active Response auf dem Server einrichten (VM1, Dateien 02–03)
7. Angriffe durchführen (VM3, Datei 03)
8. Ergebnisse in Kapitel 6 eintragen und bewerten

> **Hinweis:** Alle Angriffe werden **nur** in der isolierten Testumgebung gegen eigene VMs durchgeführt.
> Angriffe auf fremde Systeme sind verboten (StGB Art. 143bis).

## Platzhalter

Stellen mit `[AUSFÜLLEN]` oder `![Screenshot](...)` müssen während der praktischen Umsetzung mit euren
eigenen Ergebnissen und Screenshots ergänzt werden.
