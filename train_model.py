#!/usr/bin/env python3
"""
LexiTrap Model Training Script
Trains, evaluates, and exports the Machine Learning classifiers:
1. TF-IDF + Calibrated Logistic Regression
2. TF-IDF + Linear Support Vector Machine (Linear SVM)
"""

import os
import sys
import time

# Ensure root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nlp_engine.training_data import TRAINING_DATA
from nlp_engine.ml_classifier import LegalClauseMLClassifier


def train():
    print("=" * 75)
    print("   LEXITRAP MACHINE LEARNING MODEL TRAINER (LR & LINEAR SVM)")
    print("=" * 75)
    print(f"[*] Dataset Size: {len(TRAINING_DATA)} labeled clauses across 13 distinct legal categories")
    
    start_time = time.time()
    classifier = LegalClauseMLClassifier()
    
    print("[*] Training TF-IDF Multi-Gram + Calibrated Logistic Regression & Linear SVM...")
    metrics = classifier.train(TRAINING_DATA, evaluate=True)
    
    elapsed = time.time() - start_time
    print(f"[+] Training and cross-validation completed in {elapsed:.3f} seconds\n")
    
    lr_m = metrics["logistic_regression"]
    svm_m = metrics["linear_svm"]

    print("-" * 75)
    print("MODEL PERFORMANCE COMPARISON (LOGISTIC REGRESSION VS. LINEAR SVM)")
    print("-" * 75)
    print(f"{'Metric':<30} {'Logistic Regression':<22} {'Linear SVM':<20}")
    print("-" * 75)
    print(f"{'Train Accuracy':<30} {lr_m['accuracy'] * 100:>18.2f}% {svm_m['accuracy'] * 100:>18.2f}%")
    print(f"{'Macro F1-Score':<30} {lr_m['macro_f1']:>19.4f} {svm_m['macro_f1']:>19.4f}")
    print(f"{'Macro Precision':<30} {lr_m['precision']:>19.4f} {svm_m['precision']:>19.4f}")
    print(f"{'Macro Recall':<30} {lr_m['recall']:>19.4f} {svm_m['recall']:>19.4f}")
    if "cv_accuracy_mean" in lr_m:
        print(f"{'4-Fold CV Accuracy':<30} {lr_m['cv_accuracy_mean'] * 100:>18.2f}% {'N/A':>19}")
    print(f"{'Total Categories':<30} {metrics['total_categories']:>19} {metrics['total_categories']:>19}")
    print(f"{'Total Samples':<30} {metrics['total_samples']:>19} {metrics['total_samples']:>19}\n")

    print("-" * 75)
    print("PER-CATEGORY CLASSIFICATION REPORT (LOGISTIC REGRESSION)")
    print("-" * 75)
    print(f"{'Category':<42} {'Precision':<10} {'Recall':<10} {'F1-Score':<10}")
    print("-" * 75)
    
    rep = metrics.get("classification_report", {})
    for cat, scores in rep.items():
        if isinstance(scores, dict):
            p = scores.get("precision", 0)
            r = scores.get("recall", 0)
            f1 = scores.get("f1-score", 0)
            print(f"{cat:<42} {p:>8.2f}   {r:>8.2f}   {f1:>8.2f}")

    # Save model artifact
    save_path = classifier.save()
    print("-" * 75)
    print(f"[OK] Multi-Model artifacts successfully saved to:")
    print(f"     {save_path}")
    print("=" * 75)

    # Run quick validation on unseen test clauses
    print("\nINFERENCE TEST ON SAMPLE CLAUSES:")
    test_samples = [
        "We reserve the right to amend our subscription pricing and policies at any time without notice.",
        "Under no circumstances shall company liability exceed fifty dollars ($50.00).",
        "Each party agrees to mutual indemnification capped at 12 months fees with carveouts.",
        "You waive all right to a jury trial and agree to individual binding arbitration in Delaware.",
        "Either party may terminate this agreement upon providing 30 days prior written notice."
    ]

    for sample in test_samples:
        pred = classifier.predict(sample)
        print(f"\nText: \"{sample}\"")
        print(f"  -> Predicted Category: {pred['predicted_category']}")
        print(f"  -> Confidence Score:   {pred['confidence_pct']}%")
        print(f"  -> SVM Prediction:      {pred['svm_prediction']}")

    print("\n[OK] Model training and evaluation complete!")


if __name__ == "__main__":
    train()
