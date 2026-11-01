#!/usr/bin/env python3
"""Discover and download FortiOS 7.6.x official PDF docs.
Pins each doc set to the newest version <= 7.6.7 that has a full PDF.
Stdlib only. Output: pdfs/*.pdf + logs/manifest.csv
"""
import urllib.request, re, os, csv, time

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
BASE = 'https://docs.fortinet.com'
OUT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag')
PDFS = os.path.join(OUT, 'pdfs')
LOGS = os.path.join(OUT, 'logs')
os.makedirs(PDFS, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
MAXV = (7, 6, 7)

def get(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.geturl(), r.read()

product_html = get(BASE + '/product/fortigate/7.6')[1].decode('utf-8', 'ignore')
page_vers = {}
for ver, slug in re.findall(r'/document/fortigate/(\d+\.\d+\.\d+)/([a-z0-9-]+)', product_html):
    v = tuple(map(int, ver.split('.')))
    if v > MAXV:
        continue
    if slug not in page_vers or v > page_vers[slug]:
        page_vers[slug] = v

print(f'{len(page_vers)} doc slugs from product page', flush=True)

def candidates(slug):
    out = [(7, 6, 7)]
    if slug in page_vers and page_vers[slug] not in out:
        out.append(page_vers[slug])
    for p in (6, 5, 4, 3, 2, 1, 0):
        v = (7, 6, p)
        if v not in out and v <= MAXV:
            out.append(v)
    return out

rows = []
for slug in sorted(page_vers):
    done = False
    for v in candidates(slug):
        ver = '.'.join(map(str, v))
        url = f'{BASE}/document/fortigate/{ver}/{slug}'
        pdf_url = None
        try:
            final, html = get(url)
            m = re.findall(r'https://fortinetweb[^"\']*?\.pdf', html.decode('utf-8', 'ignore'))
            if m:
                pdf_url = m[0]
        except Exception as e:
            print(f'{slug} {ver} fetch fail: {e}', flush=True)
            time.sleep(1)
            continue
        if not pdf_url:
            time.sleep(1)
            continue
        fname = os.path.basename(pdf_url).replace(' ', '_')
        dest = os.path.join(PDFS, fname)
        try:
            req = urllib.request.Request(pdf_url, headers=UA)
            with urllib.request.urlopen(req, timeout=900) as r, open(dest, 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
        except Exception as e:
            print(f'{slug} {ver} dl fail: {e}', flush=True)
            time.sleep(2)
            continue
        rows.append([slug, ver, 'OK', pdf_url, os.path.getsize(dest)])
        print(f'OK {slug} {ver} {os.path.getsize(dest)//1024} KB', flush=True)
        done = True
        break
    if not done:
        rows.append([slug, 'n/a', 'NO_PDF', '', 0])
        print(f'FAIL {slug} no pdf found', flush=True)

with open(os.path.join(LOGS, 'manifest.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['slug', 'version', 'status', 'pdf_url', 'bytes'])
    w.writerows(rows)
ok = [r for r in rows if r[2] == 'OK']
print(f'DONE total={len(rows)} ok={len(ok)} failed={len(rows)-len(ok)} total_mb={sum(r[4] for r in ok)//1048576}', flush=True)
