"""
Phase 4 Unit & Integration Tests for LexiTrap Machine Learning & Clause Classification.
Verifies:
- Dataset loading and structure
- 80/20 train/test evaluation
- Logistic Regression vs Linear SVM metrics (Accuracy, Precision, Recall, F1, Confusion Matrix)
- Single clause prediction with confidence scores
- FastAPI /api/ml/evaluation and /api/ml/predict endpoints
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ml.classifier import ClauseClassificationEngine, ml_engine
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dataset_loading():
    df = ml_engine.load_dataset()
    assert len(df) >= 30
    assert "text" in df.columns
    assert "category" in df.columns
    assert "risk_level" in df.columns


def test_model_training_and_evaluation_report():
    report = ml_engine.train_and_evaluate(test_size=0.20, random_state=42)
    
    assert "dataset_statistics" in report
    assert "model_1_logistic_regression" in report
    assert "model_2_linear_svm" in report
    assert "comparison_summary" in report

    lr = report["model_1_logistic_regression"]
    svm = report["model_2_linear_svm"]

    # Check metrics are valid floats between 0 and 1
    assert 0.0 <= lr["accuracy"] <= 1.0
    assert 0.0 <= lr["f1_weighted"] <= 1.0
    assert 0.0 <= svm["accuracy"] <= 1.0
    assert 0.0 <= svm["f1_weighted"] <= 1.0

    # Check confusion matrix dimensions
    num_classes = report["dataset_statistics"]["total_categories"]
    assert len(lr["confusion_matrix"]) == num_classes
    assert len(svm["confusion_matrix"]) == num_classes


def test_clause_prediction_inference():
    test_clause = "Provider may terminate this agreement immediately without prior notice."
    result = ml_engine.predict_clause(test_clause)
    
    assert "predicted_category" in result
    assert result["predicted_category"] == "Termination"
    assert "confidence_score" in result
    assert 0.0 <= result["confidence_score"] <= 1.0
    assert len(result["top_probabilities"]) > 0


def test_api_ml_evaluation_endpoint(client):
    response = client.get("/api/ml/evaluation")
    assert response.status_code == 200
    data = response.json()
    
    assert "model_1_logistic_regression" in data
    assert "model_2_linear_svm" in data
    assert "comparison_summary" in data


def test_api_ml_predict_endpoint(client):
    payload = {
        "clause_text": "Customer shall indemnify and defend Provider against all third-party IP claims."
    }
    response = client.post("/api/ml/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["predicted_category"] == "Indemnification"
    assert "confidence_score" in data
    assert "top_probabilities" in data
