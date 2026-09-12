"""
Trap & Dark Pattern Detector
Scans legal clauses for 8 predatory contract patterns with high-precision contextual matching,
safeguard filters (false-positive prevention), and calibrated risk penalties.
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
    safeguards_found: List[str]
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
            "safeguards_found": self.safeguards_found,
            "legal_danger": self.legal_danger,
            "business_impact": self.business_impact,
            "recommended_mitigation": self.recommended_mitigation,
            "penalty_score": self.penalty_score,
        }


class TrapDetector:
    """
    High-accuracy identification of predatory legal clauses, anti-consumer stipulations,
    and dark patterns across 8 predefined categories with false-positive safeguard protection.
    """

    TRAP_RULES = {
        TrapCategory.UNILATERAL_MODIFICATION: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 30.0,
            "danger": "Allows the vendor to unilaterally change pricing, service terms, or privacy commitments without prior customer consent or notice.",
            "impact": "You could face sudden price hikes, downgraded SLAs, or feature removals with no breach-of-contract recourse.",
            "mitigation": "Demand 30-day prior written notice for material changes, with right to terminate and receive a pro-rata refund.",
            "patterns": [
                (re.compile(r"\b(?:modify|change|update|alter|amend|revise|suspend|discontinue)\s+(?:any\s+of\s+)?(?:these\s+terms(?:\s+of\s+service)?|this\s+agreement(?:['’]?s\s+terms)?|the\s+(?:[a-z0-9]+\s+)?services?|terms|policies)\b.*?\b(?:at\s+any\s+time|without\s+(?:prior\s+)?notice|in\s+(?:our|its)\s+sole\s+discretion|from\s+time\s+to\s+time\s+without\s+notice)\b", re.I), 1.0),
                (re.compile(r"\b(?:change,\s*suspend,\s*or\s*discontinue\s+.*?\s+at\s+any\s+time\s+without\s+notice)\b", re.I), 0.98),
                (re.compile(r"\b(?:amend\s+(?:any\s+of\s+)?(?:this\s+agreement['’]?s\s+terms|these\s+terms|the\s+agreement))\b.*?\b(?:sole\s+discretion|by\s+posting|without\s+notice)\b", re.I), 0.96),
                (re.compile(r"\b(?:reserves\s+the\s+right\s+to\s+(?:modify|change|alter|update|revise|amend|suspend|discontinue))\b.*?\b(?:without\s+prior\s+notice|effective\s+immediately|sole\s+(?:and\s+absolute\s+)?discretion|at\s+any\s+time)\b", re.I), 0.95),
                (re.compile(r"\b(?:reserves?\s+the\s+right\s+to\s+(?:accept|reject|cancel|waive(?:\s+off)?|modify|alter|change|amend|update))\b.*?\b(?:time\s+window|fee|fees|pricing|terms|policies|policy|cancellation|cancellations|order|orders)\b.*?\b(?:from\s+time\s+to\s+time|at\s+(?:our|its)\s+discretion|without\s+(?:prior\s+)?notice)?", re.I), 0.90),
                (re.compile(r"\b(?:communicated\s+to\s+you\s+periodically|determined\s+by\s+the\s+(?:company|platform))\b", re.I), 0.85),
                (re.compile(r"\b(?:your\s+continued\s+use\s+(?:of\s+.*?|after\s+.*?)\s*(?:constitutes|shall\s+be\s+deemed|implies)\s+(?:your\s+)?acceptance\s+of\s+(?:the\s+)?(?:modified|new|updated|revised)\s+terms)\b", re.I), 0.94),
                (re.compile(r"\b(?:we\s+may\s+revise|we\s+may\s+update|we\s+may\s+change)\s+(?:these\s+terms|this\s+agreement)\s+(?:periodically\s+)?without\s+(?:prior\s+)?(?:obligation\s+to\s+notify|notice)\b", re.I), 0.90),
                (re.compile(r"\b(?:subject\s+to\s+change\s+without\s+(?:prior\s+)?notice)\b", re.I), 0.85),
                (re.compile(r"\b(?:modifications\s+shall\s+become\s+effective\s+immediately\s+upon\s+posting)\b", re.I), 0.88),
                (re.compile(r"\b(?:by\s+continuing\s+to\s+access\s+or\s+use\s+.*?after\s+(?:those\s+)?revisions\s+become\s+effective,\s+you\s+agree\s+to\s+be\s+bound)\b", re.I), 0.90),
            ],
            "safeguards": [
                (re.compile(r"\b(?:at\s+least\s+(?:30|60)\s+days\s+prior\s+written\s+notice)\b", re.I), "Requires 30+ days prior written notice"),
                (re.compile(r"\b(?:may\s+terminate\s+.*?pro-rata\s+refund)\b", re.I), "Includes pro-rata refund upon termination"),
                (re.compile(r"\b(?:written\s+instrument\s+signed\s+by\s+both\s+parties|mutual\s+written\s+agreement)\b", re.I), "Requires mutual written agreement"),
            ],
        },
        TrapCategory.ASYMMETRIC_INDEMNIFICATION: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 35.0,
            "danger": "Forces you to defend and pay all legal damages for the vendor, while the vendor offers zero indemnification for their own software defects, negligence, or IP infringement.",
            "impact": "Exposure to uncapped third-party lawsuit defense costs and unlimited financial liability.",
            "mitigation": "Convert to a mutual indemnification with an explicit aggregate dollar liability cap (e.g., 12 months of fees paid).",
            "patterns": [
                (re.compile(r"\b(?:customer|user|you|subscriber|client)\s+(?:shall|agrees?\s+to)\s+(?:indemnify,\s*defend\s+and\s+hold\s+harmless|defend,\s*indemnify\s+and\s+hold\s+harmless)\b.*?\b(?:from\s+any\s+and\s+all\s+claims|against\s+all\s+losses|from\s+all\s+damages|against\s+any\s+claims)\b", re.I), 0.98),
                (re.compile(r"\b(?:hold\s+harmless\s+(?:company|vendor|us|licensor|platform|provider|affiliates))\s+from\s+and\s+against\s+any\s+(?:damages|liabilities|costs|losses|judgments|attorney['’]?s\s+fees|claims)\b", re.I), 0.92),
                (re.compile(r"\b(?:indemnify\s+(?:us|the\s+company|licensor|provider)\s+for\s+any\s+(?:breach|violation|misuse))\b", re.I), 0.85),
                (re.compile(r"\b(?:uncapped\s+indemnification|solely\s+responsible\s+for\s+all\s+third-party\s+claims)\b", re.I), 0.90),
                (re.compile(r"\b(?:agree\s+to\s+defend,\s*indemnify,\s*and\s+hold\s+harmless\s+(?:the\s+company|us|each\s+of\s+our\s+affiliates))\b", re.I), 0.92),
                (re.compile(r"\b(?:at\s+your\s+sole\s+expense,\s*defend|shall\s+bear\s+all\s+costs\s+of\s+defense)\b", re.I), 0.88),
            ],
            "safeguards": [
                (re.compile(r"\b(?:each\s+party\s+agrees\s+to\s+defend,\s*indemnify|mutual\s+indemnif\w+)\b", re.I), "Mutual bilateral indemnification"),
                (re.compile(r"\b(?:company\s+shall\s+indemnify\s+(?:customer|user)\s+for\s+infringement)\b", re.I), "Vendor IP infringement indemnity present"),
                (re.compile(r"\b(?:subject\s+to\s+the\s+liability\s+cap|capped\s+at\s+twelve\s+\(12\)\s+months)\b", re.I), "Indemnity bounded by liability cap"),
            ],
        },
        TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER: {
            "severity": RiskSeverity.HIGH,
            "penalty": 25.0,
            "danger": "Strips your constitutional right to a jury trial and prevents you from joining class action lawsuits against deceptive, predatory, or unlawful corporate practices.",
            "impact": "Forces expensive confidential private arbitration in the vendor's chosen jurisdiction.",
            "mitigation": "Include an opt-out window (e.g. 30 days post sign-up) or preserve small-claims court and jury access.",
            "patterns": [
                (re.compile(r"\b(?:waive\s+any\s+right\s+to\s+a\s+jury\s+trial|waiver\s+of\s+jury\s+trial|waive\s+the\s+right\s+to\s+trial\s+by\s+jury)\b", re.I), 0.98),
                (re.compile(r"\b(?:waive\s+any\s+right\s+to\s+(?:bring|participate\s+in|join)\s+a\s+class\s+action|class\s+action\s+waiver|no\s+class\s+actions?)\b", re.I), 0.98),
                (re.compile(r"\b(?:exclusively\s+resolved\s+by\s+binding\s+arbitration|shall\s+be\s+settled\s+by\s+arbitration|mandatory\s+binding\s+arbitration|is\s+subject\s+to\s+(?:the\s+)?binding\s+arbitration)\b", re.I), 0.95),
                (re.compile(r"\b(?:disputes?\/binding\s+arbitration|binding\s+arbitration,\s*governing\s+law)\b", re.I), 0.92),
                (re.compile(r"\b(?:individual\s+capacity\s+and\s+not\s+as\s+a\s+plaintiff\s+or\s+class\s+member|not\s+as\s+a\s+class\s+representative)\b", re.I), 0.95),
                (re.compile(r"\b(?:arbitrator\s+may\s+not\s+consolidate\s+more\s+than\s+one\s+person['’]?s\s+claims|class\s+arbitrations?\s+are\s+not\s+permitted)\b", re.I), 0.92),
                (re.compile(r"\b(?:waive\s+any\s+constitutional\s+and\s+statutory\s+rights\s+to\s+go\s+to\s+court)\b", re.I), 0.96),
                (re.compile(r"\b(?:under\s+the\s+commercial\s+arbitration\s+rules\s+of\s+the\s+american\s+arbitration\s+association|jams\s+comprehensive\s+arbitration)\b", re.I), 0.85),
            ],
            "safeguards": [
                (re.compile(r"\b(?:you\s+may\s+opt\s*out\s+of\s+this\s+arbitration\s+agreement\s+within\s+(?:30|60)\s+days)\b", re.I), "Provides 30-day arbitration opt-out"),
                (re.compile(r"\b(?:either\s+party\s+may\s+bring\s+an\s+action\s+in\s+small\s+claims\s+court)\b", re.I), "Small-claims court access preserved"),
                (re.compile(r"\b(?:court\s+of\s+competent\s+jurisdiction\s+preserving\s+constitutional\s+rights)\b", re.I), "Full court jurisdiction preserved"),
            ],
        },
        TrapCategory.AGGRESSIVE_IP_EXPROPRIATION: {
            "severity": RiskSeverity.HIGH,
            "penalty": 28.0,
            "danger": "Claims broad perpetual assignment or ownership of customer feedback, uploaded data, workflow customizations, or invented concepts.",
            "impact": "Loss of trade secret protections and inadvertent assignment of your proprietary inventions to the vendor.",
            "mitigation": "Restrict grant to a non-exclusive license solely needed to operate the service; clarify all customer IP remains customer property.",
            "patterns": [
                (re.compile(r"\b(?:(?:you|employee|contractor|user|customer)\s+(?:hereby\s+)?(?:irrevocably\s+)?assigns?\s+to\s+(?:us|company|the\s+company|provider)|all\s+feedback\s+shall\s+be\s+the\s+sole\s+(?:and\s+exclusive\s+)?property\s+of)\b", re.I), 0.98),
                (re.compile(r"\b(?:grant\s+(?:us|the\s+company|provider)\s+a\s+perpetual,\s*irrevocable,\s*royalty-free,\s*worldwide\s+(?:transferable,\s*sublicensable\s+)?license\s+to\s+(?:use|reproduce|modify|distribute|exploit|display|create\s+derivative))\b", re.I), 0.94),
                (re.compile(r"\b(?:all\s+improvements,\s*modifications,\s*customizations\s+or\s+derivative\s+works\s+shall\s+belong\s+exclusively\s+to\s+company)\b", re.I), 0.90),
                (re.compile(r"\b(?:waive\s+all\s+moral\s+rights|waives?\s+(?:any\s+)?moral\s+rights|work\s+made\s+for\s+hire\s+for\s+all\s+customer\s+submissions)\b", re.I), 0.88),
                (re.compile(r"\b(?:hereby\s+(?:irrevocably\s+)?assigns?\s+(?:and\s+agree\s+to\s+assign\s+)?all\s+(?:right,\s*title,\s*and\s+interest|inventions|ideas|customizations|intellectual\s+property|moral\s+rights))\b", re.I), 0.92),
                (re.compile(r"\b(?:free\s+of\s+any\s+moral\s+rights,\s*intellectual\s+property\s+rights\s+or\s+compensation)\b", re.I), 0.86),
            ],
            "safeguards": [
                (re.compile(r"\b(?:customer\s+retains\s+all\s+right,\s*title,\s*and\s+interest|customer\s+owns\s+all\s+customer\s+data)\b", re.I), "Explicit customer ownership guarantee"),
                (re.compile(r"\b(?:solely\s+to\s+the\s+extent\s+necessary\s+to\s+provide\s+the\s+services)\b", re.I), "License limited to service delivery"),
                (re.compile(r"\b(?:non-exclusive,\s*revocable\s+license)\b", re.I), "Revocable non-exclusive license"),
            ],
        },
        TrapCategory.PERPETUAL_DATA_AI_HARVESTING: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 32.0,
            "danger": "Grants the vendor rights to ingest confidential customer business data, private documents, voice input, or telemetry to train commercial AI models or monetization systems.",
            "impact": "Proprietary confidential data could leak through generative AI outputs to competitors.",
            "mitigation": "Explicit Zero-Data-Retention & No-AI-Training clause for customer proprietary content.",
            "patterns": [
                (re.compile(r"\b(?:use\s+(?:your\s+data|customer\s+content|user\s+submissions|data|content|inputs|prompts)\b.*?\b(?:train|fine-tune|develop|improve|calibrate|train\s+and\s+improve)\b.*?\b(?:machine\s+learning|ai|artificial\s+intelligence|algorithms|neural\s+networks|large\s+language\s+models|models|generative\s+ai))\b", re.I), 0.98),
                (re.compile(r"\b(?:train|fine-tune|retrain|evaluate)\b.*?\b(?:our|third-party|proprietary)?\s*(?:models|ai|llms|neural\s+networks|algorithms|generative\s+models)\b", re.I), 0.95),
                (re.compile(r"\b(?:process\s+(?:your\s+)?(?:voice\s+input|voice\s+recordings?|location|biometric|search\s+queries|viewing\s+and\s+usage\s+data)\s+in\s+the\s+cloud\s+to\s+(?:respond|improve|train))\b", re.I), 0.92),
                (re.compile(r"\b(?:stored\s+on\s+servers\s+outside\s+the\s+country\s+in\s+which\s+you\s+live)\b", re.I), 0.88),
                (re.compile(r"\b(?:read|access|collect|scrape)\s+(?:your\s+)?(?:private\s+)?(?:contacts|contact\s+list|address\s+book|photo\s+gallery|camera|microphone)\b", re.I), 0.98),
                (re.compile(r"\b(?:perpetual|irrevocable)\b.*?\b(?:aggregate,\s*de-identify,\s*and\s*monetize|license\s+to\s+use\s+.*?\s+to\s+train|ingest\s+content\s+for\s+ai)\b", re.I), 0.92),
                (re.compile(r"\b(?:incorporate\s+data\s+into\s+generalized\s+models|train\s+commercial\s+ai|extract\s+patterns\s+for\s+model\s+training)\b", re.I), 0.90),
                (re.compile(r"\b(?:train\s+our\s+algorithms|improve\s+our\s+machine\s+learning\s+capabilities\s+using\s+your\s+content)\b", re.I), 0.93),
                (re.compile(r"\b(?:analyze,\s*process,\s*and\s*utilize\s+user\s+content\s+to\s+train\s+artificial\s+intelligence)\b", re.I), 0.96),
            ],
            "safeguards": [
                (re.compile(r"\b(?:shall\s+NOT\s+be\s+used\s+to\s+train|will\s+not\s+use\s+customer\s+data\s+to\s+train\s+(?:ai|models|llms))\b", re.I), "Strict No-AI-Training covenant"),
                (re.compile(r"\b(?:zero-data-retention|zero\s+retention\s+guarantee|data\s+isolation)\b", re.I), "Zero data retention commitment"),
                (re.compile(r"\b(?:customer\s+opt-out\s+from\s+ai\s+training\s+enabled)\b", re.I), "AI training opt-out supported"),
            ],
        },
        TrapCategory.TRAPPED_AUTO_RENEWAL: {
            "severity": RiskSeverity.MEDIUM,
            "penalty": 20.0,
            "danger": "Locks you into automatic multi-year renewals or immediate unilateral access termination without a cure period.",
            "impact": "Unplanned recurring expenditures and sudden termination of service access.",
            "mitigation": "Require vendor reminder notification 30 days prior to renewal with easy 1-click in-app cancellation.",
            "patterns": [
                (re.compile(r"\b(?:automatically\s+renews?|auto-renews?|automatically\s+extend)\b.*?\b(?:successive|multi-year|additional\s+period|equal\s+length|subsequent\s+term)\b", re.I), 0.92),
                (re.compile(r"\b(?:at\s+least\s+(?:30|60|90|120)\s+days\s+prior\s+to\s+(?:the\s+end\s+of\s+the\s+(?:current\s+)?term|expiration|renewal))\b", re.I), 0.88),
                (re.compile(r"\b(?:fees\s+paid\s+are\s+strictly\s+non-refundable|strictly\s+non-refundable|non-refundable\s+under\s+any\s+circumstances?|no\s+refunds\s+or\s+credits)\b", re.I), 0.90),
                (re.compile(r"\b(?:automatically\s+terminate\s+without\s+notice\s+if\s+you\s+fail\s+to\s+comply)\b", re.I), 0.88),
                (re.compile(r"\b(?:non-cancellable\s+(?:bank\s+)?loan|auto-debit\s+mandate|nach\s+mandate|recurring\s+emi)\b", re.I), 0.95),
                (re.compile(r"\b(?:certified\s+(?:postal\s+)?mail\s+at\s+least|registered\s+mail\s+notice|written\s+notice\s+via\s+registered\s+post)\b", re.I), 0.88),
                (re.compile(r"\b(?:early\s+termination\s+fee|liquidated\s+damages\s+for\s+early\s+cancellation|accelerated\s+payment\s+of\s+all\s+remaining\s+fees)\b", re.I), 0.86),
                (re.compile(r"\b(?:authorizes\s+recurring\s+automatic\s+debits\s+without\s+further\s+authorization)\b", re.I), 0.85),
            ],
            "safeguards": [
                (re.compile(r"\b(?:vendor\s+must\s+provide\s+an\s+electronic\s+reminder\s+notice\s+at\s+least\s+30\s+days|reminder\s+notice\s+prior\s+to\s+renewal)\b", re.I), "Mandatory 30-day renewal reminder"),
                (re.compile(r"\b(?:cancel\s+at\s+any\s+time\s+via\s+(?:the\s+)?(?:web|app|online|settings|billing)\s+(?:management\s+)?console|1-click\s+cancellation)\b", re.I), "Easy self-service digital cancellation"),
                (re.compile(r"\b(?:pro-rata\s+refund\s+for\s+unused\s+period)\b", re.I), "Pro-rata refund guaranteed"),
            ],
        },
        TrapCategory.OVERBROAD_NON_COMPETE: {
            "severity": RiskSeverity.HIGH,
            "penalty": 26.0,
            "danger": "Imposes overly restrictive post-termination employment, contracting, or commercial business restrictions across wide geographies and durations.",
            "impact": "Bars you from working in your field or consulting for competitors for months or years.",
            "mitigation": "Limit scope strictly to direct solicitation of active clients or eliminate post-employment non-competes in accordance with modern FTC guidelines.",
            "patterns": [
                (re.compile(r"\b(?:shall\s+not\s+(?:directly\s+or\s+indirectly\s+)?engage\s+in\s+any\s+competing\s+business|non-compete|competing\s+business|competitive\s+enterprise)\b", re.I), 0.95),
                (re.compile(r"\b(?:for\s+a\s+period\s+of\s+(?:1|2|3|4|5|one|two|three|five)\s+years?\s+following\s+(?:the\s+)?(?:termination|separation|cessation))\b", re.I), 0.92),
                (re.compile(r"\b(?:anywhere\s+in\s+the\s+(?:world|united\s+states|territory|country|globe)|worldwide\s+(?:geographic\s+)?scope|worldwide\s+for\s+a\s+period)\b", re.I), 0.90),
                (re.compile(r"\b(?:prohibited\s+from\s+working\s+for\s+any\s+entity|operating\s+in\s+the\s+same\s+industry|perform\s+services\s+for\s+any\s+competitor)\b", re.I), 0.94),
                (re.compile(r"\b(?:covenants\s+not\s+to\s+compete|restriction\s+on\s+future\s+employment)\b", re.I), 0.88),
            ],
            "safeguards": [
                (re.compile(r"\b(?:nothing\s+in\s+this\s+agreement\s+shall\s+restrict\s+.*?from\s+engaging\s+in\s+their\s+trade|free\s+mobility)\b", re.I), "Free worker mobility guarantee"),
                (re.compile(r"\b(?:limited\s+solely\s+to\s+non-solicitation\s+of\s+key\s+personnel)\b", re.I), "Narrow non-solicitation only"),
                (re.compile(r"\b(?:in\s+accordance\s+with\s+ftc\s+non-compete\s+ban)\b", re.I), "FTC rule compliance"),
            ],
        },
        TrapCategory.ZERO_LIABILITY_GUTTING: {
            "severity": RiskSeverity.CRITICAL,
            "penalty": 30.0,
            "danger": "Vendor totally disclaims all direct and indirect liability, capping total exposure to $0, $50, or trivial amounts even in cases of gross negligence, data breach, or service collapse.",
            "impact": "You have zero financial recovery if the vendor causes catastrophic data loss or business downtime.",
            "mitigation": "Add a standard cap equal to 12 months fees paid, with carve-outs for data breach, confidentiality, and gross negligence.",
            "patterns": [
                (re.compile(r"\b(?:in\s+no\s+event\s+(?:shall|will)|under\s+no\s+circumstances\s+(?:shall|will))\s+.*?\b(?:aggregate|total|cumulative)?\s*liability\s+(?:shall\s+not\s+exceed|exceed|be\s+limited\s+to)\s+(?:fifty\s+dollars|one\s+hundred\s+dollars|\$|usd\s*|inr\s*|[0-9]{1,3}|\$[0-9]+)\b", re.I), 0.98),
                (re.compile(r"\b(?:liability\s+(?:shall\s+not\s+exceed|exceed|is\s+limited\s+to))\s+(?:fifty\s+dollars|one\s+hundred\s+dollars|\$50|\$100|\$0|the\s+amount\s+of\s+\$0|zero\s+dollars|\$[0-9]{1,3})\b", re.I), 0.96),
                (re.compile(r"\b(?:exceed\s+fifty\s+dollars\s*(?:\(\$50(?:\.00)?\))?|\$50\s*\(fifty\s+dollars\)|\$100\s*\(one\s+hundred\s+dollars\)|fifty\s+dollars\s+\(\$50(?:\.00)?\))\b", re.I), 0.99),
                (re.compile(r"\b(?:have\s+no\s+responsibility\s+or\s+liability\s+for\s+any\s+aspect\s+of|disclaims?\s+all\s+responsibility\s+or\s+liability)\b", re.I), 0.92),
                (re.compile(r"\b(?:provided\s+strictly\s+[\"']as\s+is[\"']\s+and\s+[\"']as\s+available[\"']\s+without\s+warranty|strictly\s+[\"']as\s+is[\"'])\b", re.I), 0.90),
                (re.compile(r"\b(?:non-cancellable\s+and\s+non-refundable|non-refundable\s+and\s+non-cancellable|strictly\s+non-refundable|all\s+orders?\s+are\s+non-cancellable|no\s+refunds?\s+shall\s+be\s+given)\b", re.I), 0.94),
                (re.compile(r"\b(?:disclaims\s+all\s+liability\s+for\s+any\s+loss\s+of\s+data,\s*outage|security\s+breaches|unauthorized\s+access)\b", re.I), 0.94),
                (re.compile(r"\b(?:under\s+no\s+circumstances\s+shall\s+(?:company|us|vendor)\s+be\s+liable\s+for\s+any\s+direct,\s*indirect,\s*incidental)\b", re.I), 0.92),
                (re.compile(r"\b(?:total\s+cumulative\s+liability\s+shall\s+be\s+limited\s+to\s+the\s+amount\s+paid\s+by\s+you\s+in\s+the\s+preceding\s+one\s+\(1\)\s+month)\b", re.I), 0.88),
            ],
            "safeguards": [
                (re.compile(r"\b(?:except\s+for\s+(?:indemnity\s+obligations|breaches\s+of\s+confidentiality|gross\s+negligence|willful\s+misconduct))\b", re.I), "Includes essential gross negligence / breach carve-outs"),
                (re.compile(r"\b(?:capped\s+at\s+(?:the\s+total\s+)?fees\s+paid\s+.*?in\s+the\s+twelve\s+\(12\)\s+months\s+preceding)\b", re.I), "Fair standard 12-month fee cap"),
            ],
        },
    }

    def detect_traps_in_clause(self, clause: ContractClause) -> List[TrapMatch]:
        """Scans a single clause for all trap categories with safeguard checking."""
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
                # Check for safeguards in this clause
                safeguards_found = []
                for sf_pat, sf_desc in rule.get("safeguards", []):
                    if sf_pat.search(clause_text):
                        safeguards_found.append(sf_desc)

                # If significant safeguards exist, calibrate confidence down or dismiss
                effective_conf = max_conf
                if len(safeguards_found) >= 2:
                    # Clause has comprehensive protections; false alarm
                    continue
                elif len(safeguards_found) == 1:
                    # Discount confidence and penalty
                    effective_conf = max(0.40, effective_conf * 0.6)

                # Deduplicate matched patterns
                unique_pats = list(dict.fromkeys(matched_pats))[:5]
                
                # Dynamic severity adjustment based on confidence
                severity = rule["severity"]
                if effective_conf < 0.70 and severity == RiskSeverity.CRITICAL:
                    severity = RiskSeverity.HIGH
                elif effective_conf < 0.50:
                    severity = RiskSeverity.MEDIUM

                trap_id = f"trap_{clause.clause_id}_{trap_cat.name.lower()}"
                calc_penalty = round(rule["penalty"] * effective_conf, 1)

                match = TrapMatch(
                    trap_id=trap_id,
                    category=trap_cat,
                    severity=severity,
                    confidence=round(effective_conf, 2),
                    clause_id=clause.clause_id,
                    clause_title=clause.title,
                    flagged_text=clause_text,
                    matched_patterns=unique_pats,
                    safeguards_found=safeguards_found,
                    legal_danger=rule["danger"],
                    business_impact=rule["impact"],
                    recommended_mitigation=rule["mitigation"],
                    penalty_score=calc_penalty,
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
