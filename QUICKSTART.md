# eComBot Day 04 Quick Start Guide

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- OpenRouter API key

## Quick Start

### 1. Clone and setup

```bash
cd "ecombot 12"
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_key_here
```

### 3. Start services

```bash
docker compose up -d
```

Wait for services to be ready (~10 seconds):
```bash
docker compose ps
```

Both services should show "Up" and "healthy".

### 4. Verify database

```bash
docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT order_id, status FROM orders;"
```

You should see 5 sample orders.

### 5. Test the agent

#### Interactive mode
```bash
python demo.py
```

Try these prompts:
- `Hi, my name is Priya.`
- `Where is my order ORD-001?`
- `Show me the Dell XPS laptop`
- `What about ORD-002?`
- `q` (to quit)

#### Automated scenario
```bash
python demo.py --scenario tools
```

This runs the Day 04 validation scenario automatically.

### 6. Use ADK Web (optional)

```bash
adk web
```

Open browser to http://localhost:8000 and interact with the agent visually.

## Troubleshooting

### Services won't start

```bash
# Check logs
docker compose logs

# Restart services
docker compose down
docker compose up -d
```

### Database connection errors

```bash
# Verify PostgreSQL is ready
docker compose exec postgres pg_isready -U ecombot_user

# Check if tables exist
docker compose exec postgres psql -U ecombot_user -d ecombot -c "\dt"
```

### Redis connection errors

```bash
# Verify Redis is ready
docker compose exec redis redis-cli -a ecombot_redis_pass ping
```

If Redis is unavailable, the agent automatically falls back to in-memory sessions.

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## Validation Checklist

After setup, verify:

- [ ] Docker services are running and healthy
- [ ] Database has orders and products tables
- [ ] Agent responds to greetings
- [ ] Order lookup tool works (ORD-001, ORD-002, ORD-003)
- [ ] Product search tool works (Dell XPS, Sony, Samsung)
- [ ] Session state persists (name remembered)
- [ ] Invalid inputs handled gracefully
- [ ] Cancel order works with validation

## What's New in Day 04

1. **PostgreSQL integration**
   - Real order data (5 sample orders)
   - Real product catalog (6 sample products)
   - Conversation history storage

2. **Redis session persistence**
   - Sessions survive process restart
   - 1-hour TTL (configurable)
   - Falls back to in-memory if unavailable

3. **New tools**
   - `cancel_order(order_id)` - Order cancellation
   - `lookup_product(product_name)` - Product search
   - `check_stock(product_id)` - Inventory check

4. **Production-ready error handling**
   - Database failures return safe messages
   - No stack traces leaked to users
   - Validation before all operations

## Next Steps

- Run full validation: `python demo.py --scenario tools`
- View conversation history: `python scripts/view_history.py <session_id>`
- Explore ADK Web for tool debugging
- Check manual test documentation in `tests/`

## Cleanup

```bash
# Stop services (preserves data)
docker compose stop

# Stop and remove (deletes data)
docker compose down -v
```
