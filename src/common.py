"""
common.py -- Shared console + messaging helpers for eComBot scripts
--------------------------------------------------------------------
Adapts the Day 01 common.py pattern (ask / console helpers) to the
eComBot support agent.

As of Day 03, session/runner creation has moved to session.py (the
single swap point for InMemorySessionService -> persistent storage
later). This module re-exports make_runner from there so existing
call sites (`from src.common import ask, make_runner, ...`) keep
working without change.
"""

import textwrap 

from google .adk .runners import Runner 
from google .genai import types 

from src .session import make_runner 


def divider (title :str )->None :
    width =70 
    print ("\n"+"="*width )
    print (f"  {title }")
    print ("="*width )


def label (tag :str )->None :
    print (f"\n  [{tag }]")


def wrap (text :str ,indent :int =4 )->str :
    prefix =" "*indent 
    return textwrap .fill (text ,width =74 ,initial_indent =prefix ,subsequent_indent =prefix )


def _build_message (text :str )->types .Content :
    return types .Content (role ="user",parts =[types .Part (text =text )])


async def ask (runner :Runner ,user_id :str ,session_id :str ,question :str )->str :
    """Send one user message and return the agent's final text reply."""
    reply_text =""
    async for event in runner .run_async (
    user_id =user_id ,
    session_id =session_id ,
    new_message =_build_message (question ),
    ):
        if event .is_final_response ():
            if event .content and event .content .parts :
                reply_text =event .content .parts [0 ].text or ""
    return reply_text .strip ()
