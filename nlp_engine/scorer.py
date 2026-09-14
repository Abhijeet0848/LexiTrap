"""
Contract Risk Scoring Engine & Audit Report Builder
Calculates overall contract health (0-100), letter grade (A+ to F), and clause risk heatmaps
using category-saturation penalty caps and structural deontic asymmetry weighting.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .parser import ContractClause
from .trap_detector import TrapMatch, RiskSeverity, TrapCategory


@dataclass
class AuditReport:
    document_name: str
    total_clauses: int
    total_words: int
    total_sentences: int
    overall_health_score: float      # 0 to 100 (higher is safer)
    overall_risk_score: float        # 0 to 100 (higher is riskier)
    letter_grade: str                # A+, A, B, C, D, F
    risk_level: str                  # SAFE, LOW, MODERATE, HIGH, CRITICAL
    verdict_title: str
    verdict_description: str
    total_traps_found: int
    critical_traps_count: int
    high_traps_count: int
    medium_traps_count: int
    category_penalties: Dict[str, float]
    deontic_profile: Dict[str, Any]
    clause_audit_details: List[Dict[str, Any]]
    executive_summary_points: List[str]
    redlines: List[Dict[str, Any]]
    readability_profile: Dict[str, Any] = field(default_factory=dict)
    nlp_overview: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_name": self.document_name,
            "total_clauses": self.total_clauses,
            "total_words": self.total_words,
            "total_sentences": self.total_sentences,
            "overall_health_score": self.overall_health_score,
            "overall_risk_score": self.overall_risk_score,
            "letter_grade": self.letter_grade,
            "risk_level": self.risk_level,
            "verdict_title": self.verdict_title,
            "verdict_description": self.verdict_description,
            "total_traps_found": self.total_traps_found,
            "critical_traps_count": self.critical_traps_count,
            "high_traps_count": self.high_traps_count,
            "medium_traps_count": self.medium_traps_count,
            "category_penalties": self.category_penalties,
            "deontic_profile": self.deontic_profile,
            "clause_audit_details": self.clause_audit_details,
            "executive_summary_points": self.executive_summary_points,
            "redlines": self.redlines,
            "readability_profile": self.readability_profile,
            "nlp_overview": self.nlp_overview,
        }


class ContractScorer:
    """
    Computes rigorous risk metrics, assigning penalties based on trap severity,
    deontic obligation density, and benchmark deviations with category saturation bounds.
    """

    # Maximum penalty allowed per category to prevent redundant double-counting
    CATEGORY_PENALTY_CAPS = {
        TrapCategory.UNILATERAL_MODIFICATION.value: 35.0,
        TrapCategory.ASYMMETRIC_INDEMNIFICATION.value: 40.0,
        TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER.value: 30.0,
        TrapCategory.AGGRESSIVE_IP_EXPROPRIATION.value: 32.0,
        TrapCategory.PERPETUAL_DATA_AI_HARVESTING.value: 35.0,
        TrapCategory.TRAPPED_AUTO_RENEWAL.value: 25.0,
        TrapCategory.OVERBROAD_NON_COMPETE.value: 30.0,
        TrapCategory.ZERO_LIABILITY_GUTTING.value: 35.0,
    }

    def __init__(self):
        pass

    def compute_health_grade(self, health_score: float) -> tuple[str, str, str, str]:
        """Maps health score (0-100) to Letter Grade, Risk Level, Verdict Title, and Description."""
        if health_score >= 85:
            return (
                "A+",
                "SAFE",
                "Safe & Balanced Agreement",
                "The contract adheres to standard industry norms with balanced protections and minimal legal risks."
            )
        elif health_score >= 70:
            return (
                "A",
                "LOW RISK",
                "Standard Commercial Terms",
                "The agreement is generally standard, with minor customary clauses that pose minimal operational concern."
            )
        elif health_score >= 50:
            return (
                "B",
                "MODERATE RISK",
                "Proceed with Caution",
                "Several clauses contain one-sided provisions. Request targeted redlines before execution."
            )
        elif health_score >= 30:
            return (
                "C",
                "HIGH RISK",
                "Unbalanced / Predatory Terms",
                "Contains material legal risks including asymmetric liability and potential IP exposure. Redlines strongly advised."
            )
        else:
            return (
                "F",
                "CRITICAL RISK",
                "Critical Danger - Do Not Sign",
                "Severe predatory contract loaded with dangerous liability traps, AI data harvesting, or harsh rights waivers."
            )

    def calculate_clause_risk(self, clause_traps: List[TrapMatch]) -> tuple[float, str]:
        """Calculates 0-100 risk score and heatmap tag for a single clause."""
        if not clause_traps:
            return 0.0, "SAFE"

        raw_penalty = sum(t.penalty_score for t in clause_traps)
        clause_risk = min(100.0, raw_penalty)

        if clause_risk >= 30.0 or any(t.severity == RiskSeverity.CRITICAL for t in clause_traps):
            heat_level = "CRITICAL"
        elif clause_risk >= 20.0 or any(t.severity == RiskSeverity.HIGH for t in clause_traps):
            heat_level = "HIGH"
        elif clause_risk >= 10.0:
            heat_level = "MEDIUM"
        else:
            heat_level = "LOW"

        return round(clause_risk, 1), heat_level

    def build_report(
        self,
        document_name: str,
        clauses: List[ContractClause],
        traps: List[TrapMatch],
        clause_trap_map: Dict[str, List[TrapMatch]],
        deontic_profile: Dict[str, Any],
        redlines: List[Dict[str, Any]],
        clause_details: List[Dict[str, Any]],
        readability_profile: Optional[Dict[str, Any]] = None,
        nlp_overview: Optional[Dict[str, Any]] = None,
    ) -> AuditReport:
        """Assembles a full AuditReport with calibrated penalty bounds and asymmetry metrics."""
        total_clauses = len(clauses)
        total_words = sum(c.word_count for c in clauses)
        total_sentences = sum(len(c.sentences) for c in clauses)

        # Count traps by severity
        crit_count = sum(1 for t in traps if t.severity == RiskSeverity.CRITICAL)
        high_count = sum(1 for t in traps if t.severity == RiskSeverity.HIGH)
        med_count = sum(1 for t in traps if t.severity == RiskSeverity.MEDIUM)

        # Calculate raw penalty by category with saturation caps
        category_raw: Dict[str, float] = {}
        for t in traps:
            cat_name = t.category.value
            category_raw[cat_name] = category_raw.get(cat_name, 0.0) + t.penalty_score

        category_penalties: Dict[str, float] = {}
        total_penalty = 0.0

        for cat_name, raw_p in category_raw.items():
            cap = self.CATEGORY_PENALTY_CAPS.get(cat_name, 35.0)
            capped_p = min(raw_p, cap)
            category_penalties[cat_name] = round(capped_p, 1)
            total_penalty += capped_p

        # Calibrated Proportional Health Score Calculation
        if len(traps) == 0:
            health_score = 100.0
            risk_score = 0.0
        else:
            trapped_clause_count = sum(1 for c in clause_details if c.get("has_traps", False))
            safe_clause_count = max(0, total_clauses - trapped_clause_count)
            safe_ratio = safe_clause_count / max(1, total_clauses)
            
            # Composite formula: 30% safe clause ratio + 70% exponential penalty decay
            penalty_decay = math.exp(-total_penalty / 65.0)
            raw_health = 100.0 * (0.30 * safe_ratio + 0.70 * penalty_decay)
            health_score = round(max(5.0, min(85.0, raw_health)), 1)
            risk_score = round(100.0 - health_score, 1)

        letter_grade, risk_level, verdict_title, verdict_desc = self.compute_health_grade(health_score)

        # Generate executive summary points
        summary_points = []
        if crit_count > 0:
            summary_points.append(f"Found {crit_count} CRITICAL legal trap(s) requiring immediate intervention.")
        if high_count > 0:
            summary_points.append(f"Identified {high_count} HIGH risk clause(s) with severe commercial imbalance.")
        if med_count > 0:
            summary_points.append(f"Flagged {med_count} MODERATE risk provision(s) deviating from market standards.")
        
        for cat, pen in sorted(category_penalties.items(), key=lambda x: x[1], reverse=True)[:3]:
            summary_points.append(f"Major risk driver: '{cat}' contributing {pen} penalty points.")

        asymmetry_index = deontic_profile.get("asymmetry_index", 0.0)
        if asymmetry_index >= 60.0 and len(traps) > 0 and total_clauses >= 3:
            summary_points.append(f"Contractual Duty Asymmetry ({asymmetry_index}%): The agreement places majority burdens on the user while giving wide unilateral discretion to the vendor.")

        if not summary_points:
            summary_points.append("No predatory legal patterns or dark traps detected. Agreement is clean and balanced.")

        return AuditReport(
            document_name=document_name,
            total_clauses=total_clauses,
            total_words=total_words,
            total_sentences=total_sentences,
            overall_health_score=health_score,
            overall_risk_score=risk_score,
            letter_grade=letter_grade,
            risk_level=risk_level,
            verdict_title=verdict_title,
            verdict_description=verdict_desc,
            total_traps_found=len(traps),
            critical_traps_count=crit_count,
            high_traps_count=high_count,
            medium_traps_count=med_count,
            category_penalties=category_penalties,
            deontic_profile=deontic_profile,
            clause_audit_details=clause_details,
            executive_summary_points=summary_points,
            redlines=redlines,
            readability_profile=readability_profile or {},
            nlp_overview=nlp_overview or {},
        )
