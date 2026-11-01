#!/usr/bin/env python3
"""Extract all PDFs in pdfs/ -> text/*.txt with heading/page markers,
and build chunks.jsonl (heading-aware, ~700-1000 chars).
Runs inside the RAG container. Stdlib + pymupdf.
"""
import os, json, statistics, re
import pymupdf

ROOT = '/work'
PDFS = os.path.join(ROOT, 'pdfs')
TXT = os.path.join(ROOT, 'text')
os.makedirs(TXT, exist_ok=True)

def doc_sizes(page, limit=40):
    sizes = []
    for pno in range(min(page.page_count, limit)):
        d = page[pno].get_text('dict')
        for block in d['blocks']:
            if block.get('type') != 0:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    if len(span['text'].strip()) > 2:
                        sizes.append(span['size'])
    if not sizes:
        return 10.0
    return statistics.median(sizes)

def extract_pdf(path, slug):
    page = pymupdf.open(path)
    body = doc_sizes(page)
    h1_th, h2_th = body * 1.55, body * 1.22
    out = []
    h1 = h2 = h3 = ''
    pages = page.page_count
    for pno in range(pages):
        d = page[pno].get_text('dict')
        out.append(f'<<<PAGE {pno+1}>>>')
        for block in d['blocks']:
            if block.get('type') != 0:
                continue
            for line in block['lines']:
                text = ''.join(s['text'] for s in line['spans']).strip()
                if not text:
                    continue
                maxsz = max((s['size'] for s in line['spans']), default=0)
                if maxsz >= h1_th:
                    h1, h2, h3 = text, '', ''
                    out.append(f'<<<H1|{text}>>>')
                elif maxsz >= h2_th:
                    h2, h3 = text, ''
                    out.append(f'<<<H2|{text}>>>')
                elif maxsz >= body * 1.10:
                    h3 = text
                    out.append(f'<<<H3|{text}>>>')
                else:
                    out.append(text)
    page.close()
    txt = '\n'.join(out)
    with open(os.path.join(TXT, f'{slug}.txt'), 'w') as f:
        f.write(txt)
    return pages, txt

def chunk_doc(slug, version, txt, max_len=1000, min_len=400):
    """Walk the marked text, group into chunks under heading context."""
    lines = txt.split('\n')
    h1 = h2 = h3 = ''
    page = 0
    chunks = []
    buf = []
    buf_len = 0
    buf_page = 0

    def flush():
        nonlocal buf, buf_len, buf_page
        t = '\n'.join(buf).strip()
        if len(t) >= 150:
            heading = ' | '.join(x for x in (h1, h2, h3) if x)
            chunks.append({
                'doc': slug, 'version': version, 'heading': heading,
                'page': buf_page or page, 'text': t,
            })
        buf, buf_len, buf_page = [], 0, 0

    for ln in lines:
        m = re.match(r'<<<PAGE (\d+)>>>', ln)
        if m:
            page = int(m.group(1)); continue
        m = re.match(r'<<<H([123])\|(.*)>>>', ln)
        if m:
            flush()
            lvl, t = m.group(1), m.group(2)
            if lvl == '1': h1, h2, h3 = t, '', ''
            elif lvl == '2': h2, h3 = t, ''
            else: h3 = t
            continue
        if ln.strip() == '':
            continue
        if buf_len + len(ln) > max_len and buf_len >= min_len:
            flush()
        if buf_len == 0:
            buf_page = page
        buf.append(ln)
        buf_len += len(ln) + 1
    flush()
    return chunks

def main():
    rows = []
    all_chunks = []
    for fn in sorted(os.listdir(PDFS)):
        if not fn.lower().endswith('.pdf'):
            continue
        slug = fn[:-4].replace(' ', '_')
        try:
            pages, txt = extract_pdf(os.path.join(PDFS, fn), slug)
        except Exception as e:
            rows.append([slug, pages, 0, f'EXTRACT_FAIL:{e}'])
            print(f'FAIL {slug}: {e}', flush=True)
            continue
        m = re.search(r'(\d+\.\d+(?:\.\d+)?)', fn)
        ver = m.group(1) if m else '7.6'
        chunks = chunk_doc(slug, ver, txt)
        all_chunks.extend(chunks)
        rows.append([slug, pages, len(chunks), 'OK'])
        print(f'{slug}: {pages} pages, {len(chunks)} chunks, {len(txt)//1024} KB text', flush=True)
    # stable chunk ids
    for i, c in enumerate(all_chunks):
        c['chunk_id'] = f'c{i:06d}'
    with open(os.path.join(ROOT, 'chunks.jsonl'), 'w') as f:
        for c in all_chunks:
            f.write(json.dumps(c) + '\n')
    with open(os.path.join(ROOT, 'logs', 'extract_summary.csv'), 'w') as f:
        f.write('slug,pages,chunks,status\n')
        for r in rows:
            f.write(','.join(map(str, r)) + '\n')
    print(f'DONE docs={len(rows)} chunks={len(all_chunks)}', flush=True)

if __name__ == '__main__':
    main()
