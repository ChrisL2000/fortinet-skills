---
name: fortinet-policy
version: 1.1.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet policy: firewall policy, NAT, CGNAT, carrier"
metadata:
  hermes:
    piece: policy
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 7/92 questions tagged piece=policy
    piece_card: /home/chrismok/fortinet-corpus/pieces/policy/PIECE.md
    tags: [fortios, policy, nat, cgnat, ippool, carrier]
---

# FortiNet policy piece

Firewall policy, NAT, central SNAT, IP pools, CGNAT (port-block-allocation), FortiOS Carrier edition. Load `fortinet-platform` first for interface/address/service object creation. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Firewall policy (`config firewall policy`)
```
edit 1
set name "LAN-to-WAN"            # optional in 7.6 (name support added 7.6.x)
set srcintf port2
set dstintf port1
set srcaddr "lan-subnet"
set dstaddr "all"
set schedule "All"
set service "ALL"
set action accept                # [accept|deny|all] (CLI Reference)
set logtraffic enable
set nat enable                   # per-policy NAT on/off
set ippool "mypool"              # optional policy-based NAT
next
end
```
Evaluation is top-down, **first match wins**; unmatched traffic hits the built-in implicit deny (last policy, cannot be deleted). Explicit deny = your own `action deny` policy. Reorder with `move <id> to <position>` (AG example: `config firewall policy` / `move 27 to 30` / `end` — the move subcommand is only available in tables where entry order matters).

Policy-side profile attachments (verified fields): `set dlp-profile <name>` + `set dlp-profile-status` (dlp piece); `set casb-profile <profile>` requires **proxy inspection mode** + ssl-ssh-profile doing deep SSL inspection + `set utm-status enable` (proxy-ztna-casb piece); `set type [explicit-web-proxy|ztna-web-proxy]` + `set explicit-proxy-ssl-inspection-mode` (proxy-ztna-casb piece).

## CGNAT (carrier-grade NAT, CLI Ref 7.6.x)

CGNAT uses a **firewall IP pool of type port-block-allocation (PBA)**:
```
config firewall ippool
    edit <name>
        set type port-block-allocation
        set startip 10.60.0.1
        set endip 10.60.0.10
        set cgn-block-size 64          # 64-4096, default 64 (ports per IP)
        set cgn-port-start 1024
        set cgn-port-end 65535
        set cgn-spa [enable|disable]   # sticky port allocation (block size 1)
        set nat64 [enable|disable]     # IPv6 client -> IPv4 host
        set utilization-alarm-raise <pct>
        set utilization-alarm-clear <pct>
    next
end
```
- `cgn-spa enable` = sticky PBA: one public IP sticks to a client across its concurrent sessions (port-block-size 1 behavior).
- Diagnostics: `diagnose firewall ippool list user` (per-user PBA allocation, CLI Ref p3015), `diagnose firewall ippool list pba`.
- NPU HPE monitoring: `config monitoring npu-hpe` (CLI Ref p1009) + `diagnose npu np7 hpe monitor` (hardware piece).
- Referenced from policy: `set ippool <name>` on the firewall policy (SNAT).
- Architecture + logging: cgnat-architecture-760.pdf / cgnat-logging-760.pdf in the surface `pdfs/`.

## Central SNAT (7.6.x behavior delta, field-verified)

**Since 7.6.1:** Central SNAT policies no longer accept individual SD-WAN members as interfaces (zones / non-SD-WAN interfaces only); members are removed from existing central-snat-map policies on upgrade. Emulate pre-upgrade behavior with `config firewall ippool set associated-interface <SD-WAN member>` + pool in `config firewall central-snat-map`. GUI bug 1107003 (zones hidden on Central SNAT menu) in 7.6.1/7.6.2, fixed 7.6.3.

## FortiOS Carrier edition

- `FortiOS-Carrier-767.pdf` in `fortios-7.6x/pdfs/` — 7.6.x carrier features (CGNAT at scale, NAT64, per-subscriber accounting hooks).
- **FortiOS Carrier 8.0.2** (`fortios-8.0x/text/FortiOS-Carrier-802.txt`, verified): **Carrier-grade GTP firewall** — protection for GTPv0 / GTPv1 / GTPv1-C / GTPv1-U / GTPv2 (GTPv2-C) / GTP' (GTP prime) across GTPv1 and GTPv2 (evolving packet core) networks; **GTP + PFCP protection**; **GTP stateful inspection**; monitoring (GTP activity, GTP signaling dashboard). **FGSP sync extensions (8.0.0):** selectively synchronize ONLY S10 GTP tunnels; disable IP session sync and sync only GTP tunnels.
- Version-check before citing for standard (non-Carrier) FortiOS.

## Retrieval

Root index with filter (pass the right line): `query_root.py "<q>" 12 --product fortios --line 7.6x` (7.6.x) or `--line 8.0x` (8.0.x) (runbook in the router skill `hermes-it-infosec-fw-fortig-fortios-7-6-7`). Per-surface hybrid query: `fortinet-corpus/fortios-7.6x/scripts/query.py` / `fortinet-corpus/fortios-8.0x/scripts/query.py`. Surfaces are version-isolated; sanity-check the `version` field on hits.

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/policy/PIECE.md` + `manifest.json`. Exam slice: 7 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: policy`.
