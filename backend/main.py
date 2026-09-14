"""
LexiTrap FastAPI Application.
Academic NLP & Machine Learning Engine for Legal Contract Risk & Trap-Clause Auditing.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import io

from app.nlp.preprocessing import run_nlp_pipeline
from app.nlp.clause_segmentation import segment_contract_into_clauses, LEGAL_CATEGORIES
from app.nlp.tfidf_engine import analyze_corpus_tfidf
from app.ml.classifier import ml_engine
from app.nlp.risk_detector import calculate_transparent_risk_score, audit_clause_complete, audit_contract_document
from app.nlp.semantic_engine import compare_two_clauses, find_similar_clauses, compute_pairwise_similarity_matrix
from app.reporting.report_generator import generate_markdown_report, generate_pdf_report
from app.document_processing.pdf_extractor import extract_text_from_pdf
from app.document_processing.docx_extractor import extract_text_from_docx

app = FastAPI(
    title="LexiTrap NLP Engine",
    description="Academic Natural Language Processing & Contract Risk Analysis API",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
@app.get("/analyze", response_class=HTMLResponse)
@app.get("/results", response_class=HTMLResponse)
@app.get("/nlp-analysis", response_class=HTMLResponse)
@app.get("/history", response_class=HTMLResponse)
def serve_frontend():
    """Serves the single-page React frontend."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>LexiTrap API Online</h1><p>Static frontend not found.</p>")


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw contract text or clause to analyze")


class NLPAnalysisResponse(BaseModel):
    original_text: str
    cleaned_text: str
    statistics: Dict[str, Any]
    sentences: List[str]
    tokens: List[str]
    filtered_tokens: List[str]
    standard_filtered_tokens: List[str]
    removed_stopwords: List[str]
    preserved_legal_keywords: List[str]
    stopword_academic_note: str
    lemmas: List[Dict[str, Any]]
    pos_tags: List[Dict[str, Any]]
    pos_summary: Dict[str, int]
    modal_verbs: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]


class ClauseSegmentationResponse(BaseModel):
    total_clauses: int
    categories_found: List[str]
    available_categories: List[str]
    clauses: List[Dict[str, Any]]


@app.get("/")
def read_root():
    return {
        "project": "LexiTrap",
        "title": "NLP-Based Legal Contract Risk & Trap-Clause Auditor",
        "phase": "Phase 2 - Contract Processing & Clause Segmentation",
        "status": "online",
        "academic_focus": "PDF/DOCX Extraction, Document Layout Normalization, Hierarchical Clause Segmentation"
    }


@app.post("/api/nlp/analyze", response_model=NLPAnalysisResponse)
def analyze_nlp_endpoint(payload: TextAnalysisRequest):
    """
    Core Phase 1 NLP Pipeline Endpoint:
    Processes input text through:
    1. Text Cleaning & Normalization
    2. Sentence Segmentation
    3. Word Tokenization
    4. Legal-Aware Stopword Handling
    5. Morphological Lemmatization
    6. POS Tagging & Modal Verb Detection
    7. Named Entity Recognition (NER)
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    try:
        results = run_nlp_pipeline(payload.text)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP Processing Error: {str(e)}")


@app.post("/api/document/extract")
async def extract_document_endpoint(file: UploadFile = File(...)):
    """
    Phase 2 Document Ingestion Endpoint:
    Accepts PDF, DOCX, or TXT file uploads, extracts readable text, metadata,
    and returns normalized text ready for NLP pipelines.
    """
    filename = file.filename or ""
    content = await file.read()
    
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        
    lower_filename = filename.lower()
    
    try:
        if lower_filename.endswith(".pdf"):
            extraction = extract_text_from_pdf(content)
            extraction["file_name"] = filename
            extraction["file_type"] = "PDF"
            return extraction
            
        elif lower_filename.endswith(".docx"):
            extraction = extract_text_from_docx(content)
            extraction["file_name"] = filename
            extraction["file_type"] = "DOCX"
            return extraction
            
        elif lower_filename.endswith(".txt") or lower_filename.endswith(".md"):
            text = content.decode("utf-8", errors="replace")
            return {
                "text": text,
                "file_name": filename,
                "file_type": "PLAIN_TEXT",
                "page_count": 1,
                "extraction_method": "UTF-8 Decoder"
            }
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format '{filename}'. Please upload a PDF, DOCX, or TXT file."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document Extraction Error: {str(e)}")


@app.post("/api/nlp/segment-clauses", response_model=ClauseSegmentationResponse)
def segment_clauses_endpoint(payload: TextAnalysisRequest):
    """
    Phase 2 Clause Segmentation Endpoint:
    Splits contract text into hierarchical clauses and classifies them into the 16 legal categories.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Contract text cannot be empty.")
        
    try:
        clauses = segment_contract_into_clauses(payload.text)
        categories_found = list(sorted({c["category"] for c in clauses}))
        
        return {
            "total_clauses": len(clauses),
            "categories_found": categories_found,
            "available_categories": LEGAL_CATEGORIES,
            "clauses": clauses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clause Segmentation Error: {str(e)}")


class TFIDFAnalysisRequest(BaseModel):
    clauses: Optional[List[str]] = Field(default=None, description="Optional list of discrete clause strings")
    contract_text: Optional[str] = Field(default=None, description="Raw contract text to segment and analyze")


@app.post("/api/nlp/tfidf/analyze")
def analyze_tfidf_endpoint(payload: TFIDFAnalysisRequest):
    """
    Phase 3 TF-IDF Feature Extraction & Academic Analysis Endpoint:
    Computes manual and scikit-learn TF-IDF matrices, extracts top discriminative keywords,
    and returns step-by-step mathematical tracing with formulas.
    """
    clauses_to_analyze = []
    if payload.clauses and len(payload.clauses) > 0:
        clauses_to_analyze = [c.strip() for c in payload.clauses if c.strip()]
    elif payload.contract_text and payload.contract_text.strip():
        segmented = segment_contract_into_clauses(payload.contract_text)
        clauses_to_analyze = [c["text"] for c in segmented]
    else:
        raise HTTPException(
            status_code=400, 
            detail="Must provide either 'clauses' (list of strings) or 'contract_text' (string)."
        )
        
    try:
        results = analyze_corpus_tfidf(clauses_to_analyze)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TF-IDF Processing Error: {str(e)}")


@app.get("/api/ml/evaluation")
def get_ml_evaluation():
    """
    Phase 4 Machine Learning Evaluation Endpoint:
    Returns the complete academic evaluation comparing Logistic Regression vs Linear SVM,
    including 80/20 train-test metrics, F1-scores, precision, recall, and confusion matrices.
    """
    return ml_engine.evaluation_report


class MLPredictRequest(BaseModel):
    clause_text: str = Field(..., min_length=1, description="Clause text to classify")


@app.post("/api/ml/predict")
def predict_clause_ml(payload: MLPredictRequest):
    """
    Phase 4 ML Prediction Endpoint:
    Classifies a clause using both trained models and returns predicted category, confidence, and agreement.
    """
    if not payload.clause_text or not payload.clause_text.strip():
        raise HTTPException(status_code=400, detail="Clause text cannot be empty.")
        
    try:
        prediction = ml_engine.predict_clause(payload.clause_text)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Prediction Error: {str(e)}")


class ClauseAuditRequest(BaseModel):
    clause_text: str = Field(..., min_length=1, description="Clause text to audit")
    category: Optional[str] = Field(default="Other", description="Optional legal category")


@app.post("/api/nlp/risk/audit-clause")
def audit_clause_endpoint(payload: ClauseAuditRequest):
    """
    Phase 5 Risk Audit Endpoint (Single Clause):
    Extracts linguistic danger indicators, evaluates context symmetry (unilateral vs mutual),
    calculates transparent point-based risk score (0-100), and generates explanation with balanced rewrites.
    """
    if not payload.clause_text or not payload.clause_text.strip():
        raise HTTPException(status_code=400, detail="Clause text cannot be empty.")
        
    try:
        # If category is Other, use ML classifier to infer category
        category = payload.category or "Other"
        if category == "Other":
            pred = ml_engine.predict_clause(payload.clause_text)
            category = pred["predicted_category"]
            
        clause_data = {
            "text": payload.clause_text,
            "category": category
        }
        return audit_clause_complete(clause_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clause Risk Audit Error: {str(e)}")


@app.post("/api/nlp/risk/audit-contract")
def audit_contract_endpoint(payload: TextAnalysisRequest):
    """
    Phase 5 Contract-Wide Risk Audit Endpoint:
    Processes full contract text, segments into clauses, performs ML classification,
    audits all clauses for risk signals, and computes aggregated health metrics.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Contract text cannot be empty.")
        
    try:
        segmented_clauses = segment_contract_into_clauses(payload.text)
        
        # Enrich clauses with ML category predictions
        enriched_clauses = []
        for c in segmented_clauses:
            pred = ml_engine.predict_clause(c["text"])
            c_copy = dict(c)
            c_copy["ml_predicted_category"] = pred["predicted_category"]
            c_copy["ml_confidence"] = pred["confidence_score"]
            # Use ML category if available
            c_copy["category"] = pred["predicted_category"] if pred["confidence_score"] > 0.4 else c["category"]
            enriched_clauses.append(c_copy)
            
        audit_result = audit_contract_document(enriched_clauses)
        return audit_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Contract Audit Error: {str(e)}")


class SemanticCompareRequest(BaseModel):
    clause_a: str = Field(..., min_length=1, description="First clause text")
    clause_b: str = Field(..., min_length=1, description="Second clause text")


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Target clause to find similar matches for")
    candidates: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional candidate clauses list")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Top K matches to return")


class SemanticMatrixRequest(BaseModel):
    clauses: List[str] = Field(..., min_length=2, description="List of at least 2 clauses for pairwise comparison")


@app.post("/api/nlp/semantic/similarity")
def semantic_similarity_endpoint(payload: SemanticCompareRequest):
    """
    Phase 6 Semantic Similarity & Comparative Imbalance Endpoint:
    Computes dense embeddings (Sentence Transformers) and cosine similarity,
    evaluates modality, subject symmetry, and detects contractual imbalances.
    """
    try:
        return compare_two_clauses(payload.clause_a, payload.clause_b)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic Comparison Error: {str(e)}")


@app.post("/api/nlp/semantic/search")
def semantic_search_endpoint(payload: SemanticSearchRequest):
    """
    Phase 6 Semantic Search Endpoint:
    Finds top K most semantically similar clauses from candidates or dataset using dense vector representations.
    """
    try:
        candidates = payload.candidates
        if not candidates:
            # Fall back to dataset sample clauses
            df = ml_engine.load_dataset()
            candidates = df[["text", "category", "risk_level"]].to_dict(orient="records")
            
        similar_matches = find_similar_clauses(payload.query, candidates, top_k=payload.top_k or 5)
        return {
            "query": payload.query,
            "total_matches": len(similar_matches),
            "matches": similar_matches
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic Search Error: {str(e)}")


@app.post("/api/nlp/semantic/matrix")
def semantic_matrix_endpoint(payload: SemanticMatrixRequest):
    """
    Phase 6 Pairwise Semantic Similarity Matrix Endpoint:
    Generates full N x N cosine similarity matrix for heatmap visualization.
    """
    try:
        return compute_pairwise_similarity_matrix(payload.clauses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic Matrix Error: {str(e)}")


from fastapi.responses import Response


class ReportGenerationRequest(BaseModel):
    audit_data: Dict[str, Any] = Field(..., description="Audit output containing summary and clauses")
    nlp_stats: Optional[Dict[str, Any]] = Field(default=None, description="Optional NLP pipeline statistics")


@app.post("/api/analysis/report/markdown")
def download_markdown_report_endpoint(payload: ReportGenerationRequest):
    """
    Phase 8 Markdown Report Download Endpoint:
    Generates a full Markdown audit report.
    """
    try:
        md_content = generate_markdown_report(payload.audit_data, payload.nlp_stats)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=LexiTrap_Audit_Report.md"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown Report Error: {str(e)}")


@app.post("/api/analysis/report/pdf")
def download_pdf_report_endpoint(payload: ReportGenerationRequest):
    """
    Phase 8 PDF Report Download Endpoint:
    Generates a professional PDF audit report using ReportLab.
    """
    try:
        pdf_bytes = generate_pdf_report(payload.audit_data, payload.nlp_stats)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=LexiTrap_Audit_Report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Report Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
