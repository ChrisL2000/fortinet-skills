#!/usr/bin/env python3
"""Phase 2 fetch: widen corpus to 7.6.x line (7.6.8) + 8.0 line (8.0.0 GA, 8.0.2 latest).
Stdlib only. Output: pdfs/*.pdf + logs/manifest_phase2.csv"""
import urllib.request, re, os, csv, time

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
BASE = 'https://docs.fortinet.com'
OUT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag')
PDFS = os.path.join(OUT, 'pdfs')
LOGS = os.path.join(OUT, 'logs')
os.makedirs(PDFS, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

PLAN = [
    # (version, [slugs])
    ('7.6.8', ['administration-guide', 'cli-reference', 'fortios-release-notes',
               'firmware-upgrade-guide', 'new-features', 'sd-wan-new-features',
               'cli-troubleshooting-cheat-sheet', 'hardware-acceleration',
               'fortios-log-message-reference', 'fortios-feature-platform-matrix']),
    ('8.0.0', ['administration-guide', 'cli-reference', 'fortios-release-notes',
               'new-features', 'sd-wan-new-features', 'firmware-upgrade-guide',
               'cli-troubleshooting-cheat-sheet', 'hardware-acceleration',
               'fortios-log-message-reference', 'fortios-feature-platform-matrix',
               'ztna-reference-guide', 'sd-wan-deployment-for-mssps',
               'sd-wan-sd-branch-architecture-for-mssps']),
    ('8.0.2', ['administration-guide', 'fortios-release-notes',
               'firmware-upgrade-guide', 'cli-troubleshooting-cheat-sheet']),
]

def get(url, timeout=900):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

rows = []
for ver, slugs in PLAN:
    for slug in slugs:
        url = f'{BASE}/document/fortigate/{ver}/{slug}'
        try:
            html = get(url).decode('utf-8', 'ignore')
        except Exception as e:
            print(f'PAGEFAIL {ver} {slug}: {e}', flush=True)
            rows.append([ver, slug, 'PAGE_FAIL', '', 0])
            time.sleep(2)
            continue
        m = re.findall(r'https://fortinetweb[^"\']*?\.pdf', html)
        if not m:
            print(f'NOPDF {ver} {slug}', flush=True)
            rows.append([ver, slug, 'NO_PDF', url, 0])
            time.sleep(1)
            continue
        pdf_url = m[0]
        fname = os.path.basename(pdf_url).replace(' ', '_')
        dest = os.path.join(PDFS, fname)
        try:
            data = get(pdf_url)
            with open(dest, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f'DLFAIL {ver} {slug}: {e}', flush=True)
            rows.append([ver, slug, 'DL_FAIL', pdf_url, 0])
            time.sleep(2)
            continue
        rows.append([ver, slug, 'OK', pdf_url, len(data)])
        print(f'OK {ver} {slug} {len(data)//1024} KB', flush=True)
        time.sleep(1)

with open(os.path.join(LOGS, 'manifest_phase2.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['version', 'slug', 'status', 'pdf_url', 'bytes'])
    w.writerows(rows)
ok = [r for r in rows if r[2] == 'OK']
print(f'DONE total={len(rows)} ok={len(ok)} failed={len(rows)-len(ok)} total_mb={sum(r[4] for r in ok)//1048576}', flush=True)
