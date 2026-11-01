import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# usage: ctx.py <term> <filename> [width] [n]
term, fname = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 700
n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
txt = open(ROOT + "/text/" + fname, errors="ignore").read()
hits = 0
for m in re.finditer(re.escape(term), txt):
    s = max(0, m.start() - 150)
    e = min(len(txt), m.end() + w)
    print("..." + " ".join(txt[s:e].split()) + "...")
    hits += 1
    if hits >= n:
        break
if not hits:
    print("NO MATCH")
