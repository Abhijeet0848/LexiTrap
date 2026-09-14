"""
Benchmark Matcher & Contrastive Deviation Engine
Compares predatory contract clauses against Gold-Standard Fair Industry Benchmarks
(e.g., Y-Combinator Safe NDA, Fair SaaS Framework, CommonAccord).
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import math
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .trap_detector import TrapCategory


@dataclass
class BenchmarkClause:
    benchmark_id: str
    category: TrapCategory
    standard_name: str
    title: str
    fair_text: str
    key_protective_features: List[str]

    @property
    def standard_text(self) -> str:
        return self.fair_text

    def to_dict(self) -> Dict[str, Any]:
        return {
            "benchmark_id": self.benchmark_id,
            "category": self.category.value,
            "standard_name": self.standard_name,
            "title": self.title,
            "fair_text": self.fair_text,
            "standard_text": self.fair_text,
            "key_protective_features": self.key_protective_features,
        }


class BenchmarkMatcher:
    """
    Computes contrastive deviation between contract clauses and balanced benchmark standards.
    """

    STANDARD_BENCHMARKS = [
        BenchmarkClause(
            benchmark_id="bm_unilateral_mod",
            category=TrapCategory.UNILATERAL_MODIFICATION,
            standard_name="Fair SaaS Benchmark (IEEE/CommonAccord)",
            title="Mutual Written Amendment & Notice Clause",
            fair_text=(
                "Neither party may modify, amend, or alter this Agreement except through a written instrument "
                "signed by authorized representatives of both parties. In the event Vendor updates operational "
                "policies or service terms, Vendor shall provide at least thirty (30) days prior written notice. "
                "If Customer materially objects to such modification, Customer may terminate this Agreement without "
                "penalty and receive a pro-rata refund of any prepaid, unearned fees."
            ),
            key_protective_features=[
                "Requires 30-day prior written notice before changes take effect",
                "Grants termination right with pro-rata refund upon objection",
                "Prohibits retroactive and surprise fee increases",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_indemnification",
            category=TrapCategory.ASYMMETRIC_INDEMNIFICATION,
            standard_name="YC Standard Safe Agreement / NVCA Model",
            title="Mutual Intellectual Property & Breach Indemnification",
            fair_text=(
                "Each party ('Indemnifying Party') agrees to defend, indemnify, and hold harmless the other party "
                "('Indemnified Party') from and against any third-party claims, liabilities, damages, and reasonable "
                "attorneys' fees arising directly from (a) the Indemnifying Party's gross negligence or willful misconduct, "
                "or (b) any claim that the Indemnifying Party's technology or materials infringe a valid copyright, patent, "
                "or trade secret. The total aggregate liability under this Section shall not exceed twelve (12) months "
                "of fees paid under this Agreement."
            ),
            key_protective_features=[
                "Bilateral/Mutual protection rather than one-sided",
                "Vendor indemnifies customer for IP infringement",
                "Bounded by a realistic aggregate liability cap",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_dispute_resolution",
            category=TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER,
            standard_name="American Bar Association Balanced Terms",
            title="Two-Tier Dispute Escalation & Preserved Court Jurisdiction",
            fair_text=(
                "In the event of any dispute arising out of or relating to this Agreement, senior executives from both "
                "parties shall first engage in good-faith negotiations for a period of thirty (30) days. If unresolved, "
                "either party may seek appropriate injunctive relief or adjudication in a court of competent jurisdiction "
                "in the mutual agreed forum, preserving each party's constitutional rights."
            ),
            key_protective_features=[
                "Executive good-faith negotiation tier before formal litigation",
                "Preserves open court adjudication and jury access",
                "Permits injunctive relief for trade secret preservation",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_ip_rights",
            category=TrapCategory.AGGRESSIVE_IP_EXPROPRIATION,
            standard_name="Standard Open Enterprise IP License",
            title="Customer Data Ownership & Limited Operating License",
            fair_text=(
                "As between the parties, Customer retains all right, title, and interest in and to all Customer Data, "
                "confidential information, and work product. Customer grants Vendor a non-exclusive, non-transferable, "
                "revocable license solely to process and host Customer Data to the extent strictly necessary to provide "
                "the services described herein during the Term."
            ),
            key_protective_features=[
                "Affirms explicit Customer ownership of all data and feedback",
                "Limits Vendor license strictly to service delivery scope",
                "Prohibits involuntary intellectual property transfers",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_ai_data_usage",
            category=TrapCategory.PERPETUAL_DATA_AI_HARVESTING,
            standard_name="Enterprise AI Trust & Zero-Retention Standard",
            title="Zero AI Model Training & Data Isolation Guarantee",
            fair_text=(
                "Vendor explicitly agrees that Customer Data, inputs, outputs, and confidential materials shall NOT be "
                "used, retained, or shared to train, fine-tune, retrain, or validate any machine learning models, "
                "large language models, or artificial intelligence algorithms. All Customer inputs shall remain segregated "
                "and deleted immediately following completion of the transaction."
            ),
            key_protective_features=[
                "Strict ban on training commercial LLMs/AI on customer data",
                "Enforces customer data segregation and privacy",
                "Zero data retention guarantees",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_auto_renewal",
            category=TrapCategory.TRAPPED_AUTO_RENEWAL,
            standard_name="FTC 'Click-to-Cancel' Compliant Terms",
            title="Transparent Notice-Based Renewal & Easy Cancellation",
            fair_text=(
                "This Agreement shall renew for successive one (1) month terms unless either party provides written notice "
                "of non-renewal at least fifteen (15) days prior. Vendor must provide an electronic reminder notice at least "
                "thirty (30) days prior to any annual renewal. Customer may cancel at any time via the web management console."
            ),
            key_protective_features=[
                "Mandatory 30-day reminder before renewal occurs",
                "Reasonable 15-day notice window",
                "1-Click digital cancellation mechanism",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_non_compete",
            category=TrapCategory.OVERBROAD_NON_COMPETE,
            standard_name="FTC 2024 Rule & California Standard Protection",
            title="Permissible Non-Solicitation & Free Mobility Clause",
            fair_text=(
                "Recipient shall not directly solicit for employment any key personnel of Discloser for a period of "
                "six (6) months following termination. Nothing herein shall restrict Recipient or its employees from "
                "exercising their professional trade, accepting employment with any employer, or engaging in general "
                "commercial competition."
            ),
            key_protective_features=[
                "Eliminates blanket non-compete lockouts",
                "Protects employee mobility and commercial freedom",
                "Narrowly scoped short non-solicit window (6 months)",
            ],
        ),
        BenchmarkClause(
            benchmark_id="bm_liability_cap",
            category=TrapCategory.ZERO_LIABILITY_GUTTING,
            standard_name="Balanced Commercial SaaS Liability Benchmark",
            title="Balanced Aggregate Liability Cap with Essential Carve-Outs",
            fair_text=(
                "Except for breaches of confidentiality, data security obligations, or willful misconduct, each party's "
                "total aggregate liability arising out of or related to this Agreement shall be capped at the total amount "
                "of fees paid or payable by Customer in the twelve (12) month period immediately preceding the event. "
                "Neither party shall be liable for indirect or consequential damages, subject to standard carve-outs."
            ),
            key_protective_features=[
                "Reasonable 12-month fees paid cap for both parties",
                "Carves out data breaches and confidentiality violations",
                "Provides mutual financial predictability",
            ],
        ),
    ]

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        benchmark_texts = [bm.fair_text for bm in self.STANDARD_BENCHMARKS]
        self.tfidf_matrix = self.vectorizer.fit_transform(benchmark_texts)
        self.benchmark_map: Dict[TrapCategory, BenchmarkClause] = {
            bm.category: bm for bm in self.STANDARD_BENCHMARKS
        }
        # Pre-cache individual benchmark vectors for instant cosine similarity
        self.bm_vectors: Dict[TrapCategory, Any] = {
            bm.category: self.vectorizer.transform([bm.fair_text]) for bm in self.STANDARD_BENCHMARKS
        }

    def match_benchmark_for_category(self, category: TrapCategory) -> Optional[BenchmarkClause]:
        """Returns the gold-standard benchmark clause for a specific trap category."""
        return self.benchmark_map.get(category)

    def get_standard_clause(self, category: Any) -> Optional[BenchmarkClause]:
        """Returns standard benchmark clause by category enum or string name."""
        if isinstance(category, TrapCategory):
            return self.benchmark_map.get(category)
        cat_str = str(category).lower()
        for cat_enum, bm in self.benchmark_map.items():
            if cat_enum.value.lower() in cat_str or cat_str in cat_enum.value.lower() or cat_enum.name.lower() in cat_str:
                return bm
        return self.STANDARD_BENCHMARKS[0] if self.STANDARD_BENCHMARKS else None

    def calculate_clause_deviation(self, clause_text: str, category: TrapCategory) -> Dict[str, Any]:
        """
        Calculates cosine similarity and deviation score between a clause and its category benchmark.
        """
        benchmark = self.match_benchmark_for_category(category)
        bm_vec = self.bm_vectors.get(category)
        if not benchmark or bm_vec is None:
            return {
                "similarity_score": 0.0,
                "deviation_score": 1.0,
                "deviation_level": "EXTREME",
                "benchmark": None,
            }

        clause_vec = self.vectorizer.transform([clause_text])
        sim = float(cosine_similarity(clause_vec, bm_vec)[0][0])
        dev = max(0.0, min(1.0, round(1.0 - sim, 3)))

        if dev > 0.8:
            dev_level = "CRITICAL DEVIATION"
        elif dev > 0.6:
            dev_level = "SUBSTANTIAL DEVIATION"
        elif dev > 0.35:
            dev_level = "MODERATE DEVIATION"
        else:
            dev_level = "ALIGNED WITH BENCHMARK"

        return {
            "similarity_score": round(sim, 3),
            "deviation_score": dev,
            "deviation_level": dev_level,
            "benchmark": benchmark.to_dict(),
        }
