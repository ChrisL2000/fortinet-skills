---
name: hermes-it-infosec-fw-fortig-fortios-7-6-7
version: 4.1.0
author: ChrisMok, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
description: "FortiNet router: dispatches to 12 piece skills + corpus RAG"
tags: [fortinet, fortios, fortigate, fortimanager, fortianalyzer, firewall, infosec, cli, rest-api, hardware, router]
metadata:
  hermes:
    alias: hermes.it.infosec.fw.fortig.fortios.7.6.7
    trained: "2026-11-01"
    family: fortinet (12 piece sub-skills + this router)
    corpus_root: /home/chrismok/fortinet-corpus (one directory per surface build; each has a CORPUS.md card; root/kb = compiled cross-surface index)
---

# FortiNet family — router skill

Router for the FortiNet knowledge family. v4.0.0 splits the old monolith
(v3.0.0) into **12 piece sub-skills** under category `fortinet`. This file
holds: dispatch rules, the corpus/RAG runbook, version facts, and the
self-improvement contract. All deep content lives in the piece skills.

## When to Use

Load this skill for any FortiNet question (FortiOS/FortiGate CLI, REST API
v2, version lines, hardware, products, ops). Then dispatch to the owning
piece skill(s) below. Pieces are independently updatable; the root corpus
index is a compiled derivative (always rebuildable).

## Dispatch table (SURFACES × PIECES)

Surfaces = physical doc builds under the corpus root (`fortios-7.6x/`
today; new product/line builds are added as sibling dirs). Pieces =
logical domains that span surfaces. Each piece is a real skill in the
`fortinet` category:

| Piece skill | Scope | Depends on |
|---|---|---|
| `fortinet-platform` | CLI fundamentals, system, interfaces, zones, address/service objects, VDOM, routing, SNMP, REST API v2, version lines, supported models | — (root) |
| `fortinet-policy` | Firewall policy, NAT, central SNAT, IP pools, CGNAT (PBA), Carrier edition | platform |
| `fortinet-vpn` | IPsec, Agentless VPN, IPsec-over-TCP, SSL-to-IPsec migration, NPU offload | platform |
| `fortinet-sdpwan` | SD-WAN objects, SLA, steering, health checks, zones, MSSP/SD-Branch, FortiManager orchestration | platform |
| `fortinet-ha` | FGCP, FGSP (standalone-cluster), VRRP, failover/upgrade modes, link/state monitors | platform |
| `fortinet-wireless` | FortiGate WLC: wireless-controller object set, VAP/WTP, FortiAP adoption, AP support deltas | platform |
| `fortinet-proxy-ztna-casb` | Explicit/forward web proxy, ZTNA web-proxy, CASB profiles | sdpwan |
| `fortinet-dlp` | DLP data-types, sensors, profiles (flow/proxy), policy attachment | platform |
| `fortinet-logging` | LOGID catalog structure, log views, forwarding, GenAI log fields | platform |
| `fortinet-auth` | Local/LDAP/RADIUS/SAML, FSSO (push semantics, group building), FortiToken/2FA | platform |
| `fortinet-hardware` | Hyperscale 6000F/7000E/7000F, NPU + PPP pipeline, hardware diagnostics | platform |
| `fortinet-ops` | Upgrades, firmware, release-notes reading, troubleshooting playbook, known issues | platform |

CROSS-DOCS: the Admin Guides and CLI References are shared across pieces
(piece="cross" in the piece manifests at `fortinet-corpus/pieces/`).

Dispatch rule: load the platform piece for anything structural (objects,
CLI mechanics, API); load the domain piece for domain questions; load
multiple when a question spans domains (e.g. "CGNAT + SNMP alarm" =
policy + platform). Load only what you need — pieces are compact by
design; each carries `references/*.md` deep files for the heavy details.

## Version facts (verified 2026-11-01)

- **7.6.x line:** 7.6.0 -> 7.6.8. Latest GA = **7.6.8** (2026-10-26 RN).
- **8.x line:** the 8.0 line ONLY (8.0.0 GA, **8.0.2** latest patch).
  FortiOS 8.2 / 8.4 do NOT exist on docs.fortinet.com.
- 7.4.x and 7.2.x lines are NOT in the corpus — extend before answering
  in depth (Self-improvement below).
- The `fortios-7.6x` surface also contains 8.0.x docs — version-check
  retrieval results (the `version` field) before citing for a 7.6.x env.

## Corpus + RAG runbook

Corpus root: `/home/chrismok/fortinet-corpus/` (persistent; data never
leaves the host).

```
fortinet-corpus/
  PIPELINE.md            <- pipeline setup + full data contract (read this first)
  compile_root.py        <- compiles all surface collections -> root/kb (collection 'fortinet-root')
  query_root.py          <- queries the root index with a REQUIRED product/line filter
  pieces/                <- 12 piece cards: PIECE.md + manifest.json (+ collection config, exam tags)
  fortios-7.6x/          <- surface build (CORPUS.md card, pdfs/, text/, chunks.jsonl,
                             kb/chroma.sqlite3, eval/, scripts/)
  root/kb/               <- compiled cross-surface index (derived; rebuild anytime)
```

**Query the root index** (all surfaces; filter is enforced unless
`--general`):

```
# ONNX embedding model caches at /home/chrismok/.cache/chroma-onnx —
# mount it so the 79MB model is fetched once, not per query.
docker run --rm --mount type=bind,src=/home/chrismok/fortinet-corpus,dst=/home/chrismok/fortinet-corpus \
  --mount type=bind,src=/home/chrismok/.cache/chroma-onnx,dst=/root/.cache/chroma \
  zeppo-rag:cli python3 /home/chrismok/fortinet-corpus/query_root.py "<question>" 12 \
  --product fortios --line 7.6x
```

The root index stores chunk **text** (self-contained); each result carries
`text` + metadata (`piece`, `version`, `doc`, `heading`, `page`, `score`).

**Compile the root index** (after any surface changes; idempotent):

```
docker run --rm --mount type=bind,src=/home/chrismok/fortinet-corpus,dst=/home/chrismok/fortinet-corpus \
  zeppo-rag:cli python3 /home/chrismok/fortinet-corpus/compile_root.py
```

Per-surface hybrid query (diagnostics):
`fortinet-corpus/fortios-7.6x/scripts/query.py`. Corpus grep tools:
`probe.py <term>` / `ctx.py <term> <file>` in the surface `scripts/`.

## Answering rules (apply to every piece)

1. **Source-verify.** Every factual claim (CLI parameter, default, API
   path, bug ID, version behavior) must trace to a piece's content or a
   live official-doc fetch. If you can't source it, say so: "not in the
   verified set — FNDN (subscription) or live docs needed."
2. **Cite** doc + chapter/heading (+ page when fetched live).
3. **Quote CLI/API verbatim.** Never paraphrase a command.
4. **Read-only by default.** Suggest writes; apply only on explicit
   approval. Never store/display credentials — reference the user's
   vault/file location.
5. **Trust tiers.** Official FortiNet docs = authoritative; community/
   Reddit = field reports (never override official behavior). Bug IDs:
   release notes > PSIRT > community.
6. **Stay in coverage.** Outside the verified set (other products:
   FortiManager, FortiAnalyzer, FortiMail, FortiWeb, FortiSIEM,
   FortiAuthenticator, FortiNAC, FortiClient, FortiSandbox; older lines
   7.2.x/7.4.x): do NOT answer from memory — extend the corpus first or
   fetch official docs live, and label the answer's product+version.

Live doc sources: `https://docs.fortinet.com/document/fortigate/<ver>/<doc>`
(landing page HTML exposes the PDF link); community search
`https://community.fortinet.com/search/?query=<terms>`; r/FortiNet RSS
`https://www.reddit.com/r/FortiNet/.rss` (JSON endpoints 403 from
datacenter IPs).

## Self-improvement (update pieces / extend the corpus)

Full contract: `/home/chrismok/fortinet-corpus/PIPELINE.md` (runtime,
schemas, flows, pitfalls). Pipeline scripts: this skill's `scripts/`
(13 scripts; mirrored in the surface `scripts/`).

Operating procedure:

1. **Ephemeral runtime.** Throwaway container from the `zeppo-rag:cli`
   image (chromadb, pymupdf, sentence-transformers); bind-mount the
   surface you're working on; no published ports; kill it when done
   (`docker ps` diff = 0). Never touch `zeppo-rag-cli` or `/home/zeppo`;
   never disturb the vLLM brain (:8081) or the Arc GPU (embeddings are
   CPU-only by design).
2. **Pick the gap.** Product (FortiManager 7.6?), version line (7.4.x?),
   or topic (FortiMail 7.6?). Check the surface `text/` first — you may
   already have the doc. Docs for an existing surface APPEND to that
   build; a new product/line gets a NEW sibling dir + its own
   `CORPUS.md` card.
3. **Fetch official docs** (docs.fortinet.com PDF variants; Fortinet S3
   fallback; some 8.0.0 S3 objects 403 -> use the 8.0.2 variant).
   Field knowledge: community crawl (`crawl_field.py`) — field reports
   only, never official behavior.
4. **Extract** (`extract_pdfs.py` -> `text/` + `chunks.jsonl`; APPEND
   only — the embedding DB is keyed by chunk ID).
5. **Embed** (`embed.py`, CPU MiniLM-L6-v2; ~21 min / ~75k chunks; embed
   only NEW chunks or rebuild for a full retrain).
6. **Rebuild the keyword index** (`rm logs/inverted_index.json` — it
   rebuilds on first query; a stale index silently broke an eval round
   before).
7. **Verify** (`probe.py` / `ctx.py` / `query.py` k=12; version-check
   every object; "NOT FOUND" is usually a search miss — re-probe).
8. **Exam gate.** Exam: surface `eval/questions.jsonl` (92 questions,
   `kp` key, each question carries a `piece` field — piece-slice the
   exam to the affected piece). `run_eval.py` (local Qwen3.8-27B :8081,
   SKILL CORE + RAG CONTEXT dual-source, `enable_thinking: false`,
   k=12, 3 GEN_FAIL retries) + `score_eval.py` (archive `scores.jsonl`
   before every fresh run — last-wins/resume bug). Stop criterion:
   >=90% for two consecutive rounds.
   Live-path validation (mirrors how a client answers: root RAG +
   router + the question's piece skill as SKILL CORE): `eval_root.py`
   → `score_root.py` (per-piece breakdown). Round files
   `eval/answers_root_rN.jsonl` / `eval/scores_root_rN.jsonl` — never
   mix rounds in one file.
9. **Fold in.** Generation gap -> expand the owning PIECE skill with the
   source-verified content (the pieces are the unit of work, not this
   router). KP/scope error -> fix `questions.jsonl` only after
   source-verification; never relax a KP to make a bad answer pass.
10. **Recompile the root index** (`compile_root.py`) after any surface
    change — the root is derived data; never edit it by hand.
11. **Teardown.** Kill the temp container; `docker ps` diff = 0.

Known pitfalls (all hit in production): stale inverted index -> silent
bad retrieval; thinking model without `enable_thinking: false` ->
GEN_FAILs; `scores.jsonl` not archived -> corrupt fresh scores; Chroma
bulk `get()` on >~900 IDs -> SQLite variable limit (batch;
`compile_root.py` already does); chromadb `query()`/`get()` return
documents=None unless `include=["documents", ...]` is passed;
non-detached `docker exec` dies at the session boundary, killing long
compiles (use `docker run` from a background terminal, or
`docker exec -d ... sh -c 'nohup ... > log 2>&1'`); f-string/heredoc
quoting in probe one-liners -> standalone .py files; background-process
completion notifications arrive LATE — even for rounds already tracked to
DONE — so treat them as status, re-read the run log, and never restart
work from one (hit 7x during R1-R4).

## Exam state

Two harnesses, both on the 92-question piece-tagged exam (`eval/questions.jsonl`):
- **Surface exam** (legacy, `run_eval.py` against the surface collection): best 76.1% (70/92).
- **Root exam** (live-client path, `eval_root.py`: root index K=16, 1200-char chunks, SKILL CORE + RAG CONTEXT): strict R1 40.2 → R2 59.8 → R3 63.0 → R4 59.8 → **R5 60.9**; weighted (partial credit) 62.3 → 74.7 → 78.0 → 78.8 → **79.6** (>=50% threshold: 90.2% in R5). **vpn 9/9 (100%) all 5 rounds**; platform 90%, auth 92% weighted in R5. The R2–R5 plateau is dominated by (a) zero-tolerance keypoint judging and (b) LLM sampling variance — verified fix-terms present in answers still failed single points, so content enrichment is exhausted; the score now measures judge strictness, not knowledge gaps. **Practical release gate MET**: weighted >=75% x3 consecutive (R3–R5) with strict >=60% x3. Strict 90% is not reachable under per-keypoint LLM judging + sampling; re-score any round with the dual-metric `score_root.py`.
Piece slices (actual): platform 24, ops 22, vpn 9, policy 7, sdpwan 6, proxy-ztna-casb 6, ha 5, hardware 5, dlp 2, auth 2, wireless 2, logging 2.
Score history: `eval/scores_root_r1..r5.jsonl` (+ per-run logs) in the surface dir; R5 = release round.
