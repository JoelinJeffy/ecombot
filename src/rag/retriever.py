"""
retriever.py -- ChromaDB retrieval interface (Day 05)
------------------------------------------------------
Retrieves relevant context from the knowledge base for grounding agent responses.

Usage:
    from src.rag.retriever import retrieve
    results = retrieve("What is the warranty on Dell XPS?", n_results=3)
"""

import logging 
from pathlib import Path 
from typing import List ,Dict ,Any ,Optional 

import chromadb 
from chromadb .config import Settings 
from chromadb .utils import embedding_functions 

logger =logging .getLogger (__name__ )


PROJECT_ROOT =Path (__file__ ).resolve ().parents [2 ]
CHROMA_DIR =PROJECT_ROOT /".chroma"
COLLECTION_NAME ="ecombot_kb"


_chroma_client :Optional [chromadb .ClientAPI ]=None 
_collection :Optional [chromadb .Collection ]=None 


def _get_collection ()->chromadb .Collection :
    """Get or create ChromaDB collection singleton."""
    global _chroma_client ,_collection 

    if _collection is None :
        try :
            _chroma_client =chromadb .PersistentClient (
            path =str (CHROMA_DIR ),
            settings =Settings (anonymized_telemetry =False )
            )


            embedding_function =embedding_functions .SentenceTransformerEmbeddingFunction (
            model_name ="all-MiniLM-L6-v2"
            )

            _collection =_chroma_client .get_collection (
            name =COLLECTION_NAME ,
            embedding_function =embedding_function 
            )
            logger .info (f"Loaded ChromaDB collection: {COLLECTION_NAME }")
        except Exception as e :
            logger .error (f"Failed to load ChromaDB collection: {e }")
            raise RuntimeError (
            f"ChromaDB collection '{COLLECTION_NAME }' not found. "
            f"Run: python -m src.rag.embed_catalog"
            )

    return _collection 






def retrieve (
query :str ,
n_results :int =3 ,
filter_metadata :Optional [Dict [str ,Any ]]=None 
)->List [Dict [str ,Any ]]:
    """
    Retrieve most relevant chunks from the knowledge base.
    
    Args:
        query: User query string
        n_results: Number of chunks to retrieve (default: 3)
        filter_metadata: Optional metadata filter (e.g., {"type": "faq"})
    
    Returns:
        List of dicts with keys: 'text', 'metadata', 'distance'
        Returns empty list if retrieval fails or collection is empty.
    
    Example:
        results = retrieve("What is the warranty on laptops?")
        for result in results:
            print(result['text'])
            print(result['metadata'])
    """
    try :
        collection =_get_collection ()


        count =collection .count ()
        if count ==0 :
            logger .warning ("ChromaDB collection is empty. Run embed_catalog.py first.")
            return []


        results =collection .query (
        query_texts =[query ],
        n_results =min (n_results ,count ),
        where =filter_metadata if filter_metadata else None 
        )


        formatted =[]
        if results and results ["documents"]and results ["documents"][0 ]:
            for i ,doc in enumerate (results ["documents"][0 ]):
                formatted .append ({
                "text":doc ,
                "metadata":results ["metadatas"][0 ][i ]if results ["metadatas"]else {},
                "distance":results ["distances"][0 ][i ]if results ["distances"]else None 
                })

        logger .debug (f"Retrieved {len (formatted )} chunks for query: {query }")
        return formatted 

    except Exception as e :
        logger .error (f"Retrieval failed: {e }")
        return []


def retrieve_products (query :str ,n_results :int =2 )->List [Dict [str ,Any ]]:
    """Retrieve product-related chunks only."""
    return retrieve (query ,n_results =n_results )


def retrieve_faq (query :str ,n_results :int =3 )->List [Dict [str ,Any ]]:
    """Retrieve FAQ chunks only."""
    return retrieve (query ,n_results =n_results ,filter_metadata ={"type":"faq"})


def format_context (results :List [Dict [str ,Any ]],include_metadata :bool =True )->str :
    """
    Format retrieved chunks into a context string for the agent.
    
    Args:
        results: List of retrieval results
        include_metadata: Whether to include source metadata in context (Day 06)
    
    Returns:
        Formatted context string
    
    Day 06 enhancement: Includes source file, page, and section metadata for traceability.
    """
    if not results :
        return ""

    context ="Retrieved knowledge:\n\n"
    for i ,result in enumerate (results ,1 ):
        context +=f"[{i }] {result ['text']}"


        if include_metadata and result .get ('metadata'):
            meta =result ['metadata']
            source_parts =[]

            if meta .get ('source_file'):
                source_parts .append (f"Source: {meta ['source_file']}")
            if meta .get ('page'):
                source_parts .append (f"Page {meta ['page']}")
            if meta .get ('section'):
                source_parts .append (f"Section: {meta ['section']}")

            if source_parts :
                context +=f"\n   ({', '.join (source_parts )})"

        context +="\n\n"

    return context .strip ()


def format_metadata_for_display (metadata :Dict [str ,Any ])->str :
    """
    Format metadata for human-readable display (Day 06).
    
    Useful for debugging and test validation.
    """
    parts =[]

    if metadata .get ('document_title'):
        parts .append (f"Document: {metadata ['document_title']}")
    elif metadata .get ('product_name'):
        parts .append (f"Product: {metadata ['product_name']}")

    if metadata .get ('page'):
        parts .append (f"Page: {metadata ['page']}")

    if metadata .get ('section'):
        parts .append (f"Section: {metadata ['section']}")

    if metadata .get ('type'):
        parts .append (f"Type: {metadata ['type']}")

    return " | ".join (parts )if parts else "No metadata"
