"""
Flask Web Application for Legal Contract Dark Pattern & Trap-Clause Auditor
Provides interactive dashboard, live contract analyzer, photo/PDF document scanner,
risk heatmaps, redline comparison, and report exports.
"""

import os
import io
from flask import Flask, render_template, request, jsonify, Response
from nlp_engine import ContractAuditor
from samples.sample_data import SAMPLE_CONTRACTS, load_sample_text, list_samples

app = Flask(__name__)
auditor = ContractAuditor()


@app.route("/favicon.ico")
def favicon():
    """Serves brand favicon."""
    return Response(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">⚖️</text></svg>',
        mimetype="image/svg+xml"
    )


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


@app.route("/api/upload-file", methods=["POST"])
def upload_file():
    """Extracts text from uploaded PDF or text documents."""
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded."}), 400

    file = request.files["file"]
    filename = file.filename or "Uploaded Document"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    try:
        if ext == "pdf":
            # Extract via pdfplumber or pypdf
            extracted_pages = []
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                    for page in pdf.pages:
                        txt = page.extract_text()
                        if txt:
                            extracted_pages.append(txt)
            except Exception:
                file.seek(0)
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(file.read()))
                for page in reader.pages:
                    txt = page.extract_text()
                    if txt:
                        extracted_pages.append(txt)

            full_text = "\n\n".join(extracted_pages).strip()
            if not full_text:
                return jsonify({"status": "error", "message": "Could not extract text from this PDF."}), 400

            doc_title = filename.rsplit(".", 1)[0].replace("_", " ").title()
            return jsonify({
                "status": "success",
                "title": doc_title,
                "text": full_text,
                "filename": filename
            })

        elif ext in ["txt", "md", "rtf"]:
            content = file.read().decode("utf-8", errors="replace").strip()
            doc_title = filename.rsplit(".", 1)[0].replace("_", " ").title()
            return jsonify({
                "status": "success",
                "title": doc_title,
                "text": content,
                "filename": filename
            })

        else:
            return jsonify({"status": "error", "message": f"Unsupported file type .{ext}. For photos (JPG/PNG), use the in-browser OCR scanner."}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"File parsing error: {str(e)}"}), 500


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

    md = []
    md.append(f"# Legal Contract Audit Report: {report_dict.get('document_name')}\n")
    md.append(f"**Health Score:** {report_dict.get('overall_health_score')}/100 (Grade: **{report_dict.get('letter_grade')}**)")
    md.append(f"**Risk Level:** {report_dict.get('risk_level')}")
    md.append(f"**Verdict:** {report_dict.get('verdict_title')} — {report_dict.get('verdict_description')}\n")

    md.append(f"| Summary Metric | Value |")
    md.append(f"| :--- | :--- |")
    md.append(f"| Total Clauses Analyzed | {report_dict.get('total_clauses')} |")
    md.append(f"| Total Words | {report_dict.get('total_words')} |")
    md.append(f"| Predatory Traps Flagged | {report_dict.get('total_traps_found')} |")
    md.append(f"| Critical Risk Traps | {report_dict.get('critical_traps_count')} |")
    md.append(f"| High Risk Traps | {report_dict.get('high_traps_count')} |\n")

    md.append("## Executive Summary\n")
    for pt in report_dict.get("executive_summary_points", []):
        md.append(f"- {pt}")
    md.append("\n")

    md.append("## Flagged Dangerous Clauses & Redline Recommendations\n")
    for c in report_dict.get("clause_audit_details", []):
        if c.get("has_traps"):
            md.append(f"### {c.get('title')} (Risk Score: {c.get('risk_score')}/100 - {c.get('heat_level')})\n")
            md.append(f"> **Original Predatory Text:**\n> {c.get('text')}\n")
            for t in c.get("traps", []):
                md.append(f"- **Trap Category:** {t.get('category')} ({t.get('severity')})")
                md.append(f"- **Legal Risk:** {t.get('legal_danger')}")
                md.append(f"- **Recommended Mitigation:** {t.get('recommended_mitigation')}\n")

    report_markdown = "\n".join(md)
    filename = f"LexiTrap_Audit_{report_dict.get('document_name', 'Report').replace(' ', '_')}.md"

    return Response(
        report_markdown,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
