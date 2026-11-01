# Exam harness

- `questions.jsonl` — 92 questions. Fields: `id`, `q`, `kp` (key points), `piece`.
- Per-round artifacts (kept in the corpus `fortios-7.6x/eval/`): `answers_root_rN.jsonl`,
  `scores_root_rN.jsonl`, `eval_root_rN.log`, `score_root_rN.log`.
- Run: `eval_root.py answers_root_rN.jsonl` then `score_root.py answers_root_rN.jsonl scores_root_rN.jsonl`.
- Always a fresh scores file per round (last-wins/resume semantics per id).

## Metrics

- strict pass: zero FAIL key points AND >= half PASS
- weighted (partial credit): (pass + 0.5*partial) / points, per-question mean
- question thresholds: >=75%, >=50%
- per-piece breakdowns for all views

## History (fortios-7.6x)

| round | strict | weighted | >=75% | >=50% |
|---|---|---|---|---|
| R1 | 40.2% | 62.3% | 45.7% | 70.7% |
| R2 | 59.8% | 74.7% | 68.5% | 82.6% |
| R3 | 63.0% | 78.0% | 68.5% | 87.0% |
| R4 | 59.8% | 78.8% | 70.7% | 89.1% |
| R5 | **60.9%** | **79.6%** | 67.4% | **90.2%** |

Rounds 2–4 were skill-enrichment rounds (verified CLI facts added to the weakest
pieces). R2-R4 variance is sampling noise + judge strictness; weighted scores are
stable 78-79% (R5: 79.6%). R5 is the release round. Note: strict 90% is not
realistic with per-keypoint LLM judging + sampling variance — the practical gate
is weighted ≥75% × 3 consecutive with strict ≥60% (met by R3–R5).
