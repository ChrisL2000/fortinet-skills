#!/usr/bin/env python3
"""Embed chunks.jsonl + field/topics.jsonl into Chroma (MiniLM-L6-v2, cached).
Runs inside the RAG container.
"""
import os, json, time, re
import chromadb
from sentence_transformers import SentenceTransformer

ROOT = '/work'
KB = os.path.join(ROOT, 'kb')
COLLECTION = os.environ.get('EMBED_COLLECTION', 'fortios76')

def main():
    t0 = time.time()
    client = chromadb.PersistentClient(path=KB)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={'hnsw:space': 'cosine'})
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    rows = []
    with open(os.path.join(ROOT, 'chunks.jsonl')) as f:
        for line in f:
            rows.append(json.loads(line))
    n_field = 0
    fp = os.path.join(ROOT, 'field', 'topics.jsonl')
    if os.path.exists(fp):
        with open(fp) as f:
            for line in f:
                r = json.loads(line)
                text = r.get('text', '')
                title = r.get('title', '')
                parts = re.split(r'\n\s*\n+', text)
                buf = []
                buf_len = 0
                ci = 0
                def fflush(buf):
                    nonlocal n_field
                    t = '\n'.join(buf).strip()
                    if len(t) > 200:
                        rows.append({
                            'chunk_id': f'f{n_field:06d}', 'doc': 'community',
                            'version': 'field', 'heading': title[:200],
                            'page': 0, 'url': r.get('url', ''), 'text': t,
                        })
                        n_field += 1
                for p in parts:
                    if buf_len + len(p) > 900 and buf_len >= 300:
                        fflush(buf); buf, buf_len = [], 0
                    buf.append(p); buf_len += len(p) + 1
                fflush(buf)
    print(f'total chunks: {len(rows)} (field={n_field})', flush=True)

    BATCH = 64
    ADD = 1000
    t = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        texts = [c['text'][:1800] for c in batch]
        emb = model.encode(texts, batch_size=BATCH, show_progress_bar=False, normalize_embeddings=True)
        col.add(
            ids=[c['chunk_id'] for c in batch],
            embeddings=emb.tolist(),
            documents=texts,
            metadatas=[
                {'doc': c['doc'], 'version': c.get('version', ''),
                 'heading': c.get('heading', '')[:300], 'page': c.get('page', 0),
                 'url': c.get('url', '')}
                for c in batch
            ],
        )
        t = i + len(batch)
        if (i // BATCH) % 25 == 0:
            el = time.time() - t0
            rate = t / max(el, 1e-6)
            eta = (len(rows) - t) / max(rate, 1e-6)
            print(f'{t}/{len(rows)} chunks, {rate:.0f}/s, eta {eta/60:.1f} min', flush=True)
    print(f'DONE count={col.count()} elapsed={(time.time()-t0)/60:.1f} min', flush=True)

if __name__ == '__main__':
    main()
