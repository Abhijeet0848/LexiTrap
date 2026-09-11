"""
Sample Contracts Registry and Data Loader
"""

import os
from typing import Dict, List, Any

SAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "predatory_saas_tos": {
        "id": "predatory_saas_tos",
        "name": "Toxic SaaS Terms of Service (CloudSphere)",
        "type": "Terms of Service",
        "filename": "predatory_saas_tos.txt",
        "description": "High-risk SaaS agreement containing unilateral amendments, perpetual AI training on user data, zero liability cap, and forced arbitration.",
        "expected_risk": "CRITICAL",
    },
    "unbalanced_nda": {
        "id": "unbalanced_nda",
        "name": "One-Sided Vendor NDA",
        "type": "Non-Disclosure Agreement",
        "filename": "unbalanced_nda.txt",
        "description": "Unbalanced one-way NDA with perpetual confidential lock-in, aggressive IP assignment, uncapped indemnity, and 2-year non-compete.",
        "expected_risk": "HIGH",
    },
    "fair_standard_nda": {
        "id": "fair_standard_nda",
        "name": "Fair Mutual NDA (YC / NVCA Standard)",
        "type": "Non-Disclosure Agreement",
        "filename": "fair_standard_nda.txt",
        "description": "Balanced, mutual non-disclosure agreement compliant with industry standards and free of predatory traps.",
        "expected_risk": "SAFE",
    },
    "predatory_employment_contract": {
        "id": "predatory_employment_contract",
        "name": "Predatory Executive Employment Agreement",
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
