#!/usr/bin/env python3
"""Root-index exam — live-client emulation (K4=C).

Emulates what a live Hermes client does:
  1. RAG CONTEXT  = query_root.py over the compiled root index
                    (REQUIRED product/line filter: fortios / 7.6x).
  2. SKILL CORE   = router skill + the question's piece skill
                    (each question carries a `piece` field; piece='cross'
                    -> platform, the dependency root).
  3. Generate     = local Qwen3.8-27B (:8081), enable_thinking=False,
                    max_tokens 3000, 3 retries on GEN_FAIL.

Usage:
  eval_root.py [out.jsonl] [qids_csv]
Defaults: out = <surface>/eval/answers_root_r1.jsonl, all questions.
Resumes: ids already present in out.jsonl are skipped.

Runs on the HOST (needs docker + :8081). The retrieval container uses a
persistent ONNX embedding cache at /home/chrismok/.cache/chroma-onnx so
the 79MB model is downloaded once, not per query.
"""
import json, subprocess, urllib.request, sys, os, time

CORPUS = '/home/chrismok/fortinet-corpus'
SURFACE = os.path.join(CORPUS, sys.argv[1] if len(sys.argv) > 1 else 'fortios-7.6x')
PRODUCT, LINE, K = (sys.argv[2] if len(sys.argv) > 2 else 'fortios',
                    sys.argv[3] if len(sys.argv) > 3 else '7.6x', 16)
PRODUCT_NAME = sys.argv[4] if len(sys.argv) > 4 else 'FortiGate'
SKILLS = os.path.expanduser('~/.hermes/skills')
ROUTER = os.path.join(SKILLS, 'hermes-it-infosec-fw-fortig-fortios-7-6-7', 'SKILL.md')
PIECE_DIR = os.path.join(SKILLS, 'fortinet')
VLLM = 'http://localhost:8081/v1/chat/completions'
ONNX_CACHE = os.path.expanduser('~/.cache/chroma-onnx')

PROMPT = """You are a Fortinet engineer specializing in FortiOS 7.6.x and 8.0.x, CLI and REST API v2.

You have two sources:
1. SKILL CORE — curated, source-verified knowledge (router + the domain piece skill; distilled from the official docs; the authoritative quick reference).
2. RAG CONTEXT — raw chunks retrieved from the official FortiNet documentation corpus (doc name, heading and page number shown).

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


def retrieve(q, k=K):
    r = subprocess.run([
        'docker', 'run', '--rm',
        '--mount', f'type=bind,src={CORPUS},dst={CORPUS}',
        '--mount', f'type=bind,src={ONNX_CACHE},dst=/root/.cache/chroma',
        'zeppo-rag:cli', 'python3', os.path.join(CORPUS, 'query_root.py'),
        q, str(k), '--product', PRODUCT, '--line', LINE,
    ], capture_output=True, text=True, timeout=600)
    return json.loads(r.stdout)


def skill_core(piece):
    parts = [open(ROUTER).read()]
    p = 'platform' if piece in ('cross', 'unassigned', '', None) else piece
    fp = os.path.join(PIECE_DIR, f'fortinet-{p}', 'SKILL.md')
    if os.path.exists(fp):
        parts.append(open(fp).read())
    return '\n\n---\n\n'.join(parts)


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
    out = os.path.join(SURFACE, 'eval', f'answers_root_{LINE}.jsonl')
    qs = [json.loads(l) for l in open(os.path.join(SURFACE, 'eval', 'questions.jsonl'))]
    if len(sys.argv) > 5:
        want = set(sys.argv[5].split(','))
        qs = [q for q in qs if q['id'] in want]
    pieces = sorted({q.get('piece') for q in qs})
    print(f'questions: {len(qs)}; pieces: {pieces}', flush=True)
    req = urllib.request.Request('http://localhost:8081/v1/models')
    model = json.loads(urllib.request.urlopen(req).read())['data'][0]['id']
    print('model:', model, flush=True)
    done = {}
    if os.path.exists(out):
        for l in open(out):
            r = json.loads(l)
            done[r['id']] = r
    for i, q in enumerate(qs):
        if q['id'] in done:
            continue
        piece = q.get('piece')
        ctx = retrieve(q['q'])
        context = '\n\n'.join(
            f"[{c['doc']} | {c['heading']} | p.{c['page']} | piece={c.get('piece')}]\n{c['text'][:2500]}"
            for c in ctx)
        skill = skill_core(piece)
        try:
            ans, dt = generate(q['q'], context, skill, model)
        except Exception as e:
            ans, dt = f'GEN_FAIL: {e}', 0
        r = {'id': q['id'], 'piece': piece, 'q': q['q'], 'answer': ans,
             'ctx': [{'id': c['id'], 'doc': c['doc'], 'heading': c['heading'],
                      'page': c['page'], 'piece': c.get('piece'), 'score': c['score']} for c in ctx],
             'skill_piece': piece, 'gen_secs': round(dt, 1)}
        with open(out, 'a') as f:
            f.write(json.dumps(r) + '\n')
        print(f"[{i+1}/{len(qs)}] {q['id']} ({piece}) {dt:.0f}s {ans[:60]!r}", flush=True)
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
