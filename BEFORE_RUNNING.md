# Day 04 - Before Running Checklist

## 🐳 Docker Setup Required

**IMPORTANT**: Before running the agent, you need to:

1. **Unpause Docker Desktop**
   - Click the Docker whale icon in your menu bar
   - Click "Unpause" or "Resume"
   - Wait for Docker to start (~30 seconds)

2. **Start the services**
   ```bash
   cd "/Users/jacobjosej/Downloads/ecombot 12"
   docker compose up -d
   ```

3. **Wait for health checks** (~10 seconds)
   ```bash
   docker compose ps
   ```
   Both services should show "healthy"

4. **Verify database is ready**
   ```bash
   docker compose exec postgres psql -U ecombot_user -d ecombot -c "SELECT COUNT(*) FROM orders;"
   ```
   Should show: `count: 5`

## 🔧 If Services Won't Start

### Docker Desktop Issues
```bash
# Check Docker is running
docker version

# Restart Docker Desktop completely
# Use menu bar: Docker → Restart
```

### Port Conflicts
```bash
# Check if ports are in use
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill conflicting processes or change ports in docker-compose.yml
```

### Volume Issues
```bash
# Remove old volumes and start fresh
docker compose down -v
docker compose up -d
```

## 📦 Python Dependencies

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

If you get import errors:
```bash
pip install --upgrade psycopg2-binary redis google-adk
```

## ✅ Quick Validation

Once services are running:

```bash
# Test 1: Database connection
docker compose exec postgres psql -U ecombot_user -d ecombot -c "\dt"

# Test 2: Redis connection
docker compose exec redis redis-cli -a ecombot_redis_pass ping

# Test 3: Python can connect
python -c "from src.services.db import init_db_pool; init_db_pool(); print('DB OK')"
python -c "from src.services.session_service import get_redis_client; get_redis_client().ping(); print('Redis OK')"

# Test 4: Run the agent
python demo.py --scenario tools
```

## 🎯 Expected Output

After running `python demo.py --scenario tools`, you should see:

```
======================================================================
eComBot Support Agent -- version: v2 -- scenario: tools
======================================================================

USER
  Hi, my name is Priya.

AGENT
  [Response greeting Priya and storing name]

USER
  Where is my order ORD-001?

AGENT
  [Database query for ORD-001, returns: Shipped, BlueDart, ETA: 8 Jul 2026]

USER
  What about ORD-002?

AGENT
  [Uses stored name "Priya", queries ORD-002: Processing, DTDC]

USER
  Can you track ZZ-999?

AGENT
  [Handles invalid format gracefully]

======================================================================
  Checkpoint: name stored after Turn 1, order tool called on
  Turns 2-3, invalid format handled gracefully on Turn 4.
======================================================================
```

## 🐛 Common Issues

### "Import redis could not be resolved"
```bash
pip install redis
```

### "Import psycopg2 could not be resolved"
```bash
pip install psycopg2-binary
```

### "Redis connection failed"
- Check Docker is running: `docker compose ps`
- If Redis shows unhealthy, restart: `docker compose restart redis`
- Agent will fall back to in-memory sessions automatically

### "Database error"
- Check PostgreSQL logs: `docker compose logs postgres`
- Verify tables exist: `docker compose exec postgres psql -U ecombot_user -d ecombot -c "\dt"`
- Recreate database: `docker compose down -v && docker compose up -d`

### "No module named 'src'"
```bash
# Make sure you're in the project root
cd "/Users/jacobjosej/Downloads/ecombot 12"
python demo.py
```

## 📊 Service Health Check

```bash
# All-in-one health check
cd "/Users/jacobjosej/Downloads/ecombot 12"
docker compose ps
docker compose exec postgres pg_isready -U ecombot_user
docker compose exec redis redis-cli -a ecombot_redis_pass ping
echo "All services OK ✅"
```

## 🎓 What to Test

### Basic Flow
1. Start with greeting → Name stored in Redis
2. Ask about order → PostgreSQL query executed
3. Ask follow-up → Session state reused
4. Try invalid input → Error handled gracefully

### Advanced Flow
1. Search for product (Dell, Sony)
2. Check stock availability
3. Try to cancel an order
4. Ask about the same order again

### Restart Test (Redis Persistence)
1. Run conversation, note session_id from logs
2. Stop agent (Ctrl+C)
3. Restart agent
4. Ask follow-up → Should remember context (if using same session_id)

## 📝 Ready to Run?

Checklist:
- [ ] Docker Desktop is running (not paused)
- [ ] `docker compose up -d` completed successfully
- [ ] Both services show "healthy" in `docker compose ps`
- [ ] Database has 5 orders (verified with psql)
- [ ] Python dependencies installed
- [ ] .env file has OPENROUTER_API_KEY

If all checked, run:
```bash
python demo.py --scenario tools
```

Enjoy testing your production-ready eComBot with PostgreSQL and Redis! 🚀
