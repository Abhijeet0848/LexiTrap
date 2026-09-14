"""
Phase 6 Unit & Integration Tests for LexiTrap Semantic NLP & Clause Similarity.
Verifies:
- Sentence Transformers Dense Embedding generation (384-dim)
- Cosine similarity computation
- Paraphrased synonymy demonstration (Step 16)
- Comparative clause imbalance detection (Step 17)
- Semantic candidate search & ranking
- Pairwise cosine matrix computation
- FastAPI /api/nlp/semantic/* endpoints
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.nlp.semantic_engine import (
    encode_texts,
    compute_cosine_similarity,
    compare_two_clauses,
    find_similar_clauses,
    compute_pairwise_similarity_matrix
)
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dense_embeddings_generation():
    texts = ["Payment is due within 30 days.", "Invoices must be paid in thirty days."]
    embeddings = encode_texts(texts)
    
    assert embeddings.shape[0] == 2
    assert embeddings.shape[1] == 384  # all-MiniLM-L6-v2 dimension


def test_paraphrased_semantic_similarity_step16():
    """
    Academic Requirement Step 16:
    Clause A: 'The provider may terminate the agreement without notice.'
    Clause B: 'The service provider can end the contract immediately without providing prior notification.'
    System must demonstrate high semantic similarity (> 70%) despite lexical differences.
    """
    clause_a = "The provider may terminate the agreement without notice."
    clause_b = "The service provider can end the contract immediately without providing prior notification."

    result = compare_two_clauses(clause_a, clause_b)
    
    assert result["semantic_similarity_percentage"] >= 70.0
    assert "High Semantic Equivalence" in result["semantic_verdict"]


def test_comparative_imbalance_analysis_step17():
    """
    Academic Requirement Step 17:
    Clause 5: 'Either party may terminate with 30 days' notice.'
    Clause 12: 'The provider may terminate immediately without notice.'
    System should identify difference in subject (Mutual vs Unilateral) and notice, flagging potential imbalance.
    """
    clause_5 = "Either party may terminate with 30 days' written notice."
    clause_12 = "The provider may terminate immediately without notice."

    result = compare_two_clauses(clause_5, clause_12)
    
    assert result["potential_imbalance_detected"] is True
    assert len(result["imbalance_findings"]) > 0
    assert result["clause_a"]["symmetry"] == "MUTUAL"
    assert result["clause_b"]["symmetry"] == "UNILATERAL"


def test_similar_clause_search():
    query = "Customer shall hold harmless and indemnify Provider against all third party claims."
    candidates = [
        {"text": "Customer agrees to defend, indemnify, and hold harmless Provider from losses.", "category": "Indemnification"},
        {"text": "Customer shall pay all undisputed invoice amounts within thirty days.", "category": "Payment"},
        {"text": "Provider warrants that the software will operate without material defect.", "category": "Warranty"}
    ]
    
    matches = find_similar_clauses(query, candidates, top_k=2)
    assert len(matches) == 2
    # The indemnification clause must be the top ranked match
    assert matches[0]["category"] == "Indemnification"
    assert matches[0]["similarity_percentage"] > matches[1]["similarity_percentage"]


def test_pairwise_similarity_matrix():
    clauses = [
        "Either party may terminate upon 30 days notice.",
        "Provider may terminate at will without notice.",
        "Payment is due in 30 days."
    ]
    matrix_data = compute_pairwise_similarity_matrix(clauses)
    
    assert matrix_data["num_clauses"] == 3
    assert len(matrix_data["matrix"]) == 3
    assert len(matrix_data["matrix"][0]) == 3
    # Diagonal must be 1.0 (self-similarity)
    for i in range(3):
        assert pytest.approx(matrix_data["matrix"][i][i], 0.01) == 1.0


def test_api_semantic_similarity_endpoint(client):
    payload = {
        "clause_a": "Either party may terminate with 30 days notice.",
        "clause_b": "Provider may terminate immediately without notice."
    }
    response = client.post("/api/nlp/semantic/similarity", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "semantic_similarity_percentage" in data
    assert data["potential_imbalance_detected"] is True


def test_api_semantic_search_endpoint(client):
    payload = {
        "query": "Provider disclaims all warranties including merchantability.",
        "top_k": 3
    }
    response = client.post("/api/nlp/semantic/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] <= 3
    assert len(data["matches"]) > 0
