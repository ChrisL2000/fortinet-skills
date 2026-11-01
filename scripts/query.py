#!/usr/bin/env python3
"""Hybrid query: Chroma vector + inverted-index keyword score.
Usage: query.py "query text" [k] [--alpha 0.55]
Output: JSON array of {chunk_id, doc, version, heading, page, url, score_vec, score_kw, score, text}
"""
import os, sys, json, math, re
from collections import defaultdict
import chromadb
from sentence_transformers import SentenceTransformer

ROOT = '/work'
KB = os.path.join(ROOT, 'kb')
COLLECTION = 'fortios76'
IDX = os.path.join(ROOT, 'logs', 'inverted_index.json')

def build_index():
    if not os.path.exists(IDX):
        tf = defaultdict(lambda: defaultdict(int))
        df = defaultdict(int)
        n = 0
        with open(os.path.join(ROOT, 'chunks.jsonl')) as f:
            for line in f:
                c = json.loads(line)
                toks = re.findall(r'[a-z0-9_.:/-]{2,}', c['text'].lower())
                seen = set()
                for tok in toks:
                    tf[c['chunk_id']][tok] += 1
                    if tok not in seen:
                        df[tok] += 1
                        seen.add(tok)
                n += 1
        json.dump({'tf': {k: dict(v) for k, v in tf.items()}, 'df': dict(df), 'n': n}, open(IDX, 'w'))
    return json.load(open(IDX))

def kw_score(query, idx, k=10):
    n = idx['n']
    qtoks = re.findall(r'[a-z0-9_.:/-]{2,}', query.lower())
    scores = defaultdict(float)
    idf_cache = {}
    for tok in set(qtoks):
        d = idx['df'].get(tok, 0)
        if d == 0:
            continue
        idf = math.log(1 + n / (1 + d))
        idf_cache[tok] = idf
        for cid, tfmap in idx['tf'].items():
            if tok in tfmap:
                scores[cid] += idf * (1 + math.log(tfmap[tok]))
    return scores

def main():
    q = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    alpha = 0.55
    for i, a in enumerate(sys.argv):
        if a == '--alpha' and i + 1 < len(sys.argv):
            alpha = float(sys.argv[i+1])
    client = chromadb.PersistentClient(path=KB)
    col = client.get_collection(COLLECTION)
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    emb = model.encode([q], normalize_embeddings=True)[0]

    vs = col.query(query_embeddings=[emb.tolist()], n_results=min(k*4, 100))
    vec_scores = {}
    for cid, dist in zip(vs['ids'][0], vs['distances'][0]):
        vec_scores[cid] = 1.0 - dist  # cosine sim

    idx = build_index()
    kws = kw_score(q, idx)

    cands = set(vec_scores) | set(kws)
    maxv = max((vec_scores.get(c, 0) for c in cands), default=1) or 1
    maxk = max((kws.get(c, 0) for c in cands), default=1) or 1
    scored = []
    for c in cands:
        s = alpha * (vec_scores.get(c, 0) / maxv) + (1 - alpha) * (kws.get(c, 0) / maxk)
        scored.append((s, c))
    scored.sort(reverse=True)
    res = []
    for s, cid in scored[:k]:
        m = col.get(ids=[cid])
        if not m['ids']:
            continue
        res.append({
            'chunk_id': cid, 'score': round(s, 4),
            'score_vec': round(vec_scores.get(cid, 0), 4),
            'score_kw': round(kws.get(cid, 0), 3),
            'doc': m['metadatas'][0]['doc'], 'version': m['metadatas'][0]['version'],
            'heading': m['metadatas'][0]['heading'], 'page': m['metadatas'][0]['page'],
            'url': m['metadatas'][0].get('url', ''),
            'text': m['documents'][0],
        })
    print(json.dumps(res, indent=1))

if __name__ == '__main__':
    main()
