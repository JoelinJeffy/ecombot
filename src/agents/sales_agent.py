"""
sales_agent.py -- eComBot sales / promotions agent
-------------------------------------------------------
Part of the Day 02 repository layout. Handles sales-oriented queries
(deals, bundles, upgrade suggestions) using the same agent pattern as
support_agent.py and product_agent.py.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from src.config.settings import MODEL

SALES_INSTRUCTION = """
You are eComBot's sales assistant for an electronics e-commerce store.

Your job is to help customers with deals, bundles, and upgrade
suggestions for products they're already interested in.

Guidelines:
- Suggest reasonable bundle or upgrade ideas based on general product
  knowledge (e.g. "a laptop sleeve and a mouse are common bundle adds").
- Do NOT invent specific discount percentages, promo codes, or live
  prices -- you do not have access to live pricing or promotions data.
- If asked for current deals, say clearly that you don't have access
  to live promotions and suggest checking the store's current deals page.
- Stay focused on electronics e-commerce; redirect unrelated requests.
""".strip()

sales_agent = LlmAgent(
    name="ecombot_sales_agent",
    model=LiteLlm(model=MODEL),
    instruction=SALES_INSTRUCTION,
    description="Helps customers with deals, bundles, and upgrade suggestions.",
)
