---
name: fortinet-proxy-ztna-casb
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet proxy, ZTNA, CASB: web proxy, CASB profile"
metadata:
  hermes:
    piece: proxy-ztna-casb
    surface: fortios-7.6x
    depends_on: [sdpwan]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 6/92 questions tagged piece=proxy-ztna-casb
    piece_card: /home/chrismok/fortinet-corpus/pieces/proxy-ztna-casb/PIECE.md
    tags: [fortios, web-proxy, ztna, casb, fwdns]
---

# FortiNet proxy / ZTNA / CASB piece

Web proxy (explicit + forward), ZTNA web proxy, CASB profiles, FQDN-based CASB rules. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2). Load `fortinet-sdpwan` first (ZTNA web-proxy policies attach to SD-WAN members).

## Web proxy (`config firewall web-proxy` / `proxy-policy`)

- **Explicit web proxy** (7.6.8 AG p365, verified): `config web-proxy explicit` — `set status enable`, `set ftp-over-http enable`, `set socks enable`, `set http-incoming-port 8080`, `set ipv6-status enable` + listen interface. GUI: System > Feature Visibility > Explicit Proxy, then Network > Explicit Proxy. Clients point browsers (or a PAC file) at the FortiGate IP.
- **Other `config web-proxy` sub-objects (7.6.8 CLI Ref index, verified):** `debug-url`, `explicit`, `fast-fallback`, `forward-server`, `forward-server-group`, `global`, `isolator-server`, `profile`, `url-match`, `wisp` — explicit web proxy configuration spans `explicit` (status/ports/socks/ftp-over-http), `profile` (authentication + forwarding profile), `global` (global proxy settings), `url-match`, `forward-server`/`forward-server-group`, `fast-fallback`, `isolator-server`, `wisp`, `debug-url`.
- **Proxy firewall policies** `config firewall proxy-policy` (IPv4) / `proxy-policy6` (IPv6), verified field set: `set proxy [explicit-web-proxy|transparent-web-proxy|access-proxy|...]` (selects proxy mode), `set access-proxy <name>` (references a ZTNA access-proxy object), `set srcintf`/`set dstintf`/`set srcaddr`/`set dstaddr`/`set service`/`set schedule`, `set ssl-ssh-profile` (deep SSL inspection), `set utm-status enable`, `set casb-profile <prof>`, `set dlp-profile <prof>`, `set isolator-server` (isolates traffic in logs), `set log-http-transaction` (HTTP transaction logging for explicit/transparent/access proxy). 8.0.0 adds per-policy `set poolname6` (IPv6 pool) — platform piece.
- **ZTNA (access proxy)** — verified 7.6.8 AG p447-448 (mTLS example): (1) VIP: `config firewall vip > edit "mTLS" > set type access-proxy` (+ `set client-cert enable` for mTLS, `set ssl-certificate`, `set extintf`/`set extip`/`set extport`); (2) access-proxy object: `config firewall access-proxy > edit "mTLS-access-proxy" > set vip "mTLS" > config api-gateway > edit 1 > config realservers > edit 1 > set ip 172.16.200.44`; (3) proxy policy: `set proxy access-proxy` + `set access-proxy "mTLS-access-proxy"` + auth + deep SSL inspection. `config ztna web-proxy` (7.6.8 CLI Ref p2799, verified) is the companion ZTNA web-proxy object: under `config api-gateway` — `set ldb-method`, `set persistence [none|http-cookie]` (client affinity), nested `config quic` (QUIC settings); under `config realservers > edit <id>` — `set addr-type [ip|fqdn]`, `set address {string}` / `set ip {ipv4-address-any}`, `set port {integer}`, `set status [active|standby|...]`, `set health-check [disable|enable]` + `set health-check-proto [ping|http|...]` (real-server health check), `set verify-cert [enable|disable]` (backend certificate validation), `set weight {integer}` (load balancing), `set translate-host`, plus `config ssl-cipher-suites` (priority-ordered). An `api-gateway6` variant exists for IPv6. ZTNA web-proxy policies typically attach to an SD-WAN member interface. `config ztna reverse-connector` (7.6.8 CLI Ref p2786) defines ZTNA reverse-connector objects for reverse-connection (outbound-only) ZTNA deployments.
- **CASB-profile attachment requirements (7.6.8 CLI Ref, verified):** the proxy policy needs an `ssl-ssh-profile` configured for **deep SSL inspection** and `set utm-status enable` — or the CASB profile does not apply.

## CASB — verified object set (7.6.8 CLI Ref p218-228)

`config casb` sub-objects: `attribute-match`, `profile`, `saas-application`, `user-activity`.

- SaaS applications: `config casb saas-application` — `edit <app>` / `set name`, `set domain <fqdn>` (the SaaS app FQDN).
- Profile (attached to the proxy policy via `set casb-profile`): `config casb profile` — `edit <prof>` / `set comment`; nested `config saas-application` > `edit <name>` with nested `config access-rule` > `edit <name>`:
```
config casb profile
    edit "SaaS-CASB"
        config saas-application
            edit "Salesforce"
                config access-rule
                    edit "rule1"
                        set action [monitor|bypass|...]
                        config attribute-filter
                            edit 1
                                set action [monitor|bypass|...]
                                set attribute-match {string}
                        next
                    next
                next
            next
        next
    end
```
access-rule also carries `config advanced-tenant-control` and `config custom-control`; the saas-application level has `set domain-control [enable|disable]`, `set domain-control-domains`, `set log [enable|disable]`.
- **7.6.x CASB path (verified):** `config casb profile > saas-application > access-rule > action [monitor|bypass|...]` — there is NO top-level `config casb access-rule` object.
- FQDN-based CASB: match on the SaaS app FQDN (saas-application domain) rather than IP — use when the SaaS sits behind a CDN / dynamic IPs.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/proxy-ztna-casb/PIECE.md` + `manifest.json`. Exam slice: 5 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: proxy-ztna-casb`.
