#!/usr/bin/env python3
"""Query the compiled root index (K4=C).

Usage:
  query_root.py "query text" [k] [--product fortios --line 7.6x] [--general]

The product/line filter is REQUIRED (prevents cross-version/cross-product
contamination) unless --general is passed explicitly (for cross-product or
cross-version comparison questions).

v1 is vector-only over the root collection. Per-surface hybrid (vector +
keyword) queries remain available via the surface's own query.py for
diagnostics.

Output: JSON array of {id, doc, version, heading, page, piece, product,
line, score}.
"""
import sys, json, argparse
import chromadb

ROOT = "/home/chrismok/fortinet-corpus"  # container mount point (host: /home/chrismok/fortinet-corpus)

ap = argparse.ArgumentParser()
ap.add_argument("query")
ap.add_argument("k", nargs="?", type=int, default=12)
ap.add_argument("--product")
ap.add_argument("--line")
ap.add_argument("--general", action="store_true")
a = ap.parse_args()

client = chromadb.PersistentClient(path=ROOT + "/root/kb")
coll = client.get_collection("fortinet-root")

if a.general:
    where = None
elif a.product and a.line:
    where = {"$and": [{"product": a.product}, {"line": a.line}]}
else:
    sys.exit("FILTER REQUIRED: pass --product P --line L (or --general for cross-product/version queries).")

r = coll.query(query_texts=[a.query], n_results=a.k, where=where,
               include=["documents", "metadatas", "distances"])
docs = r.get("documents") or [[None] * a.k]
out = []
for i, rid in enumerate(r["ids"][0]):
    md = r["metadatas"][0][i] or {}
    out.append({
        "id": rid,
        "doc": md.get("doc"), "version": md.get("version"),
        "heading": md.get("heading"), "page": md.get("page"),
        "piece": md.get("piece"), "product": md.get("product"), "line": md.get("line"),
        "score": 1.0 - (r["distances"][0][i] if r.get("distances") else 0.0),
        "text": ((docs[0][i] or "")[:1200]),
    })
print(json.dumps(out, indent=1))
