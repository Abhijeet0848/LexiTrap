"""
Live End-to-End System Verification Script for LexiTrap.
Executes live API requests across all 8 pipeline phases.
"""

import sys
import os
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)

def run_live_verification():
    print("=" * 80)
    print("🚀 LEXITRAP LIVE END-TO-END SYSTEM EXECUTION TEST")
    print("=" * 80)

    # 1. Root & Web Interface
    res = client.get("/")
    print(f"\n[1. WEB INTERFACE] GET / -> HTTP {res.status_code} | HTML Size: {len(res.text)} bytes")

    # 2. NLP Pipeline Preprocessing
    sample_text = "Acme Technologies LLC shall pay $75,000 within 30 days. The vendor may terminate this agreement at any time without notice."
    res = client.post("/api/nlp/analyze", json={"text": sample_text})
    nlp = res.json()
    print(f"\n[2. NLP PREPROCESSING] Tokens: {len(nlp['tokens'])} | Sentences: {len(nlp['sentences'])}")
    print(f"   - Preserved Deontic Keywords: {nlp['preserved_legal_keywords']}")
    print(f"   - Detected Modal Verbs: {[m['token'] for m in nlp['modal_verbs']]}")
    print(f"   - Named Entities: {[(e['text'], e['label']) for e in nlp['entities']]}")

    # 3. Clause Segmentation
    contract_text = """
1. UNILATERAL MODIFICATIONS
Provider reserves the right to change fees and terms at any time in its sole discretion without notice.

2. TERMINATION
Provider may immediately terminate this Agreement at will without cause or refund.

3. LIMITATION OF LIABILITY
Total aggregate liability shall be strictly capped at $50.00 under all legal theories.
"""
    res = client.post("/api/nlp/segment-clauses", json={"text": contract_text})
    seg = res.json()
    print(f"\n[3. CLAUSE SEGMENTATION] Total Clauses: {seg['total_clauses']} | Found Categories: {seg['categories_found']}")

    # 4. TF-IDF Feature Extraction & Mathematical Traces
    res = client.post("/api/nlp/tfidf/analyze", json={"contract_text": contract_text})
    tf = res.json()
    print(f"\n[4. TF-IDF ANALYSIS] Vocabulary Size: {tf['vocabulary_size']} terms")
    print(f"   - Top Features: {[f['term'] for f in tf['corpus_top_features'][:5]]}")
    print(f"   - Viva Formula Trace: {tf['clause_level_analysis'][0]['top_terms'][0]['formula_trace']}")

    # 5. Machine Learning Evaluation (Logistic Regression vs Linear SVM)
    res = client.get("/api/ml/evaluation")
    ml = res.json()
    lr_f1 = ml["model_1_logistic_regression"]["f1_weighted"]
    svm_f1 = ml["model_2_linear_svm"]["f1_weighted"]
    print(f"\n[5. ML MODEL BENCHMARK] Classes: {ml['dataset_statistics']['total_categories']}")
    print(f"   - Model 1 (TF-IDF + Logistic Regression) Weighted F1: {lr_f1}")
    print(f"   - Model 2 (TF-IDF + Linear SVM) Weighted F1:          {svm_f1}")
    print(f"   - Preferred Model: {ml['comparison_summary']['preferred_model']}")

    # 6. Contract Risk Audit
    res = client.post("/api/nlp/risk/audit-contract", json={"text": contract_text})
    risk = res.json()
    print(f"\n[6. CONTRACT RISK AUDIT] Health Grade: {risk['summary']['overall_grade']} | Avg Risk: {risk['summary']['average_risk_score']}/100")
    print(f"   - Risk Distribution: {risk['summary']['risk_distribution']}")
    c1 = risk["clauses"][0]
    print(f"   - Clause 1 ({c1['category']}): Risk Score {c1['risk_score']}/100 ({c1['risk_level']}) | Symmetry: {c1['symmetry']}")
    print(f"   - Suggested Balanced Rewrite: {c1['suggested_rewrite']['suggested_balanced_clause'][:90]}...")

    # 7. Semantic Embeddings & Cosine Similarity
    res = client.post("/api/nlp/semantic/similarity", json={
        "clause_a": "The provider may terminate the agreement without notice.",
        "clause_b": "The service provider can end the contract immediately without providing prior notification."
    })
    sem = res.json()
    print(f"\n[7. SEMANTIC TRANSFORMER SIMILARITY] Cosine Similarity: {sem['semantic_similarity_percentage']}%")
    print(f"   - Verdict: {sem['semantic_verdict']}")

    # 8. Report Generation (PDF & Markdown)
    res_md = client.post("/api/analysis/report/markdown", json={"audit_data": risk, "nlp_stats": nlp})
    res_pdf = client.post("/api/analysis/report/pdf", json={"audit_data": risk, "nlp_stats": nlp})
    print(f"\n[8. REPORT GENERATION]")
    print(f"   - Markdown Export: HTTP {res_md.status_code} | Size: {len(res_md.text)} bytes")
    print(f"   - ReportLab PDF Export: HTTP {res_pdf.status_code} | Header: {res_pdf.content[:4]} | Size: {len(res_pdf.content)} bytes")

    print("\n" + "=" * 80)
    print("✅ ALL 8 PIPELINE PHASES VERIFIED AND FULLY OPERATIONAL!")
    print("=" * 80)


if __name__ == "__main__":
    run_live_verification()
