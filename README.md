# eComBot — Production-Ready AI Support Agent

A complete e-commerce support agent built with Google ADK, featuring intelligent LLM routing, RAG-powered knowledge base, and production-grade data persistence.

## 🎯 What This Is

**eComBot v4** is a fully-functional AI customer support agent for electronics e-commerce that demonstrates:

- **Intelligent LLM Routing** — Routes queries to optimal models (fast/cheap vs deep/capable)
- **RAG Knowledge Base** — Answers grounded in PDF documents with hallucination prevention
- **Production Data Layer** — PostgreSQL for orders/products, Redis for sessions, ChromaDB for knowledge
- **Tool Integration** — Order management, product lookup, inventory checks
- **Cost Optimization** — ~50% cost savings through smart model selection
- **Graceful Fallback** — Automatic recovery when primary models fail

## 🚀 Quick Start (3 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env

# 3. Start infrastructure
docker compose up -d

# 4. Build knowledge base
python scripts/setup_rag.py

# 5. Run the agent
python demo.py
```

**Try these queries:**
- "Where is my order ORD-001?" (fast route)
- "What are the specs of the Dell XPS 15?" (RAG retrieval)
- "I have a complaint about my order" (deep route)

## 📚 What You Get

### Day 01-04: Foundation
- ✅ Tool calling with session state
- ✅ PostgreSQL-backed orders and products
- ✅ Redis session persistence
- ✅ Conversation history storage

### Day 05-06: RAG Knowledge Base
- ✅ PDF document processing with intelligent chunking
- ✅ ChromaDB vector store with metadata
- ✅ Grounded answering with hallucination guards
- ✅ Source citations (file, page, section)

### Day 07: LLM Gateway
- ✅ LiteLLM proxy with model groups
- ✅ Intelligent routing (fast-faq vs deep-support)
- ✅ Automatic fallback on failures
- ✅ Cost optimization through model selection

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    eComBot v4 Agent                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Routing      │  │ RAG          │  │ Tools        │      │
│  │ Intelligence │  │ Knowledge    │  │ (Orders,     │      │
│  │              │  │ Retrieval    │  │  Products)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
           ↓                  ↓                  ↓
    ┌─────────────┐    ┌──────────┐      ┌──────────┐
    │ LiteLLM     │    │ ChromaDB │      │PostgreSQL│
    │ Proxy       │    │ Vector   │      │ Orders & │
    │ (Routing)   │    │ Store    │      │ Products │
    └─────────────┘    └──────────┘      └──────────┘
           ↓
    ┌─────────────────────────┐          ┌──────────┐
    │ Model Groups            │          │  Redis   │
    │ • fast-faq (free)       │          │ Sessions │
    │ • deep-support (paid)   │          └──────────┘
    └─────────────────────────┘
```

### Components

**LLM Gateway (Day 07)**
- Routes simple queries → `fast-faq` (gemini-2.0-flash-exp, free)
- Routes complex queries → `deep-support` (gemini-2.5-flash, paid)
- Automatic fallback when primary models fail
- ~50% cost savings on mixed workloads

**RAG Knowledge Base (Day 05-06)**
- PDF processing with section-aware chunking
- ChromaDB with sentence-transformer embeddings (local, no API)
- Rich metadata (source file, page, section)
- Grounded answering with hallucination prevention

**Data Persistence (Day 04)**
- PostgreSQL: Orders, products, conversation history
- Redis: Session state with 1-hour TTL
- Environment-based configuration

**Tools (Day 03-04)**
- `get_order_status`, `cancel_order`
- `lookup_product`, `check_stock`
- `search_knowledge_base` (RAG retrieval)

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- OpenRouter API key ([get one free](https://openrouter.ai))

### Step-by-Step Setup

**1. Clone and Install**
```bash
git clone <your-repo-url>
cd ecombot
pip install -r requirements.txt
```

**2. Configure Environment**
```bash
cp .env.example .env
```

Edit `.env` and add:
```bash
OPENROUTER_API_KEY=your-key-here
USE_LITELLM_PROXY=true              # Enable intelligent routing
LITELLM_PROXY_URL=http://localhost:4000
```

**3. Start Infrastructure**
```bash
# Start PostgreSQL and Redis
docker compose up -d

# Verify services
docker compose ps
```

**4. Build Knowledge Base**
```bash
# Generate PDFs, index into ChromaDB, run tests
python scripts/setup_rag.py
```

This will:
- ✅ Generate sample PDF documents (FAQ + product catalog)
- ✅ Extract and chunk content with metadata
- ✅ Index 54 chunks into ChromaDB
- ✅ Run 9 validation tests

**5. Optional: Start LiteLLM Proxy**
```bash
# Terminal 1: Start proxy for intelligent routing
python scripts/start_litellm_proxy.py

# Terminal 2: Run tests
export USE_LITELLM_PROXY=true
python tests/test_litellm_routing.py
```

### Verify Setup

```bash
# Check database
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT * FROM orders;"

# Check Redis
docker compose exec redis redis-cli -a ecombot_redis_pass ping

# Check knowledge base
python tests/test_pdf_rag.py

# Check routing (if proxy enabled)
python tests/test_litellm_routing.py
```

## 🎮 Usage

### Interactive Demo

```bash
# Standard mode (direct LLM calls)
python demo.py

# With LiteLLM proxy (intelligent routing)
export USE_LITELLM_PROXY=true
python demo.py
```

**Try these queries:**

| Query | What Happens |
|-------|--------------|
| "Where is my order ORD-001?" | ⚡ Fast route → Order lookup → Response in ~1s |
| "What are the specs of Dell XPS 15?" | 📚 RAG retrieval → Grounded answer with source |
| "I have a complaint about my order" | 🧠 Deep route → More capable model |
| "What is your return policy?" | 📚 RAG retrieval from FAQ PDF |
| "Which laptop is best for video editing?" | 🧠 Deep route + RAG context |

### Routing Modes

**Without Proxy (Direct Mode)**
```bash
export USE_LITELLM_PROXY=false
python demo.py
```
All queries use `gemini-2.5-flash` directly.

**With Proxy (Smart Routing)**
```bash
export USE_LITELLM_PROXY=true
python demo.py
```
- Simple queries → `fast-faq` (free models)
- Complex queries → `deep-support` (premium models)
- Automatic fallback on failures

### ADK Web Interface

```bash
adk web
```

- Visual tool-call panel shows PostgreSQL queries
- State panel displays Redis session data
- Message history with RAG retrieval logs

### Automated Testing

```bash
# Test RAG retrieval quality
python tests/test_pdf_rag.py

# Test LiteLLM routing
python tests/test_litellm_routing.py

# Run basic scenario
python demo.py --scenario basic

# Run tools validation
python demo.py --scenario tools
```

## 🔬 Features Deep Dive

### RAG Knowledge Base (Day 05-06)

**What It Does:**
- Answers questions from PDF documents (FAQ + product catalog)
- Prevents hallucination by requiring grounded evidence
- Returns source citations (file, page, section)

**How It Works:**
1. PDFs chunked into ~1000-char sections with 200-char overlap
2. Chunks indexed into ChromaDB with sentence-transformers (local embeddings)
3. Agent retrieves top-3 relevant chunks for each query
4. Answer generated ONLY from retrieved context
5. Falls back gracefully when answer not in knowledge base

**Sample PDFs:**
- `data/ecom_faq.pdf` — 15 FAQ entries (shipping, returns, warranty, payment)
- `data/product_catalog.pdf` — 3 products with full specs (Dell XPS 15, Sony WH-1000XM5, Samsung S24)

**Commands:**
```bash
# Generate PDFs
python scripts/generate_sample_pdfs.py

# Index into ChromaDB
python -m src.rag.embed_catalog

# Test retrieval quality (9 tests)
python tests/test_pdf_rag.py

# Full setup
python scripts/setup_rag.py
```

**Test Results:**
- ✓ Direct match: "What is your return policy?" → 0.637 confidence
- ✓ Partial match: "How long to return something?" → 0.546 confidence
- ✓ Out-of-scope: "What is the weather?" → 0.148 confidence (correctly low)

---

### LLM Gateway (Day 07)

**What It Does:**
- Routes queries to optimal models based on complexity
- Saves ~50% cost by using free models for simple queries
- Automatically falls back when primary models fail

**Model Groups:**

| Group | Use Case | Primary | Fallback | Cost |
|-------|----------|---------|----------|------|
| fast-faq | Order status, simple FAQs | gemini-2.0-flash-exp | llama-3.1-8b | Free |
| deep-support | Complaints, recommendations | gemini-2.5-flash | claude-3.5-haiku | Paid |

**Routing Logic:**
```python
# Fast route keywords
"order status", "track", "price", "in stock", "shipping"

# Deep route keywords
"complaint", "refund", "compare", "recommend", "which", "best"
```

**Commands:**
```bash
# Start proxy
python scripts/start_litellm_proxy.py

# Test routing
python tests/test_litellm_routing.py

# Demo routing decisions
python scripts/demo_routing.py
```

**Fallback Behavior:**
1. Primary model fails → Retry 2x with 3s delay
2. Still failing → Switch to fallback in same group
3. Entire group down → Route to alternate group

---

### Data Persistence (Day 04)

**PostgreSQL:**
- Orders table (5 sample orders)
- Products table (6 electronics products)
- Conversation history (all interactions logged)

**Redis:**
- Session state (customer name, last order/product)
- 1-hour TTL (configurable)
- Password-protected, persistent storage

**Commands:**
```bash
# View database
docker compose exec postgres psql -U ecombot_user -d ecombot

# Query orders
docker compose exec postgres psql -U ecombot_user -d ecombot -c \
  "SELECT * FROM orders;"

# View history
python scripts/view_history.py <session_id>
```

## 🧪 Testing

### RAG Retrieval Tests

```bash
python tests/test_pdf_rag.py
```

**Tests 3 scenarios:**
1. **Direct match** — Questions clearly in knowledge base
2. **Partial match** — Similar wording, should still retrieve
3. **Out-of-scope** — Questions not in KB, should refuse

**Expected:** 8/9 PASS (one warning acceptable)

---

### LLM Routing Tests

```bash
export USE_LITELLM_PROXY=false  # Test without proxy
python tests/test_litellm_routing.py

export USE_LITELLM_PROXY=true   # Test with proxy
python tests/test_litellm_routing.py
```

**Tests 4 categories:**
1. Routing hint classification (9 queries)
2. Model selection (7 route hints)
3. Agent build with routing (3 routes)
4. Proxy connectivity (1 health check)

**Expected:** 12/12 PASS when proxy running

---

### Manual Validation

```bash
# Day 04 scenario (PostgreSQL + Redis)
python demo.py --scenario tools

# RAG grounding
python demo.py
# Try: "What are the specs of the Dell XPS 15?"

# Routing demonstration
python scripts/demo_routing.py
```

---

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not set"
```bash
# Add to .env file
echo "OPENROUTER_API_KEY=your-key-here" >> .env
```

### "Could not connect to proxy"
```bash
# Make sure proxy is running
python scripts/start_litellm_proxy.py

# Or disable proxy
export USE_LITELLM_PROXY=false
```

### "Collection ecombot_kb does not exist"
```bash
# Build knowledge base
python scripts/setup_rag.py
```

### "apscheduler not found"
```bash
# Install proxy dependencies
pip install 'litellm[proxy]' apscheduler
```

### Docker services not starting
```bash
# Check logs
docker compose logs postgres
docker compose logs redis

# Restart
docker compose down -v
docker compose up -d
```

### Numpy/ChromaDB compatibility error
```bash
# Reinstall correct versions
pip uninstall -y numpy
pip install "numpy<2.0"
pip install chromadb==0.4.22
```

---

## 📂 Project Structure

```
ecombot/
├── src/
│   ├── agents/
│   │   ├── support_agent.py              # Main agent (v1-v4 instructions)
│   │   └── support_instructions_v4_grounded.txt  # Current default
│   ├── tools/
│   │   ├── order_tools.py                # PostgreSQL order management
│   │   ├── product_tools.py              # PostgreSQL product catalog
│   │   └── rag_tool.py                   # ChromaDB knowledge retrieval
│   ├── rag/
│   │   ├── pdf_processor.py              # PDF extraction + chunking
│   │   ├── embed_catalog.py              # ChromaDB indexing
│   │   └── retriever.py                  # Vector search
│   ├── services/
│   │   ├── db.py                         # PostgreSQL pool
│   │   ├── session_service.py            # Redis sessions
│   │   └── history_service.py            # Conversation history
│   ├── config/
│   │   └── settings.py                   # Environment config + routing
│   └── session.py                        # Session factory
├── config/
│   └── litellm_config.yaml               # Proxy + model groups
├── data/
│   ├── products.json                     # Product seed data
│   ├── faq.json                          # FAQ seed data
│   ├── ecom_faq.pdf                      # Generated FAQ PDF
│   └── product_catalog.pdf               # Generated product catalog
├── scripts/
│   ├── init_db.sql                       # Database schema
│   ├── setup_rag.py                      # One-command RAG setup
│   ├── generate_sample_pdfs.py           # Create sample PDFs
│   ├── start_litellm_proxy.py            # Start proxy server
│   ├── demo_routing.py                   # Routing demonstration
│   └── view_history.py                   # View conversation logs
├── tests/
│   ├── test_pdf_rag.py                   # RAG validation (9 tests)
│   └── test_litellm_routing.py           # Routing validation (12 tests)
├── docs/                                 # Implementation guides
├── demo.py                               # Interactive + scenarios
├── docker-compose.yml                    # PostgreSQL + Redis
├── requirements.txt
├── .env
└── README.md
```

---

## 💰 Cost Optimization

**Without Routing** (all queries → gemini-2.5-flash):
- 1000 queries/day = ~$X cost

**With Routing** (50% fast, 50% deep):
- 500 fast queries → Free models = $0
- 500 deep queries → Premium = $Y
- **Savings: ~50%**

**Tips:**
1. Use proxy for production workloads
2. Monitor routing accuracy with tests
3. Tune routing keywords for your queries
4. Use free models in development/testing

---

## 🔧 Configuration

### Environment Variables

```bash
# LLM
OPENROUTER_API_KEY=your-key-here

# LiteLLM Proxy (Day 07)
USE_LITELLM_PROXY=true
LITELLM_PROXY_URL=http://localhost:4000

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ecombot
POSTGRES_USER=ecombot_user
POSTGRES_PASSWORD=ecombot_pg_pass

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=ecombot_redis_pass
REDIS_DB=0

# Session
SESSION_TTL=3600  # 1 hour
```

### Switching Modes

**Direct Mode (no proxy):**
```bash
export USE_LITELLM_PROXY=false
```

**Proxy Mode (intelligent routing):**
```bash
export USE_LITELLM_PROXY=true
```

**RAG Only (no proxy, no tools):**
```bash
# Edit src/agents/support_agent.py
# Comment out order/product tools, keep search_knowledge_base
```

---

## 📊 Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Simple query (fast route) | ~1.2s | Free model, cached embeddings |
| Complex query (deep route) | ~2.5s | Premium model, fresh retrieval |
| RAG retrieval | ~300ms | Local ChromaDB, 3 chunks |
| Order lookup (PostgreSQL) | ~50ms | Connection pool |
| Session read (Redis) | ~10ms | In-memory cache |

---

## 🚢 Deployment Considerations

### For Production:

**LiteLLM Proxy:**
- Use managed service or self-host with authentication
- Set up monitoring (Datadog, New Relic)
- Configure rate limits per user
- Add budget tracking and alerts

**Database:**
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Set up read replicas for scaling
- Regular backups with point-in-time recovery
- Index optimization for query performance

**Redis:**
- Use managed Redis (AWS ElastiCache, Redis Cloud)
- Set up persistence (AOF or RDB)
- Configure eviction policy
- Monitor memory usage

**ChromaDB:**
- Consider managed vector database (Pinecone, Weaviate)
- Set up backup/restore procedures
- Monitor index size and query latency
- Plan for incremental updates

---

## 📖 Additional Resources

**Documentation:**
- Full implementation guides in `docs/`
- Test documentation in `tests/`
- Lab history in `docs/lab-history/`

**Key Files:**
- [config/litellm_config.yaml](config/litellm_config.yaml) — Model groups & fallback
- [src/config/settings.py](src/config/settings.py) — Routing & configuration
- [src/agents/support_agent.py](src/agents/support_agent.py) — Main agent
- [scripts/setup_rag.py](scripts/setup_rag.py) — One-command setup

**External Links:**
- [Google ADK](https://cloud.google.com/vertex-ai/docs/adk)
- [LiteLLM](https://docs.litellm.ai/)
- [OpenRouter](https://openrouter.ai/)
- [ChromaDB](https://docs.trychroma.com/)

---

## ✅ Completion Checklist

### Day 01-04: Foundation
- [x] LlmAgent with instruction variants
- [x] Tool calling with session state
- [x] PostgreSQL orders and products
- [x] Redis session persistence
- [x] Conversation history storage

### Day 05-06: RAG
- [x] PDF processing with chunking
- [x] ChromaDB vector store
- [x] Grounded answering
- [x] Hallucination prevention
- [x] Source citations

### Day 07: LLM Gateway
- [x] LiteLLM proxy configuration
- [x] Intelligent routing (fast/deep)
- [x] Automatic fallback
- [x] Cost optimization
- [x] Comprehensive testing

---

## 🎓 Learning Outcomes

By building this project, you've learned:

1. **Production AI Patterns** — Not just prompts, but real architecture
2. **RAG Implementation** — From PDFs to grounded answers
3. **LLM Gateway** — Cost-effective model routing
4. **Data Persistence** — PostgreSQL, Redis, ChromaDB integration
5. **Error Handling** — Graceful degradation and fallbacks
6. **Testing Strategy** — Automated validation for AI systems
7. **Configuration Management** — Environment-based, production-ready

---

## 📝 License

[Your License Here]

---

## 🙏 Acknowledgments

Built with:
- [Google ADK](https://cloud.google.com/vertex-ai/docs/adk)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [ChromaDB](https://github.com/chroma-core/chroma)
- [OpenRouter](https://openrouter.ai/)

---

**Questions? Issues?** Open an issue or check the troubleshooting section above.
