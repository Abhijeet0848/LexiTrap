"""
Flask Web Application for Legal Contract Dark Pattern & Trap-Clause Auditor
Provides interactive dashboard, live contract analyzer, risk heatmaps, redline comparison, and report exports.
"""

import os
from flask import Flask, render_template, request, jsonify, Response
from nlp_engine import ContractAuditor
from samples.sample_data import SAMPLE_CONTRACTS, load_sample_text, list_samples

app = Flask(__name__)
auditor = ContractAuditor()


@app.route("/")
def index():
    """Renders the main contract audit dashboard."""
    samples = list_samples()
    return render_template("index.html", samples=samples)


@app.route("/api/samples", methods=["GET"])
def get_samples():
    """Returns list of built-in sample contracts."""
    return jsonify({
        "status": "success",
        "samples": list_samples()
    })


@app.route("/api/sample/<sample_id>", methods=["GET"])
def get_sample_content(sample_id):
    """Fetches text of a specified sample contract."""
    if sample_id not in SAMPLE_CONTRACTS:
        return jsonify({"status": "error", "message": f"Sample '{sample_id}' not found"}), 404
    
    meta = SAMPLE_CONTRACTS[sample_id]
    text = load_sample_text(sample_id)
    return jsonify({
        "status": "success",
        "sample": meta,
        "text": text,
    })


@app.route("/api/fetch-url", methods=["POST"])
def fetch_url():
    """Fetches and extracts clean text from a live Terms of Service URL."""
    import urllib.request
    import re
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.ignore_tags = {"script", "style", "nav", "footer", "header", "noscript", "svg"}
            self.current_tag = None

        def handle_starttag(self, tag, attrs):
            self.current_tag = tag.lower()

        def handle_endtag(self, tag):
            self.current_tag = None
            if tag.lower() in {"p", "div", "h1", "h2", "h3", "h4", "li", "section", "article"}:
                self.text_parts.append("\n")

        def handle_data(self, data):
            if self.current_tag not in self.ignore_tags:
                clean = data.strip()
                if clean:
                    self.text_parts.append(clean + " ")

        def get_text(self):
            raw = "".join(self.text_parts)
            return re.sub(r"\n{3,}", "\n\n", raw).strip()

    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"status": "error", "message": "URL cannot be empty."}), 400

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            html_content = response.read().decode("utf-8", errors="replace")

        extractor = TextExtractor()
        extractor.feed(html_content)
        extracted_text = extractor.get_text()

        if len(extracted_text) < 50:
            return jsonify({"status": "error", "message": "Could not extract sufficient text from this URL."}), 400

        # Extract page title from URL or domain
        from urllib.parse import urlparse
        parsed = urlparse(url)
        doc_title = f"{parsed.netloc} Terms of Service"

        return jsonify({
            "status": "success",
            "title": doc_title,
            "text": extracted_text,
            "url": url,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch URL: {str(e)}"}), 500


@app.route("/api/audit", methods=["POST"])
def audit_contract():
    """Performs full NLP audit on submitted contract text."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    name = data.get("name", "Submitted Contract").strip() or "Submitted Contract"

    if not text:
        return jsonify({"status": "error", "message": "Contract text cannot be empty."}), 400

    report = auditor.audit(text, document_name=name)
    return jsonify({
        "status": "success",
        "report": report.to_dict(),
    })


@app.route("/api/export", methods=["POST"])
def export_report():
    """Generates an exportable Markdown audit summary report."""
    data = request.get_json(silent=True) or {}
    report_dict = data.get("report")
    if not report_dict:
        return jsonify({"status": "error", "message": "Missing audit report data."}), 400

    # Build markdown
    md = []
    md.append(f"# Legal Contract Audit Report: {report_dict.get('document_name')}\n")
    md.append(f"**Health Score:** {report_dict.get('overall_health_score')}/100 (Grade: **{report_dict.get('letter_grade')}**)")
    md.append(f"**Risk Level:** {report_dict.get('risk_level')}")
    md.append(f"**Verdict:** {report_dict.get('verdict_title')} — {report_dict.get('verdict_description')}\n")

    md.append(f"| Summary Metric | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| Clauses Audited | {report_dict.get('total_clauses')} |")
    md.append(f"| Word Count | {report_dict.get('total_words')} |")
    md.append(f"| Total Traps Detected | {report_dict.get('total_traps_found')} |")
    md.append(f"| Critical Traps | {report_dict.get('critical_traps_count')} |")
    md.append(f"| High Risk Traps | {report_dict.get('high_traps_count')} |\n")

    md.append("## Executive Summary\n")
    for pt in report_dict.get("executive_summary_points", []):
        md.append(f"- {pt}")
    md.append("\n")

    md.append("## Clause-Level Risk Breakdown\n")
    for clause in report_dict.get("clause_audit_details", []):
        md.append(f"### {clause.get('clause_id')}: {clause.get('title')} (Risk Score: {clause.get('risk_score')}/100 - {clause.get('heat_level')})")
        md.append(f"**Dominant Modality:** {clause.get('deontic_profile', {}).get('dominant_category')}\n")
        md.append(f"> {clause.get('text')}\n")
        
        for t in clause.get("traps", []):
            md.append(f"- **Trap Type:** {t.get('category')} ({t.get('severity')})")
            md.append(f"- **Legal Risk:** {t.get('legal_danger')}")
            md.append(f"- **Business Impact:** {t.get('business_impact')}")
            md.append(f"- **Recommended Mitigation:** {t.get('recommended_mitigation')}\n")

    redlines = report_dict.get("redlines", [])
    if redlines:
        md.append("## Recommended Balanced Redlines\n")
        for rl in redlines:
            md.append(f"### {rl.get('clause_title')} — {rl.get('trap_category')}")
            md.append(f"**Original Predatory Text:**\n```text\n{rl.get('original_text')}\n```")
            md.append(f"**Balanced Alternative:**\n```text\n{rl.get('recommended_text')}\n```")
            md.append(f"**Negotiation Talking Point:** {rl.get('negotiation_talking_point')}\n")

    content = "\n".join(md)
    return Response(
        content,
        mimetype="text/markdown",
        headers={"Content-disposition": "attachment; filename=contract_audit_report.md"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
