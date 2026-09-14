"""
Automated Redline & Safe Alternative Generator
Generates balanced, reciprocal replacement clauses with highlighted diffs and legal rationales.
"""

import re
import difflib
import html
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .parser import ContractClause
from .trap_detector import TrapMatch, TrapCategory
from .benchmarks import BenchmarkMatcher


@dataclass
class RedlineResult:
    redline_id: str
    clause_id: str
    clause_title: str
    trap_category: str
    severity: str
    original_text: str
    recommended_text: str
    diff_html: str
    strike_through_summary: List[str]
    additions_summary: List[str]
    legal_rationale: str
    negotiation_talking_point: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "redline_id": self.redline_id,
            "clause_id": self.clause_id,
            "clause_title": self.clause_title,
            "trap_category": self.trap_category,
            "severity": self.severity,
            "original_text": self.original_text,
            "recommended_text": self.recommended_text,
            "diff_html": self.diff_html,
            "strike_through_summary": self.strike_through_summary,
            "additions_summary": self.additions_summary,
            "legal_rationale": self.legal_rationale,
            "negotiation_talking_point": self.negotiation_talking_point,
        }


class RedlineGenerator:
    """
    Generates balanced alternative wording for detected predatory clauses
    and generates visual strike-through / insertion diffs.
    """

    BALANCED_TEMPLATES = {
        TrapCategory.UNILATERAL_MODIFICATION: {
            "template": (
                "Neither party may modify or amend this Agreement without prior written mutual consent. "
                "Vendor may update standard operational policies upon providing at least thirty (30) calendar days' "
                "prior written notice to Customer. In the event of a material change adverse to Customer, Customer "
                "reserves the right to terminate the service without penalty and receive a full pro-rata refund "
                "for any unutilized subscription period."
            ),
            "rationale": "Protects against surprise price increases, stealth feature deprecations, and loss of critical SLAs.",
            "negotiation": "State: 'We require a standard 30-day notice and mutual sign-off for material contract alterations.'",
            "strikes": ["at any time without notice", "in our sole discretion", "continued use constitutes acceptance"],
            "adds": ["30 days prior written notice", "right to terminate without penalty", "pro-rata refund"],
        },
        TrapCategory.ASYMMETRIC_INDEMNIFICATION: {
            "template": (
                "Each party ('Indemnifying Party') agrees to defend, indemnify, and hold harmless the other party "
                "('Indemnified Party'), its officers, and employees from and against any third-party claims, liabilities, "
                "losses, and reasonable legal expenses arising directly from: (a) the Indemnifying Party's gross negligence "
                "or willful misconduct; or (b) any claim that the services or materials provided infringe upon any valid "
                "third-party copyright, patent, or intellectual property right. The aggregate indemnification liability under "
                "this Agreement shall be subject to the Liability Cap established herein."
            ),
            "rationale": "Restores bilateral fairness, making the vendor liable for third-party patent/copyright infringement caused by their own software.",
            "negotiation": "State: 'We cannot accept unilateral indemnification without reciprocal IP infringement protection from the vendor.'",
            "strikes": ["Customer shall solely indemnify", "indemnify against all losses", "uncapped indemnification"],
            "adds": ["Each party agrees to defend and indemnify mutually", "Vendor IP infringement indemnity", "Subject to liability cap"],
        },
        TrapCategory.FORCED_ARBITRATION_CLASS_WAIVER: {
            "template": (
                "Any dispute arising out of or related to this Agreement shall first be submitted to senior executives "
                "of both parties for good-faith resolution within thirty (30) days. If unresolved, disputes may be submitted "
                "to confidential mediation. Either party may seek equitable or injunctive relief in any court of competent "
                "jurisdiction to protect intellectual property or confidential trade secrets. Customer reserves all statutory "
                "court rights and remedies."
            ),
            "rationale": "Prevents secret, mandatory arbitration proceedings and preserves your right to seek legal remedies in open court.",
            "negotiation": "State: 'Our corporate governance policy requires maintaining access to local court remedies and standard mediation steps.'",
            "strikes": ["waive any right to a jury trial", "waive class action rights", "binding confidential arbitration"],
            "adds": ["Good-faith executive mediation", "Access to court jurisdiction", "Preserved statutory remedies"],
        },
        TrapCategory.AGGRESSIVE_IP_EXPROPRIATION: {
            "template": (
                "Customer retains sole and exclusive ownership of all right, title, and interest in and to all Customer Data, "
                "confidential materials, and proprietary workflows. Customer grants Vendor a non-exclusive, non-sublicensable, "
                "revocable license solely to process Customer Data strictly to the extent necessary to deliver the services. "
                "Any suggestions or feedback provided by Customer are voluntary and shall not convey any intellectual property rights."
            ),
            "rationale": "Guarantees that your proprietary workflows, data, and suggestions cannot be seized or claimed by the vendor.",
            "negotiation": "State: 'Customer Data and derivative insights must remain the exclusive property of the customer at all times.'",
            "strikes": ["irrevocably assign to company", "all feedback shall be sole property of vendor", "perpetual worldwide assignment"],
            "adds": ["Customer retains exclusive ownership", "revocable limited processing license", "voluntary non-binding feedback"],
        },
        TrapCategory.PERPETUAL_DATA_AI_HARVESTING: {
            "template": (
                "Vendor explicitly agrees that Customer Data, prompts, confidential documents, and uploaded content shall NOT "
                "be stored, aggregated, or utilized to train, fine-tune, or improve any artificial intelligence, large language "
                "model (LLM), or machine learning system of Vendor or any third party. Customer Data shall remain isolated in "
                "a secure tenant and purged upon session termination or agreement expiration."
            ),
            "rationale": "Guarantees that your confidential business data and trade secrets will not be ingested into commercial AI weights.",
            "negotiation": "State: 'We require a strict Zero-Data-Retention and No-AI-Training covenant for enterprise data privacy compliance.'",
            "strikes": ["use your data to train machine learning models", "develop AI algorithms", "perpetual right to aggregate"],
            "adds": ["Strict Zero-AI-Training guarantee", "Data isolation in secure tenant", "Automatic purge upon termination"],
        },
        TrapCategory.TRAPPED_AUTO_RENEWAL: {
            "template": (
                "This Agreement shall automatically renew for successive terms equal to the initial term, provided that Vendor "
                "delivers a written reminder notification to Customer at least thirty (30) days prior to the renewal date. "
                "Customer may terminate or modify the subscription at any time prior to renewal by providing fifteen (15) days "
                "written notice or via the self-service web billing portal."
            ),
            "rationale": "Prevents inadvertent multi-year lock-in by enforcing proactive vendor reminder notices and easy digital cancellation.",
            "negotiation": "State: 'We require automated 30-day renewal reminders and self-service online cancellation.'",
            "strikes": ["90 days prior certified mail notice", "strictly non-refundable", "auto-renews without notice"],
            "adds": ["30-day advance reminder requirement", "15-day cancellation notice window", "in-app self-service cancel"],
        },
        TrapCategory.OVERBROAD_NON_COMPETE: {
            "template": (
                "During the Term and for a period of six (6) months thereafter, Recipient shall not directly solicit for employment "
                "any current key executive of Discloser. Nothing in this Agreement shall restrict, impede, or prohibit Recipient "
                "or its personnel from engaging in their trade, accepting general employment, or providing services to any other client."
            ),
            "rationale": "Eliminates unlawful and restrictive trade barriers while preserving fair non-solicitation of key personnel.",
            "negotiation": "State: 'In alignment with current FTC regulations, broad non-compete clauses must be replaced with reasonable non-solicitation terms.'",
            "strikes": ["shall not engage in any competing business", "worldwide for 2 years", "prohibited from working in the industry"],
            "adds": ["Reasonable 6-month non-solicitation", "Full mobility of personnel", "Protection of right to work"],
        },
        TrapCategory.ZERO_LIABILITY_GUTTING: {
            "template": (
                "Except for indemnity obligations, breaches of confidentiality, or gross negligence/willful misconduct, each party's "
                "total aggregate liability arising under this Agreement shall be capped at the total fees paid or payable by Customer "
                "under this Agreement in the twelve (12) months preceding the incident. Neither party shall be liable for indirect, "
                "punitive, or consequential damages."
            ),
            "rationale": "Establishes a realistic mutual liability ceiling (12 months of fees paid) with vital carve-outs for data breaches and gross misconduct.",
            "negotiation": "State: 'A nominal or zero liability cap is uninsurable and commercially unacceptable; 12 months fees paid is standard.'",
            "strikes": ["liability shall not exceed nominal amounts", "total liability of zero", "as is with no warranty"],
            "adds": ["12-month fees paid aggregate cap", "Carve-outs for confidentiality and data breach", "Mutual balanced liability"],
        },
    }

    def __init__(self, benchmark_matcher: Optional[BenchmarkMatcher] = None):
        self.benchmark_matcher = benchmark_matcher or BenchmarkMatcher()

    def generate_diff_html(self, original_text: str, replacement_text: str) -> str:
        """
        Produces a rich HTML diff with <del> (red strike) and <ins> (green highlight) tags.
        """
        orig_words = original_text.split()
        repl_words = replacement_text.split()

        matcher = difflib.SequenceMatcher(None, orig_words, repl_words)
        html_chunks = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                chunk = " ".join(orig_words[i1:i2])
                html_chunks.append(html.escape(chunk))
            elif tag == "delete":
                deleted = " ".join(orig_words[i1:i2])
                html_chunks.append(f'<del class="redline-del">{html.escape(deleted)}</del>')
            elif tag == "insert":
                inserted = " ".join(repl_words[j1:j2])
                html_chunks.append(f'<ins class="redline-ins">{html.escape(inserted)}</ins>')
            elif tag == "replace":
                deleted = " ".join(orig_words[i1:i2])
                inserted = " ".join(repl_words[j1:j2])
                html_chunks.append(f'<del class="redline-del">{html.escape(deleted)}</del> <ins class="redline-ins">{html.escape(inserted)}</ins>')

        return " ".join(html_chunks)

    def generate_redline(self, trap: TrapMatch, clause: ContractClause) -> RedlineResult:
        """Generates a complete balanced redline result for a detected trap."""
        template_info = self.BALANCED_TEMPLATES.get(
            trap.category,
            {
                "template": "The parties agree to mutually fair terms in accordance with standard commercial practice.",
                "rationale": "Eliminates one-sided risks in this section.",
                "negotiation": "State: 'We require mutual and balanced terms for this clause.'",
                "strikes": ["unilateral terms"],
                "adds": ["mutual fair provisions"],
            },
        )

        replacement_text = template_info["template"]
        rationale = template_info["rationale"]
        negotiation = template_info["negotiation"]

        # Context-aware concise termination replacement
        if trap.category == TrapCategory.UNILATERAL_MODIFICATION and re.search(r"\b(?:terminate|cancellation|shut\s+down)\b", clause.text, re.I):
            replacement_text = "Either party may terminate this Agreement at any time by providing at least thirty (30) calendar days' prior written notice to the other party."
            rationale = "Replaces unilateral termination with reciprocal 30-day advance written notice."
            negotiation = "State: 'We require bilateral termination rights with standard 30-day prior written notice.'"
        elif trap.category == TrapCategory.ASYMMETRIC_INDEMNIFICATION and re.search(r"\b(?:liable\s+for\s+all\s+losses|without\s+limitation|unlimited\s+liability)\b", clause.text, re.I):
            replacement_text = "Except for gross negligence or willful misconduct, neither party's total aggregate liability arising under this Agreement shall exceed the total fees paid by Customer in the twelve (12) months preceding the claim."
            rationale = "Replaces uncapped customer liability with a balanced mutual aggregate liability cap equal to 12 months of fees."
            negotiation = "State: 'We cannot accept uncapped liability; customer liability must be capped at 12 months fees paid in accordance with standard commercial practice.'"

        diff_html = self.generate_diff_html(clause.text, replacement_text)

        redline_id = f"redline_{trap.trap_id}"

        return RedlineResult(
            redline_id=redline_id,
            clause_id=clause.clause_id,
            clause_title=clause.title,
            trap_category=trap.category.value,
            severity=trap.severity.value,
            original_text=clause.text,
            recommended_text=replacement_text,
            diff_html=diff_html,
            strike_through_summary=template_info["strikes"],
            additions_summary=template_info["adds"],
            legal_rationale=rationale,
            negotiation_talking_point=negotiation,
        )
