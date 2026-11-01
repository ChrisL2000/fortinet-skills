---
name: fortinet-vpn
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet VPN: IPsec, Agentless, IPsec-over-TCP, MTU"
metadata:
  hermes:
    piece: vpn
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 9/92 questions tagged piece=vpn
    piece_card: /home/chrismok/fortinet-corpus/pieces/vpn/PIECE.md
    tags: [fortios, ipsec, vpn, agentless, npu-offload]
---

# FortiNet VPN piece

IPsec site-to-site + remote access, Agentless VPN (ex-SSL web mode), IPsec-over-TCP, SSL-to-IPsec migration, NPU offload of IPsec. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Must-know (7.6.x)

- **SSL VPN tunnel mode is replaced by IPsec VPN** in the 7.6.x line. Existing tunnel-mode configs and their firewall policies are **not migrated** on upgrade — follow the AG "SSL VPN tunnel mode to IPsec VPN migration" chapter (`references/vpn-deep.md`). SSL VPN web mode continues as Agentless VPN (not supported on some FortiGate series/models; 2GB-RAM models excluded — settings not upgraded).
- **IPsec tunnel interface default MTU 1420 -> 1402 on 7.6.7** (all models; 8.0.0 did selected models only).

## IPsec (verified 7.6.7: `config vpn ipsec phase1[-interface]` / `phase2[-interface]`)

Verified working example (AG, site-to-site):
```
config vpn ipsec phase1-interface
    edit "ipsec"
        set interface "wan1"
        set peertype any
        set proposal aes256-sha1
        set remote-gw 22.22.22.22
        set psksecret <psk>
    next
end
config vpn ipsec phase2-interface
    edit "ipsec"
        set phase1name "ipsec"
        set proposal aes256-sha1
        set auto-negotiate enable
    next
end
```
- Classic interface-bound variant: `config vpn ipsec phase1` (binds IKE to a physical interface) + `config vpn ipsec phase2`.
- Key fields (CLI Reference): phase1 — `set ike-version [1|2]`, `set mode {main|aggressive}`, `set authmethod {psk|signature}`, `set proposal <list>`, `set dhgrp <list>`, `set keylife {sec}`, `set remote-gw {addr}`, `set remote-gw-subnet`, `set peerid {string}`, `set dpd [disable|on-idle|...]`, `set dpd-retrycount` / `set dpd-retryinterval`, `set transport [udp|auto|tcp]` (IPsec-over-TCP option present in 7.6.7), `set rekey`, `set nattraversal`, `set add-gw-route`, `set distance`, `set npu-offload [enable|disable]`, `set monitor <list>` (SD-WAN).
- phase2 — `set src/dst-addr-type [subnet|range|ip|name]` (CLI Reference "Local proxy ID type": subnet = IPv4 subnet, range = IPv4 range, ip = single IPv4 IP, name = IPv4 firewall address or group name; IPv6 equivalents `subnet6|range6|ip6|name6`). Per-type fields: subnet → `set src/dst-subnet <CIDR>`; range → `set src/dst-start-ip <a>` + `set src/dst-end-ip <b>`; name → `set src/dst-name <obj>`. (There are no `src-range`/`dst-range` fields in 7.6.7.) `set proposal <list>`, `set pfs`, `set keylife-type [seconds|kbs|...]`, `set keylifeseconds`, `set encapsulation [tunnel-mode|transport-mode]`, `set add-route`, `set replay`.
- **Tunnel interface MTU is 1402 in 7.6.7** (was 1420 — release notes).
- **NPU (ASIC) offload of IPsec:** controlled by `set npu-offload [enable|disable]` under phase1-interface (default: enabled). Verify it is actually offloading (AG NPU offload chapter): (1) `get hardware status` — confirm the NPU is present; (2) `diagnose npu port-list` — the tunnel's phase1 interface must be mapped to an NPU (port-to-NPU mapping); (3) `diagnose vpn tunnel list` — the `npu_flag` field shows NPU state; AG: "The npu_flag 03 flag means that the traffic processed by the NPU is bi-directional."

## Agentless VPN (formerly SSL VPN web mode)
`config vpn ssl settings` — global parameters (CLI Reference-verified): `set servercert`, `set port` (default 443), `set status`, TLS protocol bounds + `tls-groups`, `force-two-factor-auth`, `reqclientcert`, `config authentication-rule`. `config vpn ssl web portal` — portals/login pages.
Web mode persists across 7.6 upgrades under the name **Agentless VPN** (not supported on some FortiGate series). Tunnel mode is replaced by IPsec — see the AG "SSL VPN tunnel mode to IPsec VPN migration" chapter (references/vpn-deep.md).

## IPsec over TCP / IKE-over-TCP (7.6.7 AG p2926-2927, 8.0.0 NFG)

- Used when **UDP/500 and UDP/4500 are blocked** (CGNAT, restrictive ISPs). ESP is encapsulated inside TCP; **default port 443**.
- **Minimum versions: FortiOS 7.4.2+ and FortiClient 7.4.1+.**
- 7.6.x: `set transport [udp|auto|tcp]` under `config vpn ipsec phase1` / `phase1-interface` (and `set auto-transport-threshold`).
- 8.0.0: per-VDOM `config vpn ipsec setting > set ike-tcp-service [enable|disable]` and `set ike-tls-service [enable|disable]`.

## VPN known issues (7.6.7 release notes, verified)

- **1304588** — IPsec: intermediate CA not sent in the certificate payload for IKEv2 signature auth with `send-cert-chain`; workaround: install the intermediate CA in the endpoint trusted store manually.
- **1227338** — IPsec: PPK fails when IKEv2 EAP is enabled.

## Debug checklist (verified)

```
show vpn ipsec phase1-interface
diagnose vpn tunnel list
diagnose vpn ike config list
# live IKE debug (filter to one remote IP first, then ALWAYS finish with
# 'diagnose debug disable' — leaving debug enabled degrades performance)
diagnose vpn ike log filter rem-addr4 <remote-ip>
diagnose debug application ike -1
diagnose debug enable
diagnose debug disable
# packet capture (no tcpdump in 7.6.7 — use the sniffer)
diagnose sniffer packet <if> 'udp and port 500 or udp and port 4500 or esp' 4 0 l
```

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Migration doc in corpus: `FortiOS-7.6.0-SSL VPN_to_IPsec_VPN Migration.pdf`. Version-check hits (surface contains 8.0.x docs too).

## References (load on demand)

- `references/vpn-deep.md` — verified phase1/phase1-interface/phase2/phase2-interface field lists, SSL settings fields, MTU 1402, AG migration chapter summary, VPN known issues, debug checklist.
