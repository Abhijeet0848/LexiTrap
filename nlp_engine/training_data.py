"""
Curated Legal Contract Clause Training Dataset for LexiTrap NLP Engine
Contains diverse real-world legal clauses across 8 predatory trap categories and safe/balanced standards.
"""

from typing import List, Tuple

# Tuples of (clause_text, category_label)
TRAINING_DATA: List[Tuple[str, str]] = [
    # -------------------------------------------------------------
    # 1. UNILATERAL MODIFICATION TRAP
    # -------------------------------------------------------------
    ("We may modify, change, update, alter, or amend these terms of service at any time without prior notice in our sole discretion.", "Unilateral Modification Trap"),
    ("Company reserves the right to modify these terms, fees, and pricing at any time without notice.", "Unilateral Modification Trap"),
    ("We may amend any of this Agreement's terms at our sole discretion by posting the revised terms on the website.", "Unilateral Modification Trap"),
    ("We may change, suspend, or discontinue the services, or any part of them, at any time without notice.", "Unilateral Modification Trap"),
    ("Your continued use of the platform after the effective date of any modifications constitutes your acceptance of the revised terms.", "Unilateral Modification Trap"),
    ("Modifications shall become effective immediately upon posting to the service without prior notification to you.", "Unilateral Modification Trap"),
    ("We reserve the right to alter pricing, storage limits, and SLA uptime guarantees periodically at our sole discretion.", "Unilateral Modification Trap"),
    ("The company may update or change these terms from time to time without obligation to notify users.", "Unilateral Modification Trap"),
    ("By continuing to access or use the application after revisions become effective, you agree to be bound by the updated terms.", "Unilateral Modification Trap"),
    ("Platform fees, subscription tiers, and features are subject to change without notice at the company's sole discretion.", "Unilateral Modification Trap"),
    ("Vendor reserves the right to alter service specifications or discontinue features without liability or prior consultation.", "Unilateral Modification Trap"),
    ("Terms and conditions may be revised periodically and will be binding on all active accounts upon publication.", "Unilateral Modification Trap"),

    # -------------------------------------------------------------
    # 2. ASYMMETRIC INDEMNIFICATION
    # -------------------------------------------------------------
    ("Customer shall indemnify, defend and hold harmless Vendor from and against any and all claims, damages, liabilities, costs, and losses.", "Asymmetric / Uncapped Indemnification"),
    ("User agrees to defend, indemnify, and hold harmless Company and each of its affiliates from all third-party lawsuits and attorney fees.", "Asymmetric / Uncapped Indemnification"),
    ("You shall at your sole expense defend and indemnify the company against any claim arising out of your use of the software.", "Asymmetric / Uncapped Indemnification"),
    ("Customer assumes uncapped indemnification obligations for any third-party action related to the provided deliverables.", "Asymmetric / Uncapped Indemnification"),
    ("User will hold harmless the service provider from all liabilities, judgments, and legal expenses incurred in connection with the service.", "Asymmetric / Uncapped Indemnification"),
    ("You are solely responsible for defending and holding harmless the platform against all regulatory fines or user disputes.", "Asymmetric / Uncapped Indemnification"),
    ("Subscriber agrees to fully indemnify provider for any claims arising from data uploads or account activity without limitation.", "Asymmetric / Uncapped Indemnification"),
    ("Client shall bear all defense costs, settlements, and attorney fees incurred by vendor in any dispute relating to this agreement.", "Asymmetric / Uncapped Indemnification"),

    # -------------------------------------------------------------
    # 3. FORCED ARBITRATION & CLASS ACTION WAIVER
    # -------------------------------------------------------------
    ("Any dispute or claim arising from or relating to this Agreement is subject to binding arbitration and waiver of jury trial.", "Forced Arbitration & Class Action Waiver"),
    ("You agree to resolve all disputes exclusively through confidential binding arbitration under the rules of the American Arbitration Association.", "Forced Arbitration & Class Action Waiver"),
    ("You waive any right to bring or participate in a class action lawsuit or class-wide arbitration against the company.", "Forced Arbitration & Class Action Waiver"),
    ("All disputes shall be arbitrated on an individual basis and not as a plaintiff or class member in any purported class proceeding.", "Forced Arbitration & Class Action Waiver"),
    ("User waives all constitutional and statutory rights to go to court and have a trial in front of a judge or a jury.", "Forced Arbitration & Class Action Waiver"),
    ("Arbitrator may not consolidate more than one person's claims and class arbitrations are strictly prohibited.", "Forced Arbitration & Class Action Waiver"),
    ("Disputes/Binding Arbitration. Any legal controversy shall be settled by binding arbitration in Delaware with no right to court appeal.", "Forced Arbitration & Class Action Waiver"),
    ("You agree that any claim against provider must be brought individually and you forfeit all class action participation rights.", "Forced Arbitration & Class Action Waiver"),

    # -------------------------------------------------------------
    # 4. AGGRESSIVE IP & FEEDBACK EXPROPRIATION
    # -------------------------------------------------------------
    ("You hereby irrevocably assign to Company all right, title, and interest in and to all feedback, ideas, and workflow customizations.", "Aggressive IP & Feedback Expropriation"),
    ("All feedback, suggestions, and feature requests shall be the sole and exclusive property of the company without compensation.", "Aggressive IP & Feedback Expropriation"),
    ("User grants provider a perpetual, irrevocable, royalty-free, worldwide license to use, modify, exploit, and monetize all uploaded submissions.", "Aggressive IP & Feedback Expropriation"),
    ("Employee hereby assigns and agrees to assign all intellectual property rights, inventions, and moral rights created during or outside work hours.", "Aggressive IP & Feedback Expropriation"),
    ("All improvements, modifications, customizations, or derivative works created using the platform shall belong exclusively to vendor.", "Aggressive IP & Feedback Expropriation"),
    ("Customer waives all moral rights and grants company unencumbered ownership of all data workflows and prompt engineering outputs.", "Aggressive IP & Feedback Expropriation"),
    ("Any concept, idea, or technique submitted by customer becomes company property free of any royalty or attribution obligation.", "Aggressive IP & Feedback Expropriation"),

    # -------------------------------------------------------------
    # 5. PERPETUAL DATA & AI HARVESTING
    # -------------------------------------------------------------
    ("We process your voice input, location, and telemetry in the cloud to improve our services and train machine learning models.", "Perpetual AI Training & Data Monetization"),
    ("Company retains perpetual rights to ingest user documents, prompts, and confidential data to train commercial AI and LLM algorithms.", "Perpetual AI Training & Data Monetization"),
    ("You grant vendor an irrevocable license to aggregate, de-identify, and utilize customer content to develop generative AI models.", "Perpetual AI Training & Data Monetization"),
    ("User content may be analyzed, processed, and utilized to train neural networks and machine learning capabilities of vendor.", "Perpetual AI Training & Data Monetization"),
    ("App permissions grant provider continuous access to read, scrape, and collect your private contacts list, photo gallery, and microphone.", "Perpetual AI Training & Data Monetization"),
    ("Customer data may be incorporated into generalized algorithms and used to train third-party artificial intelligence models.", "Perpetual AI Training & Data Monetization"),
    ("Voice recordings and usage data are stored on servers outside your country to train natural language processing systems.", "Perpetual AI Training & Data Monetization"),
    ("Vendor may evaluate and fine-tune proprietary neural networks using confidential customer submissions and database records.", "Perpetual AI Training & Data Monetization"),

    # -------------------------------------------------------------
    # 6. HIDDEN AUTO-RENEWAL & TRAPPED TERMINATION
    # -------------------------------------------------------------
    ("This agreement automatically renews for successive multi-year periods unless cancelled 90 days prior via certified postal mail.", "Hidden Auto-Renewal & Trapped Termination"),
    ("All fees paid are strictly non-refundable under any circumstances and no partial refunds or credits will be provided.", "Hidden Auto-Renewal & Trapped Termination"),
    ("Your rights under this Agreement will automatically terminate without notice if you fail to comply with any of its terms.", "Hidden Auto-Renewal & Trapped Termination"),
    ("User authorizes recurring automatic debits and NACH bank mandates without further authorization or advance renewal notice.", "Hidden Auto-Renewal & Trapped Termination"),
    ("Subscription extends automatically for additional 12-month terms and early termination incurs liquidated damages of all remaining fees.", "Hidden Auto-Renewal & Trapped Termination"),
    ("Agreement constitutes a non-cancellable bank loan mandate with auto-debit authority through third-party NBFC finance partners.", "Hidden Auto-Renewal & Trapped Termination"),
    ("Cancellation requests must be submitted in writing via registered post at least 60 days prior to the annual renewal date.", "Hidden Auto-Renewal & Trapped Termination"),

    # -------------------------------------------------------------
    # 7. OVERBROAD NON-COMPETE & LOCKOUT
    # -------------------------------------------------------------
    ("Employee shall not directly or indirectly engage in any competing business worldwide for a period of 3 years following termination.", "Overbroad Non-Compete & Lockout"),
    ("Worker is prohibited from working for or consulting with any entity operating in the same industry anywhere in the world.", "Overbroad Non-Compete & Lockout"),
    ("Contractor covenants not to compete with company or provide similar digital services for 24 months post separation.", "Overbroad Non-Compete & Lockout"),
    ("Worldwide non-compete restriction on future employment or business ventures across all current and planned company domains.", "Overbroad Non-Compete & Lockout"),
    ("You shall not develop, market, or offer any competing software or services in any geographic territory for 2 years.", "Overbroad Non-Compete & Lockout"),
    ("Executive agrees not to engage in any competitive enterprise globally for thirty-six months following cessation of employment.", "Overbroad Non-Compete & Lockout"),

    # -------------------------------------------------------------
    # 8. COMPLETE LIABILITY GUTTING & AS-IS TRAP
    # -------------------------------------------------------------
    ("In no event will our aggregate liability with respect to any claim exceed fifty dollars ($50.00) or the amount of $0.", "Complete Liability Gutting & As-Is Trap"),
    ("Under no circumstances shall company total liability exceed fifty dollars ($50) or one hundred dollars ($100).", "Complete Liability Gutting & As-Is Trap"),
    ("Software is provided strictly 'as is' and 'as available' with all faults and company disclaims all express and implied warranties.", "Complete Liability Gutting & As-Is Trap"),
    ("Vendor disclaims all liability for data loss, server outage, security breaches, or unauthorized access to customer files.", "Complete Liability Gutting & As-Is Trap"),
    ("Total cumulative liability of provider shall be limited to the amount paid by you in the preceding one month.", "Complete Liability Gutting & As-Is Trap"),
    ("Company has no responsibility or liability for any aspect of products or third-party integrations under any legal theory.", "Complete Liability Gutting & As-Is Trap"),
    ("Under no circumstances shall vendor be liable for any direct, indirect, incidental, special, or consequential damages.", "Complete Liability Gutting & As-Is Trap"),

    # -------------------------------------------------------------
    # 9. SAFE / BALANCED COMMERCIAL CLAUSES (NEGATIVE CLASS)
    # -------------------------------------------------------------
    ("Each party agrees to defend, indemnify, and hold harmless the other party from third-party claims arising from IP infringement, capped at 12 months fees.", "Safe / Balanced Standard"),
    ("Neither party may modify this Agreement without a mutual written amendment signed by authorized representatives of both parties.", "Safe / Balanced Standard"),
    ("Vendor shall provide at least thirty (30) days prior written notice for any material modifications, with right to terminate for a pro-rata refund.", "Safe / Balanced Standard"),
    ("Customer retains all right, title, and interest in and to Customer Data. Vendor shall NOT use Customer Data to train artificial intelligence models.", "Safe / Balanced Standard"),
    ("Vendor maintains a strict zero-data-retention policy and isolates customer information in secure enterprise tenants.", "Safe / Balanced Standard"),
    ("Either party may terminate this agreement upon thirty (30) days written notice or via the self-service online account console.", "Safe / Balanced Standard"),
    ("In the event of cancellation, customer shall receive a pro-rata refund for any unused prepaid subscription period.", "Safe / Balanced Standard"),
    ("Each party's aggregate liability under this Agreement shall be limited to the total fees paid or payable in the twelve (12) months preceding the claim.", "Safe / Balanced Standard"),
    ("Liability cap shall not apply to breaches of confidentiality, gross negligence, willful misconduct, or data security breaches.", "Safe / Balanced Standard"),
    ("Any controversy shall first be submitted to senior executives for good-faith resolution, preserving all court rights and small-claims access.", "Safe / Balanced Standard"),
    ("This agreement is governed by the laws of California and disputes may be brought in courts of competent jurisdiction.", "Safe / Balanced Standard"),
    ("Vendor warrants that the cloud software will perform in material conformity with documentation and maintains 99.9% uptime SLA.", "Safe / Balanced Standard"),
    ("Confidential information shall be kept strictly confidential and used solely to the extent necessary to perform services under this agreement.", "Safe / Balanced Standard"),
    ("Free worker mobility is preserved; non-compete is limited solely to non-solicitation of key personnel in accordance with FTC rules.", "Safe / Balanced Standard"),
]
