---
name: fortinet-wireless
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet wireless: FortiGate WLC, VAP/WTP, FortiAP"
metadata:
  hermes:
    piece: wireless
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 2/92 questions tagged piece=wireless
    piece_card: /home/chrismok/fortinet-corpus/pieces/wireless/PIECE.md
    tags: [fortios, wireless, wtp, vap, fortiap, wlc]
---

# FortiNet wireless piece

FortiGate as Wireless LAN Controller: WTPs (wireless termination points), VAPs, SSIDs, profiles, FortiAP adoption, WLC vs wireless-controller mode. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Core object — `config wireless-controller` (7.6.8 CLI Ref p2686+, verified)

FortiGate as WLC: `config wireless-controller` with sub-objects: `vap`, `wtp`, `wtp-profile`, `wtp-group`, `wids-profile`, `wag-profile`, `vap-group`, `mpsk-profile`, `ssid-policy`, `qos-profile`, `nac-profile`, `lw-profile`, `region`, `setting`, `timers`, `snmp`, `syslog-profile`, `log`, `inter-controller`, `hotspot20`.

- `vap` — `edit <vap>` / `set name`, `set ssid`, `set vdom`, `set vlan-id`, `set wtp-profile <prof>`, `set mpsk-profile <prof>` (per-user PSK), `set auth [radius|usergroup]`, `set broadcast-ssid [enable|disable]`, `set 80211k` / `set 80211v [enable|disable]`, `set access-control-list {string}` (verified fields; full list in the CLI Ref).
- `wtp` — `edit <wtp>` / `set name`, `set status [enable|disable]` (adoption state), `set model <AP-model>`, `set vaps <vap-list>`, `set wtp-profile <prof>`, `set country-code <ISO>`.
- `wtp-profile` — `config wireless-controller > config wtp-profile > edit <prof>`: per-AP-group settings (7.6.8 CLI Ref p203608+, verified): `set ap-country [--|AF|...]`, `set ap-handoff [enable|disable]` (AP-to-AP handoff control — keep it in any 4-setting answer), `set admin-auth-tacacs+ {string}`, `set admin-restrict-local [enable|disable]`, `set apcfg-auto-cert [enable|disable]` + `apcfg-auto-cert-auto-regen-days {integer}`, `apcfg-auto-cert-crypto-algo`, `apcfg-auto-cert-enroll-protocol [none|est|scep]` (+ est-*/scep-* subfields).
- Adoption: the WTP object appears when the AP authenticates to the WLC; verify with `get wireless-controller wtp`.
- **Diagnostics (verified):** `diagnose wireless status` (WTP state), `diagnose sys wireless iwconfig <name> <cmd> <value1> <value2> <value3>` — per-AP radio/interface diagnostics (7.6.8 CLI Ref p3609), `diagnose wireless-controller status` (WLC status).
- 8.0.2: `config wireless-controller > config setting > set admin-auth-tacacs+ [enable|disable]` (TACACS+ admin auth for WLC — new in 8.0.2).
- 8.0.0 AP deltas (release notes): AP111/AP113/AP121/AP321/AP421/AP522 added; FortiLink switch with split-interface (uplink) must have LLDP enabled.
- 7.6.7/7.6.8 new AP support (release notes): 7.6.7 — AP431/AP433/AP435 (WiFi 7), AP236/AP423/AP552 updates, AP532; 7.6.8 — AP411 + AP431/AP435 + AP231/AP433/AP532 updates.

## AP models (7.6.7/7.6.8, verified in release notes)

- **7.6.7 new AP support:** AP431 (WiFi 7 2.5 GHz), AP433, AP435 (WiFi 7); AP236/AP423/AP552 firmware updates; AP532 (WiFi 7, 7.6.7+).
- **7.6.8 new AP support:** AP411, AP431 (WiFi 7 2.5 GHz), AP435 (WiFi 7); plus AP231/AP433/AP532 updates; WiFi-Controller feature deltas in 8.0.0/8.0.2 notes (see 8.0.2 FortiLink split-interface LLDP notice in the platform piece).

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/wireless/PIECE.md` + `manifest.json`. Exam slice: 4 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: wireless`.
