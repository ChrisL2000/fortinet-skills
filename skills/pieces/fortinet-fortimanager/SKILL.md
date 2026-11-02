---
name: fortinet-fortimanager
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiManager 7.6: ADOMs, device mgmt, policy, HA, ports"
metadata:
  hermes:
    piece: fortimanager
    surface: fortimanager-7.6x
    depends_on: []
    corpus: /home/chrismok/fortinet-corpus/fortimanager-7.6x
    exam: 10 questions tagged piece=fortimanager
    tags: [fortimanager, 7.6, adom, device-manager, policy-package, ha, fgm, fofm]
---

# FortiManager piece (7.6.x)

When to use: any question about FortiManager — ADOMs, device registration/management, policy packages, FMG HA, FMG ports, max values, FMG CLI, or FortiManager↔FortiGate protocols (FGFM/OFTP). Not for FortiOS device configuration (use the fortios piece skills) or FortiAnalyzer log analytics beyond FMG's log reference.

Centralized management platform: policy-based provisioning and configuration management for FortiGate, FortiWiFi, FortiAP and other devices; scales to 10,000+ devices/VDOMs from a single interface (medium-large enterprise + MSSP). Source-verified against the FortiManager 7.6.8 doc set (Admin Guide 1,245p, CLI Reference 364p, Release Notes, Log Reference, Upgrade Guide, Maximum Values, Ports 7.6, Best Practices 7.6.0). Corpus: `fortinet-corpus/fortimanager-7.6x/` (3,408 chunks, collection `fmgr76`).

## Module architecture (verified)

- **Object database shared by** (feed policy config info to FortiGates via Device Manager): Policies & Objects, AP Manager, VPN Manager, Extender Manager, FortiSwitch Manager.
- **Direct-protocol modules** (talk to managed devices themselves): FortiGuard, FortiAnalyzer features, Device Manager.
- Recognizes Security Fabric groups; displays Security Fabric topology + Security Fabric Ratings.
- Can act as **on-site FortiGuard Distribution Server (FDS)** (local signature/attack-signature updates for managed devices + FortiClient agents, web/email filter services) to reduce Internet usage.
- **Optional FortiAnalyzer features**: analyze managed-device logs + generate reports from FortiManager.
- Manager chapters: Dashboard, Device Manager, Policy & Objects, SD-WAN Manager, AP Manager, VPN Manager, FortiView, Fabric View, FortiAI, FortiGuard, FortiSwitch Manager, Extender Manager, System Settings, Administrators, High Availability.
- Appendices: Supported RFC Notes, Policy ID support, **Ansible Collection documentation**, FortiAI token entitlements, VM license migration.

## ADOMs (Administration Domains) — modes (verified, AG §ADOM modes)

- **Normal mode** (read/write): push configuration from FortiManager to managed devices. FortiGate units query their own configuration **every 5 seconds**; on a change they send a **diff revision** to FortiManager over the **FGFM protocol**.
- **Backup mode** (configuration storage): FortiManager CANNOT push new config directly — changes made via scripts run on the device, or the device GUI/CLI. Adding a device to a backup ADOM auto-stores its config in the FMG device database. Revisions sent when: (1) config change + session timeout, (2) config change + log out, (3) config change + reboot, (4) manual config backup from the device. Revision history viewable; existing revisions can be pushed back. Objects (e.g. firewall addresses) can be imported into the backup ADOM database to share with other devices.
- **Backup-mode CLI backups require** on the FortiManager:
  ```
  config system global
  set fcp-cfg-service enable
  end
  ```
- ADOMs: global ADOM layer; switching between ADOMs; ADOMs and devices.

## High Availability (verified, AG §High Availability)

- Purpose: protect the FortiManager database — **dynamically backs up FMG database changes to one or more backup units**; on primary failure a backup takes its place.
- **Cluster: max 5 units — 1 primary + up to 4 backup/secondary.** All units must be the **same FortiManager series**. All units are visible on the network.
- **FortiAnalyzer Features must be disabled** on the FortiManager before forming an HA cluster.
- **Geographic redundancy supported** — primary and secondaries may be in different locations.
- HA sync port: **TCP/5199** (Ports doc).
- Note: FortiManager cannot configure HA on real FortiGate devices (FMG VM HA ≠ FortiGate device HA).

## Ports (verified, FortiManager 7.6 Ports doc)

Key incoming ports (FortiGate ↔ FortiManager):
- **FGFM management: TCP/541 (IPv4), TCP/542 (IPv6, from FortiManager 7.4.1)**
- **OFTP logging (all Fortinet products): TCP/514**
- Log aggregation server: TCP/300 (requires FortiManager 800 series or higher)
- FortiGuard/GeoIP/AV file query services: TCP/8900; Antispam: TCP/8889/UDP/8889; FortiClient AV cascade: TCP/8891; IoT query services: TCP/443; license validation + UTM updates: TCP/8890, TCP/443; WebFilter queries/AV+IPS updates: UDP/53, UDP/8888, TCP/80, TCP/443, TCP/8888.

## Policy & Objects (verified)

- **Policy check tool (policy consistency check)**: checks all policy packages within an ADOM for consistency/conflicts that could prevent traffic passing; checks four object conditions:
  1. **Object duplication** — two objects with identical definitions
  2. **Object shadowing** — a higher-priority object completely encompasses another object of the same type
  3. **Object overlap** — one object partially overlaps another of the same type (partially shadowed)
  4. **Object orphaning** — object defined but unused anywhere
  Uses source/destination interface + address policy objects, services, etc.
- Object database shared across modules (see above). Policy install flow to devices via Device Manager; device association with policy packages; consistency check optional before install (results visible in Policy & Objects).

## Device Manager (verified, AG chapter headings)

- Adding **online devices via Discover mode** and legacy login; **offline devices** added by serial number, pre-shared key, or with a device template.
- **Model devices** (non-FortiGate models): device blueprints; import model devices from CSV (supported fields documented).
- **Automatic onboarding** rules; initiate onboarding from the FortiGate.
- Device templates; multiple management addresses; **PDE-managed FortiGate exceptions** (private-data-encryption FortiGates added to FMG 7.6.8).
- Security Fabric authorization; hiding unauthorized devices; FortiSASE policy package installation.
- **Scripting**: CLI scripts, Tcl scripts (limitations/variables/loops documented), **Jinja templates** (FMG metadata variables, SD-WAN overlay via Jinja, hub/branch templates, IPsec template install, pre-run CLI templates, validation on change).
- HA cluster status viewing/editing from Device Manager; REST API administrators; FortiAnalyzer/FortiAnalyzer BigData add (wizard, new or existing); license install via BYOL file or FortiFlex connector.

## Maximum values (verified)

- **`print tablesize`** shows supported maximum values for the local FMG model.
- The 7.6.8 Maximum Values doc table = values for a FortiManager **VM** (example); real limits depend on model.

## Setup / system (verified, AG chapters)

- Setup wizard: **Register with FortiCare + FortiCare SSO required** before accessing the appliance/VM; VM license activation; later-option steps postponable.
- Security: restrict GUI access by trusted host; **TPM support**; configuration backups/migrations; **self-encrypting drives** (SED) + working-with-SED examples; auto-lock; cryptographic erase; UEFI secure boot; real-time file system integrity checking.
- System Settings + Administrators chapters (ADOM access assignments by ADOM).

## Release / upgrade notes (verified)

- 7.6.8 Release Notes (2026-10-22): "what's new" content lives in the **FortiManager 7.6 New Features Guide** (indexed by release) — that guide is NOT in this doc set.
- Pre-upgrade action noted in 7.6.8 RN: **migrate SSL VPN tunnel mode to IPsec VPN before upgrading** (detailed steps in the FortiOS 7.6 New Feature Guide + migration guide links).
- Upgrade Guide 7.6.8 covers upgrade procedures/checks for moving to 7.6.8.

## Logging (verified, Log Reference 7.6.8)

- Log Reference covers **FortiManager AND FortiAnalyzer** log messages — audit log of user actions.
- Structure: log types and subtypes (separate FMG + FortiAnalyzer sections), log message examples with message breakdowns (event log, application log), priority levels.

## CLI reference (364p, 7.6.8)

- FMG CLI follows `config system global`, `config system adom`, `config device ...`, `config policy ...` style; `print tablesize` for limits; FMG has its own CLI (not FortiOS CLI) — reference doc is the FortiManager CLI Reference.

## Exam

- Exam: 10 questions (piece=fortimanager) in `fortinet-corpus/fortimanager-7.6x/eval/questions.jsonl` — ADOM modes (2), module architecture, HA, ports, max values, policy check, sync interval, log reference, FDS/scaling.
