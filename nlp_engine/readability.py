"""
Legal Readability & Meaning-Based Plain-English Simplification Engine
Calculates Flesch-Kincaid Grade Level, Flesch Reading Ease, Gunning Fog Index,
and generates semantic layperson translations for legal clauses.
"""

import re
from typing import Dict, Any, List, Optional
from .parser import ContractClause


class ReadabilityAnalyzer:
    """
    Evaluates legal linguistic complexity and synthesizes layperson plain-English translations.
    """

    # Semantic Legal Translation Templates based on detected modal logic and domain concepts
    SEMANTIC_TRANSLATIONS = [
        # Unilateral Modification
        (re.compile(r"\b(?:modify|change|alter|update|revise|amend)\s+.*?\b(?:without\s+(?:prior\s+)?notice|at\s+any\s+time|in\s+(?:our|its)\s+sole\s+discretion)\b", re.I),
         "The company can change pricing, service features, or agreement rules whenever it chooses without notifying you in advance."),
        (re.compile(r"\b(?:neither\s+party\s+may\s+modify|mutual\s+written\s+agreement|signed\s+by\s+both\s+parties)\b", re.I),
         "Neither party can change this contract unless both sides agree and sign a written document."),
        
        # Termination
        (re.compile(r"\b(?:terminate\s+.*?\b(?:at\s+any\s+time\s+)?without\s+(?:prior\s+|providing\s+|further\s+|advance\s+)?notice|suspend\s+.*?\bwithout\s+(?:prior\s+|providing\s+)?notice)\b", re.I),
         "The provider can shut down your account or terminate the agreement at any moment without prior notice."),
        (re.compile(r"\b(?:either\s+party\s+may\s+terminate\b.*?\b(?:30|60|15|90|written\s+notice)|(?:30|60|15|90)\s+days['’]?\s*(?:prior\s+)?written\s+notice\s+to\s+(?:the\s+other\s+party|terminate)|written\s+notice\s+of\s+termination)\b", re.I),
         "Either party is free to end the agreement by giving advance written notice (typically 30 days)."),
        
        # Indemnification
        (re.compile(r"\b(?:customer|user|client)\s+shall\s+indemnify,\s*defend\s+and\s+hold\s+harmless\s+.*?\b(?:company\s+provides\s+no\s+indemnification|no\s+indemnification\s+to\s+customer)\b", re.I),
         "You have to pay for all the company's legal fees and damages if someone sues them, but the company offers you zero protection in return."),
        (re.compile(r"\b(?:customer|user|client)\s+shall\s+indemnify,\s*defend\s+and\s+hold\s+harmless\b", re.I),
         "You are legally responsible for paying the company's legal defense costs and settlement damages if a lawsuit arises from your use."),
        (re.compile(r"\b(?:each\s+party|both\s+parties)\s+.*?\bindemnify,\s*defend\s+and\s+hold\s+harmless\b", re.I),
         "Both parties mutually protect each other from third-party lawsuits, IP claims, and gross negligence."),
        
        # Arbitration & Dispute Resolution
        (re.compile(r"\b(?:binding\s+arbitration|waive\s+any\s+right\s+to\s+a\s+jury\s+trial|class\s+action\s+waiver)\b", re.I),
         "You give up your right to sue the company in public court, have a jury trial, or join class-action lawsuits."),
        (re.compile(r"\b(?:good-faith\s+negotiations|executive\s+mediation|court\s+of\s+competent\s+jurisdiction)\b", re.I),
         "Disputes will first be negotiated in good faith, and both sides preserve their full legal right to go to court if unresolved."),
        
        # AI Training & Data Rights
        (re.compile(r"\b(?:perpetual,\s*irrevocable,\s*worldwide\s+license|train\s+machine\s+learning\s+models|train\s+(?:commercial\s+)?ai\s+algorithms|neural\s+networks)\b", re.I),
         "The company can keep, analyze, and train artificial intelligence models on your private documents and data forever without paying you."),
        (re.compile(r"\b(?:shall\s+not\s+be\s+stored,\s*aggregated,\s*or\s*utilized\s+to\s+train|zero-data-retention)\b", re.I),
         "The vendor promises that your confidential data and files will NEVER be used to train AI models and will be deleted after use."),
        
        # Liability & Disclaimers
        (re.compile(r"\b(?:liability\b.*?\b(?:shall\s+not\s+exceed|capped\s+at|is\s+limited\s+to|exceed)\b.*?\b(?:fees\s+paid|twelve\s+months|12\s+months|amount\s+paid)|capped\s+at\s+(?:total\s+fees\s+paid\s+in\s+the\s+preceding\s+)?12\s+months)\b", re.I),
         "The provider's financial liability is capped at the fees paid during the preceding 12 months, representing a standard balanced commercial liability limit."),
        (re.compile(r"\b(?:shall\s+be\s+liable\s+for\s+all\s+losses|liable\s+for\s+all\s+losses|without\s+limitation|unlimited\s+liability)\b", re.I),
         "You are held financially responsible for all losses, damages, and costs with potentially unlimited liability."),
        (re.compile(r"\b(?:provided\s+strictly\s+[\"']as\s+is[\"']|liability\s+(?:shall\s+not\s+exceed|exceed)\s+(?:\$0|\$50|\$100|fifty\s+dollars))\b", re.I),
         "If the service crashes or loses your data, the company disclaims all liability and refuses to pay any meaningful damages."),
        (re.compile(r"\b(?:capped\s+at\s+total\s+fees\s+paid\s+in\s+the\s+preceding\s+12\s+months|capped\s+at\s+12\s+months)\b", re.I),
         "Each party's financial liability is capped at the total amount of fees paid over the last 12 months."),
        
        # Automatic Renewal
        (re.compile(r"\b(?:automatically\s+renew\s+for\s+successive\s+(?:multi-year|3\s+years|one-year)|certified\s+postal\s+mail\s+at\s+least\s+90\s+days)\b", re.I),
         "Your subscription automatically locks in for another period unless you cancel well in advance using strict procedures."),
        (re.compile(r"\b(?:cancel\s+at\s+any\s+time|self-service\s+(?:web\s+)?portal|reminder\s+notification)\b", re.I),
         "Your subscription auto-renews, but you will receive an advance reminder and can cancel easily online at any time."),
        
        # Non-Compete
        (re.compile(r"\b(?:shall\s+not\s+(?:directly\s+or\s+indirectly\s+)?engage\s+in\s+any\s+competing\s+business|non-compete|worldwide\s+for\s+\d+\s+years)\b", re.I),
         "You are legally banned from working for competing companies or starting a business in this field after leaving."),
        (re.compile(r"\b(?:non-solicitation\s+of\s+key\s+personnel|free\s+worker\s+mobility)\b", re.I),
         "You are free to work anywhere, provided you do not recruit the company's existing employees."),
        
        # Confidentiality
        (re.compile(r"\b(?:confidential\s+information|non-disclosure|proprietary\s+information|duty\s+of\s+care)\b", re.I),
         "Both parties are strictly required to keep confidential trade secrets and business data private."),
        
        # Governing Law
        (re.compile(r"\b(?:governed\s+by\s+and\s+construed\s+in\s+accordance\s+with\s+the\s+laws\s+of)\b", re.I),
         "Any legal dispute will be decided under the laws of the specific state or country designated in this clause."),
        
        # Payment & Refunds
        (re.compile(r"\b(?:non-cancellable\s+and\s+non-refundable|strictly\s+non-refundable|no\s+refunds?)\b", re.I),
         "All payments made are final and non-refundable under any circumstance."),
        (re.compile(r"\b(?:pay\s+all\s+undisputed\s+invoices\s+within\s+30\s+days|net\s+30)\b", re.I),
         "Customer agrees to pay all undisputed invoices within 30 days of receiving the bill."),
    ]

    def count_syllables_in_word(self, word: str) -> int:
        """Estimates syllable count using phonetic heuristics with suffix adjustments."""
        w = word.lower().strip()
        if not w:
            return 0
        if len(w) <= 3:
            return 1

        w = re.sub(r"[^a-z]", "", w)
        if not w:
            return 1

        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        for char in w:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        if w.endswith("e") and not w.endswith("le") and count > 1:
            count -= 1
        elif w.endswith(("es", "ed")) and count > 1:
            count -= 1

        return max(1, count)

    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculates exact mathematical readability metrics:
        - Flesch Reading Ease (FRE): 206.835 - 1.015 * ASL - 84.6 * ASW (Higher = Easier)
        - Flesch-Kincaid Grade Level (FKGL): 0.39 * ASL + 11.8 * ASW - 15.59 (U.S. School Grade Level)
        - Gunning Fog Index: 0.4 * (ASL + Complex Word %)
        """
        if not text or not text.strip():
            return {
                "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0,
                "gunning_fog_index": 0.0,
                "obfuscation_level": "Standard Language",
                "obfuscation_score": 0.0,
                "reading_ease_label": "Very Easy",
                "avg_sentence_length": 0.0,
                "avg_syllables_per_word": 0.0,
                "complex_word_ratio": 0.0,
                "total_words": 0,
                "total_sentences": 0,
                "academic_explanation": "Flesch Reading Ease ranges from 0-100 (100 = simplest English, 0 = dense legalese). Grade Level indicates the academic school grade required to comprehend.",
            }

        raw_sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        total_sentences = max(1, len(raw_sentences))
        
        words = re.findall(r"\b[A-Za-z]+(?:'[a-z]+)?\b", text)
        total_words = max(1, len(words))

        total_syllables = sum(self.count_syllables_in_word(w) for w in words)
        complex_words = sum(1 for w in words if self.count_syllables_in_word(w) >= 3 and not w.lower().endswith(("ing", "ed", "es")))

        # Standard Academic Formulas
        asl = total_words / total_sentences
        asw = total_syllables / total_words
        complex_ratio = (complex_words / total_words) * 100

        # Flesch Reading Ease (0 to 100) -> Higher is easier
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, round(fre, 1)))

        # Flesch-Kincaid Grade Level
        fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59
        fk_grade = max(1.0, round(fk_grade, 1))

        # Gunning Fog Index
        fog = 0.4 * (asl + complex_ratio)
        fog = max(1.0, round(fog, 1))

        if fre >= 70.0:
            ease_label = "Easy to Read"
        elif fre >= 50.0:
            ease_label = "Moderate Reading"
        elif fre >= 30.0:
            ease_label = "Hard to Read (Dense Legalese)"
        else:
            ease_label = "Very Obfuscated Legalese"

        if fk_grade >= 16.0 or fre < 30.0:
            obfuscation = "Heavy Legal Jargon"
            obf_score = min(100.0, round(70.0 + (fk_grade - 16.0) * 3, 1))
        elif fk_grade >= 12.0 or fre < 50.0:
            obfuscation = "Moderate Legalese"
            obf_score = round(40.0 + (fk_grade - 12.0) * 7.5, 1)
        else:
            obfuscation = "Clear & Plain English"
            obf_score = round(max(0.0, (fk_grade / 12.0) * 35.0), 1)

        return {
            "flesch_reading_ease": fre,
            "reading_ease_label": ease_label,
            "flesch_kincaid_grade": fk_grade,
            "gunning_fog_index": fog,
            "obfuscation_level": obfuscation,
            "obfuscation_score": obf_score,
            "avg_sentence_length": round(asl, 1),
            "avg_syllables_per_word": round(asw, 2),
            "complex_word_ratio": round(complex_ratio, 1),
            "total_words": total_words,
            "total_sentences": total_sentences,
            "academic_explanation": f"FRE: {fre}/100 | Grade: {fk_grade} | ASL: {round(asl, 1)} words/sent | ASW: {round(asw, 2)} syll/word.",
        }

    def generate_clause_tldr(self, clause: ContractClause, dominant_deontic: str = "", traps: Optional[List[Any]] = None) -> str:
        """
        Synthesizes a true meaning-based layperson translation explaining the practical effect of the clause.
        """
        text = clause.text

        # 1. Semantic pattern matching
        for pattern, translation in self.SEMANTIC_TRANSLATIONS:
            if pattern.search(text):
                return translation

        # 2. Trap danger synthesis if flagged
        if traps:
            first_trap = traps[0]
            if hasattr(first_trap, "legal_danger") and first_trap.legal_danger:
                return first_trap.legal_danger
            elif isinstance(first_trap, dict) and first_trap.get("legal_danger"):
                return first_trap["legal_danger"]

        # 3. Category / Title semantic synthesis
        title_low = clause.title.lower()
        if "definition" in title_low or "recital" in title_low or "preamble" in title_low:
            return "Establishes standard baseline terminology and background context between the contracting parties."
        elif "payment" in title_low or "fee" in title_low or "bill" in title_low:
            return "Outlines payment obligations, billing schedules, and invoice terms for services provided."
        elif "confidential" in title_low or "nda" in title_low or "secrecy" in title_low:
            return "Requires both parties to maintain strict secrecy over non-public proprietary information."
        elif "liability" in title_low:
            return "Defines the financial boundaries and damage exclusions for claims arising under the contract."
        elif "warranty" in title_low or "disclaimer" in title_low:
            return "Specifies quality guarantees and disclaimers regarding service reliability."
        elif "indemnif" in title_low:
            return "Allocates legal defense responsibilities and cost reimbursement for third-party claims."
        elif "terminat" in title_low:
            return "Sets out notice requirements and procedures for canceling or ending this agreement."
        elif "dispute" in title_low or "arbitration" in title_low:
            return "Specifies how legal conflicts must be resolved between the parties."
        elif "governing" in title_low or "jurisdiction" in title_low:
            return "Identifies the governing court system and legal jurisdiction that controls this contract."

        # 4. Deontic fallback
        d = dominant_deontic.lower()
        if "obligation" in d:
            return "Establishes mandatory legal duties and performance actions required under this section."
        elif "prohibition" in d:
            return "Specifies prohibited actions, restrictions, and legal boundaries that must not be violated."
        elif "permission" in d:
            return "Defines specific legal rights, authorizations, and discretionary powers."
        elif "warranty" in d:
            return "Provides explicit quality commitments and representations."
        elif "disclaimer" in d:
            return "Disclaims specific warranties and limits legal responsibility."

        return "Defines operational terms and conditions governing the relationship between the parties."

    def analyze(self, text: str) -> Dict[str, Any]:
        return self.analyze_readability(text)

    def generate_tldr(self, clause_or_text: Any, dominant_deontic: str = "", traps: Optional[List[Any]] = None) -> str:
        if isinstance(clause_or_text, str):
            dummy = ContractClause(
                clause_id="temp", clause_number="0", title="Clause", text=clause_or_text,
                start_line=1, end_line=1, sentences=[clause_or_text],
                word_count=len(clause_or_text.split()), char_count=len(clause_or_text)
            )
            return self.generate_clause_tldr(dummy, dominant_deontic, traps)
        return self.generate_clause_tldr(clause_or_text, dominant_deontic, traps)
