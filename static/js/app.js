/**
 * LexiTrap Clean Frontend Controller
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
    const filterBtns = document.querySelectorAll(".filter-btn");

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

    // Number Counting Animation
    function animateValue(element, start, end, duration) {
        if (!element) return;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Load Sample Contract
    async function loadSample(sampleId) {
        try {
            loadingOverlay.classList.remove("hidden");
            const res = await fetch(`/api/sample/${sampleId}`);
            const data = await res.json();
            if (data.status === "success") {
                contractTextarea.value = data.text;
                docNameInput.value = data.sample.name;
                updateTextStats();
                
                loadSampleBtns.forEach(b => b.classList.remove("active"));
                const activeCard = document.querySelector(`.example-card[data-id="${sampleId}"]`);
                if (activeCard) activeCard.classList.add("active");

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
            alert("Please paste contract text or select an example above.");
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
            alert("An error occurred while analyzing the contract.");
        } finally {
            loadingOverlay.classList.add("hidden");
        }
    }

    auditBtn.addEventListener("click", runAudit);

    // Render Full Report
    function renderReport(report) {
        const score = Math.round(report.overall_health_score);
        animateValue(healthScoreVal, 0, score, 800);

        // Grade & Risk level color styling
        gradeBadge.textContent = `Grade ${report.letter_grade}`;
        riskSeverityBadge.textContent = report.risk_level === 'SAFE' ? 'Safe to Sign' : (report.risk_level === 'CRITICAL' ? 'High Risk' : `${report.risk_level} Risk`);

        gradeBadge.className = "score-badge badge-grade";
        riskSeverityBadge.className = "score-badge badge-risk";
        scoreCircle.style.backgroundColor = "";
        scoreCircle.style.borderColor = "";
        healthScoreVal.style.color = "";

        if (score >= 80) {
            scoreCircle.style.backgroundColor = "#ecfdf5";
            scoreCircle.style.borderColor = "#a7f3d0";
            healthScoreVal.style.color = "#059669";
            riskSeverityBadge.style.backgroundColor = "#059669";
        } else if (score >= 60) {
            scoreCircle.style.backgroundColor = "#fffbeb";
            scoreCircle.style.borderColor = "#fde68a";
            healthScoreVal.style.color = "#d97706";
            riskSeverityBadge.style.backgroundColor = "#d97706";
        } else {
            scoreCircle.style.backgroundColor = "#fef2f2";
            scoreCircle.style.borderColor = "#fecaca";
            healthScoreVal.style.color = "#dc2626";
            riskSeverityBadge.style.backgroundColor = "#dc2626";
        }

        verdictTitle.textContent = report.verdict_title;
        verdictDesc.textContent = report.verdict_description;

        // Animate stats
        animateValue(statTrapsCount, 0, report.total_traps_found, 600);
        animateValue(statCriticalCount, 0, report.critical_traps_count, 600);
        animateValue(statHighCount, 0, report.high_traps_count, 600);
        animateValue(statClausesCount, 0, report.total_clauses, 600);

        // Rule Breakdown
        deonticBarsContainer.innerHTML = "";
        const deonticPcts = report.deontic_profile.distribution_percentages || {};
        
        const friendlyNames = {
            "Obligation": "Must-Do Duties (Shall)",
            "Prohibition": "Forbidden Actions (Shall Not)",
            "Permission": "Allowed Rights (May)",
            "Warranty": "Promises & Guarantees",
            "Disclaimer": "Disclaimers (No Liability)",
            "Informational / Declarative": "General Information"
        };

        const colors = {
            "Obligation": "#dc2626",
            "Prohibition": "#d97706",
            "Permission": "#2563eb",
            "Warranty": "#4f46e5",
            "Disclaimer": "#7c3aed",
            "Informational / Declarative": "#94a3b8"
        };

        for (const [cat, pct] of Object.entries(deonticPcts)) {
            const displayName = friendlyNames[cat] || cat;
            const row = document.createElement("div");
            row.className = "rule-row";
            const color = colors[cat] || "#2563eb";
            row.innerHTML = `
                <span class="rule-name">${displayName}</span>
                <div class="rule-track">
                    <div class="rule-fill" style="width: ${pct}%; background-color: ${color};"></div>
                </div>
                <span class="rule-pct">${pct}%</span>
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

    // Render Clause Cards
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
                    ✓ No clauses matched this filter criteria.
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
                                <span class="trap-name">⚠️ Trap Detected: ${trap.category}</span>
                                <span class="badge ${trap.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${trap.severity === 'CRITICAL' ? 'High Risk' : 'Medium Risk'}</span>
                            </div>
                            <p class="trap-desc"><strong>What is the risk:</strong> ${trap.legal_danger}</p>
                            <p class="trap-impact"><strong>Impact on you:</strong> ${trap.business_impact}</p>
                            <div class="trap-keywords">
                                <strong>Trigger words:</strong> 
                                ${trap.matched_patterns.map(p => `<span>${p}</span>`).join(" ")}
                            </div>

                            ${redline ? `
                            <div class="redline-box">
                                <div class="redline-title">✏️ Suggested Fair Replacement:</div>
                                <div class="diff-view">${redline.diff_html}</div>
                                <div class="talking-point-box">
                                    <strong>What to say when negotiating:</strong> ${redline.negotiation_talking_point}
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

    updateTextStats();
});
