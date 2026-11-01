#!/usr/bin/env python3
"""Score root-index exam answers (LLM judge, local Qwen :8081).

Pass = no key point FAIL and >= half the points PASS (PARTIAL allowed).
Outputs: <scores.jsonl> + overall summary + PER-PIECE breakdown
(joining question ids to the `piece` field in questions.jsonl).

Usage:
  score_root.py [answers.jsonl] [scores.jsonl]
Defaults: <surface>/eval/answers_root_r1.jsonl and scores_root_r1.jsonl
(NEW scores file per round — never append across rounds).
"""
import json, os, urllib.request, sys

CORPUS = '/home/chrismok/fortinet-corpus'
SURFACE = os.path.join(CORPUS, 'fortios-7.6x')
EV = os.path.join(SURFACE, 'eval')
VLLM = 'http://localhost:8081/v1/chat/completions'

JUDGE = """You are scoring a technical answer about FortiOS 7.6.x/8.0.x for an expert exam.

KEY POINTS (what the answer must contain to be correct):
{points}

ANSWER UNDER GRADE:
{answer}

Rules:
- Judge each key point independently: PASS (fully and correctly covered), PARTIAL (mostly right, minor gaps), FAIL (missing or wrong).
- A claim is FAIL if it contradicts the key point even when other content is good.
- If the answer is exactly "INSUFFICIENT CONTEXT" or starts with GEN_FAIL, mark every key point FAIL.
Reply with ONLY a JSON array, one object per key point in order:
[{{"point": <short label>, "verdict": "PASS|PARTIAL|FAIL", "why": "<=15 words"}}]
"""


def chat(model, prompt, max_tokens=1200, temp=0.0):
    body = json.dumps({'model': model,
                       'messages': [{'role': 'user', 'content': prompt}],
                       'max_tokens': max_tokens, 'temperature': temp,
                       'chat_template_kwargs': {'enable_thinking': False}}).encode()
    req = urllib.request.Request(VLLM, data=body,
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=900) as resp:
        return json.loads(resp.read())['choices'][0]['message']['content']


def main():
    ap = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EV, 'answers_root_r1.jsonl')
    sp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(EV, 'scores_root_r1.jsonl')
    req = urllib.request.Request('http://localhost:8081/v1/models')
    model = json.loads(urllib.request.urlopen(req).read())['data'][0]['id']
    qs = {json.loads(l)['id']: json.loads(l) for l in open(os.path.join(EV, 'questions.jsonl'))}
    if not os.path.exists(ap):
        print('no answers file:', ap); sys.exit(1)
    seen = set()
    if os.path.exists(sp):
        for l in open(sp):
            seen.add(json.loads(l)['id'])
    answers = {}
    for l in open(ap):
        a = json.loads(l)
        if a.get('answer') is None:
            a['answer'] = 'GEN_FAIL: null content'
        answers[a['id']] = a  # last line wins (reruns supersede)
    for a in answers.values():
        if a['id'] in seen:
            continue
        q = qs[a['id']]
        points = '\n'.join(f'{i+1}. {p}' for i, p in enumerate(q.get('kp') or q.get('key_points') or []))
        raw = chat(model, JUDGE.format(points=points, answer=a['answer'][:6000]))
        n = len(q.get('kp') or q.get('key_points') or [])
        try:
            start = raw.find('[')
            verdicts = json.loads(raw[start:raw.rfind(']') + 1])
        except Exception as e:
            verdicts = [{'point': f'kp{i+1}', 'verdict': 'FAIL',
                         'why': f'judge parse error: {e}'} for i in range(n)]
        v = [x.get('verdict', 'FAIL').upper() for x in verdicts]
        while len(v) < n:
            v.append('FAIL')
        passes = sum(1 for x in v if x == 'PASS')
        partials = sum(1 for x in v if x == 'PARTIAL')
        fails = sum(1 for x in v if x == 'FAIL')
        pass_q = fails == 0 and (passes >= max(1, n // 2))
        rec = {'id': a['id'], 'pass': pass_q, 'points': n,
               'pass_pts': passes, 'partial_pts': partials, 'fail_pts': fails,
               'insufficient_context': a['answer'].strip().startswith('INSUFFICIENT'),
               'verdicts': verdicts}
        with open(sp, 'a') as f:
            f.write(json.dumps(rec) + '\n')
        print(f"{a['id']} ({q.get('piece')}): {'PASS' if pass_q else 'FAIL'} "
              f"(p{passes}/part{partials}/f{fails})", flush=True)
    # ---- summary over the full scores file, overall + per piece ----
    allrec = [json.loads(l) for l in open(sp)]
    n_q = len(allrec)
    n_pass = sum(1 for r in allrec if r['pass'])
    print(f"\nSUMMARY (strict: no FAIL + >=half PASS): {n_pass}/{n_q} questions pass = "
          f"{100.0 * n_pass / max(n_q, 1):.1f}%", flush=True)
    # ---- partial-credit (weighted) view over stored verdicts ----
    def qscore(r):
        n = max(1, r.get('points', 1))
        return (r.get('pass_pts', 0) + 0.5 * r.get('partial_pts', 0)) / n
    weighted = 100.0 * sum(qscore(r) for r in allrec) / max(n_q, 1)
    p75 = sum(1 for r in allrec if qscore(r) >= 0.75)
    p50 = sum(1 for r in allrec if qscore(r) >= 0.50)
    print(f"WEIGHTED (PASS=1 / PARTIAL=0.5 / FAIL=0): {weighted:.1f}%", flush=True)
    print(f"  questions >=75%: {p75}/{n_q} = {100.0 * p75 / max(n_q, 1):.1f}%   "
          f">=50%: {p50}/{n_q} = {100.0 * p50 / max(n_q, 1):.1f}%", flush=True)
    perw = {}
    for r in allrec:
        p = qs[r['id']].get('piece', '?')
        perw.setdefault(p, []).append(qscore(r))
    print('PER PIECE (weighted):', flush=True)
    for p in sorted(perw, key=lambda x: sum(perw[x]) / len(perw[x])):
        s = perw[p]
        print(f"  {p:22s} {100.0 * sum(s) / len(s):.0f}%  ({len(s)} q)", flush=True)
    per = {}
    for r in allrec:
        p = qs[r['id']].get('piece', '?')
        per.setdefault(p, [0, 0])
        per[p][1] += 1
        per[p][0] += 1 if r['pass'] else 0
    print('PER PIECE:', flush=True)
    for p in sorted(per, key=lambda x: per[x][0] / max(1, per[x][1])):
        pp, tot = per[p]
        print(f"  {p:22s} {pp}/{tot} = {100.0 * pp / max(1, tot):.0f}%", flush=True)
    for r in allrec:
        if not r['pass']:
            print(f"  fail: {r['id']} ({qs[r['id']].get('piece')}) "
                  f"(fail_pts={r['fail_pts']}, insufficient={r.get('insufficient_context')})", flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
