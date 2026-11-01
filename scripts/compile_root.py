#!/usr/bin/env python3
"""Compile all surface collections into ONE root index (architecture K4=C).

Run inside the RAG container with the corpus root at /work
(script lives at the corpus root; it resolves paths from its own location).

- Per-surface collections are the SOURCE OF TRUTH (see pieces/README.md).
- Merges every surface's collection into root/kb/, collection `fortinet-root`.
- Enriches chunk metadata with: surface, product, line, piece
  (piece from pieces/*/manifest.json; docs claimed by all 12 pieces -> "cross").
- Stores chunk TEXT in the root (documents), read straight from the
  surface collection — so the root index is self-contained for retrieval.
- Root ids are namespaced <surface>::<chunk_id> (surfaces reuse local ids).
- Idempotent: skips root ids already present. Re-run after any surface change.

The root index is a BUILD ARTIFACT — never edit it; recompile it.
"""
import os, sys, json, glob, time

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_KB = os.path.join(ROOT, "root", "kb")
COLL_NAME = "fortinet-root"
MODEL = "MiniLM-L6-v2"
BATCH = 2000

# ---- piece manifests: doc stem -> list of pieces claiming it ----
n_pieces = 0
doc_to_pieces = {}
for mf in sorted(glob.glob(os.path.join(ROOT, "pieces", "*", "manifest.json"))):
    m = json.load(open(mf))
    n_pieces += 1
    for d in m["docs"]:
        stem = d[:-4] if d.endswith(".pdf") else d
        doc_to_pieces.setdefault(stem, set()).add(m["piece"])

def piece_of(doc):
    pcs = doc_to_pieces.get(doc)
    if not pcs:
        return "unassigned"
    if len(pcs) == n_pieces:
        return "cross"
    return "/".join(sorted(pcs))

import chromadb
import sqlite3

def fetch_all(coll, kb_dir, batch=900):
    """All ids/embeddings/metas. Batched: a single coll.get() for 75k ids
    exceeds SQLite's SQL-variable limit inside Chroma's plan."""
    con = sqlite3.connect(os.path.join(kb_dir, "chroma.sqlite3"))
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    table = "embedding" if "embedding" in tables else "embeddings"
    # Chroma sqlite: the 'embeddings' table's `id` is an integer rowid;
    # the real chunk id lives in the `embedding_id` TEXT column.
    ids = [r[0] for r in con.execute(f"SELECT embedding_id FROM {table}")]
    con.close()
    out_ids, out_embs, out_mds, out_docs = [], [], [], []
    for b in range(0, len(ids), batch):
        got = coll.get(ids=ids[b:b+batch],
                       include=["embeddings", "metadatas", "documents"])
        out_ids.extend(got["ids"]); out_embs.extend(got["embeddings"])
        out_mds.extend(got["metadatas"]); out_docs.extend(got.get("documents") or [])
    return out_ids, out_embs, out_mds, out_docs

root_client = chromadb.PersistentClient(path=ROOT_KB)
root_coll = root_client.get_or_create_collection(
    COLL_NAME, metadata={"model": MODEL, "dim": 384, "hnsw:space": "cosine"})

existing = set(fetch_all(root_coll, ROOT_KB)[0])
print(f"root existing ids: {len(existing)}; pieces: {n_pieces}", flush=True)

surfaces = sorted(
    d for d in glob.glob(os.path.join(ROOT, "*", "kb", "collection.json"))
    if os.path.basename(os.path.dirname(os.path.dirname(d))) not in ("root", "pieces")
)
for cfg_path in surfaces:
    surf_dir = os.path.dirname(os.path.dirname(cfg_path))
    surface = os.path.basename(surf_dir)
    cfg = json.load(open(cfg_path))
    client = chromadb.PersistentClient(path=os.path.dirname(cfg_path))
    coll = client.get_collection(cfg["name"])
    ids, embs, mds, docs = fetch_all(coll, os.path.dirname(cfg_path))
    product, line = surface.split("-", 1)
    new_ids, new_embs, new_mds, new_docs = [], [], [], []
    unassigned = {}
    for i, cid in enumerate(ids):
        rid = f"{surface}::{cid}"
        if rid in existing:
            continue
        md = dict(mds[i] or {})
        doc = md.get("doc", "")
        pc = piece_of(doc)
        if pc == "unassigned":
            unassigned[doc] = unassigned.get(doc, 0) + 1
        md.update(surface=surface, product=product, line=line, piece=pc)
        new_ids.append(rid); new_embs.append(embs[i]); new_mds.append(md)
        new_docs.append(docs[i] if i < len(docs) else "")
    if any(d == "" for d in new_docs):
        print(f"  WARN: {sum(1 for d in new_docs if d == '')} chunks had no text", flush=True)
    for b in range(0, len(new_ids), BATCH):
        root_coll.add(
            ids=new_ids[b:b+BATCH],
            embeddings=new_embs[b:b+BATCH],
            metadatas=new_mds[b:b+BATCH],
            documents=new_docs[b:b+BATCH],
        )
        time.sleep(0.2)
    print(f"[{surface}] total={len(ids)} added={len(new_ids)} "
          f"skipped={len(ids)-len(new_ids)}", flush=True)
    if unassigned:
        print("  UNASSIGNED docs:", unassigned, flush=True)

final = root_coll.count()
print(f"ROOT TOTAL: {final} vectors (collection {COLL_NAME})")
