"""
Clause Segmentation & Boundary Detection Module for LexiTrap.
Splits contract documents into discrete, semantically coherent clauses
and maps them to the 16 standard legal categories.
"""

import re
from typing import List, Dict, Any, Optional
from app.nlp.preprocessing import segment_sentences

# The 16 Legal Contract Clause Categories specified in the NLP taxonomy
LEGAL_CATEGORIES = [
    "Termination",
    "Payment",
    "Liability",
    "Indemnification",
    "Confidentiality",
    "Privacy",
    "Intellectual Property",
    "Automatic Renewal",
    "Arbitration",
    "Governing Law",
    "Non-Compete",
    "Warranty",
    "Cancellation",
    "Refund",
    "Modification",
    "Other"
]

# Keyword indicators and lexical heuristics for rule-assisted category mapping
CATEGORY_LEXICAL_CUES: Dict[str, List[str]] = {
    "Termination": ["terminat", "end of agreement", "expiration", "right to cancel", "survive termination", "cure period"],
    "Payment": ["fee", "payment", "invoice", "billing", "due date", "late fee", "currency", "price", "taxes"],
    "Liability": ["limitation of liability", "indirect damages", "consequential", "aggregate liability", "cap on liability", "punitive", "disclaimer of liability"],
    "Indemnification": ["indemnif", "hold harmless", "defend and indemnify", "defense of claims", "third-party claim"],
    "Confidentiality": ["confidential information", "non-disclosure", "proprietary information", "trade secret", "recipient"],
    "Privacy": ["privacy", "personal data", "gdpr", "data protection", "data processing", "cookies", "harvesting"],
    "Intellectual Property": ["intellectual property", "copyright", "patent", "trademark", "ownership of work", "license grant", "proprietary rights", "ai model training"],
    "Automatic Renewal": ["automatic renewal", "auto-renew", "successive terms", "renews automatically", "renewal term"],
    "Arbitration": ["arbitration", "dispute resolution", "binding arbitration", "class action waiver", "american arbitration association", "jams", "tribunal"],
    "Governing Law": ["governing law", "jurisdiction", "venue", "construed in accordance with", "courts of"],
    "Non-Compete": ["non-compete", "non-solicitation", "restrictive covenant", "competitive business", "restraint of trade"],
    "Warranty": ["warranty", "as is", "merchantability", "fitness for a particular purpose", "express warranties", "warrants and represents"],
    "Cancellation": ["cancellation", "cooling-off", "right to revoke", "withdraw from"],
    "Refund": ["refund", "reimbursement", "money-back", "non-refundable", "pro-rata refund"],
    "Modification": ["amendment", "modification", "unilateral change", "updates to terms", "change these terms", "sole discretion to modify"]
}

# Regex patterns for detecting section headers and numbered outlines
SECTION_HEADER_REGEX = re.compile(
    r'(?:^|\n)(?:'
    r'(\d+(?:\.\d+)*\.?)\s+([A-Z][^\n]{2,80})|'                       # e.g., "1. TERMINATION" or "1.1 Payment Terms"
    r'(Section|Article|Clause)\s+(\d+(?:\.\d+)*|[IVXLCDM]+)[:.]?\s*([^\n]{0,80})|'  # e.g., "Section 4: Indemnification"
    r'([A-Z\s]{4,60})(?=\n|$)'                                         # e.g., "LIMITATION OF LIABILITY"
    r')',
    re.MULTILINE
)


def guess_clause_category(clause_text: str, title: str = "") -> str:
    """
    Infers the legal clause category from lexical cues in the title and clause body.
    (This provides initial heuristic labeling before ML TF-IDF classification in Phase 4).
    """
    search_scope = f"{title.lower()} {clause_text.lower()}"
    
    # Check title matches first (highest precision)
    for category, cues in CATEGORY_LEXICAL_CUES.items():
        for cue in cues:
            if cue in title.lower():
                return category

    # Check body cues with score ranking
    category_scores: Dict[str, int] = {cat: 0 for cat in LEGAL_CATEGORIES}
    for category, cues in CATEGORY_LEXICAL_CUES.items():
        for cue in cues:
            matches = len(re.findall(r'\b' + re.escape(cue), search_scope))
            if matches > 0:
                category_scores[category] += matches * 2

    # Find category with highest match count
    best_category, highest_score = max(category_scores.items(), key=lambda x: x[1])
    if highest_score > 0:
        return best_category
        
    return "Other"


def segment_contract_into_clauses(contract_text: str) -> List[Dict[str, Any]]:
    """
    Segments raw contract text into structured clauses.
    
    Academic Rationale:
    Unlike general unstructured NLP, legal contracts exhibit hierarchical outline
    structures (Articles, Sections, Subsections, Paragraphs). Clause segmentation
    decomposes long contracts into self-contained operational units for granular analysis.
    """
    if not contract_text or not contract_text.strip():
        return []

    text = contract_text.strip()
    
    # 1. Split text into logical paragraph blocks
    raw_blocks = re.split(r'\n\s*\n+', text)
    
    clauses: List[Dict[str, Any]] = []
    char_offset_cursor = 0
    clause_counter = 1

    for block in raw_blocks:
        block_clean = block.strip()
        if not block_clean:
            continue
            
        # Find start position in original text
        start_char = text.find(block_clean, char_offset_cursor)
        if start_char == -1:
            start_char = char_offset_cursor
        end_char = start_char + len(block_clean)
        char_offset_cursor = end_char

        # Check for section number and header title within the block
        header_match = re.match(
            r'^(?:(?:Section|Article|Clause)\s+)?(\d+(?:\.\d+)*|[IVXLCDM]+)?[.:)]?\s*([A-Za-z0-9\s,\'-]{3,60}?)(?:\n|:\s+|\s{2,}|$)(.*)$',
            block_clean,
            re.DOTALL
        )

        section_number = ""
        title = ""
        body_text = block_clean

        if header_match:
            sec_num = header_match.group(1) or ""
            potential_title = (header_match.group(2) or "").strip()
            rest_of_text = (header_match.group(3) or "").strip()

            # If the title matches known legal terms or is short enough to be a title
            if len(potential_title) < 50 and (rest_of_text or len(block_clean.splitlines()) > 1):
                section_number = sec_num
                title = potential_title
                body_text = rest_of_text if rest_of_text else block_clean

        # If no explicit title was extracted, derive a short preview title
        if not title:
            first_line = block_clean.split("\n")[0].strip()
            if len(first_line) <= 60 and not first_line.endswith("."):
                title = first_line
            else:
                title = f"Clause {clause_counter}"

        # Segment sentences within the clause
        sentences = segment_sentences(block_clean)
        category = guess_clause_category(block_clean, title)
        word_count = len(re.findall(r'\b\w+\b', block_clean))

        clauses.append({
            "clause_id": f"clause-{clause_counter}",
            "clause_number": clause_counter,
            "section_number": section_number,
            "title": title,
            "text": block_clean,
            "body_text": body_text,
            "category": category,
            "sentence_count": len(sentences),
            "sentences": sentences,
            "word_count": word_count,
            "start_char": start_char,
            "end_char": end_char
        })
        clause_counter += 1

    return clauses
