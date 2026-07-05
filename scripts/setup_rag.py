#!/usr/bin/env python3
"""
Quick start script for Day 05-06 RAG setup with PDF support
Run: python scripts/setup_rag.py
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.embed_catalog import build_vector_store


def main():
    print("="*70)
    print("eComBot Day 06 - RAG Setup with PDF Knowledge Base")
    print("="*70)
    print("\n✓ Using ChromaDB's built-in embeddings (no API key needed!)")
    
    # Step 1: Generate sample PDFs
    print("\n[Step 1/3] Generating sample PDF documents...")
    generate_script = PROJECT_ROOT / "scripts" / "generate_sample_pdfs.py"
    
    if generate_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(generate_script)],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"⚠ PDF generation had issues: {result.stderr}")
        except Exception as e:
            print(f"⚠ Could not generate PDFs: {e}")
    else:
        print("⚠ PDF generator script not found, skipping...")
    
    # Step 2: Build vector store
    print("\n[Step 2/3] Building ChromaDB vector store...")
    print("  - Indexing JSON data (products, FAQs)")
    print("  - Indexing PDF documents with metadata")
    
    try:
        build_vector_store()
    except Exception as e:
        print(f"\n✗ Vector store build failed: {e}")
        sys.exit(1)
    
    # Step 3: Run validation tests
    print("\n[Step 3/3] Running retrieval validation tests...")
    test_script = PROJECT_ROOT / "tests" / "test_pdf_rag.py"
    
    if test_script.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                cwd=str(PROJECT_ROOT)
            )
            if result.returncode != 0:
                print("\n⚠ Some tests had issues (see above)")
        except Exception as e:
            print(f"\n⚠ Could not run tests: {e}")
    else:
        print("⚠ Test script not found, skipping validation...")
    
    # Summary
    print("\n" + "="*70)
    print("✓ RAG SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run: python demo.py")
    print("2. Try direct queries:")
    print("   - 'What are the specs of the Dell XPS 15?'")
    print("   - 'What is your return policy?'")
    print("3. Try partial matches:")
    print("   - 'How long do I have to return something?'")
    print("4. Try out-of-scope:")
    print("   - 'What is the weather tomorrow?' (should refuse)")
    print("\nThe agent will:")
    print("  ✓ Answer from grounded context when available")
    print("  ✓ Show source metadata (file, page, section)")
    print("  ✓ Refuse to guess when answer is not in knowledge base")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
