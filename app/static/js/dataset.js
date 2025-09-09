// Dataset page JavaScript functionality
// Global variables
let datasetId = null;

// Initialize dataset page
document.addEventListener('DOMContentLoaded', function() {
    // Extract dataset ID from URL
    const pathParts = window.location.pathname.split('/');
    datasetId = parseInt(pathParts[2]);
    
    if (datasetId) {
        initializeDatasetPage();
    }
});

function initializeDatasetPage() {
    // Load data based on current tab
    const pathParts = window.location.pathname.split('/');
    const currentTab = pathParts[3] || 'files';
    
    switch(currentTab) {
        case 'files':
            loadFilesTab();
            break;
        case 'analysis':
            loadAnalysisTab();
            break;
        case 'reports':
            loadReportsTab();
            break;
        case 'settings':
            loadSettingsTab();
            break;
    }
}

// Files Tab Functions
function loadFilesTab() {
    loadDataStats();
    loadFilesTable();
}

function loadDataStats() {
    const statsSection = document.getElementById('dataStatsSection');
    if (!statsSection) return;
    
    fetch(`/dataset/${datasetId}/data-stats`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayDataStats(data.stats);
            } else {
                showDataStatsError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading data stats:', error);
            showDataStatsError('Failed to load data statistics');
        });
}

function loadFilesTable() {
    const filesTable = document.getElementById('filesTable');
    if (!filesTable) return;
    
    fetch(`/dataset/${datasetId}/files/api`)
        .then(response => response.json())
        .then(data => {
            displayFilesTable(data.files, data.dataset_status);
        })
        .catch(error => {
            console.error('Error loading files:', error);
            filesTable.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-2x text-danger mb-3"></i>
                    <p class="text-danger">Failed to load files</p>
                </div>
            `;
        });
}

function displayFilesTable(files, datasetStatus) {
    const filesTable = document.getElementById('filesTable');
    if (!filesTable) return;
    
    if (files.length === 0) {
        filesTable.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-folder-open fa-2x text-muted mb-3"></i>
                <p class="text-muted">No files uploaded yet</p>
            </div>
        `;
        return;
    }
    
    let html = `
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
    `;
    
    files.forEach(file => {
        const sizeFormatted = formatFileSize(file.size);
        const statusBadge = getStatusBadge(file.cure_status, file.cure_validation_status);
        const uploadedDate = new Date(file.uploaded_at).toLocaleDateString();
        
        html += `
            <tr>
                <td>
                    <i class="fas fa-file me-2 text-muted"></i>
                    ${file.filename}
                </td>
                <td>
                    <span class="badge bg-${getFileTypeColor(file.file_type)}">
                        ${file.file_type}
                    </span>
                </td>
                <td>${sizeFormatted}</td>
                <td>${statusBadge}</td>
                <td>${uploadedDate}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewFile(${file.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="deleteFile(${file.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    filesTable.innerHTML = html;
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getFileTypeColor(fileType) {
    const colors = {
        'patients': 'primary',
        'taxonomy': 'info',
        'bracken': 'success',
        'undefined': 'secondary'
    };
    return colors[fileType] || 'secondary';
}

function getStatusBadge(cureStatus, validationStatus) {
    if (validationStatus === 'validated') {
        return '<span class="badge bg-success">Validated</span>';
    } else if (validationStatus === 'failed') {
        return '<span class="badge bg-danger">Failed</span>';
    } else if (cureStatus === 'cured') {
        return '<span class="badge bg-warning">Cured</span>';
    } else {
        return '<span class="badge bg-secondary">Pending</span>';
    }
}

// Data Stats Functions
function displayDataStats(stats) {
    const statsSection = document.getElementById('dataStatsSection');
    if (!statsSection) return;
    
    let html = '<div class="row">';
    
    // Patients Data Stats
    if (stats.patients && Object.keys(stats.patients).length > 0) {
        html += `
            <div class="col-md-4">
                <div class="card border-primary h-100">
                    <div class="card-header bg-primary text-white">
                        <h6 class="mb-0"><i class="fas fa-user-injured me-2"></i>Patients Data</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <div class="h4 text-primary">${stats.patients.row_count || 0}</div>
                                <small class="text-muted">Total Rows</small>
                            </div>
                            <div class="col-6">
                                <div class="h4 text-primary">${stats.patients.column_count || 0}</div>
                                <small class="text-muted">Columns</small>
                            </div>
                        </div>
                        <div class="small text-muted">
                            <div>Columns: ${stats.patients.columns ? stats.patients.columns.length : 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Taxonomy Data Stats
    if (stats.taxonomy && Object.keys(stats.taxonomy).length > 0) {
        html += `
            <div class="col-md-4">
                <div class="card border-info h-100">
                    <div class="card-header bg-info text-white">
                        <h6 class="mb-0"><i class="fas fa-sitemap me-2"></i>Taxonomy Data</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <div class="h4 text-info">${stats.taxonomy.row_count || 0}</div>
                                <small class="text-muted">Total Rows</small>
                            </div>
                            <div class="col-6">
                                <div class="h4 text-info">${stats.taxonomy.column_count || 0}</div>
                                <small class="text-muted">Columns</small>
                            </div>
                        </div>
                        <div class="small text-muted">
                            <div>Columns: ${stats.taxonomy.columns ? stats.taxonomy.columns.length : 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Bracken Data Stats
    if (stats.bracken && Object.keys(stats.bracken).length > 0) {
        html += `
            <div class="col-md-4">
                <div class="card border-success h-100">
                    <div class="card-header bg-success text-white">
                        <h6 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Bracken Data</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center mb-3">
                            <div class="col-6">
                                <div class="h4 text-success">${stats.bracken.row_count || 0}</div>
                                <small class="text-muted">Total Rows</small>
                            </div>
                            <div class="col-6">
                                <div class="h4 text-success">${stats.bracken.column_count || 0}</div>
                                <small class="text-muted">Columns</small>
                            </div>
                        </div>
                        <div class="small text-muted">
                            <div>Columns: ${stats.bracken.columns ? stats.bracken.columns.length : 0}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    statsSection.innerHTML = html;
}

function showDataStatsError(error) {
    const statsSection = document.getElementById('dataStatsSection');
    if (!statsSection) return;
    
    statsSection.innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
            <p class="text-warning">Failed to load data statistics</p>
            <small class="text-muted">${error}</small>
        </div>
    `;
}

// File Actions
function viewFile(fileId) {
    // TODO: Implement file viewing
    console.log('View file:', fileId);
}

function deleteFile(fileId) {
    if (confirm('Are you sure you want to delete this file?')) {
        // TODO: Implement file deletion
        console.log('Delete file:', fileId);
    }
}

// Tab Navigation
function goToTab(tabName) {
    window.location.href = `/dataset/${datasetId}/${tabName}`;
}

// Analysis Tab Functions
function loadAnalysisTab() {
    loadAnalysisList();
    setupAnalysisEditor();
}

function loadAnalysisList() {
    // For now, show the "no analyses" state
    // TODO: Implement actual analysis loading from API
    const analysisListContainer = document.getElementById('analysisListContainer');
    if (analysisListContainer) {
        const noAnalysesState = document.getElementById('noAnalysesState');
        const analysisTable = document.getElementById('analysisTable');
        
        if (noAnalysesState) {
            noAnalysesState.style.display = 'block';
        }
        if (analysisTable) {
            analysisTable.style.display = 'none';
        }
    }
}

function createNewAnalysis() {
    console.log('Creating new analysis...');
    
    // Hide the analysis list and show the editor
    const analysisListContainer = document.getElementById('analysisListContainer');
    const analysisEditorSection = document.getElementById('analysisEditorSection');
    
    if (analysisListContainer) {
        analysisListContainer.style.display = 'none';
    }
    
    if (analysisEditorSection) {
        analysisEditorSection.style.display = 'block';
        
        // Reset the editor form
        resetAnalysisEditor();
        
        // Load files for data source dropdowns
        loadFilesForDataSources();
        
        // Load column groups
        loadColumnGroups();
        
        // Load bracken time points
        loadBrackenTimePoints();
        
        // Load stratifications
        loadStratifications();
    }
}

function refreshAnalysisList() {
    console.log('Refreshing analysis list...');
    loadAnalysisList();
}

function cancelAnalysisEdit() {
    console.log('Canceling analysis edit...');
    
    // Hide the editor and show the analysis list
    const analysisListContainer = document.getElementById('analysisListContainer');
    const analysisEditorSection = document.getElementById('analysisEditorSection');
    
    if (analysisListContainer) {
        analysisListContainer.style.display = 'block';
    }
    
    if (analysisEditorSection) {
        analysisEditorSection.style.display = 'none';
    }
}

function saveAnalysis() {
    console.log('Saving analysis...');
    
    const analysisName = document.getElementById('analysisName')?.value;
    const analysisDescription = document.getElementById('analysisDescription')?.value;
    
    if (!analysisName) {
        alert('Please enter an analysis name');
        return;
    }
    
    // TODO: Implement actual save functionality
    console.log('Saving analysis:', { name: analysisName, description: analysisDescription });
    
    // For now, just show success message
    alert('Analysis saved successfully!');
}

function runAnalysisFromEditor() {
    console.log('Running analysis from editor...');
    
    // Validate required fields
    const analysisName = document.getElementById('analysisName')?.value;
    if (!analysisName) {
        alert('Please enter an analysis name');
        return;
    }
    
    // TODO: Implement actual analysis execution
    console.log('Running analysis with current configuration');
    
    // For now, just show success message
    alert('Analysis started! Check the Reports tab for results.');
}

function resetAnalysisEditor() {
    // Reset form fields
    const analysisName = document.getElementById('analysisName');
    const analysisDescription = document.getElementById('analysisDescription');
    
    if (analysisName) analysisName.value = '';
    if (analysisDescription) analysisDescription.value = '';
    
    // Reset file selections
    const patientSelect = document.getElementById('editorPatientFileSelect');
    const taxonomySelect = document.getElementById('editorTaxonomyFileSelect');
    const brackenSelect = document.getElementById('editorBrackenFileSelect');
    
    if (patientSelect) patientSelect.value = '';
    if (taxonomySelect) taxonomySelect.value = '';
    if (brackenSelect) brackenSelect.value = '';
    
    // Reset analysis type to default
    const alphaDivRadio = document.getElementById('editorAlphaDiv');
    if (alphaDivRadio) alphaDivRadio.checked = true;
}

function loadFilesForDataSources() {
    // Load files for the data source dropdowns
    fetch(`/dataset/${datasetId}/files/api`)
        .then(response => response.json())
        .then(data => {
            populateFileDropdowns(data.files);
        })
        .catch(error => {
            console.error('Error loading files for data sources:', error);
        });
}

function populateFileDropdowns(files) {
    const patientSelect = document.getElementById('editorPatientFileSelect');
    const taxonomySelect = document.getElementById('editorTaxonomyFileSelect');
    const brackenSelect = document.getElementById('editorBrackenFileSelect');
    
    // Clear existing options (except the first one)
    [patientSelect, taxonomySelect, brackenSelect].forEach(select => {
        if (select) {
            while (select.children.length > 1) {
                select.removeChild(select.lastChild);
            }
        }
    });
    
    // Populate dropdowns based on file type
    files.forEach(file => {
        const option = document.createElement('option');
        option.value = file.id;
        option.textContent = `${file.filename} (${formatFileSize(file.size)})`;
        
        switch(file.file_type) {
            case 'patients':
                if (patientSelect) patientSelect.appendChild(option.cloneNode(true));
                break;
            case 'taxonomy':
                if (taxonomySelect) taxonomySelect.appendChild(option.cloneNode(true));
                break;
            case 'bracken':
                if (brackenSelect) brackenSelect.appendChild(option.cloneNode(true));
                break;
        }
    });
}

function loadColumnGroups() {
    console.log('Loading column groups from metadata...');
    
    fetch(`/dataset/${datasetId}/metadata/column-groups`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayColumnGroups(data.column_groups);
            } else {
                console.error('Error loading column groups:', data.error);
                showColumnGroupsError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading column groups:', error);
            showColumnGroupsError('Failed to load column groups');
        });
}

function displayColumnGroups(columnGroups) {
    const columnGroupsContainer = document.getElementById('columnGroupsContainer');
    if (!columnGroupsContainer) return;
    
    // Store the original column groups data for toggling
    window.columnGroupsData = columnGroups;
    
    let html = '';
    let groupIndex = 0;
    
    // columnGroups is now an ordered array from the backend
    columnGroups.forEach(group => {
        const groupId = `colGroup${groupIndex}`;
        const displayName = formatGroupName(group.name);
        const columnCount = group.columns.length;
        
        // Create a list of field names, sorted as they appear in the metadata file
        const fieldNames = group.columns.map(field => `<span class="badge bg-light text-dark me-1 mb-1">${field}</span>`).join('');
        
        html += `
            <div class="col-md-6 mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${groupId}" checked onchange="updateColumnGroupsSummary()">
                    <label class="form-check-label" for="${groupId}">
                        <strong>${displayName}</strong>
                        <small class="text-muted d-block">${columnCount} columns</small>
                        <div class="mt-1 field-names" style="display: none;">
                            ${fieldNames}
                        </div>
                    </label>
                </div>
            </div>
        `;
        groupIndex++;
    });
    
    columnGroupsContainer.innerHTML = html;
    
    // Update summary after loading
    updateColumnGroupsSummary();
}

function formatGroupName(groupName) {
    // Convert snake_case to Title Case
    return groupName
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function showColumnGroupsError(error) {
    const columnGroupsContainer = document.getElementById('columnGroupsContainer');
    if (!columnGroupsContainer) return;
    
    columnGroupsContainer.innerHTML = `
        <div class="col-12">
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Failed to load column groups: ${error}
            </div>
        </div>
    `;
}

function loadBrackenTimePoints() {
    console.log('Loading bracken time points from metadata...');
    
    fetch(`/dataset/${datasetId}/metadata/bracken-time-points`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayBrackenTimePoints(data.time_points, data.default_time_point);
            } else {
                console.error('Error loading bracken time points:', data.error);
                showBrackenTimePointsError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading bracken time points:', error);
            showBrackenTimePointsError('Failed to load bracken time points');
        });
}

function loadStratifications() {
    console.log('Loading stratifications from metadata...');
    
    fetch(`/dataset/${datasetId}/metadata/stratifications`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStratifications(data.stratifications);
            } else {
                console.error('Error loading stratifications:', data.error);
                showStratificationsError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading stratifications:', error);
            showStratificationsError('Failed to load stratifications');
        });
}

function displayBrackenTimePoints(timePoints, defaultTimePoint = null) {
    const timePointSelect = document.getElementById('editorBrackenTimePointSelect');
    if (!timePointSelect) return;
    
    // Clear existing options (except the first one)
    while (timePointSelect.children.length > 1) {
        timePointSelect.removeChild(timePointSelect.lastChild);
    }
    
    // timePoints is now an ordered array from the backend
    timePoints.forEach(timePoint => {
        const option = document.createElement('option');
        option.value = timePoint.key;
        option.textContent = `${formatTimePointName(timePoint.key)} - ${timePoint.description}`;
        option.setAttribute('data-suffix', timePoint.suffix);
        option.setAttribute('data-function', timePoint.function);
        
        // Set as selected if it's the default
        if (defaultTimePoint && timePoint.key === defaultTimePoint) {
            option.selected = true;
        }
        
        timePointSelect.appendChild(option);
    });
    
    // Update description if default was set
    if (defaultTimePoint) {
        updateTimePointDescription();
    }
}

function formatTimePointName(timePointKey) {
    // Convert snake_case to Title Case
    return timePointKey
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function displayStratifications(stratifications) {
    const stratificationContainer = document.getElementById('stratificationContainer');
    if (!stratificationContainer) return;
    
    let html = '';
    let groupIndex = 0;
    
    stratifications.forEach(group => {
        html += `
            <div class="mb-4">
                <h6 class="text-primary mb-3">
                    <i class="fas fa-layer-group me-2"></i>
                    ${group.group_label}
                </h6>
                <div class="row">
        `;
        
        group.stratifications.forEach(stratification => {
            const stratId = `strat_${groupIndex}_${stratification.name}`;
            const groupCount = stratification.groups.length;
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="${stratId}" onchange="updateStratificationSummary()">
                        <label class="form-check-label" for="${stratId}">
                            <strong>${stratification.label}</strong>
                            <small class="text-muted d-block">
                                ${stratification.type} • ${groupCount} groups
                                ${stratification.parameters ? `• ${stratification.parameters.length} parameters` : ''}
                            </small>
                            <div class="mt-1 stratification-groups" style="display: none;">
                                ${stratification.groups.map(group => 
                                    `<span class="badge bg-light text-dark me-1 mb-1">${group.label}</span>`
                                ).join('')}
                            </div>
                        </label>
                    </div>
                </div>
            `;
            groupIndex++;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    stratificationContainer.innerHTML = html;
}

function toggleStratification() {
    const stratificationContainer = document.getElementById('stratificationContainer');
    const toggleButton = document.getElementById('toggleStratificationBtn');
    
    if (!stratificationContainer || !toggleButton) return;
    
    const isVisible = stratificationContainer.style.display !== 'none';
    
    stratificationContainer.style.display = isVisible ? 'none' : 'block';
    toggleButton.textContent = isVisible ? 'Show Stratification Options' : 'Hide Stratification Options';
    toggleButton.classList.toggle('btn-outline-secondary', isVisible);
    toggleButton.classList.toggle('btn-secondary', !isVisible);
    
    // Keep stratification summary always visible - don't hide it
    // const summary = document.getElementById('stratificationSummary');
    // if (summary) {
    //     summary.style.display = isVisible ? 'none' : 'block';
    // }
}

function selectAllStratifications() {
    const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateStratificationSummary();
}

function clearAllStratifications() {
    const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateStratificationSummary();
}

function updateStratificationSummary() {
    const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]:checked');
    const summary = document.getElementById('stratificationSummaryText');
    const count = document.getElementById('stratificationCount');
    
    if (summary) {
        summary.textContent = `${checkboxes.length} stratification${checkboxes.length !== 1 ? 's' : ''} selected`;
    }
    
    if (count) {
        count.textContent = `${checkboxes.length} stratification${checkboxes.length !== 1 ? 's' : ''}`;
    }
}

function showStratificationsError(error) {
    const stratificationContainer = document.getElementById('stratificationContainer');
    if (!stratificationContainer) return;
    
    stratificationContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${error}
        </div>
    `;
}

// Clustering Functions
function loadClusteringMethods() {
    console.log('Loading clustering methods from metadata...');
    
    fetch(`/dataset/${datasetId}/metadata/clustering-methods`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayClusteringMethods(data.clustering_methods, data.default_method);
            } else {
                console.error('Error loading clustering methods:', data.error);
                showClusteringError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading clustering methods:', error);
            showClusteringError('Failed to load clustering methods');
        });
}

function displayClusteringMethods(clusteringMethods, defaultMethod = null) {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    if (!methodSelect) return;
    
    // Clear existing options (except the first one)
    while (methodSelect.children.length > 1) {
        methodSelect.removeChild(methodSelect.lastChild);
    }
    
    // Add clustering method options
    Object.entries(clusteringMethods).forEach(([key, method]) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = method.name;
        option.setAttribute('data-description', method.description);
        
        // Set as selected if it's the default
        if (defaultMethod && key === defaultMethod) {
            option.selected = true;
        }
        
        methodSelect.appendChild(option);
    });
    
    // Auto-select default method and load its parameters (but keep container hidden)
    if (defaultMethod) {
        updateClusteringParameters();
        // Ensure parameters container stays hidden initially
        const parametersContainer = document.getElementById('clusteringParametersContainer');
        if (parametersContainer) {
            parametersContainer.style.display = 'none';
        }
    }
}

function updateClusteringParameters() {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    const parametersContainer = document.getElementById('clusteringParametersContainer');
    const parametersForm = document.getElementById('clusteringParametersForm');
    const methodDescription = document.getElementById('clusteringMethodDescription');
    const methodStatus = document.getElementById('clusteringMethodStatus');
    const clusteringSummary = document.getElementById('clusteringSummary');
    
    if (!methodSelect || !parametersContainer || !parametersForm) return;
    
    const selectedMethod = methodSelect.value;
    
    if (!selectedMethod) {
        // Hide parameters and reset UI
        parametersContainer.style.display = 'none';
        clusteringSummary.style.display = 'none';
        if (methodDescription) methodDescription.textContent = 'Choose a clustering algorithm for variable grouping';
        if (methodStatus) {
            methodStatus.textContent = 'No method selected';
            methodStatus.className = 'badge bg-secondary me-2';
        }
        return;
    }
    
    // Update method description and status
    const selectedOption = methodSelect.options[methodSelect.selectedIndex];
    const description = selectedOption.getAttribute('data-description') || 'Clustering method selected';
    
    if (methodDescription) methodDescription.textContent = description;
    if (methodStatus) {
        methodStatus.textContent = 'Method configured';
        methodStatus.className = 'badge bg-success me-2';
    }
    
    // Load method parameters
    fetch(`/dataset/${datasetId}/metadata/clustering-methods/${selectedMethod}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayClusteringParameters(data.method);
                // Don't automatically show parameters container - keep it hidden
                // parametersContainer.style.display = 'block';
                clusteringSummary.style.display = 'block';
                updateClusteringSummary();
            } else {
                console.error('Error loading method parameters:', data.error);
                showClusteringError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading method parameters:', error);
            showClusteringError('Failed to load method parameters');
        });
}

function displayClusteringParameters(method) {
    const parametersForm = document.getElementById('clusteringParametersForm');
    if (!parametersForm || !method.parameters) return;
    
    let html = '<div class="row">';
    
    Object.entries(method.parameters).forEach(([paramKey, paramConfig]) => {
        const paramId = `clustering_param_${paramKey}`;
        const colClass = Object.keys(method.parameters).length > 2 ? 'col-md-6' : 'col-md-4';
        
        html += `
            <div class="${colClass} mb-3">
                <label for="${paramId}" class="form-label">
                    <i class="fas fa-cog text-primary me-2"></i>
                    ${paramConfig.name}
                </label>
        `;
        
        if (paramConfig.type === 'select') {
            html += `
                <select class="form-select" id="${paramId}" onchange="updateClusteringSummary()">
                    <option value="">Select ${paramConfig.name.toLowerCase()}...</option>
            `;
            paramConfig.options.forEach(option => {
                const isDefault = option === paramConfig.default;
                const isBest = option === paramConfig.best_component;
                const selected = isDefault ? 'selected' : '';
                const badge = isBest ? ' (Best)' : '';
                html += `<option value="${option}" ${selected}>${option}${badge}</option>`;
            });
            html += '</select>';
        } else if (paramConfig.type === 'number') {
            const step = paramConfig.step || 1;
            const min = paramConfig.min || 0;
            const max = paramConfig.max || 100;
            html += `
                <input type="number" class="form-control" id="${paramId}" 
                       value="${paramConfig.default}" 
                       min="${min}" max="${max}" step="${step}"
                       onchange="updateClusteringSummary()">
            `;
        }
        
        html += `
                <div class="form-text">
                    ${paramConfig.description}
                    ${paramConfig.best_component && paramConfig.best_component !== 'auto' ? 
                        `<br><small class="text-success"><i class="fas fa-star me-1"></i>Best: ${paramConfig.best_component}</small>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    parametersForm.innerHTML = html;
}

function toggleClustering() {
    const parametersContainer = document.getElementById('clusteringParametersContainer');
    const toggleButton = document.getElementById('toggleClusteringBtn');
    
    if (!parametersContainer || !toggleButton) return;
    
    const isVisible = parametersContainer.style.display !== 'none';
    
    parametersContainer.style.display = isVisible ? 'none' : 'block';
    toggleButton.innerHTML = isVisible ? 
        '<i class="fas fa-eye me-1"></i>Show Clustering Options' : 
        '<i class="fas fa-eye-slash me-1"></i>Hide Clustering Options';
    toggleButton.classList.toggle('btn-outline-secondary', isVisible);
    toggleButton.classList.toggle('btn-secondary', !isVisible);
}

function resetClusteringToDefaults() {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    if (!methodSelect || !methodSelect.value) return;
    
    // Reset all parameter inputs to their default values
    const parameterInputs = document.querySelectorAll('#clusteringParametersForm input, #clusteringParametersForm select');
    parameterInputs.forEach(input => {
        if (input.type === 'number') {
            // Find the default value from the method configuration
            const paramKey = input.id.replace('clustering_param_', '');
            // This would need to be enhanced to get the actual default value
            // For now, we'll just reset to the current value
        } else if (input.tagName === 'SELECT') {
            // Reset to first non-empty option
            const firstOption = Array.from(input.options).find(opt => opt.value !== '');
            if (firstOption) input.value = firstOption.value;
        }
    });
    
    updateClusteringSummary();
    showToast('Clustering parameters reset to defaults', 'success');
}

function applyBestComponents() {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    if (!methodSelect || !methodSelect.value) return;
    
    // Apply best component values to all parameters
    const parameterInputs = document.querySelectorAll('#clusteringParametersForm input, #clusteringParametersForm select');
    parameterInputs.forEach(input => {
        if (input.tagName === 'SELECT') {
            // Find option with "Best" in the text
            const bestOption = Array.from(input.options).find(opt => opt.textContent.includes('Best'));
            if (bestOption) input.value = bestOption.value;
        }
    });
    
    updateClusteringSummary();
    showToast('Best component values applied', 'success');
}

function updateClusteringSummary() {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    const summaryText = document.getElementById('clusteringSummaryText');
    const parametersCount = document.getElementById('clusteringParametersCount');
    const clusteringSummary = document.getElementById('clusteringSummary');
    
    if (!methodSelect || !summaryText || !parametersCount) return;
    
    const selectedMethod = methodSelect.value;
    if (!selectedMethod) {
        clusteringSummary.style.display = 'none';
        return;
    }
    
    const selectedOption = methodSelect.options[methodSelect.selectedIndex];
    const methodName = selectedOption.textContent;
    
    // Count configured parameters
    const parameterInputs = document.querySelectorAll('#clusteringParametersForm input, #clusteringParametersForm select');
    const configuredParams = Array.from(parameterInputs).filter(input => 
        input.value && input.value.trim() !== ''
    ).length;
    
    summaryText.textContent = `${methodName} configured with ${configuredParams} parameters`;
    parametersCount.textContent = `${configuredParams} parameters`;
    clusteringSummary.style.display = 'block';
}

function showClusteringInfo() {
    const methodSelect = document.getElementById('clusteringMethodSelect');
    if (!methodSelect || !methodSelect.value) {
        showToast('Please select a clustering method first', 'warning');
        return;
    }
    
    const selectedOption = methodSelect.options[methodSelect.selectedIndex];
    const methodName = selectedOption.textContent;
    const description = selectedOption.getAttribute('data-description') || 'No description available';
    
    // Create and show info modal
    const modalHtml = `
        <div class="modal fade" id="clusteringInfoModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-info-circle me-2"></i>
                            ${methodName} Information
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Description:</strong></p>
                        <p class="text-muted">${description}</p>
                        <p><strong>Parameters:</strong></p>
                        <ul id="clusteringParametersList">
                            <!-- Parameters will be populated here -->
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('clusteringInfoModal');
    if (existingModal) existingModal.remove();
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Load parameter details
    fetch(`/dataset/${datasetId}/metadata/clustering-methods/${methodSelect.value}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.method.parameters) {
                const parametersList = document.getElementById('clusteringParametersList');
                if (parametersList) {
                    parametersList.innerHTML = Object.entries(data.method.parameters)
                        .map(([key, param]) => `
                            <li>
                                <strong>${param.name}:</strong> ${param.description}
                                ${param.best_component && param.best_component !== 'auto' ? 
                                    `<br><small class="text-success">Best value: ${param.best_component}</small>` : ''}
                            </li>
                        `).join('');
                }
            }
        })
        .catch(error => console.error('Error loading parameter details:', error));
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('clusteringInfoModal'));
    modal.show();
}

function showClusteringError(error) {
    const parametersForm = document.getElementById('clusteringParametersForm');
    if (!parametersForm) return;
    
    parametersForm.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${error}
        </div>
    `;
}

// Cluster Representative Functions
function loadClusterRepresentativeMethods() {
    console.log('Loading cluster representative methods from metadata...');
    
    fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayClusterRepresentativeMethods(data.cluster_representative_methods, data.default_method);
            } else {
                console.error('Error loading cluster representative methods:', data.error);
                showClusterRepresentativeError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading cluster representative methods:', error);
            showClusterRepresentativeError('Failed to load cluster representative methods');
        });
}

function displayClusterRepresentativeMethods(clusterRepMethods, defaultMethod = null) {
    const methodSelect = document.getElementById('clusterRepresentativeMethod');
    if (!methodSelect) return;
    
    // Clear existing options (except the first one)
    while (methodSelect.children.length > 1) {
        methodSelect.removeChild(methodSelect.lastChild);
    }
    
    // Add methods to dropdown
    Object.entries(clusterRepMethods).forEach(([methodKey, methodConfig]) => {
        const option = document.createElement('option');
        option.value = methodKey;
        option.textContent = methodConfig.name;
        methodSelect.appendChild(option);
    });
    
    // Set default method if provided
    if (defaultMethod && clusterRepMethods[defaultMethod]) {
        methodSelect.value = defaultMethod;
        updateClusterRepresentativeMethod();
    }
    
    console.log(`Loaded ${Object.keys(clusterRepMethods).length} cluster representative methods`);
}

function updateClusterRepresentativeMethod() {
    const methodSelect = document.getElementById('clusterRepresentativeMethod');
    const methodStatus = document.getElementById('clusterRepMethodStatus');
    const container = document.getElementById('clusterRepresentativeContainer');
    const summary = document.getElementById('clusterRepSummary');
    
    if (!methodSelect || !methodStatus || !container || !summary) return;
    
    const selectedMethod = methodSelect.value;
    
    if (!selectedMethod) {
        methodStatus.textContent = 'No method selected';
        methodStatus.className = 'badge bg-secondary me-2';
        container.style.display = 'none';
        summary.style.display = 'none';
        return;
    }
    
    // Update status
    methodStatus.textContent = 'Method selected';
    methodStatus.className = 'badge bg-success me-2';
    
    // Load method details
    fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods/${selectedMethod}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayClusterRepresentativeDetails(data.method);
                summary.style.display = 'block';
                updateClusterRepresentativeSummary();
            } else {
                console.error('Error loading method details:', data.error);
                showClusterRepresentativeError(data.error);
            }
        })
        .catch(error => {
            console.error('Error loading method details:', error);
            showClusterRepresentativeError('Failed to load method details');
        });
}

function displayClusterRepresentativeDetails(method) {
    const detailsContainer = document.getElementById('clusterRepresentativeDetails');
    if (!detailsContainer || !method) return;
    
    let html = `
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-info-circle me-2"></i>
                            Method Information
                        </h6>
                        <p class="card-text"><strong>Name:</strong> ${method.name}</p>
                        <p class="card-text"><strong>Description:</strong> ${method.description}</p>
                        <p class="card-text"><strong>Method Type:</strong> ${method.method}</p>
                        <p class="card-text"><strong>Direction:</strong> ${method.direction}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-lightbulb me-2"></i>
                            Explanation
                        </h6>
                        <p class="card-text">${method.explanation}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    detailsContainer.innerHTML = html;
}

function toggleClusterRepresentative() {
    const container = document.getElementById('clusterRepresentativeContainer');
    const button = document.getElementById('toggleClusterRepBtn');
    
    if (!container || !button) return;
    
    const isVisible = container.style.display !== 'none';
    
    if (isVisible) {
        container.style.display = 'none';
        button.innerHTML = '<i class="fas fa-eye me-1"></i>Show Options';
        button.className = 'btn btn-outline-secondary';
    } else {
        container.style.display = 'block';
        button.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Hide Options';
        button.className = 'btn btn-outline-secondary';
    }
}

function resetClusterRepresentativeToDefault() {
    const methodSelect = document.getElementById('clusterRepresentativeMethod');
    if (!methodSelect) return;
    
    // Reset to default method (abundance_highest)
    methodSelect.value = 'abundance_highest';
    updateClusterRepresentativeMethod();
    
    showToast('Cluster representative method reset to default (Highest Mean Abundance)', 'success');
}

function updateClusterRepresentativeSummary() {
    const methodSelect = document.getElementById('clusterRepresentativeMethod');
    const summaryText = document.getElementById('clusterRepSummaryText');
    const methodName = document.getElementById('clusterRepMethodName');
    
    if (!methodSelect || !summaryText || !methodName) return;
    
    const selectedMethod = methodSelect.value;
    const selectedOption = methodSelect.options[methodSelect.selectedIndex];
    
    if (selectedMethod && selectedOption) {
        summaryText.textContent = `Using "${selectedOption.textContent}" method for cluster representative selection`;
        methodName.textContent = selectedOption.textContent;
    } else {
        summaryText.textContent = 'No representative method configured';
        methodName.textContent = 'No method';
    }
}

function showClusterRepresentativeInfo() {
    const methodSelect = document.getElementById('clusterRepresentativeMethod');
    if (!methodSelect || !methodSelect.value) {
        showToast('Please select a cluster representative method first', 'warning');
        return;
    }
    
    const selectedMethod = methodSelect.value;
    
    // Load method details for info modal
    fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods/${selectedMethod}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Create and show info modal
                showClusterRepresentativeInfoModal(data.method);
            } else {
                console.error('Error loading method details:', data.error);
                showToast('Error loading method information', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading method details:', error);
            showToast('Error loading method information', 'error');
        });
}

function showClusterRepresentativeInfoModal(method) {
    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="clusterRepInfoModal" tabindex="-1" aria-labelledby="clusterRepInfoModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="clusterRepInfoModalLabel">
                            <i class="fas fa-users me-2"></i>
                            Cluster Representative Method Information
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-info-circle me-2"></i>Method Details</h6>
                                <p><strong>Name:</strong> ${method.name}</p>
                                <p><strong>Description:</strong> ${method.description}</p>
                                <p><strong>Method Type:</strong> ${method.method}</p>
                                <p><strong>Direction:</strong> ${method.direction}</p>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-lightbulb me-2"></i>Explanation</h6>
                                <p>${method.explanation}</p>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6><i class="fas fa-question-circle me-2"></i>How it works</h6>
                                <p>This method will be used to select a representative taxonomy from each cluster when performing clustering analysis. The selected representative will be used as the cluster name and for further multivariate analysis.</p>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('clusterRepInfoModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('clusterRepInfoModal'));
    modal.show();
    
    // Remove modal from DOM when hidden
    document.getElementById('clusterRepInfoModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function showClusterRepresentativeError(error) {
    const detailsContainer = document.getElementById('clusterRepresentativeDetails');
    if (!detailsContainer) return;
    
    detailsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${error}
        </div>
    `;
}

function showToast(message, type = 'info') {
    // Create toast element
    const toastId = 'toast_' + Date.now();
    const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${type === 'success' ? 'check-circle text-success' : 
                                   type === 'error' ? 'exclamation-triangle text-danger' : 
                                   type === 'warning' ? 'exclamation-triangle text-warning' : 
                                   'info-circle text-info'} me-2"></i>
                <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container (create if doesn't exist)
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'error' ? 5000 : 3000
    });
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Column Groups Toggle Functions
function toggleColumnGroups() {
    const columnGroupsContent = document.getElementById('columnGroupsContent');
    const columnGroupsSummary = document.getElementById('columnGroupsSummary');
    const toggleButton = document.getElementById('toggleColumnGroupsBtn');
    
    if (!columnGroupsContent || !toggleButton) return;
    
    const isVisible = columnGroupsContent.style.display !== 'none';
    
    columnGroupsContent.style.display = isVisible ? 'none' : 'block';
    // Keep summary always visible - don't hide it
    // if (columnGroupsSummary) {
    //     columnGroupsSummary.style.display = isVisible ? 'none' : 'block';
    // }
    
    toggleButton.innerHTML = isVisible ? 
        '<i class="fas fa-eye me-1"></i>Show Column Groups' : 
        '<i class="fas fa-eye-slash me-1"></i>Hide Column Groups';
    toggleButton.classList.toggle('btn-outline-secondary', isVisible);
    toggleButton.classList.toggle('btn-secondary', !isVisible);
}

// Bracken Time Point Functions

function showBrackenTimePointInfo() {
    const timePointSelect = document.getElementById('editorBrackenTimePointSelect');
    if (!timePointSelect) {
        showToast('Time point selector not found', 'warning');
        return;
    }
    
    const selectedOption = timePointSelect.options[timePointSelect.selectedIndex];
    const selectedValue = timePointSelect.value;
    
    if (!selectedValue) {
        showToast('Please select a time point first', 'warning');
        return;
    }
    
    const timePointName = selectedOption.textContent;
    const suffix = selectedOption.getAttribute('data-suffix') || 'N/A';
    const functionType = selectedOption.getAttribute('data-function') || 'N/A';
    
    // Create and show info modal
    const modalHtml = `
        <div class="modal fade" id="brackenTimePointInfoModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-info-circle me-2"></i>
                            Bracken Time Point Information
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Time Point:</strong></p>
                                <p class="text-muted">${timePointName}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Value:</strong></p>
                                <p class="text-muted">${selectedValue}</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>File Suffix:</strong></p>
                                <p class="text-muted">${suffix}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>Function Type:</strong></p>
                                <p class="text-muted">${functionType}</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <p><strong>Description:</strong></p>
                            <p class="text-muted">This time point configuration determines how Bracken abundance data is processed and analyzed for the selected time period.</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('brackenTimePointInfoModal');
    if (existingModal) existingModal.remove();
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('brackenTimePointInfoModal'));
    modal.show();
}

function updateTimePointDescription() {
    const timePointSelect = document.getElementById('editorBrackenTimePointSelect');
    const descriptionElement = document.getElementById('timePointDescription');
    
    if (!timePointSelect) return;
    
    const selectedOption = timePointSelect.options[timePointSelect.selectedIndex];
    const selectedValue = timePointSelect.value;
    
    if (!selectedValue) {
        if (descriptionElement) descriptionElement.textContent = 'Select a time point to see its description';
        return;
    }
    
    const timePointName = selectedOption.textContent;
    const suffix = selectedOption.getAttribute('data-suffix') || '';
    const functionType = selectedOption.getAttribute('data-function') || '';
    
    // Update description
    if (descriptionElement) {
        let description = `Time point: ${timePointName}`;
        if (suffix) description += ` | Suffix: ${suffix}`;
        if (functionType) description += ` | Function: ${functionType}`;
        descriptionElement.textContent = description;
    }
}

function showBrackenTimePointsError(error) {
    const timePointSelect = document.getElementById('editorBrackenTimePointSelect');
    if (!timePointSelect) return;
    
    // Clear existing options (except the first one)
    while (timePointSelect.children.length > 1) {
        timePointSelect.removeChild(timePointSelect.lastChild);
    }
    
    // Add error option
    const errorOption = document.createElement('option');
    errorOption.value = '';
    errorOption.textContent = `Error loading time points: ${error}`;
    errorOption.disabled = true;
    timePointSelect.appendChild(errorOption);
}

function setupAnalysisEditor() {
    // Setup event listeners for the analysis editor
    console.log('Setting up analysis editor...');
    
    // Add event listeners for form validation
    const patientSelect = document.getElementById('editorPatientFileSelect');
    const taxonomySelect = document.getElementById('editorTaxonomyFileSelect');
    const brackenSelect = document.getElementById('editorBrackenFileSelect');
    
    if (patientSelect) {
        patientSelect.addEventListener('change', validateAnalysisEditor);
    }
    if (taxonomySelect) {
        taxonomySelect.addEventListener('change', validateAnalysisEditor);
    }
    if (brackenSelect) {
        brackenSelect.addEventListener('change', validateAnalysisEditor);
    }
    
    // Load clustering methods for the clustering parameters container
    loadClusteringMethods();
    
    // Load cluster representative methods for the cluster representative container
    loadClusterRepresentativeMethods();
}

// Column Groups Functions
function selectAllColumnGroups() {
    const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateColumnGroupsSummary();
}

function clearAllColumnGroups() {
    const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateColumnGroupsSummary();
}

function toggleFieldNames() {
    const fieldNamesElements = document.querySelectorAll('.field-names');
    const toggleButton = document.getElementById('toggleFieldNamesBtn');
    
    if (!fieldNamesElements.length || !toggleButton) return;
    
    const isVisible = fieldNamesElements[0].style.display !== 'none';
    
    fieldNamesElements.forEach(element => {
        element.style.display = isVisible ? 'none' : 'block';
    });
    
    toggleButton.textContent = isVisible ? 'Show Field Names' : 'Hide Field Names';
    toggleButton.classList.toggle('btn-outline-secondary', isVisible);
    toggleButton.classList.toggle('btn-secondary', !isVisible);
}

function updateColumnGroupsSummary() {
    const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
    const summary = document.getElementById('selectionSummary');
    const count = document.getElementById('totalColumnsCount');
    
    if (summary) {
        summary.textContent = `${checkboxes.length} column groups selected`;
    }
    
    if (count) {
        // Count actual columns from the selected groups
        let totalColumns = 0;
        checkboxes.forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            if (label) {
                const columnText = label.querySelector('small');
                if (columnText) {
                    const match = columnText.textContent.match(/(\d+) columns/);
                    if (match) {
                        totalColumns += parseInt(match[1]);
                    }
                }
            }
        });
        count.textContent = `${totalColumns} total columns`;
    }
}

// Validation Functions
function validateAnalysisEditor() {
    const patientFile = document.getElementById('editorPatientFileSelect')?.value;
    const taxonomyFile = document.getElementById('editorTaxonomyFileSelect')?.value;
    const brackenFile = document.getElementById('editorBrackenTimePointSelect')?.value;
    
    const isValid = patientFile && taxonomyFile && brackenFile;
    
    // Enable/disable run analysis button based on validation
    const runButton = document.querySelector('button[onclick="runAnalysisFromEditor()"]');
    if (runButton) {
        runButton.disabled = !isValid;
    }
    
    return isValid;
}

function updateTimePointDescription() {
    const timePointSelect = document.getElementById('editorBrackenTimePointSelect');
    const selectedValue = timePointSelect?.value;
    const selectedOption = timePointSelect?.selectedOptions[0];
    
    if (selectedOption && selectedValue) {
        const suffix = selectedOption.getAttribute('data-suffix');
        const function_ = selectedOption.getAttribute('data-function');
        
        console.log('Selected time point:', {
            key: selectedValue,
            suffix: suffix,
            function: function_,
            description: selectedOption.textContent
        });
        
        // You can add UI feedback here if needed
        // For example, show additional info in a tooltip or info box
    }
}

// Reports Tab Functions
function loadReportsTab() {
    loadReportsList();
}

function loadReportsList() {
    // For now, show the "no reports" state
    // TODO: Implement actual reports loading from API
    const reportsContainer = document.getElementById('reportsContainer');
    if (reportsContainer) {
        const noReportsState = document.getElementById('noReportsState');
        const reportsList = document.getElementById('reportsList');
        
        if (noReportsState) {
            noReportsState.style.display = 'block';
        }
        if (reportsList) {
            reportsList.style.display = 'none';
        }
    }
}

function clearReportFilters() {
    const reportSearch = document.getElementById('reportSearch');
    const reportTypeFilter = document.getElementById('reportTypeFilter');
    const reportStatusFilter = document.getElementById('reportStatusFilter');
    
    if (reportSearch) reportSearch.value = '';
    if (reportTypeFilter) reportTypeFilter.value = 'all';
    if (reportStatusFilter) reportStatusFilter.value = 'all';
    
    // TODO: Re-filter reports
    console.log('Report filters cleared');
}

// Settings Tab Functions
function loadSettingsTab() {
    // TODO: Implement settings tab loading
    console.log('Loading settings tab');
}
