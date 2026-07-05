"""
product_tools.py -- eComBot product tools (Day 04)
---------------------------------------------------
PostgreSQL-backed product lookup tools.
Uses connection pool from src.services.db for database access.

Tool context usage:
  lookup_product -- writes the queried product_id to session state
                     under 'last_product_id'.

Passed directly to LlmAgent(tools=[...]) in support_agent.py.
"""

import logging
from typing import Any

from google.adk.tools import ToolContext

from src.services.db import execute_query

logger = logging.getLogger(__name__)


# ── Tool functions ──────────────────────────────────────────────────────────

def lookup_product(
    product_name: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Search for a product by name in PostgreSQL and return details.
    Writes the found product_id to session state under 'last_product_id'.

    Args:
        product_name: The product name to search for (case-insensitive partial match).

    Returns:
        A dict with product_id, product_name, description, price, stock_quantity,
        and category, or an error dict if the product is not found or inactive.
    """
    if not product_name or not product_name.strip():
        return {"error": "Product name is required."}

    search_term = f"%{product_name.strip()}%"

    try:
        query = """
            SELECT product_id, product_name, description, price, stock_quantity, category, is_active
            FROM products
            WHERE product_name ILIKE %s
            ORDER BY is_active DESC, product_name ASC
            LIMIT 1
        """
        row = execute_query(query, (search_term,), fetch="one")
        
        if row is None:
            return {"error": f"No product found matching '{product_name}'."}
        
        product_id, name, description, price, stock, category, is_active = row
        
        if not is_active:
            return {
                "error": f"Product '{name}' ({product_id}) is no longer available."
            }
        
        tool_context.state["last_product_id"] = product_id
        tool_context.state["last_product_name"] = name
        
        return {
            "product_id": product_id,
            "product_name": name,
            "description": description,
            "price": float(price),
            "stock_quantity": stock,
            "category": category,
            "in_stock": stock > 0
        }
    except Exception as e:
        logger.error(f"Database error in lookup_product: {e}")
        return {"error": "Unable to search for products. Please try again."}


def get_product_by_id(
    product_id: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Get product details by exact product ID.

    Args:
        product_id: The product identifier, e.g. "PRD-101".

    Returns:
        A dict with product details or an error dict.
    """
    key = product_id.strip().upper()

    try:
        query = """
            SELECT product_id, product_name, description, price, stock_quantity, category, is_active
            FROM products
            WHERE product_id = %s
        """
        row = execute_query(query, (key,), fetch="one")
        
        if row is None:
            return {"error": f"Product {key} not found."}
        
        product_id, name, description, price, stock, category, is_active = row
        
        if not is_active:
            return {
                "error": f"Product '{name}' ({product_id}) is no longer available."
            }
        
        tool_context.state["last_product_id"] = product_id
        tool_context.state["last_product_name"] = name
        
        return {
            "product_id": product_id,
            "product_name": name,
            "description": description,
            "price": float(price),
            "stock_quantity": stock,
            "category": category,
            "in_stock": stock > 0
        }
    except Exception as e:
        logger.error(f"Database error in get_product_by_id: {e}")
        return {"error": "Unable to retrieve product information. Please try again."}


def check_stock(
    product_id: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Check current stock availability for a product.

    Args:
        product_id: The product identifier, e.g. "PRD-101".

    Returns:
        A dict with stock information or an error dict.
    """
    key = product_id.strip().upper()

    try:
        query = """
            SELECT product_id, product_name, stock_quantity, is_active
            FROM products
            WHERE product_id = %s
        """
        row = execute_query(query, (key,), fetch="one")
        
        if row is None:
            return {"error": f"Product {key} not found."}
        
        product_id, name, stock, is_active = row
        
        if not is_active:
            return {"error": f"Product '{name}' is no longer available."}
        
        return {
            "product_id": product_id,
            "product_name": name,
            "stock_quantity": stock,
            "in_stock": stock > 0,
            "availability": "In Stock" if stock > 0 else "Out of Stock"
        }
    except Exception as e:
        logger.error(f"Database error in check_stock: {e}")
        return {"error": "Unable to check stock. Please try again."}
