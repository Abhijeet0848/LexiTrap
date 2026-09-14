"""
Unit and Integration Tests for LexiTrap 4 Major Intelligence Features:
1. Readability & Obfuscation Analyzer + Plain English TL;DR Summarizer
2. Contract DNA Risk Heatmap
3. Clean & Fair Contract Generator
4. Draft A vs Draft B Comparative Audit
"""

import unittest
import json
from app import app
from nlp_engine.readability import ReadabilityAnalyzer
from nlp_engine.auditor import ContractAuditor
from nlp_engine.scorer import ContractScorer, AuditReport

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.auditor = ContractAuditor()
        self.readability = ReadabilityAnalyzer()

    def test_readability_analyzer_metrics(self):
        """Test Flesch-Kincaid, Gunning Fog, and Obfuscation scoring."""
        simple_text = "The vendor will deliver the goods on Monday. The buyer will pay upon delivery."
        metrics = self.readability.analyze(simple_text)
        
        self.assertIn("flesch_reading_ease", metrics)
        self.assertIn("flesch_kincaid_grade", metrics)
        self.assertIn("gunning_fog_index", metrics)
        self.assertIn(metrics["obfuscation_level"], [
            "Clear & Plain English",
            "Moderate Legalese",
            "Heavy Legal Jargon"
        ])

    def test_readability_tldr_summary(self):
        """Test Plain-English TL;DR generator on high-risk clauses."""
        clause_text = "Company may unilaterally modify these Terms at any time without notice. Customer waives all rights to jury trial."
        traps = [
            {"category": "Unilateral Modification Trap", "legal_danger": "Company can alter terms whenever they want without asking."}
        ]
        tldr = self.readability.generate_tldr(clause_text, "Prohibition", traps)
        self.assertTrue(len(tldr) > 10)
        self.assertTrue("company" in tldr.lower() or "terms" in tldr.lower() or "change" in tldr.lower() or "unilaterally" in tldr.lower())

    def test_auditor_populates_readability_and_tldr(self):
        """Verify that running an audit populates readability and tldr on clauses and report."""
        text = """
1. Unilateral Amendments: We reserve the right to alter pricing and agreement terms at any time in our sole discretion without notice.
2. Governing Law: This agreement is governed by the laws of California.
        """
        report = self.auditor.audit_contract(text, "Test Agreement")
        
        # Report level
        self.assertIsNotNone(report.readability_profile)
        self.assertIn("flesch_reading_ease", report.readability_profile)
        
        # Clause level
        self.assertTrue(len(report.clause_audit_details) >= 1)
        for clause in report.clause_audit_details:
            self.assertIn("readability", clause)
            self.assertIn("tldr_summary", clause)
            self.assertIsNotNone(clause["readability"])
            self.assertIsNotNone(clause["tldr_summary"])

    def test_api_clean_contract_endpoint(self):
        """Verify /api/clean-contract endpoint replaces predatory clauses with fair models."""
        text = """
1. Amendments: We reserve the right to modify these terms at any time without notice in our sole discretion.
2. User Content: You grant Company a perpetual, irrevocable, worldwide license to use, reproduce, modify, and train AI machine learning models on your content.
        """
        response = self.app.post("/api/clean-contract", json={"text": text, "name": "Test Agreement"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("clean_text", data)
        self.assertIn("modifications_count", data)
        self.assertTrue(data["modifications_count"] >= 1)
        self.assertIn("Neither party may modify or amend", data["clean_text"])

    def test_api_compare_drafts_endpoint(self):
        """Verify /api/compare-drafts endpoint calculates delta risk and eliminated traps."""
        draft_a = """
1. Amendments: We reserve the right to modify these terms at any time without notice.
2. Liability: In no event shall Company be liable for any data loss, breach, or damages.
3. Arbitration: All disputes must be submitted to confidential binding individual arbitration, waiving all class actions and jury trials.
        """
        draft_b = """
1. Amendments: Any modifications to this agreement require 30 days prior written notice and mutual consent.
2. Liability: Each party's total aggregate liability shall be capped at the total fees paid in the preceding 12 months.
3. Dispute Resolution: Disputes shall be resolved in a court of competent jurisdiction.
        """
        response = self.app.post("/api/compare-drafts", json={"draft_a": draft_a, "draft_b": draft_b})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("comparison", data)
        
        comparison = data["comparison"]
        self.assertIn("delta_risk", comparison)
        self.assertIn("delta_health", comparison)
        self.assertIn("traps_eliminated_count", comparison)
        # Draft B is significantly safer than Draft A (delta_risk is positive reduction)
        self.assertTrue(comparison["delta_risk"] > 0)
        self.assertTrue(comparison["delta_health"] > 0)
        self.assertTrue(comparison["traps_eliminated_count"] >= 1)
        self.assertTrue(comparison["is_safer"])

    def test_api_fetch_url_validation(self):
        """Verify /api/fetch-url rejects empty URLs and SSRF attacks."""
        # Empty input
        resp = self.app.post("/api/fetch-url", json={"url": ""})
        self.assertEqual(resp.status_code, 400)

        # Self-fetch blocking
        resp = self.app.post("/api/fetch-url", json={"url": "http://localhost:5000"})
        self.assertEqual(resp.status_code, 400)

    def test_api_fetch_url_flipkart_discovery(self):
        """Verify /api/fetch-url auto-discovers Flipkart terms from bare domain name."""
        resp = self.app.post("/api/fetch-url", json={"url": "flipkart.com"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Flipkart", data["title"])
        self.assertTrue(len(data["text"]) > 200)

    def test_api_fetch_url_meesho_discovery(self):
        """Verify /api/fetch-url resolves Meesho terms even with bot protection."""
        resp = self.app.post("/api/fetch-url", json={"url": "https://www.meesho.com/"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Meesho", data["title"])
        self.assertTrue(len(data["text"]) > 200)
        self.assertIn("meesho", data["text"].lower())

if __name__ == "__main__":
    unittest.main()
