---
name: hermes-it-infosec-fw-fortig-fortios-7-6-7
version: 4.2.0
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

Surfaces = physical doc builds under the corpus root (today:
`fortios-7.6x/` and `fortios-8.0x/`; new product/line builds are added
as sibling dirs). Pieces = logical domains that span surfaces. Each piece is a real skill in the
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
- **8.x line:** the 8.0 line ONLY (8.0.0 GA, **8.0.2** latest patch,
  2026-10-22 build 0251 RN). FortiOS 8.2 / 8.4 do NOT exist on
docs.fortinet.com.
- 7.4.x and 7.2.x lines are NOT in the corpus — extend before answering
  in depth (Self-improvement below).
- **Surfaces are version-isolated:** `fortios-7.6x/` holds only 7.6.x
docs; `fortios-8.0x/` holds only 8.0.x docs (the 13 8.0.x docs were
carved out of the 7.6x build in 2026-11-01). Always pass the matching
`--line` filter (7.6x or 8.0x) — the root enforces the filter unless
`--general`.

## Corpus + RAG runbook

Corpus root: `/home/chrismok/fortinet-corpus/` (persistent; data never
leaves the host).

```
fortinet-corpus/
  PIPELINE.md            <- pipeline setup + full data contract (read this first)
  compile_root.py        <- compiles all surface collections -> root/kb (collection 'fortinet-root')
  query_root.py          <- queries the root index with a REQUIRED product/line filter
  pieces/                <- 12 piece cards: PIECE.md + manifest.json (+ collection config, exam tags)
  fortios-7.6x/          <- 7.6.x surface build (CORPUS.md card, pdfs/, text/, chunks.jsonl,
                             kb/ = chroma + collection.json, eval/, scripts/); 43,528 vectors
  fortios-8.0x/          <- 8.0.x surface build (same layout); 37,220 vectors, 25 docs
  root/kb/               <- compiled cross-surface index (derived; rebuild anytime);
                             80,748 vectors = both surfaces, IDs <surface>::<chunk>
```

**Query the root index** (all surfaces; filter is enforced unless
`--general`):

```
# ONNX embedding model caches at /home/chrismok/.cache/chroma-onnx —
# mount it so the 79MB model is fetched once, not per query.
docker run --rm --mount type=bind,src=/home/chrismok/fortinet-corpus,dst=/home/chrismok/fortinet-corpus \
  --mount type=bind,src=/home/chrismok/.cache/chroma-onnx,dst=/root/.cache/chroma \
  zeppo-rag:cli python3 /home/chrismok/fortinet-corpus/query_root.py "<question>" 12 \
  --product fortios --line 7.6x        # or --line 8.0x for the 8.0 surface
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
   image (chromadb, sentence-transformers; **pymupdf is NOT in the
   image** — `pip install -q pymupdf` inside the ephemeral container
   before running extract_pdfs.py). Bind-mount the surface you're
   working on at the path the script hardcodes (extract_pdfs.py uses
   `ROOT=/work` — mount the SURFACE dir at /work, not the corpus root);
   no published ports; kill it when done (`docker ps` diff = 0). Never touch `zeppo-rag-cli` or `/home/zeppo`;
   never disturb the vLLM brain (:8081) or the Arc GPU (embeddings are
   CPU-only by design).
2. **Pick the gap.** Product (FortiManager 7.6?), version line (7.4.x?),
   or topic (FortiMail 7.6?). Check the surface `text/` first — you may
   already have the doc. Docs for an existing surface APPEND to that
   build; a new product/line gets a NEW sibling dir + its own
   `CORPUS.md` card. **A doc lives in exactly ONE surface** (root IDs are
   surface-namespaced): when carving docs out into a new surface, split
   `chunks.jsonl`, move the pdfs/ + text/ files, remove the moved chunks
   from the OLD surface's Chroma collection, and recompile the root in
   full — the same doc embedded under two surfaces duplicates vectors in
   the root.
3. **Fetch official docs** (docs.fortinet.com PDF variants; Fortinet S3
   fallback; some 8.0.0 S3 objects 403 -> use the 8.0.2 variant). The doc
   page HTML carries the direct PDF link — regex
   `https://fortinetweb[^"']*.pdf`; the product page
   `/product/fortigate/<train>` is the full doc catalog. Some docs are
   **web-only** (no PDF link in any version — e.g. FortiGate MIB info
   overview): crawl the hub page plus all chapter sub-pages
   (`/document/fortigate/<ver>/<slug>/<chapter-id>/<chapter-slug>`),
   convert to the extractor's marked-text format (`<<<Hn|...>>>`
   headings, table rows as `a | b`), and chunk with the same
   `chunk_doc()`. A full-set surface must NOT silently skip a missing
   doc — web-crawl it.
   Field knowledge: community crawl (`crawl_field.py`) — field reports
   only, never official behavior.
4. **Extract** (`extract_pdfs.py` -> `text/` + `chunks.jsonl`; APPEND
   only — the embedding DB is keyed by chunk ID).
5. **Embed** (`embed.py`, CPU MiniLM-L6-v2; ~21 min / ~75k chunks; embed
   **embed only NEW chunks or rebuild for a full retrain.)** The surface
   `embed.py` MUST also write `kb/collection.json` (`{"name":
   "<collection>","model":"MiniLM-L6-v2","dim":384}`) — without it
   `compile_root.py` silently skips the surface.
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
bad retrieval; missing `kb/collection.json` -> `compile_root.py`
silently skips a surface (root count looks fine but one surface is
absent — always verify per-surface lines in the compile log); thinking model without `enable_thinking: false` ->
GEN_FAILs; `scores.jsonl` not archived -> corrupt fresh scores; Chroma
bulk `get()` on >~900 IDs -> SQLite variable limit (batch;
`compile_root.py` already does); chromadb `query()`/`get()` return
documents=None unless `include=["documents", ...]` is passed;
non-detached `docker exec` dies at the session boundary, killing long
compiles (use `docker run` from a background terminal, or
`docker exec -d ... sh -c 'nohup ... > log 2>&1'`); `docker ps -q
--filter ancestor=<image> | xargs docker kill` kills EVERY container
from that image — when the image is shared (zeppo-rag:cli), target
cleanup by specific container name/id; f-string/heredoc
quoting in probe one-liners -> standalone .py files; background-process
completion notifications arrive LATE — even for rounds already tracked to
DONE — so treat them as status, re-read the run log, and never restart
work from one (hit 7x during R1-R4); container-written corpus files are
root-owned (host user cannot rewrite them) — do file surgery (chunk splits,
moves, rewrites) inside an ephemeral root container, not from host-side
python; detached `docker run -d ... > log` captures only the container ID,
never the job output — verify results on the filesystem or `docker logs`
before `--rm` deletes the container.

## Exam state

Two harnesses on the 7.6x 92-question piece-tagged exam (`eval/questions.jsonl`),
plus the 8.0x slice exam (12 questions, `fortios-8.0x/eval/questions.jsonl`:
6 platform / 4 hardware / 2 policy; all "enumerate N verified 8.0.x facts" style):
- **Surface exam** (legacy, `run_eval.py` against the surface collection): best 76.1% (70/92).
- **Root exam 7.6x** (live-client path, `eval_root.py`): strict R1 40.2 -> R2 59.8 -> R3 63.0 -> R4 59.8 -> **R5 60.9**; weighted 62.3 -> 74.7 -> 78.0 -> 78.8 -> **79.6** (>=50% threshold: 90.2% in R5). vpn 9/9 (100%) all 5 rounds; platform 90%, auth 92% weighted in R5. R2-R5 plateau = judge strictness + sampling; content enrichment exhausted. **Practical release gate MET** (weighted >=75% x3, strict >=60% x3).
- **Root exam 8.0x** (`eval_root.py fortios-8.0x fortios 8.0x FortiGate`): **R1 = strict 33.3%, weighted 63.0%** (>=50%: 9/12). Failure mode DIFFERENT from 7.6x: the 10 non-zero questions average ~78% of their key points; the two zero scores (r80-01 8.0.0 network new features, r80-05 8.0.1 NP7 new features) are RETRIEVAL RANKING misses — the exact "What's new for X" chunks exist in the corpus (e.g. c036321 in fortios-hardware-acceleration-802) but do not rank in top-16 for "enumerate new features in version X" questions. Fix candidates: bigger K for eval, or question rephrasing toward the section name.
`eval_root.py` / `score_root.py` are parameterized: `<surface> <product> <line> <product_name>` / `<answers> <scores> [surface]` (defaults = 7.6x).

## Release
Public release: `github.com/ChrisL2000/fortinet-skills` (tag v4.2.0, 2026-11-01) — router + 12 piece
skills, all pipeline scripts, exams, README. v4.2.0 adds the fortios-8.0x surface
(25 docs; 7.6x/8.0x version isolation) + parameterized eval/score scripts. Vendor doc text and
vector stores are never shipped (proprietary, data stays on-host); the repo README documents the
build-from-scratch path. Re-sync the repo when the family next changes.
