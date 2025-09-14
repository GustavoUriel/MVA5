// Dataset Files Tab JavaScript
// Handles file upload, display, and management functionality

class DatasetFilesManager {
    constructor(datasetId) {
        this.datasetId = datasetId;
        this.files = [];
        this.datasetStatus = 'draft';
    }

    // Initialize files tab
    async init() {
        this.setupEventListeners();
        await this.loadFilesTable();
        await this.loadDataStats();
    }

    // Setup event listeners
    setupEventListeners() {
        // File upload buttons
        const uploadButtons = document.querySelectorAll('.upload-btn');
        uploadButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const fileType = e.target.getAttribute('data-file-type');
                this.handleFileUpload(fileType);
            });
        });

        // File input changes
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const fileType = e.target.getAttribute('data-file-type');
                this.validateFileSelection(e.target, fileType);
            });
        });
    }

    // Handle file upload
    async handleFileUpload(fileType) {
        const fileInput = document.querySelector(`input[data-file-type="${fileType}"]`);
        const file = fileInput.files[0];
        
        if (!file) {
            DatasetUtils.showAlert('Please select a file first', 'warning');
            return;
        }

        if (!this.validateFile(file, fileType)) {
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_type', fileType);

        try {
            this.showUploadProgress(fileType, true);
            
            const response = await fetch(`/dataset/${this.datasetId}/upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                DatasetUtils.showAlert(data.message, 'success');
                await this.loadFilesTable();
                await this.loadDataStats();
            } else {
                DatasetUtils.showAlert(data.message, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            DatasetUtils.showAlert('Upload failed. Please try again.', 'error');
        } finally {
            this.showUploadProgress(fileType, false);
        }
    }

    // Validate file selection
    validateFile(file, fileType) {
        const allowedTypes = {
            'patients': ['.csv', '.tsv', '.txt'],
            'taxonomy': ['.csv', '.tsv', '.txt'],
            'bracken': ['.csv', '.tsv', '.txt']
        };

        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes[fileType].includes(fileExtension)) {
            DatasetUtils.showAlert(`Invalid file type for ${fileType} data. Please use CSV, TSV, or TXT files.`, 'error');
            return false;
        }

        // Check file size (16MB limit)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            DatasetUtils.showAlert('File size too large. Maximum size is 16MB.', 'error');
            return false;
        }

        return true;
    }

    // Show upload progress
    showUploadProgress(fileType, isLoading) {
        const button = document.querySelector(`button[data-file-type="${fileType}"]`);
        const statusContainer = document.getElementById(`${fileType}-status-container`);
        
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
            
            if (statusContainer) {
                statusContainer.innerHTML = `
                    <div class="alert alert-info" role="alert">
                        <i class="fas fa-spinner fa-spin me-2"></i>
                        <strong>Uploading file...</strong>
                    </div>
                `;
            }
        } else {
            button.disabled = false;
            button.innerHTML = `<i class="fas fa-upload me-2"></i>Upload ${fileType.charAt(0).toUpperCase() + fileType.slice(1)} Data`;
        }
    }

    // Load files table
    async loadFilesTable() {
        try {
            const data = await DatasetUtils.api.getDatasetFiles(this.datasetId);
            
            // The API returns data directly without success wrapper
            if (data && data.files) {
                this.files = data.files;
                this.datasetStatus = data.dataset_status;
                this.displayFilesTable(data.files, data.dataset_status);
            } else {
                this.showFilesError('No files data received from server');
            }
        } catch (error) {
            console.error('Failed to load files:', error);
            this.showFilesError('Failed to load files. Please try again.');
        }
    }

    // Display files table
    displayFilesTable(files, datasetStatus) {
        const filesTable = document.getElementById('filesTable');
        
        if (!filesTable) return;

        if (files.length === 0) {
            filesTable.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h6 class="text-muted mb-2">No Files Uploaded</h6>
                    <p class="text-muted mb-3">Upload your data files to get started with analysis.</p>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Status</th>
                            <th>Uploaded</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${files.map(file => this.createFileRow(file, datasetStatus)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        filesTable.innerHTML = tableHTML;
    }

    // Create file row HTML
    createFileRow(file, datasetStatus) {
        const fileTypeColor = DatasetUtils.getFileTypeColor(file.file_type);
        const statusBadge = DatasetUtils.getStatusBadge(file.cure_status, file.validation_status);
        const cureIcon = DatasetUtils.getCureStatusIcon(file.cure_status, file.validation_status);
        
        return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        ${cureIcon}
                        <span class="ms-2">${file.filename}</span>
                    </div>
                </td>
                <td>
                    <span class="badge bg-${fileTypeColor}">${file.file_type}</span>
                </td>
                <td>${DatasetUtils.formatFileSize(file.size)}</td>
                <td>${statusBadge}</td>
                <td>${new Date(file.uploaded_at).toLocaleDateString()}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewFile(${file.id})" title="View File">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="downloadFile(${file.id})" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="editTable(${file.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-warning" onclick="cureData(${file.id})" title="Cure Data">
                            <i class="fas fa-magic"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteFile(${file.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    // Show files error
    showFilesError(message) {
        const filesTable = document.getElementById('filesTable');
        if (filesTable) {
            filesTable.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Error loading files:</strong> ${message}
                </div>
            `;
        }
    }

    // Load data statistics
    async loadDataStats() {
        try {
            const data = await DatasetUtils.api.getDatasetStats(this.datasetId);
            
            // The data-stats API returns data with success wrapper
            if (data && data.success && data.stats) {
                this.displayDataStats(data.stats);
            } else {
                this.showDataStatsError(data.message || 'No statistics data received from server');
            }
        } catch (error) {
            console.error('Failed to load data stats:', error);
            this.showDataStatsError('Failed to load data statistics.');
        }
    }

    // Display data statistics
    displayDataStats(stats) {
        const dataStatsSection = document.getElementById('dataStatsSection');
        
        if (!dataStatsSection) return;

        // Extract counts from the actual API response structure
        const patientCount = stats.patients?.row_count || 0;
        const taxonomyCount = stats.taxonomy?.row_count || 0;
        const brackenCount = stats.bracken?.row_count || 0;
        const validatedCount = this.getValidatedFileCount();

        const statsHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="card border-primary">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-2x text-primary mb-2"></i>
                            <h5 class="card-title">${patientCount}</h5>
                            <p class="card-text text-muted mb-0">Patients</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-info">
                        <div class="card-body text-center">
                            <i class="fas fa-sitemap fa-2x text-info mb-2"></i>
                            <h5 class="card-title">${taxonomyCount}</h5>
                            <p class="card-text text-muted mb-0">Taxa</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-success">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-bar fa-2x text-success mb-2"></i>
                            <h5 class="card-title">${brackenCount}</h5>
                            <p class="card-text text-muted mb-0">Abundance Records</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card border-warning">
                        <div class="card-body text-center">
                            <i class="fas fa-check-circle fa-2x text-warning mb-2"></i>
                            <h5 class="card-title">${validatedCount}</h5>
                            <p class="card-text text-muted mb-0">Validated Files</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        dataStatsSection.innerHTML = statsHTML;
    }

    // Get count of validated files
    getValidatedFileCount() {
        return this.files.filter(file => 
            file.cure_validation_status === 'ok' || file.cure_validation_status === 'validated'
        ).length;
    }

    // Show data stats error
    showDataStatsError(message) {
        const dataStatsSection = document.getElementById('dataStatsSection');
        if (dataStatsSection) {
            dataStatsSection.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Unable to load statistics:</strong> ${message}
                </div>
            `;
        }
    }
}

// Global functions for file operations
window.viewFile = function(fileId) {
    window.open(`/dataset/file/${fileId}/view`, '_blank');
};

window.downloadFile = function(fileId) {
    window.open(`/dataset/file/${fileId}/download`, '_blank');
};

window.duplicateFile = function(fileId) {
    if (confirm('Are you sure you want to duplicate this file?')) {
        // Implementation for file duplication
        DatasetUtils.showAlert('File duplication feature coming soon', 'info');
    }
};

window.renameFile = function(fileId, currentName, fileType) {
    const newName = prompt('Enter new file name:', currentName);
    if (newName && newName !== currentName) {
        // Implementation for file renaming
        DatasetUtils.showAlert('File renaming feature coming soon', 'info');
    }
};

window.editTable = function(fileId) {
    window.open(`/dataset/file/${fileId}/edit`, '_blank');
};

window.cureData = function(fileId) {
    if (confirm('Are you sure you want to cure this data? This will process and validate the file.')) {
        // Implementation for data curing
        DatasetUtils.showAlert('Data curing feature coming soon', 'info');
    }
};

window.deleteFile = function(fileId) {
    if (confirm('Are you sure you want to delete this file? This action cannot be undone.')) {
        // Implementation for file deletion
        DatasetUtils.showAlert('File deletion feature coming soon', 'info');
    }
};

// Initialize files tab when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const datasetId = window.datasetId;
    if (datasetId) {
        const filesManager = new DatasetFilesManager(datasetId);
        filesManager.init();
    }
});

// Export for external use
window.DatasetFilesManager = DatasetFilesManager;
