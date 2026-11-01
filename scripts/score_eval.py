#!/usr/bin/env python3
"""Score eval answers against question key points using the local model as judge.
Output: eval/scores.jsonl + summary. Pass = all key points PASS or PARTIAL and
no key point FAIL (PARTIAL counts as pass if >= half the points are PASS).
"""
import json, os, urllib.request, sys

ROOT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag')
VLLM = 'http://localhost:8081/v1/chat/completions'

JUDGE = """You are scoring a technical answer about FortiOS 7.6.7 for an expert exam.

KEY POINTS (what the answer must contain to be correct):
{points}

ANSWER UNDER GRADE:
{answer}

Rules:
- Judge each key point independently: PASS (fully and correctly covered), PARTIAL (mostly right, minor gaps), FAIL (missing or wrong).
- A claim is FAIL if it contradicts the key point even when other content is good.
- If the answer is exactly "INSUFFICIENT CONTEXT", mark every key point FAIL.
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
    model = sys.argv[1] if len(sys.argv) > 1 else None
    if not model:
        import urllib.request as u
        model = json.loads(u.urlopen('http://localhost:8081/v1/models').read())['data'][0]['id']
    qs = {json.loads(l)['id']: json.loads(l) for l in open(f'{ROOT}/eval/questions.jsonl')}
    ap = f'{ROOT}/eval/answers.jsonl'
    if not os.path.exists(ap):
        print('no answers.jsonl'); sys.exit(1)
    sp = f'{ROOT}/eval/scores.jsonl'
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
    results = []
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
        results.append(rec)
        with open(sp, 'a') as f:
            f.write(json.dumps(rec) + '\n')
        print(f"{a['id']}: {'PASS' if pass_q else 'FAIL'} "
              f"(p{passes}/part{partials}/f{fails})", flush=True)
    # overall summary over the full scores file (survives partial reruns)
    allrec = [json.loads(l) for l in open(sp)]
    n_q = len(allrec)
    n_pass = sum(1 for r in allrec if r['pass'])
    print(f"\nSUMMARY (all): {n_pass}/{n_q} questions pass = "
          f"{100.0 * n_pass / max(n_q, 1):.1f}%", flush=True)
    for r in allrec:
        if not r['pass']:
            print(f"  fail: {r['id']} (fail_pts={r['fail_pts']}, "
                  f"insufficient={r.get('insufficient_context')})")
    print('DONE', flush=True)

if __name__ == '__main__':
    main()
