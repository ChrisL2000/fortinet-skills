---
name: fortinet-ops
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet ops: upgrades, release notes, troubleshooting"
metadata:
  hermes:
    piece: ops
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 22/92 questions tagged piece=ops (incl. community field-report questions)
    piece_card: /home/chrismok/fortinet-corpus/pieces/ops/PIECE.md
    tags: [fortios, operations, upgrade, firmware, troubleshooting, release-notes]
---

# FortiNet ops piece

Firmware upgrades, release-notes reading, troubleshooting methodology, config backup/restore, known-issue lookup. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Upgrade / firmware

- Check current: `get system status` (firmware + build), `get system image list` (images on flash).
- Download: `execute restore image firmware <filename>` (local flash) or `execute firmware download <url>` (TFTP/HTTP/HTTPS). Or GUI: System -> Firmware.
- Verify image integrity: `execute firmware verify <image>` (checksum + model match).
- Upgrade: `execute restore image firmware <image>` (reboots to the new image). HA clusters: `execute ha failover set <host>` first (ha piece), upgrade primary, then secondary; upgrade-mode setting gates 6000F/7000E/7000F behavior (uninterruptible default).
- **PDE gotcha (7.6.1+, platform piece):** `config system global > set private-data-encryption enable` generates a random key on every enable — a config backed up with key A cannot be restored after the key is regenerated. FortiManager 7.6.3+ manages PDE FortiGates but cannot import password-type objects.
- **7.6.8 critical upgrade notices (7.6.8 Release Notes p13-14, verified):** (1) Since 7.6.3, **SSL VPN tunnel mode is replaced by IPsec VPN** (configurable to use TCP port 443) — it is removed from GUI and CLI and settings do NOT upgrade: **migrate SSL VPN tunnel mode to IPsec (Dialup) VPN before upgrading** ("Migration from SSL VPN tunnel mode to IPsec VPN" in the FortiOS 7.6 New Feature guide). (2) **Agentless VPN (formerly SSL VPN web mode) is unavailable on some models** (e.g. FGR-60F and its 2 GB variants) — check the model's RAM before relying on it. (3) **2 GB RAM models** lose most FortiOS proxy-related features plus Security Rating and Security Fabric topology; `cp-accel-mode` default changed to none on 2 GB models.
- Backup/restore: `execute backup config to <tftp|flash|usb>` / `execute restore config from <tftp|flash|usb>`. Config backup includes all `config *` objects; does NOT include images.

## Release-notes reading (methodology)

1. **§"Introduction and supported models"** — exact model list for this version (platform piece). Any model NOT in the list = unsupported for this version.
2. **§"New features"** — version-specific additions (NPU SCTP offload in 7.6.8, CLI additions in 8.0.0, etc.).
3. **§"Resolved issues"** — bugs fixed in this version (search by bug ID).
4. **§"Known issues"** — open bugs (workaround + bug ID). Always cite the bug ID when referencing a known issue.
5. **§"Upgrading / downgrading"** — upgrade paths, pre-upgrade checks, migration notes (SSL VPN tunnel mode -> IPsec VPN in 7.6.3+).
6. **§"Special notices"** — 2GB-RAM model limitations, security notices, etc.

## Troubleshooting (methodology, verified)

1. **`get system status`** — firmware, uptime, HA role, sessions, CPU/mem.
2. **`diagnose system performance summary`** — throughput, session table, CPU per process.
3. **`diagnose debug application <app> -1`** + `diagnose debug enable` + `diagnose debug disable` — live debug (ALWAYS disable after; filter to one IP first: `diagnose vpn ike log filter rem-addr4 <ip>`).
4. **`diagnose sniffer packet <if> '<filter>' 4 0 l`** — packet capture (no tcpdump in 7.6.x); **stop with Ctrl+C**.
5. **`get log filter category ...`** — slice logs by category (logging piece).
6. **Known-issue lookup** — search the version's release notes §"Known issues" by symptom + bug ID.
- **`diagnose vpn tunnel list` key fields** (IPsec troubleshooting): `name`, `ver` (IKEv1/v2), `serial`, `local->remote`, `tun_id`, `bound_if`, `lgwy` (gateway), `proxyid_num`, `child_num`, `refcnt`, `ilast`/`olast` (in/out last-active), `ad` (ad-hoc), `stat rxp/txp/rxb/txb` (packet/byte counters), `npu` flag, DPD mode.

## Community field reports (KB questions)

The corpus includes FortiNet Community knowledge-base field reports (retrieval `doc=community`). Their standard structure — extract ALL of these when answering field-report questions, cite as (community KB):
- **Affected models + versions** (and explicitly UNAFFECTED models/ports/paths), **root cause** (often an internal driver/firmware issue, not operator error), **bug ID**, **workarounds**, **special/STS builds** (e.g. 8767/8768, obtained via TAC ticket), **upgrade paths** (e.g. 7.6.7 GA -> STS build 8767 -> 7.6.8 GA), and **FortiManager** as an alternative upgrade path.
- Example verified cases: 1800F/1801F 1GbE SFP ports 17–20 not forwarding after 7.6.8 (bug 1353422; move to ports 21–24 on GA 3744); 30/31G firmware signature-verification failure on 7.6.7->7.6.8 (STS build 8767 first; `inflate() error: -3` = out of RAM, set IPS engine-count to 1 and reboot); **memory conserve mode after 7.6.8 upgrade** — cause: default **IPSEngine 7.01200** shipped with 7.6.8; FortiGate with an IPS profile configured enters conserve mode (ipsengine process eating ~4.9 GB+). Diagnose: `diagnose sys top-mem 20` (shows ipsengine top memory consumers), `diagnose debug crashlog read | grep conserve`, `get sys perf status` (total usage). Resolve: **IPSEngine 7.01204** — log a support ticket to obtain the fixed IPSEngine when an IPS profile is used.
- Release-notes questions: the 7.6.7 supported-model list is in 7.6.7 RN §"Introduction and supported models" (p.8) — FG-30G through FG-7000F incl. all 200E–3980E/5001E + hyperscale, FortiWiFi FWF-*, Rugged FGR-*, FFW-*, VM/ARM64 images; no 100E/1000E/3000E/4000E series.

## Deep reference

`references/ops-deep.md` carries the verified detail: RN structure (special notices, CLI/default-behavior/default-value/table-size changes), the full 7.6.7 known-issues set with workarounds (1306049 blank GUI → `config system global > set admin-http-rate-limit-max-requests 0`; 1353040 370xF/480xF interfaces down after upgrade; 1347610 3xG TFTP install BIOS fix), the troubleshooting playbooks, and `diagnose sys session list` output fields.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## References (load on demand)

- `references/ops-deep.md` — upgrade procedure (HA + standalone), firmware verify, backup/restore, release-notes reading methodology, troubleshooting command set, known-issue lookup, PDE gotcha, 2GB-RAM model check.

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/ops/PIECE.md` + `manifest.json`. Exam slice: 5 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: ops`.
