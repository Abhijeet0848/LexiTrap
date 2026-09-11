"""
Document Parser & Hierarchical Clause Segmenter
Handles extraction and segmentation of legal agreements into structured clauses.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


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
            "metadata": self.metadata,
        }


class DocumentParser:
    """
    Parses unstructured legal text into hierarchical clauses and sentences.
    Supports section numbers (1., 1.1, Section 1), Roman numerals (I., IV.),
    lettered points (a., (b)), and title headers.
    """

    CLAUSE_START_PATTERNS = [
        # Section 1 / Section 1.1 / Article 2 / Clause 3: Title
        re.compile(r"^(?:Section|Article|Clause)\s+(\d+(?:\.\d+)*)\s*[:.\-–—]?\s*(.*)$", re.IGNORECASE),
        # 1. / 1.1 / 1.1.1 Title or text
        re.compile(r"^(\d+(?:\.\d+)+|\d+\.)\s*(.*)$"),
        # Roman numerals: I. / IV. / VIII. Title
        re.compile(r"^([IVXLCDM]+)\.\s*(.*)$"),
        # Capitalized ALL-CAPS headers (e.g., "INDEMNIFICATION", "LIMITATION OF LIABILITY")
        re.compile(r"^([A-Z\s]{4,50})(?::)?$"),
    ]

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Normalizes line endings and removes redundant spacing."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove BOM or weird unicode chars
        text = text.replace("\ufeff", "").replace("\u200b", "")
        return text.strip()

    def segment_sentences(self, text: str) -> List[str]:
        """
        Splits text into sentences while respecting legal abbreviations like
        e.g., i.e., et al., v., Inc., Ltd., etc.
        """
        # Protect common abbreviations
        protected = text
        abbreviations = {
            r"\be\.g\.\s*": "eg_placeholder ",
            r"\bi\.e\.\s*": "ie_placeholder ",
            r"\bet al\.\s*": "etal_placeholder ",
            r"\bInc\.\s*": "inc_placeholder ",
            r"\bLtd\.\s*": "ltd_placeholder ",
            r"\bCorp\.\s*": "corp_placeholder ",
            r"\bNo\.\s*": "no_placeholder ",
            r"\bvs?\.\s*": "vs_placeholder ",
            r"\bSec\.\s*": "sec_placeholder ",
            r"\bArt\.\s*": "art_placeholder ",
        }
        for pattern, repl in abbreviations.items():
            protected = re.sub(pattern, repl, protected, flags=re.IGNORECASE)

        # Split on sentence boundaries: period, exclamation, question mark followed by space or newline
        raw_sentences = re.split(r"(?<=[.?!])\s+(?=[A-Z0-9\"'\(])", protected)

        sentences = []
        for s in raw_sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            # Restore abbreviations
            for pattern, repl in abbreviations.items():
                orig = pattern.replace(r"\b", "").replace(r"\s*", " ").replace("\\", "")
                s_clean = s_clean.replace(repl.strip(), orig.strip())
            sentences.append(s_clean)

        return sentences if sentences else [text.strip()]

    def parse(self, text: str, document_name: str = "Contract Document") -> List[ContractClause]:
        """
        Parses full legal agreement text into a structured list of ContractClause objects.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        lines = cleaned.split("\n")
        raw_blocks = []
        current_header = ""
        current_num = ""
        current_lines = []
        start_line_idx = 1

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                # Empty line: if we have content, keep accumulating
                continue

            # Check if this line is a new clause header
            is_new_header = False
            matched_num = ""
            matched_title = ""

            for pat in self.CLAUSE_START_PATTERNS:
                m = pat.match(stripped)
                if m:
                    groups = m.groups()
                    if len(groups) == 2:
                        matched_num = groups[0].strip()
                        matched_title = groups[1].strip()
                    elif len(groups) == 1:
                        matched_title = groups[0].strip()
                        matched_num = ""
                    is_new_header = True
                    break

            if is_new_header:
                if current_lines:
                    block_text = " ".join(current_lines).strip()
                    if block_text:
                        raw_blocks.append({
                            "number": current_num or str(len(raw_blocks) + 1),
                            "title": current_header or f"Clause {len(raw_blocks) + 1}",
                            "text": block_text,
                            "start_line": start_line_idx,
                            "end_line": i - 1,
                        })
                current_num = matched_num
                current_header = matched_title if matched_title else matched_num
                current_lines = [matched_title] if (matched_title and matched_title != matched_num) else []
                start_line_idx = i
            else:
                current_lines.append(stripped)

        # Flush the last block
        if current_lines:
            block_text = " ".join(current_lines).strip()
            if block_text:
                raw_blocks.append({
                    "number": current_num or str(len(raw_blocks) + 1),
                    "title": current_header or f"Clause {len(raw_blocks) + 1}",
                    "text": block_text,
                    "start_line": start_line_idx,
                    "end_line": len(lines),
                })

        # Fallback if no structured sections were detected (e.g., pure unformatted paragraphs)
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
            
            # Clean up title if it's too long
            title = block["title"]
            if len(title) > 60:
                title = title[:57] + "..."
            if not title:
                title = f"Clause {idx}"

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
                    metadata={"document": document_name},
                )
            )

        return clauses
