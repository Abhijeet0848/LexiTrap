"""
Phase 3 Unit & Integration Tests for LexiTrap TF-IDF Engine.
Verifies:
- Manual Term Frequency (TF) calculation
- Inverse Document Frequency (IDF) smooth formula
- Mathematical formula tracing for academic viva
- Scikit-Learn TfidfVectorizer integration
- FastAPI /api/nlp/tfidf/analyze endpoint
"""

import sys
import os
import math
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.nlp.tfidf_engine import ManualTFIDF, SklearnTFIDFEngine, analyze_corpus_tfidf
from main import app


@pytest.fixture
def client():
    return TestClient(app)


SAMPLE_DOCS = [
    "The provider may terminate this agreement at any time without notice.",
    "Customer shall pay all invoice amounts within thirty days of billing.",
    "Provider's total liability shall not exceed fifty dollars under any circumstances.",
    "Customer shall indemnify and hold harmless provider against third-party claims."
]


def test_manual_tfidf_fitting():
    engine = ManualTFIDF(use_legal_stopwords=True)
    engine.fit(SAMPLE_DOCS)
    
    assert engine.corpus_size == 4
    assert len(engine.vocabulary) > 0
    # Check that legal keywords are in vocabulary
    assert "terminate" in engine.vocabulary or "notice" in engine.vocabulary
    assert "indemnify" in engine.vocabulary or "liability" in engine.vocabulary
    
    # Check IDF scores are positive
    for term, idf in engine.idf_scores.items():
        assert idf > 1.0


def test_manual_tfidf_transform_and_trace():
    engine = ManualTFIDF(use_legal_stopwords=True)
    engine.fit(SAMPLE_DOCS)
    
    res = engine.transform_single(SAMPLE_DOCS[0])
    assert "term_scores" in res
    assert "l2_normalized_vector" in res
    assert len(res["term_scores"]) > 0
    
    # Verify the mathematical trace is present
    top_entry = res["term_scores"][0]
    assert "formula_trace" in top_entry
    assert "TF(" in top_entry["formula_trace"]
    assert "IDF(" in top_entry["formula_trace"]


def test_sklearn_tfidf_engine():
    engine = SklearnTFIDFEngine(max_features=50, ngram_range=(1, 2))
    matrix, features = engine.fit_transform(SAMPLE_DOCS)
    
    assert matrix.shape[0] == 4
    assert len(features) > 0
    
    top_terms = engine.get_top_terms_for_document(SAMPLE_DOCS[0], top_k=3)
    assert len(top_terms) > 0
    assert "score" in top_terms[0]


def test_analyze_corpus_tfidf():
    result = analyze_corpus_tfidf(SAMPLE_DOCS)
    
    assert "academic_theory" in result
    assert "tf_formula" in result["academic_theory"]
    assert "limitations" in result["academic_theory"]
    assert result["total_documents"] == 4
    assert len(result["corpus_top_features"]) > 0
    assert len(result["clause_level_analysis"]) == 4


def test_api_tfidf_analyze_endpoint(client):
    payload = {
        "clauses": SAMPLE_DOCS
    }
    response = client.post("/api/nlp/tfidf/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_documents"] == 4
    assert "academic_theory" in data
    assert len(data["corpus_top_features"]) > 0
