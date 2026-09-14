"""
Curated Legal Contract Clause Training Dataset for LexiTrap NLP Engine
Contains comprehensive labeled legal clauses across 18 authentic contract categories,
featuring both predatory traps and balanced industry standards.
"""

from typing import List, Tuple

TRAINING_DATA: List[Tuple[str, str]] = [
    # -------------------------------------------------------------
    # 1. UNILATERAL MODIFICATION
    # -------------------------------------------------------------
    ("We may modify, change, update, alter, or amend these terms of service at any time without prior notice in our sole discretion.", "Unilateral Modification"),
    ("Company reserves the right to modify these terms, fees, and pricing at any time without notice.", "Unilateral Modification"),
    ("We may amend any of this Agreement's terms at our sole discretion by posting the revised terms on the website.", "Unilateral Modification"),
    ("We may change, suspend, or discontinue the services, or any part of them, at any time without notice.", "Unilateral Modification"),
    ("Your continued use of the platform after the effective date of any modifications constitutes your acceptance of the revised terms.", "Unilateral Modification"),
    ("Modifications shall become effective immediately upon posting to the service without prior notification to you.", "Unilateral Modification"),
    ("Vendor reserves the right to alter pricing, storage limits, and SLA guarantees periodically in its sole discretion.", "Unilateral Modification"),
    ("Neither party may modify or amend this Agreement except through a written amendment signed by authorized representatives of both parties.", "Unilateral Modification"),
    ("Any modification to service fees or operational terms requires thirty (30) days prior written notice to Customer.", "Unilateral Modification"),

    # -------------------------------------------------------------
    # 2. ASYMMETRIC / UNCAPPED INDEMNIFICATION
    # -------------------------------------------------------------
    ("Customer shall indemnify, defend and hold harmless Vendor from and against any and all claims, damages, liabilities, costs, and losses.", "Indemnification"),
    ("User agrees to defend, indemnify, and hold harmless Company and each of its affiliates from all third-party lawsuits and attorney fees.", "Indemnification"),
    ("You shall at your sole expense defend and indemnify the company against any claim arising out of your use of the software.", "Indemnification"),
    ("Customer assumes uncapped indemnification obligations for any third-party action related to the deliverables.", "Indemnification"),
    ("Client shall bear all defense costs, settlements, and attorney fees incurred by vendor in any dispute relating to this agreement.", "Indemnification"),
    ("Each party agrees to defend, indemnify, and hold harmless the other party against third-party claims arising from gross negligence or IP infringement.", "Indemnification"),
    ("Vendor shall indemnify and defend Customer against any claim that the software infringes any third-party patent or copyright.", "Indemnification"),

    # -------------------------------------------------------------
    # 3. FORCED ARBITRATION & CLASS ACTION WAIVER
    # -------------------------------------------------------------
    ("Any dispute or claim arising from or relating to this Agreement is subject to binding arbitration and waiver of jury trial.", "Dispute Resolution & Arbitration"),
    ("You agree to resolve all disputes exclusively through confidential binding arbitration under the rules of the American Arbitration Association.", "Dispute Resolution & Arbitration"),
    ("You waive any right to bring or participate in a class action lawsuit or class-wide arbitration against the company.", "Dispute Resolution & Arbitration"),
    ("All disputes shall be arbitrated on an individual basis and not as a plaintiff or class member in any purported class proceeding.", "Dispute Resolution & Arbitration"),
    ("User waives all constitutional and statutory rights to go to court and have a trial in front of a judge or a jury.", "Dispute Resolution & Arbitration"),
    ("Disputes shall first be submitted to senior executive negotiations for thirty days; either party may seek equitable relief in any court of competent jurisdiction.", "Dispute Resolution & Arbitration"),
    ("All legal claims arising under this agreement may be brought in any competent state or federal court.", "Dispute Resolution & Arbitration"),

    # -------------------------------------------------------------
    # 4. AGGRESSIVE IP & FEEDBACK EXPROPRIATION
    # -------------------------------------------------------------
    ("You hereby irrevocably assign to Company all right, title, and interest in and to all feedback, ideas, and workflow customizations.", "Intellectual Property"),
    ("All feedback, suggestions, and feature requests shall be the sole and exclusive property of the company without compensation.", "Intellectual Property"),
    ("User grants provider a perpetual, irrevocable, royalty-free, worldwide license to use, modify, exploit, and monetize all uploaded submissions.", "Intellectual Property"),
    ("Employee hereby assigns all intellectual property rights, inventions, and moral rights created during or outside work hours.", "Intellectual Property"),
    ("All improvements, modifications, customizations, or derivative works created using the platform shall belong exclusively to vendor.", "Intellectual Property"),
    ("Customer retains all right, title, and interest in and to Customer Data, workflows, and proprietary materials.", "Intellectual Property"),
    ("Vendor is granted a limited, revocable, non-exclusive license solely to provide the contracted services during the term.", "Intellectual Property"),

    # -------------------------------------------------------------
    # 5. PERPETUAL DATA & AI HARVESTING
    # -------------------------------------------------------------
    ("We process your voice input, location, and telemetry in the cloud to improve our services and train machine learning models.", "Privacy & Data Protection"),
    ("Company retains perpetual rights to ingest user documents, prompts, and confidential data to train commercial AI and LLM algorithms.", "Privacy & Data Protection"),
    ("You grant vendor an irrevocable license to aggregate, de-identify, and utilize customer content to develop generative AI models.", "Privacy & Data Protection"),
    ("Customer data and confidential records may be incorporated into neural networks and used to train third-party artificial intelligence systems.", "Privacy & Data Protection"),
    ("Vendor covenants that Customer Data shall NOT be stored, aggregated, or utilized to train or fine-tune any AI or machine learning model.", "Privacy & Data Protection"),
    ("All uploaded customer content is processed in strict zero-data-retention isolation and purged upon session termination.", "Privacy & Data Protection"),

    # -------------------------------------------------------------
    # 6. HIDDEN AUTO-RENEWAL & TRAPPED TERMINATION
    # -------------------------------------------------------------
    ("This agreement automatically renews for successive multi-year periods of 3 years unless cancelled 90 days prior via certified postal mail.", "Automatic Renewal"),
    ("Subscription extends automatically for additional 12-month terms and early termination incurs liquidated damages of all remaining fees.", "Automatic Renewal"),
    ("User authorizes recurring automatic debits and NACH bank mandates without advance renewal notification or cancellation options.", "Automatic Renewal"),
    ("This Agreement shall automatically renew for successive one-year terms unless either party provides thirty (30) days prior written notice.", "Automatic Renewal"),
    ("Customer may disable automatic renewal at any time directly through the self-service online account portal.", "Automatic Renewal"),

    # -------------------------------------------------------------
    # 7. OVERBROAD NON-COMPETE & LOCKOUT
    # -------------------------------------------------------------
    ("Employee shall not directly or indirectly engage in, perform services for, or invest in any competing business worldwide for 3 years.", "Non-Compete & Lockout"),
    ("Worker covenants not to work for any company operating in the software or technology industry within 500 miles for 24 months.", "Non-Compete & Lockout"),
    ("Contractor agrees to a global 2-year lockout from providing consulting services to any entity in the same market sector.", "Non-Compete & Lockout"),
    ("Employee agrees for a period of six (6) months following termination not to solicit key executive personnel of the Company.", "Non-Solicitation"),
    ("No non-compete restrictions shall apply following the termination of this independent contractor engagement.", "Non-Compete & Lockout"),

    # -------------------------------------------------------------
    # 8. COMPLETE LIABILITY GUTTING & AS-IS TRAP
    # -------------------------------------------------------------
    ("THE SERVICES ARE PROVIDED STRICTLY 'AS IS' WITHOUT WARRANTY OF ANY KIND AND COMPANY'S TOTAL LIABILITY SHALL NOT EXCEED $50.00.", "Limitation of Liability"),
    ("IN NO EVENT SHALL VENDOR BE LIABLE FOR ANY DAMAGES, DATA LOSS, OR SYSTEM BREACH EXCEEDING THE TOTAL AMOUNT OF $0.", "Limitation of Liability"),
    ("Company disclaims all warranties of merchantability and fitness for a particular purpose and assumes zero liability for outages.", "Warranty & Disclaimer"),
    ("Except for gross negligence or willful misconduct, each party's total aggregate liability shall be capped at total fees paid in the preceding 12 months.", "Limitation of Liability"),
    ("Vendor warrants that the service will perform materially in accordance with published SLA specifications.", "Warranty & Disclaimer"),

    # -------------------------------------------------------------
    # 9. TERM & TERMINATION
    # -------------------------------------------------------------
    ("The provider may terminate this agreement at any time in its sole discretion without prior notice or cause.", "Termination"),
    ("Company may immediately suspend or terminate your account without notice upon suspected breach of these terms.", "Termination"),
    ("Either party may terminate this agreement for convenience upon providing thirty (30) days prior written notice to the other party.", "Termination"),
    ("Either party may terminate this agreement immediately if the other party materially breaches any term and fails to cure within 30 days.", "Termination"),
    ("Upon termination, all licenses granted herein shall terminate and Vendor shall promptly return or destroy all Customer Data.", "Termination"),

    # -------------------------------------------------------------
    # 10. CONFIDENTIALITY
    # -------------------------------------------------------------
    ("Recipient shall hold Discloser's Confidential Information in strict confidence and not disclose it to any third party for 3 years.", "Confidentiality"),
    ("Confidential Information does not include information that is publicly known, already known to Recipient, or independently developed.", "Confidentiality"),
    ("Each party agrees to protect the other party's proprietary technical and business information with the same degree of care it uses for its own data.", "Confidentiality"),
    ("All trade secrets, customer lists, and pricing terms disclosed under this NDA shall remain confidential indefinitely.", "Confidentiality"),

    # -------------------------------------------------------------
    # 11. GOVERNING LAW & JURISDICTION
    # -------------------------------------------------------------
    ("This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of laws.", "Governing Law & Jurisdiction"),
    ("These Terms are governed by the laws of India, and the competent courts of Bengaluru, Karnataka shall have exclusive jurisdiction.", "Governing Law & Jurisdiction"),
    ("Any action arising under this contract must be instituted exclusively in the federal or state courts located in Santa Clara County, California.", "Governing Law & Jurisdiction"),

    # -------------------------------------------------------------
    # 12. PAYMENT, FEES & BILLING
    # -------------------------------------------------------------
    ("Customer shall pay all undisputed invoices within thirty (30) days of the invoice date.", "Payment & Billing"),
    ("All subscription fees are billed in advance on a monthly or annual cycle and are payable in US Dollars.", "Payment & Billing"),
    ("Late payments shall accrue interest at the rate of 1.5% per month or the maximum legal rate permissible by law.", "Payment & Billing"),
    ("Vendor shall provide itemized monthly billing statements detailing platform usage and applicable taxes.", "Payment & Billing"),

    # -------------------------------------------------------------
    # 13. CANCELLATION & REFUNDS
    # -------------------------------------------------------------
    ("All fees and payments are strictly non-refundable and non-cancellable under any circumstances.", "Cancellation & Refund"),
    ("If Customer terminates this agreement due to Vendor's uncured material breach, Customer shall receive a pro-rata refund of prepaid unearned fees.", "Cancellation & Refund"),
    ("Users may request a full refund within fourteen (14) days of the initial purchase date if unsatisfied with the service.", "Cancellation & Refund"),
]
