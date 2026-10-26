# Foto-Anleitung (Screenshots für die Doku)

Alle Angriffe sind **tatsächlich gelaufen** und wurden von Wazuh erkannt (siehe
[00_live_nachweis.txt](00_live_nachweis.txt)). Jetzt müssen nur noch die Screenshots gemacht werden.

**Dashboard öffnen:** im Browser `https://192.168.179.129` → Zertifikatswarnung akzeptieren →
Login `admin` / `admin`.

**Speichern:** alle Bilder als PNG in **genau diesen Ordner** (`screenshots/`) mit **exakt dem Dateinamen**
aus der Tabelle. Dann funktionieren die `![...]`-Verweise in der Doku automatisch.

**So filterst du die Events:** Menü **☰ → Threat Hunting → Events** (oder „Security events“). Oben im
Suchfeld (DQL) den Filter eintippen, Zeitbereich rechts oben auf **„Last 24 hours“**, dann Screenshot.

| # | Dateiname | Wo im Dashboard / Filter | Zeigt |
|---|---|---|---|
| 1 | `vm1_dashboard_login.png` | Die Login-Seite (vor dem Einloggen) | Dashboard erreichbar |
| 2 | `vm1_agents_active.png` | ☰ → **Agents** (Übersicht) | `ubuntu-endpunkt` **und** `kali-attacker` = active |
| 3 | `vm2_agent_active.png` | ☰ → Agents → **ubuntu-endpunkt** anklicken | Agent-Detail, Status active |
| 4 | `vm3_agent_active.png` | ☰ → Agents → **kali-attacker** anklicken | Agent-Detail, Status active |
| 5 | `vm3_bruteforce_alerts.png` | Events, Filter: `rule.id:100100` | SSH-Brute-Force erkannt (Level 12) |
| 6 | `vm1_active_response.png` | Events, Filter: `rule.id:651` | „Host Blocked by firewall-drop“ |
| 7 | `vm3_portscan_alert.png` | Events, Filter: `rule.id:100111` | Portscan erkannt (>15 Ports) |
| 8 | `vm2_fim_alert.png` | Events, Filter: `rule.id:100120` | Kritische Systemdatei geändert (FIM) |
| 9 | `vm3_fim_alerts.png` | Events, Filter: `rule.id:(100120 OR 100121 OR 100122)` | FIM-Alerts der Manipulation |
| 10 | `vm1_vulnerability.png` | ☰ → **Vulnerability Detection** → ubuntu-endpunkt | CVE-Liste nach Schweregrad |
| 11 | `vm1_sca.png` | ☰ → **Configuration Assessment (SCA)** → ubuntu-endpunkt | CIS-Benchmark-Score |

## Bild 12 (Terminal, kein Dashboard): `vm1_logtest.png`

Zeigt, dass die eigene Regel greift. In **PowerShell** ausführen und das Fenster mit dem Snipping Tool aufnehmen:

```powershell
ssh wazuh-user@192.168.179.129
```

Dann auf dem Server:

```bash
printf 'Oct 26 14:40:01 hardening-lab sshd[1]: Failed password for testuser from 192.168.179.130 port 51 ssh2\nOct 26 14:40:02 hardening-lab sshd[2]: Failed password for testuser from 192.168.179.130 port 52 ssh2\nOct 26 14:40:03 hardening-lab sshd[3]: Failed password for testuser from 192.168.179.130 port 53 ssh2\nOct 26 14:40:04 hardening-lab sshd[4]: Failed password for testuser from 192.168.179.130 port 54 ssh2\nOct 26 14:40:05 hardening-lab sshd[5]: Failed password for testuser from 192.168.179.130 port 55 ssh2\n' | sudo /var/ossec/bin/wazuh-logtest
```

Im Ergebnis erscheint `id: '100100'` und „M182: SSH-Brute-Force erkannt“ — das abfotografieren.

> **Tipp:** Pro Alert lohnt sich auch ein Screenshot, bei dem ein einzelner Treffer aufgeklappt ist
> (Felder `rule.id`, `rule.description`, `data.srcip`, `agent.name` sichtbar). Das macht die Doku beweiskräftiger.
