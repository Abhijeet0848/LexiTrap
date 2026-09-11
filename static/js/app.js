/**
 * LexAudit Web Application Frontend Controller
 */

document.addEventListener("DOMContentLoaded", () => {
    // Elements
    const contractTextarea = document.getElementById("contract-text");
    const docNameInput = document.getElementById("doc-name-input");
    const charCountEl = document.getElementById("char-count");
    const wordCountEl = document.getElementById("word-count");
    const estClausesEl = document.getElementById("est-clauses");
    const auditBtn = document.getElementById("audit-btn");
    const clearBtn = document.getElementById("clear-btn");
    const loadingOverlay = document.getElementById("loading-overlay");
    const resultsSection = document.getElementById("results-section");
    const sampleCards = document.querySelectorAll(".sample-card");
    const loadSampleBtns = document.querySelectorAll(".load-sample-btn");
    const exportMdBtn = document.getElementById("export-md-btn");
    const filterBtns = document.querySelectorAll(".filter-btn");

    // Results Elements
    const healthScoreVal = document.getElementById("health-score-val");
    const gaugeFill = document.getElementById("gauge-fill");
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

    // Textarea input counters
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
                
                // Highlight active sample card
                sampleCards.forEach(c => c.classList.remove("active"));
                const activeCard = document.querySelector(`.sample-card[data-sample-id="${sampleId}"]`);
                if (activeCard) activeCard.classList.add("active");

                // Automatically trigger audit
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
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const id = btn.getAttribute("data-id");
            loadSample(id);
        });
    });

    sampleCards.forEach(card => {
        card.addEventListener("click", () => {
            const id = card.getAttribute("data-sample-id");
            loadSample(id);
        });
    });

    // Clear Button
    clearBtn.addEventListener("click", () => {
        contractTextarea.value = "";
        docNameInput.value = "Custom Legal Agreement";
        updateTextStats();
        resultsSection.classList.add("hidden");
        currentAuditReport = null;
        sampleCards.forEach(c => c.classList.remove("active"));
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
        // Health Score & Gauge
        const score = report.overall_health_score;
        healthScoreVal.textContent = Math.round(score);

        // Circular Gauge calculations (radius = 70, circumference ≈ 440)
        const circumference = 440;
        const offset = circumference - (score / 100) * circumference;
        gaugeFill.style.strokeDashoffset = offset;

        // Color coding gauge and badges
        let gaugeColor = "#ff4d6d"; // Rose
        if (score >= 80) gaugeColor = "#00f2a9"; // Emerald
        else if (score >= 60) gaugeColor = "#ffb703"; // Amber
        else if (score >= 40) gaugeColor = "#fb8500";

        gaugeFill.style.stroke = gaugeColor;
        gradeBadge.textContent = report.letter_grade;
        gradeBadge.style.backgroundColor = gaugeColor;
        riskSeverityBadge.textContent = report.risk_level;

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
            "Obligation": "#ff4d6d",
            "Prohibition": "#ffb703",
            "Permission": "#00f2fe",
            "Warranty": "#4facfe",
            "Disclaimer": "#8a2be2",
            "Informational / Declarative": "#64748b"
        };

        for (const [cat, pct] of Object.entries(deonticPcts)) {
            const barRow = document.createElement("div");
            barRow.className = "deontic-row";
            const color = colors[cat] || "#00f2fe";
            barRow.innerHTML = `
                <span class="deontic-name">${cat}</span>
                <div class="deontic-bar-track">
                    <div class="deontic-bar-fill" style="width: ${pct}%; background: ${color};"></div>
                </div>
                <span class="deontic-pct">${pct}%</span>
            `;
            deonticBarsContainer.appendChild(barRow);
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
                <div class="card" style="text-align: center; color: var(--text-muted); padding: 32px;">
                    ✓ No clauses matched the active filter criteria.
                </div>
            `;
            return;
        }

        clauses.forEach(clause => {
            const clauseEl = document.createElement("div");
            clauseEl.className = `clause-item ${clause.heat_level.toLowerCase()}`;

            let trapsHtml = "";
            if (clause.traps && clause.traps.length > 0) {
                clause.traps.forEach(trap => {
                    const dev = trap.benchmark_comparison || {};
                    const redline = (currentAuditReport.redlines || []).find(r => r.clause_id === clause.clause_id && r.trap_category === trap.category);

                    trapsHtml += `
                        <div class="trap-detail-box">
                            <div class="trap-title-row">
                                <span class="trap-category-name">⚠️ ${trap.category}</span>
                                <span class="sample-badge ${trap.severity.toLowerCase()}">${trap.severity}</span>
                            </div>
                            <p class="trap-explanation"><strong>Legal Risk:</strong> ${trap.legal_danger}</p>
                            <p class="trap-explanation"><strong>Business Impact:</strong> ${trap.business_impact}</p>
                            <div class="trap-triggers">
                                <strong>Trigger Keywords:</strong> 
                                ${trap.matched_patterns.map(p => `<span>${p}</span>`).join(" ")}
                            </div>

                            ${dev.benchmark ? `
                            <div class="benchmark-box">
                                <strong>Benchmark Standard:</strong> ${dev.benchmark.standard_name} (${dev.deviation_level})
                                <div style="margin-top: 4px; color: var(--text-secondary);">${dev.benchmark.title}</div>
                            </div>
                            ` : ''}

                            ${redline ? `
                            <div class="redline-accordion">
                                <div class="redline-header">
                                    <h5>✏️ Proposed Balanced Redline Alternative</h5>
                                </div>
                                <div class="redline-body">
                                    <div class="diff-content">${redline.diff_html}</div>
                                    <div class="talking-point">
                                        <strong>Negotiation Strategy:</strong> ${redline.negotiation_talking_point}
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                    `;
                });
            }

            clauseEl.innerHTML = `
                <div class="clause-header">
                    <div class="clause-title-wrap">
                        <span class="clause-id-tag">${clause.clause_id}</span>
                        <h4 class="clause-title">${clause.title}</h4>
                    </div>
                    <div class="clause-tags">
                        <span class="deontic-badge">${clause.deontic_profile.dominant_category}</span>
                        <span class="sample-badge ${clause.heat_level.toLowerCase()}">Risk ${clause.risk_score}</span>
                    </div>
                </div>
                <div class="clause-text">${escapeHtml(clause.text)}</div>
                ${trapsHtml}
            `;

            clausesList.appendChild(clauseEl);
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
            alert("Failed to export markdown report.");
        }
    });

    // Initialize with first preset sample
    loadSample("predatory_saas_tos");
});
