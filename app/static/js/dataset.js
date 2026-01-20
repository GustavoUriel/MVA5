// Dataset page JavaScript functionality
// Global variables
let datasetId = null;

// Initialize dataset page
document.addEventListener("DOMContentLoaded", function () {
  // Extract dataset ID from URL
  const pathParts = window.location.pathname.split("/");
  datasetId = parseInt(pathParts[2]);

  if (datasetId) {
    initializeDatasetPage();
  }
});

function initializeDatasetPage() {
  // Load data based on current tab
  const pathParts = window.location.pathname.split("/");
  const currentTab = pathParts[3] || "files";

  switch (currentTab) {
    case "files":
      loadFilesTab();
      break;
    case "analysis":
      loadAnalysisTab();
      break;
    case "reports":
      loadReportsTab();
      break;
    case "settings":
      loadSettingsTab();
      break;
  }
}

// Files Tab Functions
function loadFilesTab() {
  loadDataStats();
  loadFilesTable();
  setupUploadHandlers();
  loadProgressIndicator();
}

// Upload functionality
function setupUploadHandlers() {
  // Add event listeners to all upload buttons
  const uploadButtons = document.querySelectorAll('.upload-btn');
  uploadButtons.forEach(button => {
    button.addEventListener('click', handleUpload);
  });
}

function handleUpload(event) {
  const button = event.target.closest('.upload-btn');
  const fileType = button.getAttribute('data-file-type');
  const uploadSection = button.closest('.upload-section');
  const fileInput = uploadSection.querySelector('input[type="file"]');
  
  if (!fileInput.files.length) {
    showToast('Please select a file to upload', 'warning');
    return;
  }
  
  const file = fileInput.files[0];
  
  // Validate file type
  const allowedExtensions = ['.csv', '.tsv', '.txt'];
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowedExtensions.includes(fileExtension)) {
    showToast('Please select a valid file (CSV, TSV, or TXT)', 'error');
    return;
  }
  
  // Show loading state
  button.disabled = true;
  button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
  
  // Create form data
  const formData = new FormData();
  formData.append('file', file);
  formData.append('file_type', fileType);
  
  // Upload file
  fetch(`/dataset/${datasetId}/upload`, {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      showToast(data.message, 'success');
      
      // Update status display
      updateUploadStatus(fileType, 'success', data.message);
      
      // Reload files table, data stats, and progress indicator
      loadFilesTable();
      loadDataStats();
      loadProgressIndicator();
      
      // Clear file input
      fileInput.value = '';
    } else {
      showToast(data.message, 'error');
      updateUploadStatus(fileType, 'error', data.message);
    }
  })
  .catch(error => {
    console.error('Upload error:', error);
    showToast('Upload failed. Please try again.', 'error');
    updateUploadStatus(fileType, 'error', 'Upload failed');
  })
  .finally(() => {
    // Reset button state
    button.disabled = false;
    button.innerHTML = `<i class="fas fa-upload me-2"></i>Upload ${fileType.charAt(0).toUpperCase() + fileType.slice(1)} Data`;
  });
}

function updateUploadStatus(fileType, status, message) {
  const statusElement = document.getElementById(`${fileType}-status`);
  if (!statusElement) return;
  
  let iconClass, textClass, text;
  
  switch(status) {
    case 'success':
      iconClass = 'fas fa-check-circle text-success';
      textClass = 'text-success';
      text = `<strong>${message}</strong>`;
      break;
    case 'error':
      iconClass = 'fas fa-exclamation-triangle text-danger';
      textClass = 'text-danger';
      text = `<strong>${message}</strong>`;
      break;
    case 'uploading':
      iconClass = 'fas fa-spinner fa-spin text-info';
      textClass = 'text-info';
      text = 'Uploading...';
      break;
    default:
      iconClass = 'fas fa-info-circle text-muted';
      textClass = 'text-muted';
      text = 'No actions yet';
  }
  
  statusElement.innerHTML = `
    <i class="${iconClass} me-2"></i>
    <span class="${textClass}">${text}</span>
  `;
}

function loadProgressIndicator() {
  // Fetch updated dataset status from the server
  fetch(`/dataset/${datasetId}/processing-status`)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        updateProgressIndicator(data.dataset_status);
      }
    })
    .catch(error => {
      console.error('Error loading progress indicator:', error);
    });
}

function updateProgressIndicator(datasetStatus) {
  // Update completion percentage badge
  const badges = document.querySelectorAll('.badge');
  let completionBadge = null;
  badges.forEach(badge => {
    if (badge.textContent.includes('Complete') || badge.textContent.includes('%')) {
      completionBadge = badge;
    }
  });
  
  if (completionBadge) {
    completionBadge.textContent = `${datasetStatus.completion_percentage}% Complete`;
    completionBadge.className = `badge bg-${datasetStatus.is_complete ? 'success' : 'warning'}`;
  }
  
  // Update progress bar
  const progressBar = document.querySelector('.progress-bar');
  if (progressBar) {
    progressBar.style.width = `${datasetStatus.completion_percentage}%`;
    progressBar.className = `progress-bar bg-${datasetStatus.is_complete ? 'success' : 'warning'}`;
  }
  
  // Update individual file type indicators
  updateFileTypeIndicator('patients', datasetStatus.patients_uploaded);
  updateFileTypeIndicator('taxonomy', datasetStatus.taxonomy_uploaded);
  updateFileTypeIndicator('bracken', datasetStatus.bracken_uploaded);
}

function updateFileTypeIndicator(fileType, isUploaded) {
  // Find the file type indicator by looking for the text content
  const indicators = document.querySelectorAll('.row.text-center .col-md-4');
  indicators.forEach(indicator => {
    const text = indicator.textContent.trim();
    if (text.includes('Patients Data') && fileType === 'patients') {
      updateIndicatorIcon(indicator, isUploaded);
    } else if (text.includes('Taxonomy Data') && fileType === 'taxonomy') {
      updateIndicatorIcon(indicator, isUploaded);
    } else if (text.includes('Bracken Results') && fileType === 'bracken') {
      updateIndicatorIcon(indicator, isUploaded);
    }
  });
}

function updateIndicatorIcon(container, isUploaded) {
  const icon = container.querySelector('i');
  const text = container.querySelector('span');
  
  if (icon && text) {
    if (isUploaded) {
      icon.className = 'fas fa-check-circle text-success me-2';
      text.className = 'text-success';
    } else {
      icon.className = 'fas fa-times-circle text-muted me-2';
      text.className = 'text-muted';
    }
  }
}

function loadDataStats() {
  const statsSection = document.getElementById("dataStatsSection");
  if (!statsSection) return;

  fetch(`/dataset/${datasetId}/data-stats`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayDataStats(data.stats);
      } else {
        showDataStatsError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading data stats:", error);
      showDataStatsError("Failed to load data statistics");
    });
}

function loadFilesTable() {
  const filesTable = document.getElementById("filesTable");
  if (!filesTable) return;

  fetch(`/dataset/${datasetId}/files/api`)
    .then((response) => response.json())
    .then((data) => {
      displayFilesTable(data.files, data.dataset_status);
    })
    .catch((error) => {
      console.error("Error loading files:", error);
      filesTable.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-2x text-danger mb-3"></i>
                    <p class="text-danger">Failed to load files</p>
                </div>
            `;
    });
}

function displayFilesTable(files, datasetStatus) {
  const filesTable = document.getElementById("filesTable");
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
                        <th>Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Cure Status</th>
                        <th>Uploaded</th>
                        <th>Modified</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;

  files.forEach((file) => {
    const sizeFormatted = formatFileSize(file.size);
    const cureStatusIcon = getCureStatusIcon(file.cure_status, file.cure_validation_status);
    const uploadedDate = new Date(file.uploaded_at).toLocaleDateString();
    const modifiedDate = new Date(file.modified_at).toLocaleDateString();

    html += `
            <tr>
                <td>
                    <i class="fas fa-file-csv me-2 text-primary"></i>
                    ${file.filename.replace(/\.csv$/i, "")}
                </td>
                <td>
                    <span class="badge bg-${getFileTypeColor(file.file_type)}">
                        ${file.file_type}
                    </span>
                </td>
                <td>${sizeFormatted}</td>
                <td>${cureStatusIcon}</td>
                <td>${uploadedDate}</td>
                <td>${modifiedDate}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info me-1" onclick="renameFile(${file.id}, '${
      file.filename
    }', '${file.file_type}')" title="Rename File">
                        <i class="fas fa-i-cursor"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning me-1" onclick="editTable(${
                      file.id
                    })" title="Edit Table">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success me-1" onclick="duplicateFile(${
                      file.id
                    })" title="Duplicate File">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="downloadFile(${
                      file.id
                    })" title="Download File">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm ${
                      file.cure_status === "cured" && file.cure_validation_status === "ok"
                        ? "btn-success disabled"
                        : "btn-outline-secondary"
                    }" 
                            onclick="cureData(${file.id})" 
                            ${file.cure_status === "cured" && file.cure_validation_status === "ok" ? "disabled" : ""} 
                            title="Cure Data">
                        <i class="fas fa-magic"></i> Cure
                    </button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="deleteFile(${
                      file.id
                    })" title="Delete File">
                        <i class="fas fa-trash"></i>
                    </button>
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
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function getFileTypeColor(fileType) {
  const colors = {
    patients: "primary",
    taxonomy: "info",
    bracken: "success",
    undefined: "secondary",
  };
  return colors[fileType] || "secondary";
}

function getStatusBadge(cureStatus, validationStatus) {
  if (validationStatus === "validated") {
    return '<span class="badge bg-success">Validated</span>';
  } else if (validationStatus === "failed") {
    return '<span class="badge bg-danger">Failed</span>';
  } else if (cureStatus === "cured") {
    return '<span class="badge bg-warning">Cured</span>';
  } else {
    return '<span class="badge bg-secondary">Pending</span>';
  }
}

function getCureStatusIcon(cureStatus, validationStatus) {
  if (cureStatus === "cured") {
    if (validationStatus === "ok") {
      return '<i class="fas fa-check-circle text-success" title="Cured and validation OK"></i>';
    } else if (validationStatus === "warnings") {
      return '<i class="fas fa-exclamation-triangle text-warning" title="Cured with warnings"></i>';
    } else if (validationStatus === "errors") {
      return '<i class="fas fa-times-circle text-danger" title="Cured with errors"></i>';
    }
  } else if (cureStatus === "curing") {
    return '<i class="fas fa-spinner fa-spin text-info" title="Curing in progress"></i>';
  } else if (cureStatus === "failed") {
    return '<i class="fas fa-times-circle text-danger" title="Cure failed"></i>';
  } else {
    return '<i class="fas fa-clock text-muted" title="Not yet cured"></i>';
  }
}

// Data Stats Functions
function displayDataStats(stats) {
  const statsSection = document.getElementById("dataStatsSection");
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

  html += "</div>";
  statsSection.innerHTML = html;
}

function showDataStatsError(error) {
  const statsSection = document.getElementById("dataStatsSection");
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
  console.log("View file:", fileId);
}

function deleteFile(fileId) {
  if (confirm("Are you sure you want to delete this file?")) {
    // Send delete request
    fetch(`/dataset/${datasetId}/file/${fileId}/delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        
        // Reload files table, data stats, and progress indicator
        loadFilesTable();
        loadDataStats();
        loadProgressIndicator();
      } else {
        showToast(data.message, 'error');
      }
    })
    .catch(error => {
      console.error('Delete file error:', error);
      showToast('Error deleting file. Please try again.', 'error');
    });
  }
}

// Tab Navigation
function goToTab(tabName) {
  window.location.href = `/dataset/${datasetId}/${tabName}`;
}

// Analysis Tab Functions
function loadAnalysisTab() {
  // Create DatasetAnalysisManager if it doesn't exist
  if (!window.analysisManager) {
    window.analysisManager = new DatasetAnalysisManager(datasetId);
    window.analysisManager.init();
  }
  setupAnalysisEditor();
}

function loadAnalysisList() {
  // For now, show the "no analyses" state
  // TODO: Implement actual analysis loading from API
  const analysisListContainer = document.getElementById("analysisListContainer");
  if (analysisListContainer) {
    const noAnalysesState = document.getElementById("noAnalysesState");
    const analysisTable = document.getElementById("analysisTable");

    if (noAnalysesState) {
      noAnalysesState.style.display = "block";
    }
    if (analysisTable) {
      analysisTable.style.display = "none";
    }
  }
}

function createNewAnalysis() {
  console.log("Creating new analysis...");

  // Hide the analysis list and show the editor
  const analysisListContainer = document.getElementById("analysisListContainer");
  const analysisEditorSection = document.getElementById("analysisEditorSection");

  if (analysisListContainer) {
    analysisListContainer.style.display = "none";
  }

  if (analysisEditorSection) {
    analysisEditorSection.style.display = "block";

    // Reset the editor form
    resetAnalysisEditor();

    // Load files for data source dropdowns
    loadFilesForDataSources();

    // Load column groups
    loadColumnGroups();

    // Load bracken time points - skip if analysis manager is active
    if (!window.analysisManager) {
      loadBrackenTimePoints();
    }

    // Load stratifications
    loadStratifications();
  }
}

function refreshAnalysisList() {
  console.log("Refreshing analysis list...");
  loadAnalysisList();
}

function cancelAnalysisEdit() {
  console.log("Canceling analysis edit...");

  // Hide the editor and show the analysis list
  const analysisListContainer = document.getElementById("analysisListContainer");
  const analysisEditorSection = document.getElementById("analysisEditorSection");

  if (analysisListContainer) {
    analysisListContainer.style.display = "block";
  }

  if (analysisEditorSection) {
    analysisEditorSection.style.display = "none";
  }
  // Refresh the existing analyses list
  try {
    if (window.analysisManager && typeof window.analysisManager.loadAnalysisList === 'function') {
      window.analysisManager.loadAnalysisList();
    } else if (typeof loadAnalysisList === 'function') {
      loadAnalysisList();
    }
  } catch (e) {
    console.error('Error refreshing analysis list after close:', e);
  }
}

function saveAnalysis() {
  console.log("Saving analysis...");

  const analysisName = document.getElementById("analysisName")?.value;
  const analysisDescription = document.getElementById("analysisDescription")?.value;

  if (!analysisName) {
    showAlert("Please enter an analysis name", "warning");
    return;
  }

  // Collect all form data from the three tabs
  const analysisConfig = collectAnalysisConfiguration();
  // Collect full controls state to persist all inputs (even empty/unchecked)
  try {
    analysisConfig.controls_state = collectAllControls();
  } catch (e) {}

  // Send to backend to save as JSON file
  fetch(`/dataset/${datasetId}/analysis/save`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      analysis_name: analysisName,
      analysis_description: analysisDescription,
      configuration: analysisConfig,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`Analysis "${analysisName}" saved successfully!`, "success");
      } else {
        showAlert(data.error || "Failed to save analysis", "danger");
      }
    })
    .catch((error) => {
      console.error("Error saving analysis:", error);
      showAlert("Failed to save analysis", "danger");
    });
}

function collectAnalysisConfiguration() {
  const config = {
    data_sources: {},
    analysis_config: {},
    report_config: {},
  };

  // Data Sources Tab
  config.data_sources = {
    patient_file: document.getElementById("editorPatientFileSelect")?.value || "",
    taxonomy_file: document.getElementById("editorTaxonomyFileSelect")?.value || "",
    bracken_file: document.getElementById("editorBrackenFileSelect")?.value || "",
    selection_mode: document.getElementById("selectionModeToggle")?.checked || false,
    top_percentage: document.getElementById("topPercentage")?.value || "",
    bottom_percentage: document.getElementById("bottomPercentage")?.value || "",
    // Patient Data Column Groups
    column_groups: collectColumnGroups(),
    // Bracken Time Point Selection
    bracken_time_point: document.getElementById("editorBrackenTimePointSelect")?.value || "",
    // Population Stratification
    population_stratifications: collectPopulationStratifications(),
  };

  // Analysis Config Tab
  config.analysis_config = {
    clustering_method: document.getElementById("clusteringMethodSelect")?.value || "",
    clustering_parameters: collectClusteringParameters(),
    cluster_representative: document.getElementById("clusterRepresentativeSelect")?.value || "",
    cluster_representative_parameters: collectClusterRepresentativeParameters(),
    analysis_methods: collectAnalysisMethods(),
    stratification_methods: collectStratificationMethods(),
    // Cluster Representative Selection
    cluster_representative_method: document.getElementById("clusterRepresentativeMethod")?.value || "",
    cluster_representative_details: collectClusterRepresentativeDetails(),
    // Analysis Type
    analysis_type_method: document.getElementById("analysisMethodSelect")?.value || "",
    analysis_type_parameters: collectAnalysisTypeParameters(),
  };

  // Report Config Tab
  config.report_config = {
    report_formats: {
      pdf: document.getElementById("reportPDF")?.checked || false,
      html: document.getElementById("reportHTML")?.checked || false,
      csv: document.getElementById("reportCSV")?.checked || false,
    },
    report_content: {
      summary: document.getElementById("includeSummary")?.checked || false,
      plots: document.getElementById("includePlots")?.checked || false,
      raw_data: document.getElementById("includeRawData")?.checked || false,
    },
  };

  return config;
}

function collectClusteringParameters() {
  const parameters = {};
  const container = document.getElementById("clusteringParametersForm");
  if (container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach((input) => {
      if (input.id && input.value !== "") {
        parameters[input.id] = input.type === "checkbox" ? input.checked : input.value;
      }
    });
  }
  return parameters;
}

function collectClusterRepresentativeParameters() {
  const parameters = {};
  const container = document.getElementById("clusterRepresentativeParametersForm");
  if (container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach((input) => {
      if (input.id && input.value !== "") {
        parameters[input.id] = input.type === "checkbox" ? input.checked : input.value;
      }
    });
  }
  return parameters;
}

function collectAnalysisMethods() {
  const methods = [];
  const container = document.getElementById("analysisMethodsContainer");
  if (container) {
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach((checkbox) => {
      methods.push(checkbox.value);
    });
  }
  return methods;
}

function collectStratificationMethods() {
  const methods = [];
  const container = document.getElementById("stratificationMethodsContainer");
  if (container) {
    const checkboxes = container.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach((checkbox) => {
      methods.push(checkbox.value);
    });
  }
  return methods;
}

function collectColumnGroups() {
  const columnGroups = [];
  const container = document.getElementById("columnGroupsContainer");
  if (container) {
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      columnGroups.push({
        group_name: checkbox.value,
        group_id: checkbox.id,
        is_checked: checkbox.checked,
      });
    });
  }
  return columnGroups;
}

function collectPopulationStratifications() {
  const stratifications = [];
  const container = document.getElementById("stratificationContainer");
  if (container) {
    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      stratifications.push({
        stratification_name: checkbox.value,
        stratification_id: checkbox.id,
        is_checked: checkbox.checked,
      });
    });
  }
  return stratifications;
}

function collectClusterRepresentativeDetails() {
  const details = {};
  const container = document.getElementById("clusterRepresentativeDetails");
  if (container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach((input) => {
      if (input.id && input.value !== "") {
        details[input.id] = input.type === "checkbox" ? input.checked : input.value;
      }
    });
  }
  return details;
}

function collectAnalysisTypeParameters() {
  const parameters = {};
  const container = document.getElementById("analysisMethodParametersForm");
  if (container) {
    const inputs = container.querySelectorAll("input, select, textarea");
    inputs.forEach((input) => {
      if (input.id && input.value !== "") {
        parameters[input.id] = input.type === "checkbox" ? input.checked : input.value;
      }
    });
  }
  return parameters;
}

// Collect states of all form controls inside the analysis editor (values, checked, options, visibility)
function collectAllControls() {
  const root = document.getElementById('analysisEditorSection');
  if (!root) return {};

  const controls = {};
  const elems = root.querySelectorAll('input, select, textarea, button');
  let anonIdx = 0;

  elems.forEach((el) => {
    const key = el.id || el.name || `elem_${anonIdx++}`;
    const info = { id: el.id || null, name: el.name || null, tag: el.tagName.toLowerCase() };
    try {
      if (el.tagName === 'INPUT') {
        const t = (el.type || '').toLowerCase();
        if (t === 'checkbox' || t === 'radio') {
          info.checked = !!el.checked;
          info.value = el.value !== undefined ? el.value : '';
        } else if (t === 'range' || t === 'number') {
          info.value = el.value !== undefined ? el.value : '';
        } else {
          info.value = el.value !== undefined ? el.value : '';
        }
      } else if (el.tagName === 'SELECT') {
        if (el.multiple) {
          info.selected_text = Array.from(el.selectedOptions).map(o => o.text);
        } else {
          const sel = el.selectedOptions[0];
          if (el.id === 'editorPatientFileSelect' || el.id === 'editorTaxonomyFileSelect' || el.id === 'editorBrackenFileSelect') {
            info.selected_text = sel ? sel.text : '';
            info.value = el.value || '';
          } else {
            info.selected_text = sel ? sel.text : '';
            info.value = el.value || '';
          }
        }
      } else if (el.tagName === 'TEXTAREA') {
        info.value = el.value !== undefined ? el.value : '';
      }
    } catch (e) {
      // ignore read-only properties
    }

    controls[key] = info;
  });

  return controls;
}

function runAnalysisFromEditor() {
  console.log("Running analysis from editor...");

  // Validate required fields
  const analysisName = document.getElementById("analysisName")?.value;
  if (!analysisName) {
    alert("Please enter an analysis name");
    return;
  }

  // TODO: Implement actual analysis execution
  console.log("Running analysis with current configuration");

  // For now, just show success message
  alert("Analysis started! Check the Reports tab for results.");
}

function resetAnalysisEditor() {
  // Reset form fields
  const analysisName = document.getElementById("analysisName");
  const analysisDescription = document.getElementById("analysisDescription");

  if (analysisName) analysisName.value = "";
  if (analysisDescription) analysisDescription.value = "";

  // Reset file selections
  const patientSelect = document.getElementById("editorPatientFileSelect");
  const taxonomySelect = document.getElementById("editorTaxonomyFileSelect");
  const brackenSelect = document.getElementById("editorBrackenFileSelect");

  if (patientSelect) patientSelect.value = "";
  if (taxonomySelect) taxonomySelect.value = "";
  if (brackenSelect) brackenSelect.value = "";

  // Reset analysis type to default
  const alphaDivRadio = document.getElementById("editorAlphaDiv");
  if (alphaDivRadio) alphaDivRadio.checked = true;
}

function loadFilesForDataSources() {
  // Load files for the data source dropdowns
  fetch(`/dataset/${datasetId}/files/api`)
    .then((response) => response.json())
    .then((data) => {
      populateFileDropdowns(data.files);
    })
    .catch((error) => {
      console.error("Error loading files for data sources:", error);
    });
}

function populateFileDropdowns(files) {
  const patientSelect = document.getElementById("editorPatientFileSelect");
  const taxonomySelect = document.getElementById("editorTaxonomyFileSelect");
  const brackenSelect = document.getElementById("editorBrackenFileSelect");

  // Clear existing options (except the first one)
  [patientSelect, taxonomySelect, brackenSelect].forEach((select) => {
    if (select) {
      while (select.children.length > 1) {
        select.removeChild(select.lastChild);
      }
    }
  });

  // Populate dropdowns based on file type
  files.forEach((file) => {
    const option = document.createElement("option");
    option.value = file.id;
    option.textContent = `${file.filename} (${formatFileSize(file.size)})`;

    switch (file.file_type) {
      case "patients":
        if (patientSelect) patientSelect.appendChild(option.cloneNode(true));
        break;
      case "taxonomy":
        if (taxonomySelect) taxonomySelect.appendChild(option.cloneNode(true));
        break;
      case "bracken":
        if (brackenSelect) brackenSelect.appendChild(option.cloneNode(true));
        break;
    }
  });
}

function loadColumnGroups() {
  console.log("Loading column groups from metadata...");

  fetch(`/dataset/${datasetId}/metadata/column-groups`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayColumnGroups(data.column_groups);
      } else {
        console.error("Error loading column groups:", data.error);
        showColumnGroupsError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading column groups:", error);
      showColumnGroupsError("Failed to load column groups");
    });
}

function displayColumnGroups(columnGroups) {
  const columnGroupsContainer = document.getElementById("columnGroupsContainer");
  if (!columnGroupsContainer) return;

  // Store the original column groups data for toggling
  window.columnGroupsData = columnGroups;

  let html = "";
  let groupIndex = 0;
  const usedIds = new Set();

  // columnGroups is now an ordered array from the backend
  columnGroups.forEach((group) => {
    const displayName = formatGroupName(group.name);
    // Use the first line of the label (without spaces) as id/name
    let baseId = (displayName || '').split('\n')[0].replace(/\s+/g, '');
    if (!baseId) baseId = `colGroup${groupIndex}`;
    let groupId = baseId;
    let uniqCounter = 1;
    // Ensure the id is unique within this render
    while (usedIds.has(groupId) || document.getElementById(groupId)) {
      groupId = `${baseId}_${uniqCounter}`;
      uniqCounter++;
    }
    usedIds.add(groupId);
    const columnCount = group.columns.length;

    // Create a list of field names, sorted as they appear in the metadata file
    const fieldNames = group.columns
      .map((field) => `<span class="badge bg-light text-dark me-1 mb-1">${field}</span>`)
      .join("");

    html += `
            <div class="col-md-6 mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${groupId}" name="${groupId}" checked onchange="updateColumnGroupsSummary()">
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
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function showColumnGroupsError(error) {
  const columnGroupsContainer = document.getElementById("columnGroupsContainer");
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
  console.log("Loading bracken time points from metadata...");

  fetch(`/dataset/${datasetId}/metadata/bracken-time-points`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayBrackenTimePoints(data.time_points, data.default_time_point);
      } else {
        console.error("Error loading bracken time points:", data.error);
        showBrackenTimePointsError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading bracken time points:", error);
      showBrackenTimePointsError("Failed to load bracken time points");
    });
}

function loadStratifications() {
  console.log("Loading stratifications from metadata...");

  fetch(`/dataset/${datasetId}/metadata/stratifications`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayStratifications(data.stratifications);
      } else {
        console.error("Error loading stratifications:", data.error);
        showStratificationsError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading stratifications:", error);
      showStratificationsError("Failed to load stratifications");
    });
}

function displayBrackenTimePoints(timePoints, defaultTimePoint = null) {
  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  if (!timePointSelect) return;

  // Store descriptions globally for later access
  window.brackenTimePointDescriptions = {};

  // Clear existing options (except the first one)
  while (timePointSelect.children.length > 1) {
    timePointSelect.removeChild(timePointSelect.lastChild);
  }

  // timePoints is now an ordered array from the backend
  timePoints.forEach((timePoint) => {
    const option = document.createElement("option");
    option.value = timePoint.key;
    option.textContent = timePoint.title; // Use title from metadata instead of formatted key
    option.setAttribute("data-description", timePoint.description);
    option.setAttribute("data-suffix", timePoint.suffix);
    option.setAttribute("data-function", timePoint.function);

    // Store description for later access
    window.brackenTimePointDescriptions[timePoint.key] = timePoint.description;

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
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function displayStratifications(stratifications) {
  const stratificationContainer = document.getElementById("stratificationContainer");
  if (!stratificationContainer) return;

  let html = "";
  let index = 0;
  // Accepts flat dictionary format from backend
  Object.entries(stratifications).forEach(([key, stratification]) => {
    const stratId = `strat_${index}_${key}`;
    
    let groupInfoHtml = '';
    if (Array.isArray(stratification.group_info)) {
      groupInfoHtml = `<ul class="mb-0 ps-3">${stratification.group_info.map(item => `<li>${item.replace(/^• /, '')}</li>`).join('')}</ul>`;
    } else if (stratification.group_info) {
      groupInfoHtml = `<span class="text-info" style="font-size:0.95em;">${stratification.group_info}</span>`;
    }
    let subgroupsHtml = '';
    if (Array.isArray(stratification.subgroups) && stratification.subgroups.length > 0) {
      subgroupsHtml = `<div class="mt-2"><strong>Subgroups:</strong><ul class="mb-0 ps-3">${stratification.subgroups.map(sg => `<li><strong>${sg.name}:</strong> <span class='text-muted'>${sg.condition}</span></li>`).join('')}</ul></div>`;
    }
    html += `
      <div class="col-md-6 col-lg-4 mb-3">
        <div class="card">
          <div class="card-body">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="${stratId}" onchange="(window.analysisManager && window.analysisManager.updateStratificationSummary) ? window.analysisManager.updateStratificationSummary() : updateStratificationSummary()">
              <label class="form-check-label" for="${stratId}">
                <strong>${stratification.name}</strong>
                <small class="text-muted d-block">${stratification.description || ''}</small>
              </label>
            </div>
            <div class="mt-2">${groupInfoHtml}</div>
            ${subgroupsHtml}
          </div>
        </div>
      </div>
    `;
    index++;
  });
  stratificationContainer.innerHTML = `<div class="row">${html}</div>`;

  // Ensure all stratification checkboxes are unchecked by default on load
  try {
    const boxes = stratificationContainer.querySelectorAll('input[type="checkbox"]');
    boxes.forEach((cb) => {
      cb.checked = false;
    });
  } catch (e) {
    console.warn('Unable to reset stratification checkboxes to unchecked by default', e);
  }

  // Update summary using analysisManager if available, otherwise fallback
  if (window.analysisManager && typeof window.analysisManager.updateStratificationSummary === 'function') {
    window.analysisManager.updateStratificationSummary();
  } else if (typeof updateStratificationSummary === 'function') {
    updateStratificationSummary();
  }
}

function toggleStratification() {
  const stratificationContainer = document.getElementById("stratificationContainer");
  const toggleButton = document.getElementById("toggleStratificationBtn");

  if (!stratificationContainer || !toggleButton) return;

  const isVisible = stratificationContainer.style.display !== "none";

  stratificationContainer.style.display = isVisible ? "none" : "block";
  toggleButton.textContent = isVisible ? "Show Stratification Options" : "Hide Stratification Options";
  toggleButton.classList.toggle("btn-outline-secondary", isVisible);
  toggleButton.classList.toggle("btn-secondary", !isVisible);

  // Keep stratification summary always visible - don't hide it
  // const summary = document.getElementById('stratificationSummary');
  // if (summary) {
  //     summary.style.display = isVisible ? 'none' : 'block';
  // }
}

function selectAllStratifications() {
  const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = true;
  });
  if (window.analysisManager && typeof window.analysisManager.updateStratificationSummary === 'function') {
    window.analysisManager.updateStratificationSummary();
  } else if (typeof updateStratificationSummary === 'function') {
    updateStratificationSummary();
  }
}

function clearAllStratifications() {
  const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (window.analysisManager && typeof window.analysisManager.updateStratificationSummary === 'function') {
    window.analysisManager.updateStratificationSummary();
  } else if (typeof updateStratificationSummary === 'function') {
    updateStratificationSummary();
  }
}

function updateStratificationSummary() {
  const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]:checked');
  const summary = document.getElementById("stratificationSummaryText");
  const count = document.getElementById("stratificationCount");

  if (summary) {
    summary.textContent = `${checkboxes.length} stratification${checkboxes.length !== 1 ? "s" : ""} selected`;
  }

  if (count) {
    count.textContent = `${checkboxes.length} stratification${checkboxes.length !== 1 ? "s" : ""}`;
  }
}

function showStratificationsError(error) {
  const stratificationContainer = document.getElementById("stratificationContainer");
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
  console.log("Loading clustering methods from metadata...");

  fetch(`/dataset/${datasetId}/metadata/clustering-methods`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayClusteringMethods(data.methods, data.default_method);
      } else {
        console.error("Error loading clustering methods:", data.error);
        showClusteringError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading clustering methods:", error);
      showClusteringError("Failed to load clustering methods");
    });
}

function displayClusteringMethods(clusteringMethods, defaultMethod = null) {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  if (!methodSelect) return;

  // Clear existing options (except the first one)
  while (methodSelect.children.length > 1) {
    methodSelect.removeChild(methodSelect.lastChild);
  }

  // Add clustering method options
  Object.entries(clusteringMethods).forEach(([key, method]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = method.name;
    option.setAttribute("data-description", method.description);

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
    const parametersContainer = document.getElementById("clusteringParametersContainer");
    if (parametersContainer) {
      parametersContainer.style.display = "none";
    }
  }
}

function updateClusteringParameters() {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  const parametersContainer = document.getElementById("clusteringParametersContainer");
  const parametersForm = document.getElementById("clusteringParametersForm");
  const methodDescription = document.getElementById("clusteringMethodDescription");
  const methodStatus = document.getElementById("clusteringMethodStatus");
  const clusteringSummary = document.getElementById("clusteringSummary");

  if (!methodSelect || !parametersContainer || !parametersForm) return;

  const selectedMethod = methodSelect.value;

  if (!selectedMethod) {
    // Hide parameters and reset UI
    parametersContainer.style.display = "none";
    clusteringSummary.style.display = "none";
    if (methodDescription) methodDescription.textContent = "Choose a clustering algorithm for variable grouping";
    if (methodStatus) {
      methodStatus.textContent = "No method selected";
      methodStatus.className = "badge bg-secondary me-2";
    }
    return;
  }

  // Update method description and status
  const selectedOption = methodSelect.options[methodSelect.selectedIndex];
  const description = selectedOption.getAttribute("data-description") || "Clustering method selected";

  if (methodDescription) methodDescription.textContent = description;
  if (methodStatus) {
    methodStatus.textContent = "Method configured";
    methodStatus.className = "badge bg-success me-2";
  }

  // Load method parameters
  fetch(`/dataset/${datasetId}/metadata/clustering-methods/${selectedMethod}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayClusteringParameters(data.method);
        // Don't automatically show parameters container - keep it hidden
        // parametersContainer.style.display = 'block';
        clusteringSummary.style.display = "block";
        updateClusteringSummary();
      } else {
        console.error("Error loading method parameters:", data.error);
        showClusteringError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading method parameters:", error);
      showClusteringError("Failed to load method parameters");
    });
}

function displayClusteringParameters(method) {
  const parametersForm = document.getElementById("clusteringParametersForm");
  if (!parametersForm || !method.parameters) return;

  let html = '<div class="row">';

  Object.entries(method.parameters).forEach(([paramKey, paramConfig]) => {
    const paramId = `clustering_param_${paramKey}`;
    const colClass = Object.keys(method.parameters).length > 2 ? "col-md-6" : "col-md-4";

    html += `
            <div class="${colClass} mb-3">
                <label for="${paramId}" class="form-label">
                    <i class="fas fa-cog text-primary me-2"></i>
                    ${paramConfig.name}
                </label>
        `;

    if (paramConfig.type === "select") {
      html += `
                <select class="form-select" id="${paramId}" onchange="updateClusteringSummary()">
                    <option value="">Select ${paramConfig.name.toLowerCase()}...</option>
            `;
      paramConfig.options.forEach((option) => {
        const isDefault = option === paramConfig.default;
        const isBest = option === paramConfig.best_component;
        const selected = isDefault ? "selected" : "";
        const badge = isBest ? " (Best)" : "";
        html += `<option value="${option}" ${selected}>${option}${badge}</option>`;
      });
      html += "</select>";
    } else if (paramConfig.type === "number") {
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
                    ${
                      paramConfig.best_component && paramConfig.best_component !== "auto"
                        ? `<br><small class="text-success"><i class="fas fa-star me-1"></i>Best: ${paramConfig.best_component}</small>`
                        : ""
                    }
                </div>
            </div>
        `;
  });

  html += "</div>";
  parametersForm.innerHTML = html;
}

function toggleClustering() {
  const parametersContainer = document.getElementById("clusteringParametersContainer");
  const toggleButton = document.getElementById("toggleClusteringBtn");

  if (!parametersContainer || !toggleButton) return;

  const isVisible = parametersContainer.style.display !== "none";

  parametersContainer.style.display = isVisible ? "none" : "block";
  toggleButton.innerHTML = isVisible
    ? '<i class="fas fa-eye me-1"></i>Show Clustering Options'
    : '<i class="fas fa-eye-slash me-1"></i>Hide Clustering Options';
  toggleButton.classList.toggle("btn-outline-secondary", isVisible);
  toggleButton.classList.toggle("btn-secondary", !isVisible);
}

function resetClusteringToDefaults() {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  if (!methodSelect || !methodSelect.value) return;

  // Reset all parameter inputs to their default values
  const parameterInputs = document.querySelectorAll(
    "#clusteringParametersForm input, #clusteringParametersForm select"
  );
  parameterInputs.forEach((input) => {
    if (input.type === "number") {
      // Find the default value from the method configuration
      const paramKey = input.id.replace("clustering_param_", "");
      // This would need to be enhanced to get the actual default value
      // For now, we'll just reset to the current value
    } else if (input.tagName === "SELECT") {
      // Reset to first non-empty option
      const firstOption = Array.from(input.options).find((opt) => opt.value !== "");
      if (firstOption) input.value = firstOption.value;
    }
  });

  updateClusteringSummary();
  showToast("Clustering parameters reset to defaults", "success");
}

function applyBestComponents() {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  if (!methodSelect || !methodSelect.value) return;

  // Apply best component values to all parameters
  const parameterInputs = document.querySelectorAll(
    "#clusteringParametersForm input, #clusteringParametersForm select"
  );
  parameterInputs.forEach((input) => {
    if (input.tagName === "SELECT") {
      // Find option with "Best" in the text
      const bestOption = Array.from(input.options).find((opt) => opt.textContent.includes("Best"));
      if (bestOption) input.value = bestOption.value;
    }
  });

  updateClusteringSummary();
  showToast("Best component values applied", "success");
}

function updateClusteringSummary() {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  const summaryText = document.getElementById("clusteringSummaryText");
  const parametersCount = document.getElementById("clusteringParametersCount");
  const clusteringSummary = document.getElementById("clusteringSummary");

  if (!methodSelect || !summaryText || !parametersCount) return;

  const selectedMethod = methodSelect.value;
  if (!selectedMethod) {
    clusteringSummary.style.display = "none";
    return;
  }

  const selectedOption = methodSelect.options[methodSelect.selectedIndex];
  const methodName = selectedOption.textContent;

  // Count configured parameters
  const parameterInputs = document.querySelectorAll(
    "#clusteringParametersForm input, #clusteringParametersForm select"
  );
  const configuredParams = Array.from(parameterInputs).filter(
    (input) => input.value && input.value.trim() !== ""
  ).length;

  summaryText.textContent = `${methodName} configured with ${configuredParams} parameters`;
  parametersCount.textContent = `${configuredParams} parameters`;
  clusteringSummary.style.display = "block";
}

function showClusteringInfo() {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  if (!methodSelect || !methodSelect.value) {
    showToast("Please select a clustering method first", "warning");
    return;
  }

  const selectedOption = methodSelect.options[methodSelect.selectedIndex];
  const methodName = selectedOption.textContent;
  const description = selectedOption.getAttribute("data-description") || "No description available";

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
  const existingModal = document.getElementById("clusteringInfoModal");
  if (existingModal) existingModal.remove();

  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  // Load parameter details
  fetch(`/dataset/${datasetId}/metadata/clustering-methods/${methodSelect.value}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.method.parameters) {
        const parametersList = document.getElementById("clusteringParametersList");
        if (parametersList) {
          parametersList.innerHTML = Object.entries(data.method.parameters)
            .map(
              ([key, param]) => `
                            <li>
                                <strong>${param.name}:</strong> ${param.description}
                                ${
                                  param.best_component && param.best_component !== "auto"
                                    ? `<br><small class="text-success">Best value: ${param.best_component}</small>`
                                    : ""
                                }
                            </li>
                        `
            )
            .join("");
        }
      }
    })
    .catch((error) => console.error("Error loading parameter details:", error));

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("clusteringInfoModal"));
  modal.show();

  // Remove modal from DOM when hidden and fix focus
  document.getElementById("clusteringInfoModal").addEventListener("hidden.bs.modal", function () {
    // Remove focus from any focused elements before removing modal
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    this.remove();
  });
}

function showClusteringError(error) {
  const parametersForm = document.getElementById("clusteringParametersForm");
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
  console.log("Loading cluster representative methods from metadata...");

  fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayClusterRepresentativeMethods(data.cluster_representative_methods, data.default_method);
      } else {
        console.error("Error loading cluster representative methods:", data.error);
        showClusterRepresentativeError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading cluster representative methods:", error);
      showClusterRepresentativeError("Failed to load cluster representative methods");
    });
}

function displayClusterRepresentativeMethods(clusterRepMethods, defaultMethod = null) {
  const methodSelect = document.getElementById("clusterRepresentativeMethod");
  if (!methodSelect) return;

  // Clear existing options (except the first one)
  while (methodSelect.children.length > 1) {
    methodSelect.removeChild(methodSelect.lastChild);
  }

  // Add methods to dropdown
  Object.entries(clusterRepMethods).forEach(([methodKey, methodConfig]) => {
    const option = document.createElement("option");
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
  const methodSelect = document.getElementById("clusterRepresentativeMethod");
  const methodStatus = document.getElementById("clusterRepMethodStatus");
  const container = document.getElementById("clusterRepresentativeContainer");
  const summary = document.getElementById("clusterRepSummary");

  if (!methodSelect || !methodStatus || !container || !summary) return;

  const selectedMethod = methodSelect.value;

  if (!selectedMethod) {
    methodStatus.textContent = "No method selected";
    methodStatus.className = "badge bg-secondary me-2";
    container.style.display = "none";
    summary.style.display = "none";
    return;
  }

  // Update status
  methodStatus.textContent = "Method selected";
  methodStatus.className = "badge bg-success me-2";

  // Load method details
  fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods/${selectedMethod}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayClusterRepresentativeDetails(data.method);
        summary.style.display = "block";
        updateClusterRepresentativeSummary();
      } else {
        console.error("Error loading method details:", data.error);
        showClusterRepresentativeError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading method details:", error);
      showClusterRepresentativeError("Failed to load method details");
    });
}

function displayClusterRepresentativeDetails(method) {
  const detailsContainer = document.getElementById("clusterRepresentativeDetails");
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
  const container = document.getElementById("clusterRepresentativeContainer");
  const button = document.getElementById("toggleClusterRepBtn");

  if (!container || !button) return;

  const isVisible = container.style.display !== "none";

  if (isVisible) {
    container.style.display = "none";
    button.innerHTML = '<i class="fas fa-eye me-1"></i>Show Options';
    button.className = "btn btn-outline-secondary";
  } else {
    container.style.display = "block";
    button.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Hide Options';
    button.className = "btn btn-outline-secondary";
  }
}

function resetClusterRepresentativeToDefault() {
  const methodSelect = document.getElementById("clusterRepresentativeMethod");
  if (!methodSelect) return;

  // Reset to default method (abundance_highest)
  methodSelect.value = "abundance_highest";
  updateClusterRepresentativeMethod();

  showToast("Cluster representative method reset to default (Highest Mean Abundance)", "success");
}

function updateClusterRepresentativeSummary() {
  const methodSelect = document.getElementById("clusterRepresentativeMethod");
  const summaryText = document.getElementById("clusterRepSummaryText");
  const methodName = document.getElementById("clusterRepMethodName");

  if (!methodSelect || !summaryText || !methodName) return;

  const selectedMethod = methodSelect.value;
  const selectedOption = methodSelect.options[methodSelect.selectedIndex];

  if (selectedMethod && selectedOption) {
    summaryText.textContent = `Using "${selectedOption.textContent}" method for cluster representative selection`;
    methodName.textContent = selectedOption.textContent;
  } else {
    summaryText.textContent = "No representative method configured";
    methodName.textContent = "No method";
  }
}

function showClusterRepresentativeInfo() {
  const methodSelect = document.getElementById("clusterRepresentativeMethod");
  if (!methodSelect || !methodSelect.value) {
    showToast("Please select a cluster representative method first", "warning");
    return;
  }

  const selectedMethod = methodSelect.value;

  // Load method details for info modal
  fetch(`/dataset/${datasetId}/metadata/cluster-representative-methods/${selectedMethod}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Create and show info modal
        showClusterRepresentativeInfoModal(data.method);
      } else {
        console.error("Error loading method details:", data.error);
        showToast("Error loading method information", "error");
      }
    })
    .catch((error) => {
      console.error("Error loading method details:", error);
      showToast("Error loading method information", "error");
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
  const existingModal = document.getElementById("clusterRepInfoModal");
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("clusterRepInfoModal"));
  modal.show();

  // Remove modal from DOM when hidden and fix focus
  document.getElementById("clusterRepInfoModal").addEventListener("hidden.bs.modal", function () {
    // Remove focus from any focused elements before removing modal
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    this.remove();
  });
}

function showClusterRepresentativeError(error) {
  const detailsContainer = document.getElementById("clusterRepresentativeDetails");
  if (!detailsContainer) return;

  detailsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${error}
        </div>
    `;
}

function showToast(message, type = "info") {
  // Create toast element
  const toastId = "toast_" + Date.now();
  const toastHtml = `
        <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${
                  type === "success"
                    ? "check-circle text-success"
                    : type === "error"
                    ? "exclamation-triangle text-danger"
                    : type === "warning"
                    ? "exclamation-triangle text-warning"
                    : "info-circle text-info"
                } me-2"></i>
                <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

  // Add toast to container (create if doesn't exist)
  let toastContainer = document.getElementById("toastContainer");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toastContainer";
    toastContainer.className = "toast-container position-fixed top-0 end-0 p-3";
    toastContainer.style.zIndex = "1055";
    document.body.appendChild(toastContainer);
  }

  toastContainer.insertAdjacentHTML("beforeend", toastHtml);

  // Show toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, {
    autohide: true,
    delay: type === "error" ? 5000 : 3000,
  });
  toast.show();

  // Remove toast element after it's hidden
  toastElement.addEventListener("hidden.bs.toast", () => {
    toastElement.remove();
  });
}

// Column Groups Toggle Functions
function toggleColumnGroups() {
  const columnGroupsContent = document.getElementById("columnGroupsContent");
  const columnGroupsSummary = document.getElementById("columnGroupsSummary");
  const toggleButton = document.getElementById("toggleColumnGroupsBtn");

  if (!columnGroupsContent || !toggleButton) return;

  const isVisible = columnGroupsContent.style.display !== "none";

  columnGroupsContent.style.display = isVisible ? "none" : "block";
  // Keep summary always visible - don't hide it
  // if (columnGroupsSummary) {
  //     columnGroupsSummary.style.display = isVisible ? 'none' : 'block';
  // }

  toggleButton.innerHTML = isVisible
    ? '<i class="fas fa-eye me-1"></i>Show Column Groups'
    : '<i class="fas fa-eye-slash me-1"></i>Hide Column Groups';
  toggleButton.classList.toggle("btn-outline-secondary", isVisible);
  toggleButton.classList.toggle("btn-secondary", !isVisible);
}

// Bracken Time Point Functions

function showBrackenTimePointInfo() {
  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  if (!timePointSelect) {
    showToast("Time point selector not found", "warning");
    return;
  }

  const selectedOption = timePointSelect.options[timePointSelect.selectedIndex];
  const selectedValue = timePointSelect.value;

  if (!selectedValue) {
    showToast("Please select a time point first", "warning");
    return;
  }

  const timePointName = selectedOption.textContent;
  const suffix = selectedOption.getAttribute("data-suffix") || "N/A";
  const functionType = selectedOption.getAttribute("data-function") || "N/A";

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
  const existingModal = document.getElementById("brackenTimePointInfoModal");
  if (existingModal) existingModal.remove();

  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("brackenTimePointInfoModal"));
  modal.show();

  // Remove modal from DOM when hidden and fix focus
  document.getElementById("brackenTimePointInfoModal").addEventListener("hidden.bs.modal", function () {
    // Remove focus from any focused elements before removing modal
    if (document.activeElement && document.activeElement.blur) {
      document.activeElement.blur();
    }
    this.remove();
  });
}

// This function conflicts with the analysis manager's updateTimePointDescription
// Renaming it to avoid conflicts
function updateTimePointDescriptionValidation() {
  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  const selectedValue = timePointSelect?.value;
  const selectedOption = timePointSelect?.selectedOptions[0];

  if (selectedOption && selectedValue) {
    const suffix = selectedOption.getAttribute("data-suffix");
    const function_ = selectedOption.getAttribute("data-function");

    console.log("Selected time point:", {
      key: selectedValue,
      suffix: suffix,
      function: function_,
      description: selectedOption.textContent,
    });

    // You can add UI feedback here if needed
    // For example, show additional info in a tooltip or info box
  }
}

// The correct global updateTimePointDescription function that should be called by onchange
function updateTimePointDescription() {
  // updateTimePointDescription called

  // First try the analysis manager (preferred)
  if (window.analysisManager && typeof window.analysisManager.updateTimePointDescription === 'function') {
    // using analysis manager method
    window.analysisManager.updateTimePointDescription();
    return;
  }

  // Fallback to standalone implementation
  // using fallback implementation

  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  const descriptionElement = document.getElementById("timePointDescriptionText");

  if (!timePointSelect) return;

  const selectedValue = timePointSelect.value;

  if (!selectedValue) {
    if (descriptionElement) descriptionElement.textContent = "Select a time point to see its description";
    return;
  }

  // Get description from stored descriptions
  const description = window.brackenTimePointDescriptions ? window.brackenTimePointDescriptions[selectedValue] : "";

  // Update description element with the actual description from metadata
  if (descriptionElement) {
    descriptionElement.textContent = description || "No description available";
  }
}

function showBrackenTimePointsError(error) {
  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  if (!timePointSelect) return;

  // Clear existing options (except the first one)
  while (timePointSelect.children.length > 1) {
    timePointSelect.removeChild(timePointSelect.lastChild);
  }

  // Add error option
  const errorOption = document.createElement("option");
  errorOption.value = "";
  errorOption.textContent = `Error loading time points: ${error}`;
  errorOption.disabled = true;
  timePointSelect.appendChild(errorOption);
}

function setupAnalysisEditor() {
  // Setup event listeners for the analysis editor
  console.log("Setting up analysis editor...");

  // Add event listeners for form validation
  const patientSelect = document.getElementById("editorPatientFileSelect");
  const taxonomySelect = document.getElementById("editorTaxonomyFileSelect");
  const brackenSelect = document.getElementById("editorBrackenFileSelect");

  if (patientSelect) {
    patientSelect.addEventListener("change", validateAnalysisEditor);
  }
  if (taxonomySelect) {
    taxonomySelect.addEventListener("change", validateAnalysisEditor);
  }
  if (brackenSelect) {
    brackenSelect.addEventListener("change", validateAnalysisEditor);
  }

  // Add event listener for analysis method select
  const analysisMethodSelect = document.getElementById('analysisMethodSelect');
  console.log('analysisMethodSelect found:', !!analysisMethodSelect);
  if (analysisMethodSelect) {
    analysisMethodSelect.addEventListener('change', () => {
      try {
        window.updateAnalysisMethod();
      } catch (e) {
        console.error('error calling updateAnalysisMethod', e);
      }
    });
  }

  // Load clustering methods for the clustering parameters container
  loadClusteringMethods();

  // Load cluster representative methods for the cluster representative container
  loadClusterRepresentativeMethods();

  // Load analysis methods for the analysis type container
  loadAnalysisMethods();
}

// Extreme Time Point Functions
function toggleSelectionMode() {
  const toggle = document.getElementById("selectionModeToggle");
  const modeLabel = document.getElementById("selectionModeLabel");
  const modeDescription = document.getElementById("selectionModeDescription");
  const topLabel = document.getElementById("topPercentageLabel");
  const bottomLabel = document.getElementById("bottomPercentageLabel");
  const topDescription = document.getElementById("topPercentageDescription");
  const bottomDescription = document.getElementById("bottomPercentageDescription");

  if (!toggle || !modeLabel) return;

  const isValueMode = toggle.checked;

  if (isValueMode) {
    // Value-based selection mode
    modeLabel.textContent = "Select by percentage of time variable value range";
    modeDescription.textContent =
      "When enabled: Select by percentage of time variable value range. When disabled: Select by percentage of patients.";

    if (topLabel) topLabel.textContent = "Top Value Range %";
    if (bottomLabel) bottomLabel.textContent = "Bottom Value Range %";
    if (topDescription) topDescription.textContent = "Percentage of time variable value range (highest values)";
    if (bottomDescription) bottomDescription.textContent = "Percentage of time variable value range (lowest values)";
  } else {
    // Patient-based selection mode
    modeLabel.textContent = "Select by percentage of patients";
    modeDescription.textContent =
      "When enabled: Select by percentage of time variable value range. When disabled: Select by percentage of patients.";

    if (topLabel) topLabel.textContent = "Top Percentage";
    if (bottomLabel) bottomLabel.textContent = "Bottom Percentage";
    if (topDescription) topDescription.textContent = "PPercentage of patients with highest time values";
    if (bottomDescription) bottomDescription.textContent = "Percentage of patients with lowest time values";
  }

  // Update summary to reflect the new mode
  updateExtremeTimePointSummary();
}

function updateTopPercentage(value) {
  const topPercentageValue = document.getElementById("topPercentageValue");
  const linkCheckbox = document.getElementById("linkPercentages");

  if (topPercentageValue) {
    topPercentageValue.textContent = value + "%";
  }

  // If linked, update bottom percentage to match
  if (linkCheckbox && linkCheckbox.checked) {
    const bottomPercentage = document.getElementById("bottomPercentage");
    const bottomPercentageValue = document.getElementById("bottomPercentageValue");
    if (bottomPercentage && bottomPercentageValue) {
      bottomPercentage.value = value;
      bottomPercentageValue.textContent = value + "%";
    }
  }

  updateExtremeTimePointSummary();
}

function updateBottomPercentage(value) {
  const bottomPercentageValue = document.getElementById("bottomPercentageValue");
  const linkCheckbox = document.getElementById("linkPercentages");

  if (bottomPercentageValue) {
    bottomPercentageValue.textContent = value + "%";
  }

  // If linked, update top percentage to match
  if (linkCheckbox && linkCheckbox.checked) {
    const topPercentage = document.getElementById("topPercentage");
    const topPercentageValue = document.getElementById("topPercentageValue");
    if (topPercentage && topPercentageValue) {
      topPercentage.value = value;
      topPercentageValue.textContent = value + "%";
    }
  }

  updateExtremeTimePointSummary();
}

function toggleLinkedPercentages() {
  const linkCheckbox = document.getElementById("linkPercentages");
  const topPercentage = document.getElementById("topPercentage");
  const bottomPercentage = document.getElementById("bottomPercentage");

  if (linkCheckbox && linkCheckbox.checked) {
    // Link them by setting bottom to match top
    if (topPercentage && bottomPercentage) {
      bottomPercentage.value = topPercentage.value;
      updateBottomPercentage(topPercentage.value);
    }
  }
}

function updateExtremeTimePointSummary() {
  const topPercentage = document.getElementById("topPercentage");
  const bottomPercentage = document.getElementById("bottomPercentage");
  const summaryText = document.getElementById("extremeTimePointSummaryText");
  const topPatientsCount = document.getElementById("topPatientsCount");
  const bottomPatientsCount = document.getElementById("bottomPatientsCount");
  const totalPatientsCount = document.getElementById("totalPatientsCount");
  const selectionModeToggle = document.getElementById("selectionModeToggle");

  if (!topPercentage || !bottomPercentage || !summaryText) return;

  const topPercent = parseInt(topPercentage.value);
  const bottomPercent = parseInt(bottomPercentage.value);
  const isValueMode = selectionModeToggle ? selectionModeToggle.checked : false;

  // Get total patient count from the selected patient file
  const patientFileSelect = document.getElementById("editorPatientFileSelect");

  if (patientFileSelect && patientFileSelect.value) {
    // Fetch actual patient count from API
    fetch(`/dataset/${datasetId}/file/${patientFileSelect.value}/patient-count`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const totalPatients = data.patient_count;

          if (isValueMode) {
            // Value-based selection mode
            const topPatients = Math.round((topPercent / 100) * totalPatients);
            const bottomPatients = Math.round((bottomPercent / 100) * totalPatients);

            // Update summary text for value mode
            summaryText.textContent = `Selecting patients with top ${topPercent}% and bottom ${bottomPercent}% of time variable value range for extreme analysis`;

            // Update patient count badges
            if (topPatientsCount) {
              topPatientsCount.textContent = `~${topPatients} patients`;
            }
            if (bottomPatientsCount) {
              bottomPatientsCount.textContent = `~${bottomPatients} patients`;
            }
            if (totalPatientsCount) {
              totalPatientsCount.textContent = `${totalPatients} total`;
            }
          } else {
            // Patient-based selection mode
            const topPatients = Math.round((topPercent / 100) * totalPatients);
            const bottomPatients = Math.round((bottomPercent / 100) * totalPatients);

            // Update summary text for patient mode
            summaryText.textContent = `Selecting ${topPercent}% top and ${bottomPercent}% bottom patients for extreme time point analysis`;

            // Update patient count badges
            if (topPatientsCount) {
              topPatientsCount.textContent = `${topPatients} patients`;
            }
            if (bottomPatientsCount) {
              bottomPatientsCount.textContent = `${bottomPatients} patients`;
            }
            if (totalPatientsCount) {
              totalPatientsCount.textContent = `${totalPatients} total`;
            }
          }
        } else {
          console.error("Error loading patient count:", data.error);
          updateExtremeTimePointSummaryFallback();
        }
      })
      .catch((error) => {
        console.error("Error loading patient count:", error);
        updateExtremeTimePointSummaryFallback();
      });
  } else {
    updateExtremeTimePointSummaryFallback();
  }
}

function updateExtremeTimePointSummaryFallback() {
  const topPercentage = document.getElementById("topPercentage");
  const bottomPercentage = document.getElementById("bottomPercentage");
  const summaryText = document.getElementById("extremeTimePointSummaryText");
  const topPatientsCount = document.getElementById("topPatientsCount");
  const bottomPatientsCount = document.getElementById("bottomPatientsCount");
  const totalPatientsCount = document.getElementById("totalPatientsCount");
  const selectionModeToggle = document.getElementById("selectionModeToggle");

  if (!topPercentage || !bottomPercentage || !summaryText) return;

  const topPercent = parseInt(topPercentage.value);
  const bottomPercent = parseInt(bottomPercentage.value);
  const isValueMode = selectionModeToggle ? selectionModeToggle.checked : false;

  // Fallback when no file is selected
  if (isValueMode) {
    summaryText.textContent = "Select data files to see time variable value range analysis";
  } else {
    summaryText.textContent = "Select data files to see patient counts";
  }

  if (topPatientsCount) {
    topPatientsCount.textContent = "0 patients";
  }
  if (bottomPatientsCount) {
    bottomPatientsCount.textContent = "0 patients";
  }
  if (totalPatientsCount) {
    totalPatientsCount.textContent = "0 total";
  }
}

function loadPatientCount() {
  // This function should be called when a patient file is selected
  // to fetch the actual patient count from the server
  const patientFileSelect = document.getElementById("editorPatientFileSelect");

  if (patientFileSelect && patientFileSelect.value) {
    // TODO: Implement API call to get patient count
    // For now, using placeholder
    updateExtremeTimePointSummary();
  }
}

// Analysis Methods Functions
function loadAnalysisMethods() {
  fetch(`/dataset/${datasetId}/metadata/analysis-methods`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        displayAnalysisMethods(data.methods, data.default_method, data.categories, data.descriptions);
      } else {
        showAnalysisMethodError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading analysis methods:", error);
      showAnalysisMethodError("Failed to load analysis methods");
    });
}

function displayAnalysisMethods(methods, defaultMethod, categories, descriptions) {
  const select = document.getElementById("analysisMethodSelect");
  const description = document.getElementById("analysisMethodDescription");

  if (!select || !description) return;

  // Clear existing options
  select.innerHTML = '<option value="">Select analysis method...</option>';

  // Group methods by category
  Object.keys(categories).forEach((category) => {
    const categoryMethods = categories[category];

    // Add category header
    const optgroup = document.createElement("optgroup");
    optgroup.label = category;

    // Add methods in this category
    categoryMethods.forEach((methodKey) => {
      if (methods[methodKey]) {
        const method = methods[methodKey];
        const option = document.createElement("option");
        option.value = methodKey;
        option.textContent = method.name;
        optgroup.appendChild(option);
      }
    });

    select.appendChild(optgroup);
  });

  // Set default method if available
  if (defaultMethod && methods[defaultMethod]) {
    select.value = defaultMethod;
    updateAnalysisMethod();
  }
}

function updateAnalysisMethod() {
  const select = document.getElementById("analysisMethodSelect");
  const containersParent = document.getElementById("analysisMethodParametersContainers");
  if (!select || !containersParent) return;
  const selectedKey = select.value;
  // Hide all
  Array.from(containersParent.children).forEach(child => {
    if (child && child.style) child.style.display = "none";
  });
  // Show selected
  if (selectedKey) {
    const showDiv = document.getElementById(`analysisMethodParameters_${selectedKey}`);
    if (showDiv && showDiv.style) {
      showDiv.style.display = "block";
    }
  }
  // Also update card disabling
  if (window.analysisManager && typeof window.analysisManager.updateAnalysisMethodsVisibility === 'function') {
    window.analysisManager.updateAnalysisMethodsVisibility();
  }
  // Also update card disabling
  if (window.analysisManager && typeof window.analysisManager.updateAnalysisMethodsVisibility === 'function') {
    window.analysisManager.updateAnalysisMethodsVisibility();
  }
}

function displayAnalysisMethodParameters(parameters) {
  const form = document.getElementById("analysisMethodParametersForm");
  if (!form || !parameters) return;

  form.innerHTML = "";

  // Create parameter inputs in rows of 2
  const parameterKeys = Object.keys(parameters);
  for (let i = 0; i < parameterKeys.length; i += 2) {
    const row = document.createElement("div");
    row.className = "row mb-3";

    // First parameter
    if (parameterKeys[i]) {
      const col1 = document.createElement("div");
      col1.className = "col-md-6";
      col1.appendChild(createParameterInput(parameterKeys[i], parameters[parameterKeys[i]]));
      row.appendChild(col1);
    }

    // Second parameter
    if (parameterKeys[i + 1]) {
      const col2 = document.createElement("div");
      col2.className = "col-md-6";
      col2.appendChild(createParameterInput(parameterKeys[i + 1], parameters[parameterKeys[i + 1]]));
      row.appendChild(col2);
    }

    form.appendChild(row);
  }
}

function createParameterInput(paramKey, paramConfig) {
  const div = document.createElement("div");
  div.className = "mb-3";

  // Label
  const label = document.createElement("label");
  label.className = "form-label";
  label.textContent = paramConfig.name;
  label.setAttribute("for", `analysisParam_${paramKey}`);
  div.appendChild(label);

  // Input based on type
  if (paramConfig.type === "select") {
    const select = document.createElement("select");
    select.className = "form-select";
    select.id = `analysisParam_${paramKey}`;
    select.name = paramKey;
    select.onchange = () => updateAnalysisMethodSummary();

    paramConfig.options.forEach((option) => {
      const optionElement = document.createElement("option");
      optionElement.value = option;
      optionElement.textContent = option;
      if (option === paramConfig.default) {
        optionElement.selected = true;
      }
      select.appendChild(optionElement);
    });

    div.appendChild(select);
  } else if (paramConfig.type === "boolean") {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "form-check-input";
    checkbox.id = `analysisParam_${paramKey}`;
    checkbox.name = paramKey;
    checkbox.checked = paramConfig.default;
    checkbox.onchange = () => updateAnalysisMethodSummary();

    const labelCheck = document.createElement("label");
    labelCheck.className = "form-check-label";
    labelCheck.setAttribute("for", `analysisParam_${paramKey}`);
    labelCheck.textContent = paramConfig.name;

    const checkDiv = document.createElement("div");
    checkDiv.className = "form-check";
    checkDiv.appendChild(checkbox);
    checkDiv.appendChild(labelCheck);

    div.appendChild(checkDiv);
  } else if (paramConfig.type === "number") {
    const input = document.createElement("input");
    input.type = "number";
    input.className = "form-control";
    input.id = `analysisParam_${paramKey}`;
    input.name = paramKey;
    input.min = paramConfig.min;
    input.max = paramConfig.max;
    input.step = paramConfig.step;
    input.value = paramConfig.default;
    input.onchange = () => updateAnalysisMethodSummary();

    div.appendChild(input);
  }

  // Description
  if (paramConfig.description) {
    const desc = document.createElement("div");
    desc.className = "form-text";
    desc.textContent = paramConfig.description;
    div.appendChild(desc);
  }

  return div;
}

function updateAnalysisMethodSummary() {
  const select = document.getElementById("analysisMethodSelect");
  const summaryText = document.getElementById("analysisMethodSummaryText");
  const parametersCount = document.getElementById("analysisMethodParametersCount");
  const summary = document.getElementById("analysisMethodSummary");

  if (!select || !summaryText || !parametersCount || !summary) return;

  const selectedMethod = select.value;

  if (!selectedMethod) {
    summaryText.textContent = "No analysis method configured";
    parametersCount.textContent = "0 parameters";
    summary.style.display = "none";
    return;
  }

  // Count configured parameters
  const parameterInputs = document.querySelectorAll(
    "#analysisMethodParametersForm input, #analysisMethodParametersForm select"
  );
  let configuredCount = 0;

  parameterInputs.forEach((input) => {
    if (input.type === "checkbox") {
      if (input.checked) configuredCount++;
    } else if (input.value && input.value !== "") {
      configuredCount++;
    }
  });

  // Update summary
  const methodName = select.options[select.selectedIndex].textContent;
  summaryText.textContent = `Analysis method: ${methodName}`;
  parametersCount.textContent = `${configuredCount} parameters configured`;
  summary.style.display = "block";
}

function showAnalysisMethodInfo() {
  const select = document.getElementById("analysisMethodSelect");
  if (!select || !select.value) {
    showToast("Please select an analysis method first", "warning");
    return;
  }

  const selectedMethod = select.value;

  // Fetch method details for info modal
  fetch(`/dataset/${datasetId}/metadata/analysis-methods/${selectedMethod}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAnalysisMethodInfoModal(data.method);
      } else {
        showAnalysisMethodError(data.error);
      }
    })
    .catch((error) => {
      console.error("Error loading method info:", error);
      showAnalysisMethodError("Failed to load method information");
    });
}

function showAnalysisMethodInfoModal(method) {
  // Create modal HTML
  const modalHtml = `
        <div class="modal fade" id="analysisMethodInfoModal" tabindex="-1" aria-labelledby="analysisMethodInfoModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="analysisMethodInfoModalLabel">
                            <i class="fas fa-info-circle me-2"></i>${method.name}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6>Description</h6>
                            <p>${method.description}</p>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Advantages</h6>
                                <ul class="list-unstyled">
                                    ${method.pros
                                      .map((pro) => `<li><i class="fas fa-check text-success me-2"></i>${pro}</li>`)
                                      .join("")}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Limitations</h6>
                                <ul class="list-unstyled">
                                    ${method.cons
                                      .map((con) => `<li><i class="fas fa-times text-danger me-2"></i>${con}</li>`)
                                      .join("")}
                                </ul>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <h6>Use Cases</h6>
                            <ul>
                                ${method.use_cases.map((useCase) => `<li>${useCase}</li>`).join("")}
                            </ul>
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
  const existingModal = document.getElementById("analysisMethodInfoModal");
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHtml);

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("analysisMethodInfoModal"));
  modal.show();

  // Handle modal cleanup
  document.getElementById("analysisMethodInfoModal").addEventListener("hidden.bs.modal", function () {
    document.activeElement.blur();
    this.remove();
  });
}

function showAnalysisMethodError(message) {
  console.error("Analysis Method Error:", message);
  showToast(`Analysis Method Error: ${message}`, "error");
}

// Column Groups Functions
function selectAllColumnGroups() {
  const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = true;
  });
  updateColumnGroupsSummary();
}

function clearAllColumnGroups() {
  const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  updateColumnGroupsSummary();
}

function toggleFieldNames() {
  const fieldNamesElements = document.querySelectorAll(".field-names");
  const toggleButton = document.getElementById("toggleFieldNamesBtn");

  if (!fieldNamesElements.length || !toggleButton) return;

  const isVisible = fieldNamesElements[0].style.display !== "none";

  fieldNamesElements.forEach((element) => {
    element.style.display = isVisible ? "none" : "block";
  });

  toggleButton.textContent = isVisible ? "Show Field Names" : "Hide Field Names";
  toggleButton.classList.toggle("btn-outline-secondary", isVisible);
  toggleButton.classList.toggle("btn-secondary", !isVisible);
}

function updateColumnGroupsSummary() {
  const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
  const summary = document.getElementById("selectionSummary");
  const count = document.getElementById("totalColumnsCount");

  if (summary) {
    summary.textContent = `${checkboxes.length} column groups selected`;
  }

  if (count) {
    // Count actual columns from the selected groups
    let totalColumns = 0;
    checkboxes.forEach((checkbox) => {
      const label = checkbox.nextElementSibling;
      if (label) {
        const columnText = label.querySelector("small");
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
  const patientFile = document.getElementById("editorPatientFileSelect")?.value;
  const taxonomyFile = document.getElementById("editorTaxonomyFileSelect")?.value;
  const brackenFile = document.getElementById("editorBrackenTimePointSelect")?.value;

  const isValid = patientFile && taxonomyFile && brackenFile;

  // Enable/disable run analysis button based on validation
  const runButton = document.querySelector('button[onclick="runAnalysisFromEditor()"]');
  if (runButton) {
    runButton.disabled = !isValid;
  }

  // Update extreme time point summary when patient file changes
  updateExtremeTimePointSummary();

  return isValid;
}

function updateTimePointDescriptionValidation() {
  const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
  const selectedValue = timePointSelect?.value;
  const selectedOption = timePointSelect?.selectedOptions[0];

  if (selectedOption && selectedValue) {
    const suffix = selectedOption.getAttribute("data-suffix");
    const function_ = selectedOption.getAttribute("data-function");

    console.log("Selected time point:", {
      key: selectedValue,
      suffix: suffix,
      function: function_,
      description: selectedOption.textContent,
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
  const reportsContainer = document.getElementById("reportsContainer");
  if (reportsContainer) {
    const noReportsState = document.getElementById("noReportsState");
    const reportsList = document.getElementById("reportsList");

    if (noReportsState) {
      noReportsState.style.display = "block";
    }
    if (reportsList) {
      reportsList.style.display = "none";
    }
  }
}

function clearReportFilters() {
  const reportSearch = document.getElementById("reportSearch");
  const reportTypeFilter = document.getElementById("reportTypeFilter");
  const reportStatusFilter = document.getElementById("reportStatusFilter");

  if (reportSearch) reportSearch.value = "";
  if (reportTypeFilter) reportTypeFilter.value = "all";
  if (reportStatusFilter) reportStatusFilter.value = "all";

  // TODO: Re-filter reports
  console.log("Report filters cleared");
}

// Settings Tab Functions
function loadSettingsTab() {
  // TODO: Implement settings tab loading
  console.log("Loading settings tab");
}

// Utility Functions
window.showAlert = function (message, type) {
  // Create alert element
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  alertDiv.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  // Add to body
  document.body.appendChild(alertDiv);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 5000);
};

// File Action Functions
window.downloadFile = function (fileId) {
  // Show loading state
  const downloadBtn = document.querySelector(`button[onclick="downloadFile(${fileId})"]`);
  const originalContent = downloadBtn.innerHTML;
  downloadBtn.disabled = true;
  downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  // Fetch both file data and schema to preserve column order
  Promise.all([
    fetch(`/file/${fileId}/data`).then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    }),
    fetch(`/file/${fileId}/schema`).then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    }),
  ])
    .then(([data, schema]) => {
      if (data.error) {
        throw new Error(data.error);
      }
      if (schema.error) {
        throw new Error(schema.error);
      }

      // Generate Excel file with proper column order
      generateExcelFileWithSchema(data, schema, fileId);
      showAlert("File downloaded successfully", "success");
    })
    .catch((error) => {
      console.error("Error downloading file:", error);
      showAlert(`Failed to download file: ${error.message}`, "danger");
    })
    .finally(() => {
      // Reset button state
      downloadBtn.disabled = false;
      downloadBtn.innerHTML = originalContent;
    });
};

function generateExcelFileWithSchema(data, schema, fileId) {
  try {
    // Get file info for naming
    const row = document.querySelector(`button[onclick="downloadFile(${fileId})"]`).closest("tr");
    const fileName = row.querySelector("td:first-child").textContent.trim();

    // Create workbook
    const wb = XLSX.utils.book_new();

    // Get column order from schema (preserves original CSV order)
    const columnOrder = schema.columns.map((col) => col.field);

    // Convert data to worksheet with proper column order
    if (Array.isArray(data)) {
      // Data is directly an array of records (most common case)
      if (data.length === 0) {
        throw new Error("No data to export");
      }

      // Use schema column order instead of Object.keys()
      const headers = columnOrder;

      // Convert array of objects to array of arrays for Excel
      // Maintain the exact column order from the schema
      const rows = data.map((record) => headers.map((header) => (record[header] !== null ? record[header] : "")));

      // Add headers as first row
      const worksheetData = [headers, ...rows];

      const ws = XLSX.utils.aoa_to_sheet(worksheetData);

      // Auto-size columns
      const colWidths = headers.map(
        (header) => Math.max(header.length, ...rows.map((row) => String(row[headers.indexOf(header)] || "").length)) + 2
      );
      ws["!cols"] = colWidths.map((width) => ({ wch: Math.min(width, 50) }));

      wb.SheetNames.push("Data");
      wb.Sheets["Data"] = ws;
    } else {
      throw new Error("Unexpected data format");
    }

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    const excelFileName = `${fileName}_${timestamp}.xlsx`;

    // Write and download file
    XLSX.writeFile(wb, excelFileName);
  } catch (error) {
    console.error("Error generating Excel file:", error);
    showAlert(`Error generating Excel file: ${error.message}`, "danger");
  }
}

function generateExcelFile(data, fileId) {
  try {
    // Get file info for naming
    const row = document.querySelector(`button[onclick="downloadFile(${fileId})"]`).closest("tr");
    const fileName = row.querySelector("td:first-child").textContent.trim();

    // Note: This function is kept for backward compatibility
    // The new generateExcelFileWithSchema function should be used instead

    // Create workbook
    const wb = XLSX.utils.book_new();

    // Convert data to worksheet
    if (Array.isArray(data)) {
      // Data is directly an array of records (most common case)
      if (data.length === 0) {
        throw new Error("No data to export");
      }

      // Preserve column order by using the order from the first record
      // Object.keys() maintains insertion order in modern JavaScript
      const headers = Object.keys(data[0]);

      // Convert array of objects to array of arrays for Excel
      // Maintain the exact column order from the original CSV
      const rows = data.map((record) => headers.map((header) => (record[header] !== null ? record[header] : "")));

      // Add headers as first row
      const worksheetData = [headers, ...rows];

      const ws = XLSX.utils.aoa_to_sheet(worksheetData);

      // Auto-size columns
      const colWidths = headers.map(
        (header) => Math.max(header.length, ...rows.map((row) => String(row[headers.indexOf(header)] || "").length)) + 2
      );
      ws["!cols"] = colWidths.map((width) => ({ wch: Math.min(width, 50) }));

      wb.SheetNames.push("Data");
      wb.Sheets["Data"] = ws;
    } else if (data.data && Array.isArray(data.data)) {
      // If data has a 'data' property with array of rows
      // Check if it's array of objects or array of arrays
      if (data.data.length > 0 && typeof data.data[0] === "object" && !Array.isArray(data.data[0])) {
        // Array of objects - preserve column order
        const headers = Object.keys(data.data[0]);
        const rows = data.data.map((record) =>
          headers.map((header) => (record[header] !== null ? record[header] : ""))
        );
        const worksheetData = [headers, ...rows];
        const ws = XLSX.utils.aoa_to_sheet(worksheetData);
        wb.SheetNames.push("Data");
        wb.Sheets["Data"] = ws;
      } else {
        // Array of arrays - use as is
        const ws = XLSX.utils.aoa_to_sheet(data.data);
        wb.SheetNames.push("Data");
        wb.Sheets["Data"] = ws;
      }
    } else {
      // If data is an object, try to find array properties
      const dataKeys = Object.keys(data);
      let foundArray = false;

      for (const key of dataKeys) {
        if (Array.isArray(data[key])) {
          // Check if it's array of objects or array of arrays
          if (data[key].length > 0 && typeof data[key][0] === "object" && !Array.isArray(data[key][0])) {
            // Array of objects - preserve column order
            const headers = Object.keys(data[key][0]);
            const rows = data[key].map((record) =>
              headers.map((header) => (record[header] !== null ? record[header] : ""))
            );
            const worksheetData = [headers, ...rows];
            const ws = XLSX.utils.aoa_to_sheet(worksheetData);
            wb.SheetNames.push(key);
            wb.Sheets[key] = ws;
          } else {
            // Array of arrays - use as is
            const ws = XLSX.utils.aoa_to_sheet(data[key]);
            wb.SheetNames.push(key);
            wb.Sheets[key] = ws;
          }
          foundArray = true;
        }
      }

      if (!foundArray) {
        throw new Error("No array data found to export");
      }
    }

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, "-");
    const excelFileName = `${fileName}_${timestamp}.xlsx`;

    // Write and download file
    XLSX.writeFile(wb, excelFileName);
  } catch (error) {
    console.error("Error generating Excel file:", error);
    showAlert(`Error generating Excel file: ${error.message}`, "danger");
  }
}

window.duplicateFile = function (fileId) {
  // Show confirmation dialog
  if (
    confirm(
      'Are you sure you want to duplicate this file? A copy will be created with "_copy" appended to the filename.'
    )
  ) {
    // Find the row to get file info for better user feedback
    const row = document.querySelector(`button[onclick="duplicateFile(${fileId})"]`).closest("tr");
    const fileName = row.querySelector("td:first-child").textContent.trim();

    // Show loading state
    const duplicateBtn = document.querySelector(`button[onclick="duplicateFile(${fileId})"]`);
    const originalContent = duplicateBtn.innerHTML;
    duplicateBtn.disabled = true;
    duplicateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    // Send duplicate request
    fetch(`/dataset/${datasetId}/files/${fileId}/duplicate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showAlert(`File "${fileName}" duplicated successfully`, "success");
          // Refresh the files table
          loadFilesTable();
        } else {
          showAlert(data.error || "Failed to duplicate file", "danger");
        }
      })
      .catch((error) => {
        console.error("Error duplicating file:", error);
        showAlert("Failed to duplicate file", "danger");
      })
      .finally(() => {
        // Reset button state
        duplicateBtn.disabled = false;
        duplicateBtn.innerHTML = originalContent;
      });
  }
};

window.renameFile = function (fileId, currentName, fileType) {
  // Extract the base name without extension for better UX
  const lastDotIndex = currentName.lastIndexOf(".");
  const baseName = lastDotIndex !== -1 ? currentName.substring(0, lastDotIndex) : currentName;
  const extension = lastDotIndex !== -1 ? currentName.substring(lastDotIndex) : "";

  const newName = prompt(`Enter new name for ${fileType} file:`, baseName);
  if (!newName || newName.trim() === "") {
    return;
  }

  const finalName = newName.trim() + extension;

  // Show loading state
  const renameBtn = document.querySelector(`button[onclick="renameFile(${fileId}, '${currentName}', '${fileType}')"]`);
  const originalContent = renameBtn.innerHTML;
  renameBtn.disabled = true;
  renameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  // Send rename request
  fetch(`/dataset/${datasetId}/files/${fileId}/rename`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      new_filename: finalName,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert(`File renamed to "${finalName}"`, "success");
        // Refresh the files table
        loadFilesTable();
      } else {
        showAlert(data.error || "Failed to rename file", "danger");
      }
    })
    .catch((error) => {
      console.error("Error renaming file:", error);
      showAlert("Failed to rename file", "danger");
    })
    .finally(() => {
      // Reset button state
      renameBtn.disabled = false;
      renameBtn.innerHTML = originalContent;
    });
};

window.editTable = function (fileId) {
  // Navigate to the edit table page
  window.location.href = `/file/${fileId}`;
};

window.cureData = function (fileId) {
  // Show confirmation dialog
  if (!confirm("Are you sure you want to cure this data? This will process and validate the file.")) {
    return;
  }

  // Find the button and show loading state
  const cureBtn = document.querySelector(`button[onclick="cureData(${fileId})"]`);
  const originalContent = cureBtn.innerHTML;
  cureBtn.disabled = true;
  cureBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Curing...';

  // Send cure request
  fetch(`/dataset/${datasetId}/files/${fileId}/cure`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showAlert("Data curing started successfully", "success");
        // Refresh the files table to show updated status
        loadFilesTable();
      } else {
        showAlert(data.error || "Failed to start data curing", "danger");
      }
    })
    .catch((error) => {
      console.error("Error curing data:", error);
      showAlert("Failed to start data curing", "danger");
    })
    .finally(() => {
      // Reset button state
      cureBtn.disabled = false;
      cureBtn.innerHTML = originalContent;
    });
};

window.deleteFile = function (fileId) {
  // Show confirmation dialog
  if (confirm("Are you sure you want to delete this file? This action cannot be undone.")) {
    // Find the row to get file info for better user feedback
    const row = document.querySelector(`button[onclick="deleteFile(${fileId})"]`).closest("tr");
    const fileName = row.querySelector("td:first-child").textContent.trim();

    // Show loading state
    const deleteBtn = document.querySelector(`button[onclick="deleteFile(${fileId})"]`);
    const originalContent = deleteBtn.innerHTML;
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    // Send delete request
    fetch(`/dataset/${datasetId}/files/${fileId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showAlert(`File "${fileName}" deleted successfully`, "success");
          // Refresh the files table
          loadFilesTable();
        } else {
          showAlert(data.error || "Failed to delete file", "danger");
        }
      })
      .catch((error) => {
        console.error("Error deleting file:", error);
        showAlert("Failed to delete file", "danger");
      })
      .finally(() => {
        // Reset button state
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = originalContent;
      });
  }
};
