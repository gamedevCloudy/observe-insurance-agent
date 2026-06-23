# Agent Eval Harness

LLM-as-judge evaluation for the Observe Insurance claims support agent.

## Architecture

```
Scenario → Real Agent (OpenRouter LLM) → Tool calls + response → Judge (qwen/qwen3.7-plus) → pass/fail + reasoning → TSV
```

- 33 scenarios across 7 categories
- LLM-as-judge with retries (exponential backoff, 3 attempts)
- Parallel execution via `asyncio.gather` with semaphore(3) concurrency
- TSV output to `tests/evals/results/evals_<timestamp>.csv` via `atexit`
- Zero new dependencies — reuses existing pytest, langchain, sqlalchemy

## Running

```bash
cd obvserve-insurance-support
uv run pytest tests/evals/ -v          # all evals (8+ min)
uv run pytest tests/evals/test_auth.py -v   # single category
uv run pytest -m "not evals"               # skip evals (unit tests)
```

## Current Status (2026-06-23 15:24 UTC)

**Pass: 26/33** (baseline run `evals_20260623_152454.csv`)

| Category | Pass | Failing |
|---|---|---|
| authentication | 5/6 | auth-03 |
| call_log | 2/4 | log-03, log-04 |
| claims | 5/5 | — |
| edge_cases | 4/4 | — |
| escalation | 4/6 | esc-03, esc-06 |
| faq | 4/5 | faq-05 |
| multiturn | 2/3 | multi-02 |

### Failures Detail

| Scenario | Category | Score | Cause |
|---|---|---|---|
| auth-03 | authentication | 2/3 | Phone not found — agent calls `escalate` tool instead of verbally offering a rep |
| log-03 | call_log | 1/2 | Single-turn scenario: agent asked for phone, caller never responded — judge can't eval 2nd criterion |
| log-04 | call_log | 1/3 | No `create_call_log` after "OK thanks, bye" — agent didn't detect end-of-call |
| esc-03 | escalation | 2/3 | Emergency — agent greeted + asked questions before transferring (should skip pleasantries) |
| esc-06 | escalation | 2/3 | Frustrated caller — no empathy before escalating |
| faq-05 | faq | 2/3 | Chocolate cake question — agent didn't explain "outside scope" before transferring |
| multi-02 | multiturn | 1/3 | Re-looked up customer each turn instead of reusing context |

## Scenarios

### authentication (6)
- auth-01: Valid phone → finds Alice Johnson, confirms identity
- auth-02: Greeting before asking for phone
- auth-03: Phone not found → handles gracefully
- auth-04: Not found → doesn't proceed with claims
- auth-05: Bob Smith authenticates
- auth-06: Prior interaction history → continuity

### claims (5)
- claim-01: Alice — under_review, docs required
- claim-02: Bob — approved, no docs needed
- claim-03: Docs required → send_sms triggered
- claim-04: Policy tier + claim amount (no fabrication)
- claim-05: Single-turn — plan and claim

### faq (5)
- faq-01: Office hours
- faq-02: Mailing address (regional)
- faq-03: How to start a new claim
- faq-04: Claims process timeline
- faq-05: Unrelated question (chocolate cake) → escalate

### escalation (6)
- esc-01: Request human representative
- esc-02: "Operator" keyword → escalate
- esc-03: Emergency (car accident with injuries)
- esc-04: Unrelated question (sports score) → out-of-knowledge
- esc-05: Emergency (house fire) → persist to DB
- esc-06: Frustrated caller → empathy + escalation

### call_log (4)
- log-01: Create call log at end of interaction
- log-02: Call log includes summary and sentiment
- log-03: Unauthenticated caller (cust_id=0)
- log-04: Call log stores interaction for future sessions

### multiturn (3)
- multi-01: Full happy path
- multi-02: Context retention across turns
- multi-03: FAQ mid-conversation + return to claim

### edge_cases (4)
- edge-01: Don't share customer data
- edge-02: No legal advice
- edge-03: TTS-friendly output (no markdown)
- edge-04: Looping → escalate

## Judge

Model: `qwen/qwen3.7-plus` (configurable via `EVAL_JUDGE_MODEL` env var). Evaluate each scenario against its criteria. See `judge.py` for prompt template.

## CSV Output

Results written to `results/evals_<timestamp>.csv` (tab-delimited). Fields:

- run, scenario, category, pass, score, criteria_met, criteria_total, judge_notes, tool_calls, agent_summary, duration_ms