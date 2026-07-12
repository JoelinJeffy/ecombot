"""
rag_tool.py -- RAG retrieval tool for grounding agent responses (Day 05)
-------------------------------------------------------------------------
Provides a tool interface for retrieving knowledge base context.
"""

import logging 
from typing import Any ,Dict 

from google .adk .tools import ToolContext 

from src .rag .retriever import retrieve ,format_context 

logger =logging .getLogger (__name__ )


def search_knowledge_base (
query :str ,
tool_context :ToolContext ,
)->Dict [str ,Any ]:
    """
    Search the knowledge base for relevant information.
    Use this when answering questions about products, policies, shipping, warranty, etc.
    
    Args:
        query: The search query (user's question or topic)
    
    Returns:
        A dict with 'results' (list of relevant chunks) and 'context' (formatted string)
    """
    try :
        results =retrieve (query ,n_results =3 )

        if not results :
            logger .warning (f"No knowledge base results for query: {query }")
            return {
            "found":False ,
            "message":"No relevant information found in knowledge base.",
            "context":""
            }


        tool_context .state ["last_rag_query"]=query 
        tool_context .state ["last_rag_results_count"]=len (results )

        return {
        "found":True ,
        "results_count":len (results ),
        "context":format_context (results ),
        "results":[
        {
        "text":r ["text"],
        "type":r ["metadata"].get ("type","unknown")
        }
        for r in results 
        ]
        }

    except Exception as e :
        logger .error (f"Knowledge base search failed: {e }")
        return {
        "found":False ,
        "error":"Knowledge base temporarily unavailable.",
        "context":""
        }
