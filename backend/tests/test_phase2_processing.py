"""
Phase 2 Unit & Integration Tests for LexiTrap Document Processing & Clause Segmentation.
Verifies:
- PDF extraction via PyMuPDF
- DOCX extraction via OpenXML zipfile parser
- Clause segmentation across the 16 legal categories
- FastAPI /api/document/extract and /api/nlp/segment-clauses endpoints
"""

import sys
import os
import io
import zipfile
import pytest
import pymupdf
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.document_processing.pdf_extractor import extract_text_from_pdf
from app.document_processing.docx_extractor import extract_text_from_docx
from app.nlp.clause_segmentation import segment_contract_into_clauses, LEGAL_CATEGORIES
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def create_in_memory_pdf(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), text)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def create_in_memory_docx_archive(paragraphs: list) -> bytes:
    """Creates a valid minimal in-memory OpenXML docx archive."""
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as zf:
        # Minimal document.xml
        p_xmls = []
        for p in paragraphs:
            p_xmls.append(
                f'<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f'<w:r><w:t>{p}</w:t></w:r>'
                f'</w:p>'
            )
        doc_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body>'
            + "".join(p_xmls) +
            '</w:body>'
            '</w:document>'
        )
        zf.writestr("word/document.xml", doc_xml.encode("utf-8"))
        zf.writestr("[Content_Types].xml", b'<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
    return stream.getvalue()


SAMPLE_CONTRACT_TEXT = """
1. TERMINATION
The service provider may terminate this agreement at any time without prior written notice to the customer.

2. PAYMENT TERMS
Customer shall pay all undisputed invoice amounts within 30 days of receipt. Late payments shall incur 1.5% interest per month.

3. LIMITATION OF LIABILITY
In no event shall provider's aggregate liability exceed $50 or the fees paid in the prior month, whichever is less.

4. INDEMNIFICATION
Customer agrees to defend, indemnify, and hold harmless Provider from any third-party claims arising out of Customer's use of the service.

5. CONFIDENTIALITY
Each party agrees to maintain the proprietary information of the disclosing party in strict confidence.
"""


def test_pdf_extraction():
    test_text = "Master Services Agreement\nSection 1. Payment shall be due within 30 days."
    pdf_bytes = create_in_memory_pdf(test_text)
    result = extract_text_from_pdf(pdf_bytes)
    
    assert "Master Services Agreement" in result["text"]
    assert "Payment shall be due" in result["text"]
    assert result["page_count"] == 1
    assert "PyMuPDF" in result["extraction_method"]


def test_docx_extraction():
    paragraphs = [
        "Software License Agreement",
        "Section 1. Provider grants Customer a non-exclusive license.",
        "Section 2. Either party may terminate with 30 days notice."
    ]
    docx_bytes = create_in_memory_docx_archive(paragraphs)
    result = extract_text_from_docx(docx_bytes)
    
    assert "Software License Agreement" in result["text"]
    assert "non-exclusive license" in result["text"]
    assert result["paragraph_count"] == 3
    assert "OpenXML" in result["extraction_method"]


def test_clause_segmentation():
    clauses = segment_contract_into_clauses(SAMPLE_CONTRACT_TEXT)
    
    assert len(clauses) >= 5
    categories = [c["category"] for c in clauses]
    
    assert "Termination" in categories
    assert "Payment" in categories
    assert "Liability" in categories
    assert "Indemnification" in categories
    assert "Confidentiality" in categories

    for c in clauses:
        assert "clause_id" in c
        assert "title" in c
        assert "text" in c
        assert "sentence_count" in c
        assert c["sentence_count"] >= 1


def test_api_document_extract_txt(client):
    file_bytes = SAMPLE_CONTRACT_TEXT.encode("utf-8")
    response = client.post(
        "/api/document/extract",
        files={"file": ("contract.txt", file_bytes, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "TERMINATION" in data["text"]
    assert data["file_type"] == "PLAIN_TEXT"


def test_api_document_extract_pdf(client):
    pdf_bytes = create_in_memory_pdf(SAMPLE_CONTRACT_TEXT)
    response = client.post(
        "/api/document/extract",
        files={"file": ("contract.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "TERMINATION" in data["text"]
    assert data["file_type"] == "PDF"


def test_api_document_extract_docx(client):
    paragraphs = ["Master Cloud Services Agreement", "Section 1. Payment due within 30 days."]
    docx_bytes = create_in_memory_docx_archive(paragraphs)
    response = client.post(
        "/api/document/extract",
        files={"file": ("contract.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Master Cloud Services Agreement" in data["text"]
    assert data["file_type"] == "DOCX"


def test_api_segment_clauses(client):
    payload = {"text": SAMPLE_CONTRACT_TEXT}
    response = client.post("/api/nlp/segment-clauses", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_clauses"] >= 5
    assert "Termination" in data["categories_found"]
    assert "Liability" in data["categories_found"]
    assert len(data["available_categories"]) == 16
