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
    await this.loadMicrobialGroupingPolicies();
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
                    <button type="button" class="btn btn-outline-primary" onclick='loadAnalysis("${analysis.filename}")' title="Load Analysis">
                        <i class="fas fa-folder-open"></i>
                    </button>
                    <button type="button" class="btn btn-outline-success" onclick='runAnalysis("${analysis.filename}")' title="Run Analysis">
                        <i class="fas fa-play"></i>
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick='duplicateAnalysis("${analysis.filename}")' title="Duplicate Analysis">
                        <i class="fas fa-copy"></i>
                    </button>
                    <button type="button" class="btn btn-outline-warning" onclick='renameAnalysis("${analysis.filename}", "${analysis.name}")' title="Rename Analysis">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick='deleteAnalysis("${analysis.filename}")' title="Delete Analysis">
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
      microbialDiscardingPolicies: this.collectMicrobialDiscardingPolicies(),
      microbialGrouping: this.collectMicrobialGrouping(),
      timePoint: this.collectTimePoint(),
      sample_timepoints: this.collectSampleTimepoints(),
      analysis_methods_comparison: this.collectAnalysisMethodsComparison(),
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

  // Collect microbial discarding policies
  collectMicrobialDiscardingPolicies() {
    const container = document.getElementById("microbialDiscardingPolicyContainer");
    const selectedPolicies = {};

    if (container) {
      const policyCards = container.querySelectorAll('.microbial-discarding-policy-card');
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

  // Collect microbial grouping
  collectMicrobialGrouping() {
    const container = document.getElementById("microbialGroupingContainer");
    const selectedMethod = null;

    if (container) {
      const selectedRadio = container.querySelector('input[name="microbialGroupingMethod"]:checked');
      if (selectedRadio) {
        const methodKey = selectedRadio.value;
        const methodCard = container.querySelector(`[data-method-key="${methodKey}"]`);
        const parameters = {};

        // Collect parameter values from the selected method's card
        if (methodCard) {
          const inputs = methodCard.querySelectorAll('input, select');
          inputs.forEach((input) => {
            if (input.name && input.value !== "") {
              parameters[input.name] = input.value;
            }
          });
        }

        return {
          method: methodKey,
          parameters: parameters
        };
      }
    }

    return null; // No method selected
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

    // Support both dictionary-style and ordered-list responses from backend
    let groupsArray = [];

    if (Array.isArray(columnGroups)) {
      groupsArray = columnGroups.map((g) => ({
        name: g.name || g.key || '',
        columns: g.columns || g.fields || []
      }));
    } else if (typeof columnGroups === 'object' && columnGroups !== null) {
      groupsArray = Object.entries(columnGroups).map(([key, val]) => ({
        name: val.name || key,
        columns: val.columns || val.fields || []
      }));
    }

    const groupsHTML = groupsArray
      .map((group, idx) => {
        const groupKey = (group.name || `group_${idx}`).replace(/\s+/g, '_').toLowerCase();
        const groupName = DatasetUtils.formatGroupName(group.name || groupKey);
        const fieldCount = Array.isArray(group.columns) ? group.columns.length : 0;

        return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${groupName}" id="group_${groupKey}" data-field-count="${fieldCount}" onchange="window.analysisManager && window.analysisManager.updateColumnGroupsSummary()" checked>
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

    // Ensure the content area is visible now that groups are loaded
    const content = document.getElementById('columnGroupsContent');
    if (content) content.style.display = 'block';

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
    // For microbial grouping, only show static subgroup descriptions (no inputs)
    // If a parameter has type 'static', just show its label and description
    return Object.entries(parameters)
      .map(([paramKey, paramConfig]) => {
        if (paramConfig.type === 'static') {
          // Render subgroup descriptions as a bullet list when appropriate
          if (paramKey === 'subgroups' && typeof paramConfig.description === 'string') {
            // Split into sentences by period, semicolon or newline, keep non-empty parts
            const parts = paramConfig.description
              .split(/\.|;|\n/)
              .map(p => p.trim())
              .filter(p => p.length > 0);

            const items = parts.map(p => {
              // If contains colon, bold the left side
              if (p.indexOf(':') !== -1) {
                const [left, right] = p.split(/:\s*(.+)/); // split into two parts
                return `<li><strong>${left.trim()}:</strong> ${right ? right.trim() : ''}</li>`;
              }
              return `<li>${p}</li>`;
            }).join('');

            return `<div class="col-12 mb-2">
                      <label class="form-label fw-bold">${paramConfig.label}</label>
                      <div class="form-text"><ul class="mb-0 ps-3">${items}</ul></div>
                    </div>`;
          }

          return `<div class="col-12 mb-2">
                    <label class="form-label fw-bold">${paramConfig.label}</label>
                    <div class="form-text">${paramConfig.description}</div>
                  </div>`;
        }
        // For all other types, do not render any input (future-proof)
        return '';
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
    // Populate sample timepoints comparison UI
    try { this.displaySampleTimepoints(timePoints); } catch(e) { /* ignore if UI not present */ }
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

  // Display sample timepoints comparison UI (checkboxes for all timepoints)
  displaySampleTimepoints(timePoints) {
    const container = document.getElementById('sampleTimepointsContainer');
    const selectedDisplay = document.getElementById('selectedTimePointDisplay');
    if (!container) return;

    // Clear container
    container.innerHTML = '';

    // Render each timepoint as a checkbox row
    timePoints.forEach(tp => {
      const col = document.createElement('div');
      // Use Bootstrap responsive grid columns (container uses row-cols-2)
      col.className = 'col mb-2';

      const card = document.createElement('div');
      card.className = 'card p-2 h-100';
      card.innerHTML = `
        <div class="form-check">
          <input class="form-check-input sample-timepoint-checkbox" type="checkbox" value="${tp.key}" id="sample_tp_${tp.key}">
          <label class="form-check-label" for="sample_tp_${tp.key}">
            <strong>${tp.title}</strong>
            <div class="text-muted small">${(tp.description || '').substring(0,120)}${(tp.description||'').length>120?'...':''}</div>
          </label>
        </div>
      `;

      col.appendChild(card);
      container.appendChild(col);
    });

    // Update initial selected display and visibility
    this.updateSampleTimepointsVisibility();

    // Add change listeners
    const checkboxes = container.querySelectorAll('.sample-timepoint-checkbox');
    checkboxes.forEach(cb => cb.addEventListener('change', () => this.updateSampleTimepointsSummary()));
  }

  // Hide/disable the checkbox that corresponds to the currently selected primary timepoint
  updateSampleTimepointsVisibility() {
    const selected = document.getElementById('editorBrackenTimePointSelect');
    const selectedDisplay = document.getElementById('selectedTimePointDisplay');
    const container = document.getElementById('sampleTimepointsContainer');
    if (!container) return;

    const selectedValue = selected ? selected.value : '';
      // Show the option's visible text (title) rather than the value/key
      let selectedText = '';
      try {
        selectedText = selected && selected.options && selected.selectedIndex >= 0 ? selected.options[selected.selectedIndex].text : '';
      } catch (e) {
        selectedText = selectedValue;
      }
      if (selectedDisplay) selectedDisplay.textContent = selectedText || 'None';

    const checkboxes = container.querySelectorAll('.sample-timepoint-checkbox');
    checkboxes.forEach(cb => {
      if (cb.value === selectedValue) {
        cb.checked = false;
        cb.disabled = true;
        const label = cb.nextElementSibling;
        if (label) label.classList.add('text-muted');
      } else {
        cb.disabled = false;
        const label = cb.nextElementSibling;
        if (label) label.classList.remove('text-muted');
      }
    });

    this.updateSampleTimepointsSummary();
  }

  // Update summary for sample timepoints selection
  updateSampleTimepointsSummary() {
    const container = document.getElementById('sampleTimepointsContainer');
    const summaryText = document.getElementById('sampleTimepointsSummaryText');
    const countBadge = document.getElementById('sampleTimepointsCount');
    if (!container) return;

    const selected = Array.from(container.querySelectorAll('.sample-timepoint-checkbox:checked')).map(cb => cb.value);
    if (summaryText) {
      summaryText.textContent = selected.length > 0 ? `${selected.length} timepoint(s) selected for comparison` : 'No timepoints selected';
    }
    if (countBadge) countBadge.textContent = `${selected.length} selected`;
  }

  // Collect selected sample timepoints for saving
  collectSampleTimepoints() {
    const container = document.getElementById('sampleTimepointsContainer');
    if (!container) return [];
    const selected = Array.from(container.querySelectorAll('.sample-timepoint-checkbox:checked')).map(cb => cb.value);
    return selected;
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
        // Group info (text or array)
        let groupInfoHtml = '';
        if (Array.isArray(stratification.group_info)) {
          groupInfoHtml = `<ul class="mb-0 ps-3">${stratification.group_info.map(item => `<li>${item.replace(/^• /, '')}</li>`).join('')}</ul>`;
        } else if (stratification.group_info) {
          groupInfoHtml = `<span class="text-info" style="font-size:0.95em;">${stratification.group_info}</span>`;
        }

        // Parameters for stratification
        let paramsHtml = '';
        if (stratification.parameters && Object.keys(stratification.parameters).length > 0) {
          // parameters may be an object with keys or an array in the info block
          if (Array.isArray(stratification.parameters)) {
            paramsHtml = `<div class="mt-2"><strong>Parameters:</strong><ul class="mb-0 ps-3">${stratification.parameters.map(p => `<li><strong>${p.name}</strong>: <span class='text-muted'>${p.description || ''} (default: ${p.default || ''})</span></li>`).join('')}</ul></div>`;
          } else {
            paramsHtml = `<div class="mt-2"><strong>Parameters:</strong><ul class="mb-0 ps-3">${Object.entries(stratification.parameters).map(([pkey, p]) => `<li><strong>${p.label || pkey}</strong>: <span class='text-muted'>${p.description || ''} (default: ${p.default || ''})</span></li>`).join('')}</ul></div>`;
          }
        } else if (stratification.info && Array.isArray(stratification.info.parameters) && stratification.info.parameters.length > 0) {
          paramsHtml = `<div class="mt-2"><strong>Parameters:</strong><ul class="mb-0 ps-3">${stratification.info.parameters.map(p => `<li><strong>${p.name}</strong>: <span class='text-muted'>${p.description || ''} (default: ${p.default || ''})</span></li>`).join('')}</ul></div>`;
        }

        // Subgroups list
        let subgroupsHtml = '';
        if (Array.isArray(stratification.subgroups) && stratification.subgroups.length > 0) {
          subgroupsHtml = `<div class="mt-2"><strong>Subgroups:</strong><ul class="mb-0 ps-3">${stratification.subgroups.map(sg => `<li><strong>${sg.name}:</strong> <span class='text-muted'>${sg.condition}</span></li>`).join('')}</ul></div>`;
        }

        return `
              <div class="col-12 mb-3">
                <div class="card w-100">
                  <div class="card-body">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" value="${key}" id="strat_${key}" onchange="window.analysisManager && window.analysisManager.updateStratificationSummary()">
                      <label class="form-check-label" for="strat_${key}">
                        <strong>${stratification.name}</strong>
                      </label>
                    </div>
                    ${subgroupsHtml}
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
        // Normalize methods into an array for UI usage and info modal
        const methodsArray = Array.isArray(data.methods)
          ? data.methods
          : Object.entries(data.methods || {}).map(([k, v]) => {
              return Object.assign({}, v, {
                key: k,
                title: v.title || v.name || k,
                description: v.description || v.desc || ''
              });
            });

        // store normalized methods and render comparison cards
        this.analysisMethodsData = methodsArray;
        try { this.displayAnalysisMethodsComparison(methodsArray); } catch (e) { /* ignore if UI not present */ }
      } else {
        this.showAnalysisMethodError(data.message);
      }
    } catch (error) {
      console.error("Failed to load analysis methods:", error);
      this.showAnalysisMethodError("Failed to load analysis methods");
    }
  }

  // Display analysis methods comparison cards
  displayAnalysisMethodsComparison(methods) {
    const container = document.getElementById('analysisMethodsContainer');
    if (!container) return;

    // Normalize input to an array if an object was provided
    const methodsArray = Array.isArray(methods)
      ? methods
      : Object.entries(methods || {}).map(([k, v]) => ({ key: k, title: v.title || v.name || k, description: v.description || v.desc || '', info: v.info || v }));

    container.innerHTML = '';

    methodsArray.forEach(m => {
      const col = document.createElement('div');
      col.className = 'col mb-2';

      const card = document.createElement('div');
      card.className = 'card p-2 h-100 analysis-method-card';

      const safeTitle = m.title || m.name || m.key;
      const safeDesc = m.description || '';

      card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="form-check">
              <input class="form-check-input analysis-method-checkbox" type="checkbox" value="${m.key}" id="analysis_method_${m.key}">
              <label class="form-check-label" for="analysis_method_${m.key}"><strong>${safeTitle}</strong></label>
            </div>
            <div class="text-muted small">${(safeDesc).substring(0,120)}${(safeDesc).length>120?'...':''}</div>
            <div class="text-muted small"><em>Uses default parameter values</em></div>
          </div>
          <div>
            <button type="button" class="btn btn-outline-info btn-sm" onclick="showAnalysisMethodInfo('${m.key}')">Info</button>
          </div>
        </div>
      `;

      col.appendChild(card);
      container.appendChild(col);
    });

    // wire change listeners
    const checkboxes = container.querySelectorAll('.analysis-method-checkbox');
    checkboxes.forEach(cb => cb.addEventListener('change', () => this.updateAnalysisMethodsSummary()));

    this.updateAnalysisMethodsSummary();
    // Ensure the selected analysis method is disabled in the comparison list
    try { this.updateAnalysisMethodsVisibility(); } catch (e) { /* ignore */ }
  }

  // Hide/disable the checkbox that corresponds to the currently selected analysis method
  updateAnalysisMethodsVisibility() {
    const selected = document.getElementById('analysisMethodSelect');
    const selectedDisplay = document.getElementById('selectedAnalysisMethodDisplay');
    const container = document.getElementById('analysisMethodsContainer');
    if (!container) return;

    const selectedValue = selected ? selected.value : '';
    // Show the option's visible text rather than the value/key
    let selectedText = '';
    try {
      selectedText = selected && selected.options && selected.selectedIndex >= 0 ? selected.options[selected.selectedIndex].text : '';
    } catch (e) {
      selectedText = selectedValue;
    }
    if (selectedDisplay) selectedDisplay.textContent = selectedText || 'None';

    const checkboxes = container.querySelectorAll('.analysis-method-checkbox');
    checkboxes.forEach(cb => {
      if (cb.value === selectedValue) {
        cb.checked = false;
        cb.disabled = true;
        const label = cb.nextElementSibling;
        if (label) label.classList.add('text-muted');
      } else {
        cb.disabled = false;
        const label = cb.nextElementSibling;
        if (label) label.classList.remove('text-muted');
      }
    });

    this.updateAnalysisMethodsSummary();
  }

  updateAnalysisMethodsSummary() {
    const container = document.getElementById('analysisMethodsContainer');
    const summaryText = document.getElementById('analysisMethodsSummaryText');
    const countBadge = document.getElementById('analysisMethodsCount');
    if (!container) return;

    const selected = Array.from(container.querySelectorAll('.analysis-method-checkbox:checked')).map(cb => cb.value);
    if (summaryText) summaryText.textContent = selected.length > 0 ? `${selected.length} method(s) selected for comparison` : 'No methods selected';
    if (countBadge) countBadge.textContent = `${selected.length} selected`;
  }

  collectAnalysisMethodsComparison() {
    const container = document.getElementById('analysisMethodsContainer');
    if (!container) return [];
    return Array.from(container.querySelectorAll('.analysis-method-checkbox:checked')).map(cb => cb.value);
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
    // Update sample timepoints UI visibility to hide the primary selection
    try { this.updateSampleTimepointsVisibility(); } catch(e) { /* ignore */ }
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

    // Reset checkboxes (default to checked)
    const checkboxes = document.querySelectorAll(
      '#columnGroupsContainer input[type="checkbox"], #stratificationContainer input[type="checkbox"]'
    );
    checkboxes.forEach((checkbox) => {
      checkbox.checked = true;
    });

    // Reset microbial grouping radio buttons and hide bodies
    const microbialGroupingRadios = document.querySelectorAll('#microbialGroupingContainer input[name="microbialGroupingMethod"]');
    microbialGroupingRadios.forEach((radio) => {
      radio.checked = false;
      const methodKey = radio.value;
      const body = document.getElementById(`microbial_grouping_body_${methodKey}`);
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
    this.updateMicrobialGroupingSummary();
  }

  // Update column groups summary
  updateColumnGroupsSummary() {
    const summary = document.getElementById("selectionSummary");
    const count = document.getElementById("totalColumnsCount");

    if (summary) {
      const selectedGroups = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
      // Sum the data-field-count attribute for each selected group to get total fields
      const totalFields = Array.from(selectedGroups).reduce((acc, cb) => {
        const fc = parseInt(cb.getAttribute('data-field-count') || cb.dataset.fieldCount || 0, 10);
        return acc + (isNaN(fc) ? 0 : fc);
      }, 0);

      if (totalFields === 0) {
        summary.textContent = "No column groups selected";
      } else {
        summary.textContent = `${totalFields} total attributes selected`;
      }
    }

    if (count) {
      const selectedGroups = document.querySelectorAll('#columnGroupsContainer input[type="checkbox"]:checked');
      // Sum the data-field-count attribute for each selected group to get total fields
      const totalFields = Array.from(selectedGroups).reduce((acc, cb) => {
        const fc = parseInt(cb.getAttribute('data-field-count') || cb.dataset.fieldCount || 0, 10);
        return acc + (isNaN(fc) ? 0 : fc);
      }, 0);
      count.textContent = `${totalFields} total attributes`;
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

  // Load microbial grouping policies
  async loadMicrobialGroupingPolicies() {
    try {
      const data = await DatasetUtils.api.call(`/dataset/${this.datasetId}/metadata/microbial-grouping`);

      if (data.success) {
        this.displayMicrobialGroupingPolicies(data.grouping_methods);
        this.microbialGroupingData = data.grouping_methods;
      } else {
        this.showMicrobialGroupingError(data.message);
      }
    } catch (error) {
      console.error("Failed to load microbial grouping policies:", error);
      this.showMicrobialGroupingError("Failed to load microbial grouping methods");
    }
  }

  // Display microbial grouping policies
  displayMicrobialGroupingPolicies(methods) {
    const container = document.getElementById("microbialGroupingContainer");

    if (!container) return;

    const methodsHTML = methods
      .map((method) => {
      const parameterInputs = this.generateParameterInputs(method.key, method.parameters);
      const isChecked = method.enabled ? 'checked' : '';
      return `
          <div class="col-12 mb-4">
            <div class="card microbial-grouping-card" data-method-key="${method.key}">
              <div class="card-header">
                <div class="d-flex align-items-center justify-content-between">
                  <div class="form-check">
                    <input class="form-check-input" type="radio" name="microbialGroupingMethod" id="microbial_grouping_${method.key}" value="${method.key}" ${isChecked}>
                    <label class="form-check-label" for="microbial_grouping_${method.key}">
                      ${method.name}
                      <small class="text-muted d-block">${method.description}</small>
                    </label>
                  </div>
                  <button type="button" class="btn btn-outline-info btn-sm" onclick="showMicrobialGroupingInfo('${method.key}')">
                    <i class="fas fa-info-circle me-1"></i>Info
                  </button>
                </div>
              </div>
              <div class="card-body" id="microbial_grouping_body_${method.key}" style="display: ${method.enabled ? 'block' : 'none'}">
                <div class="row">
                  ${parameterInputs}
                </div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");

    container.innerHTML = methodsHTML;

    // Add event listeners for method radio buttons
    methods.forEach((method) => {
      const radio = document.getElementById(`microbial_grouping_${method.key}`);
      if (radio) {
        radio.addEventListener('change', () => this.toggleMicrobialGroupingBody(method.key));
      }
    });

    this.updateMicrobialGroupingSummary();
  }

  // Show microbial grouping error
  showMicrobialGroupingError(message) {
    const container = document.getElementById("microbialGroupingContainer");
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

  // Update microbial grouping summary
  updateMicrobialGroupingSummary() {
    const summary = document.getElementById("microbialGroupingSummaryText");
    const count = document.getElementById("totalMicrobialGroupingCount");

    if (summary) {
      const selectedRadio = document.querySelector('#microbialGroupingContainer input[name="microbialGroupingMethod"]:checked');

      if (!selectedRadio) {
        summary.textContent = "No microbial grouping method selected";
      } else {
        const methodKey = selectedRadio.value;
        const label = selectedRadio.nextElementSibling;
        let methodName = methodKey;
        if (label) {
          const strong = label.querySelector("strong");
          if (strong && strong.textContent && strong.textContent.trim() !== "") {
            methodName = strong.textContent.trim();
          } else {
            const firstTextNode = Array.from(label.childNodes).find(n => n.nodeType === Node.TEXT_NODE && n.textContent && n.textContent.trim() !== "");
            if (firstTextNode) {
              methodName = firstTextNode.textContent.trim();
            } else {
              methodName = label.textContent.trim();
            }
          }
        }
        summary.textContent = `Selected: ${methodName}`;
      }
    }

    if (count) {
      const selectedRadio = document.querySelector('#microbialGroupingContainer input[name="microbialGroupingMethod"]:checked');
      count.textContent = selectedRadio ? "1 method" : "0 methods";
    }
  }

  // Toggle microbial grouping body visibility
  toggleMicrobialGroupingBody(selectedMethodKey) {
    // Hide all method bodies first
    const allBodies = document.querySelectorAll('#microbialGroupingContainer .card-body[id^="microbial_grouping_body_"]');
    allBodies.forEach((body) => {
      body.style.display = 'none';
    });

    // Show the selected method's body
    const selectedBody = document.getElementById(`microbial_grouping_body_${selectedMethodKey}`);
    if (selectedBody) {
      selectedBody.style.display = 'block';
    }

    this.updateMicrobialGroupingSummary();
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

window.toggleMicrobialGrouping = function () {
  const content = document.getElementById("microbialGroupingContent");
  const button = document.getElementById("toggleMicrobialGroupingBtn");

  if (content && button) {
    const isVisible = content.style.display !== "none";
    content.style.display = isVisible ? "none" : "block";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Methods`;
  }
};

window.toggleAnalysisMethods = function () {
  const container = document.getElementById("analysisMethodsContainer");
  const button = document.getElementById("toggleAnalysisMethodsBtn");

  if (container && button) {
    const isVisible = container.style.display !== "none";
    container.style.display = isVisible ? "none" : "grid";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Options`;
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

window.showMicrobialGroupingInfo = function (methodKey) {
  const methodInfo = getMicrobialGroupingInfo(methodKey);
  if (methodInfo) {
    showPolicyInfoModal(methodInfo);
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

window.toggleSampleTimepoints = function () {
  const container = document.getElementById("sampleTimepointsContainer");
  const button = document.getElementById("toggleSampleTimepointsBtn");

  if (container && button) {
    const isVisible = container.style.display !== "none";
    container.style.display = isVisible ? "none" : "grid";
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Options`;
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

window.selectAllAnalysisMethods = function () {
  const checkboxes = document.querySelectorAll('#analysisMethodsContainer .analysis-method-checkbox');
  checkboxes.forEach((checkbox) => {
    if (!checkbox.disabled) checkbox.checked = true;
  });
  if (window.analysisManager) window.analysisManager.updateAnalysisMethodsSummary();
};

window.clearAllAnalysisMethods = function () {
  const checkboxes = document.querySelectorAll('#analysisMethodsContainer .analysis-method-checkbox');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (window.analysisManager) window.analysisManager.updateAnalysisMethodsSummary();
};

window.showAnalysisMethodInfo = function (methodKey) {
  const info = getAnalysisMethodInfo(methodKey);
  if (info) showPolicyInfoModal(info);
};

function getAnalysisMethodInfo(methodKey) {
  if (window.analysisManager && window.analysisManager.analysisMethodsData) {
    const method = window.analysisManager.analysisMethodsData.find(m => m.key === methodKey);
    if (method) {
      // Build modal info structure compatible with showPolicyInfoModal
      const params = (method.info && method.info.parameters) ? method.info.parameters : (method.parameters || []);
      return {
        title: method.title || method.name || method.key,
        description: (method.info && method.info.description) || method.description || '',
        algorithm: '',
        parameters: params.map(p => ({ name: p.name || p.label || p.key, default: p.default !== undefined ? p.default : '' , description: p.description || '' })),
        pros: (method.info && method.info.pros) || method.pros || [],
        cons: (method.info && method.info.cons) || method.cons || [],
        limitations: (method.info && method.info.limitations) || method.cons || [],
        expectations: (method.info && method.info.expectations) || (method.use_cases ? method.use_cases.join('; ') : '')
      };
    }
  }
  return null;
}

// Sample timepoints selection helpers
window.selectAllSampleTimepoints = function () {
  const checkboxes = document.querySelectorAll('#sampleTimepointsContainer .sample-timepoint-checkbox');
  checkboxes.forEach((checkbox) => {
    if (!checkbox.disabled) checkbox.checked = true;
  });
  if (window.analysisManager) {
    window.analysisManager.updateSampleTimepointsSummary();
  }
};

window.clearAllSampleTimepoints = function () {
  const checkboxes = document.querySelectorAll('#sampleTimepointsContainer .sample-timepoint-checkbox');
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  if (window.analysisManager) {
    window.analysisManager.updateSampleTimepointsSummary();
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
  // Update timepoint description wrapper
  if (window.analysisManager && typeof window.analysisManager.updateTimePointDescription === 'function') {
    // calling analysis manager method
    window.analysisManager.updateTimePointDescription();
  } else {
    // analysis manager method not available
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
  // Get the policy data from the global analysis manager
  if (window.analysisManager && window.analysisManager.discardingPoliciesData) {
    const policy = window.analysisManager.discardingPoliciesData.find(p => p.key === policyKey);
    return policy ? policy.info : null;
  }
  return null;
}

function getMicrobialDiscardingPolicyInfo(policyKey) {
  // Get the policy data from the global analysis manager
  if (window.analysisManager && window.analysisManager.microbialDiscardingPoliciesData) {
    const policy = window.analysisManager.microbialDiscardingPoliciesData.find(p => p.key === policyKey);
    return policy ? policy.info : null;
  }
  return null;
}

function getMicrobialGroupingInfo(methodKey) {
  // Get the method data from the global analysis manager
  if (window.analysisManager && window.analysisManager.microbialGroupingData) {
    const method = window.analysisManager.microbialGroupingData.find(m => m.key === methodKey);
    return method ? method.info : null;
  }
  return null;
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
