// Dataset Reports Tab JavaScript
// Handles report viewing, filtering, and management

class DatasetReportsManager {
    constructor(datasetId) {
        this.datasetId = datasetId;
        this.reports = [];
        this.filters = {
            search: '',
            type: 'all',
            status: 'all'
        };
    }

    // Initialize reports tab
    async init() {
        this.setupEventListeners();
        await this.loadReportsList();
    }

    // Setup event listeners
    setupEventListeners() {
        // Search input
        const searchInput = document.getElementById('reportSearch');
        if (searchInput) {
            searchInput.addEventListener('input', DatasetUtils.debounce((e) => {
                this.filters.search = e.target.value;
                this.filterReports();
            }, 300));
        }

        // Type filter
        const typeFilter = document.getElementById('reportTypeFilter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.filters.type = e.target.value;
                this.filterReports();
            });
        }

        // Status filter
        const statusFilter = document.getElementById('reportStatusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.filterReports();
            });
        }
    }

    // Load reports list
    async loadReportsList() {
        const reportsContainer = document.getElementById('reportsContainer');
        const noReportsState = document.getElementById('noReportsState');
        const reportsList = document.getElementById('reportsList');

        if (reportsContainer) {
            // For now, show no reports state
            if (noReportsState) {
                noReportsState.style.display = 'block';
            }
            if (reportsList) {
                reportsList.style.display = 'none';
            }
        }

        // Update report count
        this.updateReportCount(0);
    }

    // Filter reports
    filterReports() {
        let filteredReports = [...this.reports];

        // Apply search filter
        if (this.filters.search) {
            const searchTerm = this.filters.search.toLowerCase();
            filteredReports = filteredReports.filter(report => 
                report.name.toLowerCase().includes(searchTerm) ||
                report.type.toLowerCase().includes(searchTerm) ||
                report.description.toLowerCase().includes(searchTerm)
            );
        }

        // Apply type filter
        if (this.filters.type !== 'all') {
            filteredReports = filteredReports.filter(report => 
                report.type === this.filters.type
            );
        }

        // Apply status filter
        if (this.filters.status !== 'all') {
            filteredReports = filteredReports.filter(report => 
                report.status === this.filters.status
            );
        }

        this.displayReports(filteredReports);
    }

    // Display reports
    displayReports(reports) {
        const reportsList = document.getElementById('reportsList');
        const noReportsState = document.getElementById('noReportsState');
        
        if (!reportsList || !noReportsState) return;

        if (reports.length === 0) {
            reportsList.style.display = 'none';
            noReportsState.style.display = 'block';
            return;
        }

        reportsList.style.display = 'block';
        noReportsState.style.display = 'none';

        const tableBody = document.getElementById('reportsTableBody');
        if (tableBody) {
            tableBody.innerHTML = reports.map(report => this.createReportRow(report)).join('');
        }

        this.updateReportCount(reports.length);
    }

    // Create report row HTML
    createReportRow(report) {
        const statusBadge = this.getStatusBadge(report.status);
        const typeBadge = this.getTypeBadge(report.type);
        const sizeText = report.size ? DatasetUtils.formatFileSize(report.size) : 'Unknown';
        const generatedDate = new Date(report.generated_at).toLocaleDateString();

        return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file-alt me-2 text-primary"></i>
                        <div>
                            <div class="fw-semibold">${report.name}</div>
                            ${report.description ? `<small class="text-muted">${report.description}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td>${typeBadge}</td>
                <td>${statusBadge}</td>
                <td>${generatedDate}</td>
                <td>${sizeText}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${this.getActionButtons(report)}
                    </div>
                </td>
            </tr>
        `;
    }

    // Get status badge HTML
    getStatusBadge(status) {
        const badges = {
            'completed': '<span class="badge bg-success">Completed</span>',
            'generating': '<span class="badge bg-warning">Generating</span>',
            'failed': '<span class="badge bg-danger">Failed</span>',
            'pending': '<span class="badge bg-secondary">Pending</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
    }

    // Get type badge HTML
    getTypeBadge(type) {
        const badges = {
            'alpha_diversity': '<span class="badge bg-primary">Alpha Diversity</span>',
            'beta_diversity': '<span class="badge bg-info">Beta Diversity</span>',
            'differential_abundance': '<span class="badge bg-success">Differential Abundance</span>',
            'summary': '<span class="badge bg-secondary">Summary</span>'
        };
        return badges[type] || '<span class="badge bg-secondary">Unknown</span>';
    }

    // Get action buttons HTML
    getActionButtons(report) {
        let buttons = '';

        if (report.status === 'completed') {
            buttons += `
                <button class="btn btn-outline-primary" onclick="viewReport(${report.id})" title="View Report">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-outline-success" onclick="downloadReport(${report.id})" title="Download">
                    <i class="fas fa-download"></i>
                </button>
            `;
        } else if (report.status === 'generating') {
            buttons += `
                <button class="btn btn-outline-info" disabled title="Generating">
                    <i class="fas fa-spinner fa-spin"></i>
                </button>
                <button class="btn btn-outline-danger" onclick="cancelReport(${report.id})" title="Cancel">
                    <i class="fas fa-times"></i>
                </button>
            `;
        } else if (report.status === 'failed') {
            buttons += `
                <button class="btn btn-outline-warning" onclick="retryReport(${report.id})" title="Retry">
                    <i class="fas fa-redo"></i>
                </button>
                <button class="btn btn-outline-danger" onclick="deleteReport(${report.id})" title="Delete">
                    <i class="fas fa-trash"></i>
                </button>
            `;
        }

        return buttons;
    }

    // Update report count
    updateReportCount(count) {
        const reportCount = document.getElementById('reportCount');
        if (reportCount) {
            reportCount.textContent = `${count} report${count !== 1 ? 's' : ''}`;
        }
    }

    // Clear all filters
    clearFilters() {
        this.filters = {
            search: '',
            type: 'all',
            status: 'all'
        };

        // Reset form elements
        const searchInput = document.getElementById('reportSearch');
        const typeFilter = document.getElementById('reportTypeFilter');
        const statusFilter = document.getElementById('reportStatusFilter');

        if (searchInput) searchInput.value = '';
        if (typeFilter) typeFilter.value = 'all';
        if (statusFilter) statusFilter.value = 'all';

        this.filterReports();
    }
}

// Global functions for report operations
window.viewReport = function(reportId) {
    window.open(`/dataset/report/${reportId}/view`, '_blank');
};

window.downloadReport = function(reportId) {
    window.open(`/dataset/report/${reportId}/download`, '_blank');
};

window.cancelReport = function(reportId) {
    if (confirm('Are you sure you want to cancel this report generation?')) {
        // Implementation for canceling report
        DatasetUtils.showAlert('Report cancellation feature coming soon', 'info');
    }
};

window.retryReport = function(reportId) {
    if (confirm('Are you sure you want to retry this failed report?')) {
        // Implementation for retrying report
        DatasetUtils.showAlert('Report retry feature coming soon', 'info');
    }
};

window.deleteReport = function(reportId) {
    if (confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
        // Implementation for deleting report
        DatasetUtils.showAlert('Report deletion feature coming soon', 'info');
    }
};

window.clearReportFilters = function() {
    if (window.reportsManager) {
        window.reportsManager.clearFilters();
    }
};

window.goToTab = function(tabName) {
    // Implementation for navigating to other tabs
    const tabMap = {
        'files-tab': 'files',
        'analysis-tab': 'analysis',
        'settings-tab': 'settings'
    };
    
    const targetTab = tabMap[tabName];
    if (targetTab) {
        window.location.href = `/dataset/${window.datasetId}?tab=${targetTab}`;
    }
};

// Initialize reports tab when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const datasetId = window.datasetId;
    if (datasetId) {
        window.reportsManager = new DatasetReportsManager(datasetId);
        window.reportsManager.init();
    }
});

// Export for external use
window.DatasetReportsManager = DatasetReportsManager;
