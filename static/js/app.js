/**
 * LexiTrap Interactive Controller (Simplified English & Clear Typography)
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
    const scanLaser = document.getElementById("scan-laser");
    const resultsSection = document.getElementById("results-section");
    const loadSampleBtns = document.querySelectorAll(".load-sample-btn");
    const exportMdBtn = document.getElementById("export-md-btn");
    const filterBtns = document.querySelectorAll(".filter-tab");

    // Results Elements
    const healthScoreVal = document.getElementById("health-score-val");
    const scoreGaugeBar = document.getElementById("score-gauge-bar");
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

    // -------------------------------------------------------------
    // 1. Interactive Three.js Visualizer
    // -------------------------------------------------------------
    function init3DScene() {
        const canvas = document.getElementById("three-canvas");
        if (!canvas || typeof THREE === "undefined") return;

        const container = canvas.parentElement;
        const width = container.clientWidth || 300;
        const height = container.clientHeight || 220;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        camera.position.z = 4.2;

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const group = new THREE.Group();
        scene.add(group);

        // Outer Wireframe
        const icosaGeometry = new THREE.IcosahedronGeometry(1.3, 1);
        const icosaMaterial = new THREE.MeshBasicMaterial({
            color: 0x1d4ed8,
            wireframe: true,
            transparent: true,
            opacity: 0.5
        });
        const icosaMesh = new THREE.Mesh(icosaGeometry, icosaMaterial);
        group.add(icosaMesh);

        // Inner Core
        const innerGeometry = new THREE.OctahedronGeometry(0.8, 0);
        const innerMaterial = new THREE.MeshPhongMaterial({
            color: 0x2563eb,
            emissive: 0x1e40af,
            emissiveIntensity: 0.5,
            shininess: 90,
            transparent: true,
            opacity: 0.9,
            flatShading: true
        });
        const innerMesh = new THREE.Mesh(innerGeometry, innerMaterial);
        group.add(innerMesh);

        // Floating particles
        const particleCount = 50;
        const particleGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for (let i = 0; i < particleCount * 3; i += 3) {
            positions[i] = (Math.random() - 0.5) * 5;
            positions[i + 1] = (Math.random() - 0.5) * 5;
            positions[i + 2] = (Math.random() - 0.5) * 5;
        }

        particleGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        const particleMaterial = new THREE.PointsMaterial({
            color: 0x2563eb,
            size: 0.07,
            transparent: true,
            opacity: 0.6
        });
        const particleField = new THREE.Points(particleGeometry, particleMaterial);
        group.add(particleField);

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x2563eb, 2, 50);
        pointLight1.position.set(5, 5, 5);
        scene.add(pointLight1);

        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;

        window.addEventListener("mousemove", (e) => {
            mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
        });

        function animate() {
            requestAnimationFrame(animate);

            targetX += (mouseX - targetX) * 0.05;
            targetY += (mouseY - targetY) * 0.05;

            group.rotation.x = targetY * 0.5;
            group.rotation.y += targetX * 0.02 + 0.007;

            innerMesh.rotation.y -= 0.012;
            renderer.render(scene, camera);
        }

        animate();

        window.addEventListener("resize", () => {
            const newWidth = container.clientWidth || 300;
            const newHeight = container.clientHeight || 220;
            camera.aspect = newWidth / newHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(newWidth, newHeight);
        });
    }

    init3DScene();

    // -------------------------------------------------------------
    // 2. Text Counting
    // -------------------------------------------------------------
    function updateTextStats() {
        const text = contractTextarea.value;
        charCountEl.textContent = text.length.toLocaleString();
        
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCountEl.textContent = words.toLocaleString();

        const clauses = (text.match(/(?:Section|Article|Clause|\b\d+\.)/gi) || []).length || Math.max(1, Math.floor(words / 60));
        estClausesEl.textContent = text.trim() ? clauses : 0;
    }

    contractTextarea.addEventListener("input", updateTextStats);

    // -------------------------------------------------------------
    // 3. Smooth Number Counter
    // -------------------------------------------------------------
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

    // -------------------------------------------------------------
    // 4. Load Preset Sample
    // -------------------------------------------------------------
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
                const activeBtn = document.querySelector(`.load-sample-btn[data-id="${sampleId}"]`);
                if (activeBtn) activeBtn.classList.add("active");

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

    // -------------------------------------------------------------
    // 5. Run Cognitive Audit
    // -------------------------------------------------------------
    async function runAudit() {
        const text = contractTextarea.value.trim();
        const docName = docNameInput.value.trim() || "Contract Agreement";

        if (!text) {
            alert("Please paste contract text or select an example above.");
            return;
        }

        loadingOverlay.classList.remove("hidden");
        scanLaser.classList.remove("hidden");
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
            scanLaser.classList.add("hidden");
        }
    }

    auditBtn.addEventListener("click", runAudit);

    // -------------------------------------------------------------
    // 6. Render Report with Gauges and Counters
    // -------------------------------------------------------------
    function renderReport(report) {
        const score = Math.round(report.overall_health_score);
        
        // Count-up animation for Score
        animateValue(healthScoreVal, 0, score, 1000);

        // Animated SVG Gauge (circumference: 2 * PI * 50 ≈ 314)
        const circumference = 314;
        const offset = circumference - (score / 100) * circumference;
        
        let gaugeColor = "#b91c1c"; // red
        if (score >= 80) gaugeColor = "#047857"; // emerald
        else if (score >= 60) gaugeColor = "#b45309"; // amber

        scoreGaugeBar.style.stroke = gaugeColor;
        scoreGaugeBar.style.strokeDashoffset = offset;

        // Badges
        gradeBadge.textContent = `Grade ${report.letter_grade}`;
        riskSeverityBadge.textContent = report.risk_level === 'SAFE' ? 'Safe to Sign' : (report.risk_level === 'CRITICAL' ? 'Critical Risk' : `${report.risk_level} Risk`);

        gradeBadge.className = "badge";
        riskSeverityBadge.className = "badge";
        healthScoreVal.style.color = gaugeColor;

        if (score >= 80) {
            gradeBadge.classList.add("grade-a");
            riskSeverityBadge.classList.add("risk-safe");
        } else if (score >= 60) {
            gradeBadge.classList.add("grade-b");
            riskSeverityBadge.classList.add("risk-medium");
        } else {
            gradeBadge.classList.add("grade-f");
            riskSeverityBadge.classList.add("risk-critical");
        }

        verdictTitle.textContent = report.verdict_title;
        verdictDesc.textContent = report.verdict_description;

        // Animate stats
        animateValue(statTrapsCount, 0, report.total_traps_found, 700);
        animateValue(statCriticalCount, 0, report.critical_traps_count, 700);
        animateValue(statHighCount, 0, report.high_traps_count, 700);
        animateValue(statClausesCount, 0, report.total_clauses, 700);

        // Contract Rules Breakdown (Plain English)
        deonticBarsContainer.innerHTML = "";
        const deonticPcts = report.deontic_profile.distribution_percentages || {};
        
        const friendlyNames = {
            "Obligation": "Must-Do Duties (Shall/Must)",
            "Prohibition": "Forbidden Actions (Shall Not)",
            "Permission": "Allowed Rights (May)",
            "Warranty": "Promises & Guarantees",
            "Disclaimer": "Disclaimers (No Liability)",
            "Informational / Declarative": "General Information"
        };

        const colors = {
            "Obligation": "#b91c1c",
            "Prohibition": "#b45309",
            "Permission": "#1d4ed8",
            "Warranty": "#4338ca",
            "Disclaimer": "#6d28d9",
            "Informational / Declarative": "#64748b"
        };

        for (const [cat, pct] of Object.entries(deonticPcts)) {
            const displayName = friendlyNames[cat] || cat;
            const row = document.createElement("div");
            row.className = "deontic-item";
            const color = colors[cat] || "#1d4ed8";
            row.innerHTML = `
                <span class="deontic-label">${displayName}</span>
                <div class="deontic-track">
                    <div class="deontic-fill" style="width: 0%; background-color: ${color};"></div>
                </div>
                <span class="deontic-percent">${pct}%</span>
            `;
            deonticBarsContainer.appendChild(row);

            setTimeout(() => {
                const fill = row.querySelector(".deontic-fill");
                if (fill) fill.style.width = `${pct}%`;
            }, 100);
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
                <div class="clause-card tilt-card" style="text-align: center; color: var(--text-muted); padding: 28px;">
                    ✓ No clauses matched this filter.
                </div>
            `;
            return;
        }

        clauses.forEach((clause, index) => {
            const card = document.createElement("div");
            card.className = `clause-card tilt-card ${clause.heat_level.toLowerCase()}`;

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
                                <strong>Trigger words found:</strong> 
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
