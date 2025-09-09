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
    
    let html = '';
    let groupIndex = 0;
    
    // columnGroups is now an ordered array from the backend
    columnGroups.forEach(group => {
        const groupId = `colGroup${groupIndex}`;
        const displayName = formatGroupName(group.name);
        const columnCount = group.columns.length;
        
        html += `
            <div class="col-md-6 mb-2">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${groupId}" checked onchange="updateColumnGroupsSummary()">
                    <label class="form-check-label" for="${groupId}">
                        <strong>${displayName}</strong>
                        <small class="text-muted d-block">${columnCount} columns</small>
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
                displayBrackenTimePoints(data.time_points);
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

function displayBrackenTimePoints(timePoints) {
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
        timePointSelect.appendChild(option);
    });
}

function formatTimePointName(timePointKey) {
    // Convert snake_case to Title Case
    return timePointKey
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
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
