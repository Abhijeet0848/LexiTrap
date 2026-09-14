"""
Phase 5 Unit & Integration Tests for LexiTrap Risk Detection & Context-Aware Scoring.
Verifies:
- Context-Aware Risk Contrast:
  Example A (Mutual + 30-day notice) vs Example B (Unilateral + No notice)
- Linguistic danger pattern extraction
- Scoring Ledger transparency (point breakdown)
- Structured explanations and balanced rewrite generation
- FastAPI /api/nlp/risk/audit-clause and /api/nlp/risk/audit-contract endpoints
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.nlp.risk_detector import (
    calculate_transparent_risk_score,
    extract_linguistic_signals,
    extract_mitigating_signals,
    determine_subject_symmetry,
    audit_clause_complete,
    audit_contract_document
)
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_context_aware_contrast():
    """
    Academic Requirement Step 14:
    Example A: Mutual + 30-day notice -> Low/Fair
    Example B: Unilateral provider + No notice -> High/Critical
    """
    example_a = "Either party may terminate the agreement at any time with 30 days written notice."
    example_b = "The provider may terminate the agreement at any time without notice."

    score_a = calculate_transparent_risk_score(example_a, "Termination")
    score_b = calculate_transparent_risk_score(example_b, "Termination")

    # Example B must be substantially riskier than Example A
    assert score_b["risk_score"] > score_a["risk_score"]
    assert score_a["risk_score"] <= 35
    assert score_b["risk_score"] >= 60

    assert score_a["symmetry"] == "MUTUAL"
    assert score_b["symmetry"] == "UNILATERAL"


def test_linguistic_signals_extraction():
    clause = "Provider reserves the right to modify these terms at any time without prior notice in its sole discretion."
    signals = extract_linguistic_signals(clause)
    
    phrases = [s["phrase"] for s in signals]
    assert "without notice" in phrases
    assert "at any time / at will" in phrases
    assert "sole discretion" in phrases

    for s in signals:
        assert "context" in s
        assert "reason" in s
        assert s["score_impact"] > 0


def test_transparent_scoring_ledger():
    clause = "The provider may immediately terminate this agreement at any time without notice."
    score_data = calculate_transparent_risk_score(clause, "Termination")
    
    assert "scoring_ledger" in score_data
    assert len(score_data["scoring_ledger"]) >= 3
    
    factors = [entry["factor"] for entry in score_data["scoring_ledger"]]
    assert "Baseline Contract Clause Neutrality" in factors
    assert "Absence of Advance Notice" in factors
    assert "Asymmetric Unilateral Right" in factors


def test_audit_clause_complete_and_rewrite():
    high_risk_clause = {
        "text": "Customer grants Provider a perpetual, irrevocable license to train commercial AI models on all Customer Data.",
        "category": "Intellectual Property"
    }
    result = audit_clause_complete(high_risk_clause)
    
    assert result["risk_level"] in {"HIGH", "CRITICAL"}
    assert result["risk_score"] >= 50
    assert "explanation" in result
    assert "recommendation" in result
    assert result["suggested_rewrite"] is not None
    assert "suggested_balanced_clause" in result["suggested_rewrite"]


def test_api_risk_audit_clause(client):
    payload = {
        "clause_text": "To the maximum extent permitted by law, Provider's total aggregate liability is capped at $50."
    }
    response = client.post("/api/nlp/risk/audit-clause", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["risk_level"] in {"HIGH", "CRITICAL"}
    assert "scoring_ledger" in data
    assert len(data["risk_signals"]) > 0


def test_api_risk_audit_contract(client):
    contract_text = """
    1. TERMINATION
    Provider may terminate this agreement at any time without notice.

    2. PAYMENT
    Customer shall pay within 30 days of invoice receipt.

    3. LIABILITY
    Total liability capped at $50.
    """
    response = client.post("/api/nlp/risk/audit-contract", json={"text": contract_text})
    assert response.status_code == 200
    data = response.json()
    
    assert "summary" in data
    assert data["summary"]["total_clauses"] == 3
    assert "risk_distribution" in data["summary"]
    assert "clauses" in data
    assert len(data["clauses"]) == 3
