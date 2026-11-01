# FortiOS 7.6.7 CLI Deep Reference

All facts below verified against the official FortiNet 7.6.7 PDF corpus (36 documents).
Citation keys: [CLI Ref] = FortiOS 7.6.7 CLI Reference; [AG] = FortiOS 7.6.7 Administration Guide; [RN] = FortiOS 7.6.7 Release Notes.

## CLI basics

- Two planes: read-only (`get`, `show`, `execute ... list/stat`) and read-write (`config ... end`, `execute ...`).
- Verify state: `get system status` (firmware version, build, HA role), `get system time`, `get system performance status [cpu|memory|session|disk]`.
- `show system interface [list]` — interface status, IP, link. `show system ha status` — cluster role/membership.
- Policy objects: `show firewall policy [<id>]`, `show firewall address [<name>]`, `show firewall service custom [<name>]`, `show firewall ippool [<name>]`.
- In `config firewall policy` blocks, iterate entries with `edit <id>` ... `next`; leave with `end`.
- 7.6.x: firewall policies accept `set name <string>` in addition to the numeric id.
- Automation note: since 7.6.x the CLI prompt includes the HA role, e.g. `FortiGate(Secondary) (global) #` — scripts that match fixed prompt patterns (Ansible, regex banners) can break. [RN, Changes in default behavior, bug 1256231]

## firewall policy (key fields) [CLI Ref, config firewall policy]

```
config firewall policy
    edit <id>
        set name <string>                 # 7.6.x named policies
        set action {accept|deny|all}
        set schedule {none|<schedule-name>}
        set logtraffic {enable|disable}
        set nat {enable|disable}
        set srcintf <intf-or-zone> ...
        set dstintf <intf-or-zone> ...
        set srcaddr <name1>, <name2>, ...
        set dstaddr <name1>, <name2>, ...
        set srcaddr6 ...                  # IPv6
        set dstaddr6 ...
        set service <name1>, <name2>, ...
        set sslserver <hostname>
        set ipsensor <name>
        set application-list <name>
        set utm-profile <name>
        set shaper <name>
        set ippool <name>
        set priority {integer}
    next
end
```
Policy evaluation: first match wins; ordering via `set priority`. Interface members may be physical interfaces or zones (mutually exclusive per entry).

## firewall address [CLI Ref]

```
config firewall address
    edit <name>
        set subnet <ipv4-classnet>        # e.g. 10.0.0.0/24
        set iprange <ip1> <ip2>
        set fqdn <hostname>
        set geo ip <user>                # geo-IP
        set interface <intf>             # address of an interface
        set allow-routing {enable|disable}
        set comment <string>
        config member                     # grouped addresses
            edit <member-name>
            next
        end
    next
end
```
IPv6 addresses use `set subnet` with an IPv6 prefix in dedicated `address6` objects.

## firewall service custom [CLI Ref]

```
config firewall service custom
    edit <name>
        set protocol {TCP|UDP|ICMP|...}
        config ports
            edit <port-or-range>          # e.g. 8080-8090
            next
        end
        set comment <string>
    next
end
```
Built-in services are `ALL-ICMP`, `ALL-TCP`, `ALL-UDP`, `ANY`, `DNS`, `HTTPS`, `HTTP`, `SSH`, `SMTP`, etc. (system service objects; read-only).

## firewall ippool [CLI Ref]

```
config firewall ippool
    edit <name>
        set iprange <ip1> <ip2>
        set type {basic|portforward|static-nat|dynamic-nat|cgn}
        set interface <intf>
        set override {enable|disable}
    next
end
```
CGN pools (NP7 platforms) have additional fields (e.g. `cgn-block-size`, `cgn-resource-quota`). Hyperscale/NP7 caveat: with overload PBA IP pool, only one block is allocated per client and `cgn-resource-quota` is ignored (NP7 hardware limitation). [RN, Special notices]

## firewall zone [CLI Ref]

```
config firewall zone
    edit <name>
        set member <intf1>, <intf2>, ...
        set comment <string>
    next
end
```
Zones group interfaces for policy `srcintf`/`dstintf`. A policy entry references either zones or individual interfaces, not both.

## system global [CLI Ref]

```
config system global
    set hostname <string>
    set timezone <tz>
    set vdom-mode {single|multi}
    set admin-http-rate-limit-max-requests {integer}   # set 0 to disable HTTP rate limiting
    set private-data-encryption {enable|disable}
    set web-svc-auto-restart {enable|disable}
end
```
Notable 7.6.x behavior:
- `private-data-encryption` (7.6.1+) generates a random key when enabled (no manual 32-hex key). A config backed up with random key A cannot be restored after the key is regenerated (disable + re-enable = new key). CLI warns: "Previous config files encrypted with the private key cannot be restored after this operation!" [RN, Special notices]
- `admin-http-rate-limit-max-requests 0` is the documented workaround for blank-GUI-after-upgrade issue. [RN, Known issues, bug 1306049]

## system settings [CLI Ref]

```
config system settings
    set admin-skip-login {enable|disable}
    set login-attempt-max {integer}
    set idle-timeout-min {integer}
    set auto-save {integer}
end
```

## system interface [CLI Ref]

```
config system interface
    edit port1
        set alias <string>
        setip allowstatic                 # static IP (classic form)
        set ip <addr>/<mask>              # e.g. 192.168.1.1/24 (7.x form)
        set type {physical|...}
        set role {wan|lan}
        set vdom <name>
        set allowaccess ping https ssh http fgfm
        config ipv6
            set ip6 <ipv6-addr>
        end
    next
end
```
`allowaccess` controls which management services may use the interface (list: ping, http, https, ssh, fgfm, and others).

## router objects [CLI Ref]

Static routes:
```
config router static
    edit <id>
        set device <interface>
        set gateway <ipv4-address>
        set distance {integer}
    next
end
config router static6
    edit <id>
        set device <interface>
        set gateway6 <ipv6-address>
    next
end
```

BGP:
```
config router bgp
    set as {integer}
    set router-id <ipv4-address>
    set preference {local|global}
    set graceful-restart {enable|disable}
    config neighbor
        edit <name>
            set remote-as {integer}
            set password <string>
        next
    end
end
```

## vpn ssl (web portal) [CLI Ref]

```
config vpn ssl settings
    set default-server-certificate <cert-name>
    set ca-cert <cert-name>
    set stunnel-port {integer}
    config client
        edit <name>
            set certificate <cert-name>
            set ssl-versions {ssl3|tls1.0|tls1.1|tls1.2|tls1.3}
        next
    end
end
config vpn ssl web portal
    edit <name>
        set status {enable|disable}
        set default-login-page {<page>}
        config login-page
            edit <name>
            next
        end
    next
end
```
7.6.x naming: SSL VPN "web mode" is now branded **Agentless VPN** and is not supported on some FortiGate series/models (see [RN] Special notices; [AG] migration chapter).

## system api-user [CLI Ref]

```
config system api-user
    edit <name>
        set status {enable|disable}
        set method {password|token}
        set expiration {none|...}
    next
end
# Token (re)generation with expiry:
execute api-user generate-key <name> [expiry in minutes]   # expiry 1-10080 minutes
```
Token-based API auth: Bearer token, HTTPS enforced (HTTP refused). [AG, REST API chapter]

## diagnose essentials (read-only) [CLI Ref, AG]

```
diagnose sys session list              # active sessions: status, flags, timeouts, src/dst ip:port, protocol, serial
diagnose sys performance status        # cpu/mem/session/disk counters
diagnose ip pool stat                  # IP pool usage
diagnose vpn tunnel list               # IPsec tunnel state
diagnose vpn ike ...                   # IKE statistics subcommands
diagnose sniffer packet <interface> '<bpf-filter>' <decode> [l]
```
Verified sniffer examples [AG]:
```
diagnose sniffer packet any 'icmp or (udp and port 4789)' 4 0
diagnose sniffer packet any 'host 10.10.100.20 or (udp and host 192.168.2.87)' 4 0 l
diagnose sniffer packet port2 ""
```
Decode level 0-5 (0 = none, higher = more decoded); `l` = continuous live output.

Config-integrity check after upgrade [RN, bug 1277454 workaround]:
```
show system global diagnose debug config-error-log read
```

## 7.6.7 CLI changes [RN, Changes in CLI]

- 895242: FortiGate-6000/7000 default HA upgrade mode changed from `simultaneous` to `uninterruptible`.
- 1236596: `config firewall profile-protocol-options > config http > set streaming-content-scan-type` default now includes `octet` (application/octet-stream files scanned/submitted to FortiSandbox even when streaming-content-bypass is enabled).
- 1238936: SFP speed-detect option renamed `auto-module` -> `detect-by-module`.
- 1266730: `arp-reply` supported on IPv4/IPv6 firewall VIPs, enabled by default; disable via `config firewall vip > set arp-reply disable`.

## 7.6.7 default-value changes [RN]

- 1248524: default MTU for IPsec tunnel interfaces changed 1420 -> 1402. On 8.0.0 for selected models; on **8.0.1/7.6.7 across all FortiGate models**.
