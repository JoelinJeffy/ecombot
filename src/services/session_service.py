"""
session_service.py -- Redis-backed session persistence (Day 04)
----------------------------------------------------------------
Implements durable session state that survives process restarts.
Stores short-lived working context like customer name, current order, etc.
"""

import json 
import logging 
from typing import Any ,Dict ,Optional 

import redis 

from src .config .settings import get_redis_url ,SESSION_TTL 

logger =logging .getLogger (__name__ )


_redis_client :Optional [redis .Redis ]=None 


def get_redis_client ()->redis .Redis :
    """Get or create Redis client singleton."""
    global _redis_client 

    if _redis_client is None :
        try :
            _redis_client =redis .from_url (
            get_redis_url (),
            decode_responses =True 
            )

            _redis_client .ping ()
            logger .info ("Redis client initialized")
        except redis .RedisError as e :
            logger .error (f"Failed to connect to Redis: {e }")
            raise RuntimeError (f"Redis connection failed: {e }")

    return _redis_client 


def close_redis_client ()->None :
    """Close Redis connection."""
    global _redis_client 

    if _redis_client is not None :
        _redis_client .close ()
        _redis_client =None 
        logger .info ("Redis client closed")


class RedisSessionService :
    """
    Redis-backed session service for ADK.
    Stores session state with automatic expiration.
    """

    def __init__ (self ):
        self .client =get_redis_client ()

    def _make_key (self ,user_id :str ,session_id :str )->str :
        """Build Redis key for session data."""
        return f"session:{user_id }:{session_id }"

    def get_session_state (self ,user_id :str ,session_id :str )->Dict [str ,Any ]:
        """
        Retrieve session state from Redis.
        Returns empty dict if session doesn't exist.
        """
        key =self ._make_key (user_id ,session_id )

        try :
            data =self .client .get (key )
            if data :
                return json .loads (data )
            return {}
        except (redis .RedisError ,json .JSONDecodeError )as e :
            logger .error (f"Failed to get session state: {e }")
            return {}

    def set_session_state (
    self ,
    user_id :str ,
    session_id :str ,
    state :Dict [str ,Any ]
    )->None :
        """
        Store session state in Redis with TTL.
        """
        key =self ._make_key (user_id ,session_id )

        try :
            self .client .setex (
            key ,
            SESSION_TTL ,
            json .dumps (state )
            )
            logger .debug (f"Session state saved: {key }")
        except (redis .RedisError ,json .JSONDecodeError )as e :
            logger .error (f"Failed to set session state: {e }")

    def update_session_state (
    self ,
    user_id :str ,
    session_id :str ,
    updates :Dict [str ,Any ]
    )->None :
        """
        Update specific fields in session state.
        Merges updates with existing state.
        """
        current =self .get_session_state (user_id ,session_id )
        current .update (updates )
        self .set_session_state (user_id ,session_id ,current )

    def delete_session (self ,user_id :str ,session_id :str )->None :
        """Delete session from Redis."""
        key =self ._make_key (user_id ,session_id )

        try :
            self .client .delete (key )
            logger .info (f"Session deleted: {key }")
        except redis .RedisError as e :
            logger .error (f"Failed to delete session: {e }")

    def extend_session (self ,user_id :str ,session_id :str )->None :
        """Extend session TTL (refresh on activity)."""
        key =self ._make_key (user_id ,session_id )

        try :
            self .client .expire (key ,SESSION_TTL )
        except redis .RedisError as e :
            logger .error (f"Failed to extend session: {e }")
