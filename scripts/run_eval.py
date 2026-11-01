#!/usr/bin/env python3
"""Eval harness: for each question in eval/questions.jsonl,
retrieve (container query.py) -> generate answer (:8081) -> eval/answers.jsonl
Usage: run_eval.py [qids_csv]
"""
import json, subprocess, urllib.request, sys, os, time

ROOT = os.path.expanduser('~/.hermes/cache/scratch/fortios-rag')
VLLM = 'http://localhost:8081/v1/chat/completions'
MODEL = sys.argv[2] if len(sys.argv) > 2 else None

PROMPT = """You are a Fortinet engineer specializing in FortiOS 7.6.x and 8.0.x, CLI and REST API v2.

You have two sources:
1. SKILL CORE — curated, source-verified summary of FortiOS 7.6.x/8.0.x (distilled from the official docs; the authoritative quick reference).
2. RAG CONTEXT — raw chunks retrieved from the official FortiNet 7.6.x/8.0.x documentation set plus verified community field reports (doc name, heading and page number shown).

Answer the question using ONLY these two sources. If neither contains the answer, say exactly: INSUFFICIENT CONTEXT. Be precise and technical. Quote exact CLI commands / API endpoints / values verbatim where relevant. Cite RAG-context facts as (doc, page); cite skill-core facts as (skill).

Method — combine BOTH sources, do not let one crowd out the other:
(a) Scan the SKILL CORE for the section(s) matching the topic; it is the distilled, authoritative quick reference — quote its specific fields, defaults and caveats.
(b) Scan the RAG CONTEXT for the supporting verbatim facts and page numbers.
(c) Your final answer must cover everything BOTH sources state on the topic — when the RAG context is narrow, still add the skill-core details on that topic (and vice versa). Do not summarize away specifics present in either source.

=== SKILL CORE ===
{skill}

=== RAG CONTEXT ===
{context}

QUESTION: {q}
"""

def retrieve(q, k=12):
    r = subprocess.run(['docker', 'exec', 'fortios-rag-tmp', 'python3',
                        '/work/scripts/query.py', q, str(k)],
                       capture_output=True, text=True, timeout=600)
    return json.loads(r.stdout)

def generate(q, context, skill, model, max_tokens=3000, retries=3):
    body = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': PROMPT.format(skill=skill, context=context, q=q)}],
        'max_tokens': max_tokens, 'temperature': 0.0,
        'chat_template_kwargs': {'enable_thinking': False},
    }).encode()
    t0 = time.time()
    last = ''
    for attempt in range(retries):
        req = urllib.request.Request(VLLM, data=body, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                d = json.loads(resp.read())
        except Exception as e:
            last = f'request error: {e}'
            time.sleep(5)
            continue
        ch = d.get('choices') or [{}]
        content = (ch[0].get('message') or {}).get('content')
        if content:
            return content, time.time() - t0
        last = f'empty content (finish_reason={ch[0].get("finish_reason")})'
        time.sleep(5)
    return f'GEN_FAIL: {last}', time.time() - t0

def main():
    global MODEL
    qs = [json.loads(l) for l in open(os.path.join(ROOT, 'eval', 'questions.jsonl'))]
    if len(sys.argv) > 1:
        want = set(sys.argv[1].split(','))
        qs = [q for q in qs if q['id'] in want]
    if not MODEL:
        req = urllib.request.Request('http://localhost:8081/v1/models')
        MODEL = json.loads(urllib.request.urlopen(req).read())['data'][0]['id']
    print('model:', MODEL, 'questions:', len(qs), flush=True)
    skill = open(os.path.expanduser(
        '~/.hermes/skills/hermes-it-infosec-fw-fortig-fortios-7-6-7/SKILL.md')).read()
    out = []
    done = {}
    ap = os.path.join(ROOT, 'eval', 'answers.jsonl')
    if os.path.exists(ap):
        for l in open(ap):
            r = json.loads(l)
            done[r['id']] = r
    for i, q in enumerate(qs):
        if q['id'] in done:
            out.append(done[q['id']]); continue
        ctx = retrieve(q['q'])
        context = '\n\n'.join(
            f"[{c['doc']} | {c['heading']} | p.{c['page']}]\n{c['text'][:2500]}"
            for c in ctx)
        try:
            ans, dt = generate(q['q'], context, skill, MODEL)
        except Exception as e:
            ans, dt = f'GEN_FAIL: {e}', 0
        r = {'id': q['id'], 'q': q['q'], 'answer': ans, 'ctx': [
            {'chunk_id': c['chunk_id'], 'doc': c['doc'], 'heading': c['heading'],
             'page': c['page'], 'score': c['score']} for c in ctx],
            'gen_secs': round(dt, 1)}
        out.append(r)
        with open(ap, 'a') as f:
            f.write(json.dumps(r) + '\n')
        print(f"[{i+1}/{len(qs)}] {q['id']} {dt:.0f}s {ans[:60]!r}", flush=True)
    print('DONE', len(out), flush=True)

if __name__ == '__main__':
    main()
