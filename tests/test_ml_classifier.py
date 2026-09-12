"""
Unit Tests for Machine Learning Legal Clause Classifier
"""

import unittest
from nlp_engine.ml_classifier import LegalClauseMLClassifier
from nlp_engine.training_data import TRAINING_DATA


class TestLegalClauseMLClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classifier = LegalClauseMLClassifier()
        if not cls.classifier.is_trained:
            cls.classifier.train(TRAINING_DATA, evaluate=False)

    def test_model_is_trained(self):
        self.assertTrue(self.classifier.is_trained)
        self.assertGreater(len(self.classifier.classes_), 5)

    def test_unilateral_modification_prediction(self):
        clause = "We reserve the right to modify or amend these terms and conditions at any time without prior notice in our sole discretion."
        pred = self.classifier.predict_clause(clause)
        self.assertTrue(pred["is_trap"])
        self.assertEqual(pred["predicted_category"], "Unilateral Modification Trap")
        self.assertGreater(pred["confidence"], 0.35)

    def test_liability_gutting_prediction(self):
        clause = "In no event shall company aggregate liability exceed fifty dollars ($50.00) or $0 for any damages."
        pred = self.classifier.predict_clause(clause)
        self.assertTrue(pred["is_trap"])
        self.assertEqual(pred["predicted_category"], "Complete Liability Gutting & As-Is Trap")

    def test_arbitration_waiver_prediction(self):
        clause = "All disputes shall be resolved by confidential binding arbitration and you waive any right to a jury trial or class action."
        pred = self.classifier.predict_clause(clause)
        self.assertTrue(pred["is_trap"])
        self.assertEqual(pred["predicted_category"], "Forced Arbitration & Class Action Waiver")

    def test_safe_clause_prediction(self):
        clause = "Each party agrees to mutual indemnification capped at 12 months of fees paid, with carve-outs for data breaches and confidentiality."
        pred = self.classifier.predict_clause(clause)
        self.assertEqual(pred["predicted_category"], "Safe / Balanced Standard")


if __name__ == "__main__":
    unittest.main()
