"""
Phase 7 Unit & Integration Tests for LexiTrap Web Interface & Complete Pipeline.
Verifies:
- Frontend static asset and route serving
- Multi-route SPA responses (/, /analyze, /results, /nlp-analysis)
- End-to-end multi-phase pipeline flow
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_frontend_routes_serving(client):
    routes = ["/", "/analyze", "/results", "/nlp-analysis", "/history"]
    for r in routes:
        res = client.get(r)
        assert res.status_code == 200
        assert "LexiTrap" in res.text
        assert "<div id=\"root\"></div>" in res.text


def test_static_app_js_serving(client):
    res = client.get("/static/app.js")
    assert res.status_code == 200
    assert "SAMPLE_CONTRACTS" in res.text
    assert "runFullAnalysis" in res.text


def test_end_to_end_audit_flow(client):
    test_contract = """
    1. TERMINATION
    Provider may terminate this agreement at any time without notice.

    2. PAYMENT
    Customer shall pay $10,000 within 30 days.

    3. INDEMNIFICATION
    Customer shall defend and hold harmless Provider against all claims.
    """
    
    # 1. NLP Preprocessing
    nlp_res = client.post("/api/nlp/analyze", json={"text": test_contract})
    assert nlp_res.status_code == 200
    assert len(nlp_res.json()["tokens"]) > 0

    # 2. Clause Segmentation
    seg_res = client.post("/api/nlp/segment-clauses", json={"text": test_contract})
    assert seg_res.status_code == 200
    assert seg_res.json()["total_clauses"] == 3

    # 3. TF-IDF Analysis
    tf_res = client.post("/api/nlp/tfidf/analyze", json={"contract_text": test_contract})
    assert tf_res.status_code == 200
    assert tf_res.json()["total_documents"] == 3

    # 4. Contract Risk Audit
    risk_res = client.post("/api/nlp/risk/audit-contract", json={"text": test_contract})
    assert risk_res.status_code == 200
    audit_data = risk_res.json()
    assert "summary" in audit_data
    assert len(audit_data["clauses"]) == 3
