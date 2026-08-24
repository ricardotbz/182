# Enumeration + Fingerprinting

> **Kompetenz:** A1A · **Bloom:** Beurteilen · **Dauer:** ~180 Min. · **Sozialform:** Einzelauftrag

---

## Vorgehen
1. [Angriffssystem bereitstellen](../lab/README.md) (Kali-Linux + Metasploitable-VM)
2. Strategie bestimmen
3. [Code of Conduct](https://panmore.com/ethical-hacking-code-of-ethics-security-risk-issues) beachten (Vorabklärung, Information, Freigabebewilligung)
4. Durchführung des Vulnerability Scans
5. Recherche zu zwei möglichen Exploits, Durchführung eines Exploits, Dokumentation

---

## Ausgangslage
- Vor einem Angriff müssen möglichst viele Informationen im Netzwerk gesammelt werden.
- Aufbau einer Lab-Umgebung mit:
  - **Kali-VM:** 
  - **Metasploitable-VM:**


**Wichtige Schritte:**
- Kali-Linux / Metasploitable2 herunterladen und konfigurieren.
- IP-Adresse im Lab-Netzwerk konfigurieren.
- Vorgehen dokumentieren (Screenshots, Erklärungen, Resultate).

**Abgabe:**
- Dokument: `M182-Nachname_Enum+Fing.pdf` (max. 5 Seiten, klare Struktur).
- Via Teams gemäss Angaben der Lehrperson.

## Ablauf
In diesem Projekt geht es erst mal darum, eine Schwachstellenbewertung in einem ausgewählten Netzwerk vorzunehmen. Beim ersten Versuch wollen wir erste Erfahrungen mit dem Enumeration-Prozess sammeln. Wir checken die Geräte, die im Netzwerk vorzufinden sind (sollte in der Lab-Umgebung nur das Kali-Linux und die Metasploitable-VM sein - oder finden Sie mehr?). Den Enumeration-Prozess sollten Sie auf der Kali-Linux-Instanz starten. Damit der Enumeration-Prozess etwas spannender wird, können Sie auch weitere VMs in Ihr Lab-Netzwerk einhängen.

In der zweiten Phase Recherchieren Sie aufgrund dieser Erkenntnisse zwei Exploits, die für die entdeckten Schwachstellen infrage kommen. Entscheiden Sie sich für einen und führen Sie diesen in der dritten Phase durch. Zum Abschluss machen Sie sich Gedanken, welche Massnahmen auf der Gegenseite nötig gewesen wären, um einen solchen Angriff abzuwehren (Resilienzanalyse).

## Begriffserklärung

In der Mathematik und auch in der Informatik wird «Enumeration» als Auflistung einer Reihe von Elementen in einer Menge bezeichnet. Bei der Aufzählung im Hacking-Kontext werden Benutzernamen, Freigaben, Dienste, Webverzeichnisse, Gruppen und Computer in einem Netzwerk abgerufen. Dies wird auch als Netzwerkaufzählung bezeichnet. Während dieses Prozesses sammeln wir, wenn möglich, auch andere nützliche netzwerkbezogene Informationen. Je mehr Informationen in dieser Phase gesammelt werden können, desto einfacher wird das spätere eindringen ins System bei der Durchführung des Penetrationstests sein.

Ein wichtiger Teil des Enumerationsprozesses ist das Scannen von Ports und das «Fingerprinting» (Fingerabdrücke sammeln). Port-Scanning wird verwendet, um einen Server oder Host auf offene TCP- und UDP-Ports zu untersuchen. 

Beim Fingerabdruck werden die mit diesen Ports verbundenen Dienste identifiziert. Ein sehr beliebtes Tool zum Auflisten von Netzwerken, Scannen von Ports und zum Ablesen von Fingerabdrücken ist NMAP (Network Mapper), welches wir in diesem Auftrag auch verwenden werden. Es könnte auch ein Aufzählungstool namens «enum4linux» verwendet werden.

Enum4linux ist ein Tool zum Auflisten von Informationen von Windows- und Samba-Hosts.

Nachdem der «Enumeration-Process» des Lab-Netzwerks erfolgreich abgeschlossen wurde, werden wir eine Schwachstellenbewertung (Vulnerability Assessment) an diesem System durchzuführen. Mit Informationen aus dem Enumeration-Process, z. B. der Betriebssystemversion, offenen Ports und dahinterliegenden Diensten (wenn möglich mit Version), werden wir nach bekannten Schwachstellen dieser Dienste suchen. Zu diesem Zweck verwenden wir dann die Open Source Vulnerability Database (OSVDB) und die Common Vulnerabilities and Exposures (CVE).

Der letzte Schritt besteht darin, den Zielhost mit einem Schwachstellenscanner namens OpenVAS unter Kali Linux auf diese Schwachstellen zu scannen.


---

## Enumeration und Port Scanning


### Netzwerkscan:

Der folgende Befehl unter Kali-Linux gibt alle Live-Hosts im angegebenen IP-Bereich zurück. In diesem Beispiel handelt es sich um den Bereich 172.16.17.0/24 (IP-Range 172.16.17.0 bis 172.16.17.255)

```bash
nmap -sn 172.16.17.0/24
```

### NMAP Port Scan (Stealthy Port Scan)

Wir starten den Open-Port-Scan mit dem Scannen der Zielhosts (mit NMAP). Zu diesem Zweck werden wir einen TCP-SYN-Scan verwenden und damit die Ziele nach offenen TCP-Ports durchsuchen. 

Der SYN-Scan wird als Stealthy-Port-Scan bezeichnet, da der vollständige TCP-Handshake nicht beendet wird.

Eine vollständige TCP-Verbindung beginnt mit einem Drei-Wege-Handshake, bei dem zuerst ein SYN-Paket von NMAP (erster Schritt des 3-Wege-Handshakes) gesendet wird. Wenn ein Port auf dem Zielcomputer geöffnet ist, antwortet dieser mit einem SYN-ACK-Paket. Falls das erste SYNPaket keine Antwort vom Ziel erhält, ist dieser Port entweder geschlossen oder von einer Firewall gefiltert. 

Beim dritten Schritt in diesem Prozess sollte unser Client auf das SYN-ACK mit einem ACKPaket antworten, um den vollständigen TCP-Handshake abzuschließen. Im Falle eines SYN-Scans ist dies allerdings niemals der Fall. 
Genau deshalb wird dieser Scan als Stealthy-Scan oder «Verstohlener Scan» bezeichnet

![image](../_resources/images/nmap_syn_scan.png)

Wenn wir einen SYN-Scan mit NMAP starten, ohne den Port-Bereich anzugeben, durchsucht NMAP nur die ersten 1000 Ports, die als die wichtigsten Ports angesehen werden, anstatt aller 65.535 Ports. 
Um alle Ports zu scannen, muss das `-p-` Flag verwendet werden. Der SYN-Scan-Befehl von Nmap verwendet das Flag `-sS`, das im folgenden Befehl zum SYN-Scannen von Port 1 bis Port 65.535 verwendet wird.

```bash
nmap -sS -p- [target IP address]
```

> __Sind offene Ports anfällig?__
> 
> Nur weil ein Port offen ist, bedeutet dies nicht, dass die damit verbundene Software anfällig ist. Wir müssen die Version des Betriebssystems und die Dienste hinter den offenen Ports kennen. Anhand dieser Informationen können wir feststellen, ob bekannte Schwachstellen zur Ausnutzung bekannt und verfügbar sind. Das Ergebnis des Dienst- und Betriebssystem-Scans gibt uns die entsprechenden Informationen, um diese Schwachstellenbewertung erfolgreich durchzuführen. Um diese Informationen zu erhalten, führen wir den Port-Scan mit der Option __-sV__ für die Versionserkennung und der Option __-O__ für die Betriebssystemerkennung aus, um die Versionen der ausgeführten Dienste und des Betriebssystems abzurufen. 
> 
> Der Scan des map Betriebssystems und der Version führt dann einen vollständigen TCP-Handshake aus und verwendet Techniken wie z.B. das Aufrufen von Bannern, um Informationen von den verfügbaren Diensten abzurufen.


### Nmap Service- und OS-Scan

Verwenden Sie den folgenden Befehl, um den Nmap-Port-Scan mit Dienst- und Betriebssystemerkennung zu starten:

```bash
nmap -sS -sV -O [target IP address]
```

Nach dem Ausführen dieses Befehls gibt NMap eine Liste der offenen Ports und der verbundenen Dienste zurück.

![image](../_resources/images/nmap_service_scan.png)

Die Nmap-Port- und -Dienst-Scans geben viele offene Ports, Abhördienste und die Version des Betriebssystems zurück. Auf dem Zielhost wird Linux 2.6.9 - 2.6.33 als Betriebssystem ausgeführt (auf diesem Screenshot nicht ersichtlich, ist weiter unten ebenfalls aufgelistet). Wir können sehen, dass der Host einen SSH-Dienst mit OpenSSH, einem Telnet-Dienst, einem Apache 2.2.8-Webserver, 2 SQLServern und einigen weiteren Diensten ausführt. Lassen Sie uns alle Services mit Version und Port in einer Liste zusammenfassen, die wir dann beim nächsten Auftrag verwenden, in der wir eine Schwachstellenbewertung durchführen und nach häufigen Schwachstellen suchen.

### NMAP UDP-Scan:

Bisher haben wir nur nach offenen TCP-Ports gesucht. Dies ist die Standardeinstellung für Nmap. Nach offenen UDP-Ports haben wir noch keine Ausschau gehalten.

Mit folgendem Befehl kann ein UDP-Scan gestartet werden.

```bash
nmap -sU [target IP address]
```

Man kann auch das Flag -p verwenden, um die zu durchsuchenden Ports zu definieren. Der UDP-Scan dauert etwas länger als ein TCP-Scan. NMAP gibt beim Angriff auch ein vulnerables System z.B. die folgenden Informationen zu den gefundenen offenen UDP-Ports zurück:

PORT | STATE | SERVICE
--|--|--
53/udp | open | domain
111/udp |  open  | rpcbind
137/udp | open | netbios-ns
2049/udp | open | nf

Beachten Sie, dass UDP-Scans viele Fehlalarme verursachen können. Die Fehlalarme können auftreten, weil UDP ein Äquivalent eines TCP-SYN-Pakets fehlt. Wenn ein gescannter UDP-Port geschlossen wird, antwortet das System mit einer Meldung, dass der ICMP-Port nicht erreichbar ist. Das Fehlen eines solchen Pakets weist darauf hin, dass der UDP-Port für viele Scan-Tools offen ist. Wenn auf dem Zielhost eine Firewall vorhanden ist, die die ICMP-Nachricht "Nicht erreichbar" blockiert, scheinen alle UDP-Ports offen zu sein. Wenn die Firewall einen einzelnen Port blockiert, meldet der Scanner fälschlicherweise, dass der Port offen ist.

Natürlich wissen wir, dass das vorbereitete «Metasploitable 2»-System absichtlich anfällig ist. Man kann daher nur vermuten, dass die meisten, wenn nicht alle Dienste Schwachstellen, Hintertüren usw. 
enthalten. 

## Recherche und Durchführung eines Exploits

Nachdem Sie nun diverse Schwachstellen im Netzwerk gefunden haben, wollen sie herausfinden, welche Exploits mit diesen gewonnenen Erkenntnissen erfolgreich umgesetzt werden können. Recherchieren Sie im Internet und sammeln Sie Informationen. Das Ziel ist es, in ihr ausgewähltes Zielsystem einzudringen. Viele Wege führen nach Rom.
1. Entscheiden Sie sich für zwei Angriffsvarianten
2. Recherchieren und finden Sie angemessene Quellen / Ressourcen, um einen Angriff entsprechend durchzuführen (Quellen müssen in der Doku angegeben werden)
3. Wählen Sie einen der beiden Exploits aus und führen Sie diesen durch, dokumentieren Sie
4. Definieren Sie drei Massnahmen, welche von der Gegenseite unterlassen wurden, um den Angriff zu vermeiden/erschweren (die Resilienz des Systems entsprechend zu erhöhen)

Experimentieren sie selbst ein wenig: https://docs.rapid7.com/metasploit/metasploitable-2-exploitability-guide

---


## Zusammenfassung der Arbeitsschritte
- Lab-Umgebung aufsetzen
- Netzwerk scannen und dokumentieren
- Schwachstellen recherchieren
- Exploit ausführen
- Resilienz-Massnahmen erarbeiten
- Dokumentation erstellen und fristgerecht abgeben
