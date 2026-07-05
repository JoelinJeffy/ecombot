"""
order_tools.py -- eComBot order tools (Day 04)
--------------------------------------------------
PostgreSQL-backed order tools with proper error handling.
Uses connection pool from src.services.db for database access.

Tool context usage:
  get_order_status -- writes the queried order_id to session state
                       under 'last_order_id'.
  cancel_order -- updates order status in database and session state.

Passed directly to LlmAgent(tools=[...]) in support_agent.py.
"""

import logging 
import re 
from typing import Any 

from google .adk .tools import ToolContext 

from src .services .db import execute_query 

logger =logging .getLogger (__name__ )

_ORDER_ID_PATTERN =re .compile (r"^ORD-\d{3}$")




def get_order_status (
order_id :str ,
tool_context :ToolContext ,
)->dict [str ,Any ]:
    """
    Return the current status of a customer's order from PostgreSQL.
    Writes the queried order ID to session state under 'last_order_id'.

    Args:
        order_id: The order identifier, e.g. "ORD-001".

    Returns:
        A dict with order_id, status, eta, carrier, and total_amount,
        or an error dict if the ID is malformed or the order does not exist.
    """
    key =order_id .strip ().upper ()

    if not _ORDER_ID_PATTERN .match (key ):
        return {"error":"Invalid order ID format. Expected format: ORD-XXX"}

    tool_context .state ["last_order_id"]=key 

    try :
        query ="""
            SELECT order_id, customer_name, status, eta, carrier, total_amount
            FROM orders
            WHERE order_id = %s
        """
        row =execute_query (query ,(key ,),fetch ="one")

        if row is None :
            return {"error":f"Order {key } not found."}

        return {
        "order_id":row [0 ],
        "customer_name":row [1 ],
        "status":row [2 ],
        "eta":row [3 ],
        "carrier":row [4 ],
        "total_amount":float (row [5 ])if row [5 ]else None 
        }
    except Exception as e :
        logger .error (f"Database error in get_order_status: {e }")
        return {"error":"Unable to retrieve order information. Please try again."}


def cancel_order (
order_id :str ,
tool_context :ToolContext ,
)->dict [str ,Any ]:
    """
    Cancel a customer's order in the database.
    Updates order status to 'Cancelled' and clears shipping details.

    Args:
        order_id: The order identifier to cancel, e.g. "ORD-001".

    Returns:
        A dict with success status and message, or an error dict.
    """
    key =order_id .strip ().upper ()

    if not _ORDER_ID_PATTERN .match (key ):
        return {"error":"Invalid order ID format. Expected format: ORD-XXX"}

    try :

        check_query ="SELECT status FROM orders WHERE order_id = %s"
        row =execute_query (check_query ,(key ,),fetch ="one")

        if row is None :
            return {"error":f"Order {key } not found."}

        current_status =row [0 ]

        if current_status =="Cancelled":
            return {"error":f"Order {key } is already cancelled."}

        if current_status =="Delivered":
            return {"error":f"Order {key } has already been delivered and cannot be cancelled."}


        cancel_query ="""
            UPDATE orders
            SET status = 'Cancelled', eta = NULL, carrier = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE order_id = %s
        """
        execute_query (cancel_query ,(key ,),fetch ="none")

        tool_context .state ["last_order_id"]=key 
        tool_context .state ["last_action"]="cancel_order"

        return {
        "success":True ,
        "order_id":key ,
        "message":f"Order {key } has been successfully cancelled."
        }
    except Exception as e :
        logger .error (f"Database error in cancel_order: {e }")
        return {"error":"Unable to cancel order. Please try again."}


def save_customer_name (
name :str ,
tool_context :ToolContext ,
)->dict [str ,Any ]:
    """
    Save the customer's name to session state.
    Call this as soon as the customer introduces themselves.

    Args:
        name: The customer's name, e.g. "Priya".

    Returns:
        A confirmation dict.
    """
    tool_context .state ["customer_name"]=name 
    return {"saved":True ,"customer_name":name }


def get_customer_context (tool_context :ToolContext )->dict [str ,Any ]:
    """
    Return what's currently known about the customer from session state.
    Reads customer_name and last_order_id.

    Returns:
        A dict with the known context for this session.
    """
    return {
    "customer_name":tool_context .state .get ("customer_name","unknown"),
    "last_order_id":tool_context .state .get ("last_order_id","none"),
    "last_action":tool_context .state .get ("last_action","none"),
    }

