"""
Comprehensive Audit Report Generator for LexiTrap.
Generates:
1. Academic Markdown Audit Reports
2. Professional PDF Audit Reports using ReportLab
"""

import io
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_markdown_report(
    audit_data: Dict[str, Any],
    nlp_stats: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a structured, exportable Markdown audit report.
    """
    summary = audit_data.get("summary", {})
    clauses = audit_data.get("clauses", [])
    dist = summary.get("risk_distribution", {})

    md_lines = [
        "# ⚖️ LexiTrap — Contract Risk & NLP Audit Report",
        "> **Academic Natural Language Processing & Contract Risk Assessment System**",
        "",
        "---",
        "",
        "## 📊 1. Executive Summary",
        f"- **Overall Grade:** `{summary.get('overall_grade', 'N/A')}`",
        f"- **Average Risk Score:** **{summary.get('average_risk_score', 0)} / 100**",
        f"- **Total Clauses Audited:** **{summary.get('total_clauses', 0)}**",
        f"- **Critical Trap Clauses:** `{dist.get('CRITICAL', 0)}`",
        f"- **High Risk Clauses:** `{dist.get('HIGH', 0)}`",
        f"- **Medium Risk Clauses:** `{dist.get('MEDIUM', 0)}`",
        f"- **Low Risk / Safe Clauses:** `{dist.get('LOW', 0)}`",
        "",
        f"**Assessment Verdict:** {summary.get('overall_status', '')}",
        "",
        "---",
        "",
        "## 🧠 2. NLP Pipeline Statistics",
    ]

    if nlp_stats and "statistics" in nlp_stats:
        stats = nlp_stats["statistics"]
        md_lines.extend([
            f"- **Character Count:** {stats.get('character_count', 0)}",
            f"- **Word Count:** {stats.get('word_count', 0)}",
            f"- **Sentence Count:** {stats.get('sentence_count', 0)}",
            f"- **Avg Words per Sentence:** {stats.get('average_sentence_length_words', 0)}",
            f"- **Preserved Legal Keywords:** {', '.join(nlp_stats.get('preserved_legal_keywords', [])) or 'None'}",
            ""
        ])
    else:
        md_lines.extend(["- NLP corpus metrics extracted from segmented clauses.", ""])

    md_lines.extend([
        "---",
        "",
        "## 🔍 3. Granular Clause-by-Clause Findings",
        ""
    ])

    for c in clauses:
        md_lines.extend([
            f"### {c.get('section_number', '')} {c.get('title', 'Clause')} — [{c.get('category', 'Other')}]",
            f"- **Risk Level:** `{c.get('risk_level', 'LOW')}` (Score: **{c.get('risk_score', 0)}/100**)",
            f"- **Subject Symmetry:** `{c.get('symmetry', 'NEUTRAL')}`",
            "",
            "**Clause Text:**",
            f"> {c.get('text', '')}",
            "",
            f"**NLP Audit Rationale:** {c.get('explanation', '')}",
            "",
            f"**Actionable Recommendation:** {c.get('recommendation', '')}",
            ""
        ])

        if c.get("suggested_rewrite"):
            rew = c["suggested_rewrite"]
            md_lines.extend([
                "**Suggested Balanced Wording (AI-Generated):**",
                f"```text\n{rew.get('suggested_balanced_clause', '')}\n```",
                ""
            ])

        md_lines.append("---")
        md_lines.append("")

    md_lines.extend([
        "## ⚖️ 4. Academic Disclaimer",
        (
            "LexiTrap is an AI/NLP-based educational contract analysis system. "
            "It identifies potentially noteworthy language and does not provide legal advice or guarantee "
            "that a contract is safe or enforceable. Users should consult a qualified legal professional for legal advice."
        ),
        ""
    ])

    return "\n".join(md_lines)


def generate_pdf_report(
    audit_data: Dict[str, Any],
    nlp_stats: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Generates a formatted PDF report as raw bytes using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    clause_box_style = ParagraphStyle(
        'ClauseBox',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=6
    )
    rewrite_box_style = ParagraphStyle(
        'RewriteBox',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#065f46"),
        backColor=colors.HexColor("#ecfdf5"),
        borderColor=colors.HexColor("#a7f3d0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # Title & Header
    story.append(Paragraph("⚖️ LexiTrap — Contract Risk & NLP Audit Report", title_style))
    story.append(Paragraph("MCA Academic Project • Natural Language Processing & Contract Risk Assessment", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0284c7"), spaceAfter=10))

    summary = audit_data.get("summary", {})
    clauses = audit_data.get("clauses", [])
    dist = summary.get("risk_distribution", {})

    # Executive Summary Table
    story.append(Paragraph("1. Executive Summary & Health Grade", h2_style))
    
    summary_table_data = [
        [
            Paragraph("<b>Overall Health Grade:</b>", body_style),
            Paragraph(f"<b>{summary.get('overall_grade', 'N/A')}</b>", body_style),
            Paragraph("<b>Avg Risk Score:</b>", body_style),
            Paragraph(f"<b>{summary.get('average_risk_score', 0)} / 100</b>", body_style)
        ],
        [
            Paragraph("<b>Total Clauses:</b>", body_style),
            Paragraph(str(summary.get('total_clauses', 0)), body_style),
            Paragraph("<b>Critical Traps:</b>", body_style),
            Paragraph(str(dist.get('CRITICAL', 0)), body_style)
        ],
        [
            Paragraph("<b>High Risk Clauses:</b>", body_style),
            Paragraph(str(dist.get('HIGH', 0)), body_style),
            Paragraph("<b>Medium / Low:</b>", body_style),
            Paragraph(f"{dist.get('MEDIUM', 0)} / {dist.get('LOW', 0)}", body_style)
        ]
    ]

    t_summary = Table(summary_table_data, colWidths=[120, 150, 120, 150])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # Clause Findings
    story.append(Paragraph("2. Granular Clause Risk & Mitigation Analysis", h2_style))

    for idx, c in enumerate(clauses[:15]):  # Report up to 15 key clauses
        clause_elements = []
        header_text = f"<b>{c.get('section_number', '')} {c.get('title', f'Clause {idx+1}')}</b> — {c.get('category', 'Other')} | Risk: <b>{c.get('risk_level', 'LOW')} ({c.get('risk_score', 0)}/100)</b>"
        clause_elements.append(Paragraph(header_text, body_style))
        clause_elements.append(Spacer(1, 3))
        
        clause_elements.append(Paragraph(f"<i>Text:</i> {c.get('text', '')}", clause_box_style))
        clause_elements.append(Paragraph(f"<b>Audit Findings:</b> {c.get('explanation', '')}", body_style))
        clause_elements.append(Paragraph(f"<b>Recommendation:</b> {c.get('recommendation', '')}", body_style))
        
        if c.get("suggested_rewrite"):
            rew = c["suggested_rewrite"]
            clause_elements.append(Spacer(1, 3))
            clause_elements.append(Paragraph(f"<b>AI Suggested Balanced Rewrite:</b><br/>{rew.get('suggested_balanced_clause', '')}", rewrite_box_style))
            
        clause_elements.append(Spacer(1, 8))
        story.append(KeepTogether(clause_elements))

    # Mandatory Legal Disclaimer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=6))
    disclaimer_text = (
        "<b>Academic Disclaimer:</b> LexiTrap is an AI/NLP-based educational contract analysis system. "
        "It identifies potentially noteworthy language and does not provide legal advice or guarantee "
        "that a contract is safe or enforceable. Users should consult a qualified legal professional for legal advice."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle('Disc', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor("#64748b"))))

    doc.build(story)
    return buffer.getvalue()
