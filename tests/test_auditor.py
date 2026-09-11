"""
Unit & Integration Test Suite for Legal Contract Dark Pattern Auditor NLP Engine
Uses Python's standard library `unittest` framework for out-of-the-box test execution.
"""

import unittest
from nlp_engine.parser import DocumentParser, ContractClause
from nlp_engine.deontic_classifier import DeonticClassifier, DeonticCategory, DutyActor
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

    def test_inline_clause_title_extraction(self):
        sample = """
        1. INDEMNIFICATION. Customer agrees to defend and indemnify Vendor against all third-party claims.
        2. LIMITATION OF LIABILITY - In no event shall Company aggregate liability exceed fifty dollars ($50.00).
        """
        clauses = self.parser.parse(sample, "Inline Title Doc")
        self.assertEqual(len(clauses), 2)
        self.assertIn("INDEMNIFICATION", clauses[0].title)
        self.assertIn("Customer agrees to defend", clauses[0].text)
        self.assertIn("LIMITATION OF LIABILITY", clauses[1].title)
        self.assertIn("In no event shall Company", clauses[1].text)

    def test_markdown_and_bold_headers(self):
        sample = """
        ### 1. Scope of Service
        The company will provide cloud hosting.

        **2. Termination Rights**
        Either party may terminate upon notice.
        """
        clauses = self.parser.parse(sample, "Markdown Doc")
        self.assertEqual(len(clauses), 2)
        self.assertIn("Scope of Service", clauses[0].title)
        self.assertIn("Termination Rights", clauses[1].title)

    def test_html_and_preamble_parsing(self):
        sample = """
        <p><b>TERMS OF SERVICE</b></p>
        <p>Welcome to our platform. By using this service you agree to these terms.</p>
        <p><b>1. User Conduct</b></p>
        <p>You must not upload malicious files.</p>
        """
        clauses = self.parser.parse(sample, "HTML Scraped Doc")
        self.assertGreaterEqual(len(clauses), 2)
        self.assertIn("User Conduct", clauses[1].title)

    def test_subitem_bullet_preservation(self):
        sample = """
        Section 3. Intellectual Property Rights
        (a) Customer retains full ownership of customer data.
        (b) Vendor receives a limited license to host data.
        (c) Suggestions are voluntary.
        """
        clauses = self.parser.parse(sample, "Bullet Doc")
        self.assertEqual(len(clauses), 1)
        self.assertIn("Intellectual Property", clauses[0].title)
        self.assertTrue(clauses[0].has_subsections)

    def test_sentence_abbreviation_preservation(self):
        text = "Vendor may terminate e.g. upon bankruptcy, i.e. insolvency et al. and Corp. failure or Pvt. Ltd. dissolution under Sec. 12."
        sentences = self.parser.segment_sentences(text)
        self.assertEqual(len(sentences), 1)
        self.assertIn("e.g.", sentences[0])
        self.assertIn("i.e.", sentences[0])
        self.assertIn("Pvt. Ltd.", sentences[0])


class TestDeonticClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = DeonticClassifier()

    def test_obligation_classification(self):
        sentence = "Customer shall promptly indemnify and defend Vendor from any damages."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.OBLIGATION.value)
        self.assertEqual(res["actor"], DutyActor.CUSTOMER_USER.value)
        self.assertGreater(res["confidence"], 0.6)

    def test_prohibition_classification(self):
        sentence = "Recipient shall not disclose or distribute any confidential information."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.PROHIBITION.value)

    def test_permission_classification(self):
        sentence = "Company reserves the right to modify services at its sole discretion."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.PERMISSION.value)
        self.assertEqual(res["actor"], DutyActor.VENDOR_COMPANY.value)

    def test_warranty_classification(self):
        sentence = "Vendor warrants and represents that the software contains no malicious code."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.WARRANTY.value)

    def test_disclaimer_classification(self):
        sentence = "The service is provided strictly as is and with all faults without warranty of any kind."
        res = self.classifier.classify_sentence(sentence)
        self.assertEqual(res["category"], DeonticCategory.DISCLAIMER.value)

    def test_asymmetry_calculation(self):
        clauses = [
            ContractClause(
                clause_id="c1", clause_number="1", title="User Rules",
                text="You shall not copy. You must indemnify us. You agree to pay all damages.",
                start_line=1, end_line=1, word_count=15, char_count=80,
                sentences=["You shall not copy.", "You must indemnify us.", "You agree to pay all damages."]
            ),
            ContractClause(
                clause_id="c2", clause_number="2", title="Vendor Rights",
                text="Company may modify at any time.",
                start_line=2, end_line=2, word_count=7, char_count=35,
                sentences=["Company may modify at any time."]
            ),
        ]
        profile = self.classifier.analyze_document_profile(clauses)
        self.assertGreater(profile["asymmetry_index"], 80.0)


class TestTrapDetector(unittest.TestCase):
    def setUp(self):
        self.detector = TrapDetector()

    def test_detect_unilateral_modification(self):
        clause_text = "Company reserves the right to modify these terms of service at any time without notice in our sole discretion."
        clause = ContractClause(
            clause_id="c1", clause_number="1", title="Modifications",
            text=clause_text, start_line=1, end_line=2,
            word_count=len(clause_text.split()), char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.UNILATERAL_MODIFICATION, trap_cats)
        self.assertTrue(any(t.severity in [RiskSeverity.CRITICAL, RiskSeverity.HIGH] for t in traps))

    def test_detect_ai_data_harvesting(self):
        clause_text = "Customer grants company a perpetual license to use customer data to train machine learning models and AI algorithms."
        clause = ContractClause(
            clause_id="c2", clause_number="2", title="Data Usage",
            text=clause_text, start_line=1, end_line=2,
            word_count=len(clause_text.split()), char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.PERPETUAL_DATA_AI_HARVESTING, trap_cats)

    def test_detect_forced_arbitration_jury_waiver(self):
        clause_text = "All claims shall be resolved exclusively by binding arbitration and you waive any right to a jury trial and class action waiver."
        clause = ContractClause(
            clause_id="c3", clause_number="3", title="Dispute Resolution",
            text=clause_text, start_line=1, end_line=2,
            word_count=len(clause_text.split()), char_count=len(clause_text),
            sentences=[clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        trap_cats = [t.category for t in traps]
        self.assertIn(TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER, trap_cats)

    def test_safeguard_prevents_false_positive_on_fair_terms(self):
        fair_clause_text = (
            "Neither party may modify this Agreement except through a written instrument signed by both parties. "
            "Vendor shall provide at least 30 days prior written notice of policy changes, with right to terminate and receive a pro-rata refund."
        )
        clause = ContractClause(
            clause_id="c4", clause_number="4", title="Amendments",
            text=fair_clause_text, start_line=1, end_line=2,
            word_count=len(fair_clause_text.split()), char_count=len(fair_clause_text),
            sentences=[fair_clause_text]
        )
        traps = self.detector.detect_traps_in_clause(clause)
        self.assertEqual(len(traps), 0)


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
        clause_text = "Customer shall indemnify, defend and hold harmless company from any and all claims and damages."
        clause = ContractClause(
            clause_id="c5", clause_number="5", title="Indemnity",
            text=clause_text, start_line=1, end_line=2,
            word_count=len(clause_text.split()), char_count=len(clause_text),
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
class TestOcrAndNoiseRegression(unittest.TestCase):
    """
    Comprehensive regression test suite for OCR scan inputs, camera capture text,
    hyphenated line-wraps, typographic ligatures, smart quotes, and noisy OCR artifacts.
    """
    def setUp(self):
        self.parser = DocumentParser()
        self.auditor = ContractAuditor()
        self.detector = TrapDetector()

    def test_ocr_hyphen_wrap_repair(self):
        noisy_ocr_text = """
        Section 1. Indemnification
        Customer agrees to defend, indemni-
        fication and hold harmless the Company from all third-party claims.

        Section 2. Dispute Resolution
        All disputes shall be resolved exclusively through binding arbi-
        tration and user agrees to a class action waiver.
        """
        clauses = self.parser.parse(noisy_ocr_text, "OCR Scanned Contract")
        self.assertEqual(len(clauses), 2)
        self.assertIn("indemnification", clauses[0].text)
        self.assertIn("arbitration", clauses[1].text)

    def test_ocr_ligature_decomposition(self):
        # Text with Unicode ligatures commonly produced by OCR engines (fi, fl, ff, ffi)
        ligature_text = "Vendor shall maintain afﬁliate records, provide flawless service, and require indemni\ufb01cation."
        cleaned = self.parser.clean_text(ligature_text)
        self.assertIn("affiliate", cleaned)
        self.assertIn("flawless", cleaned)
        self.assertIn("indemnification", cleaned)

    def test_ocr_bullet_and_pipe_margin_cleanup(self):
        scanned_bullets = """
        | Section 3. Data Rights
        • Customer grants company a perpetual license to use content.
        ● Company may train machine learning models on customer data.
        ▪ All feedback becomes exclusive property of provider.
        """
        clauses = self.parser.parse(scanned_bullets, "Scanned Bullets")
        self.assertEqual(len(clauses), 1)
        self.assertIn("Data Rights", clauses[0].title)
        self.assertNotIn("|", clauses[0].title)
        self.assertTrue(clauses[0].has_subsections)

    def test_camera_scanned_predatory_tos_regression(self):
        # Real-world simulation of camera photo OCR text with irregular line-breaks and formatting
        scanned_camera_tos = """
        TERMS OF USE AND SERVICE AGREEMENT

        1. MODIFICATION OF TERMS.
        We reserve the right to modify these
        terms of service at any time without
        prior notice in our sole discretion. Your
        continued use of the platform constitutes
        acceptance of revised terms.

        2. INTELLECTUAL PROPERTY & AI TRAINING.
        You grant company a perpetual, irrevo-
        cable, worldwide license to use your data
        to train machine learning models and AI algorithms.

        3. ARBITRATION & JURY WAIVER.
        All claims shall be settled by binding
        arbitration under AAA rules. You waive
        any right to a jury trial and class
        action waiver.

        4. LIMITATION OF LIABILITY.
        Under no circumstances shall Company aggregate
        liability exceed fifty dollars ($50.00). The service
        is provided strictly "as is".
        """
        report = self.auditor.audit(scanned_camera_tos, "Camera Photo Scanned ToS")
        self.assertGreaterEqual(report.total_clauses, 4)
        self.assertGreaterEqual(report.total_traps_found, 4)
        self.assertLess(report.overall_health_score, 50)
        self.assertIn(report.letter_grade, ["D", "F"])
        self.assertGreaterEqual(report.critical_traps_count, 2)
        
        # Verify specific trap categories detected accurately despite line breaks
        detected_categories = [t["category"] for c in report.clause_audit_details for t in c.get("traps", [])]
        self.assertIn(TrapCategory.UNILATERAL_MODIFICATION.value, detected_categories)
        self.assertIn(TrapCategory.PERPETUAL_DATA_AI_HARVESTING.value, detected_categories)
        self.assertIn(TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER.value, detected_categories)
        self.assertIn(TrapCategory.ZERO_LIABILITY_GUTTING.value, detected_categories)

    def test_scanned_employment_agreement_traps(self):
        # Scanned employment agreement with overbroad non-compete
        scanned_nda = """
        EMPLOYMENT RESTRICTIONS AND IP ASSIGNMENT

        Section 1. Non-Compete Covenant
        Employee shall not directly or indirectly engage in any
        competing business worldwide for a period of 3 years
        following termination.

        Section 2. IP Assignment
        Employee hereby irrevocably assigns to Company all
        inventions, ideas, customizations, and moral rights.
        """
        report = self.auditor.audit(scanned_nda, "Scanned Non-Compete Doc")
        self.assertGreaterEqual(report.total_traps_found, 2)
        detected_categories = [t["category"] for c in report.clause_audit_details for t in c.get("traps", [])]
        self.assertIn(TrapCategory.OVERBROAD_NON_COMPETE.value, detected_categories)
        self.assertIn(TrapCategory.AGGRESSIVE_IP_EXPROPRIATION.value, detected_categories)


if __name__ == "__main__":
    unittest.main()

