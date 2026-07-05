#!/usr/bin/env python3
"""
Quick start script for Day 05 RAG setup
Run: python scripts/setup_rag.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.rag.embed_catalog import build_vector_store


def main():
    print("="*70)
    print("eComBot Day 05 - RAG Setup")
    print("="*70)
    print("\n✓ Using ChromaDB's built-in embeddings (no API key needed!)")
    
    # Build vector store
    print("\nBuilding ChromaDB vector store...")
    try:
        build_vector_store()
        print("\n✓ RAG setup complete!")
        print("\nNext steps:")
        print("1. Run: python demo.py")
        print("2. Try: 'What are the specs of the Dell XPS 15?'")
        print("3. Try: 'What is your return policy?'")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
