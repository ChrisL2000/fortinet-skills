import os, re, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
texts = {}
for f in glob.glob(ROOT + "/text/*.txt"):
    texts[f.split("/")[-1]] = open(f, errors="ignore").read()

def find(term, limit=3, w=280):
    hits = 0
    for name, txt in texts.items():
        for m in re.finditer(re.escape(term), txt):
            s = max(0, m.start() - 100); e = min(len(txt), m.end() + w)
            snip = " ".join(txt[s:e].split())
            print("  [" + name[:42] + "] ..." + snip + "...")
            hits += 1
            if hits >= limit:
                return
    if not hits:
        print("  NO MATCH")

terms = sys.argv[1:]
for t in terms:
    print("== " + t)
    find(t, 3)
