"""
embed_catalog.py -- Build ChromaDB vector store from knowledge base (Day 05-06)
--------------------------------------------------------------------------------
Loads product catalog, FAQ data, and PDF documents, splits into chunks,
and stores in ChromaDB collection for retrieval with rich metadata.

Day 05: JSON-based product and FAQ indexing
Day 06: PDF document support with section-aware chunking and metadata

Run:
    python -m src.rag.embed_catalog
"""

import json 
import logging 
import os 
from pathlib import Path 
from typing import List ,Dict ,Any 

import chromadb 
from chromadb .config import Settings 
from chromadb .utils import embedding_functions 

logger =logging .getLogger (__name__ )


PROJECT_ROOT =Path (__file__ ).resolve ().parents [2 ]
DATA_DIR =PROJECT_ROOT /"data"
CHROMA_DIR =PROJECT_ROOT /".chroma"


COLLECTION_NAME ="ecombot_kb"


def load_products ()->List [Dict [str ,Any ]]:
    """Load product catalog from JSON."""
    products_file =DATA_DIR /"products.json"
    with open (products_file ,"r",encoding ="utf-8")as f :
        return json .load (f )


def load_faq ()->List [Dict [str ,Any ]]:
    """Load FAQ from JSON."""
    faq_file =DATA_DIR /"faq.json"
    with open (faq_file ,"r",encoding ="utf-8")as f :
        return json .load (f )


def chunk_product (product :Dict [str ,Any ])->List [Dict [str ,Any ]]:
    """
    Convert product into retrievable chunks.
    Each chunk is a focused piece of information.
    """
    chunks =[]


    main_chunk ={
    "text":f"{product ['product_name']} ({product ['product_id']})\n"
    f"Category: {product ['category']}\n"
    f"Price: ₹{product ['price']}\n"
    f"{product ['description']}\n"
    f"Best for: {product ['best_for']}",
    "metadata":{
    "type":"product_overview",
    "product_id":product ["product_id"],
    "product_name":product ["product_name"],
    "category":product ["category"]
    }
    }
    chunks .append (main_chunk )


    if "specifications"in product :
        specs_text =f"{product ['product_name']} Specifications:\n"
        for key ,value in product ["specifications"].items ():
            specs_text +=f"- {key .replace ('_',' ').title ()}: {value }\n"

        specs_chunk ={
        "text":specs_text ,
        "metadata":{
        "type":"product_specs",
        "product_id":product ["product_id"],
        "product_name":product ["product_name"]
        }
        }
        chunks .append (specs_chunk )


    policy_chunk ={
    "text":f"{product ['product_name']} Purchase Information:\n"
    f"Warranty: {product .get ('warranty','Not specified')}\n"
    f"Shipping: {product .get ('shipping','Standard shipping')}\n"
    f"Return Policy: {product .get ('return_policy','Standard returns')}\n"
    f"In Box: {product .get ('in_box','Product and accessories')}",
    "metadata":{
    "type":"product_policy",
    "product_id":product ["product_id"],
    "product_name":product ["product_name"]
    }
    }
    chunks .append (policy_chunk )

    return chunks 


def chunk_faq (faq_item :Dict [str ,Any ])->Dict [str ,Any ]:
    """
    Convert FAQ item into a retrievable chunk.
    """
    return {
    "text":f"Q: {faq_item ['question']}\nA: {faq_item ['answer']}",
    "metadata":{
    "type":"faq",
    "faq_id":faq_item ["id"],
    "category":faq_item ["category"],
    "question":faq_item ["question"]
    }
    }






def load_pdfs ()->List [Dict [str ,Any ]]:
    """
    Load and process all PDF files in data/ directory (Day 06).
    Returns chunks with metadata from PDFs.
    """
    from src .rag .pdf_processor import process_pdf_file 

    pdf_files =list (DATA_DIR .glob ("*.pdf"))
    all_chunks =[]

    for pdf_path in pdf_files :
        try :
            logger .info (f"Processing PDF: {pdf_path .name }")
            chunks =process_pdf_file (
            pdf_path ,
            chunk_size =1000 ,
            chunk_overlap =200 
            )
            all_chunks .extend (chunks )
        except Exception as e :
            logger .error (f"Failed to process {pdf_path .name }: {e }")

    return all_chunks 


def build_vector_store ():
    """
    Main function to build the ChromaDB vector store.
    Uses ChromaDB's default embedding function (sentence-transformers) - no API key needed!
    
    Day 05: Indexes JSON product and FAQ data
    Day 06: Indexes PDF documents with rich metadata
    """

    print ("Loading knowledge base...")
    products =load_products ()
    faqs =load_faq ()


    print ("Creating chunks from JSON data...")
    all_chunks =[]

    for product in products :
        all_chunks .extend (chunk_product (product ))

    for faq in faqs :
        all_chunks .append (chunk_faq (faq ))

    print (f"  JSON: {len (all_chunks )} chunks")


    print ("Processing PDF documents...")
    try :
        pdf_chunks =load_pdfs ()
        all_chunks .extend (pdf_chunks )
        print (f"  PDF: {len (pdf_chunks )} chunks")
    except Exception as e :
        logger .warning (f"PDF processing failed (may not have PDFs yet): {e }")
        print (f"  PDF: 0 chunks (skipped)")

    print (f"Total: {len (all_chunks )} chunks")


    texts =[chunk ["text"]for chunk in all_chunks ]
    metadatas =[chunk ["metadata"]for chunk in all_chunks ]
    ids =[f"chunk_{i }"for i in range (len (all_chunks ))]


    print ("Initializing ChromaDB...")
    chroma_client =chromadb .PersistentClient (
    path =str (CHROMA_DIR ),
    settings =Settings (anonymized_telemetry =False )
    )


    embedding_function =embedding_functions .SentenceTransformerEmbeddingFunction (
    model_name ="all-MiniLM-L6-v2"
    )


    try :
        chroma_client .delete_collection (name =COLLECTION_NAME )
        print (f"Deleted existing collection: {COLLECTION_NAME }")
    except Exception :
        pass 


    collection =chroma_client .create_collection (
    name =COLLECTION_NAME ,
    embedding_function =embedding_function ,
    metadata ={"description":"eComBot knowledge base - products and FAQ"}
    )


    print ("Adding documents to ChromaDB (embeddings generated automatically)...")
    collection .add (
    ids =ids ,
    documents =texts ,
    metadatas =metadatas 
    )

    print (f"✓ Successfully indexed {len (all_chunks )} chunks into {COLLECTION_NAME }")
    print (f"✓ ChromaDB location: {CHROMA_DIR }")


if __name__ =="__main__":
    logging .basicConfig (level =logging .INFO )
    build_vector_store ()
