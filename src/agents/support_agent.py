"""
support_agent.py -- eComBot support agent (Day 01 -> Day 02 -> Day 03 -> Day 04 -> Day 05)
-------------------------------------------------------------------------------------------
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
Day 05: RAG with ChromaDB for knowledge-grounded answers + hallucination guards.

Discovery for ADK Web:
    `root_agent` at module level is what `adk web` looks for.
    By default this loads v4 (grounded instruction with RAG).
    Override with ECOMBOT_INSTRUCTION_VERSION.

Run directly:
    python -m src.agents.support_agent
"""

import asyncio 
import logging 
import os 
import sys 
from pathlib import Path 

sys .path .append (str (Path (__file__ ).resolve ().parents [2 ]))

from google .adk .agents import LlmAgent 
from google .adk .models .lite_llm import LiteLlm 
from google .genai import types 

from src .config .settings import MODEL ,require_api_key ,get_model_for_route ,get_llm_params ,USE_LITELLM_PROXY 
from src .session import make_runner 
from src .tools .order_tools import cancel_order ,get_customer_context ,get_order_status ,save_customer_name 
from src .tools .product_tools import check_stock ,get_product_by_id ,lookup_product 
from src .tools .rag_tool import search_knowledge_base 

logger =logging .getLogger (__name__ )

_AGENT_DIR =Path (__file__ ).resolve ().parent 

INSTRUCTION_FILES ={
"v1":_AGENT_DIR /"support_instructions_v1.txt",
"v2":_AGENT_DIR /"support_instructions_v2.txt",
"v3":_AGENT_DIR /"support_instructions_v3.txt",
"v4":_AGENT_DIR /"support_instructions_v4_grounded.txt",
}





TOOL_USAGE_ADDENDUM ="""
Tool usage:

Knowledge Base (Day 05 - RAG):
- For questions about products, policies, shipping, warranty, returns, or general
  support topics, FIRST use search_knowledge_base to retrieve relevant information.
- Base your answer ONLY on what search_knowledge_base returns.
- If search_knowledge_base returns no results or insufficient information, use the
  fallback message from your instructions.
- Never guess product specs, prices, or policies not in the retrieved context.

Order Management:
- When a customer asks about their order status, use get_order_status.
  Ask for the order ID if missing. Use tool output directly.
- Use cancel_order when a customer requests cancellation. Check status first
  and explain if cancellation is not possible.

Product Tools (deprecated - use RAG instead):
- Use lookup_product, get_product_by_id, check_stock ONLY if search_knowledge_base
  doesn't provide sufficient product information.

Customer Context:
- Call save_customer_name when the customer introduces themselves.
- Call get_customer_context to recall stored session information.

Grounding Rule:
- Never invent information not provided by tools or retrieved knowledge.
- If uncertain, use the fallback message from instructions.
""".strip ()

TOOLS =[
search_knowledge_base ,
get_order_status ,
cancel_order ,
save_customer_name ,
get_customer_context ,
lookup_product ,
get_product_by_id ,
check_stock ,
]


def load_instruction (version :str ="v4")->str :
    """Load one of the instruction variants from disk, with the tool-usage addendum appended."""
    path =INSTRUCTION_FILES .get (version )
    if path is None or not path .exists ():
        raise FileNotFoundError (f"No instruction file found for version '{version }'")
    base =path .read_text (encoding ="utf-8").strip ()
    return f"{base }\n\n{TOOL_USAGE_ADDENDUM }"


def determine_routing_hint (query :str )->str :
    """
    Determine routing hint based on query complexity (Day 07).
    
    Simple heuristics to choose between fast-faq and deep-support:
    - Fast route: Simple FAQs, order status, product lookups
    - Deep route: Complex complaints, multi-step reasoning, ambiguous queries
    
    Args:
        query: User query text
    
    Returns:
        Routing hint: "fast" or "deep"
    """
    query_lower =query .lower ()


    deep_keywords =[
    "complaint","issue","problem","not working","defective",
    "refund","cancel","exchange",
    "compare","comparison","vs","versus",
    "recommend","suggestion","should i","which","best",
    "help me choose","confused","don't know","unsure",
    "multiple","several","why",
    "how to choose","what's better","difference between",
    ]


    fast_keywords =[
    "order status","track","where is my","order id",
    "product price","cost","how much",
    "in stock","available","availability",
    "shipping","delivery time","when will",
    "return policy","warranty","guarantee",
    ]


    if any (keyword in query_lower for keyword in deep_keywords ):
        return "deep"


    if any (keyword in query_lower for keyword in fast_keywords ):
        return "fast"


    word_count =len (query .split ())
    has_question_mark ="?"in query 


    if any (word in query_lower for word in ["should","would","could","which","what if"]):
        return "deep"


    if word_count <=10 and has_question_mark :
        return "fast"


    if word_count >20 :
        return "deep"


    return "deep"


def build_support_agent (version :str ="v4",route_hint :str ="default")->LlmAgent :
    """
    Build the eComBot support agent using the chosen instruction version + tools.
    
    Day 07: Accepts route_hint to select appropriate model via LiteLLM proxy.
    """
    instruction =load_instruction (version )


    if USE_LITELLM_PROXY :
        model_name =get_model_for_route (route_hint )
        llm_params =get_llm_params (route_hint )
        logger .info (f"Building agent with proxy route: {route_hint } → model: {model_name }")
    else :
        model_name =MODEL 
        llm_params ={"model":model_name }
        logger .debug (f"Building agent with direct model: {model_name }")

    return LlmAgent (
    name ="ecombot_support_agent",
    model =LiteLlm (**llm_params ),
    instruction =instruction ,
    description =(
    "eComBot support agent for an electronics e-commerce store -- "
    "handles order status, cancellations, product discovery with "
    "RAG-grounded knowledge retrieval, PostgreSQL-backed tools, "
    "and Redis session persistence. Answers are grounded in retrieved "
    "evidence with hallucination guards. Day 07: Routes intelligently "
    "between fast-faq and deep-support models via LiteLLM proxy."
    ),
    tools =TOOLS ,
    )




_default_version =os .environ .get ("ECOMBOT_INSTRUCTION_VERSION","v4")
root_agent =build_support_agent (_default_version )




async def _demo ()->None :
    require_api_key ()

    runner ,user_id ,session_id =await make_runner (root_agent )

    questions =[
    "Hi, my name is Priya.",
    "Where is my order ORD-001?",
    "What about ORD-002?",
    "Can you track ZZ-999?",
    ]

    for question in questions :
        print (f"\nUser : {question }")
        message =types .Content (role ="user",parts =[types .Part (text =question )])
        reply =""
        async for event in runner .run_async (
        user_id =user_id ,session_id =session_id ,new_message =message 
        ):
            if event .is_final_response ():
                if event .content and event .content .parts :
                    reply =event .content .parts [0 ].text or ""
        print (f"Agent: {reply .strip ()}")


if __name__ =="__main__":
    asyncio .run (_demo ())
