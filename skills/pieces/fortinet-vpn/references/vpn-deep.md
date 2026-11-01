# FortiOS 7.6.7 VPN Deep Reference

Verified against the FortiOS 7.6.7 CLI Reference (VPN objects) and Administration Guide (IPsec/SSL VPN chapters, SSL VPN -> IPsec migration).

## IPsec object model in 7.6.7 [CLI Ref]

Two parallel trees (interface-based vs. tunnel-interface-based):
- `config vpn ipsec phase1` + `config vpn ipsec phase2` — classic interface-bound tunnels (bound to a physical interface via `set interface`).
- `config vpn ipsec phase1-interface` + `config vpn ipsec phase2-interface` — tunnel-interface model; each phase1 gets its own tunnel interface used in policies/routing.

Other VPN objects in 7.6.7 CLI Ref: `vpn ipsec concentrator`, `vpn ipsec fec`, `vpn ipsec manualkey`, `vpn ipsec manualkey-interface`, `vpn l2tp`, `vpn pptp`, `vpn qkd`, `vpn certificate ca|crl|local|remote|hsm-local|ocsp-server|setting`, `vpn kmip-server`, `vpn ssl settings`, `vpn ssl web portal`, `vpn ssl web realm`.

There is **no `config vpn ike gateway` object in the 7.6.7 CLI Reference** — gateway identity is carried inside the phase1 objects (`peerid`, `local-gw`, `remote-gw`, `dev-id`).

## phase1 (interface-based) — key fields [CLI Ref]

```
config vpn ipsec phase1
    edit <name>
        set interface <intf>             # physical interface for IKE
        set type {static|dynamic|...}
        set mode {main|aggressive}
        set ike-version [1|2]
        set authmethod {psk|signature}
        set authmethod-remote {psk|signature}
        set psksecret {password}
        set local-gw {ipv4-address}
        set remote-gw {ipv4-address}
        set remote-gw-subnet {ipv4-classnet}   # or remote-gw-match/start/end
        set peerid {string}
        set localid {string}
        set proposal {option1}, {option2}, ... # e.g. aes128-sha1-modp2
        set dhgrp {option1}, {option2}, ...
        set keylife {integer}           # seconds
        set dpd {disable|on-idle|...}
        set dpd-retrycount {integer}
        set dpd-retryinterval {user}
        set keepalive {integer}
        set transport [udp|auto|tcp]
        set remote-gw-country {string}
        set certificate <name1>, ...    # signature auth
        set send-cert-chain {enable|disable}
        set cert-trust-store {local|ems}
        set fragmentation {enable|disable}
        set fragmentation-mtu {integer}
        set rekey {enable|disable}
        set nattraversal [enable|disable|...]
        set peergrp <name>
        set backup-gateway <addr1>, ...
        set remotegw-ddns {string}
        set add-gw-route {enable|disable}
        set distance {integer}
    next
end
```

## phase1-interface (tunnel model) — key additions [CLI Ref]

Same core fields plus:
```
        set local-gw6 {ipv6-address}
        set remote-gw6 {ipv6-address}
        set ip-version [4|6]
        set encapsulation [none|gre|...]
        set encapsulation-address [ike|ipv4|...]
        set encap-local-gw4/gw6, set encap-remote-gw4/gw6   # encap gateway overrides
        set default-gw {ipv4-address}
        set default-gw-priority {integer}
        set monitor <name1>, ...              # SD-WAN monitor link
        set monitor-hold-down-type [immediate|delay|...]
        set monitor-hold-down-delay {integer}
        set monitor-hold-down-weekday ...
        set multipath {integer}
        set passive-mode [enable|disable]
        set net-device [enable|disable]
        set vni {integer}
        set auto-discovery-sender/receiver [enable|disable]
        set auto-discovery-forwarder [enable|disable]
        set auto-discovery-shortcuts [independent|dependent]
        set auto-discovery-crossover [allow|block]
        set aggregate-member [enable|disable]
        set aggregate-weight {integer}
        set exchange-ip-addr4 {ipv4-address} # advertise specific local IP
        set exchange-interface-ip [enable|disable]
```

## phase2 / phase2-interface — key fields [CLI Ref]

```
config vpn ipsec phase2
    edit <name>
        set phase1name <phase1-name>
        set src-addr-type [subnet|range|...]
        set src-subnet {ipv4-classnet}       # or src-start-ip/src-end-ip, src-name
        set dst-addr-type [subnet|range|...]
        set dst-subnet {ipv4-classnet}
        set src-port {integer}
        set dst-port {integer}
        set protocol {integer}               # 17=GRE, 47=GREv6 etc.
        set proposal {option1}, {option2}, ...
        set dhgrp {option1}, {option2}, ...
        set pfs {enable|disable}
        set keylife-type [seconds|kbs|...]
        set keylifeseconds {integer}
        set keylifekbs {integer}
        set encapsulation [tunnel-mode|transport-mode]
        set add-route [phase1|enable|...]
        set diffserv {enable|disable}
        set diffservcode {user}
        set keepalive {enable|disable}
        set replay [enable|disable]
        set single-source {enable|disable}
        set route-overlap [use-old|use-new|...]
    next
end
```
`phase2-interface` adds `auto-discovery-forwarder` and `auto-discovery-sender` (inherited-from-phase1 options).

## MTU note (7.6.7) [RN, Changes in default values]

Default MTU for IPsec tunnel interfaces changed **1420 -> 1402** on 8.0.1/7.6.7 across **all** FortiGate models (8.0.0 did it for selected models). Sizing checks that assumed 1420 must be re-verified.

## SSL VPN in 7.6.7 [CLI Ref, AG]

- `config vpn ssl settings`: global SSL VPN parameters — `set servercert`, `set ca-cert`, `set port` (default 443), `set status`, TLS bounds (`ssl-min-proto-ver`/`ssl-max-proto-ver`), `tls-groups`, `force-two-factor-auth`, `reqclientcert`, `auth-session-check-source-ip`, DTLS heartbeat parameters, `login-attempt-limit`/`login-block-time`, `config authentication-rule` (per-user/portal/realm auth + cipher selection).
- `config vpn ssl web portal`: portals with login pages; "web mode" SSL VPN is branded **Agentless VPN** in 7.6.x and is **not supported on some FortiGate series/models** [RN, Special notices].
- **SSL VPN tunnel mode is being replaced by IPsec VPN** in the 7.6.x line [RN, Special notices]. The Administration Guide ships a full **"SSL VPN tunnel mode to IPsec VPN migration"** chapter (~p. 2900s area of the PDF) covering: inventory of tunnel-mode deployments, building the replacement IPsec phase1/phase2 (tunnel interface), policy migration (srcaddr/dstaddr from the SSL VPN subnet), client configuration changes (FortiClient IPsec profile), and cutover. Follow that chapter step-by-step rather than ad-hoc conversion.
- FortiClient SSL VPN tunnel-mode users migrate to IPsec (tunnel or remote-access IPsec) per the migration chapter.

## 7.6.7 VPN known issues [RN]

- **1227338** (IPsec VPN): IPsec VPN fails to use PPK when IKEv2 EAP is enabled.
- **1304588** (IPsec VPN): intermediate CA is **not sent** in the certificate payload for IKEv2 signature-based auth when `send-cert-chain` is enabled on phase1. Workaround: install the intermediate CA in the trusted store on the endpoint manually.
- **1321797**: PPTP connection failure when Compression Control Protocol negotiation happens on FortiGate 120G.

## VPN troubleshooting [AG, CLI Ref]

```
diagnose vpn ike ...                 # IKE stat/config subcommands (ike config list, counts, crash, crypto, admin)
diagnose vpn tunnel list             # tunnel state per phase1/phase2
diagnose sys session list            # data-plane sessions
diagnose sniffer packet <if> 'udp and port 500 or udp and port 4500 or esp' 4 0 l
show vpn ipsec phase1-interface      # verify config
get system performance status
```
Checklist order: (1) IKE reachability (UDP 500/4500) — sniffer on the phase1 interface; (2) phase1 identity/PSK/cert chain; (3) NAT traversal (`nattraversal`, UDP 4500); (4) DPD + keepalive; (5) phase2 selectors (src/dst, protocol) match both sides; (6) routing (`add-gw-route`, `set distance`, tunnel MTU 1402); (7) policy srcaddr/dstaddr covering the selectors.

## DPD (Dead Peer Detection) [AG p.2679]

- By default DPD sends probe messages **every five seconds**; increasing the
  interval reduces load but takes longer to detect dead peers.
- `set dpd [disable | on-idle | on-demand]` on the phase 1 entry:
  - `on-idle` — triggers DPD when IPsec is idle; on a dialup server this
    encourages more proactive tunnel deletion.
  - `on-demand` — passively sends DPD only when outbound IPsec packets are
    sent and no reply is received; no periodic DPD when idle (scales better
    on dialup servers with many idle tunnels).
- `set dpd-retryinterval <seconds>` + `set dpd-retrycount <n>` — AG example:
  15-second interval, retrycount 3 = wait for three missed attempts before
  declaring the peer dead and taking action.
