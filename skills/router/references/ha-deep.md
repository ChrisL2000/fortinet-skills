# FortiOS 7.6.7 High Availability Deep Reference

Verified against the FortiOS 7.6.7 CLI Reference (`config system ha`, full field set) and Administration Guide (HA chapter, ~p.3706-3750: FGCP/FGSP/VRRP, primary unit selection p.3743-3746).

## HA modes and solutions [AG]

- **FGCP** (FortiGate Clustering Protocol): device failover, link failover, remote link failover, session synchronization (most IPv4/IPv6 sessions), active-active load balancing.
- **FGSP** (FortiGate Session Life Support Protocol): session sync between FortiGates/standalone units behind an external load balancer; syncs IPv4/IPv6 TCP, SCTP, UDP, ICMP, expectation, NAT sessions; the LB performs failover.
- **VRRP**: FortiGate as primary/backup VRRP router; VRRP v2 and v3 supported; integrates with third-party VRRP devices.

## config system ha — verified field list [CLI Ref]

Modes:
```
set mode {standalone|a-p|a-a}        # a-p = active-passive, a-a = active-active
set group-id {integer}               # cluster id
set group-name {string}
```
Heartbeat and monitoring:
```
set hbdev <if1>, <if2>, ...          # heartbeat interfaces (list)
set backup-hbdev <if1>, ...
set monitor <if1>, <if2>, ...        # monitored interfaces for failover detection
set ha-direct {enable|disable}       # direct heartbeat over the same IP
set hb-interval {integer}
set hb-lost-threshold {integer}
set unicast-hb {enable|disable}
set unicast-hb-peerip {ipv4-address}
set unicast-hb-netmask {ipv4-netmask}
set unicast-gateway {ipv4-address}
config unicast-peers
    edit <id>
        set peer-ip {ipv4-address}
        set unicast-status {enable|disable}
    next
end
```
Primary-unit election:
```
set priority {integer}               # 0-255, default 128; NOT synchronized
set override {enable|disable}        # default disable
set override-wait-time {integer}     # 0-3600 s, only when override enabled
```
Session failover:
```
set session-pickup {enable|disable}
set session-pickup-delay {enable|disable}
set session-pickup-connectionless {enable|disable}
set session-pickup-expectation {enable|disable}
set session-pickup-nat {enable|disable}
set session-sync-dev <dev>
```
Sync and misc:
```
set key {password}                   # sync passphrase
set password {password}
set sync-config {enable|disable}
set upgrade-mode {simultaneous|uninterruptible|...}
set gratuitous-arps {enable|disable}
set check-secondary-dev-health {enable|disable}
set memory-based-failover {enable|disable}
set memory-threshold {user}          # memory-based failover threshold
set cpu-threshold {user}
config vcluster
    edit <vcluster-id>
        set priority {integer}
        set monitor <if-list>
        set override {enable|disable}
        set vdom <name1>, <name2>, ...
        set weight {user}
        set vcluster-status {enable|disable}
    next
end
config ha-mgmt-interfaces
    edit <id>
        set interface {string}
        set dst {ipv4-classnet}
        set gateway {ipv4-address}
        set ha-mgmt-status {enable|disable}
    next
end
```

## Primary unit selection [AG, p.3743-3746]

Selection triggers: (1) two or more units initially form a cluster, (2) a new unit joins, (3) a device failover (primary fails), (4) a link failover (monitored interface fails or is restored).

Criteria inputs:
- **Priority**: 0-255, default 128, not synchronized across members.
- **Monitor**: interfaces checked for physical link failure (physical, aggregate, redundant interfaces supported).
- **Override**: enable = priority value wins over uptime; disable (default) = uptime wins over priority.
  - Standardize override across ALL members — mixed enable/disable causes conflicts and unpredictable elections.

Order of criteria:
- **Override disabled on all members**: HA uptime, then session count, then firmware version, then serial number (the docs abbreviate this order "MUPS"; full table on p.3744).
- **Override enabled on all members**: priority evaluated first (docs abbreviate "MPUS"; table on p.3745).
- Ties advance to the next criterion. HA uptime rule: if the uptime difference is > 300 s the longer-running unit wins; if < 300 s it is a tie. A monitored-interface failure or a member restart resets that unit's HA uptime to zero.

Override wait time [AG, p.3745-3746]:
- With override enabled, a higher-priority unit would take over immediately at boot; `set override-wait-time <seconds>` (0-3600, default 0) delays takeover so the unit can sync sessions and obtain DHCP/PPPoE addresses first.
- Only configurable when override is enabled (hidden otherwise). NOT synchronized — set manually on each unit.
- Active only after a boot (not after a monitored-interface failover, not after a mode change). During the wait the booted unit is treated as lowest priority ("reverse priority"). After expiry the cluster renegotiates and the higher-priority unit takes over, sending gratuitous ARP.
- Emergency failover is never delayed (monitored-interface failure overrides the wait).
- Simultaneous boot of both units with wait > 0 causes the lower-priority unit to be primary during the wait, then a failover — two gratuitous ARPs in quick succession can destabilize the network; for power-outage/DR tests set wait to 0.
- `diagnose sys ha history read` may show the `OVERRIDE_WAIT` flag on the peer during the wait period.

## 7.6.7-specific HA notes [RN]

- 895242: FortiGate-6000/7000 default HA upgrade mode changed from simultaneous to **uninterruptible** (CLI change in 7.6.x).
- 1256231: CLI prompt now shows the HA role — `FortiGate(Secondary) (global) #`. Breaks automation relying on fixed prompts.
- Memory-based failover options (`memory-based-failover`, `memory-threshold`, `memory-failover-*`) govern failover on memory pressure rather than only link/monitor failures.

## Verification commands (verified in 7.6.7 corpus)

```
get system status                # includes HA role (7.6.x prompt shows it too)
execute ha failover status       # HA failover state
get system performance status    # per-unit load
```
`show system ha status` / `diagnose sys ha ...` are NOT in the 7.6.7 corpus —
do not cite them without a live-box check.

## Unicast HA quick pattern

For sites without a dedicated heartbeat link:
```
config system ha
    set mode a-p
    set group-id 1
    set unicast-hb enable
    set unicast-hb-peerip <peer-ip>
    set unicast-hb-netmask <mask>
    set unicast-gateway <gw>
    set hbdev <mgmt-if>
end
```
