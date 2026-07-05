"""
support_agent.py -- eComBot support agent (Day 01 -> Day 02 -> Day 03 -> Day 04)
---------------------------------------------------------------------------------
Follows the same LlmAgent + LiteLlm + OpenRouter pattern used in
hello_agent.py / agent.py from the Day 01 and Day 03 demos, but scoped
to the eComBot electronics e-commerce capstone.

Day 01: a single working instruction (v1) -- "get it running".
Day 02: multiple instruction files (v1/v2/v3) swapped into the SAME
        agent code, so tone/behavior can be compared without touching
        agent logic. See tests/test_prompt_variants.md for results.
Day 03: real tool calling + in-memory session state, mirroring the
        Day 03 travel demo's agent.py (tools=[...] registered on the
        LlmAgent, plain callables with ToolContext for state writes).
        A shared TOOL_USAGE_ADDENDUM is appended to whichever tone
        variant (v1/v2/v3) is loaded, so tool-calling behavior stays
        consistent across all instruction experiments.
Day 04: PostgreSQL-backed tools (orders, products) + Redis session
        persistence + conversation history storage.

Discovery for ADK Web:
    `root_agent` at module level is what `adk web` looks for.
    By default this loads v2 (the current best-performing instruction,
    see tests/test_prompt_variants.md). Override with ECOMBOT_INSTRUCTION_VERSION.

Run directly:
    python -m src.agents.support_agent
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))  # repo root on path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from src.config.settings import MODEL, require_api_key
from src.session import make_runner
from src.tools.order_tools import cancel_order, get_customer_context, get_order_status, save_customer_name
from src.tools.product_tools import check_stock, get_product_by_id, lookup_product

_AGENT_DIR = Path(__file__).resolve().parent

INSTRUCTION_FILES = {
    "v1": _AGENT_DIR / "support_instructions_v1.txt",
    "v2": _AGENT_DIR / "support_instructions_v2.txt",
    "v3": _AGENT_DIR / "support_instructions_v3.txt",
}


# Appended to every tone variant so tool-calling behavior stays
# consistent regardless of which persona (v1/v2/v3) is loaded.
# Updated for Day 04 with PostgreSQL-backed tools.
TOOL_USAGE_ADDENDUM = """
Tool usage:
- When a customer asks about their order, use the get_order_status tool.
  Ask for the order ID if it is missing. Do not guess order details --
  use the tool output directly in your response.
- Use cancel_order when a customer requests to cancel an order. Check
  the order status first and explain if cancellation is not possible.
- Use lookup_product to search for products by name (partial match works).
  Use get_product_by_id for exact product ID lookups.
  Use check_stock to verify current availability.
- Call save_customer_name as soon as the customer introduces themselves
  by name, then use their name naturally in later replies without
  asking for it again.
- Call get_customer_context if you need to recall what's already known
  about the customer in this session (their name, their last order).
- Never invent product details, prices, or order information. Always use
  the tools to retrieve real data from the database.
""".strip()

TOOLS = [
    get_order_status,
    cancel_order,
    save_customer_name,
    get_customer_context,
    lookup_product,
    get_product_by_id,
    check_stock,
]


def load_instruction(version: str = "v2") -> str:
    """Load one of the instruction variants from disk, with the tool-usage addendum appended."""
    path = INSTRUCTION_FILES.get(version)
    if path is None or not path.exists():
        raise FileNotFoundError(f"No instruction file found for version '{version}'")
    base = path.read_text(encoding="utf-8").strip()
    return f"{base}\n\n{TOOL_USAGE_ADDENDUM}"


def build_support_agent(version: str = "v2") -> LlmAgent:
    """Build the eComBot support agent using the chosen instruction version + tools."""
    instruction = load_instruction(version)
    return LlmAgent(
        name="ecombot_support_agent",
        model=LiteLlm(model=MODEL),
        instruction=instruction,
        description=(
            "eComBot support agent for an electronics e-commerce store -- "
            "handles order status, cancellations, product discovery, and "
            "general support with PostgreSQL-backed tools and Redis session "
            "persistence, remembering customer context across turns."
        ),
        tools=TOOLS,
    )


# ── ADK Web discovery point ─────────────────────────────────────────────────
# `adk web` looks for a module-level `root_agent`.
_default_version = os.environ.get("ECOMBOT_INSTRUCTION_VERSION", "v2")
root_agent = build_support_agent(_default_version)


# ── Standalone runner (mirrors hello_agent.py / Day 03 demo.py) ─────────────

async def _demo() -> None:
    require_api_key()

    runner, user_id, session_id = await make_runner(root_agent)

    questions = [
        "Hi, my name is Priya.",
        "Where is my order ORD-001?",
        "What about ORD-002?",
        "Can you track ZZ-999?",
    ]

    for question in questions:
        print(f"\nUser : {question}")
        message = types.Content(role="user", parts=[types.Part(text=question)])
        reply = ""
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    reply = event.content.parts[0].text or ""
        print(f"Agent: {reply.strip()}")


if __name__ == "__main__":
    asyncio.run(_demo())
