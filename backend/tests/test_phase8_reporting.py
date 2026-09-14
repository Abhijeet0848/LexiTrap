"""
Phase 8 Unit & Integration Tests for LexiTrap Report Generation (PDF & Markdown).
Verifies:
- Markdown report string generation with sections and disclaimers
- ReportLab PDF byte stream generation
- FastAPI /api/analysis/report/markdown and /api/analysis/report/pdf endpoints
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.reporting.report_generator import generate_markdown_report, generate_pdf_report
from main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE_AUDIT_DATA = {
    "summary": {
        "total_clauses": 2,
        "average_risk_score": 52.5,
        "maximum_clause_risk_score": 85,
        "overall_grade": "CAUTION / MODERATE RISK",
        "overall_status": "Contract contains several noteworthy clauses requiring revision.",
        "risk_distribution": {"LOW": 1, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 1}
    },
    "clauses": [
        {
            "clause_id": "clause-1",
            "section_number": "1",
            "title": "Termination at Will",
            "text": "Provider may terminate this agreement at any time without notice.",
            "category": "Termination",
            "risk_score": 85,
            "risk_level": "CRITICAL",
            "symmetry": "UNILATERAL",
            "explanation": "Clause allows immediate unilateral termination.",
            "recommendation": "Request 30 days written notice.",
            "suggested_rewrite": {
                "suggested_balanced_clause": "Either party may terminate with 30 days written notice."
            }
        },
        {
            "clause_id": "clause-2",
            "section_number": "2",
            "title": "Payment Terms",
            "text": "Customer shall pay within 30 days.",
            "category": "Payment",
            "risk_score": 20,
            "risk_level": "LOW",
            "symmetry": "MUTUAL",
            "explanation": "Standard payment terms.",
            "recommendation": "No revision required.",
            "suggested_rewrite": None
        }
    ]
}


def test_markdown_report_generation():
    md = generate_markdown_report(SAMPLE_AUDIT_DATA)
    assert "# ⚖️ LexiTrap — Contract Risk & NLP Audit Report" in md
    assert "Executive Summary" in md
    assert "Termination at Will" in md
    assert "Academic Disclaimer" in md


def test_pdf_report_generation():
    pdf_bytes = generate_pdf_report(SAMPLE_AUDIT_DATA)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500  # Non-trivial PDF binary stream
    assert pdf_bytes.startswith(b"%PDF")


def test_api_download_markdown(client):
    payload = {"audit_data": SAMPLE_AUDIT_DATA}
    response = client.post("/api/analysis/report/markdown", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert "LexiTrap_Audit_Report.md" in response.headers["content-disposition"]
    assert "Termination at Will" in response.text


def test_api_download_pdf(client):
    payload = {"audit_data": SAMPLE_AUDIT_DATA}
    response = client.post("/api/analysis/report/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "LexiTrap_Audit_Report.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")
