# FortiOS 7.6.7 REST API v2 Deep Reference

Verified against the FortiOS 7.6.7 Administration Guide (public REST API chapters) and the 7.6.7 CLI Reference.

## Scope limitation (important)

The **complete** FortiOS REST API v2 reference (full endpoint catalog, per-object schemas, request/response field tables) is **not published** on docs.fortinet.com — it requires a FortiSupport subscription (FNDN/FKYC) via the FortiOS Developer Program / FortiAPI docs. This reference covers what the public 7.6.7 Administration Guide documents: authentication, URL structure, call patterns, and the endpoint families the guide demonstrates. When an answer needs a field-level schema not in the public docs, say so and point to the subscription API reference rather than guessing.

## Authentication [AG, System > REST API chapter, ~p.4080-4086]

1. Create an API user:
```
config system api-user
    edit <name>
        set status enable
        set method token
    next
end
```
2. Generate (or regenerate) the token, optionally with expiry (1 - 10080 minutes):
```
execute api-user generate-key <API username> [expiry in minutes]
```
Configuring an expiry is documented as good practice. [AG, "Configuring token expiry", p.4085-4086]

3. Auth header: `Authorization: Bearer <API-TOKEN>`
4. **HTTPS is enforced** — HTTP cannot be used for API calls. [AG]
5. Optional hardening: configure a **PKI group** on the API user so that both the client certificate and the token must match (peer authentication). The PKI group is typically the name of a peer group defined under `config user group` with PKI members. [AG]
6. CORS: for third-party web apps, specify `Access-Control-Allow-Origin` on API responses; avoid using `*`. [AG]

## URL structure [AG]

Base: `https://<FortiGate_address>:443/api/v2/...` (default port 443, no need to state explicitly).

Two object families:
- **CMDB** (configuration objects, mutable state): `/api/v2/cmdb/<category>/<object>[/<id>]`
- **Monitor** (live state and actions): `/api/v2/monitor/<category>/<object>[/<path>]`

Documented endpoint examples from the 7.6.7 guide:

CMDB:
- `/api/v2/cmdb/firewall/address` — all firewall addresses (the guide's canonical "simplest API call")
- `/api/v2/cmdb/firewall/address/<id>` — single object by id
- `/api/v2/cmdb/system/admin` — admin accounts
- `/api/v2/cmdb/log.fortianalyzer/setting` — FortiAnalyzer logging settings

Monitor (live data):
- `/api/v2/monitor/license/status`
- `/api/v2/monitor/system/firmware`
- `/api/v2/monitor/system/usb-log`
- `/api/v2/monitor/system/sandbox/connection`
- `/api/v2/monitor/system/external-resource/dynamic`
- `/api/v2/monitor/system/automation-stitch/webhook/auto_webhook`
- `/api/v2/monitor/virtual-wan/health-check`
- `/api/v2/monitor/virtual-wan/sla-log`
- `/api/v2/monitor/virtual-wan/interface-log`
- `/api/v2/monitor/system/security-rating/`

Monitor (actions, e.g. certificate management):
- `/api/v2/monitor/vpn-certificate/ca/import`
- `/api/v2/monitor/vpn-certificate/local/import`
- `/api/v2/monitor/vpn-certificate/remote/import`
- `/api/v2/monitor/vpn-certificate/crl/import`
- `/api/v2/monitor/vpn-certificate/csr/generate`

## Call pattern (verified verbatim) [AG, ~p.4086]

```
curl --insecure \
  -H "Accept: application/json" \
  -H "Authorization: Bearer <API-TOKEN>" \
  https://<FortiGate_address>/api/v2/cmdb/firewall/address
```
Postman: disable SSL certificate verification (Settings > General), new HTTP request, set the Bearer header.

The public 7.6.7 guide demonstrates **GET** examples; mutation verbs (POST create / PUT update / DELETE) follow the standard v2 REST patterns but their per-object request bodies are covered only in the subscription API reference — verify against that source or against a lab before scripting writes.

## Operational notes

- API users are VDOM-scoped: an API user created in one VDOM can address that VDOM's objects; cross-VDOM access follows VDOM mode rules. (Confirm VDOM context before multi-VDOM automation.)
- The GUI "System > REST API" page and the CLI `config system api-user` are the same store.
- Token expiry: if set, the token stops working after the expiry window; regenerate with `execute api-user generate-key`.
- For bulk config management, FortiManager/FortiGate-REST are complementary: REST API v2 is the per-device surface; FortiManager provides device-group operations.

## Verification commands (CLI side)

```
show system api-user
execute api-user generate-key <name>        # re-issuing the token
```
