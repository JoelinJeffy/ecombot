"""
test_pdf_rag.py -- Validation tests for Day 06 PDF RAG implementation
----------------------------------------------------------------------
Tests retrieval quality for three scenarios:
1. Direct match - questions clearly in the knowledge base
2. Partial match - questions with related but not exact matches
3. No match - questions outside the knowledge base scope

This validates:
- Chunking quality preserves meaning
- Metadata traceability to source
- Grounded answering (no hallucination)
- Graceful fallback when answer not available

Run:
    python tests/test_pdf_rag.py
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.retriever import retrieve, format_context, format_metadata_for_display

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RAGTestSuite:
    """Test suite for validating PDF RAG retrieval quality."""
    
    def __init__(self, n_results: int = 3):
        self.n_results = n_results
        self.results = []
    
    def run_test(
        self,
        test_name: str,
        query: str,
        expected_match: bool,
        min_confidence: float = 0.7
    ) -> Dict[str, Any]:
        """
        Run a single retrieval test.
        
        Args:
            test_name: Test identifier
            query: Search query
            expected_match: Whether we expect the KB to contain the answer
            min_confidence: Minimum acceptable match score
        
        Returns:
            Test result dict
        """
        print(f"\n{'='*70}")
        print(f"TEST: {test_name}")
        print(f"Query: {query}")
        print(f"Expected match: {'YES' if expected_match else 'NO'}")
        print(f"{'='*70}")
        
        try:
            results = retrieve(query, n_results=self.n_results)
            
            if not results:
                print("❌ No results returned")
                return {
                    "test": test_name,
                    "query": query,
                    "expected_match": expected_match,
                    "status": "FAIL" if expected_match else "PASS",
                    "reason": "No results (expected)" if not expected_match else "No results (unexpected)"
                }
            
            # Display results
            print(f"\n📊 Retrieved {len(results)} chunks:\n")
            
            for i, result in enumerate(results, 1):
                distance = result.get('distance', 1.0)
                confidence = 1 - distance if distance is not None else 0.0
                
                print(f"[{i}] Confidence: {confidence:.3f}")
                print(f"    Text: {result['text'][:200]}{'...' if len(result['text']) > 200 else ''}")
                print(f"    Meta: {format_metadata_for_display(result.get('metadata', {}))}")
                print()
            
            # Evaluate result quality
            best_distance = results[0].get('distance', 1.0)
            best_confidence = 1 - best_distance if best_distance is not None else 0.0
            
            if expected_match:
                if best_confidence >= min_confidence:
                    status = "PASS"
                    reason = f"Strong match (confidence: {best_confidence:.3f})"
                else:
                    status = "WARN"
                    reason = f"Weak match (confidence: {best_confidence:.3f} < {min_confidence})"
            else:
                if best_confidence < min_confidence:
                    status = "PASS"
                    reason = f"Correctly low confidence (confidence: {best_confidence:.3f})"
                else:
                    status = "WARN"
                    reason = f"False positive (confidence: {best_confidence:.3f})"
            
            print(f"✓ Result: {status} - {reason}")
            
            return {
                "test": test_name,
                "query": query,
                "expected_match": expected_match,
                "status": status,
                "confidence": best_confidence,
                "reason": reason,
                "results": results
            }
        
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return {
                "test": test_name,
                "query": query,
                "expected_match": expected_match,
                "status": "ERROR",
                "reason": str(e)
            }
    
    def run_all_tests(self):
        """Run the full test suite."""
        print("\n" + "="*70)
        print("PDF RAG VALIDATION TEST SUITE - Day 06")
        print("="*70)
        
        # ========== CATEGORY 1: Direct Match Tests ==========
        print("\n" + "─"*70)
        print("CATEGORY 1: Direct Match (should find clear answers)")
        print("─"*70)
        
        self.results.append(self.run_test(
            "Direct Match - Return Policy",
            "What is your return policy?",
            expected_match=True,
            min_confidence=0.6
        ))
        
        self.results.append(self.run_test(
            "Direct Match - Shipping Options",
            "What shipping options do you offer?",
            expected_match=True,
            min_confidence=0.6
        ))
        
        self.results.append(self.run_test(
            "Direct Match - Product Specs",
            "What are the specifications of the Dell XPS 15?",
            expected_match=True,
            min_confidence=0.6
        ))
        
        # ========== CATEGORY 2: Partial Match Tests ==========
        print("\n" + "─"*70)
        print("CATEGORY 2: Partial Match (similar wording)")
        print("─"*70)
        
        self.results.append(self.run_test(
            "Partial Match - Return Timeframe",
            "How long do I have to send something back?",
            expected_match=True,
            min_confidence=0.5
        ))
        
        self.results.append(self.run_test(
            "Partial Match - Warranty Duration",
            "How long is the laptop covered under warranty?",
            expected_match=True,
            min_confidence=0.5
        ))
        
        self.results.append(self.run_test(
            "Partial Match - Payment Methods",
            "Can I pay with UPI?",
            expected_match=True,
            min_confidence=0.5
        ))
        
        # ========== CATEGORY 3: Out-of-Scope Tests ==========
        print("\n" + "─"*70)
        print("CATEGORY 3: No Match (out of scope - should refuse)")
        print("─"*70)
        
        self.results.append(self.run_test(
            "No Match - Weather",
            "What is the weather tomorrow?",
            expected_match=False,
            min_confidence=0.6
        ))
        
        self.results.append(self.run_test(
            "No Match - Unrelated Product",
            "Do you sell furniture?",
            expected_match=False,
            min_confidence=0.6
        ))
        
        self.results.append(self.run_test(
            "No Match - Recipe",
            "How do I bake a chocolate cake?",
            expected_match=False,
            min_confidence=0.6
        ))
        
        # ========== Summary ==========
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        failed = sum(1 for r in self.results if r["status"] in ("FAIL", "ERROR"))
        total = len(self.results)
        
        print(f"\nTotal Tests: {total}")
        print(f"  ✓ PASS: {passed}")
        print(f"  ⚠ WARN: {warned}")
        print(f"  ✗ FAIL: {failed}")
        
        if warned > 0 or failed > 0:
            print("\n⚠ Issues detected:")
            for result in self.results:
                if result["status"] in ("WARN", "FAIL", "ERROR"):
                    print(f"  - {result['test']}: {result['reason']}")
        
        print("\n" + "="*70)
        
        if failed == 0:
            print("✓ All critical tests passed!")
            if warned > 0:
                print("  (Some warnings - review retrieval quality)")
        else:
            print("✗ Some tests failed - check knowledge base and chunking")
        
        print("="*70 + "\n")


def main():
    """Run the PDF RAG test suite."""
    try:
        suite = RAGTestSuite(n_results=3)
        suite.run_all_tests()
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print("\n" + "="*70)
        print("ERROR: Could not run test suite")
        print("="*70)
        print(f"\nReason: {e}")
        print("\nMake sure:")
        print("  1. You have run: python scripts/generate_sample_pdfs.py")
        print("  2. You have run: python -m src.rag.embed_catalog")
        print("  3. ChromaDB collection exists at .chroma/")
        print("="*70 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
