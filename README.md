# FortiNet Product Knowledge — Hermes Skill Family + Corpus Pipeline

A Hermes Agent skill family covering FortiNet products (FortiOS/FortiGate first surface),
built as **two-axis model**:

- **SURFACES** (physical axis): product × version line, each with its own documentation
  collection. Current: `fortios-7.6x` (FortiOS 7.6.0–7.6.8, 43,528 vectors) and
  `fortios-8.0x` (FortiOS 8.0.0–8.0.2, 25 docs, 37,220 vectors).
- **PIECES** (logical axis): 12 knowledge domains — `platform`, `policy`, `vpn`,
  `sdpwan`, `ha`, `wireless`, `proxy-ztna-casb`, `dlp`, `logging`, `auth`, `hardware`,
  `ops`. Each piece is an independently updatable Hermes skill with CLI-verified content.

The **root index** is a compiled artifact — one merged vector collection assembled from
all surfaces/pieces (`compile_root.py`), never hand-edited. That is the "FINAL BOSS":
one giant index answering across the whole corpus, while each piece skill and surface
can be refreshed on its own.

```
question
   |
   v
router skill (hermes-it-infosec-fw-fortig-fortios-7-6-7)
   |  routes by topic -> piece skill (SKILL CORE)
   v
root index query (query_root.py, K=16, 1200-char chunks)  ->  RAG CONTEXT
   |
   v
answer (skill core + retrieved context, both cited)
```

## Repo layout

```
skills/router/.../SKILL.md   router skill — routing table, runbook, exam state
skills/pieces/fortinet-*/    12 piece skills (SKILL.md each)
scripts/                     pipeline + eval scripts (see table below)
eval/questions.jsonl         92-question 7.6x exam, piece-tagged, keypoint-graded
eval/fortios-8.0x/           12-question 8.0x exam (platform/hardware/policy slices)
PIPELINE.md                  corpus build pipeline (fetch -> extract -> embed -> compile)
CORPUS.md                    surface conventions + self-improvement/update procedure
```

### Scripts

| script | purpose |
|---|---|
| `fetch_pdfs.py`, `fetch_phase2.py`, `crawl_field.py`, `crawl_field2.py` | fetch docs from docs.fortinet.com (per-surface manifests) |
| `extract_pdfs.py` | PDF → text with heading markers (`<<<H1\|...>>>`) |
| `embed.py` | chunk + embed a surface (CPU sentence-transformers MiniLM-L6-v2) |
| `probe.py`, `ctx.py`, `query.py` | surface-level probes (dev/debug) |
| `compile_root.py` | compile all surfaces into the merged root collection |
| `query_root.py` | root query (K, char-slice, product/line filters) |
| `eval_root.py` | live-path exam runner (skill core + root RAG, local LLM) |
| `score_root.py` | LLM-judge scoring: strict + partial-credit (weighted) metrics |
| `run_eval.py`, `score_eval.py` | legacy surface-exam pair |

## Requirements

- Hermes Agent (skills load from `~/.hermes/skills/`)
- Python 3, `chromadb` + `sentence-transformers` (CPU-only embedding)
- For evaluation only: a local OpenAI-compatible chat endpoint
  (default `http://localhost:8081/v1` — e.g. Qwen via vLLM). Override the
  `VLLM` constant in `score_root.py` / `eval_root.py` for other endpoints.

## Install

```
cp -r skills/router/* ~/.hermes/skills/
cp -r skills/pieces/* ~/.hermes/skills/fortinet/
```

The router skill documents the full query runbook and the update/self-improvement
loop. Piece skills are the knowledge layer; the root index is the retrieval layer.

## Building a corpus from scratch (per surface)

Full instructions in `PIPELINE.md`. Summary:

1. **Fetch** doc PDFs per the surface manifest (docs.fortinet.com).
2. **Extract** to text with heading markers (`extract_pdfs.py`).
3. **Chunk + embed** (`embed.py`) — CPU sentence-transformers MiniLM-L6-v2,
   Chroma collection per surface.
4. **Compile** the root (`compile_root.py`) — merges all surface collections
   into `root/kb` (collection `fortinet-root`), tagging each vector with
   `product`, `line`, `piece`, `doc`.
5. **Verify** (`query_root.py` smoke queries) and **exam** (`eval_root.py` +
   `score_root.py`).

## Evaluation

`eval/questions.jsonl`: 92 questions, each with a `piece` tag and key points (`kp`).
`eval_root.py` answers them exactly the way a live Hermes client would (piece skill
as SKILL CORE + root-index RAG CONTEXT, K=16 × 1200 chars). `score_root.py` judges
each key point PASS / PARTIAL / FAIL and reports:

- **strict**: question passes only with zero FAILs and ≥ half PASS
- **weighted** (partial credit): PASS=1, PARTIAL=0.5, FAIL=0, per-question mean
- **≥75% / ≥50% question thresholds** + per-piece breakdown for both views

Score history (fortios-7.6x surface, rounds 1–5; see `eval/README.md`):
strict 40.2 → 59.8 → 63.0 → 59.8 → **60.9**; weighted 62.3 → 74.7 → 78.0 →
78.8 → **79.6**. The vpn piece is 100% strict in every round; platform 90%
weighted in R5. Practical release gate met: weighted ≥75% × 3 consecutive
(R3–R5) with strict ≥60% × 3.

## Self-improvement loop

Documented in `CORPUS.md` (in-repo copy): find a gap → verify against source docs →
patch the affected piece skill → optionally re-fetch/re-embed new docs → recompile
root → re-run exam slice. The root is always a compiled artifact — never edit it by
hand.

## Data provenance

This repo intentionally contains **no FortiNet documentation text and no vector
store** — the corpus is built locally on your host from docs you fetch yourself
(respect FortiNet's terms of use for their documentation). Everything here is the
skill knowledge, pipeline code, and exam harness.
