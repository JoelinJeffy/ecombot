# Prompt Variant Comparison — eComBot Support Agent

Same base agent code (`support_agent.py`), same question, three different
instruction files swapped in.

**Question used for comparison:** "My order is late and I need it by Friday, what can I do?"

## v1 — Baseline (Day 01)

- Tone: plain, functional.
- Behavior: answers directly, minimal empathy, no clarifying question
  about the order number.
- Verdict: works, but too generic for a real support scenario.

## v2 — Friendly (Day 02 refinement)

- Tone: warm, conversational, empathetic opener ("That sounds
  frustrating, let's sort it out").
- Behavior: asks for the order number, explains it can't check live
  status but describes what the customer can do (check tracking page,
  contact carrier, request expedited replacement if eligible).
- Verdict: best balance of warmth and usefulness. **Selected as current
  default** (`ECOMBOT_INSTRUCTION_VERSION` defaults to `v2`).

## v3 — Formal (Day 02 refinement)

- Tone: professional, no filler.
- Behavior: acknowledges the request directly, asks for order number in
  one line, gives the same practical next steps as v2 but more tersely.
- Verdict: good fit for a B2B or enterprise support surface; too curt
  for a general consumer storefront.

## Refinement notes

- v1 → v2/v3: added explicit empathy/acknowledgment step, explicit
  clarifying-question instruction, and explicit "do not invent live
  data" guardrail (v1 lacked this and occasionally guessed at delivery
  windows).
- Out-of-scope handling was added in v2/v3 after v1 answered an
  unrelated coding question directly instead of redirecting.
- Re-ran the baggage/return-policy and coding-question prompts after
  each revision to confirm scope boundaries held.

## Current status

`support_agent.py` defaults to **v2**. Switch versions for testing with:

```bash
python run_ecombot.py --version v1
python run_ecombot.py --version v3
```

or by setting `ECOMBOT_INSTRUCTION_VERSION=v3` before running `adk web`.
