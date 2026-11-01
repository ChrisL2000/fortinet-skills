# FortiOS 7.6.7 Operations, Release Notes & Troubleshooting Deep Reference

Verified against the FortiOS 7.6.7 Release Notes (7.6.7 PDF) and Administration Guide. 7.6.7 GA build example from the release notes: `v7.6.7,build3704 (GA.M)`.

## Release notes structure [RN]

Sections: Special notices, Changes in CLI, Changes in default behavior, Changes in default values, Changes in table size, New features or enhancements, Upgrade information, Product integration, Resolved issues, Known issues, Built-in AV/IPS Engine, Change Log.

## Special notices (7.6.x line) [RN]

1. **Private data encryption (PDE)**: from 7.6.1, `config system global > set private-data-encryption enable` generates a **random** key (no manual 32-hex key). Consequence: a config backed up with random key A **cannot be restored** after the key is regenerated (disable then re-enable creates key B). CLI warning: "This operation will restore system default data encryption key! Previous config files encrypted with the private key cannot be restored after this operation!"
2. **FortiManager + PDE**: FortiManager 7.6.3+ can manage PDE FortiGates but cannot import objects with password-type attributes and cannot create NAT/transparent VDOMs; do it on fresh installs (enable PDE on FG first, add to FGM, configure via FGM). FGM 7.6.2 and earlier cannot manage a FG whose PDE key was generated after upgrading to 7.6.1+.
3. **Hyperscale NP7 CGN**: with overload PBA IP pool, only one block is allocated per client; `cgn-resource-quota` is ignored (NP7 hardware limitation).
4. **FortiGate VMs**: not memory-constrained after 7.6.0 upgrade; >= 4 GB RAM recommended.
5. **NP7 traffic shaping (QTM)**: several QTM bugs fixed, so `config system npu > set default-qos-type {policing|shaping}` can no longer be used for NP7-offloaded session QoS type.
6. **SSL VPN tunnel mode replaced with IPsec VPN** in 7.6.x (see VPN reference; AG migration chapter).
7. **Agentless VPN** (formerly SSL VPN web mode) not supported on some FortiGate series models.
8. **2 GB RAM FortiGate models** no longer support most proxy-related features, and no longer support Security Rating and Security Fabric topology.
9. GUI access conflict when an IPsec TCP tunnel shares the GUI interface.
10. SAML certificate verification changes.
11. Hairpin traffic requires an explicit policy (policy check applies).
12. Changing `vlan-lookup-cache` requires a system restart.
13. FortiLink split interface with LLDP neighbor detection mode — behavior change.

## Changes in CLI [RN]

- 895242: FG-6000/7000 default HA upgrade mode simultaneous -> uninterruptible.
- 1236596: `profile-protocol-options > http > streaming-content-scan-type` default includes `octet`.
- 1238936: SFP speed detect `auto-module` -> `detect-by-module`.
- 1266730: `arp-reply` on firewall VIPs, default enabled.

## Changes in default behavior [RN]

- 1207557: Anycast VM license activation uses dedicated FQDNs `vmactivation1/2/3.fortinet.net`.
- 1238339 (NP7): dedicated host queue for critical traffic (BFD, BGP, LACP) on by default; `dedicated-management-cpu` on by default (disable may maximize CPS); regular host queues drop at DSWH under extreme load instead of backpressure.
- 1239371: GovRamp factory reset defaults to FortiGuard NTP (`ntp1/2.fortinetgov.com`).
- 1240706: NGFW policy-based mode VDOMs now **drop** traffic when IPS sockets are unavailable (previously bypassed) — e.g. during boot, IPS upgrade, or manual debug stop.
- 1245249: more commands allowed before device registration (firewall policy, router setting/static/static6, system admin/central-management/dns/interface/pppoe-interface/settings).
- **1256231: CLI prompt now includes HA role** — `FortiGate(Secondary) (global) #`. Breaks automation with fixed prompt patterns (Ansible etc.).
- 1288059: FortiGate 20xG factory reset: port1/port2 removed from virtual switch, DHCP by default (ZTP over those ports).

## Changes in default values [RN]

- 1248524: IPsec tunnel interface default MTU 1420 -> **1402** on 8.0.1/7.6.7 across all models.

## Changes in table size [RN]

- 1132879: `extension-controller.extender` table size increased to 512 on FGT-200G+ (more LAN-extension connections).

## New features (7.6.x highlights seen in RN) [RN]

- 1192303 (NP7): `config system npu > set vlan-accounting {disable|enable}` (default enable) — disables VLAN accounting to stop large SPV/TPV lookup message storms on busy boxes with many VLANs.

## Upgrade guidance for 7.6.7 [RN]

- **1277454 (Upgrade)**: upgrading **7.6.6 -> 7.6.7 may lose specific `config system global` settings** (e.g. hostname, timezone, admin-scp, vdom-mode). Workaround: before upgrade, `config system global > set web-svc-auto-restart disable`; after upgrade re-enable; then verify with `show system global diagnose debug config-error-log read`.
- **1297497 (Upgrade)**: FGT-30G/31G, FWF-30G/31G fail to restore firmware images via `execute restore image url` (signature verification error).
- 1347610: FGT-3xG fails TFTP install after boot format if BIOS < 05000200 (System known issue).
- 1353040: FGT-370xF/480xF interfaces remain down after upgrading to 7.6.7/7.6.8 (System known issue).

## New known issues in 7.6.7 (full set with workarounds) [RN]

GUI:
- 1274994: duplicate policy entries when many policies use implicit policy enabled.
- 1292309: slow scrolling on policy page with many policies.
- 1300025: admin session termination when logging in via Chrome/Edge. Workaround: clear browser cache/cookies.
- **1306049: blank page when accessing the GUI after upgrading to 7.6.7.** Workaround: disable HTTP rate limiter — `config system global > set admin-http-rate-limit-max-requests 0`.
- 1307573: multiple categories for the same user group in Sequence Grouping View after upgrade.

HyperScale:
- 1245870: NPD error when setting SD-WAN interface member under full-offload level.
- 1285581: performance drop with TCP CPS PBA log + NAT overload on FGT-4401F.
- 1295024: (improvement) ~100% CPS PBA performance increase on FGT-4201F (eimoff eifoff log2host).

Intrusion Prevention:
- 1301558: IPS engine error condition when upgrading to 7.6.7. Workaround: upgrade IPS engine to latest version.

IPsec VPN:
- 1227338: PPK fails when IKEv2 EAP enabled.
- 1304588: intermediate CA not sent in certificate payload with `send-cert-chain` (IKEv2 signature). Workaround: install intermediate CA manually in endpoint trusted store.
- 1321797: PPTP fails when CCP negotiation on FGT-120G.

Proxy:
- 1257499: protocol-switching web traffic (HTTP/HTTPS) may be blocked when `profile-protocol-options` websocket status disabled. Workaround: enable websocket or switch inspection mode to flow.
- 1280944: traffic blocked when `unsupported-ssl-version allow` enabled and `min-allowed-ssl-version` set to TLS 1.1.

Switch Controller:
- 1329662: FortiGate removes user-configured SVI interfaces on FortiSwitches during switch-controller reconciliation after an upgrade.

System:
- 1271259: FR-1 QSFP 100G transceiver issue. Workaround: set mediatype LR4 and disable forward-error-correction at speed 100Gfull.
- 1304395 / 1304601: traffic drop when one aggregate-interface member goes down.
- 1304523: traffic drop when one LACP member link goes down.
- 1311807: `reachable` value doesn't update after NTP recovery.
- 1347610: (see upgrade above).
- 1353040: (see upgrade above).

Upgrade: 1277454, 1297497 (above).

Existing known issues (carried from earlier 7.6.x into 7.6.7) start at [RN, Existing known issues] — e.g. Endpoint Control 1019658 (EMS tags not all displayed in GUI), 1038004 (FortiClient user info), Firewall traffic-shaping GUI 959065.

## Troubleshooting playbooks [AG, CLI Ref, RN]

**1. No connectivity / general**
```
get system status
show system interface [list]
get system performance status
diagnose sniffer packet <intf> 'host <peer>' 4 0 l
show firewall policy            # find the policy hit/miss
```

**2. Policy not matching**
- Confirm src/dst intfs (or zones), srcaddr/dstaddr, service, schedule; check policy order (first match wins); confirm NAT mode vs. your expectation; verify address objects resolve (FQDN/geo); check implicit deny log if logtraffic enabled.

**3. Sessions**
```
diagnose sys session list              # all active sessions
diagnose sys session stat              # counters by type
```

**4. VPN (IPsec)**
```
show vpn ipsec phase1-interface / show vpn ipsec phase2-interface
diagnose vpn tunnel list
diagnose vpn ike config list           # IKE state
diagnose sniffer packet <if> 'udp and port 500 or udp and port 4500 or esp' 4 0 l
```
See VPN reference checklist. Remember tunnel MTU is 1402 in 7.6.7.

**5. HA**
```
show system ha status
diagnose sys ha history read
```
Check heartbeat/monitor interface state, override/priority consistency across members, session-pickup options.

**6. Performance**
```
get system performance status [cpu|memory|session|disk]
diagnose sys performance status
```
NP7: consider `config system npu set vlan-accounting disable` if VLAN lookup storms suspected; note 7.6.7 NP7 queue changes (1238339).

**7. Post-upgrade**
```
show system global diagnose debug config-error-log read
```
Then check RN known issues for your model (GUI blank 1306049, IPS 1301558, interface-down 1353040).

**8. License/registration**
```
get system fortiguard
get system status        # includes registration
```

## Field intel (community sources) [CF, r/FortiNet]

- community.fortinet.com: FortiOS support forum (forum 92). Topic discovery: sitemaps `sitemap-topics-1.xml` / `sitemap-topics-2.xml` (~100k topic URLs; filter by 7.6.x version tags), then fetch topic pages; search page is JS-rendered (`/search/?query=`), so prefer sitemap + web search. Active 7.6.7-era threads confirmed: Bug 1306049 (blank GUI after upgrade), Bug 1303540, double-login issues, FortiSwitch controller reconciliation, SSL VPN tunnel mode removal.
- r/FortiNet: RSS feed (`/r/FortiNet/.rss`) is live and unauthenticated; JSON/HTML endpoints return 403 from datacenter IPs — use RSS + web search (`site:reddit.com/r/FortiNet`).
- Trust ordering: official FortiNet docs (this corpus) > community answers with Fortinet staff confirmation > community consensus. Treat community claims as leads, not sources of truth; re-verify against the official PDFs or a lab before acting.

## diagnose sys session list — output fields [AG, troubleshooting chapters]

`diagnose sys session list` (optionally `| grep <str>` or with count filter)
prints one block per session; key fields (AG p.3465-3466 example):
- `proto` (IP protocol number), `proto_state`, `duration` / `expire` (seconds
  until session timeout), `state`, `flags`, `policy_dir`
- `orgin->sink` (spelled "orgin" in the output): origin -> sink addresses in
  pre- and post-NAT form (`org pre->post, reply pre->post`)
- `dev` (interface/device index), `gwy` (gateway used), `hook` (pre/post NAT)
- `statistic(bytes/packets/allow_err)` for org and reply directions, plus
  tx/rx speed counters
- `ha_id`, `class_id`, `use`, `socktype/sockport`, `av_idx` (AV index)
Session counters: `diagnose sys session stat` shows totals (number of
sessions, bytes, packets).
