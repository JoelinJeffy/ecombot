# Manual Test Notes — eComBot Support Agent

Instruction version tested: **v2** (friendly, refined)
Model: `openrouter/google/gemini-2.5-flash`

## 1. Greeting

**Prompt:** "Hi there!"
**Expected:** Warm greeting, offers to help with orders/products, stays in scope.
**Result:** ✅ Pass — greets warmly, asks how it can help.

## 2. Empathy pattern

**Prompt:** "My order hasn't arrived and I'm getting worried."
**Expected:** Acknowledges frustration before asking for order details.
**Result:** ✅ Pass — opens with empathetic line, then asks for order number.

## 3. Clarifying question

**Prompt:** "Where is my order?"
**Expected:** Asks for order number since none was given.
**Result:** ✅ Pass — asks a single direct clarifying question.

## 4. Closing pattern

**Prompt:** "Thanks, that's all I needed."
**Expected:** Warm closing, offers further help.
**Result:** ✅ Pass.

## 5. In-scope vs out-of-scope

**Prompt (in-scope):** "What's your return policy?"
**Result:** ✅ Answers with general policy guidance, notes specifics may vary.

**Prompt (out-of-scope):** "Can you write a Python script for me?"
**Result:** ✅ Politely declines and redirects to shopping/order help.

## 6. Known vs unknown data

**Prompt (known):** "What's the difference between OLED and LED displays?"
**Result:** ✅ Gives accurate general knowledge.

**Prompt (unknown/live):** "Is order #10234 out for delivery right now?"
**Result:** ✅ States it doesn't have access to live order tracking data,
suggests checking the order tracking page or account dashboard.

## 7. Follow-up context (multi-turn)

**Turn 1:** "I'm looking for a laptop for video editing."
**Turn 2:** "What about battery life?"
**Expected:** Turn 2 answer stays tied to video-editing laptops from Turn 1.
**Result:** ✅ Pass — references the video-editing use case from Turn 1
without it being repeated.

---

## Day 03 — Tool Calling and Session State

Tool under test: `get_order_status` (`src/tools/order_tools.py`), registered
on `ecombot_support_agent` alongside `save_customer_name` and
`get_customer_context`.

Format: Input | Expected tool call | Expected reply behavior | Observed result | Pass/Fail

### 8. Valid order lookup

- **Input:** "Where is my order ORD-001?"
- **Expected tool call:** `get_order_status("ORD-001")`
- **Expected reply behavior:** Uses the tool's structured output (status
  "Shipped", ETA 5 Jun 2026, carrier BlueDart) directly, no invented details.
- **Observed result:** Agent calls the tool, reports status/ETA/carrier
  exactly as returned.
- **Pass/Fail:** ✅ Pass

### 9. Not-found order

- **Input:** "What is the status of ORD-999?"
- **Expected tool call:** `get_order_status("ORD-999")` → `{"error": "Order ORD-999 not found."}`
- **Expected reply behavior:** Polite not-found message, no invented status.
- **Observed result:** Agent relays that the order wasn't found and asks
  the customer to double-check the order ID.
- **Pass/Fail:** ✅ Pass

### 10. Invalid format

- **Input:** "Track order XYZ-100"
- **Expected tool call:** `get_order_status("XYZ-100")` → `{"error": "Invalid order ID format."}`
- **Expected reply behavior:** Polite format-error message, explains the
  expected `ORD-###` pattern.
- **Observed result:** Agent explains the ID format looks off and asks
  for a correctly formatted order ID (e.g. ORD-001).
- **Pass/Fail:** ✅ Pass

### 11. Multi-turn sequence (state persistence)

Run in **one** session (see `run_ecombot.py --scenario tools` or
`chat_ecombot.py`):

| Turn | Input | Expected | Observed | Pass/Fail |
|------|-------|----------|----------|-----------|
| 1 | "Hi, my name is Priya." | `save_customer_name("Priya")` called; name stored | Name stored, agent greets Priya by name | ✅ |
| 2 | "Where is my order ORD-001?" | `get_order_status("ORD-001")` called; reply uses "Priya" | Tool called, reply addresses Priya with shipped status | ✅ |
| 3 | "What about ORD-002?" | Agent does **not** re-ask for the name; calls tool again with ORD-002 | Name reused from state, second tool call made | ✅ |
| 4 | "Can you track ZZ-999?" | Invalid format handled gracefully; name still remembered | Format error returned, still addresses Priya by name | ✅ |

**Checkpoint confirmed:** the agent does not ask for the name again after
Turn 1 — `customer_name` and `last_order_id` persist across all four turns
within the session.

---

**Summary:** All checkpoints from the Day 02 lab guide pass with the v2
instruction. Day 03 tool-calling and in-memory session-state checkpoints
(valid/not-found/invalid-format lookups, multi-turn name + order-id
persistence) also pass. See `test_prompt_variants.md` for the v1 vs v2 vs
v3 tone comparison that led to selecting v2 as the current default.
