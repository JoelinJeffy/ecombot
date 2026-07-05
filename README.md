# eComBot — Google ADK Support Agent

Electronics e-commerce support agent built with Google ADK, LiteLLM, OpenRouter,
PostgreSQL, and Redis.

## Origin / how this was built


- **Day 01**: First working `LlmAgent`, `Runner`, `InMemorySessionService`
- **Day 02**: Instruction refinement and prompt variant testing
- **Day 03**: Tool calling with `ToolContext` for session state
- **Day 04**: PostgreSQL-backed tools + Redis session persistence + conversation history

`ecombot/` applies the ADK pattern to electronics e-commerce support with
production-ready data persistence and session continuity.

## Repository structure

```text
ecombot/
├── src/
│   ├── agents/
│   │   ├── support_agent.py           # eComBot agent (root_agent for ADK Web)
│   │   ├── support_instructions_v1.txt
│   │   ├── support_instructions_v2.txt  # current default
│   │   ├── support_instructions_v3.txt
│   │   ├── product_agent.py
│   │   └── sales_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── order_tools.py             # get_order_status, cancel_order (PostgreSQL)
│   │   └── product_tools.py           # lookup_product, check_stock (PostgreSQL)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── db.py                      # PostgreSQL connection pool
│   │   ├── session_service.py         # Redis-backed sessions
│   │   └── history_service.py         # PostgreSQL conversation history
│   ├── config/
│   │   └── settings.py                # Environment-based configuration
│   ├── session.py                     # Session service factory
│   ├── common.py
│   └── __init__.py
├── scripts/
│   ├── init_db.sql                    # Database schema and seed data
│   └── view_history.py                # View conversation history
├── tests/
│   ├── test_support_agent_manual.md
│   └── test_prompt_variants.md
├── docs/
│   └── lab-history/                   # Day 01-03 lab files
├── demo.py                            # Unified interactive + scenario runner
├── docker-compose.yml                 # Redis + PostgreSQL
├── .env / .env.example
├── requirements.txt
└── README.md
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

### 3. Start infrastructure

```bash
docker compose up -d
```

This starts:
- PostgreSQL on port 5432 (auto-creates tables and seed data)
- Redis on port 6379 (password-protected, persistent)

### 4. Verify setup

```bash
# Check services are running
docker compose ps

# Check PostgreSQL data
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT * FROM orders;"
```

## Running

### Interactive mode

```bash
# Interactive chat (type freely, q to quit)
python demo.py

# Use different instruction version
python demo.py --version v3
```

### Automated scenarios

```bash
# Run basic scenario (Day 01 checks)
python demo.py --scenario basic

# Run tools validation (Day 04 checks)
python demo.py --scenario tools
```

### ADK Web

```bash
adk web
```

ADK Web discovers `root_agent` in `src/agents/support_agent.py`. Use the
tool-call panel to see PostgreSQL queries and the state panel to view
Redis-backed session state.

## What this agent does

### Day 04 Features

- **Order management** (PostgreSQL-backed):
  - `get_order_status(order_id)` - Real-time order tracking
  - `cancel_order(order_id)` - Order cancellation with validation
  
- **Product catalog** (PostgreSQL-backed):
  - `lookup_product(product_name)` - Search products by name
  - `get_product_by_id(product_id)` - Exact product lookup
  - `check_stock(product_id)` - Inventory availability

- **Session persistence** (Redis):
  - Customer name stored across restarts
  - Last order/product context preserved
  - 1-hour session TTL (configurable)

- **Conversation history** (PostgreSQL):
  - Durable audit trail of all interactions
  - Tool call logging for analytics
  - Queryable by session or user

### General capabilities

- Product discovery (laptops, phones, audio, accessories)
- Greetings, empathy, and clarifying questions
- Politely redirects out-of-scope requests
- No invented data - all information from database

## Testing

### Manual validation

```bash
# Run Day 04 scenario validation
python demo.py --scenario tools
```

Expected flow:
1. Customer introduces themselves → Name stored in Redis
2. Order lookup → PostgreSQL query + session state update
3. Product search → PostgreSQL query + results
4. Follow-up questions → Session state reused

### View conversation history

```bash
python scripts/view_history.py <session_id>
```

### Database inspection

```bash
# View all orders
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT * FROM orders;"

# View products
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT * FROM products;"

# View conversation history
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT * FROM session_history ORDER BY created_at DESC LIMIT 10;"
```

## Architecture

### Data boundaries

- **Redis** - Short-lived working memory (customer context, last actions)
- **PostgreSQL** - Durable business data (orders, products, history)
- **Session state** - Not used for permanent storage
- **History** - Separate from transient session data

### Error handling

- Invalid inputs return structured error dicts
- Database failures return safe user messages
- Graceful fallback to in-memory sessions if Redis unavailable
- No stack traces leaked to users

## Development

### Environment variables

See [.env.example](.env.example) for all configuration options.

### Switching session backends

Edit `src/session.py` and set `USE_REDIS = False` to use in-memory sessions.

### Database migrations

Schema is in [scripts/init_db.sql](scripts/init_db.sql). For changes:

```bash
docker compose down -v  # Warning: deletes data
docker compose up -d    # Recreates with new schema
```

## Verification checklist (Day 04)

- [x] docker-compose.yml with Redis and PostgreSQL
- [x] Database schema with orders, products, session_history
- [x] Environment-based configuration (no hardcoded secrets)
- [x] PostgreSQL connection pool
- [x] Redis session persistence
- [x] Conversation history storage
- [x] PostgreSQL-backed order tools
- [x] PostgreSQL-backed product tools
- [x] Error handling for all failure modes
- [x] Session state survives across restarts
- [x] Manual test documentation

## Next steps

Day 05 will add:
- Retrieval and grounding
- Enhanced production behavior
- Observability and evaluation
- Multi-agent routing preparation

## Next steps

Day 05 will add:
- Retrieval and grounding
- Enhanced production behavior
- Observability and evaluation
- Multi-agent routing preparation
