"""
Machine Learning Clause Classifier & Academic Model Evaluation Module for LexiTrap.
Implements:
1. TF-IDF + Logistic Regression Classifier (Model 1)
2. TF-IDF + Linear SVM Classifier (Model 2)
3. 80/20 Train-Test Split with Stratification
4. Comprehensive Model Evaluation:
   - Accuracy, Precision (Macro/Weighted), Recall (Macro/Weighted), F1-Score (Macro/Weighted)
   - Labeled Confusion Matrix & Per-Class Classification Report
5. Comparative Theoretical Analysis for Academic Viva
"""

import os
import csv
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

DEFAULT_DATASET_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "dataset", "clauses.csv")
)


class ClauseClassificationEngine:
    """
    Academic Machine Learning Engine evaluating and comparing Logistic Regression vs Linear SVM
    on TF-IDF text features for 16-category legal clause classification.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = dataset_path or DEFAULT_DATASET_PATH
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words='english',
            min_df=1
        )
        self.lr_model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        self.svm_model = LinearSVC(C=1.0, random_state=42)
        
        self.classes_: List[str] = []
        self.is_trained: bool = False
        self.evaluation_report: Dict[str, Any] = {}
        
        # Automatically train and evaluate on initialization if dataset exists
        if os.path.exists(self.dataset_path):
            self.train_and_evaluate()

    def load_dataset(self) -> pd.DataFrame:
        """Loads and validates the clause classification dataset."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset file not found at: {self.dataset_path}")
            
        df = pd.read_csv(self.dataset_path)
        if "text" not in df.columns or "category" not in df.columns:
            raise ValueError("Dataset must contain 'text' and 'category' columns.")
        return df.dropna(subset=["text", "category"])

    def train_and_evaluate(self, test_size: float = 0.20, random_state: int = 42) -> Dict[str, Any]:
        """
        Executes an 80/20 train/test split, trains both classifiers, and computes
        full academic evaluation metrics and confusion matrices.
        """
        df = self.load_dataset()
        X_raw = df["text"].values
        y_raw = df["category"].values

        self.classes_ = sorted(list(set(y_raw)))

        # Check if stratification is mathematically feasible across all classes
        from collections import Counter
        class_counts = Counter(y_raw)
        min_class_count = min(class_counts.values()) if class_counts else 0
        can_stratify = min_class_count >= 2 and (len(y_raw) * test_size) >= len(self.classes_)

        # 80/20 Train-Test split
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_raw, y_raw,
            test_size=test_size,
            random_state=random_state,
            stratify=y_raw if can_stratify else None
        )

        # TF-IDF Feature Extraction
        X_train_vec = self.vectorizer.fit_transform(X_train_raw)
        X_test_vec = self.vectorizer.transform(X_test_raw)

        # 1. Train Model 1: Logistic Regression
        self.lr_model.fit(X_train_vec, y_train)
        y_pred_lr = self.lr_model.predict(X_test_vec)

        # 2. Train Model 2: Linear SVM
        self.svm_model.fit(X_train_vec, y_train)
        y_pred_svm = self.svm_model.predict(X_test_vec)

        # Evaluate Model 1 (Logistic Regression)
        lr_acc = float(accuracy_score(y_test, y_pred_lr))
        lr_prec_macro = float(precision_score(y_test, y_pred_lr, average="macro", zero_division=0))
        lr_prec_weighted = float(precision_score(y_test, y_pred_lr, average="weighted", zero_division=0))
        lr_rec_macro = float(recall_score(y_test, y_pred_lr, average="macro", zero_division=0))
        lr_rec_weighted = float(recall_score(y_test, y_pred_lr, average="weighted", zero_division=0))
        lr_f1_macro = float(f1_score(y_test, y_pred_lr, average="macro", zero_division=0))
        lr_f1_weighted = float(f1_score(y_test, y_pred_lr, average="weighted", zero_division=0))
        lr_cm = confusion_matrix(y_test, y_pred_lr, labels=self.classes_).tolist()

        # Evaluate Model 2 (Linear SVM)
        svm_acc = float(accuracy_score(y_test, y_pred_svm))
        svm_prec_macro = float(precision_score(y_test, y_pred_svm, average="macro", zero_division=0))
        svm_prec_weighted = float(precision_score(y_test, y_pred_svm, average="weighted", zero_division=0))
        svm_rec_macro = float(recall_score(y_test, y_pred_svm, average="macro", zero_division=0))
        svm_rec_weighted = float(recall_score(y_test, y_pred_svm, average="weighted", zero_division=0))
        svm_f1_macro = float(f1_score(y_test, y_pred_svm, average="macro", zero_division=0))
        svm_f1_weighted = float(f1_score(y_test, y_pred_svm, average="weighted", zero_division=0))
        svm_cm = confusion_matrix(y_test, y_pred_svm, labels=self.classes_).tolist()

        # Academic Comparative Commentary
        better_model = "Linear SVM" if svm_f1_weighted >= lr_f1_weighted else "Logistic Regression"
        comparative_analysis = (
            f"In our benchmark evaluation, {better_model} achieved superior or competitive generalization on the "
            f"test set (SVM F1: {svm_f1_weighted:.3f} vs LR F1: {lr_f1_weighted:.3f}). "
            f"Linear SVM optimizes the maximum margin hyperplane between high-dimensional sparse TF-IDF text features, "
            f"making it robust against sparse contract vocabulary. Logistic Regression produces well-calibrated posterior "
            f"probabilities P(Category|Text), offering interpretability for confidence scoring."
        )

        self.is_trained = True
        self.evaluation_report = {
            "dataset_statistics": {
                "total_samples": len(df),
                "training_samples": len(X_train_raw),
                "testing_samples": len(X_test_raw),
                "split_ratio": f"{int((1 - test_size) * 100)}% Train / {int(test_size * 100)}% Test",
                "total_categories": len(self.classes_),
                "vocabulary_features_extracted": len(self.vectorizer.get_feature_names_out()),
                "classes": self.classes_
            },
            "model_1_logistic_regression": {
                "name": "TF-IDF + Multinomial Logistic Regression",
                "accuracy": round(lr_acc, 4),
                "precision_macro": round(lr_prec_macro, 4),
                "precision_weighted": round(lr_prec_weighted, 4),
                "recall_macro": round(lr_rec_macro, 4),
                "recall_weighted": round(lr_rec_weighted, 4),
                "f1_macro": round(lr_f1_macro, 4),
                "f1_weighted": round(lr_f1_weighted, 4),
                "confusion_matrix": lr_cm
            },
            "model_2_linear_svm": {
                "name": "TF-IDF + Linear Support Vector Machine (LinearSVC)",
                "accuracy": round(svm_acc, 4),
                "precision_macro": round(svm_prec_macro, 4),
                "precision_weighted": round(svm_prec_weighted, 4),
                "recall_macro": round(svm_rec_macro, 4),
                "recall_weighted": round(svm_rec_weighted, 4),
                "f1_macro": round(svm_f1_macro, 4),
                "f1_weighted": round(svm_f1_weighted, 4),
                "confusion_matrix": svm_cm
            },
            "comparison_summary": {
                "preferred_model": better_model,
                "academic_rationale": comparative_analysis
            }
        }

        return self.evaluation_report

    def predict_clause(self, clause_text: str) -> Dict[str, Any]:
        """
        Classifies a single clause text using both trained models and returns probability distributions.
        """
        if not self.is_trained:
            self.train_and_evaluate()

        vec = self.vectorizer.transform([clause_text])

        # Logistic Regression Prediction & Probabilities
        lr_pred = self.lr_model.predict(vec)[0]
        lr_probs = self.lr_model.predict_proba(vec)[0]
        
        # Sort top 3 probabilities
        prob_dist = []
        for class_name, prob in zip(self.lr_model.classes_, lr_probs):
            prob_dist.append({"category": class_name, "probability": round(float(prob), 4)})
        prob_dist.sort(key=lambda x: x["probability"], reverse=True)

        # SVM Prediction & Decision Function Margin
        svm_pred = self.svm_model.predict(vec)[0]
        confidence_score = float(prob_dist[0]["probability"]) if prob_dist else 0.5

        return {
            "predicted_category": str(lr_pred),
            "svm_predicted_category": str(svm_pred),
            "confidence_score": confidence_score,
            "models_agree": bool(lr_pred == svm_pred),
            "top_probabilities": prob_dist[:3],
            "model_used": "TF-IDF + Logistic Regression & Linear SVM Ensemble"
        }


# Global instance for shared API usage
ml_engine = ClauseClassificationEngine()
