"""
Core Academic NLP Pipeline Module for LexiTrap
Implements the fundamental stages of the Natural Language Processing hierarchy:
1. Sentence & Word Tokenization (with Stopword analysis)
2. Morphological Lemmatization (Word -> Lemma mapping)
3. Part-of-Speech (POS) Tagging (Nouns, Verbs, Adjectives, Adverbs, Modal Auxiliaries)
4. Legal Named Entity Recognition (NER: ORG, PERSON, DATE, MONEY, GPE, LAW)
5. TF-IDF Salient Term Extraction (Unigrams, Bigrams)
6. Semantic Cosine Similarity against Gold-Standard Benchmarks
"""

import re
import math
from typing import List, Dict, Any, Tuple, Set, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Comprehensive English & Legal Stopwords
LEGAL_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "herein", "therein", "hereof", "thereof", "hereto",
    "thereto", "hereby", "thereby", "wherein", "whereof"
}

# Modal Auxiliaries indicating Normative Deontic Logic
MODAL_VERBS: Set[str] = {
    "shall", "may", "must", "will", "can", "should", "would", "could", "might", "ought"
}

# Irregular & Legal Lemma Mappings (Word -> Base Lemma)
LEGAL_LEMMA_MAP: Dict[str, str] = {
    "indemnifies": "indemnify",
    "indemnified": "indemnify",
    "indemnifying": "indemnify",
    "indemnification": "indemnify",
    "terminates": "terminate",
    "terminated": "terminate",
    "terminating": "terminate",
    "termination": "terminate",
    "modifies": "modify",
    "modified": "modify",
    "modifying": "modify",
    "modification": "modify",
    "modifications": "modify",
    "amends": "amend",
    "amended": "amend",
    "amending": "amend",
    "amendment": "amend",
    "amendments": "amend",
    "obligates": "obligate",
    "obligated": "obligate",
    "obligating": "obligate",
    "obligation": "obligation",
    "obligations": "obligation",
    "prohibits": "prohibit",
    "prohibited": "prohibit",
    "prohibiting": "prohibit",
    "prohibition": "prohibition",
    "prohibitions": "prohibition",
    "warrants": "warrant",
    "warranted": "warrant",
    "warranting": "warrant",
    "warranty": "warranty",
    "warranties": "warranty",
    "represents": "represent",
    "represented": "represent",
    "representing": "represent",
    "representation": "representation",
    "representations": "representation",
    "waives": "waive",
    "waived": "waive",
    "waiving": "waive",
    "waiver": "waiver",
    "waivers": "waiver",
    "renews": "renew",
    "renewed": "renew",
    "renewing": "renew",
    "renewal": "renewal",
    "renewals": "renewal",
    "disclaims": "disclaim",
    "disclaimed": "disclaim",
    "disclaiming": "disclaim",
    "disclaimer": "disclaimer",
    "disclaimers": "disclaimer",
    "assigns": "assign",
    "assigned": "assign",
    "assigning": "assign",
    "assignment": "assignment",
    "liabilities": "liability",
    "agreements": "agreement",
    "provisions": "provision",
    "remedies": "remedy",
    "entities": "entity",
    "parties": "party",
    "clauses": "clause",
    "services": "service",
    "users": "user",
    "customers": "customer",
    "vendors": "vendor",
    "providers": "provider",
    "companies": "company",
    "suppliers": "supplier",
    "resellers": "reseller",
    "employees": "employee",
    "contractors": "contractor",
    "damages": "damage",
    "losses": "loss",
    "claims": "claim",
    "rights": "right",
    "fees": "fee",
    "costs": "cost",
    "expenses": "expense",
    "disputes": "dispute",
    "licenses": "license",
    "licensed": "license",
    "licensing": "license",
}


class NLPPipeline:
    """
    Standard NLP Engineering Pipeline:
    Extracts linguistic, syntactic, and semantic features across contract text.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=2500,
            sublinear_tf=True,
            strip_accents="unicode"
        )

    # -------------------------------------------------------------
    # 1. TOKENIZATION & STOPWORD ANALYSIS
    # -------------------------------------------------------------
    def tokenize_words(self, text: str) -> List[str]:
        """Extracts word tokens while preserving currency, acronyms, and alphanumeric symbols."""
        if not text:
            return []
        raw_tokens = re.findall(r"\b[A-Za-z0-9\$\%\€\₹][A-Za-z0-9\-_\$\%\€\₹]*\b", text)
        return raw_tokens

    def analyze_tokens(self, text: str) -> Dict[str, Any]:
        """
        Tokenizes text and computes vocabulary size, stopword count, and token density.
        """
        tokens = self.tokenize_words(text)
        total_tokens = len(tokens)
        
        lower_tokens = [t.lower() for t in tokens]
        stopwords_found = [t for t in lower_tokens if t in LEGAL_STOPWORDS]
        content_tokens = [t for t in lower_tokens if t not in LEGAL_STOPWORDS and not t.isdigit()]
        unique_vocab = sorted(list(set(lower_tokens)))
        
        stopword_ratio = round((len(stopwords_found) / max(1, total_tokens)) * 100, 1)

        return {
            "total_tokens": total_tokens,
            "unique_vocab_count": len(unique_vocab),
            "stopwords_count": len(stopwords_found),
            "stopword_ratio_pct": stopword_ratio,
            "content_tokens_count": len(content_tokens),
            "sample_tokens": tokens[:25],
        }

    # -------------------------------------------------------------
    # 2. LEMMATIZATION (Word -> Lemma Mapping)
    # -------------------------------------------------------------
    def lemmatize_word(self, word: str) -> str:
        """Applies morphological rules and legal lemma lookups to get canonical root."""
        w = word.lower().strip()
        if w in LEGAL_LEMMA_MAP:
            return LEGAL_LEMMA_MAP[w]
        
        # Rule-based morphological suffix decomposition
        if w.endswith("ies") and len(w) > 4:
            return w[:-3] + "y"
        elif w.endswith("es") and len(w) > 3 and (w.endswith("shes") or w.endswith("ches") or w.endswith("sses") or w.endswith("xes")):
            return w[:-2]
        elif w.endswith("s") and len(w) > 3 and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is"):
            return w[:-1]
        elif w.endswith("ing") and len(w) > 5:
            # e.g., binding -> bind, terminating -> terminate
            base = w[:-3]
            if base.endswith("at"):
                return base + "e"
            elif base.endswith("v"):
                return base + "e"
            return base
        elif w.endswith("ed") and len(w) > 4:
            base = w[:-2]
            if base.endswith("at"):
                return base + "e"
            return base
            
        return w

    def extract_lemmas(self, text: str) -> Dict[str, Any]:
        """
        Generates original word -> lemma mappings and lemma frequency distribution.
        """
        tokens = self.tokenize_words(text)
        lemma_mappings: List[Dict[str, str]] = []
        lemma_counter = Counter()

        for token in tokens:
            cleaned = token.strip()
            if not cleaned or not cleaned[0].isalpha():
                continue
            lemma = self.lemmatize_word(cleaned)
            lemma_counter[lemma] += 1
            if cleaned.lower() != lemma and len(lemma_mappings) < 15:
                # Store sample transformations
                lemma_mappings.append({
                    "original": cleaned,
                    "lemma": lemma
                })

        return {
            "total_lemmas": sum(lemma_counter.values()),
            "unique_lemmas_count": len(lemma_counter),
            "top_lemmas": [{"lemma": l, "count": c} for l, c in lemma_counter.most_common(10)],
            "sample_transformations": lemma_mappings[:8],
        }

    # -------------------------------------------------------------
    # 3. PART-OF-SPEECH (POS) TAGGING
    # -------------------------------------------------------------
    def tag_pos(self, text: str) -> Dict[str, Any]:
        """
        Classifies tokens into syntactic POS classes:
        - Nouns (NN / NNP)
        - Verbs (VB / VBD / VBG)
        - Modal Auxiliaries (MD: shall, may, must, will, can)
        - Adjectives (JJ)
        - Adverbs (RB)
        - Prepositions & Conjunctions
        """
        tokens = self.tokenize_words(text)
        pos_tags: List[Dict[str, str]] = []
        counts: Dict[str, int] = {
            "Modal Verbs (Deontic)": 0,
            "Nouns (Entities/Objects)": 0,
            "Verbs (Actions)": 0,
            "Adjectives (Qualifiers)": 0,
            "Adverbs (Modifiers)": 0,
            "Other / Particles": 0,
        }
        modal_tokens_found: List[str] = []

        for token in tokens:
            t_low = token.lower()
            
            # Modal check
            if t_low in MODAL_VERBS:
                tag = "MD"
                label = "Modal Verbs (Deontic)"
                modal_tokens_found.append(t_low)
            # Adjective heuristic
            elif t_low.endswith(("able", "ible", "ous", "ive", "ful", "less", "al", "ic", "ent", "ant")):
                tag = "JJ"
                label = "Adjectives (Qualifiers)"
            # Adverb heuristic
            elif t_low.endswith("ly") and len(t_low) > 3:
                tag = "RB"
                label = "Adverbs (Modifiers)"
            # Verb heuristic
            elif t_low.endswith(("ate", "ize", "ise", "fy", "ing", "ed")) or t_low in {"terminate", "modify", "amend", "agree", "pay", "defend", "hold", "renew", "waive", "cancel", "disclaim", "indemnify", "assign", "collect", "provide", "refund"}:
                tag = "VB"
                label = "Verbs (Actions)"
            # Noun heuristic
            elif token[0].isupper() or t_low.endswith(("tion", "sion", "ment", "ness", "ity", "ship", "ance", "ence", "or", "er", "ee")) or t_low in {"party", "vendor", "customer", "user", "agreement", "term", "condition", "clause", "section", "service", "liability", "warranty", "damages", "data", "software", "court", "law"}:
                tag = "NN"
                label = "Nouns (Entities/Objects)"
            else:
                tag = "OTH"
                label = "Other / Particles"

            counts[label] += 1
            if len(pos_tags) < 20:
                pos_tags.append({"token": token, "tag": tag, "category": label})

        total = max(1, len(tokens))
        distribution = {k: {"count": v, "pct": round((v / total) * 100, 1)} for k, v in counts.items()}

        return {
            "distribution": distribution,
            "modals_found": list(set(modal_tokens_found)),
            "sample_pos_tags": pos_tags,
        }

    # -------------------------------------------------------------
    # 4. LEGAL NAMED ENTITY RECOGNITION (NER)
    # -------------------------------------------------------------
    def extract_named_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extracts domain-specific legal entities:
        - ORG: Company, Vendor, Platforms, Licensors
        - PERSON: User, Customer, Client, Employee, Contractor
        - DATE / DURATION: Notice windows, terms, grace periods (e.g. 30 days, 90 days, 12 months, 3 years)
        - MONEY: Financial liability limits and fee caps (e.g. $50.00, INR 1,000, ₹500, 100% of fees)
        - GPE / JURISDICTION: Governing law states/countries (e.g. California, Delaware, Bengaluru, India, New Delhi)
        - LAW / REGULATION: Statutory acts (e.g. Information Technology Act 2000, Consumer Protection Act, GDPR)
        """
        entities: List[Dict[str, str]] = []
        seen = set()

        # 1. Money & Financial Caps
        money_matches = re.finditer(r"(?:\$|₹|€|£|INR|USD)\s*[\d,]+(?:\.\d{2})?|\b\d+\s*(?:dollars|rupees|percent|%)\b|\b12\s+months?\s+of\s+fees\b", text, re.I)
        for m in money_matches:
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                entities.append({"entity": val, "label": "MONEY", "description": "Financial Amount / Liability Cap"})

        # 2. Dates, Deadlines & Notice Durations
        duration_matches = re.finditer(r"\b\d+\s*(?:calendar\s+days?|business\s+days?|days?|weeks?|months?|years?|hours?)\b|\b(?:immediately|at\s+any\s+time|perpetual|perpetually|upon\s+notice)\b", text, re.I)
        for m in duration_matches:
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                entities.append({"entity": val, "label": "DATE / DURATION", "description": "Time Window / Notice Period"})

        # 3. Organizations, Platforms & Corporations
        org_matches = re.finditer(r"\b(?:Flipkart|Amazon|Meesho|Swiggy|Zomato|Zepto|Blinkit|Myntra|Reddit|Discord|GitHub|Apple|Google|Microsoft|Netflix|Spotify|Steam|Disney|Adobe|Byju'?s|OpenAI|Meta|Twitter|X\s+Corp|Company|Vendor|Licensor|Provider|Discloser|Recipient|Fashnear\s+Technologies|Bundl\s+Technologies)\b(?:\s+(?:Inc\.|Ltd\.|Pvt\.\s*Ltd\.|LLC|Corporation|Limited))?", text, re.I)
        for m in org_matches:
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                entities.append({"entity": val, "label": "ORG", "description": "Corporate Entity / Platform"})

        # 4. GPE / Jurisdiction & Governing Forums
        gpe_matches = re.finditer(r"\b(?:California|Delaware|New\s+York|Texas|England|Wales|India|Karnataka|Bengaluru|Bangalore|New\s+Delhi|Delhi|Mumbai|Maharashtra|United\s+States|European\s+Union|Ireland|Singapore)\b", text, re.I)
        for m in gpe_matches:
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                entities.append({"entity": val, "label": "GPE", "description": "Governing Jurisdiction / Forum"})

        # 5. Statutory Laws & Legal Acts
        law_matches = re.finditer(r"\b(?:Information\s+Technology\s+Act(?:,\s*\d{4})?|Consumer\s+Protection\s+Act|Arbitration\s+and\s+Conciliation\s+Act|Section\s+79|GDPR|FTC\s+Act|American\s+Arbitration\s+Association|AAA\s+Rules|U\.S\.C\.|Civil\s+Code)\b", text, re.I)
        for m in law_matches:
            val = m.group(0).strip()
            if val.lower() not in seen:
                seen.add(val.lower())
                entities.append({"entity": val, "label": "LAW / STATUTE", "description": "Governing Statute / Legal Authority"})

        return entities[:12]

    # -------------------------------------------------------------
    # 5. TF-IDF SALIENT KEYTERM EXTRACTION
    # -------------------------------------------------------------
    def extract_tfidf_terms(self, text: str, top_n: int = 8) -> List[Dict[str, Any]]:
        """
        Extracts the highest TF-IDF scoring n-grams from a clause or document.
        """
        if not text or len(text.split()) < 4:
            return []
        try:
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=500)
            matrix = vec.fit_transform([text])
            feature_names = vec.get_feature_names_out()
            scores = matrix.toarray()[0]
            
            scored_terms = [(feature_names[i], float(scores[i])) for i in range(len(feature_names)) if scores[i] > 0]
            scored_terms.sort(key=lambda x: x[1], reverse=True)
            
            return [{"term": term, "tfidf_score": round(score, 4)} for term, score in scored_terms[:top_n]]
        except Exception:
            return []

    # -------------------------------------------------------------
    # 6. SEMANTIC SIMILARITY ENGINE
    # -------------------------------------------------------------
    def compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity of TF-IDF vector representations between two clauses.
        """
        if not text1 or not text2:
            return 0.0
        try:
            vec = TfidfVectorizer(ngram_range=(1, 3), stop_words="english")
            tfidf_matrix = vec.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(float(sim), 4)
        except Exception:
            return 0.0

    # -------------------------------------------------------------
    # 7. UNIFIED CLAUSE PIPELINE EXECUTION
    # -------------------------------------------------------------
    def process_clause(self, text: str) -> Dict[str, Any]:
        """
        Runs the full academic NLP pipeline on an individual clause.
        """
        token_stats = self.analyze_tokens(text)
        lemmas = self.extract_lemmas(text)
        pos = self.tag_pos(text)
        ner = self.extract_named_entities(text)
        tfidf = self.extract_tfidf_terms(text, top_n=6)

        return {
            "token_stats": token_stats,
            "lemmas": lemmas,
            "pos_distribution": pos["distribution"],
            "modal_verbs": pos["modals_found"],
            "sample_pos_tags": pos["sample_pos_tags"],
            "named_entities": ner,
            "tfidf_salient_terms": tfidf,
        }
