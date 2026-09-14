"""
TF-IDF Feature Extraction & Academic Analysis Engine for LexiTrap.
Implements:
1. Pure Mathematical / Manual TF-IDF Engine (for academic explanation & step-by-step viva tracing)
2. Scikit-Learn TfidfVectorizer (for production feature extraction & classification pipelines)
3. Keyword Importance & Top-N Distinctive Term Extractor
4. Academic Formula Breakdown & Theoretical Limitations
"""

import math
import re
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from app.nlp.preprocessing import tokenize_text, handle_stopwords


class ManualTFIDF:
    """
    Pure Python Academic Implementation of Term Frequency - Inverse Document Frequency (TF-IDF).
    
    Academic Formulas:
    ------------------
    1. Term Frequency (TF):
       TF(t, d) = (Count of term t in document d) / (Total terms in document d)
       Measures how frequently a word occurs in a specific clause.

    2. Inverse Document Frequency (IDF):
       IDF(t, D) = ln((1 + |D|) / (1 + DF(t))) + 1
       Where |D| is the total number of documents in corpus, and DF(t) is the count
       of documents containing term t.
       Measures how rare or informative a word is across all clauses.

    3. TF-IDF Score:
       TF-IDF(t, d, D) = TF(t, d) * IDF(t, D)
       High score = word is frequent in this clause, but rare across the entire contract.
    """

    def __init__(self, use_legal_stopwords: bool = True):
        self.use_legal_stopwords = use_legal_stopwords
        self.vocabulary: List[str] = []
        self.idf_scores: Dict[str, float] = {}
        self.corpus_size: int = 0

    def _preprocess_document(self, text: str) -> List[str]:
        """Tokenizes and filters document terms."""
        raw_tokens = tokenize_text(text)
        filtered = handle_stopwords(raw_tokens, preserve_legal_keywords=self.use_legal_stopwords)
        tokens = [t.lower() for t in filtered["legal_aware_filtered_tokens"] if t.isalnum()]
        return tokens

    def fit(self, documents: List[str]) -> "ManualTFIDF":
        """Fits vocabulary and computes IDF values across document collection."""
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return self

        doc_tokens_list = [self._preprocess_document(doc) for doc in documents]
        
        # Build distinct vocabulary
        unique_vocab = set()
        for doc_tokens in doc_tokens_list:
            unique_vocab.update(doc_tokens)
        self.vocabulary = sorted(list(unique_vocab))

        # Compute Document Frequency (DF) for each term
        df_counts: Dict[str, int] = {term: 0 for term in self.vocabulary}
        for doc_tokens in doc_tokens_list:
            doc_unique = set(doc_tokens)
            for term in doc_unique:
                if term in df_counts:
                    df_counts[term] += 1

        # Compute Smooth IDF: ln((1 + N) / (1 + DF)) + 1
        self.idf_scores = {}
        for term, df in df_counts.items():
            idf = math.log((1.0 + self.corpus_size) / (1.0 + df)) + 1.0
            self.idf_scores[term] = idf

        return self

    def transform_single(self, text: str) -> Dict[str, Any]:
        """
        Transforms a single document into TF-IDF scores with full mathematical tracing.
        """
        tokens = self._preprocess_document(text)
        total_tokens = len(tokens)
        if total_tokens == 0:
            return {"term_scores": [], "vector": []}

        # 1. Compute term counts (TF numerator)
        term_counts: Dict[str, int] = {}
        for t in tokens:
            term_counts[t] = term_counts.get(t, 0) + 1

        term_analysis = []
        vector = []

        for term in self.vocabulary:
            count = term_counts.get(term, 0)
            tf = count / total_tokens
            idf = self.idf_scores.get(term, math.log((1.0 + self.corpus_size) / 1.0) + 1.0)
            tfidf = tf * idf
            vector.append(tfidf)

            if count > 0:
                term_analysis.append({
                    "term": term,
                    "term_count": count,
                    "total_doc_words": total_tokens,
                    "tf": round(tf, 4),
                    "idf": round(idf, 4),
                    "tfidf": round(tfidf, 4),
                    "formula_trace": f"TF({count}/{total_tokens}={tf:.3f}) * IDF({idf:.3f}) = {tfidf:.4f}"
                })

        # Sort terms by highest TF-IDF score
        term_analysis.sort(key=lambda x: x["tfidf"], reverse=True)

        # Compute Euclidean (L2) normalized vector
        l2_norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        normalized_vector = [round(v / l2_norm, 4) for v in vector]

        return {
            "term_scores": term_analysis,
            "raw_vector": [round(v, 4) for v in vector],
            "l2_normalized_vector": normalized_vector,
            "top_terms": [t["term"] for t in term_analysis[:10]]
        }


class SklearnTFIDFEngine:
    """
    Production Scikit-Learn TF-IDF Feature Extractor.
    Extracts unigram & bigram features with sublinear term-frequency scaling.
    """

    def __init__(self, max_features: int = 500, ngram_range: Tuple[int, int] = (1, 2)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=True,
            stop_words='english'
        )
        self.is_fitted = False

    def fit_transform(self, documents: List[str]) -> Tuple[np.ndarray, List[str]]:
        """Fits vectorizer and returns TF-IDF matrix and feature vocabulary."""
        if not documents:
            return np.array([]), []
            
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        self.is_fitted = True
        feature_names = self.vectorizer.get_feature_names_out().tolist()
        return tfidf_matrix.toarray(), feature_names

    def get_top_terms_for_document(self, text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Extracts top K highest scoring TF-IDF terms for a given text."""
        if not self.is_fitted:
            return []
            
        vec = self.vectorizer.transform([text]).toarray()[0]
        feature_names = self.vectorizer.get_feature_names_out()
        
        top_indices = np.argsort(vec)[::-1][:top_k]
        top_terms = []
        for idx in top_indices:
            score = float(vec[idx])
            if score > 0.0:
                top_terms.append({
                    "term": feature_names[idx],
                    "score": round(score, 4)
                })
        return top_terms


def analyze_corpus_tfidf(clauses_text: List[str]) -> Dict[str, Any]:
    """
    Performs complete academic and practical TF-IDF analysis across a list of clauses.
    """
    if not clauses_text:
        return {"error": "Corpus is empty"}

    # 1. Manual academic calculation
    manual_engine = ManualTFIDF(use_legal_stopwords=True)
    manual_engine.fit(clauses_text)

    clause_analyses = []
    for idx, text in enumerate(clauses_text):
        analysis = manual_engine.transform_single(text)
        clause_analyses.append({
            "clause_index": idx + 1,
            "text_snippet": text[:120] + "..." if len(text) > 120 else text,
            "top_terms": analysis["term_scores"][:5],
            "distinctive_keywords": analysis["top_terms"][:5]
        })

    # 2. Sklearn feature extraction
    sklearn_engine = SklearnTFIDFEngine(max_features=200, ngram_range=(1, 2))
    matrix, features = sklearn_engine.fit_transform(clauses_text)

    # 3. Overall top corpus keywords
    mean_tfidf_per_feature = np.mean(matrix, axis=0) if len(matrix) > 0 else np.array([])
    top_feature_indices = np.argsort(mean_tfidf_per_feature)[::-1][:15] if len(mean_tfidf_per_feature) > 0 else []
    
    corpus_top_features = [
        {"term": features[i], "mean_tfidf": round(float(mean_tfidf_per_feature[i]), 4)}
        for i in top_feature_indices if mean_tfidf_per_feature[i] > 0
    ]

    return {
        "academic_theory": {
            "concept": "Term Frequency - Inverse Document Frequency (TF-IDF)",
            "tf_formula": "TF(t, d) = count(t, d) / total_words(d)",
            "idf_formula": "IDF(t, D) = ln((1 + |D|) / (1 + DF(t))) + 1",
            "tfidf_formula": "TF-IDF(t, d, D) = TF(t, d) * IDF(t, D)",
            "contract_relevance": (
                "TF-IDF penalizes universally common contract words (e.g. 'agreement', 'section', 'party') "
                "while boosting distinctive domain terms (e.g. 'indemnification', 'arbitration', 'severability', 'liquidated damages')."
            ),
            "limitations": [
                "Bag-of-Words assumption: Ignores syntactic word order.",
                "Polysemy & Synonymy blindness: Treats 'terminate' and 'cancel' as completely unrelated vectors.",
                "Negation nuance loss: Cannot capture the semantic inversion of 'shall not pay' vs 'shall pay' without n-grams."
            ]
        },
        "total_documents": len(clauses_text),
        "vocabulary_size": len(manual_engine.vocabulary),
        "vocabulary_sample": manual_engine.vocabulary[:30],
        "corpus_top_features": corpus_top_features,
        "clause_level_analysis": clause_analyses
    }
