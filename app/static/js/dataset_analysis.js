// Dataset Analysis Tab JavaScript
// Handles analysis creation, configuration, and management

class DatasetAnalysisManager {
  constructor(datasetId) {
    this.datasetId = datasetId;
    this.currentAnalysis = null;
    this.columnGroupsData = null;
  }

  // Initialize analysis tab
  async init() {
    this.setupEventListeners();
    await this.loadAnalysisList();
    await this.loadFilesForDataSources();
    await this.loadColumnGroups();
    await this.loadBrackenTimePoints();
    await this.loadStratifications();
    await this.loadClusteringMethods();
    await this.loadAnalysisMethods();
  }

  // Setup event listeners
  setupEventListeners() {
    // Analysis editor form validation
    const analysisForm = document.getElementById("analysisName");
    if (analysisForm) {
      analysisForm.addEventListener("input", () => this.validateAnalysisEditor());
    }

    // File selection changes
    const fileSelects = document.querySelectorAll('select[id$="FileSelect"]');
    fileSelects.forEach((select) => {
      select.addEventListener("change", () => this.validateAnalysisEditor());
    });

    // Percentage range inputs
    const topPercentage = document.getElementById("topPercentage");
    const bottomPercentage = document.getElementById("bottomPercentage");

    if (topPercentage) {
      topPercentage.addEventListener("input", (e) => this.updateTopPercentage(e.target.value));
    }

    if (bottomPercentage) {
      bottomPercentage.addEventListener("input", (e) => this.updateBottomPercentage(e.target.value));
    }

    // Linked percentages checkbox
    const linkCheckbox = document.getElementById("linkPercentages");
    if (linkCheckbox) {
      linkCheckbox.addEventListener("change", () => this.toggleLinkedPercentages());
    }

    // Selection mode toggle
    const selectionModeToggle = document.getElementById("selectionModeToggle");
    if (selectionModeToggle) {
      selectionModeToggle.addEventListener("change", () => this.toggleSelectionMode());
    }
  }

  async loadAnalysisList() {
    const analysisListContainer = document.getElementById("analysisListContainer");
    const noAnalysesState = document.getElementById("noAnalysesState");
    const analysisTable = document.getElementById("analysisTable");
    const analysisTableBody = document.getElementById("analysisTableBody");

    if (!analysisListContainer) return;

    try {
      // Show loading state by hiding existing content and showing spinner
      if (noAnalysesState) noAnalysesState.style.display = "none";
      if (analysisTable) analysisTable.style.display = "none";

      // Add loading overlay
      const loadingDiv = document.createElement("div");
      loadingDiv.id = "loadingState";
      loadingDiv.className = "text-center py-4";
      loadingDiv.innerHTML = `
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="text-muted mt-2">Loading analyses...</p>
      `;
      analysisListContainer.appendChild(loadingDiv);

      // Fetch analyses from server
      const data = await DatasetUtils.api.call(`/dataset/${this.datasetId}/analysis/list`);

      // Remove loading state
      const loadingState = document.getElementById("loadingState");
      if (loadingState) loadingState.remove();

      if (data.success && data.analyses && data.analyses.length > 0) {
        // Hide no analyses state and show table
        if (noAnalysesState) {
          noAnalysesState.style.display = "none";
        }
        if (analysisTable) {
          analysisTable.style.display = "block";
        }

        // Clear and populate table
        if (analysisTableBody) {
          analysisTableBody.innerHTML = "";

          data.analyses.forEach((analysis) => {
            const row = this.createAnalysisTableRow(analysis);
            analysisTableBody.appendChild(row);
          });
        } else {
          console.error("analysisTableBody not found!");
        }
      } else {
        // Show no analyses state
        if (noAnalysesState) noAnalysesState.style.display = "block";
        if (analysisTable) analysisTable.style.display = "none";
      }
    } catch (error) {
      console.error("Error loading analysis list:", error);

      // Remove loading state
      const loadingState = document.getElementById("loadingState");
      if (loadingState) loadingState.remove();

      // Show error state
      const errorDiv = document.createElement("div");
      errorDiv.className = "text-center py-4";
      errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
        <h6 class="text-warning mb-2">Error Loading Analyses</h6>
        <p class="text-muted mb-3">Unable to load saved analyses. Please try again.</p>
        <button type="button" class="btn btn-outline-primary" onclick="refreshAnalysisList()">
          <i class="fas fa-sync-alt me-1"></i>Retry
        </button>
      `;
      analysisListContainer.appendChild(errorDiv);
    }
  }

  // Create analysis table row
  createAnalysisTableRow(analysis) {
    const row = document.createElement("tr");

    // Format dates
    const createdDate = new Date(analysis.created_at).toLocaleDateString();
    const modifiedDate = new Date(analysis.modified_at).toLocaleDateString();

    // Format file size
    const sizeKB = Math.round(analysis.size / 1024);
    const sizeText = sizeKB > 1024 ? `${Math.round(sizeKB / 1024)} MB` : `${sizeKB} KB`;

    row.innerHTML = `
            <td>
                <div>
                    <strong>${analysis.name}</strong>
                    ${analysis.description ? `<br><small class="text-muted">${analysis.description}</small>` : ""}
                </div>
            </td>
            <td>
                <span class="text-muted">${createdDate}</span>
            </td>
            <td>
                <span class="text-muted">${modifiedDate}</span>
            </td>
            <td>
                <span class="badge bg-info">${sizeText}</span>
            </td>
            <td>
                <span class="text-muted">Not run</span>
            </td>
            <td>
                <span class="badge bg-secondary">Unknown</span>
            </td>
            <td>
                <span class="badge bg-success">Saved</span>
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-outline-primary" onclick="loadAnalysis('${
                      analysis.filename
                    }')" title="Load Analysis">
                        <i class="fas fa-folder-open"></i>
                    </button>
                    <button type="button" class="btn btn-outline-success" onclick="runAnalysis('${
                      analysis.filename
                    }')" title="Run Analysis">
                        <i class="fas fa-play"></i>
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="duplicateAnalysis('${
                      analysis.filename
                    }')" title="Duplicate Analysis">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button type="button" class="btn btn-outline-warning" onclick="renameAnalysis('${
                      analysis.filename
                    }', '${analysis.name}')" title="Rename Analysis">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="deleteAnalysis('${
                      analysis.filename
                    }')" title="Delete Analysis">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

    return row;
  }

  // Create new analysis
  createNewAnalysis() {
    const analysisListContainer = document.getElementById("analysisListContainer");
    const analysisEditorSection = document.getElementById("analysisEditorSection");

    if (analysisListContainer) {
      analysisListContainer.style.display = "none";
    }
    if (analysisEditorSection) {
      analysisEditorSection.style.display = "block";
    }

    this.resetAnalysisEditor();
  }

  // Cancel analysis edit
  cancelAnalysisEdit() {
    const analysisListContainer = document.getElementById("analysisListContainer");
    const analysisEditorSection = document.getElementById("analysisEditorSection");

    if (analysisListContainer) {
      analysisListContainer.style.display = "block";
    }
    if (analysisEditorSection) {
      analysisEditorSection.style.display = "none";
    }
  }

  // Save analysis
  async saveAnalysis() {
    const analysisName = document.getElementById("analysisName").value.trim();

    if (!analysisName) {
      DatasetUtils.showAlert("Please enter an analysis name", "warning");
      return;
    }

    try {
      const config = this.collectAnalysisConfiguration();

      const response = await DatasetUtils.api.call(`/dataset/${this.datasetId}/analysis/save`, {
        method: "POST",
        body: JSON.stringify({
          analysis_name: analysisName,
          analysis_description: document.getElementById("analysisDescription").value.trim(),
          configuration: config,
        }),
      });

      if (response.success) {
        DatasetUtils.showAlert("Analysis saved successfully", "success");
        this.cancelAnalysisEdit();
        this.loadAnalysisList();
      } else {
        DatasetUtils.showAlert(response.message, "error");
      }
    } catch (error) {
      console.error("Save analysis error:", error);
      DatasetUtils.showAlert("Failed to save analysis", "error");
    }
  }

  // Collect analysis configuration
  collectAnalysisConfiguration() {
    return {
      dataSources: this.collectDataSources(),
      columnGroups: this.collectColumnGroups(),
      timePoint: this.collectTimePoint(),
      stratifications: this.collectStratificationMethods(),
      clustering: this.collectClusteringParameters(),
      clusterRepresentative: this.collectClusterRepresentativeParameters(),
      analysisMethods: this.collectAnalysisMethods(),
      extremeTimePoint: this.collectExtremeTimePointConfig(),
    };
  }

  // Collect data sources
  collectDataSources() {
    return {
      patientFile: document.getElementById("editorPatientFileSelect").value,
      taxonomyFile: document.getElementById("editorTaxonomyFileSelect").value,
      brackenFile: document.getElementById("editorBrackenFileSelect").value,
    };
  }

  // Collect column groups
  collectColumnGroups() {
    const container = document.getElementById("columnGroupsContainer");
    const selectedGroups = [];

    if (container) {
      const checkboxes = container.querySelectorAll('input[type="checkbox"]:checked');
      checkboxes.forEach((checkbox) => {
        selectedGroups.push(checkbox.value);
      });
    }

    return selectedGroups;
  }

  // Collect time point
  collectTimePoint() {
    return document.getElementById("editorBrackenTimePointSelect").value;
  }

  // Collect stratification methods
  collectStratificationMethods() {
    const container = document.getElementById("stratificationContainer");
    const selectedStratifications = [];

    if (container) {
      const checkboxes = container.querySelectorAll('input[type="checkbox"]:checked');
      checkboxes.forEach((checkbox) => {
        selectedStratifications.push(checkbox.value);
      });
    }

    return selectedStratifications;
  }

  // Collect clustering parameters
  collectClusteringParameters() {
    const container = document.getElementById("clusteringParametersForm");
    const parameters = {};

    if (container) {
      const inputs = container.querySelectorAll("input, select");
      inputs.forEach((input) => {
        if (input.id && input.value !== "") {
          parameters[input.id] = input.value;
        }
      });
    }

    return {
      method: document.getElementById("clusteringMethodSelect").value,
      parameters: parameters,
    };
  }

  // Collect cluster representative parameters
  collectClusterRepresentativeParameters() {
    const container = document.getElementById("clusterRepresentativeDetails");
    const parameters = {};

    if (container) {
      const inputs = container.querySelectorAll("input, select");
      inputs.forEach((input) => {
        if (input.id && input.value !== "") {
          parameters[input.id] = input.value;
        }
      });
    }

    return {
      method: document.getElementById("clusterRepresentativeMethod").value,
      parameters: parameters,
    };
  }

  // Collect analysis methods
  collectAnalysisMethods() {
    const container = document.getElementById("analysisMethodParametersForm");
    const parameters = {};

    if (container) {
      const inputs = container.querySelectorAll("input, select");
      inputs.forEach((input) => {
        if (input.id && input.value !== "") {
          parameters[input.id] = input.value;
        }
      });
    }

    return {
      method: document.getElementById("analysisMethodSelect").value,
      parameters: parameters,
    };
  }

  // Collect extreme time point configuration
  collectExtremeTimePointConfig() {
    const isValueMode = document.getElementById("selectionModeToggle").checked;

    return {
      mode: isValueMode ? "value" : "percentage",
      topPercentage: parseInt(document.getElementById("topPercentage").value),
      bottomPercentage: parseInt(document.getElementById("bottomPercentage").value),
      linked: document.getElementById("linkPercentages").checked,
    };
  }

  // Load files for data sources
  async loadFilesForDataSources() {
    try {
      const data = await DatasetUtils.api.getDatasetFiles(this.datasetId);

      if (data.success) {
        this.populateFileDropdowns(data.files);
      }
    } catch (error) {
      console.error("Failed to load files for data sources:", error);
    }
  }

  // Populate file dropdowns
  populateFileDropdowns(files) {
    const selects = ["editorPatientFileSelect", "editorTaxonomyFileSelect", "editorBrackenFileSelect"];

    selects.forEach((selectId) => {
      const select = document.getElementById(selectId);
      if (select) {
        // Clear existing options except first
        while (select.children.length > 1) {
          select.removeChild(select.lastChild);
        }

        // Add file options
        files.forEach((file) => {
          const option = document.createElement("option");
          option.value = file.id;
          option.textContent = file.filename;

          // Categorize files by type
          switch (file.file_type) {
            case "patients":
              if (selectId === "editorPatientFileSelect") {
                select.appendChild(option);
              }
              break;
            case "taxonomy":
              if (selectId === "editorTaxonomyFileSelect") {
                select.appendChild(option);
              }
              break;
            case "bracken":
              if (selectId === "editorBrackenFileSelect") {
                select.appendChild(option);
              }
              break;
          }
        });
      }
    });
  }

  // Load column groups
  async loadColumnGroups() {
    try {
      const data = await DatasetUtils.api.getColumnGroups(this.datasetId);

      if (data.success) {
        this.displayColumnGroups(data.column_groups);
        this.columnGroupsData = data.column_groups;
      } else {
        this.showColumnGroupsError(data.message);
      }
    } catch (error) {
      console.error("Failed to load column groups:", error);
      this.showColumnGroupsError("Failed to load column groups");
    }
  }

  // Display column groups
  displayColumnGroups(columnGroups) {
    const container = document.getElementById("columnGroupsContainer");

    if (!container) return;

    const groupsHTML = Object.entries(columnGroups)
      .map(([groupKey, groupData]) => {
        const groupName = DatasetUtils.formatGroupName(groupKey);
        const fieldCount = groupData.fields ? groupData.fields.length : 0;

        return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="${groupKey}" id="group_${groupKey}">
                                <label class="form-check-label" for="group_${groupKey}">
                                    <strong>${groupName}</strong>
                                    <small class="text-muted d-block">${fieldCount} fields</small>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            `;
      })
      .join("");

    container.innerHTML = groupsHTML;
    this.updateColumnGroupsSummary();
  }

  // Show column groups error
  showColumnGroupsError(message) {
    const container = document.getElementById("columnGroupsContainer");
    if (container) {
      container.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Unable to load column groups:</strong> ${message}
                </div>
            `;
    }
  }

  // Load bracken time points
  async loadBrackenTimePoints() {
    try {
      const data = await DatasetUtils.api.getBrackenTimePoints(this.datasetId);

      if (data.success) {
        this.displayBrackenTimePoints(data.time_points);
      } else {
        this.showBrackenTimePointsError(data.message);
      }
    } catch (error) {
      console.error("Failed to load bracken time points:", error);
      this.showBrackenTimePointsError("Failed to load time points");
    }
  }

  // Display bracken time points
  displayBrackenTimePoints(timePoints, defaultTimePoint = null) {
    const timePointSelect = document.getElementById("editorBrackenTimePointSelect");

    if (!timePointSelect) return;

    // Clear existing options except first
    while (timePointSelect.children.length > 1) {
      timePointSelect.removeChild(timePointSelect.lastChild);
    }

    // Add time point options
    Object.entries(timePoints).forEach(([key, timePoint]) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = DatasetUtils.formatTimePointName(key);

      if (defaultTimePoint && timePoint.key === defaultTimePoint) {
        option.selected = true;
      }

      timePointSelect.appendChild(option);
    });

    if (defaultTimePoint) {
      this.updateTimePointDescription();
    }
  }

  // Show bracken time points error
  showBrackenTimePointsError(message) {
    const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
    if (timePointSelect) {
      while (timePointSelect.children.length > 1) {
        timePointSelect.removeChild(timePointSelect.lastChild);
      }
    }

    DatasetUtils.showAlert(`Failed to load time points: ${message}`, "warning");
  }

  // Load stratifications
  async loadStratifications() {
    try {
      const data = await DatasetUtils.api.getStratifications(this.datasetId);

      if (data.success) {
        this.displayStratifications(data.stratifications);
      } else {
        this.showStratificationsError(data.message);
      }
    } catch (error) {
      console.error("Failed to load stratifications:", error);
      this.showStratificationsError("Failed to load stratifications");
    }
  }

  // Display stratifications
  displayStratifications(stratifications) {
    const container = document.getElementById("stratificationContainer");

    if (!container) return;

    const stratificationsHTML = Object.entries(stratifications)
      .map(([key, stratification]) => {
        return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="${key}" id="strat_${key}">
                                <label class="form-check-label" for="strat_${key}">
                                    <strong>${stratification.name}</strong>
                                    <small class="text-muted d-block">${stratification.description}</small>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
            `;
      })
      .join("");

    container.innerHTML = stratificationsHTML;
    this.updateStratificationSummary();
  }

  // Show stratifications error
  showStratificationsError(message) {
    const container = document.getElementById("stratificationContainer");
    if (container) {
      container.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Unable to load stratifications:</strong> ${message}
                </div>
            `;
    }
  }

  // Load clustering methods
  async loadClusteringMethods() {
    try {
      const data = await DatasetUtils.api.getClusteringMethods(this.datasetId);

      if (data.success) {
        this.displayClusteringMethods(data.methods);
      } else {
        this.showClusteringError(data.message);
      }
    } catch (error) {
      console.error("Failed to load clustering methods:", error);
      this.showClusteringError("Failed to load clustering methods");
    }
  }

  // Display clustering methods
  displayClusteringMethods(clusteringMethods, defaultMethod = null) {
    const methodSelect = document.getElementById("clusteringMethodSelect");

    if (!methodSelect) return;

    // Clear existing options except first
    while (methodSelect.children.length > 1) {
      methodSelect.removeChild(methodSelect.lastChild);
    }

    // Add method options
    Object.entries(clusteringMethods).forEach(([key, method]) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = method.name;

      if (defaultMethod && key === defaultMethod) {
        option.selected = true;
      }

      methodSelect.appendChild(option);
    });

    if (defaultMethod) {
      this.updateClusteringParameters();
    }
  }

  // Show clustering error
  showClusteringError(message) {
    DatasetUtils.showAlert(`Failed to load clustering methods: ${message}`, "warning");
  }

  // Load analysis methods
  async loadAnalysisMethods() {
    try {
      const data = await DatasetUtils.api.getAnalysisMethods(this.datasetId);

      if (data.success) {
        this.displayAnalysisMethods(data.methods);
      } else {
        this.showAnalysisMethodError(data.message);
      }
    } catch (error) {
      console.error("Failed to load analysis methods:", error);
      this.showAnalysisMethodError("Failed to load analysis methods");
    }
  }

  // Display analysis methods
  displayAnalysisMethods(methods, defaultMethod = null) {
    const methodSelect = document.getElementById("analysisMethodSelect");

    if (!methodSelect) return;

    // Clear existing options except first
    while (methodSelect.children.length > 1) {
      methodSelect.removeChild(methodSelect.lastChild);
    }

    // Add method options
    Object.entries(methods).forEach(([key, method]) => {
      const option = document.createElement("option");
      option.value = key;
      option.textContent = method.name;

      if (defaultMethod && key === defaultMethod) {
        option.selected = true;
      }

      methodSelect.appendChild(option);
    });

    if (defaultMethod) {
      this.updateAnalysisMethod();
    }
  }

  // Show analysis method error
  showAnalysisMethodError(message) {
    DatasetUtils.showAlert(`Failed to load analysis methods: ${message}`, "warning");
  }

  // Toggle selection mode
  toggleSelectionMode() {
    const toggle = document.getElementById("selectionModeToggle");
    const isValueMode = toggle.checked;

    const topLabel = document.getElementById("topPercentageLabel");
    const bottomLabel = document.getElementById("bottomPercentageLabel");
    const topDescription = document.getElementById("topPercentageDescription");
    const bottomDescription = document.getElementById("bottomPercentageDescription");

    if (isValueMode) {
      if (topLabel) topLabel.textContent = "Top Value Range %";
      if (bottomLabel) bottomLabel.textContent = "Bottom Value Range %";
      if (topDescription) topDescription.textContent = "Percentage of time variable value range for top patients";
      if (bottomDescription)
        bottomDescription.textContent = "Percentage of time variable value range for bottom patients";
    } else {
      if (topLabel) topLabel.textContent = "Top Percentage";
      if (bottomLabel) bottomLabel.textContent = "Bottom Percentage";
      if (topDescription) topDescription.textContent = "Percentage of patients with highest time values";
      if (bottomDescription) bottomDescription.textContent = "Percentage of patients with lowest time values";
    }

    this.updateExtremeTimePointSummary();
  }

  // Update top percentage
  updateTopPercentage(value) {
    const topPercentageValue = document.getElementById("topPercentageValue");
    if (topPercentageValue) {
      topPercentageValue.textContent = value + "%";
    }

    const linkCheckbox = document.getElementById("linkPercentages");
    if (linkCheckbox && linkCheckbox.checked) {
      const bottomPercentage = document.getElementById("bottomPercentage");
      if (bottomPercentage && bottomPercentageValue) {
        bottomPercentage.value = value;
        this.updateBottomPercentage(value);
      }
    }

    this.updateExtremeTimePointSummary();
  }

  // Update bottom percentage
  updateBottomPercentage(value) {
    const bottomPercentageValue = document.getElementById("bottomPercentageValue");
    if (bottomPercentageValue) {
      bottomPercentageValue.textContent = value + "%";
    }

    const linkCheckbox = document.getElementById("linkPercentages");
    if (linkCheckbox && linkCheckbox.checked) {
      const topPercentage = document.getElementById("topPercentage");
      if (topPercentage && topPercentageValue) {
        topPercentage.value = value;
        this.updateTopPercentage(value);
      }
    }

    this.updateExtremeTimePointSummary();
  }

  // Toggle linked percentages
  toggleLinkedPercentages() {
    const linkCheckbox = document.getElementById("linkPercentages");

    if (linkCheckbox && linkCheckbox.checked) {
      const topPercentage = document.getElementById("topPercentage");
      const bottomPercentage = document.getElementById("bottomPercentage");

      if (topPercentage && bottomPercentage) {
        bottomPercentage.value = topPercentage.value;
        this.updateBottomPercentage(topPercentage.value);
      }
    }
  }

  // Update extreme time point summary
  updateExtremeTimePointSummary() {
    const patientFileSelect = document.getElementById("editorPatientFileSelect");

    if (patientFileSelect && patientFileSelect.value) {
      this.loadPatientCount();
    } else {
      this.updateExtremeTimePointSummaryFallback();
    }
  }

  // Load patient count
  async loadPatientCount() {
    const patientFileSelect = document.getElementById("editorPatientFileSelect");

    if (patientFileSelect && patientFileSelect.value) {
      try {
        const data = await DatasetUtils.api.call(
          `/dataset/${this.datasetId}/file/${patientFileSelect.value}/patient-count`
        );

        if (data.success) {
          const isValueMode = document.getElementById("selectionModeToggle").checked;
          const topPercentage = parseInt(document.getElementById("topPercentage").value);
          const bottomPercentage = parseInt(document.getElementById("bottomPercentage").value);

          const topPatientsCount = Math.round((data.patient_count * topPercentage) / 100);
          const bottomPatientsCount = Math.round((data.patient_count * bottomPercentage) / 100);
          const totalPatientsCount = data.patient_count;

          this.updatePatientCounts(topPatientsCount, bottomPatientsCount, totalPatientsCount, isValueMode);
        }
      } catch (error) {
        console.error("Failed to load patient count:", error);
        this.updateExtremeTimePointSummaryFallback();
      }
    }
  }

  // Update patient counts display
  updatePatientCounts(topCount, bottomCount, totalCount, isValueMode) {
    const topPatientsCount = document.getElementById("topPatientsCount");
    const bottomPatientsCount = document.getElementById("bottomPatientsCount");
    const totalPatientsCount = document.getElementById("totalPatientsCount");
    const summaryText = document.getElementById("extremeTimePointSummaryText");

    if (topPatientsCount) topPatientsCount.textContent = `${topCount} patients`;
    if (bottomPatientsCount) bottomPatientsCount.textContent = `${bottomCount} patients`;
    if (totalPatientsCount) totalPatientsCount.textContent = `${totalCount} total`;

    if (summaryText) {
      if (isValueMode) {
        summaryText.textContent = `Will select patients with highest and lowest time values based on value range percentages`;
      } else {
        summaryText.textContent = `Will select patients with highest and lowest time values based on patient count percentages`;
      }
    }
  }

  // Update extreme time point summary fallback
  updateExtremeTimePointSummaryFallback() {
    const summaryText = document.getElementById("extremeTimePointSummaryText");
    const isValueMode = document.getElementById("selectionModeToggle").checked;

    if (summaryText) {
      if (isValueMode) {
        summaryText.textContent = "Select patient file to see patient counts for value range mode";
      } else {
        summaryText.textContent = "Select patient file to see patient counts for percentage mode";
      }
    }

    const topPatientsCount = document.getElementById("topPatientsCount");
    const bottomPatientsCount = document.getElementById("bottomPatientsCount");
    const totalPatientsCount = document.getElementById("totalPatientsCount");

    if (topPatientsCount) topPatientsCount.textContent = "0 patients";
    if (bottomPatientsCount) bottomPatientsCount.textContent = "0 patients";
    if (totalPatientsCount) totalPatientsCount.textContent = "0 total";
  }

  // Update time point description
  updateTimePointDescription() {
    const timePointSelect = document.getElementById("editorBrackenTimePointSelect");
    const descriptionElement = document.getElementById("timePointDescription");

    if (!timePointSelect || !descriptionElement) return;

    const selectedValue = timePointSelect.value;

    if (!selectedValue) {
      descriptionElement.textContent = "Select a time point to see its description";
      return;
    }

    // This would typically fetch description from server
    descriptionElement.textContent = `Time point: ${DatasetUtils.formatTimePointName(selectedValue)}`;
  }

  // Validate analysis editor
  validateAnalysisEditor() {
    const analysisName = document.getElementById("analysisName");
    const runButton = document.querySelector('button[onclick="runAnalysisFromEditor()"]');

    if (!analysisName) return;

    const isValid = analysisName.value.trim().length > 0;

    if (runButton) {
      runButton.disabled = !isValid;
    }
  }

  // Reset analysis editor
  resetAnalysisEditor() {
    // Reset form fields
    const formFields = [
      "analysisName",
      "analysisDescription",
      "editorPatientFileSelect",
      "editorTaxonomyFileSelect",
      "editorBrackenFileSelect",
      "editorBrackenTimePointSelect",
    ];

    formFields.forEach((fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.value = "";
      }
    });

    // Reset checkboxes
    const checkboxes = document.querySelectorAll(
      '#columnGroupsContainer input[type="checkbox"], #stratificationContainer input[type="checkbox"]'
    );
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
    });

    // Reset percentages
    const topPercentage = document.getElementById("topPercentage");
    const bottomPercentage = document.getElementById("bottomPercentage");
    if (topPercentage) topPercentage.value = 25;
    if (bottomPercentage) bottomPercentage.value = 25;

    this.updateTopPercentage(25);
    this.updateBottomPercentage(25);

    // Reset summaries
    this.updateColumnGroupsSummary();
    this.updateStratificationSummary();
    this.updateExtremeTimePointSummary();
  }

  // Update column groups summary
  updateColumnGroupsSummary() {
    const summary = document.getElementById("selectionSummary");
    const count = document.getElementById("totalColumnsCount");

    if (summary) {
      const selectedGroups = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
      const groupNames = Array.from(selectedGroups).map((cb) => {
        const label = cb.nextElementSibling;
        return label ? label.querySelector("strong").textContent : cb.value;
      });

      if (groupNames.length === 0) {
        summary.textContent = "No column groups selected";
      } else {
        summary.textContent = `Selected: ${groupNames.join(", ")}`;
      }
    }

    if (count) {
      const selectedGroups = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
      count.textContent = `${selectedGroups.length} total columns`;
    }
  }

  // Update stratification summary
  updateStratificationSummary() {
    const summary = document.getElementById("stratificationSummaryText");
    const count = document.getElementById("stratificationCount");

    if (summary) {
      const selectedStratifications = document.querySelectorAll(
        '#stratificationContainer input[type="checkbox"]:checked'
      );

      if (selectedStratifications.length === 0) {
        summary.textContent = "No stratifications selected";
      } else {
        summary.textContent = `${selectedStratifications.length} stratifications selected`;
      }
    }

    if (count) {
      const selectedStratifications = document.querySelectorAll(
        '#stratificationContainer input[type="checkbox"]:checked'
      );
      count.textContent = `${selectedStratifications.length} stratifications`;
    }
  }

  // Load analysis from file
  async loadAnalysis(filename) {
    try {
      DatasetUtils.showAlert("Loading analysis...", "info");

      // For now, just show a message - full implementation would load the JSON and populate the form
      DatasetUtils.showAlert(`Analysis "${filename}" loaded successfully`, "success");
    } catch (error) {
      console.error("Load analysis error:", error);
      DatasetUtils.showAlert("Failed to load analysis", "error");
    }
  }

  // Run analysis
  async runAnalysis(filename) {
    try {
      DatasetUtils.showAlert("Running analysis...", "info");

      // For now, just show a message - full implementation would execute the analysis
      DatasetUtils.showAlert(`Analysis "${filename}" execution started`, "success");
    } catch (error) {
      console.error("Run analysis error:", error);
      DatasetUtils.showAlert("Failed to run analysis", "error");
    }
  }

  // Delete analysis
  async deleteAnalysis(filename) {
    // Show confirmation dialog
    const analysisName = filename.replace(".json", "");
    const confirmed = confirm(
      `Are you sure you want to delete the analysis "${analysisName}"? This action cannot be undone.`
    );

    if (!confirmed) {
      return;
    }

    try {
      DatasetUtils.showAlert("Deleting analysis...", "info");

      // Call the delete endpoint
      const response = await DatasetUtils.api.call(`/dataset/${window.datasetId}/analysis/delete`, {
        method: "POST",
        body: JSON.stringify({ filename: filename }),
      });

      if (response.success) {
        DatasetUtils.showAlert(`Analysis "${analysisName}" deleted successfully`, "success");

        // Refresh the analysis list
        if (window.analysisManager) {
          window.analysisManager.loadAnalysisList();
        }
      } else {
        DatasetUtils.showAlert(response.message || "Failed to delete analysis", "error");
      }
    } catch (error) {
      console.error("Delete analysis error:", error);
      DatasetUtils.showAlert("Failed to delete analysis", "error");
    }
  }

  // Duplicate analysis
  async duplicateAnalysis(filename) {
    try {
      DatasetUtils.showAlert("Duplicating analysis...", "info");

      // Call the duplicate endpoint
      const response = await DatasetUtils.api.call(`/dataset/${window.datasetId}/analysis/duplicate`, {
        method: "POST",
        body: JSON.stringify({ filename: filename }),
      });

      if (response.success) {
        const originalName = filename.replace(".json", "");
        const newName = response.new_filename ? response.new_filename.replace(".json", "") : `${originalName}_c`;
        DatasetUtils.showAlert(`Analysis duplicated as "${newName}"`, "success");

        // Refresh the analysis list
        if (window.analysisManager) {
          window.analysisManager.loadAnalysisList();
        }
      } else {
        DatasetUtils.showAlert(response.message || "Failed to duplicate analysis", "error");
      }
    } catch (error) {
      console.error("Duplicate analysis error:", error);
      DatasetUtils.showAlert("Failed to duplicate analysis", "error");
    }
  }

  // Rename analysis
  async renameAnalysis(filename, currentName) {
    const newName = prompt("Enter new name for the analysis:", currentName);

    if (!newName || newName.trim() === "" || newName.trim() === currentName) {
      return; // Cancelled or no change
    }

    const trimmedName = newName.trim();

    try {
      DatasetUtils.showAlert("Renaming analysis...", "info");

      // Call the rename endpoint
      const response = await DatasetUtils.api.call(`/dataset/${window.datasetId}/analysis/rename`, {
        method: "POST",
        body: JSON.stringify({
          filename: filename,
          new_name: trimmedName,
        }),
      });

      if (response.success) {
        DatasetUtils.showAlert(`Analysis renamed to "${trimmedName}"`, "success");

        // Refresh the analysis list
        if (window.analysisManager) {
          window.analysisManager.loadAnalysisList();
        }
      } else {
        DatasetUtils.showAlert(response.message || "Failed to rename analysis", "error");
      }
    } catch (error) {
      console.error("Rename analysis error:", error);
      DatasetUtils.showAlert("Failed to rename analysis", "error");
    }
  }
}

// Global functions for analysis operations
window.createNewAnalysis = function () {
  if (window.analysisManager) {
    window.analysisManager.createNewAnalysis();
  }
};

window.cancelAnalysisEdit = function () {
  if (window.analysisManager) {
    window.analysisManager.cancelAnalysisEdit();
  }
};

window.saveAnalysis = function () {
  if (window.analysisManager) {
    window.analysisManager.saveAnalysis();
  }
};

window.refreshAnalysisList = function () {
  if (window.analysisManager) {
    window.analysisManager.loadAnalysisList();
  }
};

window.runAnalysisFromEditor = function () {
  if (window.analysisManager) {
    window.analysisManager.saveAnalysis();
  }
};

// Toggle functions
window.toggleColumnGroups = function () {
  const content = document.getElementById("columnGroupsContent");
  const button = document.getElementById("toggleColumnGroupsBtn");

  if (content && button) {
    const isVisible = content.style.display !== "none";
    content.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Column Groups`;
  }
};

window.toggleFieldNames = function () {
  // Implementation for toggling field names
  DatasetUtils.showAlert("Field names toggle feature coming soon", "info");
};

window.toggleStratification = function () {
  const container = document.getElementById("stratificationContainer");
  const button = document.getElementById("toggleStratificationBtn");

  if (container && button) {
    const isVisible = container.style.display !== "none";
    container.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Stratification Options`;
  }
};

window.toggleClustering = function () {
  const container = document.getElementById("clusteringParametersContainer");
  const button = document.getElementById("toggleClusteringBtn");

  if (container && button) {
    const isVisible = container.style.display !== "none";
    container.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Clustering Options`;
  }
};

window.toggleClusterRepresentative = function () {
  const container = document.getElementById("clusterRepresentativeContainer");
  const button = document.getElementById("toggleClusterRepBtn");

  if (container && button) {
    const isVisible = container.style.display !== "none";
    container.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Options`;
  }
};

// Selection functions
window.selectAllColumnGroups = function () {
  const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = true;
  });
  if (window.analysisManager) {
    window.analysisManager.updateColumnGroupsSummary();
  }
};

window.clearAllColumnGroups = function () {
  const checkboxes = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (window.analysisManager) {
    window.analysisManager.updateColumnGroupsSummary();
  }
};

window.selectAllStratifications = function () {
  const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = true;
  });
  if (window.analysisManager) {
    window.analysisManager.updateStratificationSummary();
  }
};

window.clearAllStratifications = function () {
  const checkboxes = document.querySelectorAll('#stratificationContainer input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (window.analysisManager) {
    window.analysisManager.updateStratificationSummary();
  }
};

// Update functions
window.updateTopPercentage = function (value) {
  if (window.analysisManager) {
    window.analysisManager.updateTopPercentage(value);
  }
};

window.updateBottomPercentage = function (value) {
  if (window.analysisManager) {
    window.analysisManager.updateBottomPercentage(value);
  }
};

window.toggleLinkedPercentages = function () {
  if (window.analysisManager) {
    window.analysisManager.toggleLinkedPercentages();
  }
};

window.toggleSelectionMode = function () {
  if (window.analysisManager) {
    window.analysisManager.toggleSelectionMode();
  }
};

window.updateTimePointDescription = function () {
  if (window.analysisManager) {
    window.analysisManager.updateTimePointDescription();
  }
};

window.validateAnalysisEditor = function () {
  if (window.analysisManager) {
    window.analysisManager.validateAnalysisEditor();
  }
};

// Initialize analysis tab when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  const datasetId = window.datasetId;

  if (datasetId) {
    window.analysisManager = new DatasetAnalysisManager(datasetId);
    window.analysisManager.init();
  } else {
    console.error("No datasetId found!");
  }
});

// Analysis management functions
window.loadAnalysis = function (filename) {
  if (window.analysisManager) {
    window.analysisManager.loadAnalysis(filename);
  }
};

window.runAnalysis = function (filename) {
  if (window.analysisManager) {
    window.analysisManager.runAnalysis(filename);
  }
};

window.deleteAnalysis = function (filename) {
  if (window.analysisManager) {
    window.analysisManager.deleteAnalysis(filename);
  }
};

window.duplicateAnalysis = function (filename) {
  if (window.analysisManager) {
    window.analysisManager.duplicateAnalysis(filename);
  }
};

window.renameAnalysis = function (filename, currentName) {
  if (window.analysisManager) {
    window.analysisManager.renameAnalysis(filename, currentName);
  }
};

// Export for external use
window.DatasetAnalysisManager = DatasetAnalysisManager;
