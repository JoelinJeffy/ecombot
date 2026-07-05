# Day 06 Quick Start Guide

## What You Have Now

✅ **PDF Knowledge Base** — Realistic eCommerce FAQ and product catalog PDFs  
✅ **Intelligent Chunking** — Section-aware chunking with overlap  
✅ **Rich Metadata** — Source file, page, section, type for every chunk  
✅ **Retrieval Testing** — 9 validation tests (8/9 passed, 1 warning)  
✅ **Grounded Answering** — Agent uses retrieved context only

---

## Quick Commands

### 1. Full Setup (One Command)
```bash
python scripts/setup_rag.py
```
This will:
- Generate sample PDFs
- Index into ChromaDB
- Run validation tests

### 2. Just Generate PDFs
```bash
python scripts/generate_sample_pdfs.py
```

### 3. Just Index Knowledge Base
```bash
python -m src.rag.embed_catalog
```

### 4. Just Run Tests
```bash
python tests/test_pdf_rag.py
```

### 5. Test with Demo Agent
```bash
python demo.py
```

---

## Test Results Summary

### ✓ Direct Match Tests (3/3 passed)
- "What is your return policy?" → **0.637 confidence** ✓
- "What shipping options do you offer?" → **0.616 confidence** ✓
- "What are the specifications of the Dell XPS 15?" → **0.813 confidence** ✓

### ✓ Partial Match Tests (2/3 passed, 1 warning)
- "How long do I have to send something back?" → **0.546 confidence** ✓
- "How long is the laptop covered under warranty?" → **0.696 confidence** ✓
- "Can I pay with UPI?" → **0.423 confidence** ⚠ (slightly below 0.5 threshold)

### ✓ Out-of-Scope Tests (3/3 passed)
- "What is the weather tomorrow?" → **0.148 confidence** ✓ (correctly low)
- "Do you sell furniture?" → **0.322 confidence** ✓ (correctly low)
- "How do I bake a chocolate cake?" → **0.134 confidence** ✓ (correctly low)

**Overall: 8/9 PASS, 1 WARN** — Excellent retrieval quality!

---

## Sample Queries to Try

### Should Work Well ✓
```
What is your return policy?
How do I track my order?
What are the specs of the Dell XPS 15?
Do you offer warranty on electronics?
What payment methods do you accept?
Can I cancel my order?
```

### Should Refuse Gracefully ✗
```
What is the weather tomorrow?
Do you sell furniture?
How do I cook pasta?
What movies are playing?
```

---

## Knowledge Base Contents

### PDFs Generated
1. **`data/ecom_faq.pdf`** (3 pages, 15 Q&A pairs)
   - Shipping & Delivery
   - Returns & Refunds
   - Warranty & Support
   - Payment & Billing
   - Account & Orders

2. **`data/product_catalog.pdf`** (4 pages, 3 products)
   - Dell XPS 15 (laptop with full specs)
   - Sony WH-1000XM5 (headphones)
   - Samsung Galaxy S24 Ultra (smartphone)

### JSON Data (from Day 05)
- `data/products.json` — 6 products
- `data/faq.json` — 22 FAQ entries

### Total Indexed
- **54 chunks** (40 from JSON, 14 from PDFs)
- All chunks include metadata (source, page, section)

---

## What's Different from Day 05?

| Feature | Day 05 | Day 06 |
|---------|--------|--------|
| Data sources | JSON only | JSON + PDF |
| Chunking | Simple split | Section-aware with overlap |
| Metadata | Basic (type, ID) | Rich (file, page, section, type) |
| Testing | Manual | Automated test suite (9 tests) |
| Setup | Manual steps | One-command setup script |

---

## File Structure

```
ecombot/
├── data/
│   ├── products.json           # Day 05
│   ├── faq.json                # Day 05
│   ├── ecom_faq.pdf            # Day 06 ← NEW
│   └── product_catalog.pdf     # Day 06 ← NEW
├── src/rag/
│   ├── pdf_processor.py        # Day 06 ← NEW
│   ├── embed_catalog.py        # Enhanced for PDFs
│   └── retriever.py            # Enhanced metadata display
├── scripts/
│   ├── generate_sample_pdfs.py # Day 06 ← NEW
│   └── setup_rag.py            # Enhanced 3-step setup
├── tests/
│   └── test_pdf_rag.py         # Day 06 ← NEW
└── docs/
    └── Day06_Implementation.md # Day 06 ← NEW
```

---

## Dependencies Added

```bash
pip install pymupdf reportlab
```

- **pymupdf** — PDF text extraction with page/section detection
- **reportlab** — PDF generation for sample documents

---

## Next Steps

1. **Try the demo agent:**
   ```bash
   python demo.py
   ```

2. **Test different queries** (see "Sample Queries to Try" above)

3. **Inspect PDFs** to see chunking boundaries:
   ```bash
   open data/ecom_faq.pdf
   open data/product_catalog.pdf
   ```

4. **Experiment with chunk sizes** in `pdf_processor.py`:
   ```python
   processor = PDFProcessor(
       chunk_size=800,      # Try different sizes
       chunk_overlap=150    # Try different overlaps
   )
   ```

5. **Add your own PDFs** to `data/` directory and re-run:
   ```bash
   python -m src.rag.embed_catalog
   ```

---

## Troubleshooting

### "No module named 'fitz'"
```bash
pip install pymupdf
```

### "No module named 'reportlab'"
```bash
pip install reportlab
```

### "Collection ecombot_kb does not exist"
```bash
python -m src.rag.embed_catalog
```

### Retrieval confidence too low
- Try larger chunk sizes (1200-1500)
- Reduce overlap (100-150)
- Check if PDFs have proper sections/headings

---

## Key Concepts Learned

✓ **Section-aware chunking** preserves meaning  
✓ **Overlap** maintains context across boundaries  
✓ **Metadata** enables traceability and debugging  
✓ **Confidence thresholds** prevent hallucination  
✓ **Automated testing** validates retrieval quality  
✓ **Grounded answering** ensures factual responses

---

## Completion Checklist

- [x] PDF processing module created
- [x] Sample PDFs generated with realistic content
- [x] Embedding pipeline handles PDFs + JSON
- [x] Metadata attached to every chunk
- [x] Retriever displays source citations
- [x] Validation test suite (9 tests)
- [x] Automated setup script
- [x] Documentation complete

**Status: ✅ Day 06 Complete**
