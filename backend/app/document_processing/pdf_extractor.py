"""
PDF Text Extraction Module for LexiTrap.
Uses PyMuPDF for high-performance, layout-aware legal document text extraction.
"""

import io
from typing import Dict, Any, Union
import pymupdf


def extract_text_from_pdf(
    file_input: Union[str, bytes, io.BytesIO]
) -> Dict[str, Any]:
    """
    Extracts text, page count, and structural metadata from a PDF file or bytes stream.
    
    Academic Rationale:
    Legal contracts distributed as PDFs frequently contain multi-page headers, footers,
    page numbers, and columnar text. PyMuPDF extracts text blocks in reading order while
    maintaining paragraph breaks.
    """
    if isinstance(file_input, (bytes, bytearray)):
        doc = pymupdf.open(stream=file_input, filetype="pdf")
    elif isinstance(file_input, io.BytesIO):
        doc = pymupdf.open(stream=file_input.getvalue(), filetype="pdf")
    elif isinstance(file_input, str):
        doc = pymupdf.open(file_input)
    else:
        raise ValueError("Invalid PDF input. Must be filepath string, bytes, or BytesIO.")

    page_texts = []
    total_pages = len(doc)
    
    metadata = {
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "page_count": total_pages
    }

    full_text_parts = []
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            page_texts.append({
                "page_number": page_num + 1,
                "text": text.strip()
            })
            full_text_parts.append(text.strip())

    doc.close()
    
    combined_text = "\n\n".join(full_text_parts)
    
    return {
        "text": combined_text,
        "page_count": total_pages,
        "pages": page_texts,
        "metadata": metadata,
        "extraction_method": "PyMuPDF"
    }
