"""
Phase 1 Unit & Integration Tests for LexiTrap NLP Pipeline.
Verifies:
- Text Cleaning & Non-destructive representation
- Tokenization (words and punctuation)
- Sentence Segmentation
- Legal-aware stopword handling (preserving 'shall', 'may', 'must', 'without', 'unless')
- Lemmatization (base form reduction)
- POS tagging & Modal verb extraction
- Named Entity Recognition (ORG, MONEY, DATE)
- FastAPI /api/nlp/analyze endpoint response structure
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.nlp.preprocessing import (
    clean_text,
    segment_sentences,
    tokenize_text,
    handle_stopwords,
    lemmatize_text,
    pos_tag_text,
    extract_named_entities,
    run_nlp_pipeline,
    LEGAL_PRESERVED_KEYWORDS
)
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_text_cleaning():
    raw_text = "  The   provider   may terminate \r\n\r\n\r\n this agreement at any time.   "
    res = clean_text(raw_text)
    assert res["original"] == raw_text
    assert res["cleaned"] == "The provider may terminate \n\n this agreement at any time."


def test_sentence_segmentation():
    text = "The customer shall pay the fees. The provider may terminate the agreement."
    sentences = segment_sentences(text)
    assert len(sentences) == 2
    assert sentences[0] == "The customer shall pay the fees."
    assert sentences[1] == "The provider may terminate the agreement."


def test_tokenization():
    text = "The customer shall pay the fees within 30 days."
    tokens = tokenize_text(text)
    assert "The" in tokens
    assert "customer" in tokens
    assert "shall" in tokens
    assert "30" in tokens
    assert "days" in tokens


def test_legal_stopword_preservation():
    text = "The vendor shall not terminate the contract without 30 days notice unless in breach."
    tokens = tokenize_text(text)
    res = handle_stopwords(tokens, preserve_legal_keywords=True)
    
    # In legal NLP, 'shall', 'not', 'without', 'unless' must be preserved
    preserved = [t.lower() for t in res["legal_aware_filtered_tokens"]]
    assert "shall" in preserved
    assert "not" in preserved
    assert "without" in preserved
    assert "unless" in preserved
    
    # Check that generic filler stopwords like 'the' were removed
    assert "the" not in preserved


def test_lemmatization():
    text = "The parties are terminating agreements and terminating obligations."
    lemmas = lemmatize_text(text)
    lemma_map = {item["token"]: item["lemma"] for item in lemmas}
    
    assert lemma_map.get("terminating") == "terminate"
    assert lemma_map.get("agreements") == "agreement"
    assert lemma_map.get("obligations") == "obligation"


def test_pos_tagging_and_modals():
    text = "ABC Corp shall pay all fees, and Customer may terminate immediately."
    pos_data = pos_tag_text(text)
    
    modals = [m["token"].lower() for m in pos_data["modal_verbs"]]
    assert "shall" in modals
    assert "may" in modals
    
    assert "NOUN" in pos_data["summary"] or "PROPN" in pos_data["summary"]
    assert "VERB" in pos_data["summary"] or "AUX" in pos_data["summary"]


def test_named_entity_recognition():
    text = "Acme Technologies LLC shall pay $50,000 to John Doe within 30 days in New York."
    entities = extract_named_entities(text)
    
    labels = {e["label"] for e in entities}
    assert "MONEY" in labels
    
    entity_texts = [e["text"] for e in entities]
    assert any("$50,000" in t for t in entity_texts)


def test_fastapi_analyze_endpoint(client):
    payload = {
        "text": "Acme Inc. shall pay $100,000 annually. The provider may terminate this agreement at any time without notice."
    }
    response = client.post("/api/nlp/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "original_text" in data
    assert "cleaned_text" in data
    assert "statistics" in data
    assert len(data["sentences"]) == 2
    assert len(data["tokens"]) > 0
    assert len(data["filtered_tokens"]) > 0
    assert len(data["lemmas"]) > 0
    assert len(data["pos_tags"]) > 0
    assert len(data["modal_verbs"]) >= 2  # 'shall' and 'may'
    assert len(data["entities"]) > 0      # Acme Inc., $100,000, etc.


def test_empty_input_validation(client):
    response = client.post("/api/nlp/analyze", json={"text": "   "})
    assert response.status_code == 400
