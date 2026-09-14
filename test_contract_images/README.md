# 📸 Test Contract Images for Photo OCR & Risk Auditing

This folder contains realistic, high-resolution test contract images designed to test LexiTrap's **Photo OCR Scanning** (`📸 Take Photo` / `🖼️ Upload Photo`) and automated risk analysis pipeline.

---

## 📁 Available Test Contract Images

| Image File | Contract Type | Key Traps & Clauses to Verify | Expected Risk Grade |
| :--- | :--- | :--- | :---: |
| [`01_predatory_saas_contract.png`](file:///d:/NLP%20project/test_contract_images/01_predatory_saas_contract.png) | Master SaaS Cloud Agreement | Unilateral terms & pricing changes, AI data training rights, nominal liability cap ($50 / $0), mandatory arbitration | **Grade F** (Critical Risk) |
| [`02_one_way_predatory_nda.png`](file:///d:/NLP%20project/test_contract_images/02_one_way_predatory_nda.png) | One-Way Asymmetric NDA | Perpetual indefinite confidentiality, 1-sided uncapped indemnity, immediate unilateral cancellation | **Grade D/F** (High Risk) |
| [`03_toxic_employment_contract.png`](file:///d:/NLP%20project/test_contract_images/03_toxic_employment_contract.png) | Predatory Employment Agreement | 3-Year worldwide non-compete, 24/7 personal IP expropriation, termination at will without notice or severance | **Grade F** (Critical Risk) |
| [`04_unilateral_termination_clause.png`](file:///d:/NLP%20project/test_contract_images/04_unilateral_termination_clause.png) | Termination Addendum | Immediate termination at any time without notice + full fee retention with refund waiver | **Grade F** (Critical Risk) |
| [`05_balanced_fair_contract.png`](file:///d:/NLP%20project/test_contract_images/05_balanced_fair_contract.png) | Standard Commercial License | Mutual 12-month fees paid liability cap, 30-day notice for cause termination, mutual 2-year confidentiality | **Grade A** (Safe / Balanced) |

---

## 🚀 How to Test in the Browser:

1. Open LexiTrap at **`http://127.0.0.1:5000/`**.
2. Click the **`🖼️ Upload Photo`** button.
3. Select any `.png` image from the `test_contract_images/` folder (e.g. `01_predatory_saas_contract.png`).
4. Watch LexiTrap's built-in **Tesseract.js OCR engine** read the image and auto-fill the text editor.
5. Click **`⚡ Check Contract Now`** to view the full risk audit, health score, and redline rewrites!
