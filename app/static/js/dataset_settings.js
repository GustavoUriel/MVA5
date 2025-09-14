// Dataset Settings Tab JavaScript
// Handles dataset settings and configuration

class DatasetSettingsManager {
    constructor(datasetId) {
        this.datasetId = datasetId;
        this.originalSettings = {};
    }

    // Initialize settings tab
    async init() {
        this.setupEventListeners();
        await this.loadDatasetSettings();
    }

    // Setup event listeners
    setupEventListeners() {
        // Form submission
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }

        // Form validation
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                this.validateForm();
            });
        });

        // Privacy settings change
        const privacyRadios = document.querySelectorAll('input[name="privacy"]');
        privacyRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handlePrivacyChange(e.target.value);
            });
        });
    }

    // Load dataset settings
    async loadDatasetSettings() {
        try {
            // For now, use default settings since the endpoint doesn't exist yet
            const defaultSettings = {
                name: document.getElementById('datasetName')?.value || '',
                description: document.getElementById('datasetDescription')?.value || '',
                status: document.querySelector('select')?.value || 'draft',
                privacy: 'private'
            };
            
            this.populateSettingsForm(defaultSettings);
            this.originalSettings = { ...defaultSettings };
        } catch (error) {
            console.error('Failed to load dataset settings:', error);
            DatasetUtils.showAlert('Failed to load dataset settings', 'error');
        }
    }

    // Populate settings form
    populateSettingsForm(settings) {
        // Dataset name
        const nameInput = document.getElementById('datasetName');
        if (nameInput && settings.name) {
            nameInput.value = settings.name;
        }

        // Dataset description
        const descriptionInput = document.getElementById('datasetDescription');
        if (descriptionInput && settings.description) {
            descriptionInput.value = settings.description;
        }

        // Dataset status
        const statusSelect = document.querySelector('select');
        if (statusSelect && settings.status) {
            statusSelect.value = settings.status;
        }

        // Privacy settings
        const privacyRadios = document.querySelectorAll('input[name="privacy"]');
        privacyRadios.forEach(radio => {
            if (radio.value === settings.privacy) {
                radio.checked = true;
            }
        });
    }

    // Save settings
    async saveSettings() {
        if (!this.validateForm()) {
            return;
        }

        try {
            const settings = this.collectSettings();
            
            // For now, just update the local state since the endpoint doesn't exist yet
            DatasetUtils.showAlert('Settings saved locally (server endpoint coming soon)', 'info');
            this.originalSettings = { ...settings };
            
            // TODO: Implement actual server save when endpoint is available
            // const response = await DatasetUtils.api.call(`/dataset/${this.datasetId}/settings`, {
            //     method: 'PUT',
            //     body: JSON.stringify(settings)
            // });
        } catch (error) {
            console.error('Save settings error:', error);
            DatasetUtils.showAlert('Failed to save settings', 'error');
        }
    }

    // Collect settings from form
    collectSettings() {
        return {
            name: document.getElementById('datasetName').value.trim(),
            description: document.getElementById('datasetDescription').value.trim(),
            status: document.querySelector('select').value,
            privacy: document.querySelector('input[name="privacy"]:checked').value
        };
    }

    // Validate form
    validateForm() {
        const form = document.querySelector('form');
        if (!form) return true;

        // Clear previous validation
        DatasetUtils.clearFormValidation(form);

        let isValid = true;

        // Validate dataset name
        const nameInput = document.getElementById('datasetName');
        if (nameInput && !nameInput.value.trim()) {
            nameInput.classList.add('is-invalid');
            isValid = false;
        }

        // Validate status selection
        const statusSelect = document.querySelector('select');
        if (statusSelect && !statusSelect.value) {
            statusSelect.classList.add('is-invalid');
            isValid = false;
        }

        // Validate privacy selection
        const privacyChecked = document.querySelector('input[name="privacy"]:checked');
        if (!privacyChecked) {
            const privacyRadios = document.querySelectorAll('input[name="privacy"]');
            privacyRadios.forEach(radio => {
                radio.classList.add('is-invalid');
            });
            isValid = false;
        }

        return isValid;
    }

    // Handle privacy change
    handlePrivacyChange(privacyValue) {
        const privacyRadios = document.querySelectorAll('input[name="privacy"]');
        privacyRadios.forEach(radio => {
            radio.classList.remove('is-invalid');
        });

        // Show additional options based on privacy setting
        if (privacyValue === 'shared') {
            this.showSharedOptions();
        } else {
            this.hideSharedOptions();
        }
    }

    // Show shared options
    showSharedOptions() {
        // Implementation for showing shared dataset options
        DatasetUtils.showAlert('Shared dataset features coming soon', 'info');
    }

    // Hide shared options
    hideSharedOptions() {
        // Implementation for hiding shared dataset options
    }

    // Check for unsaved changes
    hasUnsavedChanges() {
        const currentSettings = this.collectSettings();
        return JSON.stringify(currentSettings) !== JSON.stringify(this.originalSettings);
    }

    // Warn about unsaved changes
    warnUnsavedChanges() {
        if (this.hasUnsavedChanges()) {
            return confirm('You have unsaved changes. Are you sure you want to leave this page?');
        }
        return true;
    }
}

// Global functions for settings operations
window.saveDatasetSettings = function() {
    if (window.settingsManager) {
        window.settingsManager.saveSettings();
    }
};

window.cancelSettingsChanges = function() {
    if (window.settingsManager) {
        if (window.settingsManager.hasUnsavedChanges()) {
            if (confirm('Are you sure you want to discard your changes?')) {
                window.settingsManager.loadDatasetSettings();
            }
        }
    }
};

// Warn before leaving page with unsaved changes
window.addEventListener('beforeunload', function(e) {
    if (window.settingsManager && window.settingsManager.hasUnsavedChanges()) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Initialize settings tab when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const datasetId = window.datasetId;
    if (datasetId) {
        window.settingsManager = new DatasetSettingsManager(datasetId);
        window.settingsManager.init();
    }
});

// Export for external use
window.DatasetSettingsManager = DatasetSettingsManager;
