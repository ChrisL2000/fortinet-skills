---
name: fortinet-hardware
version: 1.2.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet hardware: hyperscale FG, NPU, PPP pipeline"
metadata:
  hermes:
    piece: hardware
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x (+ /home/chrismok/fortinet-corpus/fortigate-hardware-7.6x)
    exam: 5/92 questions tagged piece=hardware + 10 questions fortigate-hardware-7.6x (hw-01..hw-10)
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

## NPU CLI objects (7.6.7/7.6.8, verified) + 8.0.x hardware-acceleration doc (corpus `fortios-8.0x/`)

The objects that manage the NPU (network processor) on models with NPUs:
- `config system npu` — NPU attributes (7.6.8 CLI Ref p1793+; NP7 HPE). Verified fields: `set capwap-offload [enable|disable]`, `set dedicated-management-cpu [enable|disable]` + `set dedicated-management-affinity {string}`, `set default-qos-type [policing|shaping|...]`, `config congestion-handling-mode > set mode [flow-control|head-of-line]`, `config dos-options` (`set npu-dos-meter-mode [global|local]`, `set npu-dos-tpe-mode [enable|disable]`), `set double-level-mcast-offload [enable|disable]`, `config dsw-dts-profile`, `config dsw-queue-dts-profile` (per-iport/oport DTS queues), `set napi-break-interval {integer}`, `set npu-group-index {integer}`, `set fastpath [enable|disable]`, `config fp-anomaly` (per error type: `allow`/`drop`/`trap-to-host` for csum-err, land, frag, ipv4/ipv6 options...); 7.6.7: `set vlan-accounting disable`; 7.6.8: `set sctp-offload` + `set sctp-ctrlpkt-to-host`.
- **8.0.x hardware-acceleration guide** (`fortios-hardware-acceleration-802.txt`): content processors **CP10 / CP9 / CP9XLite / CP9Lite** (CP10 ≈ 2× CP9 IPsec throughput, ≈6× rule DB); network processors NP7/NP7Lite/NP6/NP6XLite/NP6Lite; 8.0.x topics: **NP7 link-scan interval** (`config system npu set np-linkscan-interval`, 50-1000 ms, default 1000 — reduces FGCP HA failover delay), **IPsec over VNE interface** (NP7/NP7Lite, SOC5) with `ipsec-ob-np-sel {rr|packet|hash}` steering, **NP session offloading in HA active-active**, **NP HMAC check offloading**, **software-switch interfaces + NP processors**, **post-quantum readiness and NP processors**, **automatic NP7 egress shaping profile refresh** (`mcs-auto-start` auto-flush/reinstall of IPsec SAs).
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
- **7.6.8 hyperscale lineups (verified, hardware surface):** 6000F guide covers **6500F/6501F/6300F/6301F/6001F (+ -DC variants)**; 7000E guide covers **7060E/7040E/7030E**; 7000F guide covers **7121F/7081F**; 1000F QSG covers **FG-1000F/FG-1001F**.
- **Model gap (documented):** no separate 7.6.8 admin guides for 2000F/4000F/10000F or a 6000E in the hardware corpus.
- 8.0.0 supports FG-6000F/7000E/7000F (same hyperscale lineup as 7.6.x).
- **NOT in the 7.6.7 list:** 100E, 1000E, 3000E, 4000E series (discontinued).

## FortiOS 7.6.8 hardware expansion surface (verified, `fortigate-hardware-7.6x` corpus: 4 docs, 452 pages, 1,251 chunks, collection `hw76`)

Docs: FortiGate 6000F Admin 7.6.8 (128p), 7000E Admin 7.6.8 (157p), 7000F Admin 7.6.8 (156p), FG-1000F Series QSG (11p).

### 6000F (7.6.8 admin guide, verified)
- 3U 19-inch rackmount; all models share one front/back panel — differences are processing capacity only.
- Front panel: **24x 1/10/25GigE SFP28 data ports (1-24, default 10Gbps)** + **4x 40/100GigE QSFP28 data ports (25-28, default 40Gbps)**; MGMT1/2 10/100/1000BASE-T; MGMT3 1/10G SFP+ (extra mgmt bandwidth, e.g. remote logging); HA1/HA2 1/10G SFP+; RJ-45 RS-232 console; 1 USB.
- **Interface groups:** port1-24 in groups of four (1-4, 5-8, 9-12, 13-16, 17-20, 21-24); all ports in a group run at the same speed — changing one port's speed changes the whole group. Ports 25-28 are independent. Speed CLI: `config system interface > edit portN > set speed 25000full`.
- **Data plane:** management board (MBD) + internal **FPCs** (NP6 + CP9). **6500F = ten FPCs; 6300F = six FPCs.** Two DP3 load balancers do session-aware load balancing across a **3.2Tbps integrated switch fabric**; NP6 = fastpath offload incl. IPsec encryption/decryption; CP9 = SSL VPN/Antivirus/Application Control/IPS acceleration.
- **HA:** HA1/HA2 (heartbeat, session sync, mgmt between the two units; default 10Gbps, 1G not recommended); cluster = **two (and only two) units of the same model**.
- **01F models (6001F/6501F/6301F):** two internal 1 TByte log disks in RAID-1.

### 7000E (7.6.8 admin guide, verified)
- Product = chassis (7060E/7040E/7030E) + **FIMs in slots 1-2** + **FPMs in slots 3+** (e.g. 7040E ships 2 FIMs + 2 FPMs). FIMs provide network connections + session-aware load balancing to FPMs.
- Two different FIMs: install the **lower model number in slot 1** (e.g. FIM-7901E in slot 1, FIM-7904E in slot 2).
- Manage via the **primary FIM (slot 1)** management IP; same FortiOS build + configuration on every FIM/FPM; changes sync to all modules.
- Firmware upgrade from primary FIM: **all FIMs/FPMs upgrade in one step**, brief traffic interruption — quiet time.
- Licensed/registered as **one product under the chassis serial number** (all FortiGuard/FortiCare licensing applies to the whole package).

### 7000F (7.6.8 admin guide, verified)
- **7121F:** 2 FIMs (slots 1-2) + up to **10 FPMs (slots 3-12)**. **7081F:** up to **6 FPMs (slots 3-8)**.
- **NP7-accelerated session-aware load balancing** via the FIMs; FPMs carry **NP7 (CPU offload) + CP9 (security acceleration) + data interfaces**.
- Connect via MGMT interface; **MGMT1 default IP of the FIM in slot 1 = 192.168.1.99**; config made from slot-1 FIM syncs to the other FIM + all FPMs.
- Firmware upgrade: one step across all modules, brief interruption.
- Typical deployment: **two chassis as an FGCP active-passive cluster**; manage via MGMT (logs you into the primary chassis); **upgrade-mode uninterruptible** → both chassis updated without interrupting data traffic.
- Same single-package licensing/registration under the chassis serial number.

### FG-1000F QSG (verified)
- Covers **FG-1000F and FG-1001F**; default MGMT IP **192.168.1.99**; login **admin / blank password**; console port for CLI; static-IP example: management computer 192.168.1.1/24; setup locally (GUI/CLI) or via forticloud.com; register at support.fortinet.com.

## FortiGate 6000F (hyperscale) — verified management model (7.6.7 + 8.0.x)

Corpus docs: `text/fortigate-6000-767.txt` (FortiOS 7.6.7) and `fortios-8.0x/text/fortigate-6000-802.txt` (FortiOS 8.0.2).
- **FPC (FortiProcessor Card):** the 6000F is managed per-FPC — apply/activate/verify FPC subscription and perpetual licenses; manage individual management boards and FPCs; connect to individual FPC consoles/CLIs; determine the primary FPC; handle FPC failure; install firmware on an individual FPC.
- **HA:** 6000F HA pairs two FortiGate-6000 units; the secondary unit's FPC CLIs are accessible separately (7.6.7 6000F guide).
- **6000F 8.0.1 new (verified):** FGCP HA supports **high-memory-utilization failover protection**; updated primary-FortiGate-6000 selection procedures (with/without override).
- **Physical / health verification (6000F guide, verified):** two 10/100/1000BASE-T out-of-band management interfaces **MGMT1 and MGMT2** (management-board GUI + CLI login, SNMP, remote logging — all other management traffic uses MGMT1) plus one front-panel 10G SFP+ **MGMT3**; front-panel 1/10G SFP+ **HA1/HA2** for heartbeat, session sync, and management. When operating normally the **back-panel PSU and fan try LEDs are all solid green**, and the front panel (including the alarm LED) shows the normal-operating LED pattern.
- **NPU offload + virtual links:** see must-know (NP7 queues, sctp-offload, hpe monitor); `diagnose npu port-list` for the NPU port mapping.

## FortiGate 7000F (hyperscale) — verified (7.6.7 + 8.0.2 Administration Guides)

Corpus docs: `text/fortigate-7000F-767.txt` (7.6.7) and `fortios-8.0x/text/fortigate-7000F-802.txt` (8.0.2).
- **Chassis (8.0.2 verified):** **FortiGate 7121F** = 16U 19-inch rackmount **12-slot** chassis, **1Tbps fabric backplane**, 50Gbps base; managed by **two redundant System Management Modules (SMM 1/2)**; power via **eight hot-swappable 200-240 VAC PSUs** (gen-1/gen-2 chassis). A 7000F product = chassis (7121F or 7081F) + FIMs + FPMs in slots.
- **Module-based architecture:** the 7000F chassis combines **FPM (FortiProcessor Modules)** and **FIM (FortiInterface Modules)**. **FIM-7941F** has configurable interface assignments (interfaces 1–18, M1, M2 reconfigurable; 19–20 separate) and **includes NP7 processors**; **FIM-7921F** (interfaces 1–8, M1, M2; 19–20).
- **Hardware operations (all documented):** replacing a failed FPM or FIM — both in a **standalone** 7000F and in a 7000F chassis in an **HA cluster**; installing firmware on individual FIMs or FPMs; installing FIM/FPM firmware from the BIOS after a reboot; **formatting an FIM/FPM boot device and installing new firmware**.
- FPM fast-path variants (8.0.2 docs): **FPM-7620E / FPM-7630E** fast path architecture sections (see also `fortigate-7000E-802.txt`).

## Retrieval

Root index with filter (pass the right line): `query_root.py "<q>" 12 --product fortios --line 7.6x` (7.6.x) or `--line 8.0x` (8.0.x) (runbook in the router skill). Surfaces are version-isolated; sanity-check the `version` field on hits. Hyperscale chassis details (6000F/7000E/7000F/1000F, 7.6.8) live in the `fortigate-hardware-7.6x` collection (`hw76`) inside the root index — query with the surface's own metadata values: `query_root.py "<q>" 12 --product fortigate --line hardware-7.6x` (the compile step splits the surface name, so the line value is `hardware-7.6x`, not `7.6x`).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/hardware/PIECE.md` + `manifest.json`. Exam slice: 7 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: hardware`.

**Hardware surface exam** (`fortigate-hardware-7.6x/eval/`, hw-01..hw-10): R1 = **100% strict / 101.2% weighted** (101.2% is a judge artifact — 5 verdicts for hw-02's 4 key points, all PASS; hw-04 one minor partial), R2 = **100% strict / 99.3% weighted**. Gate met round 1; accepted as documented R1+R2 (2026-11-02).
