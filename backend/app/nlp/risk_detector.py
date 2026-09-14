"""
Context-Aware Risk Detection & Transparent Scoring Module for LexiTrap.
Implements:
1. Multi-signal linguistic risk pattern extraction
2. Context-aware balance analysis (Unilateral vs. Mutual rights, Notice windows, Carve-outs)
3. Transparent feature-based risk scoring (0–100 mapped to Low/Medium/High/Critical)
4. Contextual explanation generation and balanced alternative clause rewrites
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from app.nlp.preprocessing import segment_sentences, pos_tag_text

# High-risk linguistic patterns with semantic explanations and base point weights
RISK_LINGUISTIC_PATTERNS: List[Dict[str, Any]] = [
    {
        "pattern": r"\bwithout\s+(?:prior\s+)?notice\b",
        "phrase": "without notice",
        "factor_name": "Absence of Advance Notice",
        "score_impact": +20,
        "reason": "Allows action to be taken immediately with zero advance warning or transition period."
    },
    {
        "pattern": r"\b(?:at\s+any\s+time|at\s+will)\b",
        "phrase": "at any time / at will",
        "factor_name": "Unrestricted Timing / At-Will Action",
        "score_impact": +15,
        "reason": "Permits exercise of contractual remedies or termination without triggering events."
    },
    {
        "pattern": r"\b(?:sole|absolute|unilateral)\s+discretion\b",
        "phrase": "sole discretion",
        "factor_name": "Unchecked Discretionary Power",
        "score_impact": +20,
        "reason": "Grants unilateral authority to make binding decisions without standard of reasonableness."
    },
    {
        "pattern": r"\b(?:train\s+(?:commercial\s+)?(?:ai|machine\s+learning|llm|models?))\b",
        "phrase": "train commercial AI models",
        "factor_name": "AI Model Training on User Data",
        "score_impact": +30,
        "reason": "Permits vendor to utilize proprietary customer data/code to train generative AI or commercial models."
    },
    {
        "pattern": r"\b(?:perpetual(?:ly)?|irrevocable)\b",
        "phrase": "perpetual / irrevocable",
        "factor_name": "Perpetual & Irrevocable Grant",
        "score_impact": +15,
        "reason": "Grants rights or licenses that can never be revoked or terminated even after contract end."
    },
    {
        "pattern": r"\b(?:waive|waives|waiving)\s+(?:all\s+rights|any\s+right|jury|class\s+action)\b",
        "phrase": "waiver of legal rights / class action",
        "factor_name": "Waiver of Statutory / Procedural Rights",
        "score_impact": +25,
        "reason": "Forces surrender of judicial remedies, jury trial, or collective class representation."
    },
    {
        "pattern": r"\b(?:non-refundable|no\s+refunds?)\b",
        "phrase": "strictly non-refundable",
        "factor_name": "Absolute Non-Refundability",
        "score_impact": +15,
        "reason": "Bars refunds even in cases of vendor breach, downtime, or service discontinuation."
    },
    {
        "pattern": r"(?:capped\s+at\s+\$?\s*(?:0|50|100)(?:\.00)?|\$\s*(?:0|50|100)(?:\.00)?\b|nominal\s+sum|aggregate\s+liability\s+(?:is\s+capped|shall\s+not\s+exceed)\s+\$?\s*(?:0|50|100))",
        "phrase": "extreme liability cap ($0 - $50)",
        "factor_name": "Nominal Liability Disclaimers",
        "score_impact": +40,
        "reason": "Caps maximum vendor liability to a trivial sum ($50), effectively immunizing vendor against breaches."
    },
    {
        "pattern": r"\b(?:as\s+is\s+and\s+as\s+available|with\s+all\s+faults)\b",
        "phrase": "as-is disclaimer",
        "factor_name": "Complete Warranty Disclaimer",
        "score_impact": +15,
        "reason": "Disclaims all express and implied warranties regarding quality, security, and performance."
    },
    {
        "pattern": r"\b(?:certified\s+(?:physical\s+)?postal\s+mail\s+only|narrow\s+window)\b",
        "phrase": "restrictive cancellation barrier",
        "factor_name": "Trapped Renewal / Friction Barrier",
        "score_impact": +20,
        "reason": "Imposes artificial friction (such as requiring physical certified mail) to hinder cancellation."
    },
    {
        "pattern": r"\b(?:worldwide\s+in\s+any\s+capacity|period\s+of\s+5\s+years)\b",
        "phrase": "unreasonable non-compete scope",
        "factor_name": "Overbroad Restrictive Covenant",
        "score_impact": +25,
        "reason": "Exceeds reasonable geographic and temporal limits on future employment or business."
    }
]

# Context mitigating / balancing indicators (Risk Deductions)
MITIGATING_PATTERNS: List[Dict[str, Any]] = [
    {
        "pattern": r"\b(?:either\s+party|mutual(?:ly)?|each\s+party)\b",
        "factor_name": "Mutual / Bilateral Rights",
        "score_impact": -15,
        "reason": "Applies obligations or termination rights symmetrically to both parties rather than unilaterally."
    },
    {
        "pattern": r"\b(?:30|60|90)\s+(?:days?[']?\s+)?(?:prior\s+)?written\s+notice\b",
        "factor_name": "Reasonable Advance Written Notice (>= 30 days)",
        "score_impact": -15,
        "reason": "Provides sufficient advance notice window for transition or dispute resolution."
    },
    {
        "pattern": r"\b(?:except\s+in\s+(?:the\s+case|the\s+event)\s+of|unless|material\s+breach|cure\s+period)\b",
        "factor_name": "Defined Exception / Cure Period",
        "score_impact": -10,
        "reason": "Restricts immediate action strictly to defined scenarios such as uncured material breach."
    },
    {
        "pattern": r"\b(?:fees\s+paid\s+in\s+(?:the\s+prior|preceding)\s+12\s+months|annual\s+contract\s+value)\b",
        "factor_name": "Standard Commercial 12-Month Liability Cap",
        "score_impact": -15,
        "reason": "Aligns liability cap with industry-standard 12-month fees paid benchmark."
    },
    {
        "pattern": r"\b(?:pro-rata\s+refund|refund\s+of\s+unearned\s+fees)\b",
        "factor_name": "Pro-Rata Refund Guarantee",
        "score_impact": -10,
        "reason": "Protects customer financial interest by reimbursing unused prepaid fees upon termination."
    }
]


def extract_linguistic_signals(text: str) -> List[Dict[str, Any]]:
    """
    Extracts explicit linguistic danger signals with match span and context snippet.
    """
    detected = []
    text_lower = text.lower()
    
    for item in RISK_LINGUISTIC_PATTERNS:
        match = re.search(item["pattern"], text_lower)
        if match:
            start, end = match.span()
            # Capture contextual snippet around the matched pattern
            snippet_start = max(0, start - 25)
            snippet_end = min(len(text), end + 25)
            context_snippet = text[snippet_start:snippet_end].strip()
            
            detected.append({
                "phrase": item["phrase"],
                "factor_name": item["factor_name"],
                "score_impact": item["score_impact"],
                "matched_text": text[start:end],
                "context": f"...{context_snippet}...",
                "reason": item["reason"]
            })
            
    return detected


def extract_mitigating_signals(text: str) -> List[Dict[str, Any]]:
    """
    Identifies contextual balance signals that reduce risk.
    """
    mitigating = []
    text_lower = text.lower()
    
    for item in MITIGATING_PATTERNS:
        match = re.search(item["pattern"], text_lower)
        if match:
            start, end = match.span()
            mitigating.append({
                "factor_name": item["factor_name"],
                "score_impact": item["score_impact"],
                "matched_text": text[start:end],
                "reason": item["reason"]
            })
            
    return mitigating


def determine_subject_symmetry(text: str) -> Dict[str, Any]:
    """
    Analyzes whether rights in the clause are Unilateral (One-sided) or Mutual.
    
    Academic Rationale:
    'The Provider may terminate at will' is an asymmetric unilateral power.
    'Either party may terminate upon 30 days notice' is a symmetric mutual right.
    """
    text_lower = text.lower()
    
    is_mutual = bool(re.search(r'\b(either party|each party|mutually|both parties|neither party)\b', text_lower))
    is_unilateral_provider = bool(re.search(r'\b(provider|company|vendor|we)\s*(\'s)?\s+(total|aggregate|direct)?\s*(liability|may|reserves?\s+the\s+right|shall\s+have\s+the\s+right|disclaims)\b', text_lower))
    is_unilateral_customer_burden = bool(re.search(r'\b(customer|user|client|you)\s+(shall|agrees?\s+to|must)\s+(defend|indemnify|hold\s+harmless|waive)\b', text_lower))

    if is_mutual:
        return {"symmetry": "MUTUAL", "description": "Rights or obligations apply equally to both contracting parties."}
    elif is_unilateral_provider or is_unilateral_customer_burden:
        return {"symmetry": "UNILATERAL", "description": "Rights or burdens are structured asymmetrically in favor of one party."}
    else:
        return {"symmetry": "NEUTRAL", "description": "Standard bilateral contract provision."}


def calculate_transparent_risk_score(
    clause_text: str,
    category: str = "Other"
) -> Dict[str, Any]:
    """
    Computes a transparent, reproducible risk score from 0 to 100 based on linguistic signals,
    contextual symmetry, notice requirements, and exceptions.
    
    Score Mapping:
      0 – 24  : LOW RISK
     25 – 49  : MEDIUM RISK
     50 – 74  : HIGH RISK
     75 – 100 : CRITICAL RISK
    """
    base_score = 10  # Baseline neutral starting point
    scoring_ledger: List[Dict[str, Any]] = [
        {"factor": "Baseline Contract Clause Neutrality", "points": +10, "type": "baseline"}
    ]

    # 1. Linguistic Danger Signals
    risk_signals = extract_linguistic_signals(clause_text)
    for sig in risk_signals:
        scoring_ledger.append({
            "factor": sig["factor_name"],
            "points": sig["score_impact"],
            "type": "risk_penalty",
            "reason": sig["reason"]
        })
        base_score += sig["score_impact"]

    # 2. Contextual Symmetry Analysis
    symmetry_data = determine_subject_symmetry(clause_text)
    if symmetry_data["symmetry"] == "UNILATERAL" and len(risk_signals) > 0:
        unilateral_penalty = +20
        base_score += unilateral_penalty
        scoring_ledger.append({
            "factor": "Asymmetric Unilateral Right",
            "points": unilateral_penalty,
            "type": "risk_penalty",
            "reason": "One-sided discretion without reciprocal rights granted to counterparty."
        })

    # 3. Mitigating Factors
    mitigating_signals = extract_mitigating_signals(clause_text)
    for mit in mitigating_signals:
        scoring_ledger.append({
            "factor": mit["factor_name"],
            "points": mit["score_impact"],
            "type": "mitigating_credit",
            "reason": mit["reason"]
        })
        base_score += mit["score_impact"]

    # Clamp final score to [0, 100]
    final_score = max(0, min(100, base_score))

    # Map to risk level
    if final_score >= 75:
        risk_level = "CRITICAL"
        risk_color = "red"
    elif final_score >= 50:
        risk_level = "HIGH"
        risk_color = "orange"
    elif final_score >= 25:
        risk_level = "MEDIUM"
        risk_color = "yellow"
    else:
        risk_level = "LOW"
        risk_color = "green"

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "symmetry": symmetry_data["symmetry"],
        "symmetry_description": symmetry_data["description"],
        "scoring_ledger": scoring_ledger,
        "risk_signals": risk_signals,
        "mitigating_signals": mitigating_signals
    }


def generate_clause_explanation(
    category: str,
    score_data: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generates structured human-readable explanation and actionable negotiation recommendations.
    """
    risk_level = score_data["risk_level"]
    risk_signals = score_data["risk_signals"]
    score = score_data["risk_score"]

    if risk_level in {"HIGH", "CRITICAL"}:
        flagged_terms = ", ".join([f"'{s['phrase']}'" for s in risk_signals]) if risk_signals else "asymmetric covenants"
        explanation = (
            f"This {category} clause contains noteworthy contractual risk (Score: {score}/100) due to {flagged_terms}. "
            f"It grants broad discretionary or unilateral powers while lacking standard reciprocal protections or notice requirements."
        )
        recommendation = (
            f"Negotiate mutual bilateral terms. Request a mandatory 30-day prior written notice requirement, "
            f"restrict termination/amendment triggers to defined material breach cure periods, and cap liabilities reasonably."
        )
    elif risk_level == "MEDIUM":
        explanation = (
            f"This {category} clause includes moderately restrictive terms (Score: {score}/100). "
            f"While not inherently predatory, the wording may create operational ambiguity or narrow response windows."
        )
        recommendation = (
            f"Clarify notice procedures, align late payment or renewal fees with statutory defaults, "
            f"and confirm clear in-app or electronic opt-out channels."
        )
    else:
        explanation = (
            f"This {category} clause demonstrates standard, balanced commercial terms (Score: {score}/100). "
            f"It maintains bilateral rights, reasonable notice periods, and proportionate allocations of responsibility."
        )
        recommendation = "Provision appears standard and balanced. No major revision required."

    return {
        "explanation": explanation,
        "recommendation": recommendation
    }


def generate_balanced_rewrite(clause_text: str, category: str, risk_level: str) -> Optional[Dict[str, str]]:
    """
    Generates an educational, balanced alternative wording for high/critical risk clauses.
    """
    if risk_level not in {"HIGH", "CRITICAL"}:
        return None

    text_lower = clause_text.lower()
    suggested_text = clause_text

    # 1. Termination Rewrite
    if category == "Termination" or "terminate" in text_lower:
        suggested_text = (
            "Either party may terminate this Agreement upon thirty (30) days' prior written notice to the other party, "
            "or immediately with written notice in the event of an uncured material breach following a thirty (30) day cure period."
        )
    # 2. Liability Rewrite
    elif category == "Liability" or "liability" in text_lower:
        suggested_text = (
            "In no event shall either party's aggregate cumulative liability under this Agreement exceed the total fees "
            "paid or payable by Customer in the preceding twelve (12) months, except for breaches of confidentiality or gross negligence."
        )
    # 3. Modification Rewrite
    elif category == "Modification" or "modify" in text_lower or "amend" in text_lower:
        suggested_text = (
            "Company may modify these Terms upon thirty (30) days' prior written notice to Customer. If Customer does not agree "
            "to such modifications, Customer may terminate this Agreement without penalty and receive a pro-rata refund of prepaid fees."
        )
    # 4. Intellectual Property / AI Training Rewrite
    elif category == "Intellectual Property" or "ai" in text_lower or "train" in text_lower:
        suggested_text = (
            "Customer retains all right, title, and interest in and to Customer Data. Provider shall not use Customer Data "
            "or proprietary code to train, fine-tune, or develop any machine learning or artificial intelligence models without express written consent."
        )
    # 5. Indemnification Rewrite
    elif category == "Indemnification" or "indemnif" in text_lower:
        suggested_text = (
            "Each party shall mutually defend, indemnify, and hold harmless the other party against third-party claims "
            "arising out of intellectual property infringement or gross negligence, subject to the agreed limitation of liability."
        )
    # 6. Automatic Renewal Rewrite
    elif category == "Automatic Renewal" or "renew" in text_lower:
        suggested_text = (
            "This Agreement shall renew automatically for successive one-year terms unless either party gives notice of non-renewal "
            "at least thirty (30) days prior to expiration. Non-renewal notice may be submitted electronically via account dashboard settings."
        )
    # Generic fallback
    else:
        suggested_text = (
            "The parties agree that all rights and obligations hereunder shall be exercised in good faith upon reasonable "
            "thirty (30) days' written notice, subject to mutual and balanced standards of commercial reasonableness."
        )

    return {
        "original_clause": clause_text,
        "suggested_balanced_clause": suggested_text,
        "label": "AI-GENERATED BALANCED SUGGESTION",
        "academic_disclaimer": "Educational suggestion only. Not legal advice."
    }


def audit_clause_complete(clause_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes complete Phase 5 risk detection, context balance analysis, scoring,
    explanation generation, and alternative rewrite generation on a single clause.
    """
    text = clause_data.get("text", "")
    category = clause_data.get("category", "Other")

    score_data = calculate_transparent_risk_score(text, category)
    exp_data = generate_clause_explanation(category, score_data)
    rewrite_data = generate_balanced_rewrite(text, category, score_data["risk_level"])

    result = dict(clause_data)
    result.update({
        "risk_score": score_data["risk_score"],
        "risk_level": score_data["risk_level"],
        "risk_color": score_data["risk_color"],
        "symmetry": score_data["symmetry"],
        "symmetry_description": score_data["symmetry_description"],
        "scoring_ledger": score_data["scoring_ledger"],
        "risk_signals": score_data["risk_signals"],
        "mitigating_signals": score_data["mitigating_signals"],
        "explanation": exp_data["explanation"],
        "recommendation": exp_data["recommendation"],
        "suggested_rewrite": rewrite_data
    })
    return result


def audit_contract_document(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates clause audits across an entire contract and computes document-level risk health.
    """
    if not clauses:
        return {"error": "No clauses to audit"}

    audited_clauses = [audit_clause_complete(c) for c in clauses]
    
    # Calculate overall risk metrics
    scores = [c["risk_score"] for c in audited_clauses]
    avg_score = round(sum(scores) / max(len(scores), 1), 2)
    max_score = max(scores) if scores else 0
    
    # Risk category counts
    level_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for c in audited_clauses:
        level_counts[c["risk_level"]] += 1

    # Overall contract health grade
    if avg_score >= 60 or level_counts["CRITICAL"] >= 2:
        overall_grade = "DANGER / HIGH RISK"
        overall_status = "Contract contains multiple predatory or severely one-sided clauses."
    elif avg_score >= 35 or level_counts["HIGH"] >= 2:
        overall_grade = "CAUTION / MODERATE RISK"
        overall_status = "Contract contains several noteworthy clauses requiring revision."
    else:
        overall_grade = "FAIR / LOW RISK"
        overall_status = "Contract appears largely balanced with standard commercial provisions."

    return {
        "summary": {
            "total_clauses": len(audited_clauses),
            "average_risk_score": avg_score,
            "maximum_clause_risk_score": max_score,
            "overall_grade": overall_grade,
            "overall_status": overall_status,
            "risk_distribution": level_counts,
            "legal_disclaimer": (
                "LexiTrap is an AI/NLP-based educational contract analysis system. "
                "It identifies potentially noteworthy language and does not provide legal advice or guarantee "
                "that a contract is safe or enforceable. Users should consult a qualified legal professional for legal advice."
            )
        },
        "clauses": audited_clauses
    }
