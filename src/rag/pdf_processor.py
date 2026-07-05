"""
pdf_processor.py -- PDF text extraction and intelligent chunking (Day 06)
--------------------------------------------------------------------------
Extracts text from PDF documents with page-level precision, performs
section-aware chunking with overlap, and enriches chunks with metadata
for traceability.

Key features:
- Page-by-page extraction with PyMuPDF
- Section detection using heading patterns
- Chunking with configurable overlap
- Rich metadata (source, page, section, doc_type)
- Preserves logical structure
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text, "metadata": self.metadata}


class PDFProcessor:
    """
    Intelligent PDF processor with section-aware chunking.
    
    Args:
        chunk_size: Target characters per chunk
        chunk_overlap: Overlap characters between chunks
        min_chunk_size: Minimum viable chunk size
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100
    ):
        if fitz is None:
            raise ImportError(
                "PyMuPDF (fitz) not installed. Install with: pip install pymupdf"
            )
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        
        # Heading patterns (title case or all caps, followed by content)
        self.heading_pattern = re.compile(
            r'^([A-Z][A-Za-z\s&\-]{3,50}[:\?]?)\s*$',
            re.MULTILINE
        )
    
    def extract_text_with_pages(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """
        Extract text page by page from PDF.
        
        Returns:
            List of dicts with 'page_num' and 'text'
        """
        pages = []
        
        try:
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Clean up excessive whitespace
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = text.strip()
                
                if text:  # Only include non-empty pages
                    pages.append({
                        "page_num": page_num + 1,
                        "text": text
                    })
            
            doc.close()
            logger.info(f"Extracted {len(pages)} pages from {pdf_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise
        
        return pages
    
    def detect_sections(self, text: str) -> List[tuple]:
        """
        Detect section boundaries in text using heading patterns.
        
        Returns:
            List of (section_title, start_pos, end_pos) tuples
        """
        sections = []
        matches = list(self.heading_pattern.finditer(text))
        
        for i, match in enumerate(matches):
            section_title = match.group(1).strip()
            start_pos = match.start()
            
            # End position is start of next section or end of text
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            sections.append((section_title, start_pos, end_pos))
        
        return sections
    
    def chunk_text_with_overlap(
        self,
        text: str,
        section_name: Optional[str] = None
    ) -> List[str]:
        """
        Split text into overlapping chunks, respecting paragraph boundaries.
        
        Args:
            text: Text to chunk
            section_name: Optional section name for context
        
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap from previous chunk
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out tiny chunks
        chunks = [c for c in chunks if len(c) >= self.min_chunk_size]
        
        return chunks
    
    def process_pdf(
        self,
        pdf_path: Path,
        document_title: Optional[str] = None,
        doc_type: str = "pdf"
    ) -> List[TextChunk]:
        """
        Extract, chunk, and enrich PDF content with metadata.
        
        Args:
            pdf_path: Path to PDF file
            document_title: Override document title (default: filename)
            doc_type: Document type for metadata
        
        Returns:
            List of TextChunk objects with metadata
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        doc_title = document_title or pdf_path.stem
        pages = self.extract_text_with_pages(pdf_path)
        
        all_chunks = []
        chunk_id = 0
        
        for page_data in pages:
            page_num = page_data["page_num"]
            page_text = page_data["text"]
            
            # Detect sections within page
            sections = self.detect_sections(page_text)
            
            if sections:
                # Process each section separately
                for section_title, start_pos, end_pos in sections:
                    section_text = page_text[start_pos:end_pos].strip()
                    text_chunks = self.chunk_text_with_overlap(section_text, section_title)
                    
                    for chunk_text in text_chunks:
                        chunk = TextChunk(
                            text=chunk_text,
                            metadata={
                                "source_file": pdf_path.name,
                                "document_title": doc_title,
                                "section": section_title,
                                "page": page_num,
                                "doc_type": doc_type,
                                "chunk_id": chunk_id
                            }
                        )
                        all_chunks.append(chunk)
                        chunk_id += 1
            else:
                # No clear sections, chunk entire page
                text_chunks = self.chunk_text_with_overlap(page_text)
                
                for chunk_text in text_chunks:
                    chunk = TextChunk(
                        text=chunk_text,
                        metadata={
                            "source_file": pdf_path.name,
                            "document_title": doc_title,
                            "section": f"Page {page_num}",
                            "page": page_num,
                            "doc_type": doc_type,
                            "chunk_id": chunk_id
                        }
                    )
                    all_chunks.append(chunk)
                    chunk_id += 1
        
        logger.info(
            f"Processed {pdf_path.name}: {len(pages)} pages → {len(all_chunks)} chunks"
        )
        
        return all_chunks


def process_pdf_file(
    pdf_path: Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Convenience function to process a PDF file.
    
    Args:
        pdf_path: Path to PDF
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        **kwargs: Additional arguments for process_pdf
    
    Returns:
        List of chunk dictionaries
    """
    processor = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = processor.process_pdf(pdf_path, **kwargs)
    return [chunk.to_dict() for chunk in chunks]


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    test_pdf = Path("data/ecom_faq.pdf")
    if test_pdf.exists():
        chunks = process_pdf_file(test_pdf)
        print(f"\nProcessed {len(chunks)} chunks")
        print("\nFirst chunk:")
        print(chunks[0])
    else:
        print(f"Test PDF not found: {test_pdf}")
