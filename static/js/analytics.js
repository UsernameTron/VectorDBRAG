/**
 * Analytics Dashboard JavaScript
 * Handles all frontend functionality for the analytics dashboard
 */

class AnalyticsDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.loadIngestionStatus();
        this.loadHealthStatus();
    }

    setupEventListeners() {
        // Analytics search form
        document.getElementById('analyticsSearchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performAnalyticsSearch();
        });

        // Example query buttons
        document.querySelectorAll('.example-query').forEach(button => {
            button.addEventListener('click', (e) => {
                const query = e.target.getAttribute('data-query');
                document.getElementById('analyticsQuery').value = query;
                this.performAnalyticsSearch();
            });
        });

        // Report management buttons
        document.getElementById('createSampleReports').addEventListener('click', () => {
            this.createSampleReports();
        });

        document.getElementById('triggerBulkIngestion').addEventListener('click', () => {
            this.triggerBulkIngestion();
        });

        document.getElementById('refreshIngestionStatus').addEventListener('click', () => {
            this.loadIngestionStatus();
        });

        // Auto-refresh dashboard every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/analytics/dashboard');
            const data = await response.json();

            if (data.success) {
                this.updateDashboardMetrics(data.data);
            } else {
                console.error('Failed to load dashboard data:', data.message);
                this.showError('Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Dashboard data error:', error);
            this.showError('Unable to connect to analytics service');
        }
    }

    updateDashboardMetrics(data) {
        // Update metric values
        document.getElementById('vectorStoresCount').textContent = 
            data.rag_status?.vector_stores || '--';
        document.getElementById('reportsToday').textContent = 
            data.analytics_status?.reports_generated_today || '--';
        document.getElementById('activeAgents').textContent = 
            data.analytics_status?.active_agents || '--';

        // Update status indicators
        this.updateStatusIndicator('ragStatus', data.rag_status?.health);
        this.updateStatusIndicator('analyticsStatus', data.analytics_status?.health);
        this.updateStatusIndicator('ingestionStatus', data.integration_status);

        // Update system status
        const overallHealth = this.calculateOverallHealth(data);
        document.getElementById('systemStatus').innerHTML = `
            <span class="status-indicator status-${overallHealth}"></span>
            <small class="text-muted">${overallHealth === 'healthy' ? 'All Systems' : 'Issues Detected'}</small>
        `;
    }

    updateStatusIndicator(elementId, status) {
        const indicator = document.getElementById(elementId);
        if (indicator) {
            indicator.className = 'status-indicator';
            
            if (status === 'healthy' || status === 'active') {
                indicator.classList.add('status-healthy');
            } else if (status === 'degraded' || status === 'warning') {
                indicator.classList.add('status-warning');
            } else {
                indicator.classList.add('status-error');
            }
        }
    }

    calculateOverallHealth(data) {
        const statuses = [
            data.rag_status?.health,
            data.analytics_status?.health,
            data.integration_status
        ];

        if (statuses.every(s => s === 'healthy' || s === 'active')) {
            return 'healthy';
        } else if (statuses.some(s => s === 'error' || s === 'failed')) {
            return 'error';
        } else {
            return 'warning';
        }
    }

    async performAnalyticsSearch() {
        const query = document.getElementById('analyticsQuery').value.trim();
        const searchType = document.getElementById('analyticsSearchType').value;

        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/analytics/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    search_type: searchType
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.success) {
                this.displaySearchResults(data.results, query);
            } else {
                this.showError(data.message || 'Search failed');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Search error:', error);
            this.showError('Search request failed');
        }
    }

    displaySearchResults(results, query) {
        const resultsContainer = document.getElementById('analyticsResults');
        
        if (!results.search_results || results.search_results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No results found for "${query}". Try a different search term or create some sample reports first.
                </div>
            `;
            return;
        }

        let html = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Found ${results.search_results.length} results for "${query}"
            </div>
        `;

        // Display search results
        if (typeof results.search_results === 'string') {
            // AI-assisted search result
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-robot me-2"></i>AI Analysis
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="search-result-content">${this.formatSearchResponse(results.search_results)}</div>
                    </div>
                </div>
            `;
        } else if (Array.isArray(results.search_results)) {
            // Semantic search results
            results.search_results.forEach((result, index) => {
                html += `
                    <div class="card mb-3">
                        <div class="card-header">
                            <h6 class="mb-0">
                                <i class="fas fa-file-alt me-2"></i>
                                Document ${index + 1}
                                ${result.score ? `<span class="badge bg-primary ms-2">${Math.round(result.score * 100)}% match</span>` : ''}
                            </h6>
                        </div>
                        <div class="card-body">
                            <p class="card-text">${result.content || result.text || 'No content available'}</p>
                            ${result.source ? `<small class="text-muted">Source: ${result.source}</small>` : ''}
                        </div>
                    </div>
                `;
            });
        }

        // Display analytics context if available
        if (results.analytics_context) {
            html += `
                <div class="card border-info">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>Analytics Context
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <strong>Related Metrics:</strong>
                                <ul class="list-unstyled mt-1">
                                    ${results.analytics_context.related_metrics?.map(metric => 
                                        `<li><i class="fas fa-chart-bar me-1"></i>${metric}</li>`
                                    ).join('') || '<li>No metrics available</li>'}
                                </ul>
                            </div>
                            <div class="col-md-4">
                                <strong>Time Period:</strong>
                                <p class="mt-1">${results.analytics_context.time_period || 'Not specified'}</p>
                            </div>
                            <div class="col-md-4">
                                <strong>Trending Topics:</strong>
                                <div class="mt-1">
                                    ${results.analytics_context.trending_topics?.map(topic => 
                                        `<span class="badge bg-secondary me-1">${topic}</span>`
                                    ).join('') || '<span class="text-muted">None</span>'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        resultsContainer.innerHTML = html;
    }

    formatSearchResponse(response) {
        // Convert markdown-like formatting to HTML
        return response
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    async loadIngestionStatus() {
        try {
            const response = await fetch('/api/analytics/ingestion/status');
            const data = await response.json();

            if (data.success) {
                this.updateIngestionStatus(data.status);
            } else {
                console.error('Failed to load ingestion status:', data.message);
            }
        } catch (error) {
            console.error('Ingestion status error:', error);
        }
    }

    updateIngestionStatus(status) {
        // Update monitoring status
        const monitoringBadge = document.getElementById('monitoringStatus');
        if (status.monitoring_active) {
            monitoringBadge.textContent = 'Active';
            monitoringBadge.className = 'badge bg-success';
        } else {
            monitoringBadge.textContent = 'Inactive';
            monitoringBadge.className = 'badge bg-warning';
        }

        // Update statistics
        if (status.recent_ingestions) {
            document.getElementById('successfulIngestions').textContent = 
                status.recent_ingestions.successful || 0;
            document.getElementById('failedIngestions').textContent = 
                status.recent_ingestions.failed || 0;
            document.getElementById('totalIngestions').textContent = 
                status.recent_ingestions.total || 0;
        }

        // Update last ingestion time
        if (status.last_ingestion) {
            const lastTime = new Date(status.last_ingestion.timestamp).toLocaleString();
            document.getElementById('lastIngestionTime').textContent = 
                `Last ingestion: ${lastTime}`;
        }
    }

    async createSampleReports() {
        this.showLoading();

        try {
            const response = await fetch('/api/analytics/sample-reports', {
                method: 'POST'
            });

            const data = await response.json();
            this.hideLoading();

            if (data.success) {
                this.showSuccess(`Created ${data.reports_created} sample reports`);
                this.loadIngestionStatus();
            } else {
                this.showError(data.message || 'Failed to create sample reports');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Sample reports error:', error);
            this.showError('Failed to create sample reports');
        }
    }

    async triggerBulkIngestion() {
        this.showLoading();

        try {
            const response = await fetch('/api/analytics/ingestion/bulk', {
                method: 'POST'
            });

            const data = await response.json();
            this.hideLoading();

            if (data.success) {
                const results = data.results;
                this.showSuccess(
                    `Ingestion complete: ${results.successful} successful, ${results.failed} failed`
                );
                this.loadIngestionStatus();
                this.loadDashboardData();
            } else {
                this.showError(data.message || 'Bulk ingestion failed');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Bulk ingestion error:', error);
            this.showError('Bulk ingestion request failed');
        }
    }

    async loadHealthStatus() {
        try {
            const response = await fetch('/api/integration/health');
            const data = await response.json();

            if (data.success) {
                this.updateHealthStatus(data.health);
            } else {
                this.showHealthError('Failed to load health status');
            }
        } catch (error) {
            console.error('Health status error:', error);
            this.showHealthError('Unable to check system health');
        }
    }

    updateHealthStatus(health) {
        const healthContainer = document.getElementById('healthStatus');
        
        let html = '<div class="row">';
        
        // System components
        const components = [
            { name: 'RAG System', status: health.rag_system, icon: 'fas fa-search' },
            { name: 'Analytics Integration', status: health.analytics_integration, icon: 'fas fa-chart-line' },
            { name: 'Report Ingestion', status: health.report_ingestion, icon: 'fas fa-upload' }
        ];

        components.forEach(component => {
            const statusClass = this.getStatusClass(component.status);
            html += `
                <div class="col-md-4 mb-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="${component.icon} fa-2x text-${statusClass} mb-2"></i>
                            <h6 class="card-title">${component.name}</h6>
                            <span class="badge bg-${statusClass}">${component.status}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';

        // Detailed analytics health if available
        if (health.analytics_details) {
            html += `
                <div class="mt-4">
                    <h6>Detailed Analytics Health</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Analytics Path Exists</span>
                                    <span class="badge bg-${health.analytics_details.analytics_path_exists ? 'success' : 'danger'}">
                                        ${health.analytics_details.analytics_path_exists ? 'Yes' : 'No'}
                                    </span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Reports KB Exists</span>
                                    <span class="badge bg-${health.analytics_details.reports_kb_exists ? 'success' : 'danger'}">
                                        ${health.analytics_details.reports_kb_exists ? 'Yes' : 'No'}
                                    </span>
                                </li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between">
                                    <span>Integration Active</span>
                                    <span class="badge bg-${health.analytics_details.integration_active ? 'success' : 'danger'}">
                                        ${health.analytics_details.integration_active ? 'Yes' : 'No'}
                                    </span>
                                </li>
                                <li class="list-group-item">
                                    <small class="text-muted">
                                        Last Check: ${new Date(health.analytics_details.last_check).toLocaleString()}
                                    </small>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }

        healthContainer.innerHTML = html;
    }

    getStatusClass(status) {
        switch (status) {
            case 'healthy':
            case 'active':
                return 'success';
            case 'degraded':
            case 'warning':
                return 'warning';
            case 'disabled':
                return 'secondary';
            default:
                return 'danger';
        }
    }

    showHealthError(message) {
        document.getElementById('healthStatus').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }

    showLoading() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AnalyticsDashboard();
});
