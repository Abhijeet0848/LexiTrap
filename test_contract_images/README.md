# 📸 Real-World Government & Private Sector Test Contracts

This directory contains authentic, high-resolution contract images and documents from both the **Government / Public Sector** and the **Private Enterprise Sector** for testing LexiTrap's **Photo OCR Reader** (`📸 Take Photo` / `🖼️ Upload Photo`), clause segmentation, and AI risk analysis.

---

## 🏛️ Government & Public Sector Contracts

| Image File | Organization / Authority | Contract Scope & Scenario | Key Clauses & Traps |
| :--- | :--- | :--- | :--- |
| [`06_gem_government_procurement_contract.png`](file:///d:/NLP%20project/test_contract_images/06_gem_government_procurement_contract.png) | **Government of India (GeM)** • Ministry of Commerce | Public Procurement of Goods & Services | Liquidated damages (10% ceiling), unilateral termination & vendor debarment / blacklisting, New Delhi arbitration. |
| [`07_cpwd_government_works_contract.png`](file:///d:/NLP%20project/test_contract_images/07_cpwd_government_works_contract.png) | **Central Public Works Department (CPWD)** | Engineering, Procurement & Construction (EPC) Works | Unilateral variation of work scope without price escalation, full indemnity of government officials, earnest money security forfeiture. |

---

## 🏢 Private Sector & Enterprise Contracts

| Image File | Industry / Platform | Contract Type | Key Clauses & Traps |
| :--- | :--- | :--- | :--- |
| [`08_microsoft_enterprise_cloud_agreement.png`](file:///d:/NLP%20project/test_contract_images/08_microsoft_enterprise_cloud_agreement.png) | **Microsoft Corporation** • Global Cloud | Master Services & Azure Cloud Customer Agreement | Zero AI training on customer data guarantee, mutual 12-month fees paid liability cap, Washington state jurisdiction. |
| [`09_it_services_master_agreement.png`](file:///d:/NLP%20project/test_contract_images/09_it_services_master_agreement.png) | **IT Services (TCS / Infosys / Wipro)** | Master Services Agreement (MSA) | Work-made-for-hire IP assignment, 12-month mutual non-solicitation of software engineers, 60-day notice for convenience termination. |
| [`01_predatory_saas_contract.png`](file:///d:/NLP%20project/test_contract_images/01_predatory_saas_contract.png) | **Commercial SaaS Provider** | Cloud Subscription Agreement | Unilateral pricing modifications, perpetual data AI training rights, nominal liability cap ($50 / $0), mandatory arbitration. |
| [`02_one_way_predatory_nda.png`](file:///d:/NLP%20project/test_contract_images/02_one_way_predatory_nda.png) | **Corporate Legal** | One-Way Asymmetric NDA | Perpetual non-expiring confidentiality, 1-sided uncapped indemnity, immediate unilateral termination. |
| [`03_toxic_employment_contract.png`](file:///d:/NLP%20project/test_contract_images/03_toxic_employment_contract.png) | **Tech Employer** | Employment & Restrictive Covenants | 3-Year worldwide non-compete, 24/7 personal IP assignment, termination at will without notice or severance. |
| [`04_unilateral_termination_clause.png`](file:///d:/NLP%20project/test_contract_images/04_unilateral_termination_clause.png) | **Service Provider** | Termination Addendum | Immediate termination at any time without notice + full fee retention with refund waiver. |
| [`05_balanced_fair_contract.png`](file:///d:/NLP%20project/test_contract_images/05_balanced_fair_contract.png) | **Commercial Software** | Standard Balanced License | Mutual 12-month liability cap, 30-day notice for cause termination, mutual 2-year confidentiality. |

---

## 🚀 How to Test in the Browser:

1. Open LexiTrap at **`http://127.0.0.1:5000/`**.
2. Click the **`🖼️ Upload Photo`** button.
3. Select any `.png` image from `test_contract_images/` (e.g. `06_gem_government_procurement_contract.png` or `08_microsoft_enterprise_cloud_agreement.png`).
4. Watch LexiTrap's built-in **Tesseract OCR engine** read the image text and populate the editor.
5. Click **`⚡ Check Contract Now`** to view the full risk audit, health score, and fair redlines!
