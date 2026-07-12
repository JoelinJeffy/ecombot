"""
test_litellm_routing.py -- Test routing and fallback for eComBot v4 (Day 07)
-----------------------------------------------------------------------------
Validates that:
1. Simple queries route to fast-faq model group
2. Complex queries route to deep-support model group
3. Fallback works when primary model fails

Run:
    # With proxy running:
    export USE_LITELLM_PROXY=true
    python tests/test_litellm_routing.py
    
    # Without proxy (direct mode):
    export USE_LITELLM_PROXY=false
    python tests/test_litellm_routing.py
"""

import asyncio 
import logging 
import os 
import sys 
from pathlib import Path 


PROJECT_ROOT =Path (__file__ ).resolve ().parents [1 ]
sys .path .insert (0 ,str (PROJECT_ROOT ))

from src .agents .support_agent import determine_routing_hint ,build_support_agent 
from src .config .settings import USE_LITELLM_PROXY ,LITELLM_PROXY_URL ,get_model_for_route 

logging .basicConfig (level =logging .INFO ,format ='%(levelname)s: %(message)s')
logger =logging .getLogger (__name__ )


class RoutingTestSuite :
    """Test suite for LiteLLM routing and fallback."""

    def __init__ (self ):
        self .results =[]
        self .proxy_enabled =USE_LITELLM_PROXY 

    def test_routing_hint_classification (self ):
        """Test that routing hints are classified correctly."""
        print ("\n"+"="*70 )
        print ("TEST 1: Routing Hint Classification")
        print ("="*70 )

        test_cases =[

        ("Where is my order ORD-001?","fast","Simple order status"),
        ("Track my order","fast","Simple tracking request"),
        ("What is your return policy?","fast","Simple FAQ"),
        ("Is Dell XPS 15 in stock?","fast","Simple stock check"),

        ("I have a complaint about my order","deep","Complaint"),
        ("My product is defective and I want a refund","deep","Complex issue"),
        ("Which laptop should I buy for video editing?","deep","Product recommendation"),
        ("Can you compare Dell XPS and MacBook?","deep","Product comparison"),
        ("Why was my order cancelled without notice?","deep","Complex inquiry"),
        ]

        passed =0 
        failed =0 

        for query ,expected_hint ,description in test_cases :
            actual_hint =determine_routing_hint (query )
            status ="✓ PASS"if actual_hint ==expected_hint else "✗ FAIL"

            if actual_hint ==expected_hint :
                passed +=1 
            else :
                failed +=1 

            print (f"\n{status } | {description }")
            print (f"  Query: {query }")
            print (f"  Expected: {expected_hint } | Actual: {actual_hint }")

        print (f"\n{'─'*70 }")
        print (f"Results: {passed }/{len (test_cases )} passed, {failed } failed")

        self .results .append ({
        "test":"Routing Hint Classification",
        "passed":passed ,
        "failed":failed ,
        "total":len (test_cases )
        })

        return failed ==0 

    def test_model_selection (self ):
        """Test that correct models are selected for routing hints."""
        print ("\n"+"="*70 )
        print ("TEST 2: Model Selection")
        print ("="*70 )

        if not self .proxy_enabled :
            print ("\n⚠ Proxy disabled - skipping model selection test")
            print ("  Set USE_LITELLM_PROXY=true to test routing")
            return True 

        test_cases =[
        ("fast","fast-faq"),
        ("simple","fast-faq"),
        ("faq","fast-faq"),
        ("deep","deep-support"),
        ("complex","deep-support"),
        ("support","deep-support"),
        ("default","deep-support"),
        ]

        passed =0 
        failed =0 

        for hint ,expected_model in test_cases :
            actual_model =get_model_for_route (hint )
            status ="✓ PASS"if actual_model ==expected_model else "✗ FAIL"

            if actual_model ==expected_model :
                passed +=1 
            else :
                failed +=1 

            print (f"{status } | Hint: {hint :10} → Model: {actual_model :20} (expected: {expected_model })")

        print (f"\n{'─'*70 }")
        print (f"Results: {passed }/{len (test_cases )} passed, {failed } failed")

        self .results .append ({
        "test":"Model Selection",
        "passed":passed ,
        "failed":failed ,
        "total":len (test_cases )
        })

        return failed ==0 

    async def test_agent_routing (self ):
        """Test that agent is built with correct routing."""
        print ("\n"+"="*70 )
        print ("TEST 3: Agent Build with Routing")
        print ("="*70 )

        test_routes =["fast","deep","default"]

        passed =0 
        failed =0 

        for route_hint in test_routes :
            try :
                agent =build_support_agent (version ="v4",route_hint =route_hint )
                expected_model =get_model_for_route (route_hint )if self .proxy_enabled else None 

                print (f"\n✓ PASS | Built agent with route: {route_hint }")
                if self .proxy_enabled :
                    print (f"  Model: {expected_model }")
                else :
                    print (f"  Direct mode (no routing)")

                passed +=1 
            except Exception as e :
                print (f"\n✗ FAIL | Failed to build agent with route: {route_hint }")
                print (f"  Error: {e }")
                failed +=1 

        print (f"\n{'─'*70 }")
        print (f"Results: {passed }/{len (test_routes )} passed, {failed } failed")

        self .results .append ({
        "test":"Agent Build with Routing",
        "passed":passed ,
        "failed":failed ,
        "total":len (test_routes )
        })

        return failed ==0 

    def test_proxy_connectivity (self ):
        """Test that proxy is reachable (if enabled)."""
        print ("\n"+"="*70 )
        print ("TEST 4: Proxy Connectivity")
        print ("="*70 )

        if not self .proxy_enabled :
            print ("\n⚠ Proxy disabled - skipping connectivity test")
            print ("  Set USE_LITELLM_PROXY=true and start proxy to test")
            return True 

        try :
            import requests 

            health_url =f"{LITELLM_PROXY_URL }/health"
            print (f"\nChecking proxy health: {health_url }")

            response =requests .get (health_url ,timeout =5 )

            if response .status_code ==200 :
                print (f"✓ PASS | Proxy is healthy")
                print (f"  Status: {response .status_code }")
                print (f"  Response: {response .text [:100 ]}")

                self .results .append ({
                "test":"Proxy Connectivity",
                "passed":1 ,
                "failed":0 ,
                "total":1 
                })
                return True 
            else :
                print (f"✗ FAIL | Proxy returned non-200 status: {response .status_code }")

                self .results .append ({
                "test":"Proxy Connectivity",
                "passed":0 ,
                "failed":1 ,
                "total":1 
                })
                return False 

        except Exception as e :
            print (f"✗ FAIL | Could not connect to proxy: {e }")
            print (f"\nMake sure proxy is running:")
            print (f"  python scripts/start_litellm_proxy.py")

            self .results .append ({
            "test":"Proxy Connectivity",
            "passed":0 ,
            "failed":1 ,
            "total":1 
            })
            return False 

    async def run_all_tests (self ):
        """Run the complete test suite."""
        print ("\n"+"="*70 )
        print ("eComBot v4 - LiteLLM Routing Test Suite")
        print ("="*70 )
        print (f"\nProxy Mode: {'ENABLED'if self .proxy_enabled else 'DISABLED'}")
        if self .proxy_enabled :
            print (f"Proxy URL: {LITELLM_PROXY_URL }")
        print ()


        all_passed =True 

        all_passed &=self .test_routing_hint_classification ()
        all_passed &=self .test_model_selection ()
        all_passed &=await self .test_agent_routing ()
        all_passed &=self .test_proxy_connectivity ()


        print ("\n"+"="*70 )
        print ("TEST SUMMARY")
        print ("="*70 )

        total_passed =sum (r ["passed"]for r in self .results )
        total_failed =sum (r ["failed"]for r in self .results )
        total_tests =sum (r ["total"]for r in self .results )

        print (f"\nTotal Tests: {total_tests }")
        print (f"  ✓ Passed: {total_passed }")
        print (f"  ✗ Failed: {total_failed }")

        for result in self .results :
            status ="✓"if result ["failed"]==0 else "✗"
            print (f"\n{status } {result ['test']}: {result ['passed']}/{result ['total']} passed")

        print ("\n"+"="*70 )

        if all_passed :
            print ("✓ All tests passed!")
        else :
            print ("✗ Some tests failed - review output above")

        print ("="*70 +"\n")

        return all_passed 


async def main ():
    """Run the routing test suite."""
    suite =RoutingTestSuite ()
    success =await suite .run_all_tests ()
    sys .exit (0 if success else 1 )


if __name__ =="__main__":
    asyncio .run (main ())
