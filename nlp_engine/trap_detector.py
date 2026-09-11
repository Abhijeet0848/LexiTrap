"""
Trap & Dark Pattern Detector
Scans legal clauses for 8 predatory contract patterns and calculates clause-level risk.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from .parser import ContractClause


class TrapCategory(str, Enum):
    UNILATERAL_MODIFICATION = "Unilateral Modification Trap"
    ASYMMETRIC_INDEMNIFICATION = "Asymmetric / Uncapped Indemnification"
    FORCED_ARBITRATION_CLASS_WAIVER = "Forced Arbitration & Class Action Waiver"
    AGGRESSIVE_IP_EXPROPRIATION = "Aggressive IP & Feedback Expropriation"
    PERPETUAL_DATA_AI_HARVESTING = "Perpetual AI Training & Data Monetization"
    TRAPPED_AUTO_RENEWAL = "Hidden Auto-Renewal & Trapped Termination"
    OVERBROAD_NON_COMPETE = "Overbroad Non-Compete & Lockout"
    ZERO_LIABILITY_GUTTING = "Complete Liability Gutting & As-Is Trap"


class RiskSeverity(str, Enum):
    CRITICAL = "CRITICAL"  # 80-100 penalty
    HIGH = "HIGH"          # 50-79 penalty
    MEDIUM = "MEDIUM"      # 25-49 penalty
    LOW = "LOW"            # 10-24 penalty
    SAFE = "SAFE"          # 0 penalty


@dataclass
class TrapMatch:
    trap_id: str
    category: TrapCategory
    severity: RiskSeverity
    confidence: float
    clause_id: str
    clause_title: str
    flagged_text: str
    matched_patterns: List[str]
    legal_danger: str
    business_impact: str
    recommended_mitigation: str
    penalty_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trap_id": self.trap_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "clause_id": self.clause_id,
            "clause_title": self.clause_title,
            "flagged_text": self.flagged_text,
            "matched_patterns": self.matched_patterns,
            "legal_danger": self.legal_danger,
            "business_impact": self.business_impact,
            "recommended_mitigation": self.recommended_mitigation,
            "penalty_score": self.penalty_score,
        }


class TrapDetector:
    """
    Identifies high-risk legal clauses, anti-consumer stipulations,
    and one-sided commercial traps across 8 predefined categories.
    """

    TRAP_RULES = {
        TrapCategory.UNILATERAL_MODIFICATION: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 30.0,
            "danger": "Allows the vendor to unilaterally change pricing, service terms, or privacy commitments without prior customer consent or notice.",
            "impact": "You could face sudden price hikes or downgraded SLA with no legal breach recourse.",
            "mitigation": "Demand 30-day prior written notice for material changes, with right to terminate and receive a pro-rata refund.",
            "patterns": [
                (re.compile(r"\b(?:modify|change|update|alter|amend)\s+(?:these\s+terms(?:\s+of\s+service)?|this\s+agreement|the\s+service|terms)\b.*?\b(?:at\s+any\s+time|without\s+(?:prior\s+)?notice|in\s+(?:our|its)\s+sole\s+discretion)\b", re.I), 1.0),
                (re.compile(r"\b(?:reserves\s+the\s+right\s+to\s+(?:modify|change|alter|update))\b.*?\b(?:without\s+prior\s+notice|effective\s+immediately|sole\s+discretion)\b", re.I), 0.95),
                (re.compile(r"\b(?:your\s+continued\s+use\s+(?:of\s+the\s+service)?\s+constitutes\s+acceptance\s+of\s+(?:the\s+)?modified\s+terms)\b", re.I), 0.90),
                (re.compile(r"\b(?:we\s+may\s+revise|we\s+may\s+update)\s+these\s+terms\s+periodically\s+without\s+obligation\s+to\s+notify\b", re.I), 0.85),
            ],
        },
        TrapCategory.ASYMMETRIC_INDEMNIFICATION: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 35.0,
            "danger": "Forces you to defend and pay all legal damages for the vendor, while the vendor offers zero indemnification for their own software defects or IP infringement.",
            "impact": "Exposure to uncapped third-party lawsuit defense costs and unlimited financial liability.",
            "mitigation": "Convert to a mutual indemnification with an explicit aggregate dollar liability cap (e.g., 12 months of fees paid).",
            "patterns": [
                (re.compile(r"\b(?:customer|user|you)\s+shall\s+indemnify,\s*defend\s+and\s+hold\s+harmless\b.*?\b(?:from\s+any\s+and\s+all\s+claims|against\s+all\s+losses)\b", re.I), 0.95),
                (re.compile(r"\b(?:hold\s+harmless\s+(?:company|vendor|us|licensor))\s+from\s+and\s+against\s+any\s+(?:damages|liabilities|costs|attorney['’]?s\s+fees)\b", re.I), 0.90),
                (re.compile(r"\b(?:indemnify\s+(?:us|the\s+company)\s+for\s+any\s+breach)\b", re.I), 0.80),
                (re.compile(r"\b(?:uncapped\s+indemnification|solely\s+responsible\s+for\s+all\s+third-party\s+claims)\b", re.I), 0.85),
            ],
        },
        TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER: {
            "severity": RiskSeverity.HIGH,
            "penalty": 25.0,
            "danger": "Strips your constitutional right to a jury trial and prevents you from joining class action lawsuits against deceptive or unlawful practices.",
            "impact": "Expensive confidential private arbitration in the vendor's chosen jurisdiction.",
            "mitigation": "Include an opt-out window (e.g. 30 days post sign-up) or preserve small-claims court and jury access.",
            "patterns": [
                (re.compile(r"\b(?:waive\s+any\s+right\s+to\s+a\s+jury\s+trial|waiver\s+of\s+jury\s+trial)\b", re.I), 0.95),
                (re.compile(r"\b(?:waive\s+any\s+right\s+to\s+(?:bring|participate\s+in)\s+a\s+class\s+action|class\s+action\s+waiver)\b", re.I), 0.95),
                (re.compile(r"\b(?:exclusively\s+resolved\s+by\s+binding\s+arbitration|shall\s+be\s+settled\s+by\s+arbitration)\b", re.I), 0.85),
                (re.compile(r"\b(?:individual\s+capacity\s+and\s+not\s+as\s+a\s+plaintiff\s+or\s+class\s+member)\b", re.I), 0.90),
            ],
        },
        TrapCategory.AGGRESSIVE_IP_EXPROPRIATION: {
            "severity": RiskSeverity.HIGH,
            "penalty": 28.0,
            "danger": "Claims broad perpetual assignment or ownership of customer feedback, uploaded data, workflow customizations, or invented concepts.",
            "impact": "Loss of trade secret protections and inadvertent assignment of your proprietary inventions to the vendor.",
            "mitigation": "Restrict grant to a non-exclusive license solely needed to operate the service; clarify all customer IP remains customer property.",
            "patterns": [
                (re.compile(r"\b(?:you\s+irrevocably\s+assign\s+to\s+(?:us|company)|all\s+feedback\s+shall\s+be\s+the\s+sole\s+property\s+of)\b", re.I), 0.95),
                (re.compile(r"\b(?:grant\s+(?:us|the\s+company)\s+a\s+perpetual,\s*irrevocable,\s*royalty-free,\s*worldwide\s+license\s+to\s+(?:use|reproduce|modify|distribute|exploit))\b", re.I), 0.90),
                (re.compile(r"\b(?:all\s+improvements,\s*modifications,\s*or\s+derivative\s+works\s+shall\s+belong\s+exclusively\s+to\s+company)\b", re.I), 0.88),
                (re.compile(r"\b(?:waive\s+all\s+moral\s+rights|work\s+made\s+for\s+hire\s+for\s+all\s+customer\s+submissions)\b", re.I), 0.82),
            ],
        },
        TrapCategory.PERPETUAL_DATA_AI_HARVESTING: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 32.0,
            "danger": "Grants the vendor rights to ingest confidential customer business data, customer inputs, or proprietary text to train commercial AI/LLM models.",
            "impact": "Proprietary confidential data could leak through generative AI outputs to competitors.",
            "mitigation": "Explicit Zero-Data-Retention & No-AI-Training clause for customer proprietary content.",
            "patterns": [
                (re.compile(r"\b(?:use\s+(?:your\s+data|customer\s+content|user\s+submissions|data|content)\b.*?\b(?:train|fine-tune|develop|improve)\b.*?\b(?:machine\s+learning|ai|artificial\s+intelligence|algorithms|neural\s+networks|large\s+language\s+models|models))\b", re.I), 0.98),
                (re.compile(r"\b(?:train|fine-tune|retrain)\b.*?\b(?:our|third-party)?\s*(?:models|ai|llms|neural\s+networks|algorithms)\b", re.I), 0.95),
                (re.compile(r"\b(?:perpetual|irrevocable)\b.*?\b(?:aggregate,\s*de-identify,\s*and\s*monetize|license\s+to\s+use\s+.*?\s+to\s+train)\b", re.I), 0.90),
                (re.compile(r"\b(?:incorporate\s+data\s+into\s+generalized\s+models|train\s+commercial\s+ai)\b", re.I), 0.85),
            ],
        },
        TrapCategory.TRAPPED_AUTO_RENEWAL: {
            "severity": RiskSeverity.MEDIUM,
            "penalty": 20.0,
            "danger": "Locks you into automatic multi-year renewals unless notice is served in an unreasonably narrow or restrictive window (e.g. exactly 60-90 days prior via certified mail).",
            "impact": "Unplanned recurring expenditures and inability to terminate contracts upon poor service delivery.",
            "mitigation": "Require vendor reminder notification 30 days prior to renewal with easy 1-click in-app cancellation.",
            "patterns": [
                (re.compile(r"\b(?:automatically\s+renews?|auto-renews?)\b.*?\b(?:successive|multi-year|additional\s+period)\b", re.I), 0.90),
                (re.compile(r"\b(?:at\s+least\s+(?:30|60|90|120)\s+days\s+prior\s+to\s+(?:the\s+end\s+of\s+the\s+term|expiration|renewal))\b", re.I), 0.85),
                (re.compile(r"\b(?:fees\s+paid\s+are\s+strictly\s+non-refundable|strictly\s+non-refundable|non-refundable\s+under\s+any\s+circumstance)\b", re.I), 0.80),
                (re.compile(r"\b(?:certified\s+(?:postal\s+)?mail\s+at\s+least|registered\s+mail\s+notice)\b", re.I), 0.85),
            ],
        },
        TrapCategory.OVERBROAD_NON_COMPETE: {
            "severity": RiskSeverity.HIGH,
            "penalty": 26.0,
            "danger": "Imposes overly restrictive post-termination employment, contracting, or commercial business restrictions across wide geographies and durations.",
            "impact": "Bars you from working in your field or consulting for competitors for months or years.",
            "mitigation": "Limit scope strictly to direct solicitation of active clients or eliminate post-employment non-competes in accordance with modern FTC guidelines.",
            "patterns": [
                (re.compile(r"\b(?:shall\s+not\s+(?:directly\s+or\s+indirectly\s+)?engage\s+in\s+any\s+competing\s+business|non-compete|competing\s+business)\b", re.I), 0.95),
                (re.compile(r"\b(?:for\s+a\s+period\s+of\s+(?:1|2|3|4|5)\s+years?\s+following\s+(?:the\s+)?termination)\b", re.I), 0.90),
                (re.compile(r"\b(?:anywhere\s+in\s+the\s+(?:world|united\s+states|territory)|worldwide\s+(?:geographic\s+)?scope|worldwide\s+for\s+a\s+period)\b", re.I), 0.88),
                (re.compile(r"\b(?:prohibited\s+from\s+working\s+for\s+any\s+entity|operating\s+in\s+the\s+same\s+industry)\b", re.I), 0.92),
            ],
        },
        TrapCategory.ZERO_LIABILITY_GUTTING: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 30.0,
            "danger": "Vendor totally disclaims all direct and indirect liability, capping total exposure to $0, $50, or trivial amounts even in cases of gross negligence or data breach.",
            "impact": "You have zero financial recovery if the vendor causes catastrophic data loss or downtime.",
            "mitigation": "Add a standard cap equal to 12 months fees paid, with carve-outs for data breach, confidentiality, and gross negligence.",
            "patterns": [
                (re.compile(r"\b(?:in\s+no\s+event\s+shall\s+.*?\b(?:aggregate|total|cumulative)?\s*liability\s+exceed\s+(?:\$|usd\s*)[0-9]{1,3})\b", re.I), 0.98),
                (re.compile(r"\b(?:liability\s+shall\s+not\s+exceed\s+(?:fifty\s+dollars|one\s+hundred\s+dollars|\$50|\$100|the\s+amount\s+of\s+\$0|\$0))\b", re.I), 0.95),
                (re.compile(r"\b(?:exceed\s+\$50\s+\(fifty\s+dollars\))\b", re.I), 0.99),
                (re.compile(r"\b(?:provided\s+strictly\s+[\"']as\s+is[\"']\s+and\s+[\"']as\s+available[\"']\s+without\s+warranty)\b", re.I), 0.88),
                (re.compile(r"\b(?:disclaims\s+all\s+liability\s+for\s+any\s+loss\s+of\s+data,\s*outage|security\s+breaches)\b", re.I), 0.92),
            ],
        },
    }

    def detect_traps_in_clause(self, clause: ContractClause) -> List[TrapMatch]:
        """Scans a single clause for all trap categories and returns list of matched traps."""
        matches: List[TrapMatch] = []
        clause_text = clause.text

        for trap_cat, rule in self.TRAP_RULES.items():
            matched_pats = []
            max_conf = 0.0

            for pattern, weight in rule["patterns"]:
                found = pattern.findall(clause_text)
                if found:
                    for f in found:
                        match_str = f if isinstance(f, str) else " ".join(f)
                        matched_pats.append(match_str)
                    if weight > max_conf:
                        max_conf = weight

            if matched_pats:
                # Deduplicate matched patterns
                unique_pats = list(dict.fromkeys(matched_pats))[:4]
                
                # Dynamic severity adjustment based on confidence
                severity = rule["severity"]
                if max_conf < 0.85 and severity == RiskSeverity.CRITICAL:
                    severity = RiskSeverity.HIGH

                trap_id = f"trap_{clause.clause_id}_{trap_cat.name.lower()}"

                match = TrapMatch(
                    trap_id=trap_id,
                    category=trap_cat,
                    severity=severity,
                    confidence=round(max_conf, 2),
                    clause_id=clause.clause_id,
                    clause_title=clause.title,
                    flagged_text=clause_text,
                    matched_patterns=unique_pats,
                    legal_danger=rule["danger"],
                    business_impact=rule["impact"],
                    recommended_mitigation=rule["mitigation"],
                    penalty_score=rule["penalty"] * max_conf,
                )
                matches.append(match)

        return matches

    def scan_contract(self, clauses: List[ContractClause]) -> Dict[str, Any]:
        """
        Scans all clauses in a contract, returning all detected traps,
        per-clause risk level, and category distribution.
        """
        all_traps: List[TrapMatch] = []
        clause_trap_map: Dict[str, List[TrapMatch]] = {}
        category_summary: Dict[str, int] = {cat.value: 0 for cat in TrapCategory}
        severity_summary: Dict[str, int] = {sev.value: 0 for sev in RiskSeverity}

        for clause in clauses:
            traps = self.detect_traps_in_clause(clause)
            clause_trap_map[clause.clause_id] = traps
            for t in traps:
                all_traps.append(t)
                category_summary[t.category.value] += 1
                severity_summary[t.severity.value] += 1

        return {
            "total_traps": len(all_traps),
            "traps": all_traps,
            "clause_trap_map": clause_trap_map,
            "category_summary": category_summary,
            "severity_summary": severity_summary,
        }
