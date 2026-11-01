---
name: fortinet-dlp
version: 1.0.0
author: ChrisMok, Hermes Agent
license: MIT
description: "FortiNet DLP: data types, sensors, profiles, policy"
metadata:
  hermes:
    piece: dlp
    surface: fortios-7.6x
    depends_on: [platform]
    corpus: /home/chrismok/fortinet-corpus/fortios-7.6x
    exam: 2/92 questions tagged piece=dlp
    piece_card: /home/chrismok/fortinet-corpus/pieces/dlp/PIECE.md
    tags: [fortios, dlp, data-loss-prevention, sensors]
---

# FortiNet DLP piece

DLP data types, sensors, profiles, policy attachment, DLP logging. Source-verified for FortiOS 7.6.x (7.6.0-7.6.8) and 8.0.x (8.0.0-8.0.2).

## Object structure (7.6.8 CLI Ref p265-275, verified)

`config dlp` sub-objects: `data-type`, `dictionary`, `exact-data-match` (EDM templates), `filepattern`, `fp-doc-source`, `label`, `profile`, `sensitivity`, `sensor`, `settings`. **There is NO top-level `config dlp rule` in 7.6.x** — DLP rules nest inside `config dlp profile > config rule` (zero hits for top-level `config dlp rule` in the 7.6.7/7.6.8 CLI Refs).

- Sensors: `config dlp sensor` — consist of dictionaries and/or EDM templates; match any / all / logical combinations; can count match counts to trigger (7.6.8 AG).
- Data types: `config dlp data-type` (built-in categories + custom regex patterns).
- Profile: `config dlp profile` — `set name`, **`set feature-set [flow|proxy]`** (flow = firewall-policy path; proxy = web-proxy path), `set sensor <list>`, nested `config rule` (rule = sensor + file type/message + protocol match); actions per 7.6.8 AG: allow, log, block, quarantine.
- **Policy side:** firewall policy `set dlp-profile <prof>` + `set dlp-profile-status [enable|disable]`; proxy policy `set dlp-profile <prof>` + `set dlp-profile-status`.
- **Protocols (7.6.8 AG, "Protocol comparison between DLP inspection modes"):** the table covers HTTP, FTP, IMAP, POP3, SMTP, SFTP/SCP across inspection modes (flow vs proxy); TLS-wrapped variants need SSL/TLS decryption (deep SSL inspection) to be inspected.
- Backend: DLP uses Hyperscan one-parse pattern matching (7.6.8 AG). FortiGuard DLP service: 500+ predefined data patterns (7.6.8 AG).
- DLP log: extended LOGID fields (file name, data type, sensor, action, user) — logging piece.

## Retrieval

Root index with filter: `query_root.py "<q>" 12 --product fortios --line 7.6x` (runbook in the router skill). Version-check hits (surface contains 8.0.x docs too).

## Piece card / exam

Manifest + doc inventory: `/home/chrismok/fortinet-corpus/pieces/dlp/PIECE.md` + `manifest.json`. Exam slice: 5 questions in `fortinet-corpus/fortios-7.6x/eval/questions.jsonl` with `piece: dlp`.
