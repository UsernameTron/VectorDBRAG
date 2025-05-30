/**
 * RAG File Search System - Frontend JavaScript
 */

// Global state
let vectorStores = [];
let selectedVectorStores = new Set();
let currentSearchResults = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadVectorStores();
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Check system health
    checkSystemHealth();
    
    // Set up drag and drop
    setupDragAndDrop();
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    const fileInput = document.getElementById('fileInput');
    const searchQuery = document.getElementById('searchQuery');
    const newStoreName = document.getElementById('newStoreName');

    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    if (searchQuery) {
        searchQuery.addEventListener('keypress', handleSearchKeyPress);
    }

    if (newStoreName) {
        newStoreName.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                createVectorStore();
            }
        });
    }
}

/**
 * Check system health and API key status
 */
async function checkSystemHealth() {
    try {
        // Check general health
        const healthResponse = await fetch('/health');
        const healthData = await healthResponse.json();
        
        // Check API key specifically
        const apiResponse = await fetch('/api/test-api-key');
        const apiData = await apiResponse.json();
        
        if (healthData.status === 'healthy' && apiData.status === 'success') {
            updateStatusIndicator('Ready', 'success');
        } else if (apiData.status === 'error') {
            updateStatusIndicator('API Key Issue', 'danger');
            showApiKeyError(apiData.message, apiData.suggestion);
        } else {
            updateStatusIndicator('System Issue', 'warning');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatusIndicator('Offline', 'danger');
    }
}

/**
 * Show API key error message
 */
function showApiKeyError(message, suggestion) {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <h4 class="alert-heading"><i class="bi bi-exclamation-triangle-fill"></i> API Key Required</h4>
            <p><strong>Error:</strong> ${message}</p>
            <hr>
            <p class="mb-0">
                <strong>Setup Instructions:</strong><br>
                1. Get your OpenAI API key from: <a href="https://platform.openai.com/api-keys" target="_blank" class="alert-link">https://platform.openai.com/api-keys</a><br>
                2. Add it to your <code>.env</code> file: <code>OPENAI_API_KEY=your_actual_api_key</code><br>
                3. Restart the application<br>
                4. Or run: <code>./setup_api_key.sh</code> for guided setup
            </p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
}

/**
 * Update status indicator
 */
function updateStatusIndicator(text, type = 'success') {
    const indicator = document.getElementById('status-indicator');
    if (!indicator) return;

    const iconMap = {
        success: 'bi-circle-fill text-success',
        warning: 'bi-exclamation-triangle-fill text-warning',
        danger: 'bi-x-circle-fill text-danger',
        info: 'bi-info-circle-fill text-info'
    };

    indicator.innerHTML = `<i class="bi ${iconMap[type]}"></i> ${text}`;
}

/**
 * Set up drag and drop functionality
 */
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files);
        }
    });
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

/**
 * Handle files for upload
 */
function handleFiles(files) {
    const vectorStoreId = document.getElementById('vectorStoreSelect').value;
    
    if (!vectorStoreId) {
        showToast('Please select a vector store first', 'warning');
        return;
    }

    Array.from(files).forEach(file => {
        uploadFile(file, vectorStoreId);
    });
}

/**
 * Upload a file
 */
async function uploadFile(file, vectorStoreId) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('vector_store_id', vectorStoreId);

    try {
        showUploadProgress(true);
        updateStatusIndicator('Uploading...', 'info');

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showToast(`File "${file.name}" uploaded successfully`, 'success');
            updateStatusIndicator('Ready', 'success');
        } else {
            throw new Error(data.message || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast(`Upload failed: ${error.message}`, 'danger');
        updateStatusIndicator('Ready', 'success');
    } finally {
        showUploadProgress(false);
    }
}

/**
 * Upload from URL
 */
async function uploadFromUrl() {
    const urlInput = document.getElementById('urlInput');
    const vectorStoreId = document.getElementById('vectorStoreSelect').value;
    const url = urlInput.value.trim();

    if (!url) {
        showToast('Please enter a URL', 'warning');
        return;
    }

    if (!vectorStoreId) {
        showToast('Please select a vector store first', 'warning');
        return;
    }

    try {
        showUploadProgress(true);
        updateStatusIndicator('Uploading from URL...', 'info');

        const formData = new FormData();
        formData.append('url', url);
        formData.append('vector_store_id', vectorStoreId);

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showToast('File uploaded from URL successfully', 'success');
            urlInput.value = '';
            updateStatusIndicator('Ready', 'success');
        } else {
            throw new Error(data.message || 'Upload failed');
        }
    } catch (error) {
        console.error('URL upload error:', error);
        showToast(`Upload failed: ${error.message}`, 'danger');
        updateStatusIndicator('Ready', 'success');
    } finally {
        showUploadProgress(false);
    }
}

/**
 * Show/hide upload progress
 */
function showUploadProgress(show) {
    const progressElement = document.getElementById('uploadProgress');
    if (!progressElement) return;

    if (show) {
        progressElement.classList.remove('d-none');
        // Simulate progress animation
        animateProgress();
    } else {
        progressElement.classList.add('d-none');
        resetProgress();
    }
}

/**
 * Animate progress bar
 */
function animateProgress() {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
        }
        
        progressBar.style.width = progress + '%';
        progressPercent.textContent = Math.round(progress) + '%';
        
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 200);
}

/**
 * Reset progress bar
 */
function resetProgress() {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    
    if (progressBar) progressBar.style.width = '0%';
    if (progressPercent) progressPercent.textContent = '0%';
}

/**
 * Load vector stores
 */
async function loadVectorStores() {
    try {
        updateStatusIndicator('Loading vector stores...', 'info');
        
        const response = await fetch('/api/vector-stores');
        const data = await response.json();

        if (data.success) {
            vectorStores = data.vector_stores || [];
            displayVectorStores();
            populateVectorStoreSelects();
            updateStatusIndicator('Ready', 'success');
        } else {
            throw new Error(data.message || 'Failed to load vector stores');
        }
    } catch (error) {
        console.error('Error loading vector stores:', error);
        showToast(`Failed to load vector stores: ${error.message}`, 'danger');
        updateStatusIndicator('Error', 'danger');
    }
}

/**
 * Display vector stores
 */
function displayVectorStores() {
    const container = document.getElementById('vectorStoresList');
    if (!container) return;

    if (vectorStores.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="bi bi-database"></i>
                <p>No vector stores found. Create one to get started.</p>
            </div>
        `;
        return;
    }

    const storesHtml = vectorStores.map(store => `
        <div class="vector-store-item ${selectedVectorStores.has(store.id) ? 'selected' : ''}" 
             data-store-id="${store.id}" onclick="toggleVectorStore('${store.id}')">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <div class="store-name">${escapeHtml(store.name)}</div>
                    <div class="store-meta">
                        <small>ID: ${store.id}</small>
                        ${store.file_counts ? `• ${store.file_counts.total || 0} files` : ''}
                        ${store.created_at ? `• Created: ${formatDate(store.created_at)}` : ''}
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="store-status ${getStatusClass(store.status)}">
                        ${store.status || 'active'}
                    </span>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteVectorStore('${store.id}', event)">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    container.innerHTML = storesHtml;
}

/**
 * Populate vector store select elements
 */
function populateVectorStoreSelects() {
    const selects = ['vectorStoreSelect'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;

        const options = vectorStores.map(store => 
            `<option value="${store.id}">${escapeHtml(store.name)}</option>`
        ).join('');

        select.innerHTML = `
            <option value="">Choose a vector store...</option>
            ${options}
        `;
    });

    updateSearchVectorStores();
}

/**
 * Update search vector stores display
 */
function updateSearchVectorStores() {
    const container = document.getElementById('searchVectorStores');
    if (!container) return;

    if (selectedVectorStores.size === 0) {
        container.innerHTML = '<small class="text-muted">Select vector stores from the list above</small>';
        return;
    }

    const selectedStores = vectorStores.filter(store => selectedVectorStores.has(store.id));
    const storesHtml = selectedStores.map(store => `
        <span class="badge bg-primary me-2 mb-2">
            ${escapeHtml(store.name)}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    onclick="toggleVectorStore('${store.id}')" aria-label="Remove">
            </button>
        </span>
    `).join('');

    container.innerHTML = storesHtml;
}

/**
 * Toggle vector store selection
 */
function toggleVectorStore(storeId) {
    if (selectedVectorStores.has(storeId)) {
        selectedVectorStores.delete(storeId);
    } else {
        selectedVectorStores.add(storeId);
    }
    
    displayVectorStores();
    updateSearchVectorStores();
}

/**
 * Create a new vector store
 */
async function createVectorStore() {
    const nameInput = document.getElementById('newStoreName');
    const name = nameInput.value.trim();

    if (!name) {
        showToast('Please enter a vector store name', 'warning');
        return;
    }

    try {
        updateStatusIndicator('Creating vector store...', 'info');

        const response = await fetch('/api/vector-stores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Vector store "${name}" created successfully`, 'success');
            nameInput.value = '';
            loadVectorStores();
        } else {
            throw new Error(data.message || 'Failed to create vector store');
        }
    } catch (error) {
        console.error('Error creating vector store:', error);
        showToast(`Failed to create vector store: ${error.message}`, 'danger');
        updateStatusIndicator('Ready', 'success');
    }
}

/**
 * Delete a vector store
 */
async function deleteVectorStore(storeId, event) {
    event.stopPropagation();
    
    const store = vectorStores.find(s => s.id === storeId);
    if (!store) return;

    if (!confirm(`Are you sure you want to delete the vector store "${store.name}"? This action cannot be undone.`)) {
        return;
    }

    try {
        updateStatusIndicator('Deleting vector store...', 'info');

        const response = await fetch(`/api/vector-stores/${storeId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Vector store "${store.name}" deleted successfully`, 'success');
            selectedVectorStores.delete(storeId);
            loadVectorStores();
        } else {
            throw new Error(data.message || 'Failed to delete vector store');
        }
    } catch (error) {
        console.error('Error deleting vector store:', error);
        showToast(`Failed to delete vector store: ${error.message}`, 'danger');
        updateStatusIndicator('Ready', 'success');
    }
}

/**
 * Handle search key press
 */
function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
        performSearch();
    }
}

/**
 * Perform search
 */
async function performSearch() {
    const query = document.getElementById('searchQuery').value.trim();
    const searchType = document.getElementById('searchType').value;
    const maxResults = parseInt(document.getElementById('maxResults').value) || 10;

    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }

    if (selectedVectorStores.size === 0) {
        showToast('Please select at least one vector store to search', 'warning');
        return;
    }

    try {
        updateStatusIndicator('Searching...', 'info');
        showSearchResults(null, true); // Show loading state

        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                vector_store_ids: Array.from(selectedVectorStores),
                search_type: searchType,
                max_results: maxResults
            })
        });

        const data = await response.json();

        if (data.success) {
            currentSearchResults = data;
            showSearchResults(data);
            updateStatusIndicator('Ready', 'success');
        } else {
            throw new Error(data.message || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        showToast(`Search failed: ${error.message}`, 'danger');
        updateStatusIndicator('Ready', 'success');
        showSearchResults(null, false);
    }
}

/**
 * Show search results
 */
function showSearchResults(data, loading = false) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsContainer = document.getElementById('searchResults');
    
    if (!resultsCard || !resultsContainer) return;

    resultsCard.style.display = 'block';

    if (loading) {
        resultsContainer.innerHTML = `
            <div class="text-center">
                <div class="loading-spinner me-2"></div>
                Searching...
            </div>
        `;
        return;
    }

    if (!data) {
        resultsCard.style.display = 'none';
        return;
    }

    const results = data.results;
    let resultsHtml = '';

    if (data.search_type === 'assisted') {
        resultsHtml = formatAssistedResults(results);
    } else {
        resultsHtml = formatSemanticResults(results);
    }

    resultsContainer.innerHTML = resultsHtml;
}

/**
 * Format assisted search results
 */
function formatAssistedResults(results) {
    if (!results || !results.choices || results.choices.length === 0) {
        return '<div class="text-center text-muted">No results found.</div>';
    }

    const choice = results.choices[0];
    const message = choice.message;
    
    let html = `
        <div class="search-result">
            <div class="result-title">AI-Generated Response</div>
            <div class="result-content">${formatResponse(message.content)}</div>
    `;

    // Add tool calls if present
    if (message.tool_calls && message.tool_calls.length > 0) {
        html += '<div class="mt-3"><h6>Sources:</h6>';
        message.tool_calls.forEach(toolCall => {
            if (toolCall.type === 'file_search' && toolCall.file_search && toolCall.file_search.results) {
                toolCall.file_search.results.forEach(result => {
                    html += formatSourceResult(result);
                });
            }
        });
        html += '</div>';
    }

    html += `
            <div class="result-meta">
                <span class="badge bg-info">AI-Assisted</span>
                <span class="text-muted ms-2">Model: ${results.model || 'Unknown'}</span>
            </div>
        </div>
    `;

    return html;
}

/**
 * Format semantic search results
 */
function formatSemanticResults(results) {
    if (!results || !results.data || results.data.length === 0) {
        return '<div class="text-center text-muted">No results found.</div>';
    }

    return results.data.map(result => formatSourceResult(result)).join('');
}

/**
 * Format individual source result
 */
function formatSourceResult(result) {
    const filename = result.file_name || result.filename || 'Unknown file';
    const content = result.content || result.text || 'No content available';
    const score = result.score || result.similarity || 0;
    
    const confidenceClass = score > 0.8 ? 'confidence-high' : 
                           score > 0.6 ? 'confidence-medium' : 'confidence-low';

    return `
        <div class="search-result">
            <div class="result-title">
                <i class="bi bi-file-text"></i>
                ${escapeHtml(filename)}
            </div>
            <div class="result-content">${formatContent(content)}</div>
            <div class="result-meta">
                <span class="confidence-score ${confidenceClass}">
                    Confidence: ${(score * 100).toFixed(1)}%
                </span>
                ${result.file_id ? `<span class="text-muted ms-2">File ID: ${result.file_id}</span>` : ''}
            </div>
        </div>
    `;
}

/**
 * Format response content with basic markdown support
 */
function formatResponse(content) {
    if (!content) return '';
    
    // Convert markdown-like formatting
    content = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    return `<p>${content}</p>`;
}

/**
 * Format content with highlighting and truncation
 */
function formatContent(content) {
    if (!content) return '';
    
    // Truncate long content
    const maxLength = 500;
    let truncated = content.length > maxLength ? 
        content.substring(0, maxLength) + '...' : content;
    
    // Basic HTML escaping and formatting
    truncated = escapeHtml(truncated)
        .replace(/\n/g, '<br>');
    
    return truncated;
}

/**
 * Export search results
 */
function exportResults(format) {
    if (!currentSearchResults) {
        showToast('No search results to export', 'warning');
        return;
    }

    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `search_results_${timestamp}.${format}`;
    
    let content, mimeType;
    
    if (format === 'json') {
        content = JSON.stringify(currentSearchResults, null, 2);
        mimeType = 'application/json';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast(`Results exported as ${filename}`, 'success');
}

/**
 * Clear search results
 */
function clearResults() {
    const resultsCard = document.getElementById('resultsCard');
    if (resultsCard) {
        resultsCard.style.display = 'none';
    }
    currentSearchResults = null;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const iconMap = {
        success: 'bi-check-circle-fill text-success',
        danger: 'bi-exclamation-triangle-fill text-danger',
        warning: 'bi-exclamation-triangle-fill text-warning',
        info: 'bi-info-circle-fill text-info'
    };

    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="bi ${iconMap[type]} me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${escapeHtml(message)}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    if (toastElement && typeof bootstrap !== 'undefined') {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }
}

/**
 * Utility Functions
 */

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

function getStatusClass(status) {
    const statusMap = {
        'active': 'status-active',
        'processing': 'status-processing',
        'error': 'status-error',
        'completed': 'status-active'
    };
    return statusMap[status] || 'status-active';
}
