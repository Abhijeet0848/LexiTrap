"""
Advanced Document Parser & Hierarchical Legal Clause Segmenter
Handles extraction, boundary segmentation, inline title isolation,
HTML/Markdown cleanup, and abbreviation-safe sentence tokenization for legal agreements.
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
    - HTML and markdown markup cleaning
    - Sub-clause preservation (preventing fragmented (a), (b), (i) splitting)
    - Protected legal abbreviation sentence boundary tokenizer
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

    def __init__(self):
        pass

    NON_CLAUSE_HEADER_TOKENS = {
        "days", "day", "hours", "weeks", "months", "additional cost", "free", "refund",
        "replacement", "exchange", "lifestyle", "no", "yes", "na", "n/a", "etc", "none",
        "furniture", "home", "books", "electronics", "fashion", "mobiles", "appliances",
        "grocery", "toys", "sports", "auto", "beauty", "music", "category", "about",
        "consumer policy", "mail us", "registered office address", "karnataka, india"
    }

    WEB_NOISE_LINES = {
        "explore plus", "login", "become a seller", "more", "cart", "download app", 
        "sign in", "sign up", "register", "menu", "search", "back to top", "help center",
        "24x7 customer care", "terms of use", "security", "privacy", "sitemap", "about us",
        "contact us", "careers", "press", "corporate information"
    }

    def clean_text(self, text: str) -> str:
        """
        Cleans and normalizes raw text, web scrapes, and OCR scan output:
        - Unescapes HTML entities (&amp;, &lt;, &gt;, &quot;)
        - Strips HTML tags (e.g. <p>, <div>, <br>)
        - Decomposes typographic ligatures (ﬁ -> fi, ﬂ -> fl, ﬀ -> ff, etc.)
        - Normalizes smart quotes, apostrophes, and dashes
        - Reconstructs broken hyphenated line-wraps from OCR scans (e.g. "indemni-\n fication" -> "indemnification")
        - Strips web layout noise, SEO title bars, and orphan footer markers
        - Normalizes Windows (CRLF) and Unix (LF) line endings
        - Strips zero-width unicode artifacts and collapses whitespace
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
            "\ufb00": "ff",
            "\ufb01": "fi",
            "\ufb02": "fl",
            "\ufb03": "ffi",
            "\ufb04": "ffl",
            "\ufb05": "st",
            "\ufb06": "st",
            "œ": "oe",
            "æ": "ae",
            "Œ": "OE",
            "AE": "AE",
        }
        for lig, repl in ligature_map.items():
            cleaned = cleaned.replace(lig, repl)
            
        # 5. Smart quotes, apostrophes, and dashes
        cleaned = re.sub(r"[\u201c\u201d\u201e\u201f\u2033\u2036«»]", '"', cleaned)
        cleaned = re.sub(r"[\u2018\u2019\u201a\u201b\u2032\u2035\u00b4\u02bc`]", "'", cleaned)
        cleaned = re.sub(r"[\u2013\u2014\u2015\u2212]", "-", cleaned)
        
        # 6. Reconstruct broken hyphenated line wraps (e.g. "indemni-\n fication" -> "indemnification")
        cleaned = re.sub(r"(\b[A-Za-z]+)-\s*\n\s*([A-Za-z]+\b)", r"\1\2", cleaned)
        
        # 7. Strip stray OCR margin pipe artifacts
        cleaned = re.sub(r"(?:^|\n)\s*\|\s*", "\n", cleaned)

        # 8. Remove zero-width spaces, BOMs, and non-breaking spaces
        cleaned = re.sub(r"[\ufeff\u200b\u200c\u200d\u00a0]", " ", cleaned)
        
        # 9. Filter web noise, SEO title bars, and standalone corporate footer artifacts
        lines = cleaned.split("\n")
        filtered_lines = []
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if re.search(r"\b(?:Store Online|Best Price in India|Flipkart\.com)\b", s, re.I):
                continue
            if s.lower() in self.WEB_NOISE_LINES:
                continue
            filtered_lines.append(s)
        
        cleaned = "\n".join(filtered_lines)

        # 10. Collapse excessive blank lines
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

        # 4. Split on sentence terminal marks (. ? !) or bullet line markers followed by capital letter / quote / digit / bullet
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

    def parse_header_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Classifies a line into (HEADER_TYPE, NUM, TITLE, BODY) or None.
        HEADER_TYPE is either 'STANDALONE' or 'INLINE'.
        """
        line_clean = line.strip()
        if not line_clean:
            return None

        # Ignore bullet items, table rows, and pipe lines (while allowing bold markdown headers starting with **)
        if (line_clean.startswith(("•", "|")) or (line_clean.startswith(("-", "*")) and not line_clean.startswith("**"))) or " | " in line_clean:
            return None

        # 1. Part / Section / Article / Chapter / Schedule / Annexure standalone header
        part_match = re.match(
            r"^(?:Part|Section|Article|Clause|Paragraph|Chapter|Appendix|Schedule|Annexure|Exhibit)\s+([0-9IVXLCDMA-Z]+(?:\.\d+)*)\s*[:.\-–—]?\s*(.*)$",
            line_clean, re.I
        )
        if part_match:
            num = part_match.group(1).strip()
            title = part_match.group(2).strip()
            prefix = part_match.group(0).split()[0]
            if not title:
                title = f"{prefix} {num}"
            elif prefix.lower() in {"part", "chapter", "schedule", "annexure"}:
                title = f"{prefix} {num}: {title}"
            return ("STANDALONE", num, title, "")

        # 2. Markdown headers e.g. '### 1. Scope of Service' or '## Dispute Resolution'
        md_match = re.match(
            r"^(#{1,6})\s*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*(.+)$",
            line_clean, re.I
        )
        if md_match:
            num = (md_match.group(2) or "").replace(".", "").strip()
            title = re.sub(r"[*#_`]", "", md_match.group(3)).strip()
            if title.lower() not in self.NON_CLAUSE_HEADER_TOKENS:
                return ("STANDALONE", num, title, "")

        # 3. Bold Markdown headers e.g. '**1. Title**' or '**Section 1: Indemnity**'
        bold_match = re.match(
            r"^\*\*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*([^*]+)\*\*$",
            line_clean, re.I
        )
        if bold_match:
            num = (bold_match.group(1) or "").replace(".", "").strip()
            title = bold_match.group(2).strip()
            if title.lower() not in self.NON_CLAUSE_HEADER_TOKENS:
                return ("STANDALONE", num, title, "")

        # 4. Numbered Standalone Header e.g. '1. Definitions', '1.1 Scope of Work', '1. MODIFICATION OF TERMS.'
        num_match = re.match(
            r"^(\d+(?:\.\d+)*)\.?\s+([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{1,70})[:.]?$",
            line_clean
        )
        if num_match:
            num = num_match.group(1).strip()
            title = num_match.group(2).strip().rstrip(".:")
            if title.lower() not in self.NON_CLAUSE_HEADER_TOKENS:
                return ("STANDALONE", num, title, "")

        # 5. ALL-CAPS standalone header e.g. 'LIMITATION OF LIABILITY'
        if re.match(r"^[A-Z\s,;/\-–—]{4,60}:?$", line_clean) and len(line_clean.split()) <= 8:
            title = line_clean.rstrip(":")
            if title.lower() not in self.NON_CLAUSE_HEADER_TOKENS:
                return ("STANDALONE", "", title, "")

        # 6. Standalone Policy Title Lines (e.g. 'Cancellation Policy - Hyperlocal', 'Easy Doorstep Cancellation', 'Returns Policy')
        words = line_clean.split()
        if 1 <= len(words) <= 7 and len(line_clean) <= 65 and not line_clean.endswith((".", ";", ",")) and not line_clean[0].islower():
            lower = line_clean.lower()
            not_starters = (
                "the ", "if ", "you ", "we ", "in ", "for ", "any ", "all ", "each ",
                "either ", "neither ", "customer ", "user ", "by ", "except ", "subject ",
                "such ", "this ", "these ", "under ", "provided ", "whereas ", "now therefore", 
                "do read", "refer ", "our ", "free ", "brand ", "please "
            )
            is_title_case = all(w[0].isupper() or w.lower() in {"and", "or", "of", "the", "in", "on", "for", "to", "with", "a", "an", "-", "/", "&"} for w in words if w)
            has_policy_kw = bool(re.search(r"\b(?:Policy|Terms|Cancellation|Returns|Guidelines|Rules|Agreement|Provisions|Notice|Dispute|Warranty|Delivery|Hyperlocal|Conditions|Exceptions|Obligations|Liability|Indemnity)\b", line_clean, re.I))
            
            if not lower.startswith(not_starters) and (is_title_case or has_policy_kw) and lower not in self.NON_CLAUSE_HEADER_TOKENS:
                return ("STANDALONE", "", line_clean, "")

        # 7. Inline Section with body e.g. '1. INDEMNIFICATION. Customer agrees to defend...', '3.e Disputes/Binding Arbitration. Any dispute...', or 'a. Use of Services. To use...'
        inline_match = re.match(
            r"^(?:(?:Section|Article|Clause|Paragraph)\s+)?([a-z0-9]+(?:\.[a-z0-9]+)*|\([a-z0-9]+\)|[IVXLCDM]+\.)?\s*[:.\-–—]?\s*([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{2,75})[:.\-–—]\s+(.+)$",
            line_clean, re.I
        )
        if inline_match:
            num = (inline_match.group(1) or "").replace(".", "").replace("(", "").replace(")", "").strip()
            title = inline_match.group(2).strip()
            body = inline_match.group(3).strip()
            words = title.split()
            if len(words) <= 9 and title.lower() not in self.NON_CLAUSE_HEADER_TOKENS and not title.lower().startswith((
                "if ", "the ", "in the event", "provided that", "neither party", "each party", "you agree", "customer shall", "we reserve", "we will", "when you"
            )):
                return ("INLINE", num, title, body)

        return None

    def parse(self, text: str, document_name: str = "Contract Document") -> List[ContractClause]:
        """
        Parses full legal agreement text into a structured list of ContractClause objects.
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

            # Classify line as a clause or named subclause header first
            header_info = self.parse_header_line(stripped)

            if header_info is not None:
                header_type, matched_num, matched_title, inline_body = header_info

                # Flush previous block if it has content
                if current_lines:
                    block_text = " ".join(current_lines).strip()
                    if block_text:
                        block_title = current_header
                        if not block_title and is_preamble:
                            block_title = "Preamble & Recitals"
                        elif not block_title:
                            block_title = f"Clause {len(raw_blocks) + 1}"

                        raw_blocks.append({
                            "number": current_num or str(len(raw_blocks) + 1),
                            "title": block_title,
                            "text": block_text,
                            "start_line": start_line_idx,
                            "end_line": i - 1,
                        })
                        is_preamble = False

                current_num = matched_num
                current_header = matched_title
                current_lines = [inline_body] if inline_body else []
                start_line_idx = i
                continue

            # Check if this line is a sub-bullet item like (a), (b), (i), •, - inside an existing clause
            if self.SUB_ITEM_PATTERN.match(stripped) and (current_lines or current_header):
                current_lines.append(stripped)
                continue

            current_lines.append(stripped)

        # Flush the final block
        if current_lines:
            block_text = " ".join(current_lines).strip()
            if block_text:
                block_title = current_header
                if not block_title and is_preamble:
                    block_title = "Preamble & Recitals"
                elif not block_title:
                    block_title = f"Clause {len(raw_blocks) + 1}"

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

        clauses: List[ContractClause] = []
        for idx, block in enumerate(raw_blocks, 1):
            clause_text = block["text"]
            sentences = self.segment_sentences(clause_text)
            words = clause_text.split()
            
            # Clean and sanitize title
            title = block["title"]
            title = re.sub(r"[*#_`]", "", title).strip()
            if not title:
                title = f"Clause {idx}"
            if len(title) > 65:
                title = title[:62] + "..."

            # Extract subclauses (e.g. (a), (b), (i))
            subsections = []
            for s in sentences:
                if self.SUB_ITEM_PATTERN.match(s):
                    subsections.append(s)

            clauses.append(
                ContractClause(
                    clause_id=f"clause_{idx:03d}",
                    clause_number=block["number"],
                    title=title,
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

        return clauses
