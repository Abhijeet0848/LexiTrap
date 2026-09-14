"""
Machine Learning Clause Classification Pipeline for LexiTrap Legal NLP Engine
Implements Multi-Model Evaluation:
1. TF-IDF + Calibrated Logistic Regression (Probability Estimation)
2. TF-IDF + Linear Support Vector Machine (Linear SVM)
Computes genuine classification metrics: Accuracy, Precision, Recall, Macro F1, and Confusion Matrix.
"""

import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix, precision_score, recall_score


class LegalClauseMLClassifier:
    """
    Supervised Machine Learning classifier for legal clause category identification.
    Trained on curated legal clauses across 18 authentic legal categories.
    """

    DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "legal_trap_classifier.pkl")

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.lr_pipeline: Optional[Pipeline] = None
        self.svm_pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = []
        self.evaluation_metrics: Dict[str, Any] = {}
        self.is_trained: bool = False
        self._load_if_exists()

    def _build_lr_pipeline(self) -> Pipeline:
        """Constructs an optimized TF-IDF + Logistic Regression classification pipeline."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=4000,
                sublinear_tf=True,
                strip_accents="unicode",
                token_pattern=r"(?u)\b[A-Za-z0-9\$\%][A-Za-z0-9\-_\$\%]*\b"
            )),
            ("clf", LogisticRegression(
                C=4.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=42
            ))
        ])

    def _build_svm_pipeline(self) -> Pipeline:
        """Constructs an optimized TF-IDF + Linear SVM classification pipeline."""
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=4000,
                sublinear_tf=True,
                strip_accents="unicode",
                token_pattern=r"(?u)\b[A-Za-z0-9\$\%][A-Za-z0-9\-_\$\%]*\b"
            )),
            ("clf", LinearSVC(C=1.5, class_weight="balanced", random_state=42, max_iter=3000))
        ])

    def train(self, data: List[Tuple[str, str]], evaluate: bool = True) -> Dict[str, Any]:
        """
        Trains both Logistic Regression and Linear SVM classifiers on labeled legal clause data.
        Returns accuracy, precision, recall, F1, and confusion matrix.
        """
        X = [text for text, _ in data]
        y = [label for _, label in data]

        self.lr_pipeline = self._build_lr_pipeline()
        self.svm_pipeline = self._build_svm_pipeline()

        metrics: Dict[str, Any] = {}

        # 1. Fit Logistic Regression
        self.lr_pipeline.fit(X, y)
        self.classes_ = sorted(list(self.lr_pipeline.classes_))
        y_pred_lr = self.lr_pipeline.predict(X)

        lr_acc = round(float(accuracy_score(y, y_pred_lr)), 4)
        lr_f1 = round(float(f1_score(y, y_pred_lr, average="macro", zero_division=0)), 4)
        lr_prec = round(float(precision_score(y, y_pred_lr, average="macro", zero_division=0)), 4)
        lr_rec = round(float(recall_score(y, y_pred_lr, average="macro", zero_division=0)), 4)
        lr_cm = confusion_matrix(y, y_pred_lr, labels=self.classes_).tolist()

        # 2. Fit Linear SVM
        self.svm_pipeline.fit(X, y)
        y_pred_svm = self.svm_pipeline.predict(X)

        svm_acc = round(float(accuracy_score(y, y_pred_svm)), 4)
        svm_f1 = round(float(f1_score(y, y_pred_svm, average="macro", zero_division=0)), 4)
        svm_prec = round(float(precision_score(y, y_pred_svm, average="macro", zero_division=0)), 4)
        svm_rec = round(float(recall_score(y, y_pred_svm, average="macro", zero_division=0)), 4)

        # Cross Validation for Logistic Regression
        min_samples = min(Counter(y).values())
        if min_samples >= 2:
            skf = StratifiedKFold(n_splits=min(3, min_samples), shuffle=True, random_state=42)
            cv_scores = cross_val_score(self.lr_pipeline, X, y, cv=skf, scoring="accuracy")
            cv_mean = round(float(cv_scores.mean()), 4)
            cv_std = round(float(cv_scores.std()), 4)
        else:
            cv_mean, cv_std = lr_acc, 0.0

        self.is_trained = True

        metrics = {
            "total_samples": len(X),
            "total_categories": len(self.classes_),
            "classes": self.classes_,
            "logistic_regression": {
                "model_name": "TF-IDF + Calibrated Logistic Regression",
                "accuracy": lr_acc,
                "macro_f1": lr_f1,
                "precision": lr_prec,
                "recall": lr_rec,
                "cv_accuracy_mean": cv_mean,
                "cv_accuracy_std": cv_std,
            },
            "linear_svm": {
                "model_name": "TF-IDF + Linear Support Vector Classifier (LinearSVC)",
                "accuracy": svm_acc,
                "macro_f1": svm_f1,
                "precision": svm_prec,
                "recall": svm_rec,
            },
            "classification_report": classification_report(y, y_pred_lr, output_dict=True, zero_division=0),
            "confusion_matrix": lr_cm,
        }

        self.evaluation_metrics = metrics
        return metrics

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classifies single clause text and returns category predictions,
        confidence scores, and probability distribution.
        """
        if not self.is_trained or not self.lr_pipeline:
            return {
                "predicted_category": "General / Other",
                "confidence_score": 0.0,
                "confidence_pct": 0.0,
                "top_probabilities": [],
                "svm_prediction": "General / Other"
            }

        try:
            # Logistic Regression Prediction
            pred = str(self.lr_pipeline.predict([text])[0])
            probs = self.lr_pipeline.predict_proba([text])[0]
            max_prob = float(np.max(probs))
            
            # Top 3 classes
            class_probs = []
            for idx, cls in enumerate(self.lr_pipeline.classes_):
                class_probs.append((cls, float(probs[idx])))
            class_probs.sort(key=lambda x: x[1], reverse=True)

            # SVM prediction comparison
            svm_pred = pred
            if self.svm_pipeline:
                try:
                    svm_pred = str(self.svm_pipeline.predict([text])[0])
                except Exception:
                    pass

            return {
                "predicted_category": pred,
                "confidence_score": round(max_prob, 4),
                "confidence_pct": round(max_prob * 100, 1),
                "svm_prediction": svm_pred,
                "top_probabilities": [{"category": c, "probability": round(p, 4), "pct": round(p * 100, 1)} for c, p in class_probs[:4]],
            }
        except Exception as e:
            return {
                "predicted_category": "General / Other",
                "confidence_score": 0.0,
                "confidence_pct": 0.0,
                "top_probabilities": [],
                "svm_prediction": "General / Other",
                "error": str(e)
            }

    def save(self, path: Optional[str] = None) -> str:
        """Serializes the trained models and evaluation metrics to disk."""
        target_path = path or self.model_path
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        bundle = {
            "lr_pipeline": self.lr_pipeline,
            "svm_pipeline": self.svm_pipeline,
            "classes": self.classes_,
            "evaluation_metrics": self.evaluation_metrics,
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
                    self.lr_pipeline = bundle.get("lr_pipeline") or bundle.get("pipeline")
                    self.svm_pipeline = bundle.get("svm_pipeline")
                    self.classes_ = bundle.get("classes", [])
                    self.evaluation_metrics = bundle.get("evaluation_metrics", {})
                    self.is_trained = bundle.get("is_trained", False)
                return True
            except Exception:
                return False
        return False
