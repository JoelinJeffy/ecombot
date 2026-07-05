"""
settings.py -- Central configuration for eComBot
--------------------------------------------------
Mirrors the config pattern used in common.py from the Day 01 demo,
but scoped as a proper package module for the eComBot capstone project.

Day 04: Added Redis and PostgreSQL configuration.
Day 05: Added embedding model for RAG.
Day 07: Added LiteLLM proxy support with model group routing.
"""

import logging 
import os 

from dotenv import load_dotenv 


logging .getLogger ("asyncio").setLevel (logging .CRITICAL )

os .environ .setdefault ("LITELLM_LOG","ERROR")
for _name in ("LiteLLM","LiteLLM Router","LiteLLM Proxy"):
    _log =logging .getLogger (_name )
    _log .setLevel (logging .CRITICAL )
    _log .propagate =False 

load_dotenv ()

import litellm 

litellm .suppress_debug_info =True 





USE_LITELLM_PROXY =os .getenv ("USE_LITELLM_PROXY","false").lower ()=="true"
LITELLM_PROXY_URL =os .getenv ("LITELLM_PROXY_URL","http://localhost:4000")



MODEL_FAST ="fast-faq"
MODEL_DEEP ="deep-support"


MODEL ="openrouter/google/gemini-2.5-flash"


APP_NAME ="ecombot"


DOMAIN ="electronics e-commerce"





REDIS_HOST =os .getenv ("REDIS_HOST","localhost")
REDIS_PORT =int (os .getenv ("REDIS_PORT","6379"))
REDIS_PASSWORD =os .getenv ("REDIS_PASSWORD","ecombot_redis_pass")
REDIS_DB =int (os .getenv ("REDIS_DB","0"))


POSTGRES_HOST =os .getenv ("POSTGRES_HOST","localhost")
POSTGRES_PORT =int (os .getenv ("POSTGRES_PORT","5432"))
POSTGRES_DB =os .getenv ("POSTGRES_DB","ecombot")
POSTGRES_USER =os .getenv ("POSTGRES_USER","ecombot_user")
POSTGRES_PASSWORD =os .getenv ("POSTGRES_PASSWORD","ecombot_pg_pass")


SESSION_TTL =int (os .getenv ("SESSION_TTL","3600"))


def require_api_key ()->None :
    """Fail fast with a clear message if the key is missing (Day 01 checkpoint)."""
    if not os .environ .get ("OPENROUTER_API_KEY"):
        raise RuntimeError (
        "\n[ERROR] OPENROUTER_API_KEY is not set.\n"
        "Create a .env file in this directory with:\n"
        "  OPENROUTER_API_KEY=your-key-here\n"
        )





def get_redis_url ()->str :
    """Build Redis connection URL with password."""
    return f"redis://:{REDIS_PASSWORD }@{REDIS_HOST }:{REDIS_PORT }/{REDIS_DB }"


def get_postgres_dsn ()->str :
    """Build PostgreSQL connection DSN."""
    return (
    f"host={POSTGRES_HOST } "
    f"port={POSTGRES_PORT } "
    f"dbname={POSTGRES_DB } "
    f"user={POSTGRES_USER } "
    f"password={POSTGRES_PASSWORD }"
    )




def get_model_for_route (route_hint :str ="default")->str :
    """
    Get the appropriate model name based on routing hint.
    
    Args:
        route_hint: Routing hint from agent ("fast", "deep", or "default")
    
    Returns:
        Model name to use (either proxy group or direct model)
    
    Day 07: Routes to fast-faq or deep-support when proxy is enabled.
    Falls back to direct model when proxy is disabled.
    """
    if not USE_LITELLM_PROXY :
        return MODEL 


    route_map ={
    "fast":MODEL_FAST ,
    "simple":MODEL_FAST ,
    "faq":MODEL_FAST ,
    "deep":MODEL_DEEP ,
    "complex":MODEL_DEEP ,
    "support":MODEL_DEEP ,
    "default":MODEL_DEEP ,
    }

    return route_map .get (route_hint .lower (),MODEL_DEEP )


def get_llm_params (route_hint :str ="default")->dict :
    """
    Get LiteLLM parameters for the given route.
    
    Args:
        route_hint: Routing hint from agent
    
    Returns:
        Dictionary of LiteLLM parameters including model and base_url
    
    Day 07: Returns proxy URL when enabled, direct params otherwise.
    """
    model =get_model_for_route (route_hint )

    if USE_LITELLM_PROXY :
        return {
        "model":model ,
        "api_base":LITELLM_PROXY_URL ,
        "custom_llm_provider":"openai",
        }
    else :
        return {
        "model":model ,
        }

