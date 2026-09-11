"""
Legal Readability & Plain-English TL;DR Simplification Engine
Calculates Flesch-Kincaid Grade Level, Flesch Reading Ease, Gunning Fog Index,
and generates plain-English translations for dense legalese and dark-pattern clauses.
"""

import re
from typing import Dict, Any, List, Optional
from .parser import ContractClause


class ReadabilityAnalyzer:
    """
    Evaluates legal obfuscation using established linguistic formulas
    and synthesizes 1-sentence layperson TL;DR summaries.
    """

    # Common legal boilerplate phrase patterns for plain-English synthesis
    PLAIN_ENGLISH_TRANSLATIONS = [
        (re.compile(r"\b(?:indemnify,\s*defend\s+and\s+hold\s+harmless|hold\s+harmless\s+from\s+any\s+and\s+all\s+claims)\b", re.I),
         "You have to pay for all the company's legal fees and damages if someone sues them because of your account."),
        (re.compile(r"\b(?:modify|change|alter|update|revise)\s+.*?\b(?:without\s+prior\s+notice|at\s+any\s+time|in\s+(?:our|its)\s+sole\s+discretion)\b", re.I),
         "The company can change prices, features, or contract terms whenever they want without asking you first."),
        (re.compile(r"\b(?:binding\s+arbitration|waive\s+any\s+right\s+to\s+a\s+jury\s+trial|class\s+action\s+waiver)\b", re.I),
         "You give up your right to sue the company in court, have a jury trial, or join class-action lawsuits."),
        (re.compile(r"\b(?:perpetual,\s*irrevocable,\s*worldwide\s+license|train\s+machine\s+learning\s+models|ai\s+algorithms)\b", re.I),
         "The company can keep, use, and train AI models on everything you upload forever without paying you."),
        (re.compile(r"\b(?:provided\s+strictly\s+[\"']as\s+is[\"']|liability\s+(?:shall\s+not\s+exceed|exceed)\s+\$(?:0|50|100))\b", re.I),
         "If the service crashes or loses your data, the company refuses to take any financial responsibility."),
        (re.compile(r"\b(?:automatically\s+renew|continuous\s+subscription|unless\s+canceled\s+at\s+least)\b", re.I),
         "Your subscription will automatically charge your card on renewal unless you manually cancel beforehand."),
        (re.compile(r"\b(?:shall\s+not\s+(?:directly\s+or\s+indirectly\s+)?engage\s+in\s+any\s+competing\s+business|non-compete)\b", re.I),
         "You are banned from working for competitors or in the same industry after leaving this contract."),
        (re.compile(r"\b(?:non-cancellable\s+and\s+non-refundable|strictly\s+non-refundable|no\s+refunds?)\b", re.I),
         "All sales and orders are final; you cannot cancel or get any money back once purchased."),
        (re.compile(r"\b(?:governed\s+by\s+and\s+construed\s+in\s+accordance\s+with\s+the\s+laws\s+of)\b", re.I),
         "Any legal disputes will be decided under the laws of the specific location chosen by the vendor."),
        (re.compile(r"\b(?:confidential\s+information|non-disclosure|proprietary\s+information)\b", re.I),
         "You must keep business information, trade secrets, and proprietary data strictly secret."),
    ]

    def count_syllables_in_word(self, word: str) -> int:
        """Estimates syllable count using phonetic heuristics with suffix adjustments."""
        w = word.lower().strip()
        if not w:
            return 0
        if len(w) <= 3:
            return 1

        # Strip non-alpha
        w = re.sub(r"[^a-z]", "", w)
        if not w:
            return 1

        # Count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        for char in w:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        # Adjust for silent 'e', 'es', 'ed' at word ends
        if w.endswith("e") and not w.endswith("le") and count > 1:
            count -= 1
        elif w.endswith(("es", "ed")) and count > 1:
            count -= 1

        return max(1, count)

    def analyze_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculates Flesch-Kincaid Grade Level, Flesch Reading Ease (0-100),
        and Gunning Fog Index on text.
        """
        if not text or not text.strip():
            return {
                "flesch_reading_ease": 100.0,
                "flesch_kincaid_grade": 0.0,
                "gunning_fog_index": 0.0,
                "obfuscation_level": "Standard Language",
                "obfuscation_score": 0.0,
                "avg_sentence_length": 0.0,
                "complex_word_ratio": 0.0,
                "total_words": 0,
                "total_sentences": 0,
            }

        # Tokenize sentences and words
        raw_sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        total_sentences = max(1, len(raw_sentences))
        
        words = re.findall(r"\b[A-Za-z]+(?:'[a-z]+)?\b", text)
        total_words = max(1, len(words))

        total_syllables = sum(self.count_syllables_in_word(w) for w in words)
        complex_words = sum(1 for w in words if self.count_syllables_in_word(w) >= 3 and not w.lower().endswith(("ing", "ed", "es")))

        # Metrics computation
        asl = total_words / total_sentences
        asw = total_syllables / total_words
        complex_ratio = (complex_words / total_words) * 100

        # Flesch Reading Ease (0 to 100) -> Higher is easier
        fre = 206.835 - (1.015 * asl) - (84.6 * asw)
        fre = max(0.0, min(100.0, round(fre, 1)))

        # Flesch-Kincaid Grade Level (0 to 25+)
        fk_grade = (0.39 * asl) + (11.8 * asw) - 15.59
        fk_grade = max(1.0, round(fk_grade, 1))

        # Gunning Fog Index
        fog = 0.4 * (asl + complex_ratio)
        fog = max(1.0, round(fog, 1))

        # Reading Ease Label in simple English
        if fre >= 70.0:
            ease_label = "Easy to Read"
        elif fre >= 50.0:
            ease_label = "Moderate Reading"
        elif fre >= 30.0:
            ease_label = "Hard to Read"
        else:
            ease_label = "Very Hard to Read"

        # Obfuscation & Language Complexity in Simple English
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
            "complex_word_ratio": round(complex_ratio, 1),
            "total_words": total_words,
            "total_sentences": total_sentences,
        }

    def generate_clause_tldr(self, clause: ContractClause, dominant_deontic: str = "", traps: Optional[List[Any]] = None) -> str:
        """
        Synthesizes a plain-English 1-sentence TL;DR translation of the clause text.
        """
        text = clause.text

        # 1. Check known legal translation patterns
        for pattern, translation in self.PLAIN_ENGLISH_TRANSLATIONS:
            if pattern.search(text):
                return translation

        # 2. Derive from detected traps if present
        if traps:
            first_trap = traps[0]
            if hasattr(first_trap, "legal_danger") and first_trap.legal_danger:
                return first_trap.legal_danger
            elif isinstance(first_trap, dict) and first_trap.get("legal_danger"):
                return first_trap["legal_danger"]

        # 3. Deontic category fallback
        d = dominant_deontic.lower()
        if "obligation" in d:
            return "This section outlines mandatory duties and actions you are required to perform."
        elif "prohibition" in d:
            return "This section lists prohibited actions and restrictions you must not violate."
        elif "permission" in d:
            return "This section defines specific rights, choices, and permissions granted to you."
        elif "warranty" in d:
            return "This section provides promises, standards, or performance guarantees."
        elif "disclaimer" in d:
            return "This section limits the vendor's warranties and disclaims legal responsibility."
        else:
            # First sentence clean truncation
            sentences = clause.sentences or [text]
            first_s = sentences[0]
            if len(first_s) > 120:
                first_s = first_s[:117] + "..."
            return first_s

    # Convenience aliases for developer flexibility
    def analyze(self, text: str) -> Dict[str, Any]:
        """Alias for analyze_readability."""
        return self.analyze_readability(text)

    def generate_tldr(self, clause_or_text: Any, dominant_deontic: str = "", traps: Optional[List[Any]] = None) -> str:
        """Alias for generate_clause_tldr supporting either ContractClause or raw string."""
        if isinstance(clause_or_text, str):
            words = clause_or_text.split()
            dummy_clause = ContractClause(
                clause_id="temp",
                clause_number="0",
                title="Clause",
                text=clause_or_text,
                start_line=1,
                end_line=1,
                sentences=[clause_or_text],
                word_count=len(words),
                char_count=len(clause_or_text)
            )
            return self.generate_clause_tldr(dummy_clause, dominant_deontic, traps)
        return self.generate_clause_tldr(clause_or_text, dominant_deontic, traps)


