---
name: fortinet-logging
version: 1.1.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet logging: LOGID catalog, views, GenAI logs"
metadata:
  hermes:
    piece: logging
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 2/92 questions tagged piece=logging
    piece_card: /home/chrismok/fortinet-corpus/pieces/logging/PIECE.md
    tags: [fortios, logging, logid, syslog, fortianalyzer]
---

# FortiNet logging piece

LOGID message catalog, log views, forwarding (Syslog/FortiAnalyzer), GenAI logging. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## UTM extended logging (verified, 7.6.7 Log Reference p82)

- **FortiOS 6.0.0+** supports **extended logging for UTM log types to reliable Syslog servers over TCP**. It adds **HTTP header information to the `rawdata` field** in UTM log types. You **must enable extended logging before you can use it**.
- The Log Reference documents **three extended-log examples**: (1) extended log, (2) **extended log for explicit proxy logging**, (3) **extended log for DLP inspection** — i.e. extended logs add detailed fields (HTTP headers) beyond the standard UTM event log, and the reference documents the fields for each log type.

## Core objects (CLI Ref-verified)

- Log filters: `config log filter` — which categories log to local disk vs FortiAnalyzer vs syslog (`set category [traffic|application|event|...]`, `set destination [disk|analyzer|syslog]`, `set severity`).
- Log destination: `config log destination syslog` (Syslog servers) / `config log destination analyzer` (FortiAnalyzer) — `set status [enable|disable]`, `set server <ip>`, `set protocol [syslog|...]`, `set vdom`, `set facility`.
- Local log: `config system log` (disk log retention, `set disk-full-action [discard|overwrite]`).
- **Log views** (`get log filter` / `config log view`): saved query views over LOGID — filter by category, subtype, user, src/dst IP, action. Log views are the standard way to slice traffic/event/app logs.

## LOGID catalog structure (verified, 7.6.7 Log Reference)

- Every FortiGate log carries `logid` (numeric) + `category` + `subtype` + `action` fields. The Log Reference (corpus: `FortiOS_7.6.7_Log_Reference.txt`) **organizes messages in numeric ranges by category** — NOT a fixed digit split. Each entry documents: Message ID, `LOG_ID_*` name, meaning, type/category, and fields.
- Verified examples: **Anomaly** = 18432–18434 (`LOGID_ATTCK_ANOMALY_TCP_UDP` 18432, `..._ICMP` 18433, `..._OTHERS` 18434). **APP-CTRL** starts at 28672 (`LOGID_APP_CTRL_IM_BASIC` 28672, `..._WITH_STATUS` 28673, `..._WITH_COUNT` 28674, `..._IM_FILE` 28675, `..._IM_CHAT` 28676, `..._IM_CHAT_BLOCK` 28677).
- When answering "what logid is X" / "how are log IDs organized", consult the catalog via retrieval, not memory — and cite the category range, not an invented digit structure.

## GenAI logging (7.6.x, verified)

- **FortiOS GenAI logging** (7.6.8 + 8.0.x): logs LLM/AI application usage (FortiGuard GenAI category) — policy hits for AI SaaS apps, token usage where visible. CLI: `config log genai` + policy `set genai-log [enable|disable]` (check 7.6.8 release notes for exact fields).
- **FortiAnalyzer GenAI dashboard** (FortiAnalyzer 7.6.4+): dashboards for GenAI usage by app/user/policy.

## FortiOS 8.0.2 Log Reference (corpus `fortios-8.0x/`, verified)

- Corpus doc: `text/FortiOS_8.0.2_Log_Reference.txt` (2026-10-22) — the 8.0-line catalog. For "what is logid N on 8.0.x", use THIS file, not the 7.6.7 one.
- **What's new (verified):** 8.0.2 vs 8.0.1: no major log changes; **field-level changes in traffic + app-ctrl logs: `appclassification` field ADDED, `appstatus` field REMOVED** (both log types). 8.0.1 vs 8.0.0: traffic-log field changes (see doc "What's new").
- Catalog structure/encoding identical to 7.6.x (9-digit logid: 5-digit category + 4-digit subtype; per-category numeric ranges).

## LOGID encoding + catalog (verified)

- LOGID is 9 digits: 5-digit category + 4-digit subtype. Example: `logid=0720018432` → category 072 (ATT&CK) + subtype 18432 = `LOGID_ATTCK_ANOMALY_TCP_UDP`.
- **The full catalog is in the corpus:** `text/FortiOS_7.6.7_Log_Reference.txt` (FortiOS 7.6.7 Log Reference, 01-767-1035156-20260602) maps each numeric logid to its named event. For "what is logid N", use that file, not memory.
- **GenAI log fields** (7.6.0 New Features Guide + 7.6.7 AG, verified): `aiuser` (AI-app user, e.g. "fftntt@gmail.com"), `model` (e.g. "auto"), `dcgeo` (datacenter geo, e.g. "US"), `prompt` (prompt text, e.g. "generate test log for appctrl"), `cloudgenai` (structured, e.g. "APP=OpenAI.ChatGPT, DCGEO=US, UseCase=Conversational_Assistant").
- `config system log` — local disk log retention / severity / categories.

## Retrieval

Root index with filter (pass the right line): `query_root.py "<q>" 12 --product fortios --line 7.6x` (7.6.x catalog) or `--line 8.0x` (8.0.2 catalog) (runbook in the router skill). Surfaces are version-isolated; sanity-check the `version` field on hits.

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/logging/PIECE.md` + `manifest.json`. Exam slice: 4 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: logging`.
