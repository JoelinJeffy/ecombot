"""
settings.py -- Central configuration for eComBot
--------------------------------------------------
Mirrors the config pattern used in common.py from the Day 01 demo,
but scoped as a proper package module for the eComBot capstone project.

Day 04: Added Redis and PostgreSQL configuration.
"""

import logging
import os

from dotenv import load_dotenv

# ── Silence noisy loggers (same approach as common.py) ─────────────────────
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

os.environ.setdefault("LITELLM_LOG", "ERROR")
for _name in ("LiteLLM", "LiteLLM Router", "LiteLLM Proxy"):
    _log = logging.getLogger(_name)
    _log.setLevel(logging.CRITICAL)
    _log.propagate = False

load_dotenv()  # reads OPENROUTER_API_KEY and other config from .env

import litellm  # noqa: E402

litellm.suppress_debug_info = True

# ── Project-wide constants ──────────────────────────────────────────────────
MODEL = "openrouter/google/gemini-2.5-flash"
APP_NAME = "ecombot"

# Domain the agent is scoped to (used by tests / verification steps)
DOMAIN = "electronics e-commerce"

# ── Redis Configuration ─────────────────────────────────────────────────────
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "ecombot_redis_pass")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ── PostgreSQL Configuration ────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecombot")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecombot_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ecombot_pg_pass")

# ── Session Configuration ───────────────────────────────────────────────────
SESSION_TTL = int(os.getenv("SESSION_TTL", "3600"))  # 1 hour default


def require_api_key() -> None:
    """Fail fast with a clear message if the key is missing (Day 01 checkpoint)."""
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise RuntimeError(
            "\n[ERROR] OPENROUTER_API_KEY is not set.\n"
            "Create a .env file in this directory with:\n"
            "  OPENROUTER_API_KEY=your-key-here\n"
        )


def get_redis_url() -> str:
    """Build Redis connection URL with password."""
    return f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


def get_postgres_dsn() -> str:
    """Build PostgreSQL connection DSN."""
    return (
        f"host={POSTGRES_HOST} "
        f"port={POSTGRES_PORT} "
        f"dbname={POSTGRES_DB} "
        f"user={POSTGRES_USER} "
        f"password={POSTGRES_PASSWORD}"
    )

