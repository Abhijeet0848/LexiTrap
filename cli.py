"""
Interactive Command-Line Interface for Legal Contract Auditor
Run audits, view risk heatmaps, inspect deontic breakdown, and generate redlines from terminal.
"""

import argparse
import sys
import os
from typing import Optional

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = RESET = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""

from nlp_engine import ContractAuditor, AuditReport
from samples.sample_data import SAMPLE_CONTRACTS, load_sample_text, list_samples


def print_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}========================================================================
 ⚖️  LEGAL CONTRACT "DARK PATTERN" & TRAP-CLAUSE AUDITOR (NLP ENGINE)
     Cognitive Legal NLP • Deontic Logic • Benchmark Deviation • Redlines
========================================================================{Style.RESET_ALL}
"""
    print(banner)


def format_severity_badge(severity: str) -> str:
    if severity == "CRITICAL":
        return f"{Back.RED}{Fore.WHITE}{Style.BRIGHT} CRITICAL {Style.RESET_ALL}"
    elif severity == "HIGH":
        return f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT} HIGH RISK {Style.RESET_ALL}"
    elif severity == "MEDIUM":
        return f"{Fore.YELLOW}{Style.BRIGHT}[MEDIUM]{Style.RESET_ALL}"
    elif severity == "LOW":
        return f"{Fore.CYAN}[LOW]{Style.RESET_ALL}"
    else:
        return f"{Fore.GREEN}[SAFE]{Style.RESET_ALL}"


def print_audit_report(report: AuditReport, show_redlines: bool = True):
    print(f"\n{Fore.WHITE}{Style.BRIGHT}📄 DOCUMENT AUDITED:{Style.RESET_ALL} {Fore.CYAN}{report.document_name}")
    print(f"{Fore.WHITE}Clauses Analyzed:{Style.RESET_ALL} {report.total_clauses}  |  "
          f"{Fore.WHITE}Words:{Style.RESET_ALL} {report.total_words}  |  "
          f"{Fore.WHITE}Sentences:{Style.RESET_ALL} {report.total_sentences}")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}------------------------------------------------------------------------")
    print(f" 📊 OVERALL CONTRACT HEALTH & RISK VERDICT")
    print(f"------------------------------------------------------------------------{Style.RESET_ALL}")

    grade_color = Fore.GREEN if report.letter_grade.startswith("A") else (Fore.YELLOW if report.letter_grade in ["B", "C"] else Fore.RED)
    print(f"  Health Score: {grade_color}{Style.BRIGHT}{report.overall_health_score}/100{Style.RESET_ALL}  (Grade: {grade_color}{Style.BRIGHT}{report.letter_grade}{Style.RESET_ALL})")
    print(f"  Risk Level:   {format_severity_badge(report.risk_level)}")
    print(f"  Verdict:      {Fore.WHITE}{Style.BRIGHT}{report.verdict_title}{Style.RESET_ALL}")
    print(f"  Description:  {Fore.WHITE}{report.verdict_description}{Style.RESET_ALL}")

    print(f"\n{Fore.WHITE}{Style.BRIGHT}  Traps Breakdown:{Style.RESET_ALL} Total: {report.total_traps_found} | "
          f"{Fore.RED}Critical: {report.critical_traps_count}{Style.RESET_ALL} | "
          f"{Fore.YELLOW}High: {report.high_traps_count}{Style.RESET_ALL} | "
          f"{Fore.CYAN}Medium: {report.medium_traps_count}{Style.RESET_ALL}")

    # Executive Summary Points
    print(f"\n{Fore.WHITE}{Style.BRIGHT}🔍 EXECUTIVE FINDINGS:{Style.RESET_ALL}")
    for pt in report.executive_summary_points:
        print(f"  • {pt}")

    # Deontic Logic Distribution
    print(f"\n{Fore.WHITE}{Style.BRIGHT}------------------------------------------------------------------------")
    print(f" ⚖️  DEONTIC LOGIC MODALITY PROFILE")
    print(f"------------------------------------------------------------------------{Style.RESET_ALL}")
    for cat, pct in report.deontic_profile.get("distribution_percentages", {}).items():
        bar_len = int(pct / 4)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        print(f"  {cat:<28} : [{Fore.CYAN}{bar}{Style.RESET_ALL}] {pct:>5.1f}%")

    # Clause-Level Risk Heatmap
    print(f"\n{Fore.WHITE}{Style.BRIGHT}------------------------------------------------------------------------")
    print(f" 🌡️  CLAUSE-LEVEL RISK HEATMAP & TRAP AUDIT")
    print(f"------------------------------------------------------------------------{Style.RESET_ALL}")

    for clause in report.clause_audit_details:
        badge = format_severity_badge(clause["heat_level"])
        deontic_dom = clause["deontic_profile"]["dominant_category"]
        print(f"\n[{clause['clause_id']}] {Fore.WHITE}{Style.BRIGHT}{clause['title']}{Style.RESET_ALL} (Risk: {clause['risk_score']}/100) {badge}")
        print(f"  {Fore.MAGENTA}Modal Stance:{Style.RESET_ALL} {deontic_dom} | {clause['word_count']} words")
        
        if clause["traps"]:
            for t in clause["traps"]:
                print(f"  {Fore.RED}⚠️  TRAP DETECTED:{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{t['category']}{Style.RESET_ALL}")
                print(f"     {Fore.YELLOW}Danger:{Style.RESET_ALL} {t['legal_danger']}")
                print(f"     {Fore.CYAN}Triggers:{Style.RESET_ALL} {', '.join(t['matched_patterns'][:2])}")
                
                # Benchmark Deviation
                bm = t.get("benchmark_comparison", {})
                if bm:
                    print(f"     {Fore.MAGENTA}Benchmark Deviation:{Style.RESET_ALL} {bm.get('deviation_level')} (Score: {bm.get('deviation_score')})")
        else:
            print(f"  {Fore.GREEN}✓ No predatory traps detected in this clause.{Style.RESET_ALL}")

    # Redlines
    if show_redlines and report.redlines:
        print(f"\n{Fore.WHITE}{Style.BRIGHT}========================================================================")
        print(f" ✏️  AUTOMATED BALANCED REDLINE RECOMMENDATIONS")
        print(f"========================================================================{Style.RESET_ALL}")

        for idx, rl in enumerate(report.redlines, 1):
            print(f"\n{Fore.CYAN}[REDLINE #{idx}] {rl['clause_title']} - {rl['trap_category']}{Style.RESET_ALL}")
            print(f"{Fore.RED}ORIGINAL PREDATORY TEXT:{Style.RESET_ALL}\n  {rl['original_text']}")
            print(f"\n{Fore.GREEN}BALANCED REPLACEMENT TEXT:{Style.RESET_ALL}\n  {rl['recommended_text']}")
            print(f"\n{Fore.YELLOW}Legal Rationale:{Style.RESET_ALL} {rl['legal_rationale']}")
            print(f"{Fore.MAGENTA}Negotiation Talking Point:{Style.RESET_ALL} {rl['negotiation_talking_point']}")
            print(f"{Fore.WHITE}------------------------------------------------------------------------{Style.RESET_ALL}")


def export_markdown_report(report: AuditReport, output_filepath: str):
    """Exports audit findings to a clean GitHub-flavored markdown report."""
    md = []
    md.append(f"# Legal Contract Audit Report: {report.document_name}\n")
    md.append(f"**Audit Health Score:** {report.overall_health_score}/100 (Grade: **{report.letter_grade}**)")
    md.append(f"**Verdict:** {report.verdict_title} - {report.verdict_description}\n")
    md.append(f"| Metric | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| Total Clauses | {report.total_clauses} |")
    md.append(f"| Total Words | {report.total_words} |")
    md.append(f"| Traps Detected | {report.total_traps_found} (Critical: {report.critical_traps_count}, High: {report.high_traps_count}) |")
    md.append(f"| Risk Level | {report.risk_level} |\n")

    md.append("## Executive Findings\n")
    for pt in report.executive_summary_points:
        md.append(f"- {pt}")
    md.append("\n")

    md.append("## Clause-Level Risk Heatmap\n")
    for clause in report.clause_audit_details:
        md.append(f"### {clause['clause_id']}: {clause['title']} (Risk: {clause['risk_score']}/100 - {clause['heat_level']})")
        md.append(f"**Deontic Category:** {clause['deontic_profile']['dominant_category']}")
        md.append(f"\n> {clause['text']}\n")
        if clause["traps"]:
            for t in clause["traps"]:
                md.append(f"- **Trap:** {t['category']} ({t['severity']})")
                md.append(f"- **Legal Danger:** {t['legal_danger']}")
                md.append(f"- **Mitigation:** {t['recommended_mitigation']}\n")

    if report.redlines:
        md.append("## Recommended Balanced Redlines\n")
        for rl in report.redlines:
            md.append(f"### Redline for: {rl['clause_title']} ({rl['trap_category']})")
            md.append(f"**Original Clause:**\n```text\n{rl['original_text']}\n```")
            md.append(f"**Balanced Proposed Alternative:**\n```text\n{rl['recommended_text']}\n```")
            md.append(f"**Rationale:** {rl['legal_rationale']}\n")

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"\n{Fore.GREEN}✓ Markdown report successfully saved to: {output_filepath}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="Legal Contract Dark Pattern & Trap-Clause Auditor")
    parser.add_argument("--sample", type=str, help="ID of sample contract to audit (e.g. predatory_saas_tos, unbalanced_nda)")
    parser.add_argument("--file", type=str, help="Path to contract file (.txt / .md)")
    parser.add_argument("--list-samples", action="store_true", help="List all available built-in sample contracts")
    parser.add_argument("--no-redlines", action="store_true", help="Omit redlines in terminal output")
    parser.add_argument("--export", type=str, help="Path to export markdown audit report")

    args = parser.parse_args()
    print_banner()

    if args.list_samples:
        print(f"{Fore.WHITE}{Style.BRIGHT}Available Sample Contracts:{Style.RESET_ALL}\n")
        for s in list_samples():
            print(f"  • {Fore.CYAN}{s['id']:<30}{Style.RESET_ALL} [{s['type']}] ({s['expected_risk']})")
            print(f"    {s['description']}\n")
        return

    text = ""
    doc_name = "Custom Contract"

    if args.sample:
        if args.sample not in SAMPLE_CONTRACTS:
            print(f"{Fore.RED}Error: Unknown sample ID '{args.sample}'. Use --list-samples to see options.{Style.RESET_ALL}")
            sys.exit(1)
        text = load_sample_text(args.sample)
        doc_name = SAMPLE_CONTRACTS[args.sample]["name"]
    elif args.file:
        if not os.path.exists(args.file):
            print(f"{Fore.RED}Error: File not found: {args.file}{Style.RESET_ALL}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        doc_name = os.path.basename(args.file)
    else:
        # Default to predatory_saas_tos sample if no arguments provided
        print(f"{Fore.YELLOW}No contract specified. Defaulting to built-in sample: 'predatory_saas_tos'{Style.RESET_ALL}")
        print(f"Run with --help or --list-samples for more options.\n")
        text = load_sample_text("predatory_saas_tos")
        doc_name = SAMPLE_CONTRACTS["predatory_saas_tos"]["name"]

    auditor = ContractAuditor()
    print(f"{Fore.CYAN}Auditing contract with NLP engine...{Style.RESET_ALL}")
    report = auditor.audit(text, document_name=doc_name)

    print_audit_report(report, show_redlines=not args.no_redlines)

    if args.export:
        export_markdown_report(report, args.export)


if __name__ == "__main__":
    main()
