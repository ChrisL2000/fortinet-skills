# Corpus card — FortiOS 7.6.x train

Backs the skill family `hermes-it-infosec-fw-fortig-fortios-7-6-7` (v4.0.0
router + 12 `fortinet/*` piece skills), specifically its source-verified
core. Built 2026-10/11 on the zeppo host; all data has never left the host.

## Target environments

- FortiOS 7.6.x deployments (7.6.0 → 7.6.8 GA): **full coverage**
- FortiGate FG-6000F / FG-7000E / FG-7000F hyperscale (7.6.7): covered
- FortiOS 8.0.x (8.0.0, 8.0.2): **covered** — full AG + CLI Reference + Log
  Reference + release-notes/new-features sets are in this build
- 7.2.x / 7.4.x lines: NOT present
- Other FortiNet products: only the 7.6-line deployment briefs listed below

Version discipline: this build mixes 7.6.x and 8.0.x docs. Version-check
every retrieval result (chunks carry doc + page anchors) before citing it
for a specific environment's version.

## Surface areas (what this corpus answers)

- FortiOS CLI: full CLI References for 7.6.7, 7.6.8, 8.0.0, 8.0.2
- FortiOS REST API v2: Admin Guide §REST API (api-user, cmdb/monitor, query params)
- Domain topics: SD-WAN, IPsec/SSL VPN, VDOM, HA (FGCP/FGSP/VRRP),
  NPU/hardware acceleration/Parallel Path Processing, CASB (inline), ZTNA,
  explicit web proxy, wireless controller, SNMP, FSSO, CGNAT, DLP,
  logging/LogIDs, routing, policy
- Admin/ops: 7.6.7/7.6.8/8.0.x Administration Guides, release notes,
  new features, upgrade + SSL→IPsec migration, troubleshooting cheat sheets,
  supported-RFC list, carrier guide (7.6.7)
- Field knowledge: 174 community.fortinet.com reports — field intel,
  never overrides official behavior

## Adjacent-product docs (7.6 line, in this build)

- FortiWeb: `Architecture_Guide-7.6-Client_Web_Security`,
  `Deployment_Guide-7.6-NGFW_Web_Security`
- DLP: `DLP_7.6.0_Deployment_Brief`
- CASB/ZTNA: `Inline_CASB_Deploy_Brief`, `ZTNA_for_Web_Applications-7.6.3`,
  `FortiOS-7.6-ZTNA_Reference_Guide`, `FortiOS-8.0-ZTNA_Reference_Guide`
- SD-WAN + FortiManager: `SD-WAN_with_FOS_FMG-7.6.x-New_Features`,
  `SD-WAN_with_FOS_FMG-8.0.x-New_Features`
- 5G: `5G_Device_Modem--Operator's_Manual` (130 chunks)
- Historical: `FortiGate-7.0.0-Firmware_Upgrade_Guide` (36 chunks, 7.0.x only)

## Inventory

- `pdfs/` — 54 official PDFs (~960MB)
- `text/` — 53 extracted texts with `<<<PAGE n>>>` + `<<<H1|config path>>>` markers
- `chunks.jsonl` — 73,552 chunks (text + doc + page anchors)
- `kb/chroma.sqlite3` — 75,543 vectors: MiniLM-L6-v2 (384-d), collection
  `fortios76` = 73,552 main + 1,089 field + 902 (HA 8.0.2 incremental append)
- `logs/inverted_index.json` — keyword index (auto-rebuilds from chunks.jsonl)
- `field/` — 174 field reports (178 page files + topics.jsonl)
- `eval/` — 92-question exam (`questions.jsonl`, key field `kp`), 70 answers,
  score history. Best round: R2 = 76.1% (70/92), 2026-11-01
- `scripts/` — 13 pipeline scripts (identical copies in the skill's `scripts/`)

Largest chunk counts: 8.0.2 AG 9,792 · 8.0.0 AG 9,329 · 7.6.8 AG 8,527 ·
7.6.7 AG 8,504 · 8.0.2 CLI Ref 6,567 · 7.6.8 CLI Ref 6,192 · 7.6.7 CLI Ref
6,179 · Log Refs 2,397-2,435 · New Features 1,690-1,853 · HW acceleration
859-887 · 7000E 451 · 7000F 430 · SD-WAN+FMC/FM new features 393 ·
hyperscale guide 393 · 6000F 362 · CGNAT arch 271.

## How to query

```
docker run -d --name <tmp> --mount type=bind,src=/home/chrismok/fortinet-corpus/fortios-7.6x,dst=/work zeppo-rag:cli sleep infinity
docker exec <tmp> python /work/scripts/query.py "<question>"    # hybrid vector+keyword, k=12
docker exec <tmp> python /work/scripts/probe.py "<term>"        # grep across text/
docker exec <tmp> python /work/scripts/ctx.py "<term>" <file>   # context snippets
# kill the container when done — embeddings are CPU-only by design
```

## What's missing (extension candidates)

- Future 7.6.x minors (7.6.9+) and 8.0.x point releases as released
- 7.4.x and 7.2.x lines
- Full product doc sets: FortiManager, FortiAnalyzer, FortiAuthenticator,
  FortiNAC, FortiMail, FortiWeb (beyond the 7.6 briefs), FortiSIEM,
  FortiClient, FortiSandbox, other hardware lines

## How to extend this build (or add a sibling surface)

Follow the skill's **Self-improvement** section
(`/home/chrismok/.hermes/skills/hermes-it-infosec-fw-fortig-fortios-7-6-7/SKILL.md`):
fetch official PDFs → extract (APPEND to chunks.jsonl) → embed new chunks
(CPU-only MiniLM-L6-v2) → `rm logs/inverted_index.json` → re-exam
(≥90% for two consecutive rounds) → fold verified content into the skill →
**recompile the root index** (`compile_root.py` — the root is derived data).

Surface rule: docs belonging to this surface (FortiOS 7.6.x/8.0.x train +
its hardware) are APPENDed here. A brand-new product or version line gets a
NEW sibling directory under `/home/chrismok/fortinet-corpus/` with its own
`CORPUS.md` card.

## Provenance

- Official PDFs: docs.fortinet.com / Fortinet S3 (`scripts/fetch_pdfs.py`,
  `fetch_phase2.py`). Known gotcha: some 8.0.0 S3 objects return 403 → use
  the 8.0.2 variant of the same doc.
- Field reports: community.fortinet.com (`scripts/crawl_field.py`,
  `crawl_field2.py`).
- Exam: 2026-10 phase 1 (54 questions) + 2026-11 phase 2 (+38 → 92).
- File ownership: files written by the container run as root (e.g.
  `chunks.jsonl`); the directories are chrismok-owned, so as chrismok you
  can replace a root-owned file (recreate it) but not edit it in place.
