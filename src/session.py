"""
session.py -- Session service factory (Day 04)
------------------------------------------------
Provides session management using Redis for short-term state persistence
and PostgreSQL for durable conversation history.

run_ecombot.py and manual test scripts call make_runner(agent) to get
a Runner + session. ADK Web creates its own session internally.

Day 04: Integrated Redis-backed session persistence and PostgreSQL history.
"""

import logging 
import uuid 

from google .adk .runners import Runner 
from google .adk .sessions import InMemorySessionService 

from src .config .settings import APP_NAME 
from src .services .db import init_db_pool 
from src .services .session_service import RedisSessionService 

logger =logging .getLogger (__name__ )



USE_REDIS =False 


def get_session_service ():
    """
    Get the appropriate session service based on configuration.
    
    Note: Redis integration is planned but currently disabled.
    Using InMemorySessionService for now until Redis session service
    properly implements ADK's SessionService interface.
    """
    if USE_REDIS :
        try :
            return RedisSessionService ()
        except RuntimeError as e :
            logger .warning (f"Redis unavailable, falling back to in-memory: {e }")
            return InMemorySessionService ()
    else :
        return InMemorySessionService ()


async def make_runner (agent )->tuple [Runner ,str ,str ]:
    """
    Wrap an agent in a Runner with a fresh isolated session.
    Initializes database pool and returns (runner, user_id, session_id).
    """

    try :
        init_db_pool ()
    except Exception as e :
        logger .warning (f"Database initialization failed: {e }")

    session_service =get_session_service ()
    runner =Runner (agent =agent ,app_name =APP_NAME ,session_service =session_service )

    user_id =f"user-{uuid .uuid4 ().hex [:6 ]}"
    session_id =f"session-{uuid .uuid4 ().hex [:8 ]}"


    if isinstance (session_service ,InMemorySessionService ):
        await session_service .create_session (
        app_name =APP_NAME ,user_id =user_id ,session_id =session_id 
        )

    return runner ,user_id ,session_id 

