"""
demo.py -- eComBot interactive and scenario runner (Day 03)
------------------------------------------------------------
Unified demo script supporting both interactive chat and automated scenarios.

Modes:
  - Interactive (default): Type prompts freely, q to quit
  - Scenario: Run predefined test scenarios automatically

Run:
    python demo.py                              # interactive mode
    python demo.py --version v3                 # use different instruction version
    python demo.py --scenario basic             # run basic scenario
    python demo.py --scenario tools             # run Day 03 tool validation
"""

import argparse 
import asyncio 
import textwrap 

from google .genai import types 

from src .agents .support_agent import build_support_agent 
from src .common import ask ,divider ,label ,wrap 
from src .config .settings import require_api_key 
from src .session import make_runner 


BASIC_PROMPTS =[
"Hi, can you help me?",
"Where is my order #10234?",
"Can you recommend a good laptop for video editing?",
]


TOOL_PROMPTS =[
"Hi, my name is Priya.",
"Where is my order ORD-001?",
"What about ORD-002?",
"Can you track ZZ-999?",
]

_GUIDE ="""
  SCENARIO GUIDE  (type freely or follow this order)
  ────────────────────────────────────────────────────────────────────
  1  Introduce yourself   "Hi, my name is Priya."
  2  Valid order          "Where is my order ORD-001?"
  3  Follow-up order      "What about ORD-002?"          ← reuses name
  4  Not-found order      "What is the status of ORD-999?"
  5  Invalid format       "Track order XYZ-100"
  6  Recall context       "What do you know about me so far?"
  ────────────────────────────────────────────────────────────────────
  All prompts run in ONE session -- state (customer_name, last_order_id)
  accumulates. Scenario 6 reads back what earlier tool calls wrote.
"""


def _wrap_text (text :str )->str :
    """Wrap text for interactive mode output."""
    prefix ="    "
    return textwrap .fill (text ,width =74 ,initial_indent =prefix ,subsequent_indent =prefix )


def _build_message (text :str )->types .Content :
    """Create a user message for the ADK runner."""
    return types .Content (role ="user",parts =[types .Part (text =text )])


async def _ask_interactive (runner ,user_id :str ,session_id :str ,prompt :str )->str :
    """Ask a question in interactive mode and return the reply."""
    reply =""
    async for event in runner .run_async (
    user_id =user_id ,session_id =session_id ,new_message =_build_message (prompt )
    ):
        if event .is_final_response ():
            if event .content and event .content .parts :
                reply =event .content .parts [0 ].text or ""
    return reply .strip ()


async def run_interactive (version :str )->None :
    """Run interactive REPL mode."""
    require_api_key ()

    print (f"""
+======================================================================+
|         eComBot -- Tool Calling and Session State (Day 03)          |
|   Instruction version: {version }                                             |
+======================================================================+""")
    print (_GUIDE )

    agent =build_support_agent (version )
    runner ,user_id ,session_id =await make_runner (agent )

    while True :
        try :
            prompt =input ("  You: ").strip ()
        except (EOFError ,KeyboardInterrupt ):
            print ()
            break 

        if prompt .lower ()=="q":
            break 
        if not prompt :
            continue 

        reply =await _ask_interactive (runner ,user_id ,session_id ,prompt )
        print (f"\n  [eComBot]\n{_wrap_text (reply )}\n")

    print ("  Goodbye.\n")


async def run_scenario (version :str ,scenario :str )->None :
    """Run automated scenario mode."""
    require_api_key ()

    prompts =TOOL_PROMPTS if scenario =="tools"else BASIC_PROMPTS 
    divider (f"eComBot Support Agent -- version: {version } -- scenario: {scenario }")

    agent =build_support_agent (version )



    runner ,user_id ,session_id =await make_runner (agent )

    for question in prompts :
        label ("USER")
        print (wrap (question ))
        reply =await ask (runner ,user_id ,session_id ,question )
        label ("AGENT")
        print (wrap (reply ))

    print ("\n"+"="*70 )
    if scenario =="tools":
        print ("  Checkpoint: name stored after Turn 1, order tool called on")
        print ("  Turns 2-3, invalid format handled gracefully on Turn 4.")
    else :
        print ("  Checkpoint: agent started, responded, stayed on e-commerce topic.")
    print ("="*70 +"\n")


async def main (args )->None :
    """Main entry point - route to interactive or scenario mode."""
    if args .scenario :
        await run_scenario (args .version ,args .scenario )
    else :
        await run_interactive (args .version )


if __name__ =="__main__":
    parser =argparse .ArgumentParser (
    description ="eComBot demo: interactive chat or automated scenarios"
    )
    parser .add_argument (
    "--version",
    default ="v2",
    choices =["v1","v2","v3"],
    help ="Which instruction file to load (default: v2)"
    )
    parser .add_argument (
    "--scenario",
    choices =["basic","tools"],
    help ="Run automated scenario instead of interactive mode"
    )
    args =parser .parse_args ()
    asyncio .run (main (args ))
