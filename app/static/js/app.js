// Main JavaScript for Microbiome Analysis Platform

// Global app object
const MicrobiomeApp = {
    // Configuration - will be loaded from server
    config: {
        apiBaseUrl: '/api',
        maxFileSize: 16 * 1024 * 1024, // Default 16MB, will be updated from server
        allowedFileTypes: ['.csv', '.xlsx', '.xls', '.json'],
        refreshInterval: 30000 // 30 seconds
    },

    // Initialize the application
    async init() {
        await this.loadConfiguration();
        this.setupEventListeners();
        this.initializeTooltips();
        this.setupFormValidation();
        this.checkAuthStatus();
        console.log('Microbiome Analysis Platform initialized with config:', this.config);
    },

    // Load configuration from server
    async loadConfiguration() {
        try {
            const response = await fetch('/api/config');
            if (response.ok) {
                const serverConfig = await response.json();
                // Update config with server values
                this.config.maxFileSize = serverConfig.maxFileSize;
                this.config.maxFileSizeMB = serverConfig.maxFileSizeMB;
                this.config.allowedFileTypes = serverConfig.allowedFileTypes;
                console.log('Configuration loaded from server:', serverConfig);
            } else {
                console.warn('Failed to load server configuration, using defaults');
            }
        } catch (error) {
            console.warn('Error loading server configuration:', error);
        }
    },

    // Setup global event listeners
    setupEventListeners() {
        // Handle flash message auto-dismiss
        this.setupFlashMessages();
        
        // Handle form submissions
        this.setupFormSubmissions();
        
        // Handle file uploads
        this.setupFileUploads();
        
        // Handle navigation
        this.setupNavigation();
    },

    // Initialize Bootstrap tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Setup form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    },

    // Setup flash messages
    setupFlashMessages() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        
        alerts.forEach(alert => {
            // Auto-dismiss success messages after 5 seconds
            if (alert.classList.contains('alert-success')) {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 5000);
            }
            
            // Auto-dismiss info messages after 7 seconds
            if (alert.classList.contains('alert-info')) {
                setTimeout(() => {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }, 7000);
            }
        });
    },

    // Setup form submissions with loading states
    setupFormSubmissions() {
        const forms = document.querySelectorAll('form[data-loading]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    const originalText = submitButton.innerHTML;
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                    
                    // Re-enable after 10 seconds as fallback
                    setTimeout(() => {
                        submitButton.disabled = false;
                        submitButton.innerHTML = originalText;
                    }, 10000);
                }
            });
        });
    },

    // Setup file upload handling
    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.validateFileUpload(e.target);
            });
        });
    },

    // Validate file uploads
    validateFileUpload(input) {
        const files = input.files;
        const validFiles = [];
        const errors = [];

        Array.from(files).forEach(file => {
            // Check file size
            if (file.size > this.config.maxFileSize) {
                const maxSizeMB = this.config.maxFileSizeMB || (this.config.maxFileSize / (1024 * 1024));
                errors.push(`${file.name} is too large. Maximum size is ${maxSizeMB}MB.`);
                return;
            }

            // Check file type
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            if (!this.config.allowedFileTypes.includes(extension)) {
                errors.push(`${file.name} has an unsupported file type.`);
                return;
            }

            validFiles.push(file);
        });

        // Show errors if any
        if (errors.length > 0) {
            this.showAlert('error', errors.join('<br>'));
            input.value = ''; // Clear the input
            return false;
        }

        return true;
    },

    // Setup navigation enhancements
    setupNavigation() {
        // Highlight current page in navigation
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('active');
            }
        });

        // Handle dropdown menus
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('click', function(e) {
                e.preventDefault();
            });
        });
    },

    // Check authentication status
    checkAuthStatus() {
        // This could be expanded to periodically check if user is still authenticated
        const userMenu = document.querySelector('.navbar .dropdown-toggle');
        if (userMenu) {
            console.log('User is authenticated');
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
                const response = await fetch(`${MicrobiomeApp.config.apiBaseUrl}${endpoint}`, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                MicrobiomeApp.showAlert('error', 'Failed to communicate with server. Please try again.');
                throw error;
            }
        },

        // Get user's datasets
        async getDatasets() {
            return this.call('/datasets');
        },

        // Create new dataset
        async createDataset(data) {
            return this.call('/datasets', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        }
    },

    // Utility methods
    utils: {
        // Format file size
        formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        // Format date
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },

        // Format date and time
        formatDateTime(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
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
        }
    },

    // Show alert messages
    showAlert(type, message, dismissible = true) {
        const alertContainer = document.querySelector('.container:first-of-type') || document.body;
        const alertId = `alert-${this.utils.generateId()}`;
        
        const alertHTML = `
            <div class="alert alert-${type === 'error' ? 'danger' : type} ${dismissible ? 'alert-dismissible' : ''} fade show" role="alert" id="${alertId}">
                ${message}
                ${dismissible ? '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' : ''}
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHTML);
        
        // Auto-dismiss after delay
        if (dismissible) {
            setTimeout(() => {
                const alertElement = document.getElementById(alertId);
                if (alertElement) {
                    const bsAlert = new bootstrap.Alert(alertElement);
                    bsAlert.close();
                }
            }, type === 'success' ? 5000 : 7000);
        }
    },

    // Loading spinner methods
    showLoading(element = null, text = 'Loading...') {
        const target = element || document.body;
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
        } else {
            target.insertAdjacentHTML('beforeend', loadingHTML);
        }
    },

    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
};

// Dataset management specific functions
const DatasetManager = {
    // Refresh dataset list
    async refreshDatasets() {
        try {
            const datasets = await MicrobiomeApp.api.getDatasets();
            this.updateDatasetDisplay(datasets);
        } catch (error) {
            console.error('Failed to refresh datasets:', error);
        }
    },

    // Update dataset display
    updateDatasetDisplay(datasets) {
        const gridContainer = document.getElementById('grid-container');
        const listContainer = document.getElementById('list-container');
        
        if (gridContainer) {
            // Update grid view
            this.updateGridView(gridContainer, datasets);
        }
        
        if (listContainer) {
            // Update list view
            this.updateListView(listContainer, datasets);
        }
    },

    // Update grid view
    updateGridView(container, datasets) {
        // Implementation for updating grid view
        // This would be expanded based on specific requirements
    },

    // Update list view
    updateListView(container, datasets) {
        // Implementation for updating list view
        // This would be expanded based on specific requirements
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    MicrobiomeApp.init().catch(error => {
        console.error('Failed to initialize MicrobiomeApp:', error);
    });
    
    // Page-specific initialization
    const currentPage = document.body.getAttribute('data-page');
    
    switch (currentPage) {
        case 'dashboard':
            // Dashboard-specific initialization
            console.log('Dashboard page loaded');
            break;
        case 'dataset':
            // Dataset view specific initialization
            console.log('Dataset page loaded');
            break;
        case 'new-dataset':
            // New dataset specific initialization
            console.log('New dataset page loaded');
            break;
        default:
            console.log('General page loaded');
    }
});

// Handle browser back/forward buttons
window.addEventListener('popstate', function(event) {
    // Handle navigation state changes if needed
    console.log('Navigation state changed');
});

// Handle online/offline status
window.addEventListener('online', function() {
    MicrobiomeApp.showAlert('success', 'Connection restored!');
});

window.addEventListener('offline', function() {
    MicrobiomeApp.showAlert('warning', 'You are currently offline. Some features may not be available.');
});

// Export for global access
window.MicrobiomeApp = MicrobiomeApp;
window.DatasetManager = DatasetManager;
