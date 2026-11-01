---
name: fortinet-sdpwan
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet SD-WAN: steering, SLA, health checks, MSSP"
metadata:
  hermes:
    piece: sdpwan
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 6/92 questions tagged piece=sdpwan
    piece_card: /home/chrismok/fortinet-corpus/pieces/sdpwan/PIECE.md
    tags: [fortios, sdwan, sla, steering, mssp]
---

# FortiNet SD-WAN piece

SD-WAN objects, SLA, steering, health checks, zones, MSSP/SD-Branch architecture, FortiManager orchestration. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Objects (CLI Ref)

- Top level (`config system sdwan`): `set interface <members>`, `set gateway <name1>, <name2>`, `set load-balance-mode [source-ip-based|weight-based|usage-based|source-dest-ip-based|measured-volume-based]` (algorithm for balancing Internet traffic across SD-WAN members — a top-level setting in 7.6.7, NOT per-service), `config members` (per-member cost/priority).
- **SD-WAN rules are in `config service`** (not `config rules`). A service matches src/dst address, ports, protocol, DSCP, input device/zone and selects members. Key fields: `set priority-members <seq-num1>, <seq-num2>, ...` (member sequence numbers in priority order), `set minimum-sla-meet-members {integer}`, `set hold-down-time {integer}` (seconds to keep using a member that dropped below SLA), `set tie-break [zone|cfg-order|...]` (tie-breaker when members are equivalent), `set load-balance [enable|disable]`, `set hash-mode [round-robin|source-ip-based|...]` (per-flow hashing when load balancing is on), `set link-cost-factor` / `set link-cost-threshold`, `set quality-link [enable|disable]`, `set sla-stickiness`.
- **Internet service matching (7.6.7 p1964-1965):** `set internet-service [enable|disable]` (enable Internet Service matching), `set internet-service-name <name1>, <name2>, ...` (named Internet Services), `set internet-service-custom <list>` + `set internet-service-custom-group <list>` (custom services), `set internet-service-fortiguard <name1>, <name2>, ...` (FortiGuard Internet Service Database entries), `set internet-service-group <list>`, `set internet-service-app-ctrl <id1>, <id2>, ...` + `set internet-service-app-ctrl-category` / `set internet-service-app-ctrl-group` (application-control extension).
- **Zones (`config zone` under `config system sdwan`, 7.6.7):** group services into a zone; zone fields include `set minimum-sla-meet-members`, `set service-sla-tie-break [cfg-order|fib-best-match|...]` (tie-breaker applied within the zone), `set advpn-select [enable|disable]` (allow Advanced VPN tunnels in the zone). A service references its zone with `set priority-zone <name>` and `set zone-mode [enable|disable]`.
- Health checks: `config health-check` (`set detect-mode [active|passive]`, `set server`, `set protocol [ping|http|...]`, `set interval` — **unit is MILLISECONDS** (20-3600000; 10 s = 10000), `set probe-count`, `set probe-timeout`, `set failtime`, `set recoverytime`, `set latency-weight` / `set packet-loss-weight`, `set fortiguard [enable|disable]`, nested `config sla` with `set latency-threshold` / `set packetloss-threshold`).
- Monitor API: `GET /api/v2/monitor/virtual-wan/{interface-log|sla-log|health-check}`.

## Architecture docs in the corpus

- SD-WAN-7.6-Architecture_for_MSSPs.pdf
- SD-WAN-7.6-Deploying_Secure_SD-WAN_and_SD-Branch_for_MSSPs.pdf
- SD-WAN-7.6-Service_Bundle_Example_Guide.pdf
- SD-WAN_SD-Branch-7.6-Architecture_for_Enterprise.pdf
- Secure_SD-Branch-7.6-Architecture_Guide.pdf (also the FGSP session-sync use case — ha piece)
- SD-WAN-8.0-Deploying_Secure_SD-WAN_and_SD-Branch_for_MSSPs.pdf
- SD-WAN_SD-Branch-8.0-Architecture_for_MSSPs.pdf
- SD-WAN_with_FOS_FMG-7.6.x-New_Features.pdf / -8.0.x (FortiManager orchestration)

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/sdpwan/PIECE.md` + `manifest.json`. Exam slice: 6 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: sdpwan`.
