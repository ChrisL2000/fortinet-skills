# Fortinet RAG Pipeline — setup & data contract

This document makes the pipeline reproducible: runtime contract, script
inventory, every data format, build-from-scratch and incremental-update
flows, and the pitfalls hit in production. Scripts live in each surface
build's `scripts/` (identical copies are vendored in the skill's
`scripts/`).

## Runtime contract

- Image: `zeppo-rag:cli` (chromadb, pymupdf/fitz, sentence-transformers,
  trafilatura, bs4, requests). Check with `scripts/probe_env.py`.
- Ephemeral container, surface mounted read-write at `/work`:
  ```
  docker run -d --name <tmp> \
    --mount type=bind,src=/home/chrismok/fortinet-corpus/<surface>,dst=/work \
    zeppo-rag:cli sleep infinity
  ```
- Constraints: no published ports; CPU-only embeddings (MiniLM-L6-v2,
  384-dim); never touch `zeppo-rag-cli`, `/home/zeppo`, or vLLM `:8081`
  (eval LLM only); data never leaves the host.
- MiniLM weights are pulled from the HF cache on first use inside the
  container — embedding needs network at that moment.
- Files written by container processes are root-owned; directories are
  chrismok-owned (see surface card provenance).

## Script inventory (13)

| script | role | usage |
|---|---|---|
| fetch_pdfs.py | fetch official FortiOS 7.6.x PDFs (pins newest version <= target with full PDFs) | container; → `pdfs/` + `logs/manifest.csv` |
| fetch_phase2.py | fetch 7.6.8 + 8.0.x + hardware doc sets | → `pdfs/` + `logs/manifest_phase2.csv` |
| crawl_field.py | search-crawl community.fortinet.com for 7.6.x field reports | → `field/pages/*.html` + `field/topics.jsonl` |
| crawl_field2.py | crawl explicit URL list (`field/crawl_urls.txt`, one per line) | same outputs |
| extract_pdfs.py | PDFs → `text/` with `<<<PAGE n>>>` / `<<<H1\|heading>>>` markers + `chunks.jsonl` | heading-aware ~700–1000 char chunks |
| embed.py | embed chunks + field topics into Chroma (MiniLM-L6-v2) | collection `fortios76`; skips existing IDs |
| append_ha802.py | worked example of incremental append (new doc → same collection, no rebuild) | pattern for add-doc |
| query.py | hybrid retrieval: Chroma vector + inverted-index keyword | `query.py "q" [k] [--alpha 0.55]` → JSON array |
| probe.py | grep a term across `text/` | `probe.py <term>` (ROOT resolved from script location) |
| ctx.py | context snippet around a hit | `ctx.py <term> <file> [width] [n]` |
| probe_env.py | runtime dependency check | diagnostic |
| run_eval.py | answer generation: retrieve → Qwen3.8-27B `:8081` (dual-source prompt: SKILL CORE + RAG CONTEXT; k=12; `enable_thinking: false`; 3 retries × 5s on GEN_FAIL) | `run_eval.py [qids_csv]` → `eval/answers.jsonl` |
| score_eval.py | LLM-judge key-point scoring → pass/fail per KP | → `eval/scores.jsonl` + summary |

Corpus-root scripts (live-client path; not per-surface — copies vendored in
the skill's `scripts/`):

| script | role | usage |
|---|---|---|
| compile_root.py | merge all surface collections into `root/kb` (collection `fortinet-root`); namespaced ids `<surface>::<chunk_id>`; metadata +surface/product/line/piece; **stores chunk text (documents)** resolved from each surface's `chunks.jsonl`; idempotent (skips existing ids) | container at corpus root; ~3 min per 75k vectors |
| query_root.py | root-index vector query with **required** product/line filter | `query_root.py "q" [k] --product fortios --line 7.6x` (`--general` skips filter) → JSON with text + metadata |
| eval_root.py | live-client exam: RAG via query_root.py + SKILL CORE (router + the question's piece skill) → Qwen `:8081` | `eval_root.py [out.jsonl] [qids_csv]` → `eval/answers_root_rN.jsonl` (resume-safe) |
| score_root.py | judge scoring of root rounds + **per-piece breakdown** | `score_root.py [answers.jsonl] [scores.jsonl]` → `eval/scores_root_rN.jsonl` |

`probe.py` / `ctx.py` resolve ROOT from their own location (parent of
`scripts/`) — portable across surface builds.

## Data contract

### chunks.jsonl
`{"chunk_id":"c000000","doc":"FortiOS-7.6.8-CLI_Reference","version":"7.6.8","heading":"...","page":2,"text":"..."}`
- `chunk_id`: zero-padded 7-digit, append-only, never renumbered
- `doc`: PDF stem; `version`: version string from the doc; `heading`:
  nearest H1; `page`: PDF page number

### text/*.txt
Extraction output, one file per doc, with `<<<PAGE n>>>` and
`<<<H1|heading>>>` markers (source of heading-aware chunking).

### Chroma (`kb/chroma.sqlite3`)
- Collection `fortios76`; MiniLM-L6-v2 384-dim; IDs = chunk_id;
  metadata = chunk fields (doc, version, heading, page, url)
- Chroma v2 keeps vectors in `<uuid>/data_0.bin` beside the sqlite;
  the sqlite also carries FTS content for keyword search

### logs/inverted_index.json
`{"tf": {...}, "df": {...}, "n": <chunk_count>}` — auto-rebuilt from
chunks.jsonl on first query when missing (see pitfall #1)

### eval/questions.jsonl
`{"id":"cli-01","q":"...","kp":["point 1", ...]}` — key points are the
judge's checklist; equivalent phrasings accepted (CIDR == netmask etc.)

### eval/answers.jsonl
`{"id","q","answer","ctx":[{chunk_id,doc,heading,page,score}],"gen_secs"}`

### eval/scores.jsonl
`{"id","pass","points","pass_pts","partial_pts","fail_pts","insufficient_context","verdicts":[{point,verdict,why}]}`
- Pass = no FAIL verdict and ≥ half of KP points PASS

### field/topics.jsonl
`{"url","title","text_len","text"}` (+ raw `field/pages/*.html`)

## Root index (compiled, K4=C)

- Location: `root/kb/` (chromadb PersistentClient), collection
  `fortinet-root`. BUILD ARTIFACT — never edit; recompile with
  `compile_root.py` after any surface change.
- Contents: one vector per surface chunk. Ids `<surface>::<chunk_id>`;
  metadata = chunk fields + `surface`, `product`, `line`, `piece`
  (piece from `pieces/*/manifest.json`; a doc claimed by all 12 pieces →
  `cross`); **documents = chunk text** (root is self-contained).
- Query contract: `query_root.py` REQUIRES `--product` + `--line` (or
  `--general`). Surface-local queries stay `query.py` on the surface kb.
- The MiniLM ONNX weights used at query time cache in
  `/home/chrismok/.cache/chroma-onnx` (bind-mount to `/root/.cache/chroma`
  in throwaway containers) so the 79MB model is fetched once.

## Build from scratch (reproducible)

1. Create surface dir + CORPUS.md card under `fortinet-corpus/`
2. Fetch: official PDFs (fetch_pdfs.py / fetch_phase2.py patterns),
   field reports (crawl_field*.py)
3. Extract: `python scripts/extract_pdfs.py`
4. Embed: `python scripts/embed.py` (CPU; ~21 min per ~75k chunks)
5. Keyword index auto-rebuilds on first `query.py` run
6. Exam: `run_eval.py` → `score_eval.py`; pass = ≥90% × 2 consecutive
   rounds
7. Fold verified knowledge into the skill core (skill
   `Self-improvement` section is the operating procedure)

## Incremental update (smallest unit = one doc)

1. Add the PDF to `pdfs/` (fetch)
2. Extract it → APPEND its chunks (new chunk_ids; never touch existing)
3. `embed.py` (skips existing IDs → only new vectors written)
4. `rm logs/inverted_index.json` (auto-rebuild on next query)
5. Re-run the affected exam slice (regression gate)

Worked example: `append_ha802.py`.

## Pitfalls (hit in production)

1. Stale inverted index → silently bad retrieval (invalidated an entire
   eval round). Always rebuild after any chunks.jsonl change.
2. Eval LLM is a thinking model: `chat_template_kwargs:
   {'enable_thinking': False}` required or answers GEN_FAIL.
3. `score_eval.py` last-wins + resume bug: archive `scores.jsonl` before
   each fresh scoring run.
4. Some 8.0.0 S3 objects return 403 → use the 8.0.2 variant of the same
   doc.
5. Merging exam sets → ID collisions; rename on import.
6. Over-strict KP wording (CIDR vs netmask) → accept equivalent forms
   in the judge prompt.
7. f-string/heredoc quoting in shell one-liners → use standalone .py
   files.
8. "NOT FOUND" is often a probe miss → re-probe (different casing,
   abbreviation) before declaring an object absent.
9. Root-owned files: replace (recreate) them, don't edit in place.
10. Chroma sqlite: the `embeddings` table's `id` column is an integer
    rowid — the real chunk id is the `embedding_id` TEXT column
    (compile_root.py `fetch_all`).
11. chromadb `query()`/`get()` do NOT return documents unless you pass
    `include=["documents", "metadatas", "distances"]` — silent `None`
    otherwise (hit in query_root.py; root kb had no `documents` table
    until compile_root.py started storing them).
12. A non-detached `docker exec` dies at the session boundary, killing
    long compiles silently. Use `docker run` from a background terminal,
    or `docker exec -d ... sh -c 'nohup ... > log 2>&1'`.
13. Manifest `docs` entries must match chunks.jsonl `doc` stems
    EXACTLY (URL-encoded chars like `%C2%A0` preserved) — mismatched
    names show up as "unassigned" chunks in the root compile.
14. Bulk chromadb `get()` over >~900 ids hits SQLite's SQL-variable
    limit — batch it (compile_root.py `fetch_all` batches at 900).

## Lineage

- Phase 1 (2026-10): 36 PDFs → 24,298 chunks; exam A+B → 87.0%/100%/100%
- Phase 2 (2026-11): +18 official PDFs + 174 field reports → 73,552
  chunks; +HA 8.0.2 → 75,543 vectors; exam C+D+X → 92 questions,
  R2 = 76.1% (phase 2 closed at R2)
- Surface named 2026-11-01 (see `fortios-7.6x/CORPUS.md`)
- Root index first compiled 2026-11-01: 75,543 vectors, 0 unassigned
  (pieces: 12 manifests; vpn manifest carries a `%C2%A0` doc-name
  variant; ops claims the `community` field-report chunks)
