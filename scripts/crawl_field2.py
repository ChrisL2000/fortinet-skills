#!/usr/bin/env python3
"""Crawl topic URLs listed in field/crawl_urls.txt (one per line).
Saves field/pages/*.html + field/topics.jsonl. Stdlib only.
"""
import urllib.request, re, os, json, time, html as H

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
ROOT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag/field')
PAGES = os.path.join(ROOT, 'pages')
os.makedirs(PAGES, exist_ok=True)

urls = [l.strip() for l in open(os.path.join(ROOT, 'crawl_urls.txt')) if l.strip().startswith('http')]
seen = set()
uniq = []
for u in urls:
    if u not in seen:
        seen.add(u)
        uniq.append(u)
print(f'crawling {len(uniq)} topics', flush=True)

def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read()

def strip_text(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<br\s*/?>', '\n', h)
    h = re.sub(r'(?is)</p>', '\n', h)
    h = re.sub(r'(?is)<[^>]+>', ' ', h)
    h = H.unescape(h)
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n\s*\n+', '\n\n', h)
    return h.strip()

recs = []
fails = 0
for i, u in enumerate(uniq, 1):
    tid = u.rstrip('/').rsplit('/', 1)[-1]
    try:
        final, html = get(u)
    except Exception as e:
        fails += 1
        if fails <= 10:
            print(f'fail {u}: {e}', flush=True)
        continue
    raw = html.decode('utf-8', 'ignore')
    m = re.search(r'(?s)<meta[^>]+property="og:title"[^>]+content="([^"]+)"', raw)
    if m:
        title = H.unescape(m.group(1))
    else:
        t = re.search(r'(?s)<title>([^<]+)</title>', raw)
        title = H.unescape(t.group(1)) if t else tid
    text = strip_text(raw)
    with open(os.path.join(PAGES, f'{i:04d}-{tid}.html'), 'w') as f:
        f.write(raw)
    recs.append({'url': u, 'title': title, 'text_len': len(text), 'text': text[:200000]})
    if i % 25 == 0:
        print(f'{i}/{len(uniq)} ok={len(recs)} fail={fails}', flush=True)
    time.sleep(1.0)

with open(os.path.join(ROOT, 'topics.jsonl'), 'w') as f:
    for r in recs:
        f.write(json.dumps(r) + '\n')
print(f'DONE topics={len(recs)} fails={fails}', flush=True)
