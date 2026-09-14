"""
Advanced Document Parser & Hierarchical Legal Clause Segmenter
Handles extraction, boundary segmentation, inline title isolation,
HTML/Markdown cleanup, abbreviation-safe sentence tokenization,
and strict legal content validation / web noise rejection.
"""

import re
import html
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class ContractClause:
    clause_id: str
    clause_number: str
    title: str
    text: str
    start_line: int
    end_line: int
    word_count: int
    char_count: int
    sentences: List[str] = field(default_factory=list)
    subsections: List[str] = field(default_factory=list)
    has_subsections: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "clause_number": self.clause_number,
            "title": self.title,
            "text": self.text,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "sentences": self.sentences,
            "subsections": self.subsections,
            "has_subsections": self.has_subsections,
            "metadata": self.metadata,
        }


class DocumentParser:
    """
    High-precision legal agreement parser with:
    - Multi-tier section & article detection (Section 1.1, Article IV, 1., 1.1)
    - Inline title extraction (e.g. '1. INDEMNITY. Customer shall defend...')
    - Web noise, navigation, and category listing filtering
    - Sub-clause preservation (preventing fragmented (a), (b), (i) splitting)
    - Protected legal abbreviation sentence boundary tokenizer
    - Legal validity verification
    """

    # Sub-item patterns that belong inside a clause (should NOT start a new major clause)
    SUB_ITEM_PATTERN = re.compile(r"^(?:[•●▪■◆►✓✔○▫\-*]|\([a-z0-9]+\)|[a-z]\.|\([ivxlcdm]+\))\s+", re.I)

    # Abbreviations that must not trigger a sentence split
    LEGAL_ABBREVIATIONS = {
        r"\be\.g\.\s*": "eg_placeholder ",
        r"\bi\.e\.\s*": "ie_placeholder ",
        r"\bet al\.\s*": "etal_placeholder ",
        r"\betc\.\s*": "etc_placeholder ",
        r"\bviz\.\s*": "viz_placeholder ",
        r"\bInc\.\s*": "inc_placeholder ",
        r"\bLtd\.\s*": "ltd_placeholder ",
        r"\bPvt\.\s*": "pvt_placeholder ",
        r"\bCorp\.\s*": "corp_placeholder ",
        r"\bCo\.\s*": "co_placeholder ",
        r"\bLLC\.\s*": "llc_placeholder ",
        r"\bLLP\.\s*": "llp_placeholder ",
        r"\bL\.L\.C\.\s*": "llc2_placeholder ",
        r"\bL\.P\.\s*": "lp_placeholder ",
        r"\bNo\.\s*": "no_placeholder ",
        r"\bNos\.\s*": "nos_placeholder ",
        r"\bvs?\.\s*": "vs_placeholder ",
        r"\bSec\.\s*": "sec_placeholder ",
        r"\bArt\.\s*": "art_placeholder ",
        r"\bPara\.\s*": "para_placeholder ",
        r"\bCl\.\s*": "cl_placeholder ",
        r"\bU\.S\.\s*": "us_placeholder ",
        r"\bU\.S\.C\.\s*": "usc_placeholder ",
        r"\bC\.F\.R\.\s*": "cfr_placeholder ",
        r"\bF\.3d\s*": "f3d_placeholder ",
        r"\bJan\.\s*": "jan_placeholder ",
        r"\bFeb\.\s*": "feb_placeholder ",
        r"\bMar\.\s*": "mar_placeholder ",
        r"\bApr\.\s*": "apr_placeholder ",
        r"\bAug\.\s*": "aug_placeholder ",
        r"\bSept?\.\s*": "sep_placeholder ",
        r"\bOct\.\s*": "oct_placeholder ",
        r"\bNov\.\s*": "nov_placeholder ",
        r"\bDec\.\s*": "dec_placeholder ",
        r"\bapprox\.\s*": "approx_placeholder ",
        r"\bw\.r\.t\.\s*": "wrt_placeholder ",
    }

    WEB_NOISE_TOKENS = {
        "explore plus", "login", "become a seller", "more", "cart", "download app", 
        "sign in", "sign up", "register", "menu", "search", "back to top", "help center",
        "24x7 customer care", "security", "sitemap", "about us", "contact us", "careers", 
        "press", "corporate information", "wishlist", "orders", "rewards", "flipkart plus",
        "sports & fitness", "fashion", "mobiles", "electronics", "beauty", "home appliances",
        "toys, baby", "advertise on flipkart", "gift cards", "help center", "consumer policy",
        "mail us", "registered office address", "social", "facebook", "twitter", "youtube",
        "for you", "top offers", "appliances", "grocery", "new customer? sign up", "my profile",
        "mobiles electronics beauty home appliances toys", "flipkart plus zone", "advertise"
    }

    LEGAL_CONTENT_MARKERS = [
        r"\b(?:shall|must|may|covenants?|undertakes?|agrees?|hereby|parties|party)\b",
        r"\b(?:liability|indemnif\w+|warrant\w+|disclaim\w+|terminat\w+|confidential\w*)\b",
        r"\b(?:arbitration|dispute|governed\s+by|jurisdiction|infringement|intellectual\s+property|ip\b)\b",
        r"\b(?:non-compete|non-disclosure|damages|breach|remedy|severability|waiver)\b",
        r"\b(?:agreement|contract|terms\s+of\s+(?:use|service)|user\s+agreement|subscription)\b",
        r"\b(?:force\s+majeure|assign\w*|invention\w*|proprietary|patent\w*|copyright\w*|entire\s+agreement|statutory|in\s+witness\s+whereof)\b",
        r"\b(?:employee|employer|contractor|consultant|confidentiality|non-solicitation)\b",
    ]

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """
        Cleans and normalizes raw text, web scrapes, and OCR scan output.
        Strips navigation noise, orphan UI labels, and HTML artifacts.
        """
        if not text:
            return ""
        
        # 1. HTML unescape
        cleaned = html.unescape(text)
        
        # 2. Strip basic HTML tags while maintaining newlines
        cleaned = re.sub(r"<(?:br|p|div|li|h[1-6])\s*/?>", "\n", cleaned, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        
        # 3. Normalize line endings
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        
        # 4. Decompose Unicode typographic ligatures from OCR
        ligature_map = {
            "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
            "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st", "œ": "oe",
            "æ": "ae", "Œ": "OE", "AE": "AE",
        }
        for lig, repl in ligature_map.items():
            cleaned = cleaned.replace(lig, repl)
            
        # 5. Smart quotes, apostrophes, and dashes
        cleaned = re.sub(r"[\u201c\u201d\u201e\u201f\u2033\u2036«»]", '"', cleaned)
        cleaned = re.sub(r"[\u2018\u2019\u201a\u201b\u2032\u2035\u00b4\u02bc`]", "'", cleaned)
        cleaned = re.sub(r"[\u2013\u2014\u2015\u2212]", "-", cleaned)
        
        # 6. Reconstruct broken hyphenated line wraps (e.g. "indemni-\n fication" -> "indemnification")
        cleaned = re.sub(r"(\b[A-Za-z]+)-\s*\n\s*([A-Za-z]+\b)", r"\1\2", cleaned)
        
        # 7. Strip zero-width spaces, BOMs, and non-breaking spaces
        cleaned = re.sub(r"[\ufeff\u200b\u200c\u200d\u00a0]", " ", cleaned)
        
        # 8. Filter web noise, SEO title bars, and standalone corporate footer artifacts
        lines = cleaned.split("\n")
        filtered_lines = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if s.lower() in self.WEB_NOISE_TOKENS:
                continue
            if re.search(r"\b(?:Store Online|Best Price in India|Flipkart\.com|Explore Plus|Download App)\b", s, re.I) and len(s.split()) < 8:
                continue
            # Filter navigation breadcrumbs (e.g. "Home > Mobiles > Accessories")
            if " > " in s and len(s.split()) < 10:
                continue
            filtered_lines.append(s)
        
        cleaned = "\n".join(filtered_lines)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def segment_sentences(self, text: str) -> List[str]:
        """
        Splits text into coherent sentences with legal citation and abbreviation protection.
        """
        if not text:
            return []

        # 1. Protect currency amounts with decimals (e.g. $50.00, ₹100.50, 18.5%)
        protected = re.sub(r"(\$|₹|€|£)\s*(\d+)\.(\d{2})\b", r"\1\2_dot_\3", text)
        protected = re.sub(r"\b(\d+)\.(\d+)\s*%", r"\1_pctdot_\2%", protected)
        
        # 2. Protect legal abbreviations
        for pattern, repl in self.LEGAL_ABBREVIATIONS.items():
            protected = re.sub(pattern, repl, protected, flags=re.IGNORECASE)

        # 3. Protect subsection numbers inside text (e.g. Section 4.2.1 or Cl. 3(a))
        protected = re.sub(r"\b(Section|Article|Clause|Sec|Art|Cl)\s+(\d+)\.(\d+)\b", r"\1 \2_sdot_\3", protected, flags=re.I)

        # 4. Split on sentence terminal marks (. ? !) or bullet line markers followed by capital letter
        raw_sentences = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9\"'\(\[•●▪■◆►✓✔○▫\-])|(?<=\n)(?=[•●▪■◆►✓✔○▫\-])", protected)

        sentences = []
        for s in raw_sentences:
            s_clean = s.strip()
            if not s_clean:
                continue

            # Restore currency and percentages
            s_clean = s_clean.replace("_dot_", ".").replace("_pctdot_", ".").replace("_sdot_", ".")

            # Restore abbreviations
            for pattern, repl in self.LEGAL_ABBREVIATIONS.items():
                orig = pattern.replace(r"\b", "").replace(r"\s*", " ").replace("\\", "")
                s_clean = s_clean.replace(repl.strip(), orig.strip())

            sentences.append(s_clean)

        return sentences if sentences else [text.strip()]

    def is_legal_sentence(self, sentence: str) -> bool:
        """Determines if a sentence contains substantive legal terminology."""
        s = sentence.strip()
        if len(s.split()) < 4:
            return False
        return any(re.search(pat, s, re.IGNORECASE) for pat in self.LEGAL_CONTENT_MARKERS)

    def is_valid_legal_clause(self, text: str, title: str = "") -> bool:
        """
        Validates whether a text block is a genuine legal contract clause
        versus random webpage noise or product catalogue fragments.
        """
        words = text.strip().split()
        if len(words) < 3:
            return False
        
        # Check for web noise headings
        t_low = title.lower().strip()
        if t_low in self.WEB_NOISE_TOKENS or any(t_low == w for w in self.WEB_NOISE_TOKENS):
            return False

        has_legal_marker = any(re.search(pat, text, re.IGNORECASE) for pat in self.LEGAL_CONTENT_MARKERS)

        # Fallback headings ("Preamble & Recitals", "Clause 1", "Section 1") must have substantive legal markers
        is_fallback_heading = bool(re.match(r"^(?:Clause|Section|Part|Paragraph)\s+\d+$", title.strip(), re.I) or t_low in ("preamble & recitals", "preamble", "recitals"))

        if not is_fallback_heading:
            legal_heading_keywords = [
                "definition", "scope", "payment", "liability", "warranty", "indemnif",
                "confidential", "dispute", "govern", "amend", "renew", "non-compete",
                "intellectual", "property", "arbitration", "assignment", "ip", "invention",
                "cancellation", "termination", "user account", "eligibility", "license",
                "obligation", "data rights", "privacy", "terms of use", "terms of service"
            ]
            if any(w in t_low for w in legal_heading_keywords):
                # Has explicit legal heading - require at least 3 words and no noise tokens
                return True

        # Must contain at least one legal content pattern
        if has_legal_marker:
            return True

        # If length >= 20 words with complete legal sentence punctuation and modal verbs
        if len(words) >= 20 and re.search(r"\b(?:shall|may|must|agrees?|covenants?|undertakes?)\b", text, re.I) and (text.strip().endswith((".", ";", ":", ")", '"', "'")) or ";" in text):
            return True

        return False

    def parse_header_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Classifies a line into (HEADER_TYPE, NUM, TITLE, BODY) or None.
        """
        line_clean = line.strip()
        # Clean OCR pipe margin artifact at start of line
        if line_clean.startswith("|") and not line_clean.startswith("|---"):
            line_clean = line_clean.lstrip("| \t")

        if not line_clean:
            return None

        # Ignore bullet items and table rows
        if (line_clean.startswith("•") or (line_clean.startswith(("-", "*")) and not line_clean.startswith("**"))) or " | " in line_clean:
            return None

        # 1. Part / Section / Article / Clause / Schedule standalone header
        part_match = re.match(
            r"^(?:Part|Section|Article|Clause|Paragraph|Chapter|Appendix|Schedule|Annexure)\s+([0-9IVXLCDMA-Z]+(?:\.\d+)*)\s*[:.\-–—]?\s*(.*)$",
            line_clean, re.I
        )
        if part_match:
            num = part_match.group(1).strip()
            title = part_match.group(2).strip()
            prefix = part_match.group(0).split()[0]
            if not title:
                title = f"{prefix} {num}"
            return ("STANDALONE", num, title, "")

        # 2. Numbered Standalone Header e.g. '1. Definitions', '2. User Account', '3. LIMITATION OF LIABILITY'
        num_match = re.match(
            r"^(\d+(?:\.\d+)*)\.?\s+([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{1,65})[:.]?$",
            line_clean
        )
        if num_match:
            num = num_match.group(1).strip()
            title = num_match.group(2).strip().rstrip(".:")
            if title.lower() not in self.WEB_NOISE_TOKENS:
                return ("STANDALONE", num, title, "")

        # 3. Markdown headers e.g. '### 1. Scope of Service' or '## Dispute Resolution'
        md_match = re.match(
            r"^(#{1,6})\s*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*(.+)$",
            line_clean, re.I
        )
        if md_match:
            num = (md_match.group(2) or "").replace(".", "").strip()
            title = re.sub(r"[*#_`]", "", md_match.group(3)).strip()
            if title.lower() not in self.WEB_NOISE_TOKENS:
                return ("STANDALONE", num, title, "")

        # 4. Bold Markdown headers e.g. '**1. Title**' or '**Section 1: Indemnity**'
        bold_match = re.match(
            r"^\*\*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*([^*]+)\*\*$",
            line_clean, re.I
        )
        if bold_match:
            num = (bold_match.group(1) or "").replace(".", "").strip()
            title = bold_match.group(2).strip()
            if title.lower() not in self.WEB_NOISE_TOKENS:
                return ("STANDALONE", num, title, "")

        # 5. ALL-CAPS standalone header e.g. 'LIMITATION OF LIABILITY'
        if re.match(r"^[A-Z\s,;/\-–—]{4,60}:?$", line_clean) and len(line_clean.split()) <= 7:
            title = line_clean.rstrip(":")
            if title.lower() not in self.WEB_NOISE_TOKENS and any(w in title for w in ["TERMS", "LIABILITY", "INDEMNITY", "TERMINATION", "WARRANTY", "DISPUTE", "CONFIDENTIAL", "PAYMENT", "GOVERNING", "MODIFICATION", "RENEWAL", "GENERAL", "DEFINITIONS"]):
                return ("STANDALONE", "", title, "")

        # 6. Inline Section with body e.g. '1. INDEMNIFICATION. Customer agrees to defend...'
        inline_match = re.match(
            r"^(?:(?:Section|Article|Clause|Paragraph)\s+)?([a-z0-9]+(?:\.[a-z0-9]+)*|\([a-z0-9]+\)|[IVXLCDM]+\.)?\s*[:.\-–—]?\s*([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{2,65})[:.\-–—]\s+(.+)$",
            line_clean, re.I
        )
        if inline_match:
            num = (inline_match.group(1) or "").replace(".", "").replace("(", "").replace(")", "").strip()
            title = inline_match.group(2).strip()
            body = inline_match.group(3).strip()
            if title.lower() not in self.WEB_NOISE_TOKENS and not title.lower().startswith((
                "if ", "the ", "in the event", "provided that", "neither party", "each party", "you agree", "customer shall"
            )):
                return ("INLINE", num, title, body)

        return None

    def infer_clause_title(self, text: str, fallback: str = "Clause") -> str:
        """Infers a domain-accurate title for standalone clauses without explicit headings."""
        t_low = text.lower()
        if re.search(r"\b(?:liability|damages|shall\s+not\s+exceed|capped\s+at)\b", t_low):
            return "Limitation of Liability"
        elif re.search(r"\b(?:terminate|termination|cancellation)\b", t_low):
            return "Termination Clause"
        elif re.search(r"\b(?:indemnif\w+|hold\s+harmless|defend\s+and\s+indemnify)\b", t_low):
            return "Indemnification"
        elif re.search(r"\b(?:confidential\w*|non-disclosure|proprietary\s+information)\b", t_low):
            return "Confidentiality"
        elif re.search(r"\b(?:arbitration|dispute\s+resolution|governing\s+law|jurisdiction)\b", t_low):
            return "Dispute Resolution"
        elif re.search(r"\b(?:payment|invoicing|fees|pricing|billing)\b", t_low):
            return "Payment & Fees"
        elif re.search(r"\b(?:warrant\w*|disclaim\w*|as\s+is)\b", t_low):
            return "Warranties & Disclaimers"
        elif re.search(r"\b(?:non-compete|non-solicitation)\b", t_low):
            return "Restrictive Covenants"
        elif re.search(r"\b(?:intellectual\s+property|inventions?|copyright|patent)\b", t_low):
            return "Intellectual Property"
        elif re.search(r"\b(?:whereas|recitals?|entered\s+into\s+by\s+and\s+between)\b", t_low):
            return "Preamble & Recitals"
        return fallback

    def parse(self, text: str, document_name: str = "Contract Document") -> List[ContractClause]:
        """
        Parses full legal agreement text into a structured list of verified ContractClause objects.
        Filters out non-legal webpage noise and orphan fragments.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        lines = cleaned.split("\n")
        raw_blocks: List[Dict[str, Any]] = []
        
        current_header = ""
        current_num = ""
        current_lines: List[str] = []
        start_line_idx = 1
        is_preamble = True

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue

            header_info = self.parse_header_line(stripped)

            if header_info is not None:
                header_type, matched_num, matched_title, inline_body = header_info

                # Flush previous block if it has content
                if current_lines:
                    block_text = " ".join(current_lines).strip()
                    if block_text:
                        block_title = current_header or self.infer_clause_title(block_text, "Preamble & Recitals" if is_preamble else f"Section {len(raw_blocks) + 1}")

                        raw_blocks.append({
                            "number": current_num or str(len(raw_blocks) + 1),
                            "title": block_title,
                            "text": block_text,
                            "start_line": start_line_idx,
                            "end_line": i - 1,
                        })

                # Start new block
                is_preamble = False
                current_header = matched_title
                current_num = matched_num
                current_lines = [inline_body] if inline_body else []
                start_line_idx = i
                continue

            if self.SUB_ITEM_PATTERN.match(stripped) and (current_lines or current_header):
                current_lines.append(stripped)
                continue

            current_lines.append(stripped)

        # Flush final block
        if current_lines:
            block_text = " ".join(current_lines).strip()
            if block_text:
                block_title = current_header or self.infer_clause_title(block_text, "Preamble & Recitals" if is_preamble else f"Section {len(raw_blocks) + 1}")

                raw_blocks.append({
                    "number": current_num or str(len(raw_blocks) + 1),
                    "title": block_title,
                    "text": block_text,
                    "start_line": start_line_idx,
                    "end_line": len(lines),
                })

        # Fallback if no structured sections were detected (pure paragraph text)
        if not raw_blocks:
            paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
            for idx, p in enumerate(paragraphs, 1):
                raw_blocks.append({
                    "number": str(idx),
                    "title": f"Clause {idx}",
                    "text": p,
                    "start_line": 1,
                    "end_line": len(lines),
                })

        # Filter out non-legal blocks
        clauses: List[ContractClause] = []
        clause_counter = 1

        for block in raw_blocks:
            clause_text = block["text"]
            title = block["title"].strip()
            
            # Strict Legal Content Validation
            if not self.is_valid_legal_clause(clause_text, title=title):
                continue

            sentences = self.segment_sentences(clause_text)
            words = clause_text.split()
            
            # Clean and sanitize title
            clean_title = re.sub(r"[*#_`]", "", title).strip()
            if not clean_title or clean_title.lower() in self.WEB_NOISE_TOKENS:
                clean_title = f"Section {clause_counter}"
            if len(clean_title) > 60:
                clean_title = clean_title[:57] + "..."

            subsections = [s for s in sentences if self.SUB_ITEM_PATTERN.match(s)]

            clauses.append(
                ContractClause(
                    clause_id=f"clause_{clause_counter:03d}",
                    clause_number=block["number"] or str(clause_counter),
                    title=clean_title,
                    text=clause_text,
                    start_line=block["start_line"],
                    end_line=block["end_line"],
                    word_count=len(words),
                    char_count=len(clause_text),
                    sentences=sentences,
                    subsections=subsections,
                    has_subsections=len(subsections) > 0,
                    metadata={"document": document_name},
                )
            )
            clause_counter += 1

        return clauses
