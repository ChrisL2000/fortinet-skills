---
name: fortinet-fortiweb
description: "FortiWeb 7.6x: operation modes, scan seq, HA, WAF, FWM."
version: 1.0.0
---

# FortiWeb (piece: fortiweb)

Surface: FortiWeb 7.6.10 (+ FWM 7.6.0, troubleshooting, script ref). Corpus: `fortinet-corpus/fortiweb-7.6x` (8 docs, 3,339 pages, 6,850 chunks, collection `fw76`). All facts below verified against the extracted text.

## When to use
- ANY question about FortiWeb / FortiWeb Manager (WAF, reverse proxy, TTP/TI, WCCP, FortiWeb HA, bot mitigation, API protection, DoS protection, server policies, FWM device mgmt).
- NOT for: FortiGate (FortiOS pieces), FortiManager (fortinet-fortimanager), FortiAnalyzer (fortinet-fortianalyzer).
- Caveat: `fortiweb-trouble-shooting.pdf` cover is a mislabeled FortiNet template artifact; content is the genuine FortiWeb troubleshooting guide (247p, verified).

## Doc set (8 PDFs, 3,339 pages)
- FortiWeb Admin Guide 7.6.10 (1,654p), CLI Reference 7.6.10 (798p), Log Message Reference 7.6.10 (516p), Release Notes 7.6.10 (26p)
- FortiWeb Manager 7.6.0 Admin Guide (60p), Troubleshooting (247p), Script Reference (27p), FWM Release Notes 7.6.0 (11p)

## Operation modes
- **Reverse Proxy**: full WAF feature set; FortiWeb is the server's proxy (dest IP changes; virtual servers).
- **Transparent modes** — True Transparent Proxy (TTP) and Transparent Inspection (TI): traffic hits FortiWeb's L2 bridge interface, destination IP unchanged, server responds directly with its original IP.
  - TTP: full security features, can modify traffic (headers, error pages), decrypts AND re-encrypts HTTPS, TLS 1.0-1.3, user authentication.
  - TI: limited features, does NOT modify traffic, decrypts but does not re-encrypt HTTPS, no TLS 1.3, no user auth.
- **WCCP** (Web Cache Content Protocol), **Offline Protection**.
- High Volume Active-Active HA requires Reverse Proxy mode.

## Sequence of scans (Admin Guide p183)
- Protection profile scans run in table order, top→bottom; **disabled scans are skipped**.
- Early entries: Add X-Forwarded-For/X-Real-IP/X-Forwarded-Proto → **IP List** → **TCP Connection Number Limit** (TCP flood prevention) → IP Reputation → Quarantined source IPs → Known Bots → Geo IP → … (DoS, signature, ML, DLP, …).
- **Allow-listed source IP → subsequent checks skipped.**
- Performance guidance: block with the earliest possible / least memory-consuming technique (e.g. block via IP List block list instead of syntax-based SQL/XSS).
- Whole-packet scans (e.g. File Security) may actually run later than listed.

## WAF features (OWASP Top 10 + API + bot)
- Signature Detection (signature library + Custom Signature regexes), **ML-based Anomaly Detection** (two-layer: 1) Hidden Markov Model (HMM) models normal behavior, flags deviations; 2) pre-built continuously updated threat models trained on thousands of real attack samples verify anomalies), DLP, Syntax-based SQL/XSS Injection Detection, Input Validation, Protocol Constraints, Access Control, IP Protection, URL Encryption, Link Cloaking, CSRF Protection.
- ML svm-type: **standard** (default; disables SVM models prone to false positives) vs **extended** (all models).

## HA
- Modes: **Active-Passive**, **Standard Active-Active**, **High Volume Active-Active**.
- Heartbeat: multicast **239.0.0.1 port 6065**, hard-coded HA IPs (not modifiable); switches must allow L2 frames on heartbeat interfaces.
- **Heartbeat timeout = Detection Interval × Heartbeat Lost Threshold**; failover triggered when heartbeat or monitored port down exceeds it.
- Failover: standby assumes the primary's **virtual MAC** (e.g. 00:09:0F:A0:CC:02 format in AP/standard AA) and broadcasts ARP/NS; then scans traffic.
- **High Volume AA**: Reverse Proxy mode only, **up to 8 units**, no central primary — each member gets unique VIPs and processes traffic directly; designated backup assumes failed VIPs.
- Managing secondary nodes (AP/standard AA): need a **Reserved Management Interface** + HA static/policy route (otherwise interface settings sync to all members).
- Don't use 169.254.0.0/16 on regular interfaces in HA (used by HA heartbeat/sync).

## Sizing (FortiWeb-VM)
- 10 vNICs. Server policies by vRAM: <64 GB → 20 for first 1 GB + 15 per extra GB (max 256); ≥64 GB → up to **1024**. vRAM = MemTotal of `diagnose hardware mem list`, KB floored to GB.
- Max values table in Admin Guide appendix (e.g. Bot Mitigation Policy 256, Known Bots 256).

## FortiWeb Manager (FWM 7.6.0)
- Central mgmt of multiple FortiWeb appliances: device groups, add/upgrade devices, FortiWeb-VM license apply/reclaim, scheduled jobs (with status notifications), device monitoring, log viewing, API proxy.

## CLI / troubleshooting essentials
- `config log traffic-log / set disk-log enable` (needs w/rw on loggrp area) — disk traffic logging risks premature disk failure at high volume; verify `get log traffic-log`; sample `diagnose log tlog show`.
- `diagnose debug nowaf`, `diagnose debug flow filter module-bypass-info` (module bypass diagnostics); PCRE high-CPU troubleshooting via monitoring CLI commands.
- WCCP web cache: enable in Feature Visibility; enabling on a server policy auto-creates the cache policy (Application Delivery > Caching); a web cache rule is REQUIRED; rules match in order, first match wins.
- Troubleshooting guide: baseline first; server-policy connectivity; ARP/routing checks; packet traces; proxyd debugging (incl. `proxyd asan` notes); site-publish/caching/Lua FAQ sections.

## Exam
10 questions, `eval/questions.jsonl`, ids fw-01..fw-10, tagged `piece: fortiweb`.
