---
name: fortinet-fortianalyzer
description: "FortiAnalyzer 7.6x: modes, logs, HA, Fabric, datasets."
version: 1.0.0
---

# FortiAnalyzer (piece: fortianalyzer)

Surface: FortiAnalyzer 7.6.8. Corpus: `fortinet-corpus/fortianalyzer-7.6x` (8 docs, 1,718 pages, 4,063 chunks, collection `fca76`). All facts below verified against the extracted text.

## When to use
- ANY question about FortiAnalyzer (log collection/analysis, FortiAnalyzer HA/Fabric, dataset/charts, log forwarding endpoints on FortiAnalyzer).
- NOT for: FortiGate device config (fortinet-* FortiOS pieces), FortiManager management-of-devices (fortinet-fortimanager), FortiWeb WAF (fortinet-fortiweb). FMG→FCA log forwarding: use this piece for the FortiAnalyzer-side ports/destinations.

## Doc set (8 PDFs, 1,718 pages)
- Administration Guide 7.6.8 (659p), CLI Reference 7.6.8 (343p), Dataset Reference 7.6.8 (573p)
- Release Notes 7.6.8 (69p), Upgrade Guide 7.6.8 (27p), Ports 7.6 (4p)
- Best Practices (26p), Architecture Guide 7.6 (17p)

## Operation modes
- **Analyzer mode**: receives, analyzes, stores (SQL database), reports. Full feature set.
- **Collector mode**: primary task = forwarding connected devices' logs to an Analyzer and archiving. Retains logs in **original binary format** (not written to the DB); most features disabled.
- Feature comparison: BOTH = Device Manager, System Settings, Log Forwarding. ANALYZER-ONLY = FortiView, Incidents & Events, Reporting, monitoring devices. Log View = full in Analyzer, raw archive logs only in Collector.
- **Analyzer–Collector collaboration**: Analyzer + Collector on separate units; the Analyzer offloads log receiving to the Collector (maximizes Collector log-receiving performance); setup in Admin Guide "Collectors and Analyzers" (p640).
- **FortiAnalyzer Fabric**: multiple FortiAnalyzers as members; one device in supervisor mode as root; incidents/events/logs synced from members to supervisor **via API**; ideal for high-volume environments with many FortiAnalyzers (sizing: Architecture Guide).
- **ADOMs**: FortiAnalyzer supports administrative domains (constrain admin visibility).

## HA (Admin Guide p629-639)
- Operation modes: **Active-Passive** or **Active-Active** (Active-Active → geo-redundant solution).
- All members must share Group Name, Group ID (1-255), and password.
- Default role = **Secondary**; a secondary **cannot become primary until synchronized** with the current primary.
- **Initial Sync rule**: during initial setup at least ONE node must have Initial Sync **disabled**; the primary is elected from those nodes. If ALL nodes have Initial Sync enabled, **the cluster gets stuck trying to synchronize**. Nodes added later can have it enabled (default).
- **Cluster VIP**: optional; requires a **layer 2 connection** between HA members. If no VIP, pick the peer-communication interface as Heart Beat Interface.
- Heart Beat Interval default **4 s**; Failover Threshold = interval × 3 (default **12 s**).
- **Log Data Sync** on by default (real-time log sync among units); configuration sync available.
- Load balancing (HA cluster) enhances **Reports** and **FortiView**.
- Preempt: preferred-primary unit gets keepalived priority +120.

## Incoming ports (Ports 7.6 doc)
- HA: **TCP/5199** · log fetch (server side): **TCP/514**
- OFTP from FortiGate / FortiManager: **TCP/514** · syslog: **UDP/514** (or TCP/514)
- FortiManager **management** of FortiAnalyzer: **TCP/541**
- FortiClient (Win/Mac/Linux) TCP/514, Chromebook TCP/8443; FortiAP-S syslog/OFTP/registration TCP/514
- Web Service (SOAP/XML API): **TCP/8080** · JSON API: **TCP/443/80** · DC polling: TCP/445
- FortiPortal API TCP/443/8080; management SSH 22, HTTP 80, HTTPS 443

## Logs, storage, datasets
- Log storage in SQL database; log rolling, deletion; Analytics and Archive logs; data policy + automatic deletion; disk-utilization controls.
- Log encryption; log integrity + secure log transfer (Appendix B).
- **Datasets** (Dataset Reference): a dataset = collection of log messages from monitored devices; **charts are generated from datasets**; predefined or custom (querying the log SQL DB); both can be cloned; macros reference datasets (Macro Reference list from p570).
- FortiView: FortiView dashboard widgets (status, log receive, insert lag, disk I/O, devices, cloud status).

## Exam
10 questions, `eval/questions.jsonl`, ids fca-01..fca-10, tagged `piece: fortianalyzer`.
