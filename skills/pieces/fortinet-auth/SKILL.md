---
name: fortinet-auth
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet auth: FSSO, LDAP/RADIUS, FortiToken, 2FA"
metadata:
  hermes:
    piece: auth
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 2/92 questions tagged piece=auth
    piece_card: /home/chrismok/fortinet-corpus/pieces/auth/PIECE.md
    tags: [fortios, authentication, fsoo, ldap, radius, forti-token, 2fa]
---

# FortiNet auth piece

User authentication: local users, LDAP, RADIUS, SAML, FSSO, FortiToken (2FA). Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Objects (CLI Ref-verified)

- **Local users:** `config user local` — `edit <user>` / `set type [local|...]`, `set password <pwd>` (hashes at rest), `set privileged-mode [enable|disable]`, `set two-factor-auth [enable|disable]`, `set auth-type [password|cert|...]`, `set token-policy` (FortiToken policy, 2FA). Local user sync across HA via `config system ha > set config-sync user-account` (ha piece).
- **LDAP:** `config user device` (LDAP/AD) — `edit <server>` / `set type [ldap|ad]`, `set server <ip>`, `set port 389` (or 636 for LDAPS), `set cn <cn>`, `set basedn <dc=...>`, `set bind-type [simple|...|none]`, `set bind-passwd`, `set group-cn` (AD group CN), `set member-of <filter>` (LDAP group membership filter), `set filter <filter>`, `set ca-cert` (LDAPS CA), `set starttls [enable|disable]`. AD groups: `config user device > config group` (AD group objects; `set ad-group <dn>`).
- **RADIUS:** `config user radius` — `edit <server>` / `set server <ip>`, `set port 1812`, `set shared-key <key>`, `set timeout`, `set retransmit`, `set nas-ipv4-address` (NAS-IP), `set coa-port` (Change of Authorization), `set nas-ipv6-address`.
- **SAML:** `config user saml` (SAML 2.0 IdP metadata, SP config) — `edit <profile>` / `set idp-metadata <url-or-file>`, `set sp-name`, `set sp-entity-id`, `set assertion-consumer-service`, `set name-id-format`.
- **FortiToken hardware (2FA):** `config user fortitoken` — `edit <serial_number>` registers/imports hardware FortiTokens (one object per token serial). GUI: **User & Authentication > FortiTokens > Import** for bulk import. Every FortiGate has two free mobile tokens (AG 7.6.7).
- **FTM / FortiIdentity Cloud:** `execute fortitoken-mobile import <FTM code>` (FTM license codes). The AG's 2FA section covers FortiToken Mobile push and FortiIdentity Cloud, including IPsec IKEv2 2FA with EAP and certificate authentication, and the two-factor filter used when synchronizing AD users to FortiIdentity Cloud.
- 2FA enforcement: `config user local > set two-factor-auth enable` + `set token-policy <policy>` (which token policy applies; e.g. `set two-factor fortitoken` in VPN profiles). FortiToken MFA also on web/API admin login (`config system global > set login-2fa [enable|disable]`).
- **FSSO:** see below (distinct from device-auth objects).

## FSSO (FortiSingle Sign-On) — verified semantics

- **Direction: the agent PUSHES logon info to the FortiGate** (TCP port 2100 by default; `config user fsso > set port 2100` / `set server <fg-ip>` on the agent side). The FortiGate does NOT pull from the agent.
- **The FortiGate BUILDS user groups locally** from the pushed logons (user groups are FortiGate-local objects created from FSSO logon data, not from the directory). Policy `srcaddr` references these FSSO groups.
- Agent types: Windows (agent service), Linux (agent), Active Directory (domain controller logging), NetScaler (NetScaler FSSO agent), ICA (Citrix), SSO proxy (web SSO for SaaS).
- Verify: `get user fsoo info` (FSSO status, active logons), `diagnose user fsoo list` (per-user FSSO logon details), `get user fsoo groups` (groups built from FSSO).
- FSSO is separate from LDAP/RADIUS device-auth: FSSO = passive logon observation for policy matching; device-auth = active credential check.

## FSSO — verified field list (7.6.8 CLI Ref p2131)

`config user fsso` — `edit <fsoo>` / `set name`, `set server <ip>` + `set server2..server5` (up to 5 agent servers), `set port <port>` + `set port2..port5` (agent push port; default 2100), `set status enable`, `set interface <if>` + `set interface-select-method [auto|sdwan|...]`, `set source-ip <ipv4>`, `set sni <sni>`, `set logon-timeout <sec>`, `set password <pwd>` + `set password2..5` (per-server auth), `set ldap-poll [enable|disable]` + `set ldap-poll-filter` + `set ldap-poll-interval` + `set ldap-server` (periodic LDAP polling supplements the push), `set group-poll-interval`.
- `config user fsso-polling` (7.6.8 CLI Ref p2135) — separate FSSO polling object.
- Push semantics (verified): the agent PUSHES logon info to the FortiGate; the FortiGate BUILDS user groups locally from the pushed logons — policy `srcaddr` references those FSSO groups. FSSO is passive logon observation for policy matching, not active credential checking (that is the LDAP/RADIUS/SAML device-auth objects above).
- Verify: `get user fsoo info`, `diagnose user fsoo list`, `get user fsoo groups`.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/auth/PIECE.md` + `manifest.json`. Exam slice: 5 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: auth`.
