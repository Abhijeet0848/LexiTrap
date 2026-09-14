"""
Sample Contracts Registry and Data Loader
"""

import os
from typing import Dict, List, Any

SAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "saas_agreement": {
        "id": "saas_agreement",
        "name": "Benchmark 1: SaaS Master Services Agreement",
        "type": "SaaS Agreement",
        "filename": "saas_agreement.txt",
        "description": "Standard balanced enterprise cloud SaaS agreement with 60-day renewal notice, 12-month liability caps, and customer data ownership.",
        "expected_risk": "SAFE",
    },
    "nda_agreement": {
        "id": "nda_agreement",
        "name": "Benchmark 2: Mutual NDA (Standard)",
        "type": "Non-Disclosure Agreement",
        "filename": "nda_agreement.txt",
        "description": "Balanced two-way mutual non-disclosure agreement with 2-year term and reasonable standard-of-care protections.",
        "expected_risk": "SAFE",
    },
    "fair_standard_nda": {
        "id": "fair_standard_nda",
        "name": "Fair Mutual NDA (YC Standard)",
        "type": "Non-Disclosure Agreement",
        "filename": "fair_standard_nda.txt",
        "description": "Balanced, mutual non-disclosure agreement compliant with industry standards and free of predatory traps.",
        "expected_risk": "SAFE",
    },
    "employment_contract": {
        "id": "employment_contract",
        "name": "Benchmark 3: Software Engineering Employment Agreement",
        "type": "Employment Agreement",
        "filename": "employment_contract.txt",
        "description": "Fair employment contract with IP assignment strictly during work hours, personal project retention, and 30-day notice period.",
        "expected_risk": "SAFE",
    },
    "terms_of_service": {
        "id": "terms_of_service",
        "name": "Benchmark 4: Consumer Platform Terms of Service",
        "type": "Terms of Service",
        "filename": "terms_of_service.txt",
        "description": "Fair consumer platform terms with user data rights and 6-month liability limitation.",
        "expected_risk": "SAFE",
    },
    "freelance_contract": {
        "id": "freelance_contract",
        "name": "Benchmark 5: Freelance & Contractor Agreement",
        "type": "Independent Contractor",
        "filename": "freelance_contract.txt",
        "description": "Balanced freelance developer contract with milestone payments, IP assignment upon full payment, and 14-day notice.",
        "expected_risk": "SAFE",
    },
    "predatory_saas_tos": {
        "id": "predatory_saas_tos",
        "name": "High-Risk Test: Toxic Cloud SaaS Terms",
        "type": "Terms of Service",
        "filename": "predatory_saas_tos.txt",
        "description": "High-risk SaaS agreement containing unilateral amendments, perpetual AI training on user data, zero liability cap, and forced arbitration.",
        "expected_risk": "CRITICAL",
    },
    "unbalanced_nda": {
        "id": "unbalanced_nda",
        "name": "High-Risk Test: One-Sided Vendor NDA",
        "type": "Non-Disclosure Agreement",
        "filename": "unbalanced_nda.txt",
        "description": "Unbalanced one-way NDA with perpetual confidential lock-in, aggressive IP assignment, uncapped indemnity, and 2-year non-compete.",
        "expected_risk": "HIGH",
    },
    "predatory_employment_contract": {
        "id": "predatory_employment_contract",
        "name": "High-Risk Test: Predatory Executive Employment",
        "type": "Employment Agreement",
        "filename": "predatory_employment_contract.txt",
        "description": "Overbroad agreement claiming 24/7 personal IP ownership, 3-year worldwide non-compete lockout, and unilateral compensation changes.",
        "expected_risk": "CRITICAL",
    },
}


def load_sample_text(sample_id: str) -> str:
    """Loads contract text for a given sample ID."""
    if sample_id not in SAMPLE_CONTRACTS:
        raise ValueError(f"Unknown sample ID: {sample_id}. Available: {list(SAMPLE_CONTRACTS.keys())}")
    
    filename = SAMPLE_CONTRACTS[sample_id]["filename"]
    filepath = os.path.join(SAMPLES_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def list_samples() -> List[Dict[str, Any]]:
    """Returns a list of all sample contracts with metadata."""
    return list(SAMPLE_CONTRACTS.values())
