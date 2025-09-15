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
    case "reports":
      loadReportsTab();
      break;
    case "settings":
      loadSettingsTab();
      break;
    default:
      loadFilesTab();
  }
}

// Tab Navigation Functions
function goToTab(tabName) {
  const tabMap = {
    "files-tab": "files",
    "reports-tab": "reports",
    "settings-tab": "settings"
  };

  const tab = tabMap[tabName];
  if (tab) {
    window.location.href = `/dataset/${datasetId}/${tab}`;
  }
}

// Files Tab Functions
function loadFilesTab() {
  console.log("Loading files tab...");
  loadFilesList();
  setupFileUpload();
}

function loadFilesList() {
  fetch(`/dataset/${datasetId}/files/api`)
    .then((response) => response.json())
    .then((data) => {
      if (data.files) {
        displayFilesList(data.files, data.dataset_status);
      }
    })
    .catch((error) => {
      console.error("Error loading files:", error);
      showAlert("Failed to load files", "danger");
    });
}

function displayFilesList(files, datasetStatus) {
  const container = document.getElementById("filesListContainer");
  if (!container) return;

  if (files.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5">
        <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
        <h5 class="text-muted mb-3">No Files Uploaded</h5>
        <p class="text-muted mb-4">Upload your first file to get started with your dataset.</p>
        <button type="button" class="btn btn-primary" onclick="showFileUploadModal()">
          <i class="fas fa-upload me-1"></i>Upload First File
        </button>
      </div>
    `;
    return;
  }

  // Group files by type
  const filesByType = {
    patients: files.filter(f => f.file_type === 'patients'),
    taxonomy: files.filter(f => f.file_type === 'taxonomy'),
    bracken: files.filter(f => f.file_type === 'bracken')
  };

  let html = '<div class="row">';

  // Patients files
  if (filesByType.patients.length > 0) {
    html += `
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header bg-primary text-white">
            <h6 class="mb-0">
              <i class="fas fa-user-injured me-2"></i>
              Patient Data Files
            </h6>
          </div>
          <div class="card-body">
            ${filesByType.patients.map(file => createFileCard(file)).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // Taxonomy files
  if (filesByType.taxonomy.length > 0) {
    html += `
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header bg-info text-white">
            <h6 class="mb-0">
              <i class="fas fa-sitemap me-2"></i>
              Taxonomy Files
            </h6>
          </div>
          <div class="card-body">
            ${filesByType.taxonomy.map(file => createFileCard(file)).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // Bracken files
  if (filesByType.bracken.length > 0) {
    html += `
      <div class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header bg-success text-white">
            <h6 class="mb-0">
              <i class="fas fa-chart-bar me-2"></i>
              Bracken Files
            </h6>
          </div>
          <div class="card-body">
            ${filesByType.bracken.map(file => createFileCard(file)).join('')}
          </div>
        </div>
      </div>
    `;
  }

  html += '</div>';

  // Add dataset status summary
  if (datasetStatus) {
    html += `
      <div class="row mt-4">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-info-circle me-2"></i>
                Dataset Status
              </h6>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3">
                  <div class="h5 text-primary">${datasetStatus.file_count || 0}</div>
                  <small class="text-muted">Files</small>
                </div>
                <div class="col-md-3">
                  <div class="h5 text-info">${formatFileSize(datasetStatus.total_size || 0)}</div>
                  <small class="text-muted">Total Size</small>
                </div>
                <div class="col-md-3">
                  <div class="h5 text-${datasetStatus.is_complete ? 'success' : 'warning'}">${datasetStatus.completion_percentage || 0}%</div>
                  <small class="text-muted">Complete</small>
                </div>
                <div class="col-md-3">
                  <span class="badge bg-${datasetStatus.status === 'ready' ? 'success' : 'secondary'}">${datasetStatus.status || 'draft'}</span>
                  <small class="text-muted d-block">Status</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function createFileCard(file) {
  const statusBadge = getStatusBadge(file.cure_status, file.cure_validation_status);
  const size = formatFileSize(file.size);
  const uploadedDate = new Date(file.uploaded_at).toLocaleDateString();

  return `
    <div class="file-item mb-3 p-3 border rounded">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <h6 class="mb-0">${file.filename}</h6>
        <div class="dropdown">
          <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
            <i class="fas fa-ellipsis-v"></i>
          </button>
          <ul class="dropdown-menu">
            <li><a class="dropdown-item" href="#" onclick="downloadFile(${file.id})">
              <i class="fas fa-download me-2"></i>Download
            </a></li>
            <li><a class="dropdown-item" href="#" onclick="deleteFile(${file.id})">
              <i class="fas fa-trash me-2"></i>Delete
            </a></li>
          </ul>
        </div>
      </div>
      <div class="small text-muted">
        <div>${statusBadge}</div>
        <div><i class="fas fa-weight me-1"></i>${size}</div>
        <div><i class="fas fa-calendar me-1"></i>${uploadedDate}</div>
      </div>
    </div>
  `;
}

function setupFileUpload() {
  // File upload functionality is handled by the upload modal
  console.log("File upload setup complete");
}

function showFileUploadModal() {
  // This would show a file upload modal
  console.log("Showing file upload modal...");
}

// Reports Tab Functions
function loadReportsTab() {
  console.log("Loading reports tab...");
  // Reports functionality would be implemented here
}

// Settings Tab Functions
function loadSettingsTab() {
  console.log("Loading settings tab...");
  // Settings functionality would be implemented here
}

// Utility Functions
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getStatusBadge(cureStatus, validationStatus) {
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
}

function showAlert(message, type = 'info') {
  // Create and show Bootstrap alert
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  // Insert at the top of the content area
  const contentArea = document.querySelector('.container');
  if (contentArea) {
    contentArea.insertBefore(alertDiv, contentArea.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove();
      }
    }, 5000);
  }
}

function downloadFile(fileId) {
  console.log(`Downloading file ${fileId}...`);
  // Implement file download functionality
}

function deleteFile(fileId) {
  if (confirm('Are you sure you want to delete this file?')) {
    console.log(`Deleting file ${fileId}...`);
    // Implement file deletion functionality
  }
}
