#!/usr/bin/env python3
"""Targeted crawl of Fortinet Community search results for 7.6.x field reports.
Stdlib only. Output: field/pages/*.html + field/topics.jsonl
"""
import urllib.request, urllib.parse, re, os, json, time, html as H

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
CF = 'https://community.fortinet.com'
OUT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag/field')
PAGES = os.path.join(OUT, 'pages')
os.makedirs(PAGES, exist_ok=True)

QUERIES = [
    'fortios 7.6.7', 'fortios 7.6.6', 'fortios 7.6.5', 'fortios 7.6.4',
    'fortios 7.6.3', 'fortios 7.6.2', 'fortios 7.6.1', 'fortios 7.6.0',
    '7.6 upgrade issue', '7.6 bug', '7.6 regression', 'fortios 7.6 rest api',
]
TOPIC_RE = re.compile(r'https://community\.fortinet\.com/[a-z0-9-]+/[a-z0-9-]+-\d+')

def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read()

urls = []
seen = set()
for q in QUERIES:
    su = CF + '/search/?query=' + urllib.parse.quote(q)
    try:
        final, html = get(su)
    except Exception as e:
        print(f'search fail {q}: {e}', flush=True)
        continue
    for u in TOPIC_RE.findall(html.decode('utf-8', 'ignore')):
        if u not in seen:
            seen.add(u)
            urls.append(u)
    print(f'query {q!r}: total={len(urls)}', flush=True)
    time.sleep(1.0)

CAP = 250
urls = urls[:CAP]
print(f'crawling {len(urls)} topics', flush=True)

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
for i, u in enumerate(urls, 1):
    tid = u.rstrip('/').rsplit('/', 1)[-1]
    try:
        final, html = get(u)
    except Exception as e:
        print(f'fetch fail {u}: {e}', flush=True)
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
        print(f'{i}/{len(urls)}', flush=True)
    time.sleep(1.0)

with open(os.path.join(OUT, 'topics.jsonl'), 'w') as f:
    for r in recs:
        f.write(json.dumps(r) + '\n')
print(f'DONE topics={len(recs)}', flush=True)
