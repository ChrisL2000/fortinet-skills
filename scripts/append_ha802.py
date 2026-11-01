#!/usr/bin/env python3
"""Append the 8.0.2 hardware-acceleration doc to the EXISTING Chroma collection
(no rebuild). Run inside fortios-rag-tmp AFTER the main embed build has exited.
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_pdfs import extract_pdf, chunk_doc
import chromadb
from sentence_transformers import SentenceTransformer

ROOT = '/work'
COLLECTION = 'fortios76'
FN = 'fortios-hardware-acceleration-802.pdf'

def main():
    slug = FN[:-4]
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', FN)
    ver = m.group(1) if m else '8.0'
    pages, txt = extract_pdf(os.path.join(ROOT, 'pdfs', FN), slug)
    chunks = chunk_doc(slug, ver, txt)
    print(f'{slug}: {pages} pages, {len(chunks)} chunks, {len(txt)//1024} KB', flush=True)

    client = chromadb.PersistentClient(path=os.path.join(ROOT, 'kb'))
    col = client.get_collection(COLLECTION)
    before = col.count()

    # ID prefix 'ha802' cannot collide with 'c%06d' (PDF) or 'f%06d' (field)
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    BATCH = 64
    for i in range(0, len(chunks), BATCH):
        b = chunks[i:i+BATCH]
        texts = [c['text'][:1800] for c in b]
        emb = model.encode(texts, batch_size=BATCH, show_progress_bar=False,
                           normalize_embeddings=True)
        col.add(
            ids=[f'ha802{j:04d}' for j in range(i, i+len(b))],
            embeddings=emb.tolist(),
            documents=texts,
            metadatas=[{'doc': c['doc'], 'version': c['version'],
                        'heading': c['heading'][:300], 'page': c['page'],
                        'url': ''} for c in b],
        )
    after = col.count()
    assert after == before + len(chunks), f'count mismatch: {before}+{len(chunks)} != {after}'
    print(f'DONE before={before} after={after} added={after-before}', flush=True)

if __name__ == '__main__':
    main()
