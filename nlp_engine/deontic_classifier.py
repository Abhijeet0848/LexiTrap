"""
Deontic Logic Classifier & Contract Asymmetry Engine
Extracts normative modalities: Obligation, Prohibition, Permission, Warranty, Disclaimer.
Extracts duty actors (User vs Vendor) to measure structural contractual asymmetry.
"""

import re
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from .parser import ContractClause


class DeonticCategory(str, Enum):
    OBLIGATION = "Obligation"
    PROHIBITION = "Prohibition"
    PERMISSION = "Permission"
    WARRANTY = "Warranty"
    DISCLAIMER = "Disclaimer"
    NEUTRAL = "Informational / Declarative"


class DutyActor(str, Enum):
    CUSTOMER_USER = "Customer / User / Employee"
    VENDOR_COMPANY = "Vendor / Company / Licensor"
    MUTUAL = "Mutual / Both Parties"
    UNKNOWN = "General / Unspecified"


class DeonticClassifier:
    """
    Classifies legal sentences and clauses into deontic modality categories
    using contextual pattern weighting, modal auxiliary analysis, and actor assignment.
    """

    USER_ACTOR_PATTERNS = [
        re.compile(r"\b(?:you|your|user|customer|subscriber|client|employee|recipient|buyer|borrower|consumer|licensee)\b", re.I),
    ]

    VENDOR_ACTOR_PATTERNS = [
        re.compile(r"\b(?:we|us|our|company|vendor|provider|licensor|discloser|bank|lender|platform|service\s+provider)\b", re.I),
    ]

    MUTUAL_ACTOR_PATTERNS = [
        re.compile(r"\b(?:each\s+party|both\s+parties|neither\s+party|either\s+party|the\s+parties)\b", re.I),
    ]

    MODAL_PATTERNS = {
        DeonticCategory.PROHIBITION: [
            (re.compile(r"\b(?:shall\s+not|must\s+not|may\s+not|will\s+not|cannot|should\s+not)\b", re.I), 4.5),
            (re.compile(r"\b(?:is\s+prohibited\s+from|are\s+prohibited\s+from|prohibited\s+from)\b", re.I), 4.5),
            (re.compile(r"\b(?:under\s+no\s+circumstances\s+shall|in\s+no\s+event\s+shall)\b", re.I), 4.5),
            (re.compile(r"\b(?:strictly\s+forbidden|not\s+permitted\s+to|shall\s+refrain\s+from)\b", re.I), 4.0),
            (re.compile(r"\b(?:waives\s+any\s+right|relinquishes\s+any\s+claim|forfeits\s+any\s+right)\b", re.I), 3.5),
            (re.compile(r"\b(?:no\s+license\s+is\s+granted|no\s+rights\s+are\s+conveyed)\b", re.I), 3.0),
        ],
        DeonticCategory.OBLIGATION: [
            (re.compile(r"\b(?:shall(?!\s+not)|must(?!\s+not)|will(?!\s+not)|is\s+required\s+to|are\s+required\s+to)\b", re.I), 3.2),
            (re.compile(r"\b(?:agrees\s+to|undertakes\s+to|covenants\s+to|hereby\s+agrees)\b", re.I), 2.8),
            (re.compile(r"\b(?:is\s+obligated\s+to|are\s+obligated\s+to|bound\s+to|compelled\s+to)\b", re.I), 3.0),
            (re.compile(r"\b(?:will\s+promptly|shall\s+immediately|shall\s+cause|is\s+responsible\s+for)\b", re.I), 3.2),
            (re.compile(r"\b(?:duty\s+to|responsible\s+for\s+ensuring|assumes\s+full\s+responsibility)\b", re.I), 2.5),
            (re.compile(r"\b(?:indemnify(?:,\s*defend)?\s+and\s+hold\s+harmless|shall\s+defend|shall\s+reimburse)\b", re.I), 3.5),
        ],
        DeonticCategory.PERMISSION: [
            (re.compile(r"\b(?:may|is\s+permitted\s+to|are\s+permitted\s+to|is\s+authorized\s+to)\b", re.I), 2.5),
            (re.compile(r"\b(?:is\s+entitled\s+to|are\s+entitled\s+to|has\s+the\s+right\s+to|have\s+the\s+right\s+to)\b", re.I), 2.8),
            (re.compile(r"\b(?:at\s+its\s+sole\s+discretion|in\s+its\s+discretion|sole\s+and\s+absolute\s+discretion)\b", re.I), 3.5),
            (re.compile(r"\b(?:reserves\s+the\s+right\s+to|reserves\s+all\s+rights\s+to|reserves\s+discretion)\b", re.I), 3.2),
            (re.compile(r"\b(?:can|optional\s+to|has\s+liberty\s+to|at\s+any\s+time\s+elect)\b", re.I), 2.0),
        ],
        DeonticCategory.WARRANTY: [
            (re.compile(r"\b(?:warrants\s+and\s+represents|represents\s+and\s+warrants)\b", re.I), 4.0),
            (re.compile(r"\b(?:warrants\s+that|represents\s+that|guarantees\s+that)\b", re.I), 3.5),
            (re.compile(r"\b(?:express\s+warranty|implied\s+warranty|merchantability)\b", re.I), 2.8),
            (re.compile(r"\b(?:fitness\s+for\s+a\s+particular\s+purpose|freedom\s+from\s+defects)\b", re.I), 2.5),
            (re.compile(r"\b(?:certifies\s+that|covenants\s+that)\b", re.I), 2.5),
        ],
        DeonticCategory.DISCLAIMER: [
            (re.compile(r"\b(?:as\s+is|with\s+all\s+faults|as\s+available)\b", re.I), 4.0),
            (re.compile(r"\b(?:disclaims\s+all\s+warranties|disclaims\s+any\s+liability|disclaims\s+all\s+implied)\b", re.I), 4.0),
            (re.compile(r"\b(?:in\s+no\s+event\s+shall\s+.*?\s+be\s+liable|shall\s+not\s+be\s+liable\s+for)\b", re.I), 3.5),
            (re.compile(r"\b(?:without\s+warranty\s+of\s+any\s+kind|no\s+representations\s+or\s+warranties)\b", re.I), 3.8),
            (re.compile(r"\b(?:no\s+liability\s+for|not\s+responsible\s+for|at\s+your\s+own\s+risk)\b", re.I), 3.0),
            (re.compile(r"\b(?:consequential,\s*incidental,\s*special|punitive\s+damages|indirect\s+damages)\b", re.I), 3.0),
        ],
    }

    def detect_actor(self, sentence: str) -> DutyActor:
        """Determines who is the primary subject / duty bearer in the sentence."""
        # Check mutual first
        for pat in self.MUTUAL_ACTOR_PATTERNS:
            if pat.search(sentence):
                return DutyActor.MUTUAL

        user_match = any(pat.search(sentence) for pat in self.USER_ACTOR_PATTERNS)
        vendor_match = any(pat.search(sentence) for pat in self.VENDOR_ACTOR_PATTERNS)

        if user_match and not vendor_match:
            return DutyActor.CUSTOMER_USER
        elif vendor_match and not user_match:
            return DutyActor.VENDOR_COMPANY
        elif user_match and vendor_match:
            # Check subject position (first occurrence before verb/modal)
            u_pos = min((m.start() for pat in self.USER_ACTOR_PATTERNS for m in pat.finditer(sentence)), default=999)
            v_pos = min((m.start() for pat in self.VENDOR_ACTOR_PATTERNS for m in pat.finditer(sentence)), default=999)
            if u_pos < v_pos:
                return DutyActor.CUSTOMER_USER
            else:
                return DutyActor.VENDOR_COMPANY
        return DutyActor.UNKNOWN

    def classify_sentence(self, sentence: str) -> Dict[str, Any]:
        """Classifies an individual sentence into a deontic modality and identifies actor."""
        scores: Dict[DeonticCategory, float] = {cat: 0.0 for cat in DeonticCategory if cat != DeonticCategory.NEUTRAL}
        matched_markers: List[Dict[str, str]] = []

        for category, patterns in self.MODAL_PATTERNS.items():
            for regex, weight in patterns:
                matches = regex.findall(sentence)
                if matches:
                    scores[category] += weight * len(matches)
                    for m in matches:
                        match_text = m if isinstance(m, str) else m[0]
                        matched_markers.append({
                            "marker": match_text,
                            "category": category.value,
                            "weight": weight
                        })

        top_category = DeonticCategory.NEUTRAL
        top_score = 0.0
        for cat, score in scores.items():
            if score > top_score:
                top_score = score
                top_category = cat

        # Compute confidence score (0 to 1)
        confidence = min(round(top_score / 4.0, 2), 1.0) if top_score > 0 else 0.5
        actor = self.detect_actor(sentence)

        return {
            "sentence": sentence,
            "category": top_category.value,
            "confidence": confidence,
            "score": round(top_score, 2),
            "actor": actor.value,
            "markers": matched_markers,
        }

    def classify_clause(self, clause: ContractClause) -> Dict[str, Any]:
        """
        Aggregates sentence-level classifications to provide clause-level deontic profile.
        """
        sentence_results = [self.classify_sentence(s) for s in clause.sentences]
        
        category_counts: Dict[str, int] = {}
        actor_counts: Dict[str, int] = {}

        for r in sentence_results:
            cat = r["category"]
            act = r["actor"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            actor_counts[act] = actor_counts.get(act, 0) + 1

        # Dominant category (excluding neutral unless all neutral)
        non_neutral = {k: v for k, v in category_counts.items() if k != DeonticCategory.NEUTRAL.value}
        if non_neutral:
            dominant_category = max(non_neutral, key=non_neutral.get)
        else:
            dominant_category = DeonticCategory.NEUTRAL.value

        all_markers = []
        for r in sentence_results:
            all_markers.extend(r["markers"])

        return {
            "clause_id": clause.clause_id,
            "dominant_category": dominant_category,
            "category_breakdown": category_counts,
            "actor_breakdown": actor_counts,
            "sentence_classifications": sentence_results,
            "total_markers": len(all_markers),
            "markers": all_markers,
        }

    def analyze_document_profile(self, clauses: List[ContractClause]) -> Dict[str, Any]:
        """Calculates global deontic profile of the entire agreement and computes duty asymmetry."""
        total_sentences = 0
        global_counts: Dict[str, int] = {cat.value: 0 for cat in DeonticCategory}
        actor_obligation_counts = {
            "user_obligations": 0,
            "vendor_obligations": 0,
            "mutual_obligations": 0,
            "user_prohibitions": 0,
            "vendor_permissions": 0,
        }
        
        for c in clauses:
            res = self.classify_clause(c)
            for s_res in res["sentence_classifications"]:
                total_sentences += 1
                cat = s_res["category"]
                actor = s_res["actor"]
                global_counts[cat] = global_counts.get(cat, 0) + 1

                if cat == DeonticCategory.OBLIGATION.value:
                    if actor == DutyActor.CUSTOMER_USER.value:
                        actor_obligation_counts["user_obligations"] += 1
                    elif actor == DutyActor.VENDOR_COMPANY.value:
                        actor_obligation_counts["vendor_obligations"] += 1
                    elif actor == DutyActor.MUTUAL.value:
                        actor_obligation_counts["mutual_obligations"] += 1
                elif cat == DeonticCategory.PROHIBITION.value:
                    if actor == DutyActor.CUSTOMER_USER.value:
                        actor_obligation_counts["user_prohibitions"] += 1
                elif cat == DeonticCategory.PERMISSION.value:
                    if actor == DutyActor.VENDOR_COMPANY.value:
                        actor_obligation_counts["vendor_permissions"] += 1

        percentages = {}
        for cat, count in global_counts.items():
            pct = round((count / total_sentences * 100), 1) if total_sentences > 0 else 0.0
            percentages[cat] = pct

        # Calculate Asymmetry Ratio accurately
        user_burdens = actor_obligation_counts["user_obligations"] + actor_obligation_counts["user_prohibitions"]
        vendor_commitments = actor_obligation_counts["vendor_obligations"] + actor_obligation_counts["mutual_obligations"]
        
        if user_burdens == 0 and vendor_commitments == 0:
            asymmetry_index = 0.0
        elif vendor_commitments == 0 and user_burdens > 0:
            asymmetry_index = 100.0
        elif user_burdens == 0 and vendor_commitments > 0:
            asymmetry_index = 0.0
        else:
            asymmetry_index = round((user_burdens / (user_burdens + vendor_commitments)) * 100, 1)

        return {
            "total_sentences": total_sentences,
            "counts": global_counts,
            "distribution_percentages": percentages,
            "actor_burdens": actor_obligation_counts,
            "asymmetry_index": asymmetry_index,
        }
