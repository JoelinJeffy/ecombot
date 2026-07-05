# eComBot v3 RAG Manual Testing (Day 05)

## Test Setup
- ChromaDB collection built with product and FAQ data
- Agent using v4 grounded instruction with hallucination guards
- RAG retrieval via `search_knowledge_base` tool

---

## Test Case 1: Clean Match (Product Specs)

**Query:** "What are the specifications of the Dell XPS 15 laptop?"

**Expected Behavior:**
- `search_knowledge_base` retrieves product specs chunk
- Agent answers with specific details from retrieved knowledge
- No hallucinated information

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 2: Partial Match (Policy Question)

**Query:** "What is your return policy for laptops?"

**Expected Behavior:**
- `search_knowledge_base` retrieves return policy FAQ
- Agent provides policy details from knowledge base
- Mentions specific return window and conditions

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 3: Fallback (No Match)

**Query:** "Do you sell gaming consoles like PlayStation 5?"

**Expected Behavior:**
- `search_knowledge_base` returns no relevant results or weak match
- Agent uses fallback message: "I don't have specific information about that..."
- Does NOT invent product availability

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 4: Hallucination Trap

**Query:** "What is the screen size of the Sony WH-1000XM5?"

**Expected Behavior:**
- `search_knowledge_base` retrieves headphone info (no screen)
- Agent recognizes headphones don't have screens
- Does NOT invent a screen size
- May use fallback or clarify product type

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 5: Shipping Policy

**Query:** "How much does shipping cost and how long does it take?"

**Expected Behavior:**
- `search_knowledge_base` retrieves shipping FAQ
- Agent provides free shipping threshold, delivery times, express options
- Details match FAQ data

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 6: Warranty Question

**Query:** "Does the Dell XPS 15 warranty cover accidental damage?"

**Expected Behavior:**
- `search_knowledge_base` retrieves warranty information for Dell XPS 15
- Agent mentions 1 year accidental damage protection (from product data)
- Cites specific warranty terms

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 7: Out-of-Stock Handling

**Query:** "When will the Samsung Galaxy S24 be back in stock?"

**Expected Behavior:**
- `search_knowledge_base` retrieves product info with stock note
- Agent mentions expected restock date (July 15, 2026 from product data)
- Does NOT invent availability

**Retrieved Chunks:**
```
[To be filled during test run]
```

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Test Case 8: Empty Collection Handling

**Query:** [Any query after deleting ChromaDB collection]

**Expected Behavior:**
- `search_knowledge_base` handles missing collection gracefully
- Returns appropriate error message
- Agent uses fallback without crashing

**Agent Response:**
```
[To be filled during test run]
```

**Result:** ☐ Pass ☐ Fail

**Notes:**


---

## Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| 1. Clean Match | ☐ | |
| 2. Partial Match | ☐ | |
| 3. Fallback | ☐ | |
| 4. Hallucination Trap | ☐ | |
| 5. Shipping Policy | ☐ | |
| 6. Warranty Question | ☐ | |
| 7. Out-of-Stock | ☐ | |
| 8. Empty Collection | ☐ | |

**Overall Assessment:**
- Grounding effectiveness: [To be filled]
- Hallucination guard effectiveness: [To be filled]
- Retrieval quality: [To be filled]
- Fallback appropriateness: [To be filled]

**Issues Found:**
1. 
2. 
3. 

**Recommendations:**
1. 
2. 
3. 
