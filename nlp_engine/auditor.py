"""
Unified Contract Auditor Pipeline
Connects parser, deontic classifier, trap detector, benchmark matcher, redliner,
scorer, readability analyzer, and the full Academic NLP Pipeline (Tokenization,
Lemmatization, POS tagging, NER, TF-IDF, Semantic Similarity, and ML Classification).
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from .parser import DocumentParser, ContractClause
from .deontic_classifier import DeonticClassifier
from .trap_detector import TrapDetector, TrapMatch, RiskSeverity
from .benchmarks import BenchmarkMatcher
from .redliner import RedlineGenerator, RedlineResult
from .scorer import ContractScorer, AuditReport
from .readability import ReadabilityAnalyzer
from .nlp_pipeline import NLPPipeline
from .ml_classifier import LegalClauseMLClassifier


class ContractAuditor:
    """
    Main orchestration class that takes raw legal text and produces
    a comprehensive audit report with risk metrics, deontic analysis,
    benchmark deviation scores, readability metrics, plain-English summaries,
    balanced redlines, and an end-to-end Academic NLP Pipeline.
    """

    def __init__(self):
        self.parser = DocumentParser()
        self.deontic_classifier = DeonticClassifier()
        self.trap_detector = TrapDetector()
        self.benchmark_matcher = BenchmarkMatcher()
        self.redliner = RedlineGenerator(self.benchmark_matcher)
        self.scorer = ContractScorer()
        self.readability_analyzer = ReadabilityAnalyzer()
        self.nlp_pipeline = NLPPipeline()
        self.ml_classifier = LegalClauseMLClassifier()

    def audit(self, text: str, document_name: str = "Legal Agreement") -> AuditReport:
        """Runs end-to-end NLP audit pipeline on contract text."""
        # Auto-detect document title if generic or unspecified
        if not document_name or document_name in ("Legal Agreement", "Submitted Contract", "Contract Document"):
            lines = text.strip().split("\n")
            for line in lines[:5]:
                clean = line.strip().strip("#*`_")
                if clean and 3 <= len(clean) <= 85 and not clean.lower().startswith(("last updated", "dated:", "version", "this is an agreement", "between")):
                    document_name = clean
                    break

        # 1. Parse document into hierarchical clauses
        clauses = self.parser.parse(text, document_name=document_name)
        if not clauses:
            empty_nlp = {
                "insufficient_legal_content": True,
                "message": "Insufficient legal text detected. Please paste actual contract clauses or terms of service.",
                "token_stats": {"total_tokens": 0, "stopword_ratio_pct": 0, "unique_vocab_count": 0},
                "entities_by_type": {},
                "top_tfidf_terms": [],
                "ml_model_metrics": self.ml_classifier.evaluation_metrics,
            }
            return self.scorer.build_report(
                document_name=document_name,
                clauses=[],
                traps=[],
                clause_trap_map={},
                deontic_profile={"total_sentences": 0, "counts": {}, "distribution_percentages": {}, "asymmetry_index": 0.0},
                redlines=[],
                clause_details=[],
                readability_profile=self.readability_analyzer.analyze_readability(""),
                nlp_overview=empty_nlp,
            )

        # 2. Deontic logic profiling
        deontic_doc_profile = self.deontic_classifier.analyze_document_profile(clauses)

        # 3. Readability Analysis
        doc_readability = self.readability_analyzer.analyze_readability(text)

        # 4. Trap & Dark pattern detection
        scan_results = self.trap_detector.scan_contract(clauses)
        traps: List[TrapMatch] = scan_results["traps"]
        clause_trap_map = scan_results["clause_trap_map"]

        # 5. Document-level NLP aggregation structures
        all_doc_entities: List[Dict[str, str]] = []
        doc_top_tfidf = self.nlp_pipeline.extract_tfidf_terms(text, top_n=12)
        doc_token_analysis = self.nlp_pipeline.analyze_tokens(text)
        doc_lemmas = self.nlp_pipeline.extract_lemmas(text)
        doc_pos = self.nlp_pipeline.tag_pos(text)

        # 6. Generate redlines, summaries, NLP features, and clause-level audit metadata
        redlines: List[Dict[str, Any]] = []
        clause_details: List[Dict[str, Any]] = []

        for clause in clauses:
            # Full Academic NLP Pipeline on clause
            clause_nlp = self.nlp_pipeline.process_clause(clause.text)
            
            # Supervised ML Classification (Logistic Regression + Linear SVM)
            ml_prediction = self.ml_classifier.predict(clause.text)
            
            # Deontic profile for this clause
            clause_deontic = self.deontic_classifier.classify_clause(clause)
            
            # Traps for this clause
            c_traps = clause_trap_map.get(clause.clause_id, [])
            clause_risk_score, heat_level = self.scorer.calculate_clause_risk(c_traps)

            # Readability & Plain-English TL;DR
            c_readability = self.readability_analyzer.analyze_readability(clause.text)
            c_tldr = self.readability_analyzer.generate_clause_tldr(
                clause,
                dominant_deontic=clause_deontic.get("dominant_category", ""),
                traps=c_traps
            )

            # Collect named entities
            all_doc_entities.extend(clause_nlp["named_entities"])

            # Benchmark deviations and redlines for traps
            trap_items = []
            similarity_to_benchmark = 0.0
            
            # If clause matches category, check similarity to standard market template
            pred_cat = ml_prediction.get("predicted_category", "")
            std_benchmark = self.benchmark_matcher.get_standard_clause(pred_cat)
            if std_benchmark:
                similarity_to_benchmark = self.nlp_pipeline.compute_semantic_similarity(
                    clause.text, std_benchmark.standard_text
                )

            for t in c_traps:
                # Benchmark comparison
                dev_info = self.benchmark_matcher.calculate_clause_deviation(clause.text, t.category)
                # Generate redline
                redline_res = self.redliner.generate_redline(t, clause)
                redlines.append(redline_res.to_dict())

                t_dict = t.to_dict()
                t_dict["benchmark_comparison"] = dev_info
                t_dict["redline_id"] = redline_res.redline_id
                trap_items.append(t_dict)

            clause_details.append({
                "clause_id": clause.clause_id,
                "clause_number": clause.clause_number,
                "title": clause.title,
                "text": clause.text,
                "start_line": clause.start_line,
                "end_line": clause.end_line,
                "word_count": clause.word_count,
                "sentences_count": len(clause.sentences),
                "deontic_profile": clause_deontic,
                "readability": c_readability,
                "tldr_summary": c_tldr,
                "risk_score": clause_risk_score,
                "heat_level": heat_level,
                "has_traps": len(c_traps) > 0,
                "traps_count": len(c_traps),
                "traps": trap_items,
                "nlp_analysis": clause_nlp,
                "ml_classification": ml_prediction,
                "benchmark_similarity": similarity_to_benchmark,
            })

        # Group unique Named Entities by category
        entities_by_type: Dict[str, List[str]] = {}
        for ent in all_doc_entities:
            lbl = ent["label"]
            val = ent["entity"]
            if lbl not in entities_by_type:
                entities_by_type[lbl] = []
            if val not in entities_by_type[lbl]:
                entities_by_type[lbl].append(val)

        nlp_overview = {
            "token_stats": doc_token_analysis,
            "lemmas": doc_lemmas,
            "pos_distribution": doc_pos["distribution"],
            "modal_verbs": doc_pos["modals_found"],
            "entities_by_type": entities_by_type,
            "top_tfidf_terms": doc_top_tfidf,
            "ml_model_metrics": self.ml_classifier.evaluation_metrics,
        }

        # 7. Build final report
        report = self.scorer.build_report(
            document_name=document_name,
            clauses=clauses,
            traps=traps,
            clause_trap_map=clause_trap_map,
            deontic_profile=deontic_doc_profile,
            redlines=redlines,
            clause_details=clause_details,
            readability_profile=doc_readability,
            nlp_overview=nlp_overview,
        )

        return report

    # Convenience alias
    audit_contract = audit

