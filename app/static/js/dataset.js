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
      // Analysis tab is now handled by dataset_analysis.js
      break;
      // Validate required fields
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
