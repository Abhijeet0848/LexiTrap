#!/usr/bin/env python3
"""
LexiTrap Model Training Script
Trains, evaluates, and exports the Machine Learning classifier for Legal Trap & Dark Pattern detection.
"""

import os
import sys
import time

# Ensure root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nlp_engine.training_data import TRAINING_DATA
from nlp_engine.ml_classifier import LegalClauseMLClassifier


def train():
    print("=" * 70)
    print("   LEXITRAP MACHINE LEARNING MODEL TRAINER")
    print("=" * 70)
    print(f"[*] Dataset Size: {len(TRAINING_DATA)} labeled clauses across 9 legal categories")
    
    start_time = time.time()
    classifier = LegalClauseMLClassifier()
    
    print("[*] Training TF-IDF Multi-Gram + Calibrated Logistic Classifier...")
    metrics = classifier.train(TRAINING_DATA, evaluate=True)
    
    elapsed = time.time() - start_time
    print(f"[+] Training completed in {elapsed:.3f} seconds\n")
    
    print("-" * 70)
    print(f"MODEL ACCURACY & PERFORMANCE METRICS")
    print("-" * 70)
    print(f"- Training Set Accuracy:    {metrics['train_accuracy'] * 100:.2f}%")
    if "cv_accuracy_mean" in metrics:
        print(f"- 5-Fold Cross-Validation:  {metrics['cv_accuracy_mean'] * 100:.2f}% (+/- {metrics['cv_accuracy_std'] * 100:.2f}%)")
    print(f"- Macro F1-Score:           {metrics['macro_f1']:.4f}")
    print(f"- Total Labeled Categories: {metrics['total_classes']}")
    print(f"- Total Training Samples:   {metrics['total_samples']}\n")

    print("-" * 70)
    print("PER-CATEGORY CLASSIFICATION REPORT")
    print("-" * 70)
    print(f"{'Category':<45} {'Precision':<10} {'Recall':<10} {'F1-Score':<10}")
    print("-" * 75)
    
    rep = metrics.get("classification_report", {})
    for cat, scores in rep.items():
        if isinstance(scores, dict):
            p = scores.get("precision", 0)
            r = scores.get("recall", 0)
            f1 = scores.get("f1-score", 0)
            print(f"{cat:<45} {p:>8.2f}   {r:>8.2f}   {f1:>8.2f}")

    # Save model artifact
    save_path = classifier.save()
    print("-" * 70)
    print(f"[OK] Model artifact successfully saved to:")
    print(f"     {save_path}")
    print("=" * 70)

    # Run quick validation on unseen test clauses
    print("\nINFERENCE TEST ON SAMPLE CLAUSES:")
    test_samples = [
        "We reserve the right to amend our subscription pricing and policies without notice.",
        "Under no circumstances shall company liability exceed fifty dollars ($50.00).",
        "Each party agrees to mutual indemnification capped at 12 months fees with carveouts.",
        "You waive all right to a jury trial and agree to individual binding arbitration."
    ]

    for sample in test_samples:
        pred = classifier.predict_clause(sample)
        status_icon = "TRAP" if pred["is_trap"] else "SAFE"
        print(f"\nText: \"{sample}\"")
        print(f"  -> Prediction: {pred['predicted_category']} [{status_icon}]")
        print(f"  -> Confidence: {pred['confidence'] * 100:.1f}%")

    print("\n[OK] Model training and evaluation complete!")


if __name__ == "__main__":
    train()
