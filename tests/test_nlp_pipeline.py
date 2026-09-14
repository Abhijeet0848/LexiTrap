"""
Comprehensive Academic NLP Pipeline & Legal Contract Analysis Tests
Verifies:
1. Tokenization, Lemmatization, POS Tagging, NER, TF-IDF, Semantic Similarity
2. Supervised ML Classifier (Logistic Regression & Linear SVM)
3. 10+ Diverse Legal Clauses with Balanced vs Risky Discrimination
4. Web Navigation / Menu Noise Rejection
5. Mathematical Scoring Consistency
"""

import pytest
import unittest
from nlp_engine.nlp_pipeline import NLPPipeline
from nlp_engine.ml_classifier import LegalClauseMLClassifier
from nlp_engine.training_data import TRAINING_DATA
from nlp_engine.parser import DocumentParser
from nlp_engine.auditor import ContractAuditor
from nlp_engine.scorer import ContractScorer
from samples.sample_data import load_sample_text


class TestAcademicNLPPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nlp = NLPPipeline()
        cls.classifier = LegalClauseMLClassifier()
        if not cls.classifier.is_trained:
            cls.classifier.train(TRAINING_DATA, evaluate=True)
        cls.auditor = ContractAuditor()
        cls.parser = DocumentParser()

    # -------------------------------------------------------------
    # 1. NLP Pipeline Components Verification
    # -------------------------------------------------------------
    def test_tokenization_and_stopwords(self):
        text = "The provider may terminate this agreement at any time without prior notice."
        tokens_res = self.nlp.analyze_tokens(text)
        self.assertGreater(tokens_res["total_tokens"], 8)
        self.assertGreater(tokens_res["stopword_ratio_pct"], 20.0)
        self.assertIn("terminate", [t.lower() for t in tokens_res["sample_tokens"]])

    def test_lemmatization(self):
        # Test irregular and legal morphological mappings
        self.assertEqual(self.nlp.lemmatize_word("indemnifies"), "indemnify")
        self.assertEqual(self.nlp.lemmatize_word("terminating"), "terminate")
        self.assertEqual(self.nlp.lemmatize_word("obligations"), "obligation")
        self.assertEqual(self.nlp.lemmatize_word("warranties"), "warranty")
        self.assertEqual(self.nlp.lemmatize_word("renewals"), "renewal")

    def test_pos_tagging_and_modals(self):
        text = "Customer shall pay all fees within 30 days. Provider may suspend services."
        pos_res = self.nlp.tag_pos(text)
        self.assertIn("shall", pos_res["modals_found"])
        self.assertIn("may", pos_res["modals_found"])
        self.assertIn("Modal Verbs (Deontic)", pos_res["distribution"])

    def test_named_entity_recognition(self):
        text = "Flipkart Pvt. Ltd. warrants that damages shall not exceed INR 500 within 30 calendar days under the Information Technology Act in Bengaluru, India."
        entities = self.nlp.extract_named_entities(text)
        entity_types = {e["label"] for e in entities}
        self.assertIn("MONEY", entity_types)
        self.assertIn("DATE / DURATION", entity_types)
        self.assertIn("ORG", entity_types)
        self.assertIn("GPE", entity_types)
        self.assertIn("LAW / STATUTE", entity_types)

    def test_tfidf_salient_terms(self):
        text = "Confidential Information includes all non-public trade secrets, proprietary source code, and customer databases."
        tfidf_terms = self.nlp.extract_tfidf_terms(text, top_n=5)
        terms = [t["term"] for t in tfidf_terms]
        self.assertTrue(any("confidential" in t or "trade" in t or "secrets" in t for t in terms))

    def test_semantic_cosine_similarity(self):
        s1 = "The provider may terminate the agreement at any time without notice."
        s2 = "The service provider can end the contract immediately without providing prior notification."
        s3 = "Customer agrees to pay all monthly subscription fees in US dollars."
        sim_high = self.nlp.compute_semantic_similarity(s1, s2)
        sim_low = self.nlp.compute_semantic_similarity(s1, s3)
        self.assertGreater(sim_high, sim_low)

    # -------------------------------------------------------------
    # 2. Supervised ML Classifier Multi-Model Verification
    # -------------------------------------------------------------
    def test_ml_classifier_multi_model(self):
        metrics = self.classifier.train(TRAINING_DATA, evaluate=True)
        self.assertIn("logistic_regression", metrics)
        self.assertIn("linear_svm", metrics)
        self.assertGreaterEqual(metrics["logistic_regression"]["accuracy"], 0.90)
        self.assertGreaterEqual(metrics["linear_svm"]["accuracy"], 0.90)
        self.assertIn("confusion_matrix", metrics)

    # -------------------------------------------------------------
    # 3. 10 Legal Clauses: Balanced vs Risky Contrast
    # -------------------------------------------------------------
    def test_clause_1_balanced_termination(self):
        # Balanced: 30 days written notice
        clause = "Either party may terminate this agreement by providing 30 days written notice."
        res = self.auditor.audit(f"Section 1. Termination\n{clause}")
        self.assertEqual(res.total_traps_found, 0)
        self.assertEqual(res.risk_level, "SAFE")

    def test_clause_2_risky_unilateral_termination(self):
        # Risky: Unilateral without notice
        clause = "The provider may terminate this agreement at any time without prior notice."
        res = self.auditor.audit(f"Section 1. Termination\n{clause}")
        self.assertGreater(res.total_traps_found, 0)
        self.assertIn(res.risk_level, ["HIGH RISK", "CRITICAL"])

    def test_clause_3_automatic_renewal_trap(self):
        clause = "This agreement shall automatically renew for successive one-year periods unless either party provides written notice at least 90 days before expiration."
        res = self.auditor.audit(f"Section 1. Renewal\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    def test_clause_4_unlimited_liability_trap(self):
        clause = "The customer shall be liable for all losses without limitation."
        res = self.auditor.audit(f"Section 1. Liability\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    def test_clause_5_balanced_liability_cap(self):
        clause = "Each party's aggregate maximum liability arising under this agreement shall be strictly capped at the total amount of fees paid during the preceding twelve (12) months."
        res = self.auditor.audit(f"Section 1. Limitation of Liability\n{clause}")
        self.assertEqual(res.total_traps_found, 0)

    def test_clause_6_unilateral_modification_trap(self):
        clause = "Company reserves the right to modify or amend any term at any time in its sole and absolute discretion without prior notice."
        res = self.auditor.audit(f"Section 1. Amendments\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    def test_clause_7_balanced_ip_ownership(self):
        clause = "Customer retains all right, title, and ownership interest in all Customer Data uploaded to the platform."
        res = self.auditor.audit(f"Section 1. Data Ownership\n{clause}")
        self.assertEqual(res.total_traps_found, 0)

    def test_clause_8_perpetual_ai_data_harvesting_trap(self):
        clause = "You grant Company a perpetual, irrevocable, worldwide license to use, reproduce, and train artificial intelligence and machine learning models on all user content."
        res = self.auditor.audit(f"Section 1. License\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    def test_clause_9_forced_arbitration_and_class_waiver_trap(self):
        clause = "All disputes shall be resolved by confidential binding arbitration and you waive any right to a jury trial or class action lawsuit."
        res = self.auditor.audit(f"Section 1. Dispute Resolution\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    def test_clause_10_overbroad_employee_ip_trap(self):
        clause = "Employee assigns to Company all inventions and ideas conceived at any time 24 hours a day, whether during work hours or on personal time, for a period of three (3) years."
        res = self.auditor.audit(f"Section 1. IP Assignment\n{clause}")
        self.assertGreater(res.total_traps_found, 0)

    # -------------------------------------------------------------
    # 4. Web Navigation Noise Rejection Test
    # -------------------------------------------------------------
    def test_web_noise_filtering(self):
        noise_text = """
        New customer? Sign Up My Profile
        Flipkart Plus Zone
        Orders
        Wishlist
        Rewards
        Gift Cards
        Advertise on Flipkart
        Sports & Fitness
        Mobiles Electronics Beauty Home Appliances Toys
        """
        clauses = self.parser.parse(noise_text)
        self.assertEqual(len(clauses), 0, "Webpage navigation text should NOT be parsed as legal contract clauses.")

    # -------------------------------------------------------------
    # 5. Mathematical Scoring Consistency Test
    # -------------------------------------------------------------
    def test_scoring_internal_consistency(self):
        # 1. Balanced contract: High health (100), Low risk (0), 0 traps, 0% Asymmetry
        saas_text = load_sample_text("saas_agreement")
        report_safe = self.auditor.audit(saas_text)
        self.assertGreaterEqual(report_safe.overall_health_score, 85.0)
        self.assertLessEqual(report_safe.overall_risk_score, 15.0)
        self.assertEqual(report_safe.overall_health_score + report_safe.overall_risk_score, 100.0)
        self.assertEqual(report_safe.risk_level, "SAFE")
        self.assertNotIn("High Contractual Asymmetry (100.0%)", " ".join(report_safe.executive_summary_points))

        # 2. Toxic contract: Low health, High risk, high traps count
        toxic_text = load_sample_text("predatory_saas_tos")
        report_toxic = self.auditor.audit(toxic_text)
        self.assertLess(report_toxic.overall_health_score, 50.0)
        self.assertGreater(report_toxic.overall_risk_score, 50.0)
        self.assertIn(report_toxic.risk_level, ["HIGH RISK", "CRITICAL RISK"])
        self.assertGreater(report_toxic.total_traps_found, 0)


if __name__ == "__main__":
    unittest.main()
