/**
 * Advanced OpenAI Features JavaScript
 * Handles all frontend interactions for advanced OpenAI capabilities
 */

class AdvancedOpenAIFeatures {
    constructor() {
        this.init();
        this.setupEventListeners();
        this.loadSystemStatus();
        this.selectedVoice = 'nova';
        this.activeSessions = new Map();
        this.batchJobs = new Map();
        this.resultHistory = [];
    }

    init() {
        console.log('🔮 Advanced OpenAI Features initialized');
        this.updateSessionId();
    }

    setupEventListeners() {
        // System status and controls
        document.getElementById('refresh-status')?.addEventListener('click', () => this.loadSystemStatus());
        document.getElementById('cleanup-sessions')?.addEventListener('click', () => this.cleanupSessions());

        // Vision Analysis
        this.setupVisionListeners();
        
        // Structured Reports
        this.setupStructuredListeners();
        
        // Real-time Chat
        this.setupRealtimeListeners();
        
        // Batch Processing
        this.setupBatchListeners();
        
        // Enhanced Embeddings
        this.setupEmbeddingsListeners();
        
        // Function Calling
        this.setupFunctionsListeners();

        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.handleTabSwitch(e.target.getAttribute('data-bs-target'));
            });
        });
    }

    // System Status Management
    async loadSystemStatus() {
        const indicator = document.getElementById('system-status-indicator');
        const metricsContainer = document.getElementById('system-metrics');
        
        indicator.className = 'status-indicator status-loading';
        
        try {
            const response = await fetch('/api/advanced/status');
            const data = await response.json();
            
            if (data.success) {
                indicator.className = 'status-indicator status-online';
                this.displaySystemMetrics(data.status, metricsContainer);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('System status error:', error);
            indicator.className = 'status-indicator status-offline';
            metricsContainer.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        Unable to load system status: ${error.message}
                    </div>
                </div>
            `;
        }
    }

    displaySystemMetrics(status, container) {
        const metrics = [
            { label: 'Active Sessions', value: status.active_sessions || 0, icon: 'comments' },
            { label: 'Batch Jobs', value: status.batch_jobs || 0, icon: 'layer-group' },
            { label: 'Total Requests', value: status.total_requests || 0, icon: 'chart-line' },
            { label: 'Success Rate', value: `${status.success_rate || 100}%`, icon: 'check-circle' }
        ];

        container.innerHTML = metrics.map(metric => `
            <div class="col-lg-3 col-md-6">
                <div class="metric-card">
                    <div class="metric-value">
                        <i class="fas fa-${metric.icon} me-2"></i>
                        ${metric.value}
                    </div>
                    <div class="metric-label">${metric.label}</div>
                </div>
            </div>
        `).join('');
    }

    async cleanupSessions() {
        try {
            const response = await fetch('/api/advanced/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ max_age_hours: 24 })
            });
            
            const data = await response.json();
            if (data.success) {
                this.showNotification('Sessions cleaned up successfully', 'success');
                this.loadSystemStatus();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Cleanup failed: ${error.message}`, 'error');
        }
    }

    // Vision Analysis
    setupVisionListeners() {
        const uploadZone = document.getElementById('visionUploadZone');
        const fileInput = document.getElementById('visionFile');
        const analyzeBtn = document.getElementById('analyzeImage');
        const maxTokensSlider = document.getElementById('maxTokens');
        const maxTokensValue = document.getElementById('maxTokensValue');

        // File upload handling
        uploadZone?.addEventListener('click', () => fileInput?.click());
        uploadZone?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        uploadZone?.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        uploadZone?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                this.updateVisionUploadDisplay(files[0]);
            }
        });

        fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.updateVisionUploadDisplay(e.target.files[0]);
            }
        });

        maxTokensSlider?.addEventListener('input', (e) => {
            maxTokensValue.textContent = e.target.value;
        });

        analyzeBtn?.addEventListener('click', () => this.analyzeImage());
    }

    updateVisionUploadDisplay(file) {
        const uploadZone = document.getElementById('visionUploadZone');
        uploadZone.innerHTML = `
            <i class="fas fa-image fa-2x mb-2"></i>
            <p><strong>${file.name}</strong></p>
            <small class="text-muted">${this.formatFileSize(file.size)} - Click to change</small>
        `;
    }

    async analyzeImage() {
        const fileInput = document.getElementById('visionFile');
        const analysisType = document.getElementById('analysisType').value;
        const useContext = document.getElementById('useContext').checked;
        const maxTokens = document.getElementById('maxTokens').value;

        if (!fileInput.files.length) {
            this.showNotification('Please select an image to analyze', 'warning');
            return;
        }

        const analyzeBtn = document.getElementById('analyzeImage');
        const originalText = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('analysis_type', analysisType);
            formData.append('use_context', useContext);
            formData.append('max_tokens', maxTokens);

            const response = await fetch('/api/vision/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                this.displayVisionResult(data);
                bootstrap.Modal.getInstance(document.getElementById('visionModal')).hide();
                this.switchToResultsTab();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Vision analysis failed: ${error.message}`, 'error');
        } finally {
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    }

    displayVisionResult(data) {
        const result = {
            type: 'vision',
            timestamp: new Date().toISOString(),
            data: data
        };

        this.addToResults(result);
        this.resultHistory.push(result);
    }

    // Structured Reports
    setupStructuredListeners() {
        const generateBtn = document.getElementById('generateReport');
        const loadSampleBtn = document.getElementById('loadSampleData');
        const reportTypeSelect = document.getElementById('reportType');

        generateBtn?.addEventListener('click', () => this.generateStructuredReport());
        loadSampleBtn?.addEventListener('click', () => this.loadSampleData());
        
        reportTypeSelect?.addEventListener('change', (e) => {
            this.updateReportSchema(e.target.value);
        });
    }

    loadSampleData() {
        const reportType = document.getElementById('reportType').value;
        const sourceDataTextarea = document.getElementById('sourceData');
        
        const sampleData = {
            business: {
                revenue: 1250000,
                quarterly_growth: 15.3,
                expenses: 980000,
                market_share: 12.5,
                customer_satisfaction: 4.2,
                key_initiatives: ["Digital transformation", "Market expansion", "Cost optimization"]
            },
            technical: {
                system_performance: {
                    uptime: 99.8,
                    response_time: 145,
                    throughput: 1250
                },
                security_metrics: {
                    vulnerabilities: 2,
                    patches_applied: 15,
                    security_score: 8.5
                },
                development_stats: {
                    deployments: 23,
                    bug_fixes: 47,
                    features_released: 8
                }
            },
            analysis: {
                data_points: 1500,
                trends_identified: ["Increased usage", "Seasonal patterns", "User behavior shifts"],
                key_findings: ["Performance improved by 25%", "User engagement up 40%"],
                recommendations: ["Scale infrastructure", "Optimize user experience"]
            }
        };

        sourceDataTextarea.value = JSON.stringify(sampleData[reportType] || sampleData.analysis, null, 2);
    }

    async generateStructuredReport() {
        const reportType = document.getElementById('reportType').value;
        const sourceData = document.getElementById('sourceData').value;

        if (!sourceData.trim()) {
            this.showNotification('Please provide source data', 'warning');
            return;
        }

        let parsedData;
        try {
            parsedData = JSON.parse(sourceData);
        } catch (error) {
            this.showNotification('Invalid JSON format in source data', 'error');
            return;
        }

        const generateBtn = document.getElementById('generateReport');
        const originalText = generateBtn.innerHTML;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        generateBtn.disabled = true;

        try {
            const response = await fetch('/api/structured/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    data: parsedData,
                    report_type: reportType
                })
            });

            const data = await response.json();
            if (data.success) {
                this.displayStructuredResult(data);
                bootstrap.Modal.getInstance(document.getElementById('structuredModal')).hide();
                this.switchToResultsTab();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Report generation failed: ${error.message}`, 'error');
        } finally {
            generateBtn.innerHTML = originalText;
            generateBtn.disabled = false;
        }
    }

    displayStructuredResult(data) {
        const result = {
            type: 'structured_report',
            timestamp: new Date().toISOString(),
            data: data
        };

        this.addToResults(result);
        this.resultHistory.push(result);
    }

    // Real-time Chat
    setupRealtimeListeners() {
        const startBtn = document.getElementById('startSession');
        const voiceOptions = document.querySelectorAll('.voice-option');

        voiceOptions.forEach(option => {
            option.addEventListener('click', () => {
                voiceOptions.forEach(v => v.classList.remove('selected'));
                option.classList.add('selected');
                this.selectedVoice = option.dataset.voice;
            });
        });

        startBtn?.addEventListener('click', () => this.startRealtimeSession());
    }

    updateSessionId() {
        const sessionIdInput = document.getElementById('sessionId');
        if (sessionIdInput) {
            sessionIdInput.placeholder = `session_${Date.now()}`;
        }
    }

    async startRealtimeSession() {
        const sessionId = document.getElementById('sessionId').value || `session_${Date.now()}`;
        const instructions = document.getElementById('sessionInstructions').value;

        const startBtn = document.getElementById('startSession');
        const originalText = startBtn.innerHTML;
        startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
        startBtn.disabled = true;

        try {
            const response = await fetch('/api/realtime/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    voice: this.selectedVoice,
                    instructions: instructions
                })
            });

            const data = await response.json();
            if (data.success) {
                this.activeSessions.set(sessionId, data.session);
                this.displayRealtimeSession(sessionId, data.session);
                bootstrap.Modal.getInstance(document.getElementById('realtimeModal')).hide();
                this.switchToSessionsTab();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Session creation failed: ${error.message}`, 'error');
        } finally {
            startBtn.innerHTML = originalText;
            startBtn.disabled = false;
        }
    }

    displayRealtimeSession(sessionId, sessionData) {
        const sessionsContainer = document.getElementById('sessions-container');
        
        // Clear empty state if this is the first session
        if (this.activeSessions.size === 1) {
            sessionsContainer.innerHTML = '';
        }

        const sessionElement = document.createElement('div');
        sessionElement.className = 'realtime-session';
        sessionElement.id = `session-${sessionId}`;
        sessionElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">
                    <i class="fas fa-comments text-primary"></i>
                    ${sessionId}
                </h6>
                <div>
                    <span class="badge bg-success">Active</span>
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="advancedFeatures.endRealtimeSession('${sessionId}')">
                        <i class="fas fa-stop"></i> End
                    </button>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <small class="text-muted">Voice: ${sessionData.voice || this.selectedVoice}</small>
                </div>
                <div class="col-md-6">
                    <small class="text-muted">Started: ${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
            ${sessionData.instructions ? `<div class="mt-2"><small><strong>Instructions:</strong> ${sessionData.instructions}</small></div>` : ''}
        `;

        sessionsContainer.appendChild(sessionElement);
    }

    async endRealtimeSession(sessionId) {
        try {
            const response = await fetch(`/api/realtime/session/${sessionId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                this.activeSessions.delete(sessionId);
                document.getElementById(`session-${sessionId}`)?.remove();
                
                // Show empty state if no sessions remain
                if (this.activeSessions.size === 0) {
                    document.getElementById('sessions-container').innerHTML = `
                        <div class="text-center text-muted py-5">
                            <i class="fas fa-comments fa-3x mb-3"></i>
                            <h5>No active sessions</h5>
                            <p>Start a real-time conversation to see active sessions.</p>
                        </div>
                    `;
                }
                
                this.showNotification('Session ended successfully', 'success');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Failed to end session: ${error.message}`, 'error');
        }
    }

    // Batch Processing
    setupBatchListeners() {
        const uploadZone = document.getElementById('batchUploadZone');
        const fileInput = document.getElementById('batchFiles');
        const submitBtn = document.getElementById('submitBatch');
        const processingTypeSelect = document.getElementById('processingType');

        // File upload handling
        uploadZone?.addEventListener('click', () => fileInput?.click());
        uploadZone?.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        uploadZone?.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        uploadZone?.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            this.updateBatchFileList();
        });

        fileInput?.addEventListener('change', () => this.updateBatchFileList());
        submitBtn?.addEventListener('click', () => this.submitBatchProcessing());
        
        processingTypeSelect?.addEventListener('change', (e) => {
            const customDiv = document.getElementById('customInstructionsDiv');
            customDiv.style.display = e.target.value === 'custom' ? 'block' : 'none';
        });
    }

    updateBatchFileList() {
        const fileInput = document.getElementById('batchFiles');
        const fileList = document.getElementById('fileList');
        
        if (fileInput.files.length === 0) {
            fileList.innerHTML = '';
            return;
        }

        const files = Array.from(fileInput.files);
        fileList.innerHTML = `
            <div class="mt-2">
                <h6>Selected Files (${files.length}):</h6>
                ${files.map(file => `
                    <div class="d-flex justify-content-between align-items-center py-1">
                        <span>${file.name}</span>
                        <small class="text-muted">${this.formatFileSize(file.size)}</small>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async submitBatchProcessing() {
        const fileInput = document.getElementById('batchFiles');
        const processingType = document.getElementById('processingType').value;
        const customInstructions = document.getElementById('customInstructions').value;

        if (fileInput.files.length === 0) {
            this.showNotification('Please select files to process', 'warning');
            return;
        }

        const submitBtn = document.getElementById('submitBatch');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        submitBtn.disabled = true;

        try {
            const formData = new FormData();
            
            Array.from(fileInput.files).forEach((file, index) => {
                formData.append(`file_${index}`, file);
            });
            
            formData.append('processing_type', processingType);
            if (customInstructions) {
                formData.append('custom_instructions', customInstructions);
            }

            const response = await fetch('/api/batch/submit', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (data.success) {
                this.batchJobs.set(data.batch_id, {
                    id: data.batch_id,
                    processing_type: processingType,
                    document_count: data.document_count,
                    submitted_at: new Date().toISOString(),
                    status: 'submitted'
                });
                
                this.displayBatchJob(data.batch_id);
                bootstrap.Modal.getInstance(document.getElementById('batchModal')).hide();
                this.switchToSessionsTab();
                this.startBatchStatusPolling(data.batch_id);
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Batch submission failed: ${error.message}`, 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    displayBatchJob(batchId) {
        const sessionsContainer = document.getElementById('sessions-container');
        const job = this.batchJobs.get(batchId);
        
        // Clear empty state if this is the first job
        if (this.batchJobs.size === 1 && this.activeSessions.size === 0) {
            sessionsContainer.innerHTML = '';
        }

        const jobElement = document.createElement('div');
        jobElement.className = 'batch-item';
        jobElement.id = `batch-${batchId}`;
        jobElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">
                    <i class="fas fa-layer-group text-info"></i>
                    Batch Job: ${batchId.substring(0, 8)}...
                </h6>
                <span class="badge bg-warning" id="batch-status-${batchId}">Processing</span>
            </div>
            <div class="row">
                <div class="col-md-4">
                    <small class="text-muted">Type: ${job.processing_type}</small>
                </div>
                <div class="col-md-4">
                    <small class="text-muted">Documents: ${job.document_count}</small>
                </div>
                <div class="col-md-4">
                    <small class="text-muted">Submitted: ${new Date(job.submitted_at).toLocaleTimeString()}</small>
                </div>
            </div>
            <div class="progress mt-2" style="height: 6px;">
                <div class="progress-bar bg-info progress-bar-striped progress-bar-animated" 
                     id="batch-progress-${batchId}" 
                     style="width: 20%"></div>
            </div>
        `;

        sessionsContainer.appendChild(jobElement);
    }

    async startBatchStatusPolling(batchId) {
        const pollStatus = async () => {
            try {
                const response = await fetch(`/api/batch/status/${batchId}`);
                const data = await response.json();
                
                if (data.success) {
                    this.updateBatchStatus(batchId, data.status);
                    
                    if (data.status.status === 'completed') {
                        this.fetchBatchResults(batchId);
                        return; // Stop polling
                    } else if (data.status.status === 'failed') {
                        return; // Stop polling
                    }
                }
            } catch (error) {
                console.error('Batch status polling error:', error);
            }

            // Continue polling if not completed
            setTimeout(pollStatus, 5000);
        };

        setTimeout(pollStatus, 2000); // Start polling after 2 seconds
    }

    updateBatchStatus(batchId, statusData) {
        const statusBadge = document.getElementById(`batch-status-${batchId}`);
        const progressBar = document.getElementById(`batch-progress-${batchId}`);
        
        if (statusBadge) {
            statusBadge.textContent = statusData.status || 'Processing';
            statusBadge.className = `badge ${this.getBatchStatusClass(statusData.status)}`;
        }
        
        if (progressBar) {
            const progress = statusData.progress || 20;
            progressBar.style.width = `${Math.min(progress, 90)}%`;
            
            if (statusData.status === 'completed') {
                progressBar.style.width = '100%';
                progressBar.className = 'progress-bar bg-success';
            } else if (statusData.status === 'failed') {
                progressBar.className = 'progress-bar bg-danger';
            }
        }
    }

    getBatchStatusClass(status) {
        switch (status) {
            case 'completed': return 'bg-success';
            case 'failed': return 'bg-danger';
            case 'processing': return 'bg-warning';
            default: return 'bg-info';
        }
    }

    async fetchBatchResults(batchId) {
        try {
            const response = await fetch(`/api/batch/results/${batchId}`);
            const data = await response.json();
            
            if (data.success) {
                const result = {
                    type: 'batch_processing',
                    timestamp: new Date().toISOString(),
                    batch_id: batchId,
                    data: data
                };
                
                this.addToResults(result);
                this.resultHistory.push(result);
                this.showNotification(`Batch job ${batchId.substring(0, 8)}... completed`, 'success');
            }
        } catch (error) {
            console.error('Failed to fetch batch results:', error);
            this.showNotification(`Failed to fetch results for batch ${batchId.substring(0, 8)}...`, 'error');
        }
    }

    // Enhanced Embeddings
    setupEmbeddingsListeners() {
        const createBtn = document.getElementById('createEmbeddings');
        createBtn?.addEventListener('click', () => this.createEnhancedEmbeddings());
    }

    async createEnhancedEmbeddings() {
        const texts = document.getElementById('embeddingTexts').value.split('\n').filter(t => t.trim());
        const metadata = document.getElementById('embeddingMetadata').value;
        const dimensions = parseInt(document.getElementById('embeddingDimensions').value);

        if (texts.length === 0) {
            this.showNotification('Please provide texts to embed', 'warning');
            return;
        }

        let parsedMetadata = null;
        if (metadata.trim()) {
            try {
                parsedMetadata = JSON.parse(metadata);
            } catch (error) {
                this.showNotification('Invalid JSON format in metadata', 'error');
                return;
            }
        }

        const createBtn = document.getElementById('createEmbeddings');
        const originalText = createBtn.innerHTML;
        createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        createBtn.disabled = true;

        try {
            const response = await fetch('/api/embeddings/enhanced', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    texts: texts,
                    metadata: parsedMetadata,
                    dimensions: dimensions
                })
            });

            const data = await response.json();
            if (data.success) {
                this.displayEmbeddingsResult(data);
                bootstrap.Modal.getInstance(document.getElementById('embeddingsModal')).hide();
                this.switchToResultsTab();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Embeddings creation failed: ${error.message}`, 'error');
        } finally {
            createBtn.innerHTML = originalText;
            createBtn.disabled = false;
        }
    }

    displayEmbeddingsResult(data) {
        const result = {
            type: 'enhanced_embeddings',
            timestamp: new Date().toISOString(),
            data: data
        };

        this.addToResults(result);
        this.resultHistory.push(result);
    }

    // Function Calling
    setupFunctionsListeners() {
        const createBtn = document.getElementById('createAgent');
        const loadSampleBtn = document.getElementById('loadSampleTools');

        createBtn?.addEventListener('click', () => this.createFunctionCallingAgent());
        loadSampleBtn?.addEventListener('click', () => this.loadSampleTools());
    }

    loadSampleTools() {
        const toolsTextarea = document.getElementById('availableTools');
        
        const sampleTools = [
            {
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search through documents in the vector database",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_sentiment",
                    "description": "Analyze the sentiment of given text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to analyze"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_summary",
                    "description": "Generate a summary of provided content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to summarize"
                            },
                            "max_length": {
                                "type": "integer",
                                "description": "Maximum length of summary",
                                "default": 200
                            }
                        },
                        "required": ["content"]
                    }
                }
            }
        ];

        toolsTextarea.value = JSON.stringify(sampleTools, null, 2);
    }

    async createFunctionCallingAgent() {
        const instructions = document.getElementById('agentInstructions').value;
        const tools = document.getElementById('availableTools').value;

        if (!tools.trim()) {
            this.showNotification('Please provide tools configuration', 'warning');
            return;
        }

        let parsedTools;
        try {
            parsedTools = JSON.parse(tools);
        } catch (error) {
            this.showNotification('Invalid JSON format in tools configuration', 'error');
            return;
        }

        const createBtn = document.getElementById('createAgent');
        const originalText = createBtn.innerHTML;
        createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        createBtn.disabled = true;

        try {
            const response = await fetch('/api/function-calling/agent', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tools: parsedTools,
                    instructions: instructions
                })
            });

            const data = await response.json();
            if (data.success) {
                this.displayFunctionCallingResult(data);
                bootstrap.Modal.getInstance(document.getElementById('functionsModal')).hide();
                this.switchToResultsTab();
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            this.showNotification(`Agent creation failed: ${error.message}`, 'error');
        } finally {
            createBtn.innerHTML = originalText;
            createBtn.disabled = false;
        }
    }

    displayFunctionCallingResult(data) {
        const result = {
            type: 'function_calling_agent',
            timestamp: new Date().toISOString(),
            data: data
        };

        this.addToResults(result);
        this.resultHistory.push(result);
    }

    // Results Management
    addToResults(result) {
        const resultsContainer = document.getElementById('results-container');
        
        // Clear empty state if this is the first result
        if (this.resultHistory.length === 0) {
            resultsContainer.innerHTML = '';
        }

        const resultElement = this.createResultElement(result);
        resultsContainer.insertBefore(resultElement, resultsContainer.firstChild);
    }

    createResultElement(result) {
        const element = document.createElement('div');
        element.className = 'result-card mb-3';
        
        const typeInfo = this.getResultTypeInfo(result.type);
        const timestamp = new Date(result.timestamp).toLocaleString();

        element.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0">
                    <i class="fas fa-${typeInfo.icon} text-${typeInfo.color}"></i>
                    ${typeInfo.title}
                </h6>
                <small class="text-muted">${timestamp}</small>
            </div>
            <div class="result-content">
                ${this.formatResultContent(result)}
            </div>
            <div class="mt-2">
                <button class="btn btn-sm btn-outline-primary" onclick="advancedFeatures.expandResult(this)">
                    <i class="fas fa-expand"></i> View Details
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="advancedFeatures.exportResult(${JSON.stringify(result).replace(/"/g, '&quot;')})">
                    <i class="fas fa-download"></i> Export
                </button>
            </div>
        `;

        return element;
    }

    getResultTypeInfo(type) {
        const typeMap = {
            vision: { icon: 'eye', color: 'primary', title: 'Vision Analysis' },
            structured_report: { icon: 'file-alt', color: 'success', title: 'Structured Report' },
            batch_processing: { icon: 'layer-group', color: 'info', title: 'Batch Processing' },
            enhanced_embeddings: { icon: 'vector-square', color: 'warning', title: 'Enhanced Embeddings' },
            function_calling_agent: { icon: 'robot', color: 'danger', title: 'Function Calling Agent' }
        };

        return typeMap[type] || { icon: 'file', color: 'secondary', title: 'Result' };
    }

    formatResultContent(result) {
        switch (result.type) {
            case 'vision':
                return `
                    <p><strong>Analysis:</strong> ${result.data.analysis.substring(0, 200)}${result.data.analysis.length > 200 ? '...' : ''}</p>
                    ${result.data.objects_detected ? `<p><strong>Objects:</strong> ${result.data.objects_detected.join(', ')}</p>` : ''}
                `;
            case 'structured_report':
                return `
                    <p><strong>Report Type:</strong> ${result.data.report_type}</p>
                    <p><strong>Summary:</strong> ${JSON.stringify(result.data.report).substring(0, 200)}...</p>
                `;
            case 'batch_processing':
                return `
                    <p><strong>Batch ID:</strong> ${result.batch_id}</p>
                    <p><strong>Results:</strong> ${result.data.total_results} processed</p>
                `;
            case 'enhanced_embeddings':
                return `
                    <p><strong>Embeddings:</strong> ${result.data.embeddings.length} vectors created</p>
                    <p><strong>Dimensions:</strong> ${result.data.dimensions}</p>
                    <p><strong>Model:</strong> ${result.data.model}</p>
                `;
            case 'function_calling_agent':
                return `
                    <p><strong>Agent:</strong> Function calling agent created</p>
                    <p><strong>Tools:</strong> ${result.data.agent_config.tools?.length || 0} available</p>
                `;
            default:
                return '<p>Result details available in expanded view.</p>';
        }
    }

    expandResult(button) {
        // Implementation for expanding result details
        this.showNotification('Detailed view coming soon!', 'info');
    }

    exportResult(result) {
        const dataStr = JSON.stringify(result, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `advanced_openai_result_${Date.now()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('Result exported successfully', 'success');
    }

    // Tab Management
    handleTabSwitch(target) {
        switch (target) {
            case '#sessions':
                this.refreshSessionsTab();
                break;
            case '#history':
                this.refreshHistoryTab();
                break;
        }
    }

    switchToResultsTab() {
        const resultsTab = document.getElementById('results-tab');
        bootstrap.Tab.getInstance(resultsTab)?.show() || new bootstrap.Tab(resultsTab).show();
    }

    switchToSessionsTab() {
        const sessionsTab = document.getElementById('sessions-tab');
        bootstrap.Tab.getInstance(sessionsTab)?.show() || new bootstrap.Tab(sessionsTab).show();
    }

    refreshSessionsTab() {
        // Update sessions display
        const sessionsContainer = document.getElementById('sessions-container');
        if (this.activeSessions.size === 0 && this.batchJobs.size === 0) {
            sessionsContainer.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-tasks fa-3x mb-3"></i>
                    <h5>No active sessions</h5>
                    <p>Start a real-time conversation or batch processing job to see active sessions.</p>
                </div>
            `;
        }
    }

    refreshHistoryTab() {
        const historyContainer = document.getElementById('history-container');
        
        if (this.resultHistory.length === 0) {
            historyContainer.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-history fa-3x mb-3"></i>
                    <h5>No history yet</h5>
                    <p>Your previous results and sessions will appear here for easy reference.</p>
                </div>
            `;
            return;
        }

        historyContainer.innerHTML = this.resultHistory
            .slice().reverse() // Show newest first
            .map(result => {
                const typeInfo = this.getResultTypeInfo(result.type);
                const timestamp = new Date(result.timestamp).toLocaleString();
                
                return `
                    <div class="batch-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">
                                <i class="fas fa-${typeInfo.icon} text-${typeInfo.color}"></i>
                                ${typeInfo.title}
                            </h6>
                            <small class="text-muted">${timestamp}</small>
                        </div>
                        <div class="mt-2">
                            ${this.formatResultContent(result)}
                        </div>
                    </div>
                `;
            })
            .join('');
    }

    // Utility Functions
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getBootstrapAlertClass(type) {
        const typeMap = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'info'
        };
        return typeMap[type] || 'info';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.advancedFeatures = new AdvancedOpenAIFeatures();
});

// Export for global access
window.AdvancedOpenAIFeatures = AdvancedOpenAIFeatures;
