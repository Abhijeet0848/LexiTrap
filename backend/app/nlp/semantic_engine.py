"""
Semantic NLP & Clause Embedding Engine for LexiTrap.
Implements:
1. Dense Vector Embeddings using Sentence Transformers (all-MiniLM-L6-v2, 384 dimensions)
2. Mathematical Cosine Similarity Calculation
3. Academic Synonymy Demonstration (paraphrased clause semantic equivalence)
4. Comparative Clause Imbalance Analysis (subject, modality, notice, rights)
5. Semantic Similarity Search & Corpus Pairwise Similarity Matrix
"""

import os
import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from app.nlp.risk_detector import calculate_transparent_risk_score, determine_subject_symmetry
from app.nlp.preprocessing import pos_tag_text

# Singleton container for SentenceTransformer model
_MODEL_INSTANCE: Optional[SentenceTransformer] = None


def get_embedding_model() -> SentenceTransformer:
    """Lazily loads and caches the SentenceTransformer model."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = SentenceTransformer('all-MiniLM-L6-v2')
    return _MODEL_INSTANCE


def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Computes mathematical Cosine Similarity between two real vectors:
    sim(A, B) = (A · B) / (||A||_2 * ||B||_2)
    """
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def encode_texts(texts: List[str]) -> np.ndarray:
    """Converts a list of text strings into 384-dimensional dense embeddings."""
    if not texts:
        return np.array([])
    model = get_embedding_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


def compare_two_clauses(clause_a: str, clause_b: str) -> Dict[str, Any]:
    """
    Academic Comparative Analysis (Steps 16 & 17):
    Compares two clauses across:
    1. Semantic Cosine Similarity percentage
    2. Modality & Modal Verbs (shall, may, must)
    3. Subject Symmetry (Mutual vs. Unilateral)
    4. Notice Requirements
    5. Risk Score Delta & Imbalance Alert
    """
    embeddings = encode_texts([clause_a, clause_b])
    cos_sim = compute_cosine_similarity(embeddings[0], embeddings[1])
    sim_percent = round(max(0.0, min(1.0, cos_sim)) * 100, 2)

    # Risk and symmetry analysis
    risk_a = calculate_transparent_risk_score(clause_a)
    risk_b = calculate_transparent_risk_score(clause_b)
    
    pos_a = pos_tag_text(clause_a)
    pos_b = pos_tag_text(clause_b)
    
    modals_a = [m["token"].lower() for m in pos_a["modal_verbs"]]
    modals_b = [m["token"].lower() for m in pos_b["modal_verbs"]]

    # Detect contractual differences
    imbalance_notes = []
    if risk_a["symmetry"] != risk_b["symmetry"]:
        imbalance_notes.append(
            f"Subject Symmetry Shift: Clause A is {risk_a['symmetry']} whereas Clause B is {risk_b['symmetry']}."
        )
    
    risk_delta = abs(risk_a["risk_score"] - risk_b["risk_score"])
    if risk_delta >= 25:
        riskier = "Clause A" if risk_a["risk_score"] > risk_b["risk_score"] else "Clause B"
        imbalance_notes.append(
            f"Significant Risk Disparity: {riskier} presents a substantially higher risk posture (Score Delta: {risk_delta} pts)."
        )

    # Academic explanation of semantic similarity
    if sim_percent >= 70.0:
        semantic_verdict = "High Semantic Equivalence: Both clauses share core legal meaning despite wording differences."
    elif sim_percent >= 45.0:
        semantic_verdict = "Moderate Semantic Alignment: Clauses share topical domain but differ in specific conditions or remedies."
    else:
        semantic_verdict = "Low Semantic Overlap: Clauses govern distinct subject matters."

    return {
        "clause_a": {
            "text": clause_a,
            "risk_score": risk_a["risk_score"],
            "risk_level": risk_a["risk_level"],
            "symmetry": risk_a["symmetry"],
            "modal_verbs": modals_a
        },
        "clause_b": {
            "text": clause_b,
            "risk_score": risk_b["risk_score"],
            "risk_level": risk_b["risk_level"],
            "symmetry": risk_b["symmetry"],
            "modal_verbs": modals_b
        },
        "semantic_similarity_score": round(cos_sim, 4),
        "semantic_similarity_percentage": sim_percent,
        "semantic_verdict": semantic_verdict,
        "potential_imbalance_detected": len(imbalance_notes) > 0,
        "imbalance_findings": imbalance_notes,
        "academic_note": (
            "Sentence Transformer embeddings map contractual clauses into dense vector space, "
            "allowing the system to detect paraphrased obligations that bag-of-words or keyword matchers miss."
        )
    }


def find_similar_clauses(
    target_clause: str,
    candidate_clauses: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Finds the top K most semantically similar clauses from a candidate list using dense embeddings.
    """
    if not candidate_clauses or not target_clause:
        return []

    candidate_texts = [c.get("text", "") for c in candidate_clauses]
    all_texts = [target_clause] + candidate_texts
    
    embeddings = encode_texts(all_texts)
    target_vec = embeddings[0]
    candidate_vecs = embeddings[1:]

    scored_candidates = []
    for idx, cand_vec in enumerate(candidate_vecs):
        sim = compute_cosine_similarity(target_vec, cand_vec)
        cand_data = dict(candidate_clauses[idx])
        cand_data["similarity_score"] = round(sim, 4)
        cand_data["similarity_percentage"] = round(max(0.0, min(1.0, sim)) * 100, 2)
        scored_candidates.append(cand_data)

    # Sort descending by similarity score
    scored_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_candidates[:top_k]


def compute_pairwise_similarity_matrix(clauses: List[str]) -> Dict[str, Any]:
    """
    Computes complete N x N cosine similarity matrix across a list of clauses.
    """
    if not clauses:
        return {"matrix": [], "labels": []}

    embeddings = encode_texts(clauses)
    num_clauses = len(clauses)
    matrix = np.zeros((num_clauses, num_clauses))

    for i in range(num_clauses):
        for j in range(num_clauses):
            matrix[i, j] = compute_cosine_similarity(embeddings[i], embeddings[j])

    labels = [f"Clause {i+1}: {clauses[i][:40]}..." for i in range(num_clauses)]

    return {
        "num_clauses": num_clauses,
        "labels": labels,
        "matrix": [[round(float(val), 4) for val in row] for row in matrix]
    }
