const { useState, useEffect, useRef } = React;

// Sample Pre-loaded Contracts for Quick Testing
const SAMPLE_CONTRACTS = {
  predatory_saas: {
    name: "Predatory SaaS Terms of Service",
    description: "Contains unilateral termination, $50 liability cap, forced arbitration, AI training, and trapped auto-renewals.",
    text: `1. UNILATERAL MODIFICATIONS
The Provider reserves the right to modify these Terms, pricing, and service levels at any time in its sole discretion without prior notice to Customer. Continued use constitutes binding acceptance.

2. TERMINATION AT WILL
The Provider may immediately terminate this Agreement and suspend user accounts at will at any time without cause, notice, liability, or explanation.

3. EXTREME LIMITATION OF LIABILITY
To the maximum extent permitted by law, Provider's total aggregate liability under this Agreement shall be capped at $50.00. Provider disclaims all liability for data loss, downtime, or indirect damages under all theories.

4. ASYMMETRIC INDEMNIFICATION
Customer agrees to defend, indemnify, and hold harmless Provider from all third-party claims, legal fees, and regulatory penalties arising from Customer's use of the platform.

5. AI MODEL TRAINING & IP EXPROPRIATION
Customer grants Provider a perpetual, irrevocable, worldwide, royalty-free license to use, reproduce, modify, and train commercial AI models and machine learning algorithms on all Customer Data.

6. TRAPPED AUTOMATIC RENEWAL
This subscription renews automatically perpetually at standard rates. Cancellation requires 90 days prior written notice sent exclusively via certified physical postal mail.

7. FORCED ARBITRATION & CLASS ACTION WAIVER
All disputes must be resolved solely through confidential binding individual arbitration. Customer explicitly waives all rights to a jury trial or to participate in any class action lawsuit.

8. DISCLAIMER OF WARRANTIES
The Service is provided strictly 'AS IS' and 'AS AVAILABLE' with all faults, and Provider disclaims all express or implied warranties including merchantability and fitness.`
  },
  fair_standard_nda: {
    name: "Standard Mutual NDA (Balanced Benchmark)",
    description: "Bilateral confidentiality obligations, mutual 30-day notice, and standard exceptions.",
    text: `1. DEFINITION OF CONFIDENTIAL INFORMATION
Confidential Information includes all non-public technical, business, or financial information disclosed by either party to the other party that is designated as confidential or should reasonably be understood to be confidential.

2. STANDARD EXCLUSIONS
Confidential Information shall not include information that is publicly known, already known to recipient prior to disclosure, or independently developed without reference to the disclosing party's information.

3. MUTUAL CONFIDENTIALITY OBLIGATIONS
Each party agrees to hold the other party's Confidential Information in strict confidence and use the same degree of care as for its own proprietary information, but in no event less than reasonable care.

4. TERM AND SURVIVAL
This Agreement shall remain in effect for one (1) year. All confidentiality obligations shall survive the expiration or termination of this Agreement for a period of three (3) years.

5. TERMINATION UPON NOTICE
Either party may terminate this Agreement upon thirty (30) days' prior written notice to the other party for any reason.

6. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflicts of law principles.`
  },
  unbalanced_employment: {
    name: "Unbalanced Contractor / Employment Terms",
    description: "Includes overbroad worldwide 5-year non-compete and unilateral IP expropriation.",
    text: `1. INTELLECTUAL PROPERTY ASSIGNMENT
All feedback, modifications, inventions, algorithms, and derivative works created by Contractor during the term shall become the sole exclusive property of Vendor worldwide.

2. OVERBROAD RESTRICTIVE COVENANT
Contractor agrees not to engage in or advise any technology business worldwide in any capacity for a period of five (5) years following termination of services.

3. IMMEDIATE TERMINATION FOR CONVENIENCE
Company reserves the right to terminate Contractor's engagement immediately without notice and without payment of pending milestone invoices.

4. NON-REFUNDABLE FEES
All advance fees paid to Contractor shall be immediately refunded to Company upon demand, while Contractor retains no right to claim unearned milestone fees.`
  }
};

function App() {
  const [activeTab, setActiveTab] = useState("input");
  const [contractText, setContractText] = useState(SAMPLE_CONTRACTS.predatory_saas.text);
  const [selectedSampleKey, setSelectedSampleKey] = useState("predatory_saas");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [nlpAnalysisData, setNlpAnalysisData] = useState(null);
  const [tfidfData, setTfidfData] = useState(null);
  const [mlEvalData, setMlEvalData] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  // Filter states for Results tab
  const [selectedCategoryFilter, setSelectedCategoryFilter] = useState("ALL");
  const [selectedRiskFilter, setSelectedRiskFilter] = useState("ALL");
  const [searchFilter, setSearchFilter] = useState("");

  // Semantic Comparator state
  const [semanticClauseA, setSemanticClauseA] = useState("The provider may terminate the agreement without notice.");
  const [semanticClauseB, setSemanticClauseB] = useState("The service provider can end the contract immediately without providing prior notification.");
  const [semanticCompareResult, setSemanticCompareResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);

  // Load ML evaluation on mount
  useEffect(() => {
    fetch("/api/ml/evaluation")
      .then(res => res.json())
      .then(data => setMlEvalData(data))
      .catch(err => console.error("Error loading ML evaluation:", err));
  }, []);

  // Handle Sample Preset Selection
  const handleSampleChange = (key) => {
    setSelectedSampleKey(key);
    if (SAMPLE_CONTRACTS[key]) {
      setContractText(SAMPLE_CONTRACTS[key].text);
    }
  };

  // Handle File Upload (PDF, DOCX, TXT)
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setErrorMsg("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/document/extract", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to extract document text");
      }

      const data = await res.json();
      setContractText(data.text || "");
      setSelectedSampleKey("custom");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Run Complete Audit Pipeline
  const runFullAnalysis = async () => {
    if (!contractText || !contractText.strip ? contractText.trim().length === 0 : false) {
      setErrorMsg("Please paste contract text or upload a document.");
      return;
    }

    setIsAnalyzing(true);
    setErrorMsg("");

    try {
      // 1. Run Contract Risk Audit
      const riskRes = await fetch("/api/nlp/risk/audit-contract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: contractText })
      });
      if (!riskRes.ok) throw new Error("Failed to execute Contract Risk Audit");
      const riskData = await riskRes.json();
      setAuditResult(riskData);

      // 2. Run NLP Foundation Pipeline
      const nlpRes = await fetch("/api/nlp/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: contractText })
      });
      if (nlpRes.ok) {
        const nlpData = await nlpRes.json();
        setNlpAnalysisData(nlpData);
      }

      // 3. Run TF-IDF Corpus Analysis
      const tfidfRes = await fetch("/api/nlp/tfidf/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contract_text: contractText })
      });
      if (tfidfRes.ok) {
        const tfData = await tfidfRes.json();
        setTfidfData(tfData);
      }

      // Switch to Results Tab
      setActiveTab("results");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run 2-Clause Semantic Comparison
  const handleRunSemanticComparison = async () => {
    setIsComparing(true);
    try {
      const res = await fetch("/api/nlp/semantic/similarity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clause_a: semanticClauseA,
          clause_b: semanticClauseB
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSemanticCompareResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsComparing(false);
    }
  };

  // Filter clauses
  const filteredClauses = (auditResult && auditResult.clauses) ? auditResult.clauses.filter(c => {
    if (selectedCategoryFilter !== "ALL" && c.category !== selectedCategoryFilter) return false;
    if (selectedRiskFilter !== "ALL" && c.risk_level !== selectedRiskFilter) return false;
    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      return c.text.toLowerCase().includes(q) || c.category.toLowerCase().includes(q) || c.title.toLowerCase().includes(q);
    }
    return true;
  }) : [];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header / Nav */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
              <i className="fa-solid fa-scale-balanced text-white text-lg"></i>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-extrabold tracking-tight">Lexi<span className="text-sky-400">Trap</span></span>
                <span className="text-xs bg-sky-500/10 text-sky-400 border border-sky-500/20 px-2 py-0.5 rounded-full font-mono">NLP & ML Auditor</span>
              </div>
              <p className="text-xs text-slate-400">MCA Academic Project • Contract Risk & Trap-Clause NLP Pipeline</p>
            </div>
          </div>

          {/* Tab Navigation */}
          <nav className="flex items-center space-x-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab("input")}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "input" ? "bg-sky-500 text-white shadow-md shadow-sky-500/20" : "text-slate-400 hover:text-white"
              }`}
            >
              <i className="fa-solid fa-file-contract mr-1.5"></i> Contract Input
            </button>
            <button
              onClick={() => setActiveTab("results")}
              disabled={!auditResult}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "results"
                  ? "bg-sky-500 text-white shadow-md shadow-sky-500/20"
                  : !auditResult ? "text-slate-600 cursor-not-allowed" : "text-slate-400 hover:text-white"
              }`}
            >
              <i className="fa-solid fa-shield-halved mr-1.5"></i> Risk Results
            </button>
            <button
              onClick={() => setActiveTab("nlp")}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "nlp" ? "bg-sky-500 text-white shadow-md shadow-sky-500/20" : "text-slate-400 hover:text-white"
              }`}
            >
              <i className="fa-solid fa-brain mr-1.5"></i> NLP Analysis
            </button>
            <button
              onClick={() => setActiveTab("models")}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "models" ? "bg-sky-500 text-white shadow-md shadow-sky-500/20" : "text-slate-400 hover:text-white"
              }`}
            >
              <i className="fa-solid fa-chart-line mr-1.5"></i> ML Evaluation
            </button>
            <button
              onClick={() => setActiveTab("viva")}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "viva" ? "bg-sky-500 text-white shadow-md shadow-sky-500/20" : "text-slate-400 hover:text-white"
              }`}
            >
              <i className="fa-solid fa-graduation-cap mr-1.5"></i> Viva Guide
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Error Alert */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <i className="fa-solid fa-triangle-exclamation"></i>
              <span>{errorMsg}</span>
            </div>
            <button onClick={() => setErrorMsg("")} className="text-red-400 hover:text-white">
              <i className="fa-solid fa-xmark"></i>
            </button>
          </div>
        )}

        {/* TAB 1: INPUT & INGESTION */}
        {activeTab === "input" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="glass-panel p-6 rounded-2xl">
              <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                <div>
                  <h2 className="text-xl font-bold text-white flex items-center">
                    <i className="fa-solid fa-cloud-arrow-up text-sky-400 mr-2"></i> Contract Document Ingestion
                  </h2>
                  <p className="text-sm text-slate-400">Paste contract text or upload PDF / DOCX / TXT documents for NLP extraction.</p>
                </div>
                
                {/* Sample Selector */}
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-400 font-medium">Load Sample:</span>
                  <select
                    value={selectedSampleKey}
                    onChange={(e) => handleSampleChange(e.target.value)}
                    className="bg-slate-900 text-xs border border-slate-700 text-sky-400 rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
                  >
                    <option value="predatory_saas">Predatory SaaS Terms</option>
                    <option value="fair_standard_nda">Fair Standard NDA</option>
                    <option value="unbalanced_employment">Unbalanced Contractor Agreement</option>
                    <option value="custom">Custom Input</option>
                  </select>
                </div>
              </div>

              {/* Upload Zone */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <label className="md:col-span-1 border-2 border-dashed border-slate-700 hover:border-sky-500 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-900/40 group">
                  <i className="fa-solid fa-file-pdf text-2xl text-slate-500 group-hover:text-sky-400 mb-2 transition-colors"></i>
                  <span className="text-xs font-semibold text-slate-300">Upload PDF / DOCX / TXT</span>
                  <span className="text-[10px] text-slate-500 mt-1">Extracts via PyMuPDF / OpenXML</span>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>

                <div className="md:col-span-3">
                  <textarea
                    value={contractText}
                    onChange={(e) => {
                      setContractText(e.target.value);
                      setSelectedSampleKey("custom");
                    }}
                    rows="12"
                    placeholder="Paste full contract or individual clauses here..."
                    className="w-full bg-slate-950/80 border border-slate-800 rounded-xl p-4 text-xs font-mono leading-relaxed text-slate-200 focus:outline-none focus:border-sky-500 custom-scrollbar"
                  ></textarea>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2">
                <div className="text-xs text-slate-400 font-mono">
                  Length: {contractText.length} characters | ~{contractText.split(/\s+/).filter(Boolean).length} words
                </div>
                <button
                  onClick={runFullAnalysis}
                  disabled={isAnalyzing || isUploading}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-sky-500/25 flex items-center space-x-2 transition-all disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <i className="fa-solid fa-spinner fa-spin"></i>
                      <span>Auditing via NLP Pipeline...</span>
                    </>
                  ) : (
                    <>
                      <i className="fa-solid fa-wand-magic-sparkles"></i>
                      <span>Run Complete NLP Audit</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Educational Pipeline Banner */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="glass-panel p-4 rounded-xl border-l-4 border-l-sky-500">
                <div className="text-xs text-sky-400 font-bold mb-1">STEP 1: Preprocessing & POS</div>
                <p className="text-[11px] text-slate-400">Tokenization, Lemmatization, Deontic Modals (*shall, may, must*), and Legal Stopword Semantics.</p>
              </div>
              <div className="glass-panel p-4 rounded-xl border-l-4 border-l-indigo-500">
                <div className="text-xs text-indigo-400 font-bold mb-1">STEP 2: Clause Segmentation</div>
                <p className="text-[11px] text-slate-400">Hierarchical boundary detection splitting contract text into 16 standardized legal categories.</p>
              </div>
              <div className="glass-panel p-4 rounded-xl border-l-4 border-l-purple-500">
                <div className="text-xs text-purple-400 font-bold mb-1">STEP 3: ML Classification</div>
                <p className="text-[11px] text-slate-400">Sublinear TF-IDF vectors with Logistic Regression & Linear SVM ensemble classification.</p>
              </div>
              <div className="glass-panel p-4 rounded-xl border-l-4 border-l-pink-500">
                <div className="text-xs text-pink-400 font-bold mb-1">STEP 4: Risk & Semantic NLP</div>
                <p className="text-[11px] text-slate-400">Linguistic trap scoring (0–100), sentence transformer cosine similarity, and balanced rewrites.</p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: AUDIT RESULTS DASHBOARD */}
        {activeTab === "results" && auditResult && (
          <div className="space-y-6 animate-fadeIn">
            {/* Top Metrics Banner */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {/* Overall Score */}
              <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between md:col-span-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Overall Contract Health</span>
                  <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                    auditResult.summary.average_risk_score >= 60 ? "bg-red-500/20 text-red-400 border border-red-500/30" :
                    auditResult.summary.average_risk_score >= 35 ? "bg-amber-500/20 text-amber-400 border border-amber-500/30" :
                    "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  }`}>
                    {auditResult.summary.overall_grade}
                  </span>
                </div>
                <div className="my-4 flex items-baseline space-x-3">
                  <span className="text-4xl font-extrabold text-white font-mono">{auditResult.summary.average_risk_score}</span>
                  <span className="text-xs text-slate-400">/ 100 Avg Risk Score</span>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <p className="text-xs text-slate-300 leading-relaxed max-w-[70%]">{auditResult.summary.overall_status}</p>
                  <div className="flex space-x-2">
                    <button
                      onClick={async () => {
                        const res = await fetch("/api/analysis/report/pdf", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ audit_data: auditResult, nlp_stats: nlpAnalysisData })
                        });
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "LexiTrap_Audit_Report.pdf";
                        a.click();
                      }}
                      className="px-2.5 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 rounded-lg text-xs font-semibold flex items-center space-x-1"
                      title="Download PDF Audit Report"
                    >
                      <i className="fa-solid fa-file-pdf"></i>
                      <span>PDF</span>
                    </button>
                    <button
                      onClick={async () => {
                        const res = await fetch("/api/analysis/report/markdown", {
                          method: "POST",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ audit_data: auditResult, nlp_stats: nlpAnalysisData })
                        });
                        const blob = await res.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "LexiTrap_Audit_Report.md";
                        a.click();
                      }}
                      className="px-2.5 py-1.5 bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/40 rounded-lg text-xs font-semibold flex items-center space-x-1"
                      title="Download Markdown Report"
                    >
                      <i className="fa-solid fa-file-code"></i>
                      <span>MD</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Counts */}
              <div className="glass-panel p-4 rounded-2xl flex flex-col justify-between">
                <div className="text-xs text-slate-400 font-semibold">Total Clauses</div>
                <div className="text-3xl font-extrabold text-white font-mono">{auditResult.summary.total_clauses}</div>
                <div className="text-[11px] text-sky-400 font-medium">Decomposed units</div>
              </div>

              <div className="glass-panel p-4 rounded-2xl flex flex-col justify-between border-l-4 border-l-red-500">
                <div className="text-xs text-slate-400 font-semibold">Critical Traps</div>
                <div className="text-3xl font-extrabold text-red-400 font-mono">{auditResult.summary.risk_distribution.CRITICAL}</div>
                <div className="text-[11px] text-red-400/80 font-medium">Score 75–100</div>
              </div>

              <div className="glass-panel p-4 rounded-2xl flex flex-col justify-between border-l-4 border-l-amber-500">
                <div className="text-xs text-slate-400 font-semibold">High / Medium</div>
                <div className="text-3xl font-extrabold text-amber-400 font-mono">
                  {auditResult.summary.risk_distribution.HIGH + auditResult.summary.risk_distribution.MEDIUM}
                </div>
                <div className="text-[11px] text-amber-400/80 font-medium">Requires review</div>
              </div>
            </div>

            {/* Filter Bar */}
            <div className="glass-panel p-4 rounded-xl flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-3">
                {/* Category Filter */}
                <select
                  value={selectedCategoryFilter}
                  onChange={(e) => setSelectedCategoryFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
                >
                  <option value="ALL">All Categories</option>
                  {Array.from(new Set(auditResult.clauses.map(c => c.category))).sort().map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>

                {/* Risk Filter */}
                <select
                  value={selectedRiskFilter}
                  onChange={(e) => setSelectedRiskFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-sky-500"
                >
                  <option value="ALL">All Risk Levels</option>
                  <option value="CRITICAL">Critical Only</option>
                  <option value="HIGH">High Only</option>
                  <option value="MEDIUM">Medium Only</option>
                  <option value="LOW">Low / Safe Only</option>
                </select>
              </div>

              {/* Search */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search clause text..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg pl-8 pr-3 py-1.5 focus:outline-none focus:border-sky-500 w-48"
                />
                <i className="fa-solid fa-magnifying-glass absolute left-2.5 top-2.5 text-slate-500 text-xs"></i>
              </div>
            </div>

            {/* Clause Cards List */}
            <div className="space-y-4">
              {filteredClauses.map((clause) => (
                <div
                  key={clause.clause_id}
                  className={`glass-panel p-5 rounded-2xl border transition-all ${
                    clause.risk_level === "CRITICAL" ? "border-red-500/30 bg-red-950/10" :
                    clause.risk_level === "HIGH" ? "border-amber-500/30 bg-amber-950/10" :
                    clause.risk_level === "MEDIUM" ? "border-yellow-500/20 bg-yellow-950/5" :
                    "border-slate-800"
                  }`}
                >
                  {/* Card Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded">
                        {clause.section_number ? `Section ${clause.section_number}` : `Clause ${clause.clause_number}`}
                      </span>
                      <span className="text-xs font-bold text-white">{clause.title}</span>
                      <span className="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full">
                        {clause.category}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        clause.symmetry === "MUTUAL" ? "bg-emerald-500/20 text-emerald-400" :
                        clause.symmetry === "UNILATERAL" ? "bg-purple-500/20 text-purple-400" :
                        "bg-slate-800 text-slate-400"
                      }`}>
                        {clause.symmetry}
                      </span>
                      <span className={`text-xs font-bold font-mono px-2.5 py-0.5 rounded-full ${
                        clause.risk_level === "CRITICAL" ? "bg-red-500 text-white" :
                        clause.risk_level === "HIGH" ? "bg-amber-500 text-slate-950" :
                        clause.risk_level === "MEDIUM" ? "bg-yellow-500 text-slate-950" :
                        "bg-emerald-500 text-white"
                      }`}>
                        {clause.risk_score}/100 • {clause.risk_level}
                      </span>
                    </div>
                  </div>

                  {/* Clause Body Text */}
                  <p className="text-xs text-slate-200 font-mono bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 leading-relaxed mb-4">
                    {clause.text}
                  </p>

                  {/* Signals & Ledger */}
                  {clause.risk_signals && clause.risk_signals.length > 0 && (
                    <div className="mb-3 space-y-1.5">
                      <span className="text-[11px] font-bold text-red-400 uppercase tracking-wider">Detected Risk Indicators:</span>
                      <div className="flex flex-wrap gap-2">
                        {clause.risk_signals.map((sig, sIdx) => (
                          <span key={sIdx} className="text-[11px] bg-red-500/10 text-red-300 border border-red-500/20 px-2 py-0.5 rounded-md flex items-center space-x-1">
                            <i className="fa-solid fa-triangle-exclamation text-[10px]"></i>
                            <span>{sig.factor_name} ({sig.score_impact > 0 ? `+${sig.score_impact}` : sig.score_impact} pts)</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Explanation & Recommendation */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3 text-xs">
                    <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                      <span className="font-bold text-slate-300 block mb-1">
                        <i className="fa-solid fa-circle-info text-sky-400 mr-1"></i> NLP Audit Analysis:
                      </span>
                      <p className="text-slate-400 leading-relaxed text-[11px]">{clause.explanation}</p>
                    </div>

                    <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                      <span className="font-bold text-slate-300 block mb-1">
                        <i className="fa-solid fa-lightbulb text-amber-400 mr-1"></i> Negotiation Talking Point:
                      </span>
                      <p className="text-slate-400 leading-relaxed text-[11px]">{clause.recommendation}</p>
                    </div>
                  </div>

                  {/* AI Suggested Balanced Rewrite */}
                  {clause.suggested_rewrite && (
                    <div className="bg-emerald-950/20 border border-emerald-500/30 p-3.5 rounded-xl text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <span className="text-emerald-400 font-bold flex items-center">
                          <i className="fa-solid fa-arrows-rotate mr-1.5"></i> Suggested Balanced Alternative:
                        </span>
                        <span className="text-[10px] text-emerald-400/70 font-mono">Not Legal Advice</span>
                      </div>
                      <p className="text-emerald-200/90 font-mono text-[11px] leading-relaxed">
                        {clause.suggested_rewrite.suggested_balanced_clause}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: NLP DEEP ANALYSIS DASHBOARD (Step 20 Core Academic Demo) */}
        {activeTab === "nlp" && (
          <div className="space-y-6 animate-fadeIn">
            {/* Top Text Statistics Cards */}
            {nlpAnalysisData && nlpAnalysisData.statistics && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="glass-panel p-4 rounded-2xl">
                  <div className="text-xs text-slate-400 font-semibold">Characters</div>
                  <div className="text-2xl font-extrabold text-white font-mono">{nlpAnalysisData.statistics.character_count}</div>
                </div>
                <div className="glass-panel p-4 rounded-2xl">
                  <div className="text-xs text-slate-400 font-semibold">Words</div>
                  <div className="text-2xl font-extrabold text-sky-400 font-mono">{nlpAnalysisData.statistics.word_count}</div>
                </div>
                <div className="glass-panel p-4 rounded-2xl">
                  <div className="text-xs text-slate-400 font-semibold">Sentences</div>
                  <div className="text-2xl font-extrabold text-indigo-400 font-mono">{nlpAnalysisData.statistics.sentence_count}</div>
                </div>
                <div className="glass-panel p-4 rounded-2xl">
                  <div className="text-xs text-slate-400 font-semibold">Avg Words / Sent</div>
                  <div className="text-2xl font-extrabold text-purple-400 font-mono">{nlpAnalysisData.statistics.average_sentence_length_words}</div>
                </div>
                <div className="glass-panel p-4 rounded-2xl">
                  <div className="text-xs text-slate-400 font-semibold">Modal Verbs</div>
                  <div className="text-2xl font-extrabold text-pink-400 font-mono">{nlpAnalysisData.modal_verbs ? nlpAnalysisData.modal_verbs.length : 0}</div>
                </div>
              </div>
            )}

            {/* Academic Stopword Handling Explanation Card */}
            {nlpAnalysisData && (
              <div className="glass-panel p-5 rounded-2xl border-l-4 border-l-sky-500">
                <h3 className="text-sm font-bold text-white mb-1 flex items-center">
                  <i className="fa-solid fa-filter text-sky-400 mr-2"></i> Stopword Semantics in Legal NLP
                </h3>
                <p className="text-xs text-slate-300 mb-3">{nlpAnalysisData.stopword_academic_note}</p>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs text-slate-400 font-semibold">Preserved Legal Keywords:</span>
                  {nlpAnalysisData.preserved_legal_keywords && nlpAnalysisData.preserved_legal_keywords.map((kw, idx) => (
                    <span key={idx} className="text-xs bg-sky-500/20 text-sky-300 border border-sky-500/30 px-2 py-0.5 rounded font-mono">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Interactive Token & Lemma Table */}
            {nlpAnalysisData && nlpAnalysisData.lemmas && (
              <div className="glass-panel p-5 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-3 flex items-center">
                  <i className="fa-solid fa-list-ol text-indigo-400 mr-2"></i> Tokenization, Morphological Lemmatization & POS Tags
                </h3>
                <div className="max-h-60 overflow-y-auto custom-scrollbar border border-slate-800 rounded-xl">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-900 sticky top-0 text-slate-400 font-semibold">
                      <tr>
                        <th className="p-2.5">Original Token</th>
                        <th className="p-2.5">Canonical Lemma</th>
                        <th className="p-2.5">POS Tag</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 font-mono">
                      {nlpAnalysisData.lemmas.slice(0, 40).map((lem, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/50">
                          <td className="p-2.5 text-white">{lem.token}</td>
                          <td className="p-2.5 text-sky-400">{lem.lemma}</td>
                          <td className="p-2.5">
                            <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded text-[10px]">
                              {lem.pos}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Named Entity Recognition (NER) */}
            {nlpAnalysisData && nlpAnalysisData.entities && (
              <div className="glass-panel p-5 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-3 flex items-center">
                  <i className="fa-solid fa-tags text-purple-400 mr-2"></i> Contractual Named Entity Recognition (NER)
                </h3>
                <div className="flex flex-wrap gap-2.5">
                  {nlpAnalysisData.entities.length > 0 ? (
                    nlpAnalysisData.entities.map((ent, eIdx) => (
                      <div key={eIdx} className="bg-slate-900 border border-slate-800 p-2.5 rounded-xl flex items-center space-x-2 text-xs">
                        <span className="font-mono text-white font-semibold">{ent.text}</span>
                        <span className="bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] px-2 py-0.5 rounded font-bold">
                          {ent.label}
                        </span>
                        <span className="text-[10px] text-slate-500">{ent.explanation}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">No specific named entities detected in current snippet.</span>
                  )}
                </div>
              </div>
            )}

            {/* TF-IDF Academic Explorer */}
            {tfidfData && tfidfData.academic_theory && (
              <div className="glass-panel p-5 rounded-2xl">
                <h3 className="text-sm font-bold text-white mb-2 flex items-center">
                  <i className="fa-solid fa-square-root-variable text-pink-400 mr-2"></i> TF-IDF Feature Extraction & Mathematical Traces
                </h3>
                <p className="text-xs text-slate-300 mb-4">{tfidfData.academic_theory.contract_relevance}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Top Corpus Features */}
                  <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                    <span className="text-xs font-bold text-slate-300 block mb-2">Top Corpus Discriminative Keywords:</span>
                    <div className="flex flex-wrap gap-2">
                      {tfidfData.corpus_top_features.map((feat, fIdx) => (
                        <span key={fIdx} className="text-xs bg-slate-800 border border-slate-700 px-2 py-1 rounded-md text-sky-300 font-mono">
                          {feat.term} <span className="text-[10px] text-slate-500">({feat.mean_tfidf})</span>
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Mathematical Trace Example */}
                  <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                    <span className="text-xs font-bold text-slate-300 block mb-2">Mathematical Viva Trace Example:</span>
                    {tfidfData.clause_level_analysis && tfidfData.clause_level_analysis[0] && tfidfData.clause_level_analysis[0].top_terms[0] ? (
                      <div className="text-xs font-mono text-emerald-400 bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                        {tfidfData.clause_level_analysis[0].top_terms[0].formula_trace}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500">Run audit to generate traces.</span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Live Semantic 2-Clause Comparator */}
            <div className="glass-panel p-5 rounded-2xl">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center">
                <i className="fa-solid fa-code-compare text-emerald-400 mr-2"></i> Live Semantic Paraphrase & Imbalance Comparator (Steps 16 & 17)
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Demonstrates Sentence Transformers cosine similarity across paraphrased clauses with differing vocabulary.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="text-xs text-slate-400 font-semibold block mb-1">Clause A:</label>
                  <textarea
                    value={semanticClauseA}
                    onChange={(e) => setSemanticClauseA(e.target.value)}
                    rows="3"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200"
                  ></textarea>
                </div>
                <div>
                  <label className="text-xs text-slate-400 font-semibold block mb-1">Clause B:</label>
                  <textarea
                    value={semanticClauseB}
                    onChange={(e) => setSemanticClauseB(e.target.value)}
                    rows="3"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200"
                  ></textarea>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={handleRunSemanticComparison}
                  disabled={isComparing}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-all"
                >
                  {isComparing ? "Comparing Dense Vectors..." : "Calculate Semantic Similarity"}
                </button>
              </div>

              {/* Comparison Output */}
              {semanticCompareResult && (
                <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400 font-semibold">Semantic Cosine Similarity:</span>
                    <span className="text-lg font-bold font-mono text-emerald-400">
                      {semanticCompareResult.semantic_similarity_percentage}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 font-medium">{semanticCompareResult.semantic_verdict}</p>
                  {semanticCompareResult.potential_imbalance_detected && (
                    <div className="mt-2 text-xs bg-amber-500/10 border border-amber-500/30 p-2.5 rounded-lg text-amber-300 space-y-1">
                      <span className="font-bold flex items-center">
                        <i className="fa-solid fa-triangle-exclamation mr-1.5"></i> Imbalance Detected:
                      </span>
                      {semanticCompareResult.imbalance_findings.map((finding, idx) => (
                        <p key={idx} className="text-[11px] text-amber-200/90">{finding}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: ML MODEL EVALUATION (Step 26) */}
        {activeTab === "models" && mlEvalData && (
          <div className="space-y-6 animate-fadeIn">
            <div className="glass-panel p-6 rounded-2xl">
              <h2 className="text-xl font-bold text-white mb-2 flex items-center">
                <i className="fa-solid fa-robot text-sky-400 mr-2"></i> Machine Learning Classifier Evaluation & Comparison
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Benchmarked on 80% Training / 20% Testing split across 16 Legal Contract Categories using TF-IDF features.
              </p>

              {/* Comparative Table */}
              <div className="overflow-x-auto border border-slate-800 rounded-xl mb-6">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900 text-slate-400 font-semibold">
                    <tr>
                      <th className="p-3">Model Architecture</th>
                      <th className="p-3">Accuracy</th>
                      <th className="p-3">Precision (Weighted)</th>
                      <th className="p-3">Recall (Weighted)</th>
                      <th className="p-3">F1-Score (Weighted)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 font-mono">
                    <tr className="hover:bg-slate-900/50">
                      <td className="p-3 font-sans font-bold text-white">Model 1: TF-IDF + Multinomial Logistic Regression</td>
                      <td className="p-3 text-sky-400">{mlEvalData.model_1_logistic_regression.accuracy}</td>
                      <td className="p-3 text-slate-300">{mlEvalData.model_1_logistic_regression.precision_weighted}</td>
                      <td className="p-3 text-slate-300">{mlEvalData.model_1_logistic_regression.recall_weighted}</td>
                      <td className="p-3 text-emerald-400 font-bold">{mlEvalData.model_1_logistic_regression.f1_weighted}</td>
                    </tr>
                    <tr className="hover:bg-slate-900/50 bg-sky-500/5">
                      <td className="p-3 font-sans font-bold text-white">Model 2: TF-IDF + Linear Support Vector Machine (LinearSVC)</td>
                      <td className="p-3 text-sky-400">{mlEvalData.model_2_linear_svm.accuracy}</td>
                      <td className="p-3 text-slate-300">{mlEvalData.model_2_linear_svm.precision_weighted}</td>
                      <td className="p-3 text-slate-300">{mlEvalData.model_2_linear_svm.recall_weighted}</td>
                      <td className="p-3 text-emerald-400 font-bold">{mlEvalData.model_2_linear_svm.f1_weighted}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Academic Rationale */}
              <div className="bg-slate-900/70 p-4 rounded-xl border border-slate-800 mb-6">
                <span className="text-xs font-bold text-sky-400 block mb-1">
                  <i className="fa-solid fa-graduation-cap mr-1.5"></i> Academic Model Selection Rationale:
                </span>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {mlEvalData.comparison_summary.academic_rationale}
                </p>
              </div>

              {/* Classes List */}
              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2">Evaluated Legal Taxonomies ({mlEvalData.dataset_statistics.total_categories} Classes):</span>
                <div className="flex flex-wrap gap-2">
                  {mlEvalData.dataset_statistics.classes.map((cls, idx) => (
                    <span key={idx} className="text-xs bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md text-slate-300">
                      {cls}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: VIVA GUIDE & DOCUMENTATION (Step 28) */}
        {activeTab === "viva" && (
          <div className="space-y-6 animate-fadeIn">
            <div className="glass-panel p-6 rounded-2xl">
              <h2 className="text-xl font-bold text-white mb-2 flex items-center">
                <i className="fa-solid fa-graduation-cap text-sky-400 mr-2"></i> MCA Viva Preparation & NLP Concepts Guide
              </h2>
              <p className="text-xs text-slate-400 mb-6">
                Key questions and concise theoretical explanations to demonstrate mastery of the NLP pipeline.
              </p>

              <div className="space-y-4">
                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold text-sky-400 mb-1">Q1: Why should legal NLP not blindly remove all standard stopwords?</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Standard stopwords eliminate modal verbs (<em>shall, may, must</em>) and logical conditions (<em>not, unless, without</em>). 
                    In legal agreements, removing these alters the entire meaning: <em>"Provider may terminate without notice"</em> becomes identical to 
                    <em>"Provider shall not terminate"</em> if stopwords are stripped.
                  </p>
                </div>

                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold text-sky-400 mb-1">Q2: What is the core difference between Lemmatization and Stemming?</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Stemming applies heuristic chopping rules to remove suffixes (often producing non-words like <em>terminat-</em>), whereas 
                    Lemmatization uses morphological vocabulary and Part-of-Speech context to return the legitimate dictionary base form (<em>terminate</em>).
                  </p>
                </div>

                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold text-sky-400 mb-1">Q3: Why use TF-IDF rather than raw Bag-of-Words for clause classification?</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Raw Bag-of-Words counts give high weights to universally frequent words like <em>agreement, party, section</em>. TF-IDF applies 
                    Inverse Document Frequency (IDF) penalties to ubiquitous words while boosting discriminative terms like <em>indemnify, arbitration, liquidated damages</em>.
                  </p>
                </div>

                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold text-sky-400 mb-1">Q4: Why do Dense Sentence Embeddings outperform TF-IDF in semantic similarity?</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    TF-IDF relies on exact lexical token matching (orthogonal vectors if words differ). Sentence Transformers use deep contextual self-attention 
                    to map synonyms (<em>"end contract"</em> vs <em>"terminate agreement"</em>) into adjacent positions in continuous dense vector space.
                  </p>
                </div>

                <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
                  <h4 className="text-xs font-bold text-sky-400 mb-1">Q5: Why compare Logistic Regression and Linear SVM?</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Linear SVM maximizes the geometric margin between high-dimensional sparse TF-IDF vectors, making it robust against overfitting. 
                    Logistic Regression minimizes log-loss and generates calibrated probability distributions useful for confidence ranking.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer & Mandatory Legal Disclaimer (Step 29) */}
      <footer className="mt-auto border-t border-slate-800/80 p-6 bg-slate-950/80 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-slate-400">LexiTrap Academic NLP Engine</span> • Master of Computer Applications (MCA) Submission
          </div>
          <p className="text-[11px] text-slate-400 max-w-2xl text-center md:text-right">
            ⚖️ <strong>Academic Disclaimer:</strong> LexiTrap is an AI/NLP-based educational contract analysis system. 
            It identifies potentially noteworthy language and does not provide legal advice or guarantee that a contract is safe or enforceable. 
            Users should consult a qualified legal professional for legal advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
