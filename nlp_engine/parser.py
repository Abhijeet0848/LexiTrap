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
    SUB_ITEM_PATTERN = re.compile(r"^(?:\([a-z0-9]+\)|[a-z]\.|\([ivxlcdm]+\))\s+", re.I)

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

    def clean_text(self, text: str) -> str:
        """
        Cleans and normalizes raw text:
        - Unescapes HTML entities (&amp;, &lt;, &gt;, &quot;)
        - Strips HTML tags (e.g. <p>, <div>, <br>)
        - Normalizes Windows (CRLF) and Unix (LF) line endings
        - Strips zero-width unicode artifacts
        """
        if not text:
            return ""
        
        # HTML unescape
        cleaned = html.unescape(text)
        
        # Strip basic HTML tags while maintaining newlines
        cleaned = re.sub(r"<(?:br|p|div|li|h[1-6])\s*/?>", "\n", cleaned, flags=re.I)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        
        # Normalize line endings
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove zero-width spaces and BOMs
        cleaned = re.sub(r"[\ufeff\u200b\u200c\u200d\u00a0]", " ", cleaned)
        
        # Collapse excessive blank lines
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

        # 4. Split on sentence terminal marks (. ? !) followed by whitespace and capital letter / quote / digit
        raw_sentences = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9\"'\(])", protected)

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

        # 1. Markdown headers e.g. '### 1. Scope of Service' or '## Dispute Resolution'
        md_match = re.match(
            r"^(#{1,6})\s*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*(.+)$",
            line_clean, re.I
        )
        if md_match:
            num = (md_match.group(2) or "").replace(".", "").strip()
            title = re.sub(r"[*#_`]", "", md_match.group(3)).strip()
            return ("STANDALONE", num, title, "")

        # 2. Bold Markdown headers e.g. '**1. Title**' or '**Section 1: Indemnity**'
        bold_match = re.match(
            r"^\*\*(?:(?:Section|Article|Clause|Paragraph)\s+)?(?:(\d+(?:\.\d+)*|[IVXLCDM]+\.)\s*)?[:.\-–—]?\s*([^*]+)\*\*$",
            line_clean, re.I
        )
        if bold_match:
            num = (bold_match.group(1) or "").replace(".", "").strip()
            title = bold_match.group(2).strip()
            return ("STANDALONE", num, title, "")

        # 3. Explicit Section/Article Standalone Header e.g. 'Section 1. Definitions' or 'Article II: Governing Law'
        sec_match = re.match(
            r"^(?:Section|Article|Clause|Paragraph|Schedule|Exhibit)\s+(\d+(?:\.\d+)*|[IVXLCDM]+)\s*[:.\-–—]?\s*(.*)$",
            line_clean, re.I
        )
        if sec_match:
            num = sec_match.group(1).strip()
            title = sec_match.group(2).strip()
            if not title:
                title = f"Section {num}"
            return ("STANDALONE", num, title, "")

        # 4. Numbered Standalone Header e.g. '1. Definitions' or '1.1 Scope of Work'
        num_match = re.match(
            r"^(\d+(?:\.\d+)*)\.?\s+([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{1,60})$",
            line_clean
        )
        if num_match:
            num = num_match.group(1).strip()
            title = num_match.group(2).strip()
            return ("STANDALONE", num, title, "")

        # 5. Inline Section with body e.g. '1. INDEMNIFICATION. Customer agrees to defend...' or 'Section 1: Indemnity - Customer shall...'
        inline_match = re.match(
            r"^(?:(?:Section|Article|Clause|Paragraph)\s+)?(\d+(?:\.\d+)*|[IVXLCDM]+\.)?\s*[:.\-–—]?\s*([A-Za-z][A-Za-z0-9\s/&,;'\(\)\-–—]{1,40})[:.\-–—]\s+(.+)$",
            line_clean, re.I
        )
        if inline_match:
            num = (inline_match.group(1) or "").replace(".", "").strip()
            title = inline_match.group(2).strip()
            body = inline_match.group(3).strip()
            if len(title.split()) <= 7 and not title.lower().startswith((
                "if ", "the ", "in the event", "provided that", "neither party", "each party", "you agree", "customer shall"
            )):
                return ("INLINE", num, title, body)

        # 6. ALL-CAPS standalone header e.g. 'LIMITATION OF LIABILITY'
        if re.match(r"^[A-Z\s,;/\-–—]{4,60}:?$", line_clean) and len(line_clean.split()) <= 8:
            return ("STANDALONE", "", line_clean.rstrip(":"), "")

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

            # Check if this line is a sub-bullet item like (a), (b), (i) inside an existing clause
            if self.SUB_ITEM_PATTERN.match(stripped) and current_lines:
                current_lines.append(stripped)
                continue

            # Classify line as a clause header
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
            else:
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
