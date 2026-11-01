---
name: fortinet-ha
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet HA: FGCP, FGSP, VRRP, failover, link monitors"
metadata:
  hermes:
    piece: ha
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 5/92 questions tagged piece=ha
    piece_card: /home/chrismok/fortinet-corpus/pieces/ha/PIECE.md
    tags: [fortios, ha, fgcp, fgsp, vrrp, failover, clustering]
---

# FortiNet HA piece

FortiGate HA: FGCP (config sync), FGSP (session sync), VRRP, failover/upgrade modes, link/state monitors. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Must-know (7.6.x deltas, verified)

- **FG-6000F/7000E/7000F (hyperscale): default upgrade mode = uninterrupted** (was simultaneous). In uninterrupted mode the secondary is NOT a standby — it takes over the session load before being upgraded.
- **CLI prompt now shows the HA role**: `FortiGate(Secondary) (global) #` — fixed-prompt automation (regex on `FortiGate (global) #`) breaks; use the role-aware form or `get system ha status`.
- **7.6.0 change:** `set config-sync-objects` no longer supports `config user local` — user accounts sync via `set config-sync user-account` (the separate user-account-sync object).

## FGCP / FGSP / VRRP

- FGCP = config sync across the cluster (`config system ha > set config-sync-objects ...`). FGSP = session sync (per-interface `set session-sync [enable|disable]` on the FGSP port; `config system ha config vdom-sync`).
- VRRP: per-interface `config system interface > edit <intf> > config vrrp > edit <vid> > set priority` (0-254, higher wins), `set preemption`, `set gratuitous-arp-interval` / `set gratuitous-arp-count`.
- Verify: `get system ha status` (master/primary roles, sync status), `get system ha status full`.

## Links/monitors

- Link monitors: `config system ha-link-monitor` — per-link `set interface`, `set protocol [ping|http|...]`, `set server`, `set failure-threshold` / `set recovery-threshold`; `set weight` for weighted link scoring.
- State monitors: `config system ha-state-monitor` (CPU/memory/session thresholds). The **link-monitor + state-monitor** combination is what drives automatic failover scoring.

## Failover / upgrade

- `set mode [fgcp|ha-cluster]`, `set fb-addr <fgsp-port>`, `set priority` (0-254), `set override [enable|disable]`, `set per-vdom-priority [enable|disable]`, `set heartbeat [failover|sync|both]`, `set vrrp [enable|disable]`, `set master-priority <list>`.
- **`set hbdev <intf> <weight> [<intf> <weight> ...]`** — heartbeat interfaces with per-interface weights (AG examples: `set hbdev ha1 200 ha2 100`, `set hbdev "port3" 50 "port5" 100`). `set backup-hbdev <intf-list>` for backup heartbeat path. Tuning: `set hb-interval`, `set hb-lost-threshold`.
- **`set monitor <intf> <weight> [<intf> <weight> ...]`** — monitored (state-sync) interfaces with weights (CLI Ref: `set monitor <name1>, <name2>, ...` with per-interface weights; e.g. `set monitor port1 1`).
- Canonical minimal FGCP a-p example (7.6.7 AG):
  ```
  config system ha
      set mode a-p
      set group-id 1
      set priority 100
      set password <shared-secret>
      set hbdev port10 1
      set monitor port1 1
  end
  ```
- Upgrades: `execute ha failover set <host>` (manual failover), `execute ha failover unset`, `execute ha failover status`. Upgrade-mode setting (`set upgrade-mode [simultaneous|uninterruptible]`) gates the 6000F/7000E/7000F behavior above.

## FGSP in SD-Branch (architecture doc)

Secure_SD-Branch-7.6-Architecture_Guide.pdf documents an SD-Branch use case where an edge FortiGate forwards sessions to a second FortiGate via FGSP for centralized inspection — the FGSP link must traverse a trusted path; sessions appear on both units. Version-check the doc (7.6 architecture) before applying to other lines.

## References (load on demand)

- `references/ha-deep.md` — verified HA object field lists (system ha, ha-link-monitor, ha-state-monitor, vrrp, session-sync), FGCP/FGSP/VRRP semantics, upgrade modes, 7.6.x deltas, debug commands.

## Full field list + FGSP standalone cluster

- `references/ha-deep.md` holds the verified full `config system ha` field list (mode [standalone|a-p|a-a], group-id, override, override-wait-time, priority, per-vdom-priority, heartbeat, monitor, fb-addr, vrrp, session-pickup, key, link-monitor, pingserver-failover-threshold, upgrade-mode), the primary-unit selection rules (override > priority > serial), and the FGSP standalone-cluster pattern: two standalone units syncing sessions over FGSP behind an external load balancer (FGSP syncs IPv4/IPv6 TCP, SCTP, UDP, ICMP, expectation, NAT sessions; the LB performs failover).
- The 7.6.x must-know above (uninterrupted upgrade default on 6000F/7000E/7000F; role-aware CLI prompt; 7.6.0 user-account sync split) is the exam-relevant delta.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill `hermes-it-infosec-fw-fortig-fortios-7-6-7`). Version-check hits (surface contains 8.0.x docs too).
