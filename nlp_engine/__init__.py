"""
Legal Contract Dark Pattern & Trap-Clause Auditor NLP Engine
"""

from .parser import DocumentParser, ContractClause
from .deontic_classifier import DeonticClassifier, DeonticCategory
from .trap_detector import TrapDetector, TrapMatch, TrapCategory
from .benchmarks import BenchmarkMatcher, BenchmarkClause
from .redliner import RedlineGenerator, RedlineResult
from .scorer import ContractScorer, AuditReport
from .auditor import ContractAuditor

__all__ = [
    "DocumentParser",
    "ContractClause",
    "DeonticClassifier",
    "DeonticCategory",
    "TrapDetector",
    "TrapMatch",
    "TrapCategory",
    "BenchmarkMatcher",
    "BenchmarkClause",
    "RedlineGenerator",
    "RedlineResult",
    "ContractScorer",
    "AuditReport",
    "ContractAuditor",
]
