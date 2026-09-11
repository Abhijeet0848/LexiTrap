/**
 * LexiTrap Instant Frontend Controller (Optimized & Ultra-Fast)
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

    // Number Counting Animation (Fast 250ms)
    function animateValue(element, start, end, duration = 250) {
        if (!element) return;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            element.textContent = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                element.textContent = end;
            }
        };
        window.requestAnimationFrame(step);
    }

    // Load Sample Contract
    async function loadSample(sampleId) {
        loadSampleBtns.forEach(b => b.classList.remove("active"));
        const activeCard = document.querySelector(`.example-card[data-id="${sampleId}"]`);
        if (activeCard) activeCard.classList.add("active");

        try {
            const res = await fetch(`/api/sample/${sampleId}`);
            const data = await res.json();
            if (data.status === "success") {
                contractTextarea.value = data.text;
                docNameInput.value = data.sample.name;
                updateTextStats();
                await runAudit();
            }
        } catch (err) {
            console.error("Failed to load sample:", err);
            alert("Error loading sample contract.");
        }
    }

    // URL Fetcher Handler
    const urlInput = document.getElementById("url-input");
    const fetchUrlBtn = document.getElementById("fetch-url-btn");

    async function handleFetchUrl() {
        const url = urlInput.value.trim();
        if (!url) {
            alert("Please paste a valid Terms of Service URL.");
            return;
        }

        const originalText = fetchUrlBtn.textContent;
        fetchUrlBtn.textContent = "Fetching...";
        fetchUrlBtn.disabled = true;

        try {
            const res = await fetch("/api/fetch-url", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url })
            });
            const data = await res.json();
            if (data.status === "success") {
                contractTextarea.value = data.text;
                docNameInput.value = data.title;
                updateTextStats();
                await runAudit();
            } else {
                alert("Could not fetch URL: " + (data.message || "Unknown error"));
            }
        } catch (err) {
            console.error("Fetch URL error:", err);
            alert("Failed to connect to the provided URL.");
        } finally {
            fetchUrlBtn.textContent = originalText;
            fetchUrlBtn.disabled = false;
        }
    }

    if (fetchUrlBtn) {
        fetchUrlBtn.addEventListener("click", handleFetchUrl);
    }
    if (urlInput) {
        urlInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleFetchUrl();
            }
        });
    }

    // Photo OCR & File Upload Controls
    const photoUploadInput = document.getElementById("photo-upload-input");
    const uploadPhotoBtn = document.getElementById("upload-photo-btn");
    const pdfUploadInput = document.getElementById("pdf-upload-input");
    const uploadPdfBtn = document.getElementById("upload-pdf-btn");
    const ocrStatusBanner = document.getElementById("ocr-status-banner");
    const ocrStatusTitle = document.getElementById("ocr-status-title");
    const ocrStatusSub = document.getElementById("ocr-status-sub");
    const ocrProgressBar = document.getElementById("ocr-progress-bar");
    const photoPreviewBox = document.getElementById("photo-preview-box");
    const photoPreviewImg = document.getElementById("photo-preview-img");
    const photoPreviewName = document.getElementById("photo-preview-name");
    const removePhotoBtn = document.getElementById("remove-photo-btn");

    if (uploadPhotoBtn && photoUploadInput) {
        uploadPhotoBtn.addEventListener("click", () => {
            photoUploadInput.click();
        });

        photoUploadInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Show thumbnail preview
            const reader = new FileReader();
            reader.onload = (re) => {
                photoPreviewImg.src = re.target.result;
                photoPreviewName.textContent = file.name;
                photoPreviewBox.classList.remove("hidden");
            };
            reader.readAsDataURL(file);

            // Show OCR progress banner
            ocrStatusBanner.classList.remove("hidden");
            ocrProgressBar.style.width = "10%";
            ocrStatusTitle.textContent = "Scanning contract photo with OCR...";
            ocrStatusSub.textContent = "Initializing Optical Character Recognition engine...";

            try {
                if (typeof Tesseract === "undefined") {
                    throw new Error("OCR library could not be loaded from CDN. Please check internet connection.");
                }

                const result = await Tesseract.recognize(
                    file,
                    'eng',
                    {
                        logger: (m) => {
                            if (m.status === "recognizing text") {
                                const progress = Math.round((m.progress || 0) * 100);
                                ocrProgressBar.style.width = `${progress}%`;
                                ocrStatusTitle.textContent = `Reading contract text... (${progress}%)`;
                                ocrStatusSub.textContent = `Processing image lines and characters...`;
                            }
                        }
                    }
                );

                const extractedText = (result && result.data && result.data.text) ? result.data.text.trim() : "";

                if (!extractedText || extractedText.length < 20) {
                    alert("Could not detect clear legal text in this photo. Please make sure the photo is well-lit and readable.");
                } else {
                    contractTextarea.value = extractedText;
                    const cleanDocTitle = file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ");
                    docNameInput.value = `Scanned: ${cleanDocTitle}`;
                    updateTextStats();
                    
                    ocrStatusTitle.textContent = "✅ Text successfully extracted!";
                    ocrStatusSub.textContent = "Running instant contract risk audit...";
                    ocrProgressBar.style.width = "100%";
                    
                    setTimeout(async () => {
                        ocrStatusBanner.classList.add("hidden");
                        await runAudit();
                    }, 500);
                }
            } catch (err) {
                console.error("OCR scanning error:", err);
                alert("OCR Error: " + err.message);
                ocrStatusBanner.classList.add("hidden");
            } finally {
                photoUploadInput.value = "";
            }
        });
    }

    if (removePhotoBtn) {
        removePhotoBtn.addEventListener("click", () => {
            photoPreviewBox.classList.add("hidden");
            photoPreviewImg.src = "";
        });
    }

    // PDF / Text File Upload Handler
    if (uploadPdfBtn && pdfUploadInput) {
        uploadPdfBtn.addEventListener("click", () => {
            pdfUploadInput.click();
        });

        pdfUploadInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const originalBtnText = uploadPdfBtn.innerHTML;
            uploadPdfBtn.innerHTML = "<span>⏳</span> Reading...";
            uploadPdfBtn.disabled = true;

            const formData = new FormData();
            formData.append("file", file);

            try {
                const res = await fetch("/api/upload-file", {
                    method: "POST",
                    body: formData,
                });
                const data = await res.json();
                if (data.status === "success") {
                    contractTextarea.value = data.text;
                    docNameInput.value = data.title;
                    updateTextStats();
                    await runAudit();
                } else {
                    alert("File upload error: " + (data.message || "Failed to read file"));
                }
            } catch (err) {
                console.error("Upload error:", err);
                alert("Failed to upload and parse document.");
            } finally {
                uploadPdfBtn.innerHTML = originalBtnText;
                uploadPdfBtn.disabled = false;
                pdfUploadInput.value = "";
            }
        });
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
        if (photoPreviewBox) photoPreviewBox.classList.add("hidden");
        if (ocrStatusBanner) ocrStatusBanner.classList.add("hidden");
        currentAuditReport = null;
        loadSampleBtns.forEach(b => b.classList.remove("active"));
    });

    // Run Audit (Instant execution)
    async function runAudit() {
        const text = contractTextarea.value.trim();
        const docName = docNameInput.value.trim() || "Contract Agreement";

        if (!text) {
            alert("Please paste contract text or select an example above.");
            return;
        }

        const originalBtnHtml = auditBtn.innerHTML;
        auditBtn.innerHTML = '<span>⏳</span> Checking...';
        auditBtn.disabled = true;

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
            auditBtn.innerHTML = originalBtnHtml;
            auditBtn.disabled = false;
        }
    }

    auditBtn.addEventListener("click", runAudit);

    // Render Full Report
    function renderReport(report) {
        const score = Math.round(report.overall_health_score);
        animateValue(healthScoreVal, 0, score, 300);

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

        // Fast animate stats
        animateValue(statTrapsCount, 0, report.total_traps_found, 250);
        animateValue(statCriticalCount, 0, report.critical_traps_count, 250);
        animateValue(statHighCount, 0, report.high_traps_count, 250);
        animateValue(statClausesCount, 0, report.total_clauses, 250);

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
