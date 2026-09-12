"""
Machine Learning Trap Classifier Pipeline for LexiTrap Legal NLP Engine
Uses TF-IDF multi-gram vectorization with calibrated linear probability estimation
to detect predatory dark patterns and classify contract clauses.
"""

import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score


class LegalClauseMLClassifier:
    """
    Supervised Machine Learning classifier for legal clause risk identification.
    Trained on curated legal clauses across 8 predatory trap taxonomies and balanced baselines.
    """

    DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "legal_trap_classifier.pkl")

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = []
        self.is_trained: bool = False
        self._load_if_exists()

    def _build_pipeline(self) -> Pipeline:
        """Constructs an optimized NLP classification pipeline."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=5000,
                sublinear_tf=True,
                strip_accents="unicode",
                token_pattern=r"(?u)\b[A-Za-z0-9\$\%][A-Za-z0-9\-_\$\%]*\b"
            )),
            ("clf", LogisticRegression(
                C=5.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=42
            ))
        ])

    def train(self, data: List[Tuple[str, str]], evaluate: bool = True) -> Dict[str, Any]:
        """
        Trains the classifier on labeled legal clause data.
        Returns accuracy and evaluation metrics.
        """
        X = [text for text, _ in data]
        y = [label for _, label in data]

        self.pipeline = self._build_pipeline()
        
        metrics = {}
        if evaluate and len(X) >= 20:
            # 5-fold cross-validation
            skf = StratifiedKFold(n_splits=min(5, len(set(y))), shuffle=True, random_state=42)
            cv_scores = cross_val_score(self.pipeline, X, y, cv=skf, scoring="accuracy")
            metrics["cv_accuracy_mean"] = round(float(cv_scores.mean()), 4)
            metrics["cv_accuracy_std"] = round(float(cv_scores.std()), 4)

        # Fit full pipeline
        self.pipeline.fit(X, y)
        self.classes_ = list(self.pipeline.classes_)
        self.is_trained = True

        # In-sample metrics
        y_pred = self.pipeline.predict(X)
        metrics["train_accuracy"] = round(float(accuracy_score(y, y_pred)), 4)
        metrics["macro_f1"] = round(float(f1_score(y, y_pred, average="macro")), 4)
        metrics["classification_report"] = classification_report(y, y_pred, output_dict=True)
        metrics["total_samples"] = len(X)
        metrics["total_classes"] = len(self.classes_)

        return metrics

    def save(self, path: Optional[str] = None) -> str:
        """Serializes the trained pipeline and metadata to disk."""
        target_path = path or self.model_path
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        bundle = {
            "pipeline": self.pipeline,
            "classes": self.classes_,
            "is_trained": self.is_trained,
        }
        with open(target_path, "wb") as f:
            pickle.dump(bundle, f)
        
        return target_path

    def _load_if_exists(self) -> bool:
        """Loads a pre-trained model bundle from disk if available."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    bundle = pickle.load(f)
                    self.pipeline = bundle.get("pipeline")
                    self.classes_ = bundle.get("classes", [])
                    self.is_trained = bundle.get("is_trained", False)
                return True
            except Exception:
                self.is_trained = False
                return False
        return False

    def predict_clause(self, clause_text: str) -> Dict[str, Any]:
        """
        Predicts the trap category for a single clause with confidence scores.
        Returns top prediction, confidence (0.0 to 1.0), and full probability distribution.
        """
        if not self.is_trained or not self.pipeline:
            # Fallback when model not trained
            return {
                "predicted_category": "Safe / Balanced Standard",
                "confidence": 0.0,
                "is_trap": False,
                "probabilities": {}
            }

        probs = self.pipeline.predict_proba([clause_text])[0]
        prob_dict = {cls: round(float(p), 4) for cls, p in zip(self.classes_, probs)}
        
        top_idx = probs.argmax()
        top_class = self.classes_[top_idx]
        top_prob = round(float(probs[top_idx]), 4)
        
        is_trap = top_class != "Safe / Balanced Standard" and top_prob >= 0.35

        return {
            "predicted_category": top_class,
            "confidence": top_prob,
            "is_trap": is_trap,
            "probabilities": prob_dict
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Predicts risk categories for a list of clause texts."""
        return [self.predict_clause(t) for t in texts]
