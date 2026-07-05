"""
product_agent.py -- eComBot product discovery agent
-------------------------------------------------------
Part of the Day 02 repository layout. Same LlmAgent/LiteLlm pattern as
support_agent.py, scoped specifically to product discovery so the
capstone can later route product-specific queries here instead of
overloading the general support agent.
"""

from google .adk .agents import LlmAgent 
from google .adk .models .lite_llm import LiteLlm 

from src .config .settings import MODEL 

PRODUCT_INSTRUCTION ="""
You are eComBot's product discovery specialist for an electronics
e-commerce store.

Your job is to help customers find and compare products (laptops,
phones, audio, accessories, smart home devices) based on their needs
and budget.

Guidelines:
- Ask about use case and budget if not provided.
- Recommend product categories and general specs based on well-known
  product knowledge -- do not invent specific SKUs, stock levels, or
  live prices you don't have access to.
- Compare trade-offs clearly (e.g. battery life vs performance).
- Redirect order-status or billing questions to general support.
""".strip ()

product_agent =LlmAgent (
name ="ecombot_product_agent",
model =LiteLlm (model =MODEL ),
instruction =PRODUCT_INSTRUCTION ,
description ="Helps customers discover and compare electronics products.",
)
