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
    const statCriticalCount = document.getElementById("stat-critical-count");
    const statHighCount = document.getElementById("stat-high-count");
    const statLowCount = document.getElementById("stat-low-count");
    const statClausesCount = document.getElementById("stat-clauses-count");
    const deonticBarsContainer = document.getElementById("deontic-bars-container");
    const executivePointsList = document.getElementById("executive-points-list");
    const clausesList = document.getElementById("clauses-list");

    // Filter counts
    const countAllEl = document.getElementById("count-all");
    const countTrapsEl = document.getElementById("count-traps");
    const countCriticalEl = document.getElementById("count-critical");

    // OCR Progress Banner Elements
    const ocrStatusBanner = document.getElementById("ocr-status-banner");
    const ocrProgressBar = document.getElementById("ocr-progress-bar");
    const ocrStatusTitle = document.getElementById("ocr-status-title");
    const ocrStatusSub = document.getElementById("ocr-status-sub");

    // Photo Preview Elements
    const photoPreviewBox = document.getElementById("photo-preview-box");
    const photoPreviewImg = document.getElementById("photo-preview-img");
    const photoPreviewName = document.getElementById("photo-preview-name");
    const removePhotoBtn = document.getElementById("remove-photo-btn");
    const photoPlaceholderIcon = document.getElementById("photo-placeholder-icon");

    // PDF / File Upload Elements
    const uploadPdfBtn = document.getElementById("upload-pdf-btn");
    const pdfUploadInput = document.getElementById("pdf-upload-input");

    let currentAuditReport = null;
    let activeFilter = "ALL";
    let isUserManuallyEditingDocName = false;

    if (docNameInput) {
        docNameInput.addEventListener("input", () => {
            isUserManuallyEditingDocName = (docNameInput.value.trim().length > 0);
        });
    }

    // Smart Auto-Detect Contract Title
    function autoDetectContractTitle(text) {
        if (!text || !text.trim()) return "";
        
        // If user manually edited the contract name and it's meaningful, respect it
        const current = (docNameInput.value || "").trim();
        if (isUserManuallyEditingDocName && current && current.length >= 3) {
            return current;
        }

        const lines = text.trim().split("\n").map(l => l.trim()).filter(Boolean);
        if (lines.length === 0) return "";

        // 1. Check for explicit heading / title in the first 3 lines
        for (let line of lines.slice(0, 3)) {
            const clean = line.replace(/^[#*`_\s\d.:\-–—]+|[#*`_\s]+$/g, "").trim();
            if (clean && clean.length >= 4 && clean.length <= 55 && !clean.includes(";") && !clean.endsWith(".")) {
                if (!/^(last updated|dated:|version|effective date|between|whereas|this is an agreement|the provider may|the user shall)/i.test(clean)) {
                    docNameInput.value = clean;
                    return clean;
                }
            }
        }

        // 2. Intent-based Legal Topic Classification from text content
        const lower = text.toLowerCase();
        let inferredTitle = "";

        if (/\b(?:terminate|termination|cancellation|cancel\s+this\s+agreement)\b/i.test(lower)) {
            inferredTitle = "Termination Agreement / Clause";
        } else if (/\b(?:non-disclosure|confidentiality|proprietary\s+information|trade\s+secrets?)\b/i.test(lower)) {
            inferredTitle = "Non-Disclosure Agreement (NDA)";
        } else if (/\b(?:employment|employee|employer|salary|job\s+title|work\s+for\s+hire)\b/i.test(lower)) {
            inferredTitle = "Employment Agreement";
        } else if (/\b(?:freelance|independent\s+contractor|consultant|scope\s+of\s+work|deliverables)\b/i.test(lower)) {
            inferredTitle = "Freelance & Contractor Agreement";
        } else if (/\b(?:terms\s+of\s+(?:service|use)|user\s+agreement|platform\s+rules|acceptable\s+use)\b/i.test(lower)) {
            inferredTitle = "Terms of Service Agreement";
        } else if (/\b(?:privacy\s+policy|gdpr|personal\s+data|data\s+processing)\b/i.test(lower)) {
            inferredTitle = "Privacy Policy";
        } else if (/\b(?:intellectual\s+property|inventions?|patent|copyright|assigns?\s+all\s+rights)\b/i.test(lower)) {
            inferredTitle = "IP & Inventions Assignment";
        } else if (/\b(?:indemnif\w+|hold\s+harmless|defend\s+and\s+indemnify)\b/i.test(lower)) {
            inferredTitle = "Indemnification Agreement";
        } else if (/\b(?:liability|disclaim\w+|damages|limitation\s+of\s+liability)\b/i.test(lower)) {
            inferredTitle = "Limitation of Liability Clause";
        } else if (/\b(?:non-compete|non-solicitation|restrictive\s+covenant)\b/i.test(lower)) {
            inferredTitle = "Non-Compete Agreement";
        } else if (/\b(?:arbitration|dispute\s+resolution|governing\s+law|jurisdiction)\b/i.test(lower)) {
            inferredTitle = "Dispute Resolution & Arbitration Clause";
        } else if (/\b(?:payment\s+terms|invoicing|fees|pricing|billing\s+cycle)\b/i.test(lower)) {
            inferredTitle = "Payment & Billing Agreement";
        } else if (/\b(?:automatically\s+renew|auto-renews?|successive\s+(?:one|two|multi|\d+)?\s*-?\s*year|renewal\s+term)\b/i.test(lower)) {
            inferredTitle = "Automatic Renewal Clause";
        } else if (/\b(?:software\s+as\s+a\s+service|saas|subscription\s+agreement)\b/i.test(lower)) {
            inferredTitle = "SaaS Subscription Agreement";
        } else {
            inferredTitle = "Contract Agreement";
        }

        docNameInput.value = inferredTitle;
        return inferredTitle;
    }

    let statsDebounceTimer = null;
    function updateTextStats() {
        const text = contractTextarea.value;
        charCountEl.textContent = text.length.toLocaleString();
        
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCountEl.textContent = words.toLocaleString();

        const clauses = (text.match(/(?:Section|Article|Clause|\b\d+\.)/gi) || []).length || Math.max(1, Math.floor(words / 60));
        estClausesEl.textContent = text.trim() ? clauses : 0;

        clearTimeout(statsDebounceTimer);
        statsDebounceTimer = setTimeout(() => {
            if (text.trim().length >= 10 && !isUserManuallyEditingDocName) {
                autoDetectContractTitle(text);
            }
        }, 150);
    }

    contractTextarea.addEventListener("input", updateTextStats);
    contractTextarea.addEventListener("paste", () => {
        setTimeout(updateTextStats, 50);
    });
    contractTextarea.addEventListener("change", updateTextStats);

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
        isUserManuallyEditingDocName = false;
        loadSampleBtns.forEach(b => b.classList.remove("active"));
        const activeCard = document.querySelector(`.load-sample-btn[data-id="${sampleId}"]`);
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
            alert("Please paste a company website or URL (e.g. flipkart.com, amazon.in, or discord.com).");
            return;
        }

        const originalText = fetchUrlBtn.textContent;
        fetchUrlBtn.textContent = "🔍 Finding & Fetching Terms...";
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
                alert("Could not fetch Terms: " + (data.message || "Unknown error"));
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

    const urlQuickPills = document.querySelectorAll(".url-quick-pill");
    urlQuickPills.forEach(pill => {
        pill.addEventListener("click", () => {
            const targetUrl = pill.getAttribute("data-url");
            if (targetUrl && urlInput) {
                urlInput.value = targetUrl;
                handleFetchUrl();
            }
        });
    });

    // Photo OCR & File Upload Controls (Direct Standalone Buttons)
    const btnCameraScan = document.getElementById("btn-camera-scan");
    const btnGalleryUpload = document.getElementById("btn-gallery-upload");
    const cameraCaptureInput = document.getElementById("camera-capture-input");
    const galleryUploadInput = document.getElementById("gallery-upload-input");

    // Camera Modal Elements
    const cameraModal = document.getElementById("camera-modal");
    const cameraModalBackdrop = document.getElementById("camera-modal-backdrop");
    const cameraVideoFeed = document.getElementById("camera-video-feed");
    const closeCameraBtn = document.getElementById("close-camera-btn");
    const cancelCameraBtn = document.getElementById("cancel-camera-btn");
    const snapPhotoBtn = document.getElementById("snap-photo-btn");
    let activeCameraStream = null;

    function stopCameraStream() {
        if (activeCameraStream) {
            activeCameraStream.getTracks().forEach(track => track.stop());
            activeCameraStream = null;
        }
        if (cameraVideoFeed) {
            cameraVideoFeed.srcObject = null;
        }
        if (cameraModal) {
            cameraModal.classList.add("hidden");
        }
    }

    // Direct Button 1: Live Webcam / Device Camera
    if (btnCameraScan) {
        btnCameraScan.addEventListener("click", async () => {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: {
                            facingMode: { ideal: "environment" },
                            width: { ideal: 1920 },
                            height: { ideal: 1080 }
                        },
                        audio: false
                    });
                    activeCameraStream = stream;
                    cameraVideoFeed.srcObject = stream;
                    cameraModal.classList.remove("hidden");
                } catch (err) {
                    console.warn("Could not access camera via getUserMedia, falling back to file picker:", err);
                    if (cameraCaptureInput) cameraCaptureInput.click();
                }
            } else if (cameraCaptureInput) {
                cameraCaptureInput.click();
            }
        });

        if (cameraCaptureInput) {
            cameraCaptureInput.addEventListener("change", (e) => {
                const file = e.target.files[0];
                if (file) processImageFile(file);
                cameraCaptureInput.value = "";
            });
        }
    }

    // Camera Modal Controls
    if (closeCameraBtn) closeCameraBtn.addEventListener("click", stopCameraStream);
    if (cancelCameraBtn) cancelCameraBtn.addEventListener("click", stopCameraStream);
    if (cameraModalBackdrop) cameraModalBackdrop.addEventListener("click", stopCameraStream);

    // Snap & Capture Photo from Video Stream
    if (snapPhotoBtn && cameraVideoFeed) {
        snapPhotoBtn.addEventListener("click", () => {
            const video = cameraVideoFeed;
            const width = video.videoWidth || 1280;
            const height = video.videoHeight || 720;

            const canvas = document.createElement("canvas");
            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, width, height);

            canvas.toBlob((blob) => {
                if (blob) {
                    const file = new File([blob], "camera_contract_snap.jpg", { type: "image/jpeg" });
                    stopCameraStream();
                    processImageFile(file);
                } else {
                    alert("Failed to capture image snapshot from camera.");
                }
            }, "image/jpeg", 0.95);
        });
    }

    // Direct Button 2: Media / Gallery Upload
    if (btnGalleryUpload && galleryUploadInput) {
        btnGalleryUpload.addEventListener("click", () => {
            galleryUploadInput.click();
        });

        galleryUploadInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) processImageFile(file);
            galleryUploadInput.value = "";
        });
    }

    // High-Accuracy Image Preprocessing for OCR (Grayscale & Contrast Normalization)
    async function preprocessImageForOcr(imageFile) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement("canvas");
                let width = img.width;
                let height = img.height;

                // Scale up small photos for sharper OCR character boundary detection
                if (width < 1400 && height < 1400) {
                    const scale = 2;
                    width *= scale;
                    height *= scale;
                } else if (width > 2800 || height > 2800) {
                    const maxDim = 2800;
                    if (width > height) {
                        height = Math.round((height * maxDim) / width);
                        width = maxDim;
                    } else {
                        width = Math.round((width * maxDim) / height);
                        height = maxDim;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, width, height);

                // Pixel-level Grayscale & Adaptive Contrast Stretching
                try {
                    const imgData = ctx.getImageData(0, 0, width, height);
                    const d = imgData.data;
                    for (let i = 0; i < d.length; i += 4) {
                        const gray = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
                        const contrast = 1.35; // 35% contrast boost
                        const enhanced = Math.min(255, Math.max(0, (gray - 128) * contrast + 128));
                        d[i] = enhanced;
                        d[i + 1] = enhanced;
                        d[i + 2] = enhanced;
                    }
                    ctx.putImageData(imgData, 0, 0);
                    canvas.toBlob((blob) => {
                        resolve(blob || imageFile);
                    }, "image/png");
                } catch (e) {
                    resolve(imageFile);
                }
            };
            img.onerror = () => resolve(imageFile);
            img.src = URL.createObjectURL(imageFile);
        });
    }

    // Post-OCR Legal Text Sanitizer & Artifact Fixer
    function cleanOcrExtractedText(rawText) {
        if (!rawText) return "";
        let text = rawText;
        // Reconstruct broken hyphenated line wraps (e.g. "indemni-\n fication" -> "indemnification")
        text = text.replace(/(\w+)-\s*\n\s*(\w+)/g, "$1$2");
        // Normalize smart quotes and apostrophes
        text = text.replace(/[\u201C\u201D\u201E\u201F\u2033\u2036]/g, '"');
        text = text.replace(/[\u2018\u2019\u201A\u201B\u2032\u2035]/g, "'");
        // Normalize bullet points
        text = text.replace(/^[•●▪■◆]\s*/gm, "(a) ");
        // Collapse multiple spaces
        text = text.replace(/[ \t]+/g, " ");
        // Clean excessive line breaks
        text = text.replace(/\n{3,}/g, "\n\n");
        return text.trim();
    }

    // Shared OCR Image Processor with Preprocessing & Multi-Stage Status
    async function processImageFile(file) {
        if (!file) return;

        // Show thumbnail preview
        const reader = new FileReader();
        const photoPlaceholderIcon = document.getElementById("photo-placeholder-icon");
        reader.onload = (re) => {
            photoPreviewImg.src = re.target.result;
            photoPreviewImg.style.display = "block";
            if (photoPlaceholderIcon) photoPlaceholderIcon.style.display = "none";
            photoPreviewName.textContent = file.name || "Camera Photo";
            photoPreviewBox.classList.remove("hidden");
        };
        reader.readAsDataURL(file);

        // Show OCR progress banner
        ocrStatusBanner.classList.remove("hidden");
        ocrProgressBar.style.width = "15%";
        ocrStatusTitle.textContent = "Preprocessing contract photo...";
        ocrStatusSub.textContent = "Enhancing contrast and sharpening legal character boundaries...";

        try {
            // Stage 1: Preprocessing
            const processedBlob = await preprocessImageForOcr(file);
            ocrProgressBar.style.width = "30%";
            ocrStatusTitle.textContent = "Loading Optical Character Recognition (OCR)...";
            ocrStatusSub.textContent = "Scanning document lines and legal terminology...";

            if (typeof Tesseract === "undefined") {
                throw new Error("OCR engine library could not be loaded. Please check your internet connection.");
            }

            // Stage 2: Tesseract Recognition
            const result = await Tesseract.recognize(
                processedBlob,
                'eng',
                {
                    logger: (m) => {
                        if (m.status === "recognizing text") {
                            const progress = Math.round((m.progress || 0) * 100);
                            ocrProgressBar.style.width = `${Math.max(30, progress)}%`;
                            ocrStatusTitle.textContent = `Reading contract text... (${progress}%)`;
                            ocrStatusSub.textContent = `Extracting words, clauses, and definitions...`;
                        }
                    }
                }
            );

            const rawText = (result && result.data && result.data.text) ? result.data.text : "";
            const cleanText = cleanOcrExtractedText(rawText);

            if (!cleanText || cleanText.length < 20) {
                alert("Could not detect sufficient legal text in this photo. Please ensure the document is clear, well-lit, and in focus.");
                ocrStatusBanner.classList.add("hidden");
            } else {
                contractTextarea.value = cleanText;
                const baseName = (file.name || "contract").replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ");
                docNameInput.value = `Scanned: ${baseName}`;
                updateTextStats();
                
                ocrStatusTitle.textContent = "✅ Text successfully extracted!";
                ocrStatusSub.textContent = "Running instant contract risk audit...";
                ocrProgressBar.style.width = "100%";
                
                setTimeout(async () => {
                    ocrStatusBanner.classList.add("hidden");
                    await runAudit();
                }, 350);
            }
        } catch (err) {
            console.error("OCR scanning error:", err);
            alert("OCR Error: " + err.message);
            ocrStatusBanner.classList.add("hidden");
        }
    }

    if (removePhotoBtn) {
        removePhotoBtn.addEventListener("click", () => {
            photoPreviewBox.classList.add("hidden");
            photoPreviewImg.src = "";
            photoPreviewImg.style.display = "none";
            const photoPlaceholderIcon = document.getElementById("photo-placeholder-icon");
            if (photoPlaceholderIcon) photoPlaceholderIcon.style.display = "inline-block";
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
        isUserManuallyEditingDocName = false;
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
        let docName = (docNameInput.value || "").trim();
        if (!docName || docName === "Contract Agreement" || docName === "Submitted Contract") {
            docName = autoDetectContractTitle(text) || "Contract Agreement";
            docNameInput.value = docName;
        }

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
        
        let rawRisk = (report.risk_level || 'Moderate Risk').trim();
        let formattedRisk = rawRisk;
        if (rawRisk.toUpperCase() === 'SAFE') {
            formattedRisk = 'Safe to Sign';
        } else if (rawRisk.toUpperCase() === 'CRITICAL') {
            formattedRisk = 'Critical Risk';
        } else if (!rawRisk.toLowerCase().includes('risk')) {
            formattedRisk = `${rawRisk} Risk`;
        }
        riskSeverityBadge.textContent = formattedRisk;

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

        // Dynamic Executive Verdict & Security Advice Box
        const decisionBox = document.getElementById("verdict-decision-box");
        const decisionPill = document.getElementById("decision-pill");
        const decisionTitle = document.getElementById("decision-title");
        const decisionAdvice = document.getElementById("decision-advice");

        if (decisionBox) {
            if (score >= 80) {
                decisionBox.className = "verdict-decision-box decision-success";
                if (decisionPill) {
                    decisionPill.className = "decision-pill pill-success";
                    decisionPill.textContent = "🛡️ FAIR & BALANCED";
                }
                if (decisionTitle) decisionTitle.textContent = "Standard Commercial Terms (Low Risk)";
                if (decisionAdvice) decisionAdvice.innerHTML = "This document aligns with industry standard protections and contains no aggressive unilateral trap clauses.";
            } else if (score >= 60) {
                decisionBox.className = "verdict-decision-box decision-warning";
                if (decisionPill) {
                    decisionPill.className = "decision-pill pill-warning";
                    decisionPill.textContent = "⚠️ MODERATE RISK";
                }
                if (decisionTitle) decisionTitle.textContent = "Customary Disclaimers / Telemetry Detected";
                if (decisionAdvice) decisionAdvice.innerHTML = "Contains typical big-tech clauses (e.g. cloud diagnostic telemetry or standard liability waivers). Review account privacy preferences before consenting.";
            } else if (score >= 40) {
                decisionBox.className = "verdict-decision-box decision-warning";
                if (decisionPill) {
                    decisionPill.className = "decision-pill pill-warning";
                    decisionPill.textContent = "⚠️ ELEVATED RISK";
                }
                if (decisionTitle) decisionTitle.textContent = "One-Sided Provisions Identified";
                if (decisionAdvice) decisionAdvice.innerHTML = "Material risk factors detected (e.g. unilateral change rights, mandatory arbitration, or limited liability). Review carefully before agreeing.";
            } else {
                decisionBox.className = "verdict-decision-box decision-danger";
                if (decisionPill) {
                    decisionPill.className = "decision-pill pill-danger";
                    decisionPill.textContent = "🚫 CRITICAL RISK";
                }
                if (decisionTitle) decisionTitle.textContent = "Predatory Terms Detected — Do Not Agree Blindly";
                if (decisionAdvice) decisionAdvice.innerHTML = "Critical dark patterns found (e.g. nominal liability cap, silent unilateral amendments, immediate access termination, or forced arbitration). Redlines strongly recommended.";
            }
        }

        // Fast animate stats for Risk Tiers (High, Medium, Low, Total Sections)
        const clausesListAll = report.clause_audit_details || [];
        const highRiskClauses = clausesListAll.filter(c => c.heat_level === "CRITICAL" || c.heat_level === "HIGH").length;
        const medRiskClauses = clausesListAll.filter(c => c.heat_level === "MEDIUM").length;
        const lowRiskClauses = Math.max(0, (report.total_clauses || clausesListAll.length) - highRiskClauses - medRiskClauses);

        animateValue(statCriticalCount, 0, highRiskClauses, 250);
        animateValue(statHighCount, 0, medRiskClauses, 250);
        animateValue(statLowCount, 0, lowRiskClauses, 250);
        animateValue(statClausesCount, 0, report.total_clauses || clausesListAll.length, 250);

        // Render Interactive Contract DNA Heatmap Strip
        renderContractDnaStrip(report.clause_audit_details || []);

        // Rule Breakdown (if container is present)
        if (deonticBarsContainer) {
            deonticBarsContainer.innerHTML = "";
            const deonticPcts = (report.deontic_profile && report.deontic_profile.distribution_percentages) ? report.deontic_profile.distribution_percentages : {};
            
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
                    <span class="rule-name">${escapeHtml(displayName)}</span>
                    <div class="rule-track">
                        <div class="rule-fill" style="width: ${encodeURIComponent(pct)}%; background-color: ${escapeHtml(color)};"></div>
                    </div>
                    <span class="rule-pct">${escapeHtml(String(pct))}%</span>
                `;
                deonticBarsContainer.appendChild(row);
            }
        }

        // Executive Findings
        executivePointsList.innerHTML = "";
        (report.executive_summary_points || []).forEach(pt => {
            const li = document.createElement("li");
            li.textContent = pt;
            executivePointsList.appendChild(li);
        });

        // Render Academic NLP Inspector
        renderNlpInspector(report.nlp_overview || {});

        // Filter Counts
        const clauses = report.clause_audit_details || [];
        countAllEl.textContent = clauses.length;
        countTrapsEl.textContent = clauses.filter(c => c.has_traps).length;
        countCriticalEl.textContent = clauses.filter(c => c.heat_level === "CRITICAL").length;

        // Render Clauses
        renderClausesList();
    }

    // Render Academic NLP Pipeline & ML Benchmark Inspector
    function renderNlpInspector(nlp) {
        if (!nlp) return;

        // Token & Lemma stats
        const tokenStats = nlp.token_stats || {};
        const statTokensEl = document.getElementById("nlp-stat-tokens");
        const statVocabEl = document.getElementById("nlp-stat-vocab");
        const statStopwordEl = document.getElementById("nlp-stat-stopword-pct");
        if (statTokensEl) statTokensEl.textContent = (tokenStats.total_tokens || 0).toLocaleString();
        if (statVocabEl) statVocabEl.textContent = (tokenStats.unique_vocab_count || 0).toLocaleString();
        if (statStopwordEl) statStopwordEl.textContent = `${tokenStats.stopword_ratio_pct || 0}%`;

        // Sample lemmas
        const lemmasBox = document.getElementById("nlp-lemmas-sample");
        if (lemmasBox) {
            lemmasBox.innerHTML = "";
            const sampleLemmas = (nlp.lemmas && nlp.lemmas.sample_transformations) ? nlp.lemmas.sample_transformations : [];
            if (sampleLemmas.length > 0) {
                sampleLemmas.slice(0, 6).forEach(item => {
                    const pill = document.createElement("span");
                    pill.className = "nlp-tag-pill";
                    pill.innerHTML = `<code>${escapeHtml(item.original)}</code> → <strong>${escapeHtml(item.lemma)}</strong>`;
                    lemmasBox.appendChild(pill);
                });
            } else {
                lemmasBox.innerHTML = `<span style="font-size:0.75rem; color:var(--text-muted);">Standard morphological base forms</span>`;
            }
        }

        // Modals & POS mini-bars
        const modalsEl = document.getElementById("nlp-stat-modals");
        if (modalsEl) {
            const modals = nlp.modal_verbs || [];
            modalsEl.textContent = modals.length > 0 ? modals.join(", ") : "None detected";
        }

        const posBarsBox = document.getElementById("nlp-pos-bars");
        if (posBarsBox) {
            posBarsBox.innerHTML = "";
            const posDist = nlp.pos_distribution || {};
            const posColors = {
                "Modal Verbs (Deontic)": "#2563eb",
                "Nouns (Entities/Objects)": "#059669",
                "Verbs (Actions)": "#d97706",
                "Adjectives (Qualifiers)": "#7c3aed",
                "Adverbs (Modifiers)": "#dc2626",
                "Other / Particles": "#94a3b8"
            };

            for (const [posLabel, pData] of Object.entries(posDist)) {
                const count = (typeof pData === "object") ? pData.count : pData;
                const pct = (typeof pData === "object") ? pData.pct : 0;
                const row = document.createElement("div");
                row.className = "nlp-mini-bar-row";
                row.innerHTML = `
                    <span class="nlp-mini-bar-label">${escapeHtml(posLabel.split(" ")[0])} (${pct}%):</span>
                    <div class="nlp-mini-bar-track">
                        <div class="nlp-mini-bar-fill" style="width:${encodeURIComponent(pct)}%; background-color:${posColors[posLabel] || '#2563eb'};"></div>
                    </div>
                `;
                posBarsBox.appendChild(row);
            }
        }

        // Named Entities (NER)
        const nerContainer = document.getElementById("nlp-ner-entities-list");
        if (nerContainer) {
            nerContainer.innerHTML = "";
            const entitiesByType = nlp.entities_by_type || {};
            let hasEntities = false;

            for (const [entType, entList] of Object.entries(entitiesByType)) {
                if (!entList || entList.length === 0) continue;
                hasEntities = true;
                const group = document.createElement("div");
                group.className = "nlp-entity-group";
                
                let pillClass = "entity-org";
                if (entType.includes("MONEY")) pillClass = "entity-money";
                else if (entType.includes("DATE")) pillClass = "entity-date";
                else if (entType.includes("GPE")) pillClass = "entity-gpe";
                else if (entType.includes("LAW")) pillClass = "entity-law";

                const pillsHtml = entList.slice(0, 4).map(e => `<span class="nlp-tag-pill ${pillClass}">${escapeHtml(e)}</span>`).join(" ");
                group.innerHTML = `
                    <strong>${escapeHtml(entType)} (${entList.length}):</strong>
                    <div class="nlp-tags-wrap">${pillsHtml}</div>
                `;
                nerContainer.appendChild(group);
            }

            if (!hasEntities) {
                nerContainer.innerHTML = `<span style="font-size:0.75rem; color:var(--text-muted);">No specific jurisdictional entities or statutory citations detected.</span>`;
            }
        }

        // Top TF-IDF Terms
        const tfidfContainer = document.getElementById("nlp-tfidf-terms-list");
        if (tfidfContainer) {
            tfidfContainer.innerHTML = "";
            const tfidfTerms = nlp.top_tfidf_terms || [];
            if (tfidfTerms.length > 0) {
                tfidfTerms.slice(0, 8).forEach(t => {
                    const pill = document.createElement("span");
                    pill.className = "nlp-tag-pill tfidf";
                    pill.textContent = `${t.term} (${t.tfidf_score})`;
                    tfidfContainer.appendChild(pill);
                });
            } else {
                tfidfContainer.innerHTML = `<span style="font-size:0.75rem; color:var(--text-muted);">TF-IDF vector extracted across document vocabulary.</span>`;
            }
        }

        // ML Model Benchmark Metrics
        const mlMetrics = nlp.ml_model_metrics || {};
        const lrMetrics = mlMetrics.logistic_regression || {};
        const svmMetrics = mlMetrics.linear_svm || {};

        const lrAccEl = document.getElementById("ml-stat-lr-acc");
        const lrF1El = document.getElementById("ml-stat-lr-f1");
        const svmAccEl = document.getElementById("ml-stat-svm-acc");
        const svmF1El = document.getElementById("ml-stat-svm-f1");

        if (lrAccEl) lrAccEl.textContent = `${Math.round((lrMetrics.accuracy || 1.0) * 1000) / 10}%`;
        if (lrF1El) lrF1El.textContent = (lrMetrics.macro_f1 || 1.0).toFixed(4);
        if (svmAccEl) svmAccEl.textContent = `${Math.round((svmMetrics.accuracy || 1.0) * 1000) / 10}%`;
        if (svmF1El) svmF1El.textContent = (svmMetrics.macro_f1 || 1.0).toFixed(4);
    }

    // Toggle NLP Details Button
    const toggleNlpDetailsBtn = document.getElementById("toggle-nlp-details-btn");
    const nlpInspectorBody = document.getElementById("nlp-inspector-body");
    if (toggleNlpDetailsBtn && nlpInspectorBody) {
        toggleNlpDetailsBtn.addEventListener("click", () => {
            nlpInspectorBody.classList.toggle("hidden");
        });
    }

    // Render Contract DNA Strip
    function renderContractDnaStrip(clauses) {
        const dnaStrip = document.getElementById("contract-dna-strip");
        if (!dnaStrip) return;
        dnaStrip.innerHTML = "";

        if (!clauses || clauses.length === 0) {
            dnaStrip.innerHTML = `<span style="font-size: 0.8rem; color: var(--text-muted); padding: 8px;">No sections mapped</span>`;
            return;
        }

        clauses.forEach((clause, idx) => {
            const seg = document.createElement("div");
            const heatClass = (clause.heat_level || "safe").toLowerCase();
            const shortLabel = (clause.clause_number && clause.clause_number.length <= 3) ? clause.clause_number : String(idx + 1);
            
            seg.className = `dna-segment ${heatClass}`;
            seg.title = `Section ${shortLabel}: ${clause.title || 'Clause'} • Risk: ${clause.risk_score}/100 • Traps: ${clause.traps ? clause.traps.length : 0}`;
            
            // Only show numbers if there are 16 or fewer clauses to avoid visual clutter and smudging
            if (clauses.length <= 16) {
                seg.innerHTML = `<span class="dna-segment-num">${escapeHtml(shortLabel)}</span>`;
            }

            seg.addEventListener("click", () => {
                // If filter hides this clause, switch to ALL first
                if (activeFilter !== "ALL") {
                    filterBtns.forEach(b => b.classList.remove("active"));
                    const allBtn = document.querySelector(`.filter-btn[data-filter="ALL"]`);
                    if (allBtn) allBtn.classList.add("active");
                    activeFilter = "ALL";
                    renderClausesList();
                }

                const targetCard = document.getElementById(`clause-card-${clause.clause_id}`);
                if (targetCard) {
                    targetCard.scrollIntoView({ behavior: "smooth", block: "center" });
                    targetCard.classList.remove("clause-card-target-highlight");
                    void targetCard.offsetWidth; // trigger reflow
                    targetCard.classList.add("clause-card-target-highlight");
                }
            });

            dnaStrip.appendChild(seg);
        });
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

    // Render Clause Cards with Expandable Academic NLP Inspection
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
            card.id = `clause-card-${clause.clause_id}`;
            const heatClass = (clause.heat_level || "safe").toLowerCase();
            card.className = `clause-card ${heatClass}`;

            // TL;DR Plain English Box
            let tldrHtml = "";
            if (clause.tldr_summary) {
                tldrHtml = `
                    <div class="clause-tldr-box">
                        <span class="tldr-icon-wrap">💡</span>
                        <div class="tldr-content">
                            <span class="tldr-label">Plain English Summary</span>
                            <p class="tldr-text">${escapeHtml(clause.tldr_summary)}</p>
                        </div>
                    </div>
                `;
            }

            // Academic NLP Inspection Drawer for this clause
            const nlpData = clause.nlp_analysis || {};
            const mlData = clause.ml_classification || {};
            const predCat = mlData.predicted_category || "General";
            const confPct = mlData.confidence_pct || 0;
            const svmPred = mlData.svm_prediction || predCat;
            const topProbs = mlData.top_probabilities || [];
            
            const tokenStats = nlpData.token_stats || {};
            const modals = nlpData.modal_verbs || [];
            const lemmasSample = (nlpData.lemmas && nlpData.lemmas.sample_transformations) ? nlpData.lemmas.sample_transformations : [];
            const nerEntities = nlpData.named_entities || [];
            const tfidfTerms = nlpData.tfidf_salient_terms || [];
            const simScore = clause.benchmark_similarity !== undefined ? clause.benchmark_similarity : 0.0;

            const nlpAccordionHtml = `
                <details class="clause-nlp-details">
                    <summary class="clause-nlp-summary-bar">
                        <span>🔬 NLP Pipeline & ML Classification Inspector</span>
                        <span style="font-size: 0.72rem; color: var(--primary);">ML Class: <strong>${escapeHtml(predCat)}</strong> (${confPct}%) ▾</span>
                    </summary>
                    <div class="clause-nlp-content">
                        <!-- ML Prediction Box -->
                        <div class="clause-nlp-block">
                            <span class="clause-nlp-block-title">⚡ Supervised ML Classifier</span>
                            <div><strong>Predicted Category:</strong> <span class="badge-ml">${escapeHtml(predCat)}</span></div>
                            <div style="margin-top: 4px;"><strong>LogReg Confidence:</strong> ${confPct}%</div>
                            <div style="margin-top: 2px;"><strong>Linear SVM Class:</strong> ${escapeHtml(svmPred)}</div>
                            <div style="margin-top: 6px; font-size: 0.72rem; color: var(--text-muted);">
                                <strong>Top Probabilities:</strong>
                                ${topProbs.slice(0, 3).map(p => `<div>• ${escapeHtml(p.category)}: ${p.pct}%</div>`).join("")}
                            </div>
                        </div>

                        <!-- Linguistic & POS Box -->
                        <div class="clause-nlp-block">
                            <span class="clause-nlp-block-title">📝 Syntactic & POS Tags</span>
                            <div><strong>Tokens:</strong> ${tokenStats.total_tokens || 0} (${tokenStats.stopword_ratio_pct || 0}% Stopwords)</div>
                            <div style="margin-top: 4px;"><strong>Modal Verbs:</strong> ${modals.length > 0 ? modals.join(", ") : "None"}</div>
                            <div style="margin-top: 6px;">
                                <strong>Sample Lemmas:</strong>
                                <div class="nlp-tags-wrap" style="margin-top: 3px;">
                                    ${lemmasSample.slice(0, 3).map(l => `<span class="nlp-tag-pill">${escapeHtml(l.original)} → ${escapeHtml(l.lemma)}</span>`).join(" ")}
                                </div>
                            </div>
                        </div>

                        <!-- Named Entities (NER) -->
                        <div class="clause-nlp-block">
                            <span class="clause-nlp-block-title">🏷️ Legal Named Entities (NER)</span>
                            <div class="nlp-tags-wrap">
                                ${nerEntities.length > 0 ? nerEntities.slice(0, 5).map(e => `<span class="nlp-tag-pill entity-${e.label.toLowerCase().includes('money') ? 'money' : (e.label.toLowerCase().includes('date') ? 'date' : 'org')}">${escapeHtml(e.entity)} <small>(${escapeHtml(e.label)})</small></span>`).join(" ") : '<span style="color:var(--text-muted);">No specific legal entities extracted.</span>'}
                            </div>
                        </div>

                        <!-- TF-IDF & Semantic Similarity -->
                        <div class="clause-nlp-block">
                            <span class="clause-nlp-block-title">📊 TF-IDF & Semantic Similarity</span>
                            <div><strong>Market Benchmark Cosine Similarity:</strong> <span class="text-primary" style="font-weight: 700;">${simScore}</span></div>
                            <div style="margin-top: 6px;">
                                <strong>Top Salient Terms:</strong>
                                <div class="nlp-tags-wrap" style="margin-top: 3px;">
                                    ${tfidfTerms.slice(0, 4).map(t => `<span class="nlp-tag-pill tfidf">${escapeHtml(t.term)}</span>`).join(" ")}
                                </div>
                            </div>
                        </div>
                    </div>
                </details>
            `;

            let trapsHtml = "";
            if (clause.traps && clause.traps.length > 0) {
                clause.traps.forEach(trap => {
                    const redline = (currentAuditReport.redlines || []).find(r => r.clause_id === clause.clause_id && r.trap_category === trap.category);

                    let trapCategoryName = trap.category || '';
                    if (trapCategoryName.toLowerCase().includes("unilateral") && /terminate|cancell?ation/i.test(clause.text)) {
                        trapCategoryName = "Unilateral Termination Risk";
                    } else if (trapCategoryName.toLowerCase().includes("indemnif") && /liable\s+for\s+all\s+losses|without\s+limitation|unlimited\s+liability/i.test(clause.text)) {
                        trapCategoryName = "Unlimited Customer Liability Trap";
                    }

                    // Deduplicate and filter trigger pills (keep only 1 short, clean keyword if available)
                    const rawPats = trap.matched_patterns || [];
                    const shortTags = rawPats
                        .map(p => p.trim())
                        .filter(p => p.length > 2 && p.length <= 40 && !p.toLowerCase().startsWith("machine learning"))
                        .filter((p, idx, arr) => arr.indexOf(p) === idx)
                        .slice(0, 1);

                    trapsHtml += `
                        <div class="trap-box">
                            <div class="trap-head">
                                <span class="trap-name">⚠️ Trap Detected: ${escapeHtml(trapCategoryName)}</span>
                                <span class="badge ${trap.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${trap.severity === 'CRITICAL' ? 'High Risk' : 'Medium Risk'}</span>
                            </div>
                            <p class="trap-desc">${escapeHtml(trap.legal_danger || '')}</p>
                            ${shortTags.length > 0 ? `
                            <div class="trap-keywords">
                                <strong>Trigger phrase:</strong> 
                                ${shortTags.map(p => `<span>${escapeHtml(p)}</span>`).join(" ")}
                            </div>
                            ` : ''}

                            ${redline ? `
                            <div class="redline-box">
                                <div class="redline-title">✏️ Suggested Fair Replacement:</div>
                                <div class="redline-clean-text">
                                    ${escapeHtml(redline.recommended_text || '')}
                                </div>
                                ${redline.negotiation_talking_point ? `
                                <div class="talking-point-box">
                                    <strong>💬 Negotiation Tip:</strong> ${escapeHtml(redline.negotiation_talking_point)}
                                </div>
                                ` : ''}
                            </div>
                            ` : ''}
                        </div>
                    `;
                });
            }

            let readabilityBadgeHtml = '';
            if (clause.readability) {
                const grade = (typeof clause.readability === 'object' && clause.readability !== null)
                    ? (clause.readability.flesch_kincaid_grade !== undefined ? clause.readability.flesch_kincaid_grade : clause.readability.grade)
                    : clause.readability;
                if (grade !== undefined && grade !== null && String(grade).trim() !== '') {
                    readabilityBadgeHtml = `<span class="clause-readability-pill">📖 Grade ${escapeHtml(String(grade))}</span>`;
                }
            }

            let displayTitle = (clause.title || '').trim();
            if (/liable\s+for\s+all\s+losses|without\s+limitation|unlimited\s+liability/i.test(clause.text)) {
                displayTitle = "Limitation of Liability";
            } else if ((!displayTitle || displayTitle.toLowerCase().includes("preamble") || /^clause\s+\d+$/i.test(displayTitle) || /^section\s+\d+$/i.test(displayTitle)) && predCat && predCat !== "General" && predCat !== "Other") {
                displayTitle = predCat;
            }

            card.innerHTML = `
                <div class="clause-card-header">
                    <div class="clause-title-group">
                        <span class="clause-id">${escapeHtml(clause.clause_id || '')}</span>
                        <h4 class="clause-heading">${escapeHtml(displayTitle)}</h4>
                        ${readabilityBadgeHtml}
                    </div>
                    <div class="clause-badge-group">
                        <span class="deontic-pill">${escapeHtml(clause.deontic_profile ? clause.deontic_profile.dominant_category : '')}</span>
                        <span class="risk-pill ${heatClass}">Risk ${escapeHtml(String(clause.risk_score || 0))}</span>
                    </div>
                </div>
                ${tldrHtml}
                <div class="clause-body-text">${highlightClauseDangerText(clause)}</div>
                ${nlpAccordionHtml}
                ${trapsHtml}
            `;

            clausesList.appendChild(card);
        });
    }

    function highlightClauseDangerText(clause) {
        if (!clause || !clause.text) return "";
        const text = clause.text;
        if (!clause.traps || clause.traps.length === 0) {
            return escapeHtml(text);
        }

        // Collect all distinct matched patterns
        const patterns = [];
        const criticalSet = new Set();

        clause.traps.forEach(trap => {
            const isCritical = trap.severity === "CRITICAL" || trap.severity === "HIGH";
            (trap.matched_patterns || []).forEach(p => {
                const trimmed = (p || "").trim();
                if (trimmed.length >= 3 && !patterns.includes(trimmed)) {
                    patterns.push(trimmed);
                    if (isCritical) criticalSet.add(trimmed.toLowerCase());
                }
            });
        });

        if (patterns.length === 0) {
            return escapeHtml(text);
        }

        // Sort by length descending so longer compound phrases match first
        patterns.sort((a, b) => b.length - a.length);

        // Escape for regex and build master composite regex
        const escapedPatterns = patterns.map(p => p.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
        const masterRegex = new RegExp(`(${escapedPatterns.join("|")})`, "gi");

        // Split text by regex preserving matches
        const parts = text.split(masterRegex);
        let resultHtml = "";

        parts.forEach(part => {
            if (!part) return;
            const isMatch = patterns.some(p => p.toLowerCase() === part.toLowerCase());
            if (isMatch) {
                const isCrit = criticalSet.has(part.toLowerCase());
                const className = isCrit ? "highlight-danger" : "highlight-warning";
                resultHtml += `<mark class="${className}" title="⚠️ Risk Trigger: ${escapeHtml(part)}">${escapeHtml(part)}</mark>`;
            } else {
                resultHtml += escapeHtml(part);
            }
        });

        return resultHtml;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // =========================================================================
    // Multi-Format Export Report Controller (PDF, HTML, MD, TXT, Clipboard)
    // =========================================================================
    const exportModal = document.getElementById("export-modal");
    const exportModalBackdrop = document.getElementById("export-modal-backdrop");
    const closeExportModalBtn = document.getElementById("close-export-modal-btn");
    const cancelExportBtn = document.getElementById("cancel-export-btn");
    const exportOptPrint = document.getElementById("export-opt-print");
    const exportOptHtml = document.getElementById("export-opt-html");
    const exportOptMd = document.getElementById("export-opt-md");
    const exportOptTxt = document.getElementById("export-opt-txt");
    const copySummaryBtn = document.getElementById("copy-summary-btn");
    const exportCopyStatus = document.getElementById("export-copy-status");

    function openExportModal() {
        if (!currentAuditReport) {
            alert("Please run a contract audit first.");
            return;
        }
        if (exportModal) exportModal.classList.remove("hidden");
    }

    function closeExportModal() {
        if (exportModal) exportModal.classList.add("hidden");
    }

    if (exportMdBtn) exportMdBtn.addEventListener("click", openExportModal);
    if (closeExportModalBtn) closeExportModalBtn.addEventListener("click", closeExportModal);
    if (cancelExportBtn) cancelExportBtn.addEventListener("click", closeExportModal);
    if (exportModalBackdrop) exportModalBackdrop.addEventListener("click", closeExportModal);

    // Option 1: Print / Save as PDF
    if (exportOptPrint) {
        exportOptPrint.addEventListener("click", () => {
            closeExportModal();
            setTimeout(() => {
                window.print();
            }, 250);
        });
    }

    // Option 2: Download Standalone HTML Report
    if (exportOptHtml) {
        exportOptHtml.addEventListener("click", () => {
            if (!currentAuditReport) return;
            const rep = currentAuditReport;
            const docTitle = rep.document_name || "Contract";
            const dateStr = new Date().toLocaleDateString();

            let clausesHtml = "";
            (rep.clause_audit_details || []).forEach(c => {
                let trapsList = "";
                (c.traps || []).forEach(t => {
                    trapsList += `
                        <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px; margin-top:8px;">
                            <strong style="color:#991b1b;">⚠️ ${escapeHtml(t.category)} (${t.severity})</strong>
                            <p style="margin:4px 0; color:#7f1d1d; font-size:13px;"><strong>Risk:</strong> ${escapeHtml(t.legal_danger || '')}</p>
                            <p style="margin:4px 0; color:#065f46; font-size:13px;"><strong>Mitigation:</strong> ${escapeHtml(t.recommended_mitigation || '')}</p>
                        </div>
                    `;
                });

                clausesHtml += `
                    <div style="border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:14px; background:#ffffff;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <strong>${escapeHtml(c.clause_id)}: ${escapeHtml(c.title || 'Section')}</strong>
                            <span style="font-size:12px; padding:2px 8px; border-radius:12px; background:${c.heat_level === 'CRITICAL' ? '#fef2f2; color:#dc2626;' : '#ecfdf5; color:#059669;'}">${c.heat_level || 'SAFE'}</span>
                        </div>
                        <p style="font-size:14px; color:#334155; line-height:1.5; font-family:monospace; background:#f8fafc; padding:10px; border-radius:4px;">${escapeHtml(c.text)}</p>
                        ${trapsList}
                    </div>
                `;
            });

        let verdictActionHtml = '';
        let verdictActionTxt = '';
        const hScore = Math.round(rep.overall_health_score || 0);
        if (hScore >= 80) {
            verdictActionHtml = '<div style="background:#f0fdf4; border:1px solid #bbf7d0; border-left:5px solid #16a34a; padding:12px 16px; border-radius:6px; margin:16px 0; color:#166534;"><strong>✅ SAFE TO PROCEED:</strong> Safe to Agree / Proceed with Website Login & Account Creation. This agreement follows balanced standards.</div>';
            verdictActionTxt = 'CONCLUSION / ACTION: ✅ SAFE TO PROCEED - Safe for Website Login, Signup & Agreement';
        } else if (hScore >= 60) {
            verdictActionHtml = '<div style="background:#fffbeb; border:1px solid #fde68a; border-left:5px solid #d97706; padding:12px 16px; border-radius:6px; margin:16px 0; color:#92400e;"><strong>⚠️ PROCEED WITH CAUTION:</strong> Review account privacy settings and opt out of optional tracking or auto-renewals.</div>';
            verdictActionTxt = 'CONCLUSION / ACTION: ⚠️ PROCEED WITH CAUTION - Review Privacy & Sharing Settings';
        } else if (hScore >= 40) {
            verdictActionHtml = '<div style="background:#fffbeb; border:1px solid #fde68a; border-left:5px solid #d97706; padding:12px 16px; border-radius:6px; margin:16px 0; color:#92400e;"><strong>⚠️ RISKY - AVOID AGREEING BLINDLY:</strong> High caution advised. Avoid providing confidential files or sensitive personal data.</div>';
            verdictActionTxt = 'CONCLUSION / ACTION: ⚠️ RISKY - Do NOT Agree Without Review';
        } else {
            verdictActionHtml = '<div style="background:#fef2f2; border:1px solid #fecaca; border-left:5px solid #dc2626; padding:12px 16px; border-radius:6px; margin:16px 0; color:#991b1b;"><strong>🚫 DO NOT PROCEED / AVOID:</strong> Avoid creating an account, logging in, or agreeing. Contains aggressive predatory terms and legal rights waivers.</div>';
            verdictActionTxt = 'CONCLUSION / ACTION: 🚫 DO NOT PROCEED / AVOID - Avoid Account Creation or Login';
        }

        const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LexiTrap Audit Report - ${escapeHtml(docTitle)}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:#f8fafc; color:#0f172a; padding:30px; margin:0; line-height:1.5; }
        .container { max-width:860px; margin:0 auto; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:32px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05); }
        .badge { display:inline-block; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:bold; }
        .score-box { display:flex; justify-content:space-between; align-items:center; background:#f1f5f9; padding:20px; border-radius:8px; margin:20px 0; }
        .stat-grid { display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:24px; text-align:center; }
        .stat-card { background:#f8fafc; border:1px solid #e2e8f0; padding:12px; border-radius:6px; }
        .stat-val { font-size:20px; font-weight:800; display:block; }
    </style>
</head>
<body>
    <div class="container">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:16px;">
            <div>
                <h1 style="margin:0 0 4px 0; font-size:24px;">⚖️ LexiTrap Legal Contract Audit</h1>
                <p style="margin:0; color:#64748b; font-size:14px;">Document: <strong>${escapeHtml(docTitle)}</strong> • Generated: ${dateStr}</p>
            </div>
            <span class="badge" style="background:#2563eb; color:#ffffff;">NLP Audit</span>
        </div>

        <div class="score-box">
            <div>
                <h2 style="margin:0; font-size:28px; color:${rep.overall_health_score >= 80 ? '#059669' : (rep.overall_health_score >= 60 ? '#d97706' : '#dc2626')};">
                    Health Score: ${Math.round(rep.overall_health_score)}/100 (Grade ${rep.letter_grade})
                </h2>
                <p style="margin:4px 0 0 0; color:#475569; font-size:14px;">${escapeHtml(rep.verdict_title || '')} — ${escapeHtml(rep.verdict_description || '')}</p>
            </div>
        </div>

        ${verdictActionHtml}

        <div class="stat-grid">
            <div class="stat-card"><span class="stat-val" style="color:#dc2626;">${rep.total_traps_found}</span><span style="font-size:12px; color:#64748b;">Traps Found</span></div>
            <div class="stat-card"><span class="stat-val" style="color:#dc2626;">${rep.critical_traps_count}</span><span style="font-size:12px; color:#64748b;">High Risk</span></div>
            <div class="stat-card"><span class="stat-val" style="color:#d97706;">${rep.high_traps_count}</span><span style="font-size:12px; color:#64748b;">Medium Risk</span></div>
            <div class="stat-card"><span class="stat-val" style="color:#2563eb;">${rep.total_clauses}</span><span style="font-size:12px; color:#64748b;">Total Sections</span></div>
        </div>

        <h3 style="border-bottom:1px solid #e2e8f0; padding-bottom:6px;">Executive Summary</h3>
        <ul>
            ${(rep.executive_summary_points || []).map(p => `<li>${escapeHtml(p)}</li>`).join('')}
        </ul>

        <h3 style="border-bottom:1px solid #e2e8f0; padding-bottom:6px; margin-top:28px;">Section-by-Section Findings</h3>
        ${clausesHtml}
    </div>
</body>
</html>`;

            downloadTextFile(`LexiTrap_Audit_${docTitle.replace(/[^a-zA-Z0-9_-]/g, '_')}.html`, htmlContent);
            closeExportModal();
        });
    }

    // Option 3: Download Markdown
    if (exportOptMd) {
        exportOptMd.addEventListener("click", async () => {
            if (!currentAuditReport) return;
            try {
                const res = await fetch("/api/export", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ report: currentAuditReport })
                });

                const text = await res.text();
                const safeName = (currentAuditReport.document_name || "Report").replace(/[^a-zA-Z0-9_-]/g, "_");
                downloadTextFile(`LexiTrap_Audit_${safeName}.md`, text);
                closeExportModal();
            } catch (err) {
                console.error("Export error:", err);
                alert("Failed to export Markdown report.");
            }
        });
    }

    // Option 4: Download Plain Text
    function generateCleanPlainTextSummary(rep) {
        let actLine = 'CONCLUSION / ACTION: 🚫 DO NOT PROCEED / AVOID - Avoid Account Creation or Login';
        const sc = Math.round(rep.overall_health_score || 0);
        if (sc >= 80) actLine = 'CONCLUSION / ACTION: ✅ SAFE TO PROCEED - Safe for Website Login, Signup & Agreement';
        else if (sc >= 60) actLine = 'CONCLUSION / ACTION: ⚠️ PROCEED WITH CAUTION - Review Privacy & Sharing Settings';
        else if (sc >= 40) actLine = 'CONCLUSION / ACTION: ⚠️ RISKY - Do NOT Agree Without Review';

        const lines = [
            `========================================================================`,
            `LEXITRAP LEGAL CONTRACT AUDIT REPORT`,
            `Document: ${rep.document_name || 'Contract'}`,
            `Date: ${new Date().toLocaleDateString()}`,
            `========================================================================`,
            ``,
            `HEALTH SCORE: ${Math.round(rep.overall_health_score)}/100 (Grade ${rep.letter_grade})`,
            `RISK LEVEL: ${rep.risk_level}`,
            `VERDICT: ${rep.verdict_title} - ${rep.verdict_description}`,
            ``,
            `>>> ${actLine} <<<`,
            ``,
            `STATISTICS:`,
            `- Total Sections Analyzed: ${rep.total_clauses}`,
            `- Predatory Traps Found: ${rep.total_traps_found}`,
            `- Critical Risk Traps: ${rep.critical_traps_count}`,
            `- Medium Risk Traps: ${rep.high_traps_count}`,
            ``,
            `EXECUTIVE SUMMARY:`,
            ...(rep.executive_summary_points || []).map(p => `* ${p}`),
            ``,
            `========================================================================`,
            `FLAGGED CLAUSES & MITIGATIONS`,
            `========================================================================`,
        ];

        (rep.clause_audit_details || []).forEach(c => {
            if (c.has_traps) {
                lines.push(``);
                lines.push(`SECTION ${c.clause_id}: ${c.title || 'Clause'} [Risk: ${c.risk_score}/100 - ${c.heat_level}]`);
                lines.push(`Original Text: ${c.text}`);
                (c.traps || []).forEach(t => {
                    lines.push(`  * Trap: ${t.category} (${t.severity})`);
                    lines.push(`    Danger: ${t.legal_danger}`);
                    lines.push(`    Mitigation: ${t.recommended_mitigation}`);
                });
            }
        });

        return lines.join('\n');
    }

    if (exportOptTxt) {
        exportOptTxt.addEventListener("click", () => {
            if (!currentAuditReport) return;
            const plainTxt = generateCleanPlainTextSummary(currentAuditReport);
            const safeName = (currentAuditReport.document_name || "Report").replace(/[^a-zA-Z0-9_-]/g, "_");
            downloadTextFile(`LexiTrap_Audit_${safeName}.txt`, plainTxt);
            closeExportModal();
        });
    }

    // Copy Summary to Clipboard
    if (copySummaryBtn) {
        copySummaryBtn.addEventListener("click", async () => {
            if (!currentAuditReport) return;
            const plainTxt = generateCleanPlainTextSummary(currentAuditReport);
            try {
                await navigator.clipboard.writeText(plainTxt);
                if (exportCopyStatus) {
                    exportCopyStatus.classList.remove("hidden");
                    setTimeout(() => exportCopyStatus.classList.add("hidden"), 3000);
                }
            } catch (err) {
                console.error("Copy error:", err);
            }
        });
    }


    // =========================================================================
    // Feature 3: Clean & Fair Contract Generator Modal Controller
    // =========================================================================
    const generateCleanBtn = document.getElementById("generate-clean-btn");
    const cleanContractModal = document.getElementById("clean-contract-modal");
    const cleanModalBackdrop = document.getElementById("clean-modal-backdrop");
    const closeCleanModalBtn = document.getElementById("close-clean-modal-btn");
    const cleanContractTextarea = document.getElementById("clean-contract-textarea");
    const cleanModCount = document.getElementById("clean-mod-count");
    const copyCleanBtn = document.getElementById("copy-clean-btn");
    const cleanCopyStatus = document.getElementById("clean-copy-status");
    const downloadCleanTxtBtn = document.getElementById("download-clean-txt-btn");
    const downloadCleanMdBtn = document.getElementById("download-clean-md-btn");

    function closeCleanModal() {
        if (cleanContractModal) cleanContractModal.classList.add("hidden");
    }

    if (closeCleanModalBtn) closeCleanModalBtn.addEventListener("click", closeCleanModal);
    if (cleanModalBackdrop) cleanModalBackdrop.addEventListener("click", closeCleanModal);

    if (generateCleanBtn) {
        generateCleanBtn.addEventListener("click", async () => {
            const text = contractTextarea.value.trim();
            const docName = docNameInput.value.trim() || "Clean Contract";
            if (!text) {
                alert("Please input or audit a contract first.");
                return;
            }

            const originalBtnText = generateCleanBtn.innerHTML;
            generateCleanBtn.innerHTML = "<span>⏳</span> Generating Clean Draft...";
            generateCleanBtn.disabled = true;

            try {
                const res = await fetch("/api/clean-contract", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: text, name: docName })
                });

                const data = await res.json();
                if (data.status === "success") {
                    cleanContractTextarea.value = data.clean_text;
                    cleanModCount.textContent = data.modifications_count || 0;
                    if (cleanCopyStatus) cleanCopyStatus.classList.add("hidden");
                    cleanContractModal.classList.remove("hidden");
                } else {
                    alert("Failed to generate clean contract: " + (data.message || "Unknown error"));
                }
            } catch (err) {
                console.error("Clean contract generation error:", err);
                alert("An error occurred while generating the clean contract.");
            } finally {
                generateCleanBtn.innerHTML = originalBtnText;
                generateCleanBtn.disabled = false;
            }
        });
    }

    if (copyCleanBtn) {
        copyCleanBtn.addEventListener("click", async () => {
            if (!cleanContractTextarea.value) return;
            try {
                await navigator.clipboard.writeText(cleanContractTextarea.value);
                if (cleanCopyStatus) {
                    cleanCopyStatus.classList.remove("hidden");
                    setTimeout(() => cleanCopyStatus.classList.add("hidden"), 3000);
                }
            } catch (err) {
                console.error("Copy error:", err);
                cleanContractTextarea.select();
                document.execCommand("copy");
                if (cleanCopyStatus) cleanCopyStatus.classList.remove("hidden");
            }
        });
    }

    function downloadTextFile(filename, content) {
        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }

    if (downloadCleanTxtBtn) {
        downloadCleanTxtBtn.addEventListener("click", () => {
            const text = cleanContractTextarea.value;
            if (!text) return;
            downloadTextFile(`clean_contract_${Date.now()}.txt`, text);
        });
    }

    if (downloadCleanMdBtn) {
        downloadCleanMdBtn.addEventListener("click", () => {
            const text = cleanContractTextarea.value;
            if (!text) return;
            const mdContent = `# Clean & Fair Contract Agreement\n\n*Generated by LexiTrap NLP System on ${new Date().toLocaleDateString()}*\n\n---\n\n${text}\n`;
            downloadTextFile(`clean_contract_${Date.now()}.md`, mdContent);
        });
    }

    // =========================================================================
    // Feature 4: Draft A vs Draft B Version Diff Analyzer Modal Controller
    // =========================================================================
    const openCompareBtn = document.getElementById("open-compare-btn");
    const compareModal = document.getElementById("compare-modal");
    const compareModalBackdrop = document.getElementById("compare-modal-backdrop");
    const closeCompareModalBtn = document.getElementById("close-compare-modal-btn");
    const draftAText = document.getElementById("draft-a-text");
    const draftBText = document.getElementById("draft-b-text");
    const btnUseCurrentForA = document.getElementById("btn-use-current-for-a");
    const btnUseCleanForB = document.getElementById("btn-use-clean-for-b");
    const runCompareBtn = document.getElementById("run-compare-btn");
    const compareInputsStage = document.getElementById("compare-inputs-stage");
    const compareResultsStage = document.getElementById("compare-results-stage");
    const deltaRiskScore = document.getElementById("delta-risk-score");
    const deltaRiskDesc = document.getElementById("delta-risk-desc");
    const deltaHealthScore = document.getElementById("delta-health-score");
    const deltaTrapsCount = document.getElementById("delta-traps-count");
    const eliminatedTrapsBox = document.getElementById("eliminated-traps-box");
    const eliminatedBadgesList = document.getElementById("eliminated-badges-list");
    const draftASummaryBox = document.getElementById("draft-a-summary-box");
    const draftBSummaryBox = document.getElementById("draft-b-summary-box");
    const resetCompareBtn = document.getElementById("reset-compare-btn");

    function openCompareModal() {
        if (compareModal) {
            compareModal.classList.remove("hidden");
            // Auto populate Draft A if current text exists and Draft A is empty
            if (contractTextarea.value && !draftAText.value) {
                draftAText.value = contractTextarea.value;
            }
        }
    }

    function closeCompareModal() {
        if (compareModal) compareModal.classList.add("hidden");
    }

    if (openCompareBtn) openCompareBtn.addEventListener("click", openCompareModal);
    if (closeCompareModalBtn) closeCompareModalBtn.addEventListener("click", closeCompareModal);
    if (compareModalBackdrop) compareModalBackdrop.addEventListener("click", closeCompareModal);

    if (btnUseCurrentForA) {
        btnUseCurrentForA.addEventListener("click", () => {
            draftAText.value = contractTextarea.value;
        });
    }

    if (btnUseCleanForB) {
        btnUseCleanForB.addEventListener("click", async () => {
            const baseText = draftAText.value.trim() || contractTextarea.value.trim();
            if (!baseText) {
                alert("Please paste text into Draft A first.");
                return;
            }

            btnUseCleanForB.textContent = "⏳ Generating...";
            btnUseCleanForB.disabled = true;

            try {
                const res = await fetch("/api/clean-contract", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: baseText })
                });
                const data = await res.json();
                if (data.status === "success") {
                    draftBText.value = data.clean_text;
                } else {
                    alert("Could not generate clean draft: " + (data.message || ""));
                }
            } catch (err) {
                console.error("Clean error:", err);
            } finally {
                btnUseCleanForB.textContent = "Use Clean Redline";
                btnUseCleanForB.disabled = false;
            }
        });
    }

    if (runCompareBtn) {
        runCompareBtn.addEventListener("click", async () => {
            const textA = draftAText.value.trim();
            const textB = draftBText.value.trim();

            if (!textA || !textB) {
                alert("Please enter text for both Draft A and Draft B to compare.");
                return;
            }

            const origHtml = runCompareBtn.innerHTML;
            runCompareBtn.innerHTML = "<span>⏳</span> Analyzing Both Drafts...";
            runCompareBtn.disabled = true;

            try {
                const res = await fetch("/api/compare-drafts", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ draft_a: textA, draft_b: textB })
                });

                const data = await res.json();
                if (data.status === "success") {
                    renderCompareResults(data);
                } else {
                    alert("Comparison audit failed: " + (data.message || "Unknown error"));
                }
            } catch (err) {
                console.error("Compare error:", err);
                alert("Failed to compare drafts.");
            } finally {
                runCompareBtn.innerHTML = origHtml;
                runCompareBtn.disabled = false;
            }
        });
    }

    function renderCompareResults(data) {
        const delta = data.comparison || {};
        const repA = data.draft_a_report || delta.report_a || {};
        const repB = data.draft_b_report || delta.report_b || {};

        // Render Delta Banner
        // delta_risk = report_a.risk - report_b.risk
        // If positive (e.g. 35), Draft B reduced risk by 35 points (Safer)
        const riskDelta = delta.delta_risk !== undefined ? delta.delta_risk : (delta.delta_risk_score !== undefined ? delta.delta_risk_score : 0);
        const healthDelta = delta.delta_health !== undefined ? delta.delta_health : (delta.delta_health_score !== undefined ? delta.delta_health_score : 0);

        deltaRiskScore.textContent = `${riskDelta > 0 ? '-' : (riskDelta < 0 ? '+' : '')}${Math.abs(riskDelta)} pts`;
        deltaRiskScore.className = `delta-number ${riskDelta >= 0 ? 'text-success' : 'text-danger'}`;
        deltaRiskDesc.textContent = riskDelta > 0 
            ? `Draft B reduced risk by ${riskDelta} points 🎉` 
            : (riskDelta === 0 ? 'Risk is identical across drafts' : `Draft B increased risk by ${Math.abs(riskDelta)} points ⚠️`);

        deltaHealthScore.textContent = `${healthDelta > 0 ? '+' : (healthDelta < 0 ? '-' : '')}${Math.abs(healthDelta)} pts`;
        deltaHealthScore.className = `delta-number ${healthDelta >= 0 ? 'text-success' : 'text-danger'}`;

        deltaTrapsCount.textContent = delta.traps_eliminated_count || 0;

        // Eliminated Badges
        if (delta.eliminated_categories && delta.eliminated_categories.length > 0) {
            eliminatedTrapsBox.classList.remove("hidden");
            eliminatedBadgesList.innerHTML = "";
            delta.eliminated_categories.forEach(cat => {
                const badge = document.createElement("span");
                badge.className = "eliminated-badge";
                badge.innerHTML = `<span>✓</span> ${escapeHtml(cat)}`;
                eliminatedBadgesList.appendChild(badge);
            });
        } else {
            eliminatedTrapsBox.classList.add("hidden");
        }

        // Draft A Findings Box
        const healthA = Math.round(repA.overall_health_score || 0);
        const gradeA = repA.letter_grade || 'N/A';
        const readGradeA = repA.readability_profile ? repA.readability_profile.flesch_kincaid_grade : 'N/A';
        const obfA = repA.readability_profile ? repA.readability_profile.obfuscation_level : 'N/A';

        draftASummaryBox.innerHTML = `
            <div class="draft-stat-row"><span>Health Score:</span> <strong>${healthA}/100 (Grade ${gradeA})</strong></div>
            <div class="draft-stat-row"><span>Risk Severity:</span> <strong class="text-danger">${escapeHtml(repA.risk_level || 'Moderate')}</strong></div>
            <div class="draft-stat-row"><span>Traps Flagged:</span> <strong class="text-danger">${repA.total_traps_found || 0}</strong></div>
            <div class="draft-stat-row"><span>Critical Traps:</span> <strong>${repA.critical_traps_count || 0}</strong></div>
            <div class="draft-stat-row"><span>Readability Grade:</span> <strong>Grade ${readGradeA}</strong></div>
            <div class="draft-stat-row"><span>Language Clarity:</span> <strong>${escapeHtml(obfA)}</strong></div>
        `;

        // Draft B Findings Box
        const healthB = Math.round(repB.overall_health_score || 0);
        const gradeB = repB.letter_grade || 'N/A';
        const readGradeB = repB.readability_profile ? repB.readability_profile.flesch_kincaid_grade : 'N/A';
        const obfB = repB.readability_profile ? repB.readability_profile.obfuscation_level : 'N/A';

        draftBSummaryBox.innerHTML = `
            <div class="draft-stat-row"><span>Health Score:</span> <strong class="text-success">${healthB}/100 (Grade ${gradeB})</strong></div>
            <div class="draft-stat-row"><span>Risk Severity:</span> <strong class="${repB.risk_level === 'SAFE' ? 'text-success' : 'text-warning'}">${escapeHtml(repB.risk_level || 'Safe')}</strong></div>
            <div class="draft-stat-row"><span>Traps Flagged:</span> <strong class="text-success">${repB.total_traps_found || 0}</strong></div>
            <div class="draft-stat-row"><span>Critical Traps:</span> <strong>${repB.critical_traps_count || 0}</strong></div>
            <div class="draft-stat-row"><span>Readability Grade:</span> <strong>Grade ${readGradeB}</strong></div>
            <div class="draft-stat-row"><span>Language Clarity:</span> <strong>${escapeHtml(obfB)}</strong></div>
        `;

        compareInputsStage.classList.add("hidden");
        compareResultsStage.classList.remove("hidden");
    }

    if (resetCompareBtn) {
        resetCompareBtn.addEventListener("click", () => {
            compareResultsStage.classList.add("hidden");
            compareInputsStage.classList.remove("hidden");
        });
    }

    updateTextStats();
});

