#!/usr/bin/env python3
"""
demo_routing.py -- Demonstrate LiteLLM routing with eComBot v4 (Day 07)
------------------------------------------------------------------------
Shows how queries are routed between fast-faq and deep-support models.

Run:
    # Without proxy (direct mode)
    export USE_LITELLM_PROXY=false
    python scripts/demo_routing.py
    
    # With proxy (routing mode)
    # Terminal 1: python scripts/start_litellm_proxy.py
    # Terminal 2:
    export USE_LITELLM_PROXY=true
    python scripts/demo_routing.py
"""

import asyncio 
import logging 
import os 
import sys 
from pathlib import Path 


PROJECT_ROOT =Path (__file__ ).resolve ().parents [1 ]
sys .path .insert (0 ,str (PROJECT_ROOT ))

from src .agents .support_agent import determine_routing_hint 
from src .config .settings import USE_LITELLM_PROXY ,get_model_for_route 

logging .basicConfig (level =logging .INFO ,format ='%(levelname)s: %(message)s')
logger =logging .getLogger (__name__ )



DEMO_QUERIES =[
{
"category":"Simple Queries (Fast Route)",
"queries":[
"Where is my order ORD-001?",
"What is your return policy?",
"Is Dell XPS 15 in stock?",
"How much does the Sony headphone cost?",
"When will my order arrive?",
]
},
{
"category":"Complex Queries (Deep Route)",
"queries":[
"I have a complaint about my defective laptop and want a full refund",
"Which laptop should I buy for professional video editing and 3D rendering?",
"Can you compare the Dell XPS 15 and MacBook Pro for my use case?",
"Why was my order cancelled without any notification?",
"I'm confused about which phone to choose - help me decide",
]
},
]


def print_routing_analysis (query :str ,route :str ,model :str ):
    """Print routing analysis for a query."""
    route_emoji ="⚡"if route =="fast"else "🧠"

    print (f"\n{route_emoji } Query: {query }")
    print (f"   Route: {route .upper ()}")
    if USE_LITELLM_PROXY :
        print (f"   Model: {model }")
    else :
        print (f"   Model: {model } (direct mode)")
    print (f"   {'-'*70 }")


async def main ():
    """Run the routing demonstration."""
    print ("\n"+"="*70 )
    print ("eComBot v4 - LiteLLM Routing Demonstration")
    print ("="*70 )


    print (f"\nConfiguration:")
    print (f"  Proxy Mode: {'ENABLED'if USE_LITELLM_PROXY else 'DISABLED'}")

    if USE_LITELLM_PROXY :
        from src .config .settings import LITELLM_PROXY_URL ,MODEL_FAST ,MODEL_DEEP 
        print (f"  Proxy URL: {LITELLM_PROXY_URL }")
        print (f"  Fast Model: {MODEL_FAST }")
        print (f"  Deep Model: {MODEL_DEEP }")
    else :
        from src .config .settings import MODEL 
        print (f"  Direct Model: {MODEL }")

    print (f"\nRouting Logic:")
    print (f"  ⚡ FAST route → Lightweight model for simple queries")
    print (f"  🧠 DEEP route → Capable model for complex queries")


    for category_info in DEMO_QUERIES :
        category =category_info ["category"]
        queries =category_info ["queries"]

        print ("\n"+"="*70 )
        print (f"{category }")
        print ("="*70 )

        for query in queries :
            route =determine_routing_hint (query )
            model =get_model_for_route (route )
            print_routing_analysis (query ,route ,model )


    print ("\n"+"="*70 )
    print ("ROUTING SUMMARY")
    print ("="*70 )

    total_queries =sum (len (cat ["queries"])for cat in DEMO_QUERIES )
    fast_count =0 
    deep_count =0 

    for category_info in DEMO_QUERIES :
        for query in category_info ["queries"]:
            route =determine_routing_hint (query )
            if route =="fast":
                fast_count +=1 
            else :
                deep_count +=1 

    print (f"\nTotal Queries: {total_queries }")
    print (f"  ⚡ Fast Route: {fast_count } ({fast_count /total_queries *100 :.0f}%)")
    print (f"  🧠 Deep Route: {deep_count } ({deep_count /total_queries *100 :.0f}%)")

    if USE_LITELLM_PROXY :
        print (f"\n💡 Cost Optimization:")
        print (f"  {fast_count } queries routed to free/cheap models")
        print (f"  {deep_count } queries routed to premium models")
        print (f"  Estimated savings: ~{fast_count /total_queries *50 :.0f}% vs all-premium")
    else :
        print (f"\n💡 Enable proxy mode to see routing in action:")
        print (f"  export USE_LITELLM_PROXY=true")
        print (f"  python scripts/start_litellm_proxy.py")

    print ("\n"+"="*70 )
    print ("Next Steps:")
    print ("="*70 )

    if not USE_LITELLM_PROXY :
        print ("\n1. Start the LiteLLM proxy:")
        print ("   python scripts/start_litellm_proxy.py")
        print ("\n2. Enable proxy mode:")
        print ("   export USE_LITELLM_PROXY=true")
        print ("\n3. Re-run this demo:")
        print ("   python scripts/demo_routing.py")
        print ("\n4. Test with the agent:")
        print ("   python demo.py")
    else :
        print ("\n✓ Proxy mode is enabled!")
        print ("\n1. Test with the agent:")
        print ("   python demo.py")
        print ("\n2. Run validation tests:")
        print ("   python tests/test_litellm_routing.py")
        print ("\n3. Monitor proxy logs for routing decisions")

    print ("\n"+"="*70 +"\n")


if __name__ =="__main__":
    asyncio .run (main ())
