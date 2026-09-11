"""
Unified Contract Auditor Pipeline
Connects parser, deontic classifier, trap detector, benchmark matcher, redliner, and scorer.
"""

from typing import List, Dict, Any, Optional
from .parser import DocumentParser, ContractClause
from .deontic_classifier import DeonticClassifier
from .trap_detector import TrapDetector, TrapMatch, RiskSeverity
from .benchmarks import BenchmarkMatcher
from .redliner import RedlineGenerator, RedlineResult
from .scorer import ContractScorer, AuditReport
from .readability import ReadabilityAnalyzer


class ContractAuditor:
    """
    Main orchestration class that takes raw legal text and produces
    a comprehensive audit report with risk metrics, deontic analysis,
    benchmark deviation scores, readability metrics, plain-English TL;DRs,
    and balanced redlines.
    """

    def __init__(self):
        self.parser = DocumentParser()
        self.deontic_classifier = DeonticClassifier()
        self.trap_detector = TrapDetector()
        self.benchmark_matcher = BenchmarkMatcher()
        self.redliner = RedlineGenerator(self.benchmark_matcher)
        self.scorer = ContractScorer()
        self.readability_analyzer = ReadabilityAnalyzer()

    def audit(self, text: str, document_name: str = "Legal Agreement") -> AuditReport:
        """Runs end-to-end NLP audit pipeline on contract text."""
        # 1. Parse document into hierarchical clauses
        clauses = self.parser.parse(text, document_name=document_name)
        if not clauses:
            return self.scorer.build_report(
                document_name=document_name,
                clauses=[],
                traps=[],
                clause_trap_map={},
                deontic_profile={"total_sentences": 0, "counts": {}, "distribution_percentages": {}},
                redlines=[],
                clause_details=[],
                readability_profile=self.readability_analyzer.analyze_readability(""),
            )

        # 2. Deontic logic profiling
        deontic_doc_profile = self.deontic_classifier.analyze_document_profile(clauses)

        # 3. Readability Analysis
        doc_readability = self.readability_analyzer.analyze_readability(text)

        # 4. Trap & Dark pattern detection
        scan_results = self.trap_detector.scan_contract(clauses)
        traps: List[TrapMatch] = scan_results["traps"]
        clause_trap_map = scan_results["clause_trap_map"]

        # 5. Generate redlines, TL;DR summaries, and clause-level audit metadata
        redlines: List[Dict[str, Any]] = []
        clause_details: List[Dict[str, Any]] = []

        for clause in clauses:
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

            # Benchmark deviations and redlines for traps
            trap_items = []
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
            })

        # 6. Build final report
        report = self.scorer.build_report(
            document_name=document_name,
            clauses=clauses,
            traps=traps,
            clause_trap_map=clause_trap_map,
            deontic_profile=deontic_doc_profile,
            redlines=redlines,
            clause_details=clause_details,
            readability_profile=doc_readability,
        )

        return report

    # Convenience alias
    audit_contract = audit
