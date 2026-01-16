// Dataset utility functions
// Shared functions used across multiple dataset tabs

// Global utility functions
window.DatasetUtils = {
    // Format file size in human-readable format
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Get color class for file type
    getFileTypeColor(fileType) {
        const colors = {
            'patients': 'primary',
            'taxonomy': 'info',
            'bracken': 'success',
            'csv': 'secondary',
            'tsv': 'warning',
            'txt': 'dark'
        };
        return colors[fileType] || 'secondary';
    },

    // Get status badge HTML
    getStatusBadge(cureStatus, validationStatus) {
        if (validationStatus === 'validated') {
            if (cureStatus === 'cured') {
                return '<span class="badge bg-success">Cured & Validated</span>';
            } else {
                return '<span class="badge bg-warning">Validated</span>';
            }
        } else if (cureStatus === 'cured') {
            return '<span class="badge bg-info">Cured</span>';
        } else {
            return '<span class="badge bg-secondary">Raw</span>';
        }
    },

    // Get cure status icon
    getCureStatusIcon(cureStatus, validationStatus) {
        if (cureStatus === 'cured') {
            if (validationStatus === 'ok') {
                return '<i class="fas fa-check-circle text-success"></i>';
            } else {
                return '<i class="fas fa-check-circle text-info"></i>';
            }
        } else {
            return '<i class="fas fa-circle text-muted"></i>';
        }
    },

    // Show alert messages
    showAlert(message, type = 'info') {
        const alertContainer = document.querySelector('.container:first-of-type') || document.body;
        const alertId = `alert-${Math.random().toString(36).substr(2, 9)}`;
        
        const alertHTML = `
            <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert" id="${alertId}">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-dismiss after delay
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                const bsAlert = new bootstrap.Alert(alertElement);
                bsAlert.close();
            }
        }, type === 'success' ? 5000 : 7000);
    },

    // Show toast notifications
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toastId = `toast-${Math.random().toString(36).substr(2, 9)}`;
        const toastHTML = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-${type === 'success' ? 'check-circle text-success' : type === 'error' ? 'exclamation-circle text-danger' : 'info-circle text-info'} me-2"></i>
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    },

    // Create toast container if it doesn't exist
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },

    // Format group name for display
    formatGroupName(groupName) {
        return groupName
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    },

    // Format time point name for display
    formatTimePointName(timePointKey) {
        return timePointKey
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Generate random ID
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    },

    // Validate form inputs
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    // Clear form validation
    clearFormValidation(formElement) {
        const inputs = formElement.querySelectorAll('.is-invalid');
        inputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
    },

    // Show loading state
    showLoading(element, text = 'Loading...') {
        const loadingHTML = `
            <div class="d-flex justify-content-center align-items-center" id="loading-spinner">
                <div class="spinner-border text-primary me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>${text}</span>
            </div>
        `;
        
        if (element) {
            element.innerHTML = loadingHTML;
        }
    },

    // Hide loading state
    hideLoading(element) {
        const spinner = element ? element.querySelector('#loading-spinner') : document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    },

    // API helper methods
    api: {
        // Generic API call method
        async call(endpoint, options = {}) {
            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            };

            const config = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(endpoint, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                DatasetUtils.showAlert('Failed to communicate with server. Please try again.', 'error');
                throw error;
            }
        },

        // Get dataset files
        async getDatasetFiles(datasetId) {
            return this.call(`/dataset/${datasetId}/files/api`);
        },

        // Get dataset stats
        async getDatasetStats(datasetId) {
            return this.call(`/dataset/${datasetId}/data-stats`);
        },

        // Get column groups
        async getColumnGroups(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/column-groups`);
        },

        // Get attribute discarding policies
        async getAttributeDiscarding(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/attribute-discarding`);
        },

        // Get bracken time points
        async getBrackenTimePoints(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/bracken-time-points`);
        },

        // Get stratifications
        async getStratifications(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/stratifications`);
        },

        // Get clustering methods
        async getClusteringMethods(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/clustering-methods`);
        },

        // Get analysis methods
        async getAnalysisMethods(datasetId) {
            return this.call(`/dataset/${datasetId}/metadata/analysis-methods`);
        }
    }
};

// Export for global access
window.DatasetUtils = DatasetUtils;
