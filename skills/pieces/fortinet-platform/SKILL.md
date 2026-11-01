---
name: fortinet-platform
version: 1.1.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet platform: CLI, system, VDOM, routing, REST API v2"
metadata:
  hermes:
    piece: platform
    surface: fortios-7.6x
    depends_on: []
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 24/92 questions tagged piece=platform (fortinet-corpus/fortios-7.6x/eval/questions.jsonl `piece` field)
    piece_card: /home/chrismok/fortinet-corpus/pieces/platform/PIECE.md
    tags: [fortios, cli, vdom, routing, rest-api, platform]
---

# FortiNet platform piece

Dependency ROOT of the FortiNet piece family (router: `hermes-it-infosec-fw-fortig-fortios-7-6-7`). Covers: CLI fundamentals, system objects, interfaces, zones, address/service objects, multi-VDOM, routing, SNMP, REST API v2, version lines.

Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2) against the official FortiNet PDFs + 174 field reports. Quote CLI verbatim; cite doc + chapter/heading + page. Read-only by default.

## Version lines and scope (verified 2026-11-01)

- **7.6.x line:** 7.6.0 -> 7.6.8. Latest GA = **7.6.8** (2026-10-26 release notes).
- **8.x line:** the 8.0 line ONLY (8.0.0 GA, **8.0.2** latest patch, both 2026-10-26). FortiOS 8.2 and 8.4 do NOT exist on docs.fortinet.com.
- 7.6.7 content stays authoritative for 7.6.x behavior; version-specific deltas are in this piece and in the embedded release notes.

### 7.6.8 special notices (Release Notes 7.6.8, verified)
- **SSL VPN tunnel mode replaced by IPsec VPN (since 7.6.3):** IPsec VPN can be configured to use TCP port 443. SSL VPN tunnel mode is gone from GUI and CLI; its settings are NOT upgraded from previous versions. Migrate before upgrading to 7.6.3+ (migration guides: SSL VPN to IPsec VPN, 7.6 and 7.4 — see the `fortinet-vpn` piece).
- **Agentless VPN (formerly SSL VPN web mode) unavailable on 2GB-RAM models:** 40F, 50G, 60F, 61F, FGR-60F (2GB only), 70G, 90G, 91G and variants; settings not upgraded; migrate to IPsec Dialup VPN. Check RAM: `diagnose hardware sysinfo conserve` (total RAM < 2000 MB = 2GB model).
- 2GB-RAM models: most proxy-related features and Security Rating / Security Fabric topology no longer supported (also in 8.0.x notices).
- 7.6.8 new features include NPU SCTP offload on SoC4/SoC5 (`config system npu set sctp-offload`, `set sctp-ctrlpkt-to-host`), IPv4 option handling in `config system npu config fp-anomaly set ipv4-option {allow|trap-to-host}`, and per-stack RSPAN/ERSAN on FortiSwitch. (NPU details: `fortinet-hardware` piece.)

### 8.0.x facts (Release Notes 8.0.0/8.0.2, verified)
- **CLI additions (8.0.0):** NP7 `set session-acct-interval` range 1-600 s; `set sw-np-rate` / `sw-np-rate-unit {mbps|pps}` / `sw-np-rate-burst` (NP7-to-ISF bandwidth); `set poolname6` IPv6 pool in `config firewall proxy-policy`; `set ses-denied-multicast-traffic enable` in `config system settings`.
- **8.0.2** adds a FortiLink split-interface LLDP neighbor-detection notice.
- 8.0.0 supports FG-6000F/7000E/7000F (same hyperscale lineup as 7.6.x). WiFi-Controller AP support deltas: `fortinet-wireless` piece.

### 8.0.x verified ports (FortiOS-8.0.0-Ports, corpus `fortios-8.0x/`)
- **FGFM tunnel:** TCP 541 (IPv4), TCP 542 (IPv6) — FortiGate-to-FortiManager/FortiGate-to-FortiGate sync.
- **NetFlow collector:** UDP 2055. **sFlow collector:** UDP 6343.
- **FortiPortal:** TCP 443 (REST API) for API communication; email notification TCP 465.
- **HA sync:** UDP 703. (Full table in the doc — version-check for other lines.)

### 8.0.x MIB (FortiOS-8.0.0-FortiGate_MIB_information_overview, web-only doc, corpus `fortios-8.0x/`)
- Fortinet enterprise OID: **1.3.6.1.4.1.12356** (`fortinet` MIB module for Fortinet network devices).
- `fnCoreMib` = 1.3.6.1.4.1.12356.100; `fnSystem` = ...100.1.1; `fnSysSerial` = ...100.1.1.1 (device serial, same as ENTITY-MIB base entity); `fnMgmt` = ...100.1.2; `fnAdmin` = ...100.1.2.100.
- MIB objects/OIDs may be unavailable per-model/version — the doc lists the reasons (web-crawl source; no PDF exists for this doc).

### 8.0.x cellular/5G modem (5G_Device_Modem-80x + FortiOS-8.0.0-Modem_Firmware_Upgrade, corpus `fortios-8.0x/`)
- Modem firmware upgrade (8.0.0+): `execute cellular-modem firmware-upgrade ftp [ImageFile] [FTP Server]:Port (username) (password)` / `... tftp [ImageFile] [TFTP Server]` / `... usb [ImageFile]` / `... management-station` — four transport variants, verified command syntax.
- 5G device/modem doc covers 5G modem (SIM) support on FortiGate/FortiWiFi 5G models.

### 8.0.x reference docs (corpus `fortios-8.0x/`)
- `FortiOS-8.0.0-Best_Practices` — 8.0.0-era design/configuration best practices.
- `FortiOS-8.0-Supported_RFCs` — RFC support matrix for the 8.0 line.

### Must-know 7.6.x changes (index — details in the owning piece)
- **PDE (private data encryption), from 7.6.1:** `config system global > set private-data-encryption enable` now generates a *random* key — a config backed up with key A cannot be restored after the key is regenerated; FortiManager 7.6.3+ can manage PDE FortiGates but cannot import password-type objects. (platform — here)
- SSL VPN tunnel mode replaced by IPsec VPN; tunnel-mode configs NOT migrated. (vpn piece)
- IPsec tunnel interface default MTU 1420 -> 1402 on 7.6.7 (all models; 8.0.0 did selected models only). (vpn piece)
- HA upgrade mode default on FortiGate 6000/7000 changed simultaneous -> **uninterruptible**; CLI prompt now shows HA role — `FortiGate(Secondary) (global) #` (breaks fixed-prompt automation). (ha piece)
- NP7 (7.6.7): dedicated host queue for control-plane traffic + `dedicated-management-cpu` on by default; regular host queues drop at DSWH under extreme load instead of backpressure; `config system npu > set vlan-accounting disable` stops VLAN-lookup message storms. (hardware piece)
- 20xG models (7.6.7, bug 1288059): after factory reset or out-of-box init, port1/port2 removed from the virtual switch, configured for DHCP for Zero Touch Provisioning (ZTP). (hardware piece)
- Central SNAT policy restriction since 7.6.1. (policy piece)
- 2 GB RAM FortiGate models lose most proxy features and Security Rating / Security Fabric topology support.

## CLI core mechanics (CLI Reference, all chapters)

Top-level command classes:
- `config` — read/write configuration tree (commit immediately on `set`)
- `get` — read-only system state (sessions, routes, performance)
- `show` — dump configuration objects
- `execute` — one-shot operations (ping, test, reset, `execute api-user generate-key`, `execute ha failover set|unset|status`, `execute restore image`)

Tree mechanics:
- `next` = saves the current table entry and returns to the entries prompt (so you can add the next entry); `end` = saves and exits the current subcommand entirely (returns to the parent level); `exit` = up one level **without** saving; `clear` = clear a value (reverts to default).
- CLI environment variables (AG "Environment variables", case-sensitive): `$USERFROM` (admin's management access type + IPv4 address), `$USERNAME` (admin account name), `$SerialNum` (device serial number) — usable in `set` commands, e.g. comments.
- Abbreviation: shortest unique prefix works (`conf sys int` = `config system interface`); `?` at any position gives context-sensitive help and full spellings.
- List parameters (`set allowaccess ping ssh https`) — a plain `set` **replaces** the list; `select`/`unselect` add/remove individual values; `append` appends list entries.
- Special characters (AG p.79, "Special characters"): `<, >, (, ), #, ', "` cannot be used in most CLI commands. To enter one (or a space) inside a string: enclose the ENTIRE string in single or double quotes (`"Security Administrator"` / `'Security Administrator'`) or prefix the character with a backslash. `?` and Tab cannot be pasted (CLI Console / some SSH clients) — press Ctrl+V (or Ctrl+Shift+-) FIRST, then type the character.
- Config is applied live as you `set` (no commit step); `clear`/`unset` remove settings (reverting to defaults). Use `show | compare` (and `get system status`) to review.

### Top-level config object map

```
config system      (global, settings, interface, zone, ha, ha-monitor, vdom,
                   api-user, firmware, log, performance, netbird, sdn, time, ...)
config firewall    (policy, policy6, address, address6, service, ippool,
                   ip, all, group, ssl, log, ips, dlp, webfilter, application,
                   av-profile, spamfilter, ...)
config vpn         (ipsec phase1 / phase1-interface / phase2 / setting / ipsec
                   settings / ssl settings / ssl web portal / ssl local / dh,
                   ad, ...)
config router      (static, rip, bgp, ospf, interface, prefix-list, route-map,
                   policy, vdom, ...)
config switch      (port, interface, vlan, link, mirroring, storm, mcast)
config user        (local, certificate, device, ftm, ldap, radius, saml, ...
                   — identity objects)
config log         (filter, ...)
```

### Interface (`config system interface`)
Key fields (CLI Reference-verified): `set ip <addr> <mask>` (type `ipv4-classnet-host`; AG example: `set ip 10.200.0.1 255.255.255.255`; CIDR form `set ip 10.0.0.1/24` also appears throughout AG examples), `set type [physical|vlan|...]`, `set vlanid {integer}`, `set interface <parent>`, `set allowaccess <opt1>, <opt2>, ...` (list), `set defaultgw [enable|disable]`, `set vrf {integer}`, `set role [lan|wan|...]`, `set dedicated-to [none|management]` ("configure interface for single purpose"; used on the HA reserved management interface, e.g. `mgmt1` — AG p.3777).
Management access on an interface is controlled by the `allowaccess` list — AG p.48-49 examples: LAN `port1` gets `set allowaccess ping https ssh`, WAN `port2` gets `set allowaccess ping` only ("for a WAN interface, it is recommended to only allow PING").
**Link aggregation:** `set type aggregate` + `set aggregate-type [physical|vxlan]` (CLI Reference p.1632) + `set member <port1>, <port2>` (member list) + optional `set min-links` / `set min-links-down`; LACP per IEEE 802.3ad/802.1ax (AG p.244 "Aggregation and redundancy"). Give the aggregate interface its IP with the usual `set ip <addr> <mask>`.

### Address / service objects (CLI Reference-verified)
`config firewall address` — **one object = one type**:
`set type [ipmask|iprange|fqdn|...]`.
- ipmask: `set subnet <addr> <mask>` (CIDR form also works, e.g. `10.1.100.0/24`).
- iprange: `set start-ip <a>` + `set end-ip <b>` (AG "IP range" p.1969: continuous range, format `x.x.x.x-x.x.x.x`, no spaces).
- single host: `set subnet <ip> 255.255.255.255`.
- **Mixing types (e.g. an IP range + a single host) = an address GROUP:** create each object separately, then `config firewall addrgrp` / `edit <group>` / `set member <obj1> <obj2>` / `next` / `end`. The policy references the group: `set srcaddr "<group>"` (or `set dstaddr`). An object cannot hold entries of different types in one `edit` block. (Policy usage: `fortinet-policy` piece.)
`config firewall service custom` — `set protocol [TCP|UDP|UDP-Lite|SCTP]` (named, not numeric) and the port fields are `set tcp-portrange` / `set udp-portrange` — space-separated ports and ranges; a single port is fine (`set tcp-portrange 8443`; AG p.1920 `set tcp-portrange 23`; AG p.2136 `set tcp-portrange 25 110 143 119 465 995 993`). There is no `set tcp-port` field in 7.6.7.

### Static route (`config router static`)
```
edit 1
set dst 10.10.0.0/16
set device port1
set gateway 10.0.0.254
set distance 10
set vrf <id>          # optional
set blackhole enable  # optional (discard)
next
end
```
Default gateway: `set defaultgw enable` on the interface (adds implicit 0/0) or explicit `config router static 0.0.0.0/0` with device+gateway.
Gateway requirement (AG §static routes): the gateway address must be the upstream router or L3 switch the FortiGate is connected to on the specified interface — "set the interface to be the WAN interface that the gateway is connected to." A route whose gateway is not reachable on its `device` interface will not work.

## VDOM (`config system vdom`, CLI Ref)
- `config system global > set vdom-mode [multi-vdom|single-vdom]`.
- `config system vdom` — `edit <vdom>` / `set name`, `set status`, `set admin <list>`, `set system-status-log`, per-VDOM settings.
- Assign interfaces: `config system interface > edit <intf> > set vdom <vdom>`.
- **`config system vdom-dns` (7.6.7 CLI Ref — GLOBAL object, not a per-VDOM edit):** configures DNS servers for NON-management VDOMs. Fields: `set vdom-dns [enable|disable]`, `set primary` / `set secondary` (IPv4 DNS servers), `set ip6-primary` / `set ip6-secondary` (IPv6), `set protocol {option1}, {option2}, ...` [cleartext (UDP/TCP 53)|dot (TLS 853)|doh (HTTPS 443)], `set interface-select-method [auto|sdwan|specify]`, `set alt-primary` / `set alt-secondary` (alternate DNS for multi-VDOM), `set server-hostname`, `set server-select-method [least-rtt|failover]`, `set source-ip`, `set ssl-certificate`, `set vrf-select`.
- NPU virtual-link models on 6000F/7000E/7000F: see the `fortinet-hardware` piece (vlinks + multicast-loop warning).

## SNMP (`config system snmp`, CLI Ref 7.6.7 p2024-2041)
- `config system snmp` — global agent settings (enable, version, VRF).
- `config system snmp community` (p2024) — per-community: `set name`, `set access [ro|rw]`, `set source-address`, `set vhost` (per-VDOM community).
- `config system snmp mib-view` (p2034) — MIB views (include/exclude OID ranges).
- `config system snmp rmon-stat` (p2034) — RMON statistics.
- `config system snmp sysinfo` (p2035) — system info extensions.
- `config system snmp user` (p2037) — **SNMPv3 users AND trap/notify destinations**: `set auth-proto [md5|sha|...]`, `set auth-pwd`, `set priv-proto [aes|des|aes256|aes256cisco]`, `set priv-pwd`, `set notify-hosts {ipv4-address}` / `set notify-hosts6` (trap destinations). There is no separate `snmp host` object.
- SNMP utilization alarms tie into CGNAT pool `set utilization-alarm-raise/clear` (policy piece).

## REST API v2 quick reference (Admin Guide §REST API)

- Base: `https://<host>/api/v2/cmdb/<schema>` for config objects (e.g. `GET .../api/v2/cmdb/system/global`, `.../api/v2/cmdb/firewall/address`) and `.../api/v2/monitor/...` for operational telemetry.
- Auth: `Authorization: Bearer *** API v2 admin user. **HTTPS required.**
- Admin users: `config system api-user edit <name>` — `set api-key <key>` or `execute api-user generate-key <name> [expiry-minutes]` (1-10080 min; the key is displayed **only once** after generation), `set accprofile <access-profile>` (least-privilege scope), `set peer-auth`, `set cors-allow-origin` (CORS for third-party web apps calling the API; avoid `*` where possible — CLI Reference p.1424), `config trusthost` with `set ipv4-trusthost <addr/mask>` / `set ipv6-trusthost <addr/prefix>` (trusted host sources; AG p.3548: 0.0.0.0/0 is not permitted). Only the **super_admin** profile can create REST API administrators (AG p.3547).
- Query params (AG example): `format` (field list, e.g. `format="name|comment"`) and `filter` (e.g. `filter=name=@SSLVPN`).
- **Retired endpoints (AG "Retired REST API Endpoints" subsection, p.1021):** `/api/v2/monitor/system/security-rating/*` is no longer supported in 7.6.7.
- The public Admin Guide demonstrates GET; verbs beyond GET and the full per-object request/response schemas are Fortinet FNDN (FKYC) subscription content. Beyond the verified examples above: state FNDN is required.

## Supported models — 7.6.7 (Release Notes p.8, verified)

FortiOS 7.6.7 (build 3704) supports:
- **FortiGate:** FG-30G ... FG-7000F (~60 SKUs) — incl. 200E/201E/300E/400E/500E/600E, 1100E/1101E, 2000E/2200E, 3300E/3600E/3960E/3980E, 5001E; hyperscale FG-6000F/7000E/7000F (own support/limitations section in RN).
- **FortiWiFi:** FWF-30G ... FWF-81F-2R-POE family.
- **FortiGate Rugged:** FGR-50G-5G ... FGR-70G-5G-Dual family.
- **FortiFirewall appliances:** FFW-1801F ... FFW-4801F + FFW-VM64/FFW-VM64-KVM.
- **VM images:** FG-VM64* (x86: KVM/AWS/Azure/GCP/IBM/HV/OPC/XEN/ALI/RAXONDEMAND) and FG-ARM64-* (AWS/Azure/GCP/KVM/OCI).
- **NOT in the 7.6.7 list:** 100E, 1000E, 3000E, 4000E series (discontinued lines) — do not answer "supported" for these.
- Full exact list: Release Notes 7.6.7 §"Introduction and supported models" (p.8).

## Retrieval (this piece's data)

Root index (all surfaces, filter-enforced — **pass the right line**):
```
docker run --rm --mount type=bind,src=/home/chrismok/fortinet-corpus,dst=/home/chrismok/fortinet-corpus zeppo-rag:cli python3 /home/chrismok/fortinet-corpus/query_root.py "<question>" 12 --product fortios --line 7.6x   # 7.6.x facts
# ... --product fortios --line 8.0x   # 8.0.x facts
```
Per-surface hybrid (diagnostics): `fortinet-corpus/fortios-7.6x/scripts/query.py` / `fortinet-corpus/fortios-8.0x/scripts/query.py`. Grep tools: `probe.py` / `ctx.py` in each surface `scripts/`.
Version discipline: surfaces are version-isolated (7.6.x docs in fortios-7.6x, 8.0.x docs in fortios-8.0x) — the `--line` filter is the primary version gate; still sanity-check the `version` field on hits.

## References (load on demand)

- `references/cli-deep.md` — CLI core: tree mechanics, object map, verified field lists (interface, policy, address, service, ippool, routing, static), diagnose command set, worked examples.
- `references/api-deep.md` — REST API v2: api-user object (verified fields incl. generate-key expiry, accprofile, cors-allow-origin, trusted-ips), URL families (cmdb/monitor), verified filter/format query params, FNDN coverage gap map.
