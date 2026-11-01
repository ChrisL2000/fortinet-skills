---
name: fortinet-hardware
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet hardware: hyperscale FG, NPU, PPP pipeline"
metadata:
  hermes:
    piece: hardware
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 5/92 questions tagged piece=hardware
    piece_card: /home/chrismok/fortinet-corpus/pieces/hardware/PIECE.md
    tags: [fortios, hardware, hyperscale, npu, 6000f, 7000e, 7000f]
---

# FortiNet hardware piece

Hyperscale FortiGate (FG-6000F/7000E/7000F), NPU (ASIC) offload, PPP pipeline, hardware diagnostics. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Must-know (7.6.x, verified)

- **NP7 (7.6.7):** dedicated host queue for control-plane traffic + `dedicated-management-cpu` on by default. Regular host queues **drop at DSWH** under extreme load instead of backpressure — control-plane traffic now has its own queue. `config system npu > set vlan-accounting disable` stops VLAN-lookup message storms (7.6.7 fix).
- **20xG models (7.6.7, bug 1288059):** after factory reset or out-of-box init, port1/port2 are removed from the virtual switch and configured for DHCP for Zero Touch Provisioning (ZTP). Re-add to the virtual switch if ZTP is not used.
- **Hyperscale FG-6000F/7000E/7000F:** own support/limitations section in every release notes doc — check the specific version's RN §"Supported models" for the exact list + limitations (NPU virtual-link, multicast-loop warnings, VRRP behavior).
- **NPU virtual-link models (6000F/7000E/7000F):** `config system npu` + `diagnose npu np7` — NPU ports are virtual links between the CPU and the NPU. Multicast-loop warning: do NOT bridge NPU ports into the same VLAN as CPU-side ports without NPU multicast config (see 7.6.7 AG §NPU).
- **NPU SCTP offload (7.6.8, SoC4/SoC5):** `config system npu set sctp-offload [enable|disable]` + `set sctp-ctrlpkt-to-host [enable|disable]` (SCTP control packets to host). 7.6.8 also adds `config system npu config fp-anomaly set ipv4-option {allow|trap-to-host}` (IPv4 option handling on the NPU).
- **NPU HPE monitoring (7.6.x):** `config monitoring npu-hpe` (CLI Ref p1009) + `diagnose npu np7 hpe monitor` — per-NPU port HPE (hardware processing engine) stats.
- **IPsec NPU offload:** `config vpn ipsec phase1-interface > set npu-offload [enable|disable]` (vpn piece) — verify with `diagnose npu port-list` + `diagnose vpn tunnel list` `npu_flag`.

## NPU CLI objects (7.6.7/7.6.8, verified)

The objects that manage the NPU (network processor) on models with NPUs:
- `config system npu` — NPU attributes (7.6.8 CLI Ref p1793+; NP7 HPE). Verified fields: `set capwap-offload [enable|disable]`, `set dedicated-management-cpu [enable|disable]` + `set dedicated-management-affinity {string}`, `set default-qos-type [policing|shaping|...]`, `config congestion-handling-mode > set mode [flow-control|head-of-line]`, `config dos-options` (`set npu-dos-meter-mode [global|local]`, `set npu-dos-tpe-mode [enable|disable]`), `set double-level-mcast-offload [enable|disable]`, `config dsw-dts-profile`, `config dsw-queue-dts-profile` (per-iport/oport DTS queues), `set napi-break-interval {integer}`, `set npu-group-index {integer}`, `set fastpath [enable|disable]`, `config fp-anomaly` (per error type: `allow`/`drop`/`trap-to-host` for csum-err, land, frag, ipv4/ipv6 options...); 7.6.7: `set vlan-accounting disable`; 7.6.8: `set sctp-offload` + `set sctp-ctrlpkt-to-host`.
- `config system npu-post` — NPU port mapping (hw-acceleration doc p98; `diagnose npu port-list` shows the mapping).
- `config system npu-setting prp` — 7.6.7 CLI Ref p1886 (NPU PRP settings).
- `config system npu-vlink` — 7.6.7 CLI Ref p1887 (NP7 NPU VDOM links for inter-VDOM acceleration).
- Diagnostics: `diagnose npu np7` (NP7 state), `diagnose npu np7 hpe monitor` (per-port HPE stats), `diagnose npu port-list`.

## FortiOS 7.6 parallel path processing pipeline (verified order)

Per the Parallel Path Processing document (corpus: `FortiOS-7.6.0-Parallel-Path-Processing.txt`), a packet passes these stages IN THIS ORDER:
1. **Ingress** (20Gbps-class models use NPUs; 10Gbps-class use dedicated CPUs)
2. **Admission control** — quarantine list check (source/destination), captive portal authentication on ingress
3. **Kernel checks** (basic kernel path)
4. **Destination NAT** — NAT table lookup, rewrite destination IP for incoming traffic
5. **Routing** — including SD-WAN (SD-WAN considers source/destination, user group, application via ISDB)
6. **Stateful inspection** — Layer 3/4; source/destination address, port, protocol; first packet of a session vs. established flow
7. **Policy lookup** — required for the first packet of a session to decide pass/deny
8. **Session management** — session table entry creation/maintenance
9. **Session helpers**
10. **User authentication**
11. **Device identification**
12. **Agentless VPN**
13. **Local management** — completes the pipeline
The design goal: parallel path (hardware-assisted forwarding) vs. basic path, so line-rate forwarding stays at line rate while inspection/security happens in parallel.

## Hardware diagnostics (verified)

```
get hardware status          # model, serial, NPU presence, fan, PSU, temp
diagnose hardware sysinfo conserve   # RAM (2GB-model check: total RAM < 2000 MB)
diagnose hardware sensor     # temperature sensors
diagnose npu port-list       # NPU port mapping
diagnose npu np7 hpe monitor # NPU HPE stats
get system performance       # throughput, sessions, CPU
```

## Supported models

- Full 7.6.7/7.6.8 model list: Release Notes §"Introduction and supported models" (platform piece has the 7.6.7 list). 7.6.8 adds AP411 + WiFi-7 AP updates (wireless piece).
- 8.0.0 supports FG-6000F/7000E/7000F (same hyperscale lineup as 7.6.x).
- **NOT in the 7.6.7 list:** 100E, 1000E, 3000E, 4000E series (discontinued).

## FortiGate 6000F (hyperscale) — verified management model (7.6.7)

Corpus doc: `text/fortigate-6000-767.txt` (FortiGate 6000F Administration, FortiOS 7.6.7, 01-767-465651-20260716).
- **FPC (FortiProcessor Card):** the 6000F is managed per-FPC — apply/activate/verify FPC subscription and perpetual licenses; manage individual management boards and FPCs; connect to individual FPC consoles/CLIs; determine the primary FPC; handle FPC failure; install firmware on an individual FPC.
- **HA:** 6000F HA pairs two FortiGate-6000 units; the secondary unit's FPC CLIs are accessible separately (7.6.7 6000F guide).
- **Physical / health verification (6000F guide, verified):** two 10/100/1000BASE-T out-of-band management interfaces **MGMT1 and MGMT2** (management-board GUI + CLI login, SNMP, remote logging — all other management traffic uses MGMT1) plus one front-panel 10G SFP+ **MGMT3**; front-panel 1/10G SFP+ **HA1/HA2** for heartbeat, session sync, and management. When operating normally the **back-panel PSU and fan try LEDs are all solid green**, and the front panel (including the alarm LED) shows the normal-operating LED pattern.
- **NPU offload + virtual links:** see must-know (NP7 queues, sctp-offload, hpe monitor); `diagnose npu port-list` for the NPU port mapping.

## FortiGate 7000F (hyperscale) — verified (7.6.7 Administration Guide)

Corpus doc: `text/fortigate-7000F-767.txt`.
- **Module-based architecture:** the 7000F chassis combines **FPM (FortiProcessor Modules)** and **FIM (FortiInterface Modules)**. **FIM-7941F** has configurable interface assignments (interfaces 1–18, M1, M2 reconfigurable; 19–20 separate) and **includes NP7 processors**; **FIM-7921F** (interfaces 1–8, M1, M2; 19–20).
- **Hardware operations (all documented):** replacing a failed FPM or FIM — both in a **standalone** 7000F and in a 7000F chassis in an **HA cluster**; installing firmware on individual FIMs or FPMs; installing FIM/FPM firmware from the BIOS after a reboot; **formatting an FIM/FPM boot device and installing new firmware**.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/hardware/PIECE.md` + `manifest.json`. Exam slice: 7 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: hardware`.
