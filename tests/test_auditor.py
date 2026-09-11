"""
Unit & Integration Test Suite for Legal Contract Dark Pattern Auditor NLP Engine
Uses Python's standard library `unittest` framework for out-of-the-box test execution.
"""

import unittest
from nlp_engine.parser import DocumentParser, ContractClause
from nlp_engine.deontic_classifier import DeonticClassifier, DeonticCategory
from nlp_engine.trap_detector import TrapDetector, TrapCategory, RiskSeverity
from nlp_engine.benchmarks import BenchmarkMatcher
from nlp_engine.redliner import RedlineGenerator
from nlp_engine.scorer import ContractScorer
from nlp_engine.auditor import ContractAuditor
from samples.sample_data import load_sample_text


class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        self.parser = DocumentParser()

    def test_numbered_section_parsing(self):
        sample = """
        Section 1. Definitions
        This section defines all basic terms.

        Section 2. Confidentiality Obligations
        Recipient shall keep all materials secret.
        """
        clauses = self.parser.parse(sample, "Test Doc")
        self.assertEqual(len(clauses), 2)
        self.assertEqual(clauses[0].clause_number, "1")
        self.assertIn("Definitions", clauses[0].title)
        self.assertEqual(clauses[1].clause_number, "2")
        self.assertIn("Confidentiality", clauses[1].title)

    def test_sentence_abbreviation_preservation(self):
        text = "Vendor may terminate e.g. upon bankruptcy, i.e. insolvency et al. and Corp. failure."
        sentences = self.parser.segment_sentences(text)
        self.assertEqual(len(sentences), 1)
        self.assertIn("e.g.", sentences[0])
        self.assertIn("i.e.", sentences[0])


class TestDeonticClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = DeonticClassifier()

    def test_obligation_classification(self):
        sentence = "Customer shall promptly indemnify and defend Vendor from any damages."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.OBLIGATION.value)
        self.assertGreater(res["confidence"], 0.6)

    def test_prohibition_classification(self):
        sentence = "Recipient shall not disclose or distribute any confidential information."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.PROHIBITION.value)

    def test_permission_classification(self):
        sentence = "Company may modify services at its sole discretion."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.PERMISSION.value)

    def test_warranty_classification(self):
        sentence = "Vendor warrants and represents that the software contains no malicious code."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.WARRANTY.value)

    def test_disclaimer_classification(self):
        sentence = "The service is provided strictly as is and with all faults without warranty of any kind."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.DISCLAIMER.value)


class TestTrapDetector(unittest.TestCase):
    def setUp(self):
        self.detector = TrapDetector()
        self.parser = DocumentParser()

    def test_detect_unilateral_modification(self):
        clause_text = "Company reserves the right to modify these terms of service at any time without notice in our sole discretion."
        clause = ContractClause(
            clause_id="c1",
            clause_number="1",
            title="Modifications",
            text=clause_text,
            start_line=1,
            end_line=2,
            word_count=len(clause_text.split()),
            char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.UNILATERAL_MODIFICATION, trap_cats)
        self.assertTrue(any(t.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH] for t in traps))

    def test_detect_ai_data_harvesting(self):
        clause_text = "Customer grants company a perpetual license to use customer data to train machine learning models and AI algorithms."
        clause = ContractClause(
            clause_id="c2",
            clause_number="2",
            title="Data Usage",
            text=clause_text,
            start_line=1,
            end_line=2,
            word_count=len(clause_text.split()),
            char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.PERPETUAL_DATA_AI_HARVESTING, trap_cats)

    def test_detect_forced_arbitration_jury_waiver(self):
        clause_text = "All claims shall be resolved by binding arbitration and you waive any right to a jury trial and class action waiver."
        clause = ContractClause(
            clause_id="c3",
            clause_number="3",
            title="Dispute Resolution",
            text=clause_text,
            start_line=1,
            end_line=2,
            word_count=len(clause_text.split()),
            char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER, trap_cats)


class TestBenchmarkAndRedliner(unittest.TestCase):
    def setUp(self):
        self.matcher = BenchmarkMatcher()
        self.redliner = RedlineGenerator(self.matcher)
        self.detector = TrapDetector()

    def test_benchmark_matching(self):
        dev = self.matcher.calculate_clause_deviation(
            "Company may change terms anytime without notice.",
            TrapCategory.UNILATERAL_MODIFICATION
        )
        self.assertIsNotNone(dev["benchmark"])
        self.assertGreater(dev["deviation_score"], 0.0)

    def test_redline_generation(self):
        clause_text = "Customer shall indemnify, defend and hold harmless company from any and all claims."
        clause = ContractClause(
            clause_id="c4",
            clause_number="4",
            title="Indemnity",
            text=clause_text,
            start_line=1,
            end_line=2,
            word_count=len(clause_text.split()),
            char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        self.assertGreater(len(traps), 0)
        rl = self.redliner.generate_redline(traps[0], clause)
        self.assertIsNotNone(rl.recommended_text)
        self.assertTrue("redline-del" in rl.diff_html or "redline-ins" in rl.diff_html)
        self.assertGreater(len(rl.legal_rationale), 10)


class TestEndToEndAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = ContractAuditor()

    def test_predatory_tos_audit(self):
        text = load_sample_text("predatory_saas_tos")
        report = self.auditor.audit(text, "CloudSphere Predatory SaaS")
        self.assertGreaterEqual(report.total_clauses, 5)
        self.assertGreaterEqual(report.total_traps_found, 4)
        self.assertLess(report.overall_health_score, 60)
        self.assertIn(report.letter_grade, ["C", "D", "F"])
        self.assertGreaterEqual(report.critical_traps_count, 1)

    def test_fair_nda_audit(self):
        text = load_sample_text("fair_standard_nda")
        report = self.auditor.audit(text, "Fair YC Mutual NDA")
        self.assertGreaterEqual(report.total_clauses, 4)
        self.assertGreaterEqual(report.overall_health_score, 80)
        self.assertIn(report.letter_grade, ["A+", "A"])
        self.assertEqual(report.critical_traps_count, 0)


if __name__ == "__main__":
    unittest.main()
