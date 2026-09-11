/**
 * LexiTrap Web Application Controller (Light Theme)
 */

document.addEventListener("DOMContentLoaded", () => {
    // Input Elements
    const contractTextarea = document.getElementById("contract-text");
    const docNameInput = document.getElementById("doc-name-input");
    const charCountEl = document.getElementById("char-count");
    const wordCountEl = document.getElementById("word-count");
    const estClausesEl = document.getElementById("est-clauses");
    const auditBtn = document.getElementById("audit-btn");
    const clearBtn = document.getElementById("clear-btn");
    const loadingOverlay = document.getElementById("loading-overlay");
    const resultsSection = document.getElementById("results-section");
    const loadSampleBtns = document.querySelectorAll(".load-sample-btn");
    const exportMdBtn = document.getElementById("export-md-btn");
    const filterBtns = document.querySelectorAll(".filter-tab");

    // Results Elements
    const healthScoreVal = document.getElementById("health-score-val");
    const scoreCircle = document.getElementById("score-circle");
    const gradeBadge = document.getElementById("grade-badge");
    const riskSeverityBadge = document.getElementById("risk-severity-badge");
    const verdictTitle = document.getElementById("verdict-title");
    const verdictDesc = document.getElementById("verdict-desc");
    const statTrapsCount = document.getElementById("stat-traps-count");
    const statCriticalCount = document.getElementById("stat-critical-count");
    const statHighCount = document.getElementById("stat-high-count");
    const statClausesCount = document.getElementById("stat-clauses-count");
    const deonticBarsContainer = document.getElementById("deontic-bars-container");
    const executivePointsList = document.getElementById("executive-points-list");
    const clausesList = document.getElementById("clauses-list");

    // Filter counts
    const countAllEl = document.getElementById("count-all");
    const countTrapsEl = document.getElementById("count-traps");
    const countCriticalEl = document.getElementById("count-critical");

    let currentAuditReport = null;
    let activeFilter = "ALL";

    // Text counters
    function updateTextStats() {
        const text = contractTextarea.value;
        charCountEl.textContent = text.length.toLocaleString();
        
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCountEl.textContent = words.toLocaleString();

        const clauses = (text.match(/(?:Section|Article|Clause|\b\d+\.)/gi) || []).length || Math.max(1, Math.floor(words / 60));
        estClausesEl.textContent = text.trim() ? clauses : 0;
    }

    contractTextarea.addEventListener("input", updateTextStats);

    // Load Preset Sample
    async function loadSample(sampleId) {
        try {
            loadingOverlay.classList.remove("hidden");
            const res = await fetch(`/api/sample/${sampleId}`);
            const data = await res.json();
            if (data.status === "success") {
                contractTextarea.value = data.text;
                docNameInput.value = data.sample.name;
                updateTextStats();
                
                // Highlight active pill
                loadSampleBtns.forEach(b => b.classList.remove("active"));
                const activeBtn = document.querySelector(`.load-sample-btn[data-id="${sampleId}"]`);
                if (activeBtn) activeBtn.classList.add("active");

                // Trigger audit
                await runAudit();
            }
        } catch (err) {
            console.error("Failed to load sample:", err);
            alert("Error loading sample contract.");
        } finally {
            loadingOverlay.classList.add("hidden");
        }
    }

    loadSampleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const id = btn.getAttribute("data-id");
            loadSample(id);
        });
    });

    // Clear Button
    clearBtn.addEventListener("click", () => {
        contractTextarea.value = "";
        docNameInput.value = "";
        updateTextStats();
        resultsSection.classList.add("hidden");
        currentAuditReport = null;
        loadSampleBtns.forEach(b => b.classList.remove("active"));
    });

    // Run Audit
    async function runAudit() {
        const text = contractTextarea.value.trim();
        const docName = docNameInput.value.trim() || "Contract Agreement";

        if (!text) {
            alert("Please paste contract text or select a preset sample first.");
            return;
        }

        loadingOverlay.classList.remove("hidden");
        resultsSection.classList.add("hidden");

        try {
            const response = await fetch("/api/audit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text, name: docName }),
            });

            const data = await response.json();
            if (data.status === "success") {
                currentAuditReport = data.report;
                renderReport(data.report);
                resultsSection.classList.remove("hidden");
                resultsSection.scrollIntoView({ behavior: "smooth" });
            } else {
                alert("Audit failed: " + (data.message || "Unknown error"));
            }
        } catch (err) {
            console.error("Audit error:", err);
            alert("An error occurred while communicating with the NLP auditor.");
        } finally {
            loadingOverlay.classList.add("hidden");
        }
    }

    auditBtn.addEventListener("click", runAudit);

    // Render Full Report
    function renderReport(report) {
        const score = Math.round(report.overall_health_score);
        healthScoreVal.textContent = score;

        // Color coding for score badge & circle
        gradeBadge.textContent = `Grade ${report.letter_grade}`;
        riskSeverityBadge.textContent = report.risk_level;

        gradeBadge.className = "badge";
        riskSeverityBadge.className = "badge";
        scoreCircle.style.backgroundColor = "";
        scoreCircle.style.borderColor = "";
        healthScoreVal.style.color = "";

        if (score >= 80) {
            gradeBadge.classList.add("grade-a");
            riskSeverityBadge.classList.add("risk-safe");
            scoreCircle.style.backgroundColor = "#ecfdf5";
            scoreCircle.style.borderColor = "#a7f3d0";
            healthScoreVal.style.color = "#059669";
        } else if (score >= 60) {
            gradeBadge.classList.add("grade-b");
            riskSeverityBadge.classList.add("risk-medium");
            scoreCircle.style.backgroundColor = "#fffbeb";
            scoreCircle.style.borderColor = "#fde68a";
            healthScoreVal.style.color = "#d97706";
        } else {
            gradeBadge.classList.add("grade-f");
            riskSeverityBadge.classList.add("risk-critical");
            scoreCircle.style.backgroundColor = "#fef2f2";
            scoreCircle.style.borderColor = "#fecaca";
            healthScoreVal.style.color = "#dc2626";
        }

        verdictTitle.textContent = report.verdict_title;
        verdictDesc.textContent = report.verdict_description;

        statTrapsCount.textContent = report.total_traps_found;
        statCriticalCount.textContent = report.critical_traps_count;
        statHighCount.textContent = report.high_traps_count;
        statClausesCount.textContent = report.total_clauses;

        // Deontic Modality Progress Bars
        deonticBarsContainer.innerHTML = "";
        const deonticPcts = report.deontic_profile.distribution_percentages || {};
        const colors = {
            "Obligation": "#dc2626",
            "Prohibition": "#d97706",
            "Permission": "#2563eb",
            "Warranty": "#4f46e5",
            "Disclaimer": "#7c3aed",
            "Informational / Declarative": "#94a3b8"
        };

        for (const [cat, pct] of Object.entries(deonticPcts)) {
            const row = document.createElement("div");
            row.className = "deontic-item";
            const color = colors[cat] || "#2563eb";
            row.innerHTML = `
                <span class="deontic-label">${cat}</span>
                <div class="deontic-track">
                    <div class="deontic-fill" style="width: ${pct}%; background-color: ${color};"></div>
                </div>
                <span class="deontic-percent">${pct}%</span>
            `;
            deonticBarsContainer.appendChild(row);
        }

        // Executive Findings
        executivePointsList.innerHTML = "";
        (report.executive_summary_points || []).forEach(pt => {
            const li = document.createElement("li");
            li.textContent = pt;
            executivePointsList.appendChild(li);
        });

        // Filter Counts
        const clauses = report.clause_audit_details || [];
        countAllEl.textContent = clauses.length;
        countTrapsEl.textContent = clauses.filter(c => c.has_traps).length;
        countCriticalEl.textContent = clauses.filter(c => c.heat_level === "CRITICAL").length;

        // Render Clauses
        renderClausesList();
    }

    // Filter Buttons
    filterBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            filterBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeFilter = btn.getAttribute("data-filter");
            renderClausesList();
        });
    });

    // Render Clause Items
    function renderClausesList() {
        if (!currentAuditReport) return;
        clausesList.innerHTML = "";

        let clauses = currentAuditReport.clause_audit_details || [];
        if (activeFilter === "TRAPS") {
            clauses = clauses.filter(c => c.has_traps);
        } else if (activeFilter === "CRITICAL") {
            clauses = clauses.filter(c => c.heat_level === "CRITICAL");
        }

        if (clauses.length === 0) {
            clausesList.innerHTML = `
                <div class="clause-card" style="text-align: center; color: var(--text-muted); padding: 24px;">
                    ✓ No clauses matched this filter.
                </div>
            `;
            return;
        }

        clauses.forEach(clause => {
            const card = document.createElement("div");
            card.className = `clause-card ${clause.heat_level.toLowerCase()}`;

            let trapsHtml = "";
            if (clause.traps && clause.traps.length > 0) {
                clause.traps.forEach(trap => {
                    const dev = trap.benchmark_comparison || {};
                    const redline = (currentAuditReport.redlines || []).find(r => r.clause_id === clause.clause_id && r.trap_category === trap.category);

                    trapsHtml += `
                        <div class="trap-box">
                            <div class="trap-head">
                                <span class="trap-name">⚠️ ${trap.category}</span>
                                <span class="badge ${trap.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${trap.severity}</span>
                            </div>
                            <p class="trap-desc"><strong>Legal Risk:</strong> ${trap.legal_danger}</p>
                            <p class="trap-impact"><strong>Business Impact:</strong> ${trap.business_impact}</p>
                            <div class="trap-keywords">
                                <strong>Trigger Words:</strong> 
                                ${trap.matched_patterns.map(p => `<span>${p}</span>`).join(" ")}
                            </div>

                            ${redline ? `
                            <div class="redline-box">
                                <div class="redline-title">✏️ Recommended Balanced Alternative:</div>
                                <div class="diff-view">${redline.diff_html}</div>
                                <div class="talking-point-box">
                                    <strong>Negotiation Tip:</strong> ${redline.negotiation_talking_point}
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    `;
                });
            }

            card.innerHTML = `
                <div class="clause-card-header">
                    <div class="clause-title-group">
                        <span class="clause-id">${clause.clause_id}</span>
                        <h4 class="clause-heading">${clause.title}</h4>
                    </div>
                    <div class="clause-badge-group">
                        <span class="deontic-pill">${clause.deontic_profile.dominant_category}</span>
                        <span class="risk-pill ${clause.heat_level.toLowerCase()}">Risk ${clause.risk_score}</span>
                    </div>
                </div>
                <div class="clause-body-text">${escapeHtml(clause.text)}</div>
                ${trapsHtml}
            `;

            clausesList.appendChild(card);
        });
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // Export Markdown Report
    exportMdBtn.addEventListener("click", async () => {
        if (!currentAuditReport) return;
        try {
            const res = await fetch("/api/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ report: currentAuditReport })
            });

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `contract_audit_${Date.now()}.md`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } catch (err) {
            console.error("Export error:", err);
            alert("Failed to export report.");
        }
    });

    // Initial empty stats
    updateTextStats();
});
