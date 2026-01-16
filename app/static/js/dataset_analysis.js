// Dataset Analysis Tab JavaScript
// Handles analysis creation, configuration, and management

class DatasetAnalysisManager {
  constructor(datasetId) {
    this.datasetId = datasetId;
    this.currentAnalysis = null;
    this.columnGroupsData = null;
    this.discardingPoliciesData = null;
  }

  // Initialize analysis tab
  async init() {
    this.setupEventListeners();
    await this.loadAnalysisList();
    await this.loadFilesForDataSources();
    await this.loadColumnGroups();
    await this.loadDiscardingPolicies();
    await this.loadMicrobialDiscardingPolicies();
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
      discardingPolicies: this.collectDiscardingPolicies(),
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

  // Collect discarding policies
  collectDiscardingPolicies() {
    const container = document.getElementById("discardingPolicyContainer");
    const selectedPolicies = {};

    if (container) {
      const policyCards = container.querySelectorAll('.discarding-policy-card');
      policyCards.forEach((card) => {
        const policyKey = card.dataset.policyKey;
        const enabledCheckbox = card.querySelector('input[type="checkbox"]');
        const parameters = {};

        // Collect parameter values
        const inputs = card.querySelectorAll('input, select');
        inputs.forEach((input) => {
          if (input.name && input.value !== "") {
            parameters[input.name] = input.value;
          }
        });

        selectedPolicies[policyKey] = {
          enabled: enabledCheckbox ? enabledCheckbox.checked : false,
          parameters: parameters
        };
      });
    }

    return selectedPolicies;
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

  // Load discarding policies
  async loadDiscardingPolicies() {
    try {
      const data = await DatasetUtils.api.call(`/dataset/${this.datasetId}/metadata/attribute-discarding`);

      if (data.success) {
        this.displayDiscardingPolicies(data.discarding_policies);
        this.discardingPoliciesData = data.discarding_policies;
      } else {
        this.showDiscardingPoliciesError(data.message);
      }
    } catch (error) {
      console.error("Failed to load discarding policies:", error);
      this.showDiscardingPoliciesError("Failed to load discarding policies");
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

  // Display discarding policies
  displayDiscardingPolicies(policies) {
    const container = document.getElementById("discardingPolicyContainer");

    if (!container) return;

    const policiesHTML = policies
      .map((policy) => {
        const parameterInputs = this.generateParameterInputs(policy.key, policy.parameters);
        const isEnabled = policy.enabled ? 'checked' : '';

        return `
                <div class="col-12 mb-4">
                    <div class="card discarding-policy-card" data-policy-key="${policy.key}">
                        <div class="card-header">
                            <div class="d-flex align-items-center justify-content-between">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="policy_${policy.key}" ${isEnabled}>
                                    <label class="form-check-label" for="policy_${policy.key}">
                                        ${policy.name}
                                        <small class="text-muted d-block">${policy.description}</small>
                                    </label>
                                </div>
                                <button type="button" class="btn btn-outline-info btn-sm" onclick="showDiscardingPolicyInfo('${policy.key}')">
                                    <i class="fas fa-info-circle me-1"></i>Info
                                </button>
                            </div>
                        </div>
                        <div class="card-body" id="policy_body_${policy.key}" style="display: ${policy.enabled ? 'block' : 'none'}">
                            <div class="row">
                                ${parameterInputs}
                            </div>
                        </div>
                    </div>
                </div>
            `;
      })
      .join("");

    container.innerHTML = policiesHTML;

    // Add event listeners for policy checkboxes
    policies.forEach((policy) => {
      const checkbox = document.getElementById(`policy_${policy.key}`);
      if (checkbox) {
        checkbox.addEventListener('change', () => this.togglePolicyBody(policy.key));
      }
    });

    this.updateDiscardingPolicySummary();
  }

  // Generate parameter inputs for a policy
  generateParameterInputs(policyKey, parameters) {
    return Object.entries(parameters)
      .map(([paramKey, paramConfig]) => {
        const inputId = `${policyKey}_${paramKey}`;
        const inputName = paramKey;
        let inputHTML = '';

        switch (paramConfig.type) {
          case 'float':
            inputHTML = `
                        <div class="col-md-6 mb-3">
                            <label for="${inputId}" class="form-label">${paramConfig.label}</label>
                            <input
                                type="number"
                                class="form-control"
                                id="${inputId}"
                                name="${inputName}"
                                value="${paramConfig.default}"
                                min="${paramConfig.min || ''}"
                                max="${paramConfig.max || ''}"
                                step="${paramConfig.step || 'any'}"
                            />
                            <div class="form-text">${paramConfig.description}</div>
                        </div>
                    `;
            break;
          case 'int':
            inputHTML = `
                        <div class="col-md-6 mb-3">
                            <label for="${inputId}" class="form-label">${paramConfig.label}</label>
                            <input
                                type="number"
                                class="form-control"
                                id="${inputId}"
                                name="${inputName}"
                                value="${paramConfig.default}"
                                min="${paramConfig.min || ''}"
                                max="${paramConfig.max || ''}"
                                step="${paramConfig.step || 1}"
                            />
                            <div class="form-text">${paramConfig.description}</div>
                        </div>
                    `;
            break;
          case 'select':
            const options = paramConfig.options
              .map(option => `<option value="${option.value}" ${option.value === paramConfig.default ? 'selected' : ''}>${option.label}</option>`)
              .join('');
            inputHTML = `
                        <div class="col-md-6 mb-3">
                            <label for="${inputId}" class="form-label">${paramConfig.label}</label>
                            <select class="form-select" id="${inputId}" name="${inputName}">
                                ${options}
                            </select>
                            <div class="form-text">${paramConfig.description}</div>
                        </div>
                    `;
            break;
        }

        return inputHTML;
      })
      .join("");
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

  // Show discarding policies error
  showDiscardingPoliciesError(message) {
    const container = document.getElementById("discardingPolicyContainer");
    if (container) {
      container.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Unable to load discarding policies:</strong> ${message}
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

    // Clear existing options except first (placeholder if exists)
    while (timePointSelect.children.length > 1) {
      timePointSelect.removeChild(timePointSelect.lastChild);
    }

    // Clear all existing options
    timePointSelect.innerHTML = '';

    // Add placeholder option
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select a Time Point...";
    placeholderOption.disabled = true;
    placeholderOption.selected = true;
    timePointSelect.appendChild(placeholderOption);

    // Initialize descriptions map
    this.timePointDescriptions = {};

    // Add time point options
    timePoints.forEach((timePoint, index) => {
      const option = document.createElement("option");
      option.value = timePoint.key;
      option.textContent = timePoint.title;

      // Store description
      this.timePointDescriptions[timePoint.key] = timePoint.description;

      // Set as selected if it's the default, otherwise don't select any by default
      if (defaultTimePoint && timePoint.key === defaultTimePoint) {
        option.selected = true;
      }

      timePointSelect.appendChild(option);
    });

    // Store the first option value for later
    if (timePoints.length > 0) {
      this.firstTimePointKey = timePoints[0].key;
    }


    // Update description - placeholder should be selected initially
    this.updateTimePointDescription();
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
      // When linked, update the other input and its display directly to avoid
      // calling the counterpart function which would create a recursive loop.
      const bottomPercentage = document.getElementById("bottomPercentage");
      const bottomPercentageValue = document.getElementById("bottomPercentageValue");
      if (bottomPercentage) {
        bottomPercentage.value = value;
      }
      if (bottomPercentageValue) {
        bottomPercentageValue.textContent = value + "%";
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
      // When linked, update the other input and its display directly to avoid
      // calling the counterpart function which would create a recursive loop.
      const topPercentage = document.getElementById("topPercentage");
      const topPercentageValue = document.getElementById("topPercentageValue");
      if (topPercentage) {
        topPercentage.value = value;
      }
      if (topPercentageValue) {
        topPercentageValue.textContent = value + "%";
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
    const descriptionElement = document.getElementById("timePointDescriptionText");

    if (!timePointSelect) return;

    const selectedValue = timePointSelect.value;

    // If description element exists, update it
    if (descriptionElement) {
      if (!selectedValue) {
        // Placeholder selected - show no description
        descriptionElement.textContent = "";
        return;
      }

      // Show the description of the selected time point
      const description = this.timePointDescriptions[selectedValue];
      descriptionElement.textContent = description || DatasetUtils.formatTimePointName(selectedValue);
    }

    // No longer disabling the first option - all options should remain selectable
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

    // Reset discarding policy checkboxes and hide bodies
    const discardingCheckboxes = document.querySelectorAll('#discardingPolicyContainer input[type="checkbox"]');
    discardingCheckboxes.forEach((checkbox) => {
      checkbox.checked = false;
      const policyKey = checkbox.id.replace('policy_', '');
      const body = document.getElementById(`policy_body_${policyKey}`);
      if (body) {
        body.style.display = 'none';
      }
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
    this.updateDiscardingPolicySummary();
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

  // Update discarding policy summary
  updateDiscardingPolicySummary() {
    const summary = document.getElementById("discardingPolicySummaryText");
    const count = document.getElementById("totalDiscardingPoliciesCount");

    if (summary) {
      const enabledPolicies = document.querySelectorAll('#discardingPolicyContainer input[type="checkbox"]:checked');

      if (enabledPolicies.length === 0) {
        summary.textContent = "No discarding policies configured";
      } else {
        const policyNames = Array.from(enabledPolicies).map((cb) => {
          const label = cb.nextElementSibling;
          const strongElement = label ? label.querySelector("strong") : null;
          return strongElement ? strongElement.textContent : (label ? label.textContent : "Unknown policy");
        });
        summary.textContent = `Enabled: ${policyNames.join(", ")}`;
      }
    }

    if (count) {
      const enabledPolicies = document.querySelectorAll('#discardingPolicyContainer input[type="checkbox"]:checked');
      count.textContent = `${enabledPolicies.length} policies`;
    }
  }

  // Toggle policy body visibility
  togglePolicyBody(policyKey) {
    const checkbox = document.getElementById(`policy_${policyKey}`);
    const body = document.getElementById(`policy_body_${policyKey}`);

    if (checkbox && body) {
      body.style.display = checkbox.checked ? 'block' : 'none';
    }

    this.updateDiscardingPolicySummary();
  }

  // Load microbial discarding policies
  async loadMicrobialDiscardingPolicies() {
    try {
      const data = await DatasetUtils.api.call(`/dataset/${this.datasetId}/metadata/microbial-discarding`);

      if (data.success) {
        this.displayMicrobialDiscardingPolicies(data.discarding_policies);
        this.microbialDiscardingPoliciesData = data.discarding_policies;
      } else {
        this.showMicrobialDiscardingPoliciesError(data.message);
      }
    } catch (error) {
      console.error("Failed to load microbial discarding policies:", error);
      this.showMicrobialDiscardingPoliciesError("Failed to load microbial discarding policies");
    }
  }

  // Display microbial discarding policies
  displayMicrobialDiscardingPolicies(policies) {
    const container = document.getElementById("microbialDiscardingPolicyContainer");

    if (!container) return;

    const policiesHTML = policies
      .map((policy) => {
        const parameterInputs = this.generateParameterInputs(policy.key, policy.parameters);
        const isEnabled = policy.enabled ? 'checked' : '';

        return `
                <div class="col-12 mb-4">
                    <div class="card microbial-discarding-policy-card" data-policy-key="${policy.key}">
                        <div class="card-header">
                            <div class="d-flex align-items-center justify-content-between">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="microbial_policy_${policy.key}" ${isEnabled}>
                                    <label class="form-check-label" for="microbial_policy_${policy.key}">
                                        ${policy.name}
                                        <small class="text-muted d-block">${policy.description}</small>
                                    </label>
                                </div>
                                <button type="button" class="btn btn-outline-info btn-sm" onclick="showMicrobialDiscardingPolicyInfo('${policy.key}')">
                                    <i class="fas fa-info-circle me-1"></i>Info
                                </button>
                            </div>
                        </div>
                        <div class="card-body" id="microbial_policy_body_${policy.key}" style="display: ${policy.enabled ? 'block' : 'none'}">
                            <div class="row">
                                ${parameterInputs}
                            </div>
                        </div>
                    </div>
                </div>
            `;
      })
      .join("");

    container.innerHTML = policiesHTML;

    // Add event listeners for policy checkboxes
    policies.forEach((policy) => {
      const checkbox = document.getElementById(`microbial_policy_${policy.key}`);
      if (checkbox) {
        checkbox.addEventListener('change', () => this.toggleMicrobialPolicyBody(policy.key));
      }
    });

    this.updateMicrobialDiscardingPolicySummary();
  }

  // Show microbial discarding policies error
  showMicrobialDiscardingPoliciesError(message) {
    const container = document.getElementById("microbialDiscardingPolicyContainer");
    if (container) {
      container.innerHTML = `
        <div class="col-12">
          <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
          </div>
        </div>
      `;
    }
  }

  // Update microbial discarding policy summary
  updateMicrobialDiscardingPolicySummary() {
    const summary = document.getElementById("microbialDiscardingPolicySummaryText");
    const count = document.getElementById("totalMicrobialDiscardingPoliciesCount");

    if (summary) {
      const enabledPolicies = document.querySelectorAll('#microbialDiscardingPolicyContainer input[type="checkbox"]:checked');

      if (enabledPolicies.length === 0) {
        summary.textContent = "No microbial discarding policies configured";
      } else {
        const policyNames = Array.from(enabledPolicies).map((cb) => {
          const label = cb.nextElementSibling;
          const strongElement = label ? label.querySelector("strong") : null;
          return strongElement ? strongElement.textContent : (label ? label.textContent : "Unknown policy");
        });
        summary.textContent = `Enabled: ${policyNames.join(", ")}`;
      }
    }

    if (count) {
      const enabledPolicies = document.querySelectorAll('#microbialDiscardingPolicyContainer input[type="checkbox"]:checked');
      count.textContent = `${enabledPolicies.length} policies`;
    }
  }

  // Toggle microbial policy body visibility
  toggleMicrobialPolicyBody(policyKey) {
    const checkbox = document.getElementById(`microbial_policy_${policyKey}`);
    const body = document.getElementById(`microbial_policy_body_${policyKey}`);

    if (checkbox && body) {
      body.style.display = checkbox.checked ? 'block' : 'none';
    }

    this.updateMicrobialDiscardingPolicySummary();
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

window.toggleDiscardingPolicy = function () {
  const content = document.getElementById("discardingPolicyContent");
  const button = document.getElementById("toggleDiscardingPolicyBtn");

  if (content && button) {
    const isVisible = content.style.display !== "none";
    content.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Policies`;
  }
};

window.toggleMicrobialDiscardingPolicy = function () {
  const content = document.getElementById("microbialDiscardingPolicyContent");
  const button = document.getElementById("toggleMicrobialDiscardingPolicyBtn");

  if (content && button) {
    const isVisible = content.style.display !== "none";
    content.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Policies`;
  }
};

window.calculateRemainingAttributes = async function () {
  try {
    const response = await DatasetUtils.api.call(`/dataset/${window.datasetId}/metadata/attribute-discarding/calculate-remaining`, {
      method: "POST"
    });

    if (response.success) {
      DatasetUtils.showAlert("Remaining attributes calculated successfully", "success");
    } else {
      DatasetUtils.showAlert(response.message, "info");
    }
  } catch (error) {
    console.error("Calculate remaining attributes error:", error);
    DatasetUtils.showAlert("Failed to calculate remaining attributes", "error");
  }
};

window.calculateRemainingMicrobes = async function () {
  try {
    const response = await DatasetUtils.api.call(`/dataset/${window.datasetId}/metadata/microbial-discarding/calculate-remaining`, {
      method: "POST"
    });

    if (response.success) {
      DatasetUtils.showAlert("Remaining microbial taxa calculated successfully", "success");
    } else {
      DatasetUtils.showAlert(response.message, "info");
    }
  } catch (error) {
    console.error("Calculate remaining microbes error:", error);
    DatasetUtils.showAlert("Failed to calculate remaining microbial taxa", "error");
  }
};

window.showDiscardingPolicyInfo = function (policyKey) {
  const policyInfo = getDiscardingPolicyInfo(policyKey);
  if (policyInfo) {
    showPolicyInfoModal(policyInfo);
  }
};

window.showMicrobialDiscardingPolicyInfo = function (policyKey) {
  const policyInfo = getMicrobialDiscardingPolicyInfo(policyKey);
  if (policyInfo) {
    showPolicyInfoModal(policyInfo);
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
  // #region agent log - hypothesis G: Window wrapper called
  fetch('http://127.0.0.1:7243/ingest/5860f252-044a-4785-9428-d425c09f65f7',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'dataset_analysis.js:window.updateTimePointDescription',message:'Window wrapper called',data:{analysisManagerExists:!!window.analysisManager,hasUpdateMethod:!!(window.analysisManager && window.analysisManager.updateTimePointDescription)},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'G'})}).catch(()=>{});
  // #endregion

  if (window.analysisManager && typeof window.analysisManager.updateTimePointDescription === 'function') {
    // #region agent log - hypothesis G: Calling analysis manager method
    fetch('http://127.0.0.1:7243/ingest/5860f252-044a-4785-9428-d425c09f65f7',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'dataset_analysis.js:window.updateTimePointDescription',message:'Calling analysis manager updateTimePointDescription',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'G'})}).catch(()=>{});
    // #endregion
    window.analysisManager.updateTimePointDescription();
  } else {
    // #region agent log - hypothesis G: Analysis manager method not available
    fetch('http://127.0.0.1:7243/ingest/5860f252-044a-4785-9428-d425c09f65f7',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'dataset_analysis.js:window.updateTimePointDescription',message:'Analysis manager or method not available',data:{managerExists:!!window.analysisManager,methodExists:!!(window.analysisManager && window.analysisManager.updateTimePointDescription)},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'G'})}).catch(()=>{});
    // #endregion
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

// Helper functions for discarding policy info
function getDiscardingPolicyInfo(policyKey) {
  const policyDetails = {
    'prevalence_filtering': {
      title: 'Prevalence Filtering',
      description: 'Discard taxa present in fewer than a specified percentage of samples, removing unreliable measurements.',
      algorithm: 'For each taxon: prevalence = (abundance > detection_threshold).sum() / total_samples; if prevalence < min_prevalence_threshold: discard_taxon',
      parameters: [
        { name: 'Detection threshold', default: '>0', description: 'Minimum abundance to consider taxon present' },
        { name: 'Minimum prevalence', default: '10% of samples', description: 'Minimum fraction of samples where taxon must be present' }
      ],
      pros: [
        'Data quality control - Eliminates measurement artifacts and rare taxa',
        'Statistical reliability - Focuses on consistently detectable microbes',
        'Computational efficiency - Reduces dataset size significantly',
        'Reproducibility - Removes taxa with unreliable abundance estimates',
        'Simple implementation - Easy to understand and apply'
      ],
      cons: [
        'May discard important taxa - Some biologically relevant microbes may be rare',
        'Arbitrary thresholds - Prevalence cutoff is subjective',
        'Context dependence - Optimal prevalence varies by study design and technology',
        'False negatives - Rare pathogens or keystone species may be excluded'
      ],
      limitations: [
        'Doesn\'t consider abundance levels, only presence/absence',
        'May be too conservative for some research questions',
        'Threshold selection requires biological knowledge'
      ],
      expectations: 'Reduces taxa count by 20-60%, depending on threshold'
    },
    'abundance_filtering': {
      title: 'Abundance Filtering',
      description: 'Discard taxa with consistently low abundance across samples, focusing on ecologically important microbes.',
      algorithm: 'For each taxon: mean_abundance = taxon_abundances.mean(); median_abundance = taxon_abundances.median(); if mean_abundance < min_mean_threshold or median_abundance < min_median_threshold: discard_taxon',
      parameters: [
        { name: 'Minimum mean abundance', default: '0.01% relative abundance', description: 'Minimum mean relative abundance threshold' },
        { name: 'Minimum median abundance', default: '0.005% relative abundance', description: 'Minimum median relative abundance threshold' }
      ],
      pros: [
        'Ecological relevance - Focuses on microbes that contribute meaningfully to community',
        'Measurement precision - Removes taxa near detection limits',
        'Biological signal - Prioritizes microbes with functional impact',
        'Data normalization - Complements relative abundance transformations',
        'Statistical power - Reduces noise in downstream analyses'
      ],
      cons: [
        'Context dependence - Abundance thresholds vary by sample type and technology',
        'Functional bias - May exclude important low-abundance functional specialists',
        'Normalization effects - Results depend on abundance transformation method',
        'Sample variability - Abundance distributions vary across studies'
      ],
      limitations: [
        'Requires appropriate abundance normalization (relative abundance, CLR, etc.)',
        'May miss conditionally abundant taxa (bloomers under specific conditions)',
        'Thresholds need validation against biological knowledge'
      ],
      expectations: 'Further reduces taxa count by 10-40%, depending on thresholds'
    },
    'variance_based_selection': {
      title: 'Variance-Based Selection',
      description: 'Select taxa with highest variance across samples, identifying microbes that differ between patients or conditions.',
      algorithm: 'For each taxon: variance = taxon_abundances.var(); coefficient_of_variation = variance / mean_abundance; rank_taxa_by_variance(); select_top_n_most_variable()',
      parameters: [
        { name: 'Number of taxa to select', default: '50', description: 'Maximum number of most variable taxa to retain' },
        { name: 'Variance metric', default: 'Coefficient of Variation', description: 'Method to measure taxon variability' }
      ],
      pros: [
        'Biological heterogeneity - Identifies taxa that vary between individuals',
        'Condition differences - Captures microbes that change with disease states',
        'Data-driven - No biological assumptions required',
        'Quality indicator - High variance suggests reliable measurements',
        'Exploratory power - Reveals major sources of microbiome variation'
      ],
      cons: [
        'No clinical relevance - Doesn\'t consider relationship to outcomes',
        'Noise sensitivity - Technical variation can inflate variance',
        'Scale dependence - Affected by abundance transformations',
        'Arbitrary selection - "Top N" is subjective',
        'Context ignorance - May select taxa varying for non-biological reasons'
      ],
      limitations: [
        'Doesn\'t distinguish biological from technical variation',
        'Rare taxa may appear highly variable due to sparsity',
        'Selection depends on study population characteristics'
      ],
      expectations: 'Selects 20-100 most variable taxa from the microbial group'
    },
    'univariate_pfs_screening': {
      title: 'Univariate PFS Screening',
      description: 'Test each taxon individually against PFS using statistical models, keeping only those showing significant associations.',
      algorithm: 'For each taxon: model = fit_statistical_model(pfs_outcomes, taxon_abundance); if p_value < significance_threshold: keep_taxon',
      parameters: [
        { name: 'Statistical test', default: 'Cox Regression', description: 'Method for testing PFS association' },
        { name: 'Significance threshold', default: 'p < 0.05', description: 'P-value threshold for significance' },
        { name: 'Multiple testing correction', default: 'FDR', description: 'Method to correct for multiple hypothesis testing' }
      ],
      pros: [
        'Direct clinical relevance - Only keeps taxa associated with outcomes',
        'Statistical rigor - Formal hypothesis testing for each taxon',
        'Easy interpretation - Clear inclusion criteria',
        'Biological insight - Reveals which microbes matter for disease progression',
        'Flexible thresholds - Can adjust stringency based on study goals'
      ],
      cons: [
        'Ignores interactions - May miss taxa significant only in combination',
        'Multiple testing issues - Risk of false positives without correction',
        'Conservative approach - May exclude taxa with weak individual effects',
        'Sample size dependence - Power varies with number of events',
        'Context independence - Doesn\'t account for clinical covariates'
      ],
      limitations: [
        'Requires sufficient PFS events for statistical power',
        'May miss synergistic effects between taxa',
        'Results sensitive to censoring patterns'
      ],
      expectations: 'Retains 5-30% of taxa showing PFS associations'
    },
    'multivariate_pfs_screening': {
      title: 'Multivariate PFS Screening',
      description: 'Test taxa in multivariate models including clinical variables, selecting those significant after adjusting for confounders.',
      algorithm: 'Fit full multivariate model: PFS ~ clinical_vars + all_taxa; Extract significant taxa (p < 0.05 after clinical adjustment)',
      parameters: [
        { name: 'Significance threshold', default: 'p < 0.05', description: 'P-value threshold for significance after clinical adjustment' },
        { name: 'Regularization strength', default: '0.1', description: 'Penalty strength for numerical stability' },
        { name: 'Maximum iterations', default: '10', description: 'Maximum iterations for iterative refinement' },
        { name: 'Minimum taxa to retain', default: '5', description: 'Minimum number of taxa to keep for model stability' }
      ],
      pros: [
        'Clinically realistic - Considers clinical context and confounding',
        'Context-aware - Identifies taxa significant beyond clinical factors',
        'Multivariate validity - Accounts for taxon intercorrelations',
        'Clinical translation - Results relevant for patient stratification',
        'Confounding control - Adjusts for known clinical predictors'
      ],
      cons: [
        'Computational intensity - Requires fitting large multivariate models',
        'Parameter instability - Large models can be numerically unstable',
        'Clinical variable dependence - Results depend on which covariates are included',
        'Overfitting risk - Too many taxa relative to sample size',
        'Interpretation complexity - Hard to attribute effects to individual taxa'
      ],
      limitations: [
        'Requires sufficient sample size for multivariate model stability',
        'Sensitive to multicollinearity between taxa and clinical variables',
        'Clinical covariate selection affects which taxa appear significant'
      ],
      expectations: 'Retains 3-15 taxa significant in multivariate clinical context'
    },
    'stability_selection': {
      title: 'Stability Selection',
      description: 'Use bootstrap resampling to identify taxa with consistently significant PFS associations across multiple subsamples.',
      algorithm: 'For each bootstrap sample: fit PFS model; calculate stability scores based on consistency across bootstraps; select taxa above stability threshold',
      parameters: [
        { name: 'Number of bootstraps', default: '100', description: 'Number of bootstrap samples for stability assessment' },
        { name: 'Stability threshold', default: '0.7', description: 'Minimum fraction of bootstraps where taxon must be significant' },
        { name: 'Bootstrap sample size', default: '80%', description: 'Fraction of original sample size for each bootstrap' }
      ],
      pros: [
        'Robust identification - Finds consistently associated taxa',
        'Controls overfitting - Reduces false positive selections',
        'Uncertainty quantification - Provides confidence in selections',
        'Cross-validation built-in - Bootstrap validation of associations',
        'Sample variability - Accounts for population heterogeneity'
      ],
      cons: [
        'Computationally expensive - Requires many model fits',
        'Time-intensive - May take hours for large taxon sets',
        'Parameter dependence - Stability threshold affects results',
        'Conservative bias - May miss taxa with moderate associations'
      ],
      limitations: [
        'Requires sufficient sample size for meaningful bootstrapping',
        'Assumes bootstrap samples represent population characteristics',
        'May be overly conservative for small datasets',
        'Computational cost scales with number of taxa'
      ],
      expectations: 'Identifies 5-20 taxa with high stability scores (70%+ consistency)'
    },
    'information_theoretic_selection': {
      title: 'Information-Theoretic Selection',
      description: 'Select taxa based on mutual information with PFS outcomes, capturing non-linear and complex relationships.',
      algorithm: 'For each taxon: calculate mutual information I(taxon_abundance; pfs_outcome); test significance against null distribution',
      parameters: [
        { name: 'Mutual information estimator', default: 'K-Nearest Neighbors', description: 'Method for estimating mutual information' },
        { name: 'Number of permutations', default: '1000', description: 'Number of permutations for significance testing' },
        { name: 'Significance threshold', default: 'p < 0.05', description: 'P-value threshold for significance' }
      ],
      pros: [
        'Non-linear relationships - Captures complex taxon-PFS associations',
        'No distribution assumptions - Works with any abundance distribution',
        'Information-theoretic foundation - Solid theoretical basis',
        'Model independence - Doesn\'t assume specific relationship form',
        'Robust to outliers - Less sensitive to extreme values'
      ],
      cons: [
        'Computational cost - Especially for continuous variables',
        'Estimator sensitivity - Results depend on binning or k parameter',
        'Limited interpretability - MI scores don\'t indicate relationship direction',
        'Multiple testing - Requires careful correction for many taxa'
      ],
      limitations: [
        'Requires sufficient sample size for reliable MI estimation',
        'Sensitive to discretization parameters for continuous variables',
        'Doesn\'t provide effect size or relationship direction',
        'May select redundant taxa with similar information content'
      ],
      expectations: 'Selects 10-40 taxa with significant information shared with PFS'
    },
    'boruta_algorithm': {
      title: 'Boruta Algorithm',
      description: 'Iterative algorithm using random forest to identify all features with predictive relevance, not just the strongest ones.',
      algorithm: 'Add shadow features; train random forest; compare real vs shadow feature importance; iteratively remove features less important than best shadow',
      parameters: [
        { name: 'Shadow features per real feature', default: '3', description: 'Number of randomized shadow features to create' },
        { name: 'Maximum iterations', default: '100', description: 'Maximum iterations for Boruta algorithm' },
        { name: 'Random forest trees', default: '1000', description: 'Number of trees in random forest' }
      ],
      pros: [
        'All-relevant selection - Finds all predictive taxa, not just top performers',
        'Statistical foundation - Uses permutation testing for significance',
        'Handles correlations - Works well with correlated microbial features',
        'Robust to overfitting - Ensemble method reduces variance',
        'No parameter tuning - Algorithm determines optimal feature set'
      ],
      cons: [
        'Computationally intensive - Multiple random forest trainings',
        'Time-consuming - May take significant time for large datasets',
        'Memory intensive - Random forest objects for each iteration',
        'Random forest dependence - Results depend on RF implementation',
        'May be overly inclusive - Includes marginally relevant features'
      ],
      limitations: [
        'Requires sufficient sample size for stable random forest importance',
        'May be conservative in small datasets',
        'Computational requirements may be prohibitive for very large feature sets'
      ],
      expectations: 'Selects 15-50 taxa with confirmed predictive relevance'
    },
    'elastic_net_regularization': {
      title: 'Elastic Net Regularization',
      description: 'Use L1/L2 regularized regression to automatically select taxa with PFS predictive value through coefficient shrinkage.',
      algorithm: 'Optimize elastic net: minimize loss + λ₁||β||₁ + λ₂||β||₂; select taxa with non-zero coefficients',
      parameters: [
        { name: 'L1 ratio', default: '0.5', description: 'Balance between L1 (0) and L2 (1) regularization' },
        { name: 'Maximum iterations', default: '1000', description: 'Maximum iterations for optimization' },
        { name: 'Convergence tolerance', default: '1e-4', description: 'Tolerance for convergence in optimization' }
      ],
      pros: [
        'Automated selection - No manual threshold setting required',
        'Handles correlations - L2 component manages multicollinear taxa',
        'Continuous selection - Gradual elimination rather than hard cutoffs',
        'Cross-validation built-in - Automatic parameter optimization',
        'Predictive focus - Selects for outcome prediction performance'
      ],
      cons: [
        'Model dependence - Results depend on chosen base model',
        'Linear assumptions - Assumes linear relationships for selection',
        'Parameter sensitivity - Regularization balance affects results',
        'May miss weak signals - Conservative selection approach',
        'Computational cost - Especially for large feature sets'
      ],
      limitations: [
        'Requires specification of base regression model',
        'Selection depends on regularization parameter choice',
        'May not capture non-linear taxon-PFS relationships',
        'Cross-validation can be computationally expensive'
      ],
      expectations: 'Selects 5-25 taxa with non-zero coefficients in regularized model'
    },
    'combined_multi_method': {
      title: 'Combined Multi-Method Selection',
      description: 'Apply multiple selection methods and take consensus to identify robustly selected taxa.',
      algorithm: 'Apply multiple methods; take intersection/union/weighted consensus of selected taxa',
      parameters: [
        { name: 'Consensus rule', default: 'Intersection', description: 'How to combine results from multiple methods' },
        { name: 'Minimum agreement', default: '2', description: 'Minimum number of methods that must agree' }
      ],
      pros: [
        'Robust selection - Taxa selected by multiple methods are more reliable',
        'Method validation - Cross-validation of different approaches',
        'Comprehensive coverage - Captures different types of associations',
        'Uncertainty reduction - Reduces method-specific biases',
        'Confidence building - Multiple lines of evidence for selected taxa'
      ],
      cons: [
        'Computational cost - Running multiple methods increases time',
        'Result complexity - Different methods may give different answers',
        'Decision complexity - Choosing how to combine results',
        'Conservative bias - Strict consensus may miss valid taxa',
        'Method dependence - Results depend on which methods are combined'
      ],
      limitations: [
        'Requires careful consideration of which methods to combine',
        'Consensus rules are somewhat arbitrary',
        'May miss taxa only detectable by specific methods',
        'Interpretation becomes more complex'
      ],
      expectations: 'Highly confident selection of 5-20 taxa supported by multiple methods'
    }
  };

  return policyDetails[policyKey];
}

function getMicrobialDiscardingPolicyInfo(policyKey) {
  const policyDetails = {
    'prevalence_filtering': {
      title: 'Prevalence Filtering',
      description: 'Discard microbial taxa present in fewer than a specified percentage of samples, removing unreliable measurements.',
      algorithm: 'For each taxon: prevalence = (abundance > detection_threshold).sum() / total_samples; if prevalence < min_prevalence_threshold: discard_taxon',
      parameters: [
        { name: 'Detection threshold', default: '>0', description: 'Minimum abundance to consider taxon present' },
        { name: 'Minimum prevalence', default: '10% of samples', description: 'Minimum fraction of samples where taxon must be present' }
      ],
      pros: [
        'Data quality control - Eliminates measurement artifacts and rare taxa',
        'Statistical reliability - Focuses on consistently detectable microbes',
        'Computational efficiency - Reduces dataset size significantly',
        'Reproducibility - Removes taxa with unreliable abundance estimates',
        'Simple implementation - Easy to understand and apply'
      ],
      cons: [
        'May discard important taxa - Some biologically relevant microbes may be rare',
        'Arbitrary thresholds - Prevalence cutoff is subjective',
        'Context dependence - Optimal prevalence varies by study design and technology',
        'False negatives - Rare pathogens or keystone species may be excluded'
      ],
      limitations: [
        'Doesn\'t consider abundance levels, only presence/absence',
        'May be too conservative for some research questions',
        'Threshold selection requires biological knowledge'
      ],
      expectations: 'Reduces taxa count by 20-60%, depending on threshold'
    },
    'abundance_filtering': {
      title: 'Abundance Filtering',
      description: 'Discard taxa with consistently low abundance across samples, focusing on ecologically important microbes.',
      algorithm: 'For each taxon: mean_abundance = taxon_abundances.mean(); median_abundance = taxon_abundances.median(); if mean_abundance < min_mean_threshold or median_abundance < min_median_threshold: discard_taxon',
      parameters: [
        { name: 'Minimum mean abundance', default: '0.01% relative abundance', description: 'Minimum mean relative abundance threshold' },
        { name: 'Minimum median abundance', default: '0.005% relative abundance', description: 'Minimum median relative abundance threshold' }
      ],
      pros: [
        'Ecological relevance - Focuses on microbes that contribute meaningfully to community',
        'Measurement precision - Removes taxa near detection limits',
        'Biological signal - Prioritizes microbes with functional impact',
        'Data normalization - Complements relative abundance transformations',
        'Statistical power - Reduces noise in downstream analyses'
      ],
      cons: [
        'Context dependence - Abundance thresholds vary by sample type and technology',
        'Functional bias - May exclude important low-abundance functional specialists',
        'Normalization effects - Results depend on abundance transformation method',
        'Sample variability - Abundance distributions vary across studies'
      ],
      limitations: [
        'Arbitrary thresholds - No universal abundance cutoff exists',
        'Scale dependence - Results vary with sequencing depth and technology',
        'Biological context - Some low-abundance taxa are functionally important'
      ],
      expectations: 'Reduces taxa count by 30-70%, depending on threshold and sample type'
    },
    'taxonomic_rarity_filtering': {
      title: 'Taxonomic Rarity Filtering',
      description: 'Filter out rare taxa that appear in very few samples regardless of abundance, focusing on consistently detectable microbes.',
      algorithm: 'For each taxon: sample_count = number of samples with abundance > detection_threshold; if sample_count < min_sample_count: discard_taxon',
      parameters: [
        { name: 'Minimum sample count', default: '3 samples', description: 'Minimum number of samples where taxon must be detected' },
        { name: 'Rarity threshold', default: '1% of samples', description: 'Maximum proportion of samples where rare taxa are allowed' }
      ],
      pros: [
        'Conservative approach - Ensures taxa are consistently detectable',
        'Measurement reliability - Focuses on taxa with multiple measurements',
        'Statistical stability - Reduces variance from sporadic detections',
        'Quality control - Removes potential contamination artifacts',
        'Simple and transparent - Easy to understand and communicate'
      ],
      cons: [
        'May be too conservative - Excludes biologically relevant rare taxa',
        'Context dependence - Appropriate thresholds vary by study size',
        'Sample size bias - Larger studies can retain rarer taxa',
        'Technology dependence - Detection limits vary by sequencing platform'
      ],
      limitations: [
        'Doesn\'t consider ecological importance of rare taxa',
        'May exclude important low-prevalence pathogens',
        'Threshold selection is somewhat arbitrary'
      ],
      expectations: 'Reduces taxa count by 15-40%, depending on study size and detection threshold'
    },
    'low_abundance_taxa_removal': {
      title: 'Low Abundance Taxa Removal',
      description: 'Remove taxa that never exceed a specified abundance threshold in any sample, focusing on potentially impactful microbes.',
      algorithm: 'For each taxon: max_abundance = maximum abundance across all samples; if max_abundance < max_abundance_threshold: discard_taxon; keep top N most abundant taxa regardless',
      parameters: [
        { name: 'Maximum abundance threshold', default: '0.1% relative abundance', description: 'Taxa exceeding this threshold in any sample will be retained' },
        { name: 'Keep top N taxa', default: '100 taxa', description: 'Always retain the N most abundant taxa regardless of threshold' }
      ],
      pros: [
        'Ecological focus - Prioritizes microbes that can dominate communities',
        'Functional relevance - High abundance often correlates with ecological impact',
        'Data quality - Removes taxa consistently near detection limits',
        'Computational efficiency - Significantly reduces dataset size',
        'Biological plausibility - Low abundance taxa may be ecologically irrelevant'
      ],
      cons: [
        'May exclude important taxa - Some functional specialists are low abundance',
        'Context dependence - Abundance thresholds vary by ecosystem',
        'Detection limit bias - Results depend on sequencing technology sensitivity',
        'Temporal variability - Abundance peaks may be missed in sampling'
      ],
      limitations: [
        'Assumes abundance correlates with importance',
        'May miss rare but ecologically important taxa',
        'Threshold selection requires ecological knowledge'
      ],
      expectations: 'Reduces taxa count by 40-80%, depending on threshold and ecosystem'
    },
    'contaminant_filtering': {
      title: 'Contaminant Filtering',
      description: 'Remove potential contaminants based on prevalence in negative controls, ensuring data quality.',
      algorithm: 'For each taxon: control_prevalence = prevalence in negative controls; control_abundance = mean abundance in controls; if control_prevalence > threshold or control_abundance > threshold: discard_taxon',
      parameters: [
        { name: 'Control prevalence threshold', default: '50% of controls', description: 'Maximum prevalence allowed in negative controls' },
        { name: 'Control abundance threshold', default: '1% relative abundance', description: 'Maximum abundance allowed in negative controls' }
      ],
      pros: [
        'Data quality assurance - Removes laboratory contamination artifacts',
        'Experimental validity - Ensures microbial signal is biological, not technical',
        'Reproducibility - Standardizes contamination removal across studies',
        'Method validation - Uses experimental controls for quality control',
        'Publication standards - Meets rigorous microbiome data quality requirements'
      ],
      cons: [
        'Requires controls - Not applicable without negative control samples',
        'Control quality dependence - Results depend on control sample quality',
        'Conservative approach - May remove true low-level contaminants',
        'Control variability - Different labs may have different contamination profiles'
      ],
      limitations: [
        'Limited to studies with proper negative controls',
        'May not detect all contamination types',
        'Control contamination may not reflect sample contamination'
      ],
      expectations: 'Removes 5-20% of taxa, depending on laboratory and sequencing conditions'
    },
    'singleton_filtering': {
      title: 'Singleton Filtering',
      description: 'Remove taxa that appear as singletons (detected in only one sample), reducing potential artifacts.',
      algorithm: 'For each taxon: detection_count = number of samples with abundance > detection_threshold; if detection_count == 1: apply singleton strategy',
      parameters: [
        { name: 'Singleton removal strategy', default: 'Strict removal', description: 'How to handle taxa detected in only one sample' },
        { name: 'Singleton abundance threshold', default: '1% relative abundance', description: 'Minimum abundance to retain singletons (for lenient mode)' }
      ],
      pros: [
        'Artifact removal - Eliminates likely sequencing or PCR errors',
        'Data quality - Focuses on consistently detectable taxa',
        'Statistical reliability - Removes highly variable singleton measurements',
        'Computational stability - Reduces noise in diversity calculations',
        'Biological plausibility - Singletons may represent contamination'
      ],
      cons: [
        'May remove real taxa - Some microbes are legitimately rare',
        'Overly conservative - Excludes potentially important low-prevalence taxa',
        'Detection limit dependence - Results vary with sequencing sensitivity',
        'Biological context ignored - All singletons treated equally'
      ],
      limitations: [
        'Doesn\'t distinguish between true rarity and artifacts',
        'May exclude important rare biosphere members',
        'Threshold for "singleton" may not be biologically meaningful'
      ],
      expectations: 'Removes 10-30% of taxa, depending on sequencing depth and technology'
    },
    'variance_based_selection': {
      title: 'Variance-Based Selection',
      description: 'Select taxa with highest variance across samples, focusing on microbes that vary between conditions.',
      algorithm: 'For each taxon: calculate variance metric (total variance or coefficient of variation); rank taxa by variance; select top N most variable taxa',
      parameters: [
        { name: 'Number of taxa to select', default: '50 taxa', description: 'Maximum number of most variable taxa to retain' },
        { name: 'Variance metric', default: 'Coefficient of variation', description: 'Method to measure taxon variability' }
      ],
      pros: [
        'Biological relevance - Variable taxa often respond to environmental changes',
        'Differential abundance focus - Prioritizes taxa that differ between groups',
        'Statistical power - Variable taxa are easier to detect as significant',
        'Ecological insight - Highlights taxa involved in community dynamics',
        'Data-driven approach - Uses empirical variability patterns'
      ],
      cons: [
        'May select noise - High variance doesn\'t always indicate biological signal',
        'Context dependence - Important taxa may be consistently present',
        'Scale dependence - Variance depends on abundance transformation',
        'Confounding factors - Variance may reflect technical rather than biological factors'
      ],
      limitations: [
        'Assumes variable taxa are more important',
        'May miss consistently important taxa',
        'Variance calculation sensitive to outliers'
      ],
      expectations: 'Selects 50-200 most variable taxa, depending on desired subset size'
    },
    'taxonomic_level_filtering': {
      title: 'Taxonomic Level Filtering',
      description: 'Filter taxa based on their taxonomic classification level, ensuring reliable taxonomic assignment.',
      algorithm: 'For each taxon: check taxonomic classification depth; if classification level < min_required_level: discard_taxon',
      parameters: [
        { name: 'Minimum taxonomic level', default: 'Genus level', description: 'Require taxa to be classified at least to this level' },
        { name: 'Unclassified taxa handling', default: 'Remove all unclassified', description: 'How to handle taxa without complete classification' }
      ],
      pros: [
        'Taxonomic reliability - Ensures taxa are properly identified',
        'Comparative analysis - Enables cross-study comparisons',
        'Biological interpretation - Provides meaningful taxonomic context',
        'Database quality - Reflects quality of taxonomic reference database',
        'Standardization - Creates consistent taxonomic resolution across studies'
      ],
      cons: [
        'Resolution loss - May exclude taxa only identifiable to higher levels',
        'Database dependence - Results vary with classification database quality',
        'Biological information loss - Higher-level taxa may be ecologically relevant',
        'Conservative approach - May be too restrictive for some analyses'
      ],
      limitations: [
        'Depends on reference database completeness',
        'May exclude novel or poorly characterized taxa',
        'Arbitrary level cutoffs may not reflect biological reality'
      ],
      expectations: 'Retains 60-90% of taxa, depending on classification database and required level'
    },
    'core_microbiome_filtering': {
      title: 'Core Microbiome Filtering',
      description: 'Retain only taxa that are part of the core microbiome, focusing on consistently present microbes.',
      algorithm: 'For each taxon: calculate prevalence across all samples; if prevalence >= core_prevalence_threshold and mean_abundance >= core_abundance_threshold: retain_taxon',
      parameters: [
        { name: 'Core prevalence threshold', default: '80% of samples', description: 'Minimum prevalence to be considered core microbiome' },
        { name: 'Core abundance threshold', default: '1% relative abundance', description: 'Minimum abundance to be considered core microbiome' }
      ],
      pros: [
        'Ecological stability - Focuses on consistently present community members',
        'Functional importance - Core taxa often perform essential ecosystem functions',
        'Comparative studies - Enables cross-sample and cross-study comparisons',
        'Biological relevance - Core microbiome represents stable community structure',
        'Robust analysis - Less sensitive to sampling variability'
      ],
      cons: [
        'Context dependence - Core microbiome varies by ecosystem and condition',
        'Temporal variability - Core taxa may change over time',
        'Definition ambiguity - No universal definition of "core"',
        'May miss important variable taxa - Focuses on presence, not change'
      ],
      limitations: [
        'Arbitrary thresholds for core definition',
        'May exclude ecologically important but variable taxa',
        'Core composition changes with environmental conditions'
      ],
      expectations: 'Retains 10-30 core taxa, depending on ecosystem and thresholds'
    },
    'combined_microbial_selection': {
      title: 'Combined Microbial Selection',
      description: 'Apply multiple microbial selection methods and take consensus to identify robustly selected taxa.',
      algorithm: 'Apply multiple methods independently; combine results using specified consensus rule; retain taxa selected by consensus',
      parameters: [
        { name: 'Consensus rule', default: 'Intersection (ALL methods)', description: 'How to combine results from multiple methods' },
        { name: 'Minimum agreement', default: '2 methods', description: 'Minimum number of methods that must agree (for weighted voting)' }
      ],
      pros: [
        'Robust selection - Taxa selected by multiple methods are more reliable',
        'Method validation - Cross-validation of different filtering approaches',
        'Comprehensive evaluation - Considers multiple data quality aspects',
        'Uncertainty reduction - Reduces method-specific biases',
        'Confidence building - Multiple lines of evidence for retained taxa'
      ],
      cons: [
        'Computational cost - Running multiple methods increases processing time',
        'Result complexity - Different methods may give conflicting results',
        'Decision complexity - Choosing appropriate consensus rule',
        'Conservative bias - Strict consensus may miss valid taxa',
        'Method dependence - Results depend on which methods are combined'
      ],
      limitations: [
        'Requires careful selection of complementary methods',
        'Consensus rules are somewhat subjective',
        'May miss taxa only detectable by specific approaches',
        'Interpretation becomes more complex with multiple criteria'
      ],
      expectations: 'Highly confident retention of 20-50 taxa supported by multiple quality criteria'
    }
  };

  return policyDetails[policyKey];
}

function showPolicyInfoModal(policyInfo) {
  // Create modal HTML
  const modalHTML = `
    <div class="modal fade" id="policyInfoModal" tabindex="-1" aria-labelledby="policyInfoModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="policyInfoModalLabel">
              <i class="fas fa-info-circle text-info me-2"></i>${policyInfo.title}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6>Description</h6>
              <p class="text-muted">${policyInfo.description}</p>
            </div>

            <div class="mb-3">
              <h6>Algorithm</h6>
              <code class="d-block p-2 bg-light rounded">${policyInfo.algorithm}</code>
            </div>

            <div class="mb-3">
              <h6>Parameters</h6>
              <ul class="list-group list-group-flush">
                ${policyInfo.parameters.map(param => `
                  <li class="list-group-item px-0">
                    <strong>${param.name}</strong> (default: ${param.default})
                    <br><small class="text-muted">${param.description}</small>
                  </li>
                `).join('')}
              </ul>
            </div>

            <div class="row">
              <div class="col-md-6">
                <h6 class="text-success">✓ Pros</h6>
                <ul class="list-unstyled">
                  ${policyInfo.pros.map(pro => `<li class="mb-1"><i class="fas fa-check text-success me-2"></i>${pro}</li>`).join('')}
                </ul>
              </div>
              <div class="col-md-6">
                <h6 class="text-danger">✗ Cons</h6>
                <ul class="list-unstyled">
                  ${policyInfo.cons.map(con => `<li class="mb-1"><i class="fas fa-times text-danger me-2"></i>${con}</li>`).join('')}
                </ul>
              </div>
            </div>

            <div class="mt-3">
              <h6 class="text-warning">⚠ Limitations</h6>
              <ul class="list-unstyled">
                ${policyInfo.limitations.map(limit => `<li class="mb-1"><i class="fas fa-exclamation-triangle text-warning me-2"></i>${limit}</li>`).join('')}
              </ul>
            </div>

            <div class="mt-3 p-3 bg-info bg-opacity-10 rounded">
              <h6 class="text-info mb-2"><i class="fas fa-chart-bar me-2"></i>Expected Results</h6>
              <p class="mb-0">${policyInfo.expectations}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Remove existing modal if present
  const existingModal = document.getElementById('policyInfoModal');
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to body
  document.body.insertAdjacentHTML('beforeend', modalHTML);

  // Show modal
  const modal = new bootstrap.Modal(document.getElementById('policyInfoModal'));
  modal.show();

  // Clean up modal when hidden
  document.getElementById('policyInfoModal').addEventListener('hidden.bs.modal', function () {
    this.remove();
  });
}
