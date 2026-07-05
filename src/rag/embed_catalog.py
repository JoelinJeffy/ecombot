"""
embed_catalog.py -- Build ChromaDB vector store from knowledge base (Day 05)
-----------------------------------------------------------------------------
Loads product catalog and FAQ data, splits into chunks, embeds with OpenAI,
and stores in ChromaDB collection for retrieval.

Run:
    python -m src.rag.embed_catalog
"""

import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / ".chroma"

# Collection name
COLLECTION_NAME = "ecombot_kb"


def load_products() -> List[Dict[str, Any]]:
    """Load product catalog from JSON."""
    products_file = DATA_DIR / "products.json"
    with open(products_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_faq() -> List[Dict[str, Any]]:
    """Load FAQ from JSON."""
    faq_file = DATA_DIR / "faq.json"
    with open(faq_file, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_product(product: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert product into retrievable chunks.
    Each chunk is a focused piece of information.
    """
    chunks = []
    
    # Main product description chunk
    main_chunk = {
        "text": f"{product['product_name']} ({product['product_id']})\n"
                f"Category: {product['category']}\n"
                f"Price: ₹{product['price']}\n"
                f"{product['description']}\n"
                f"Best for: {product['best_for']}",
        "metadata": {
            "type": "product_overview",
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"]
        }
    }
    chunks.append(main_chunk)
    
    # Specifications chunk
    if "specifications" in product:
        specs_text = f"{product['product_name']} Specifications:\n"
        for key, value in product["specifications"].items():
            specs_text += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        specs_chunk = {
            "text": specs_text,
            "metadata": {
                "type": "product_specs",
                "product_id": product["product_id"],
                "product_name": product["product_name"]
            }
        }
        chunks.append(specs_chunk)
    
    # Warranty and shipping chunk
    policy_chunk = {
        "text": f"{product['product_name']} Purchase Information:\n"
                f"Warranty: {product.get('warranty', 'Not specified')}\n"
                f"Shipping: {product.get('shipping', 'Standard shipping')}\n"
                f"Return Policy: {product.get('return_policy', 'Standard returns')}\n"
                f"In Box: {product.get('in_box', 'Product and accessories')}",
        "metadata": {
            "type": "product_policy",
            "product_id": product["product_id"],
            "product_name": product["product_name"]
        }
    }
    chunks.append(policy_chunk)
    
    return chunks


def chunk_faq(faq_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert FAQ item into a retrievable chunk.
    """
    return {
        "text": f"Q: {faq_item['question']}\nA: {faq_item['answer']}",
        "metadata": {
            "type": "faq",
            "faq_id": faq_item["id"],
            "category": faq_item["category"],
            "question": faq_item["question"]
        }
    }


# Embeddings are handled automatically by ChromaDB's default embedding function
# No need for OpenAI API - uses sentence-transformers locally


def build_vector_store():
    """
    Main function to build the ChromaDB vector store.
    Uses ChromaDB's default embedding function (sentence-transformers) - no API key needed!
    """
    # Load data
    print("Loading knowledge base...")
    products = load_products()
    faqs = load_faq()
    
    # Create chunks
    print("Creating chunks...")
    all_chunks = []
    
    for product in products:
        all_chunks.extend(chunk_product(product))
    
    for faq in faqs:
        all_chunks.append(chunk_faq(faq))
    
    print(f"Created {len(all_chunks)} chunks")
    
    # Extract texts and metadata
    texts = [chunk["text"] for chunk in all_chunks]
    metadatas = [chunk["metadata"] for chunk in all_chunks]
    ids = [f"chunk_{i}" for i in range(len(all_chunks))]
    
    # Initialize ChromaDB
    print("Initializing ChromaDB...")
    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Use a simple CPU-only embedding function to avoid macOS CoreML issues
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Delete existing collection if it exists
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except Exception:
        pass
    
    # Create new collection with explicit embedding function
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"description": "eComBot knowledge base - products and FAQ"}
    )
    
    # Add documents to collection
    print("Adding documents to ChromaDB (embeddings generated automatically)...")
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas
    )
    
    print(f"✓ Successfully indexed {len(all_chunks)} chunks into {COLLECTION_NAME}")
    print(f"✓ ChromaDB location: {CHROMA_DIR}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_vector_store()
