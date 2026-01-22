// Dataset Analysis Tab JavaScript
// Handles analysis creation, configuration, and management

class DatasetAnalysisManager {
  constructor(datasetId) {
    this.datasetId = datasetId;
    this.currentAnalysis = null;
    this.columnGroupsData = null;
    this.discardingPoliciesData = null;
    this.previousSelectedPostAnalysisKey = null; // Track previously selected method
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
    await this.loadClusterRepresentativeMethods();
    await this.loadAnalysisMethods();
    // Ensure all editor elements have ids and matching names
    try { this.ensureEditorIdsAndNames(); } catch (e) { /* ignore */ }
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
    const topPercentage = document.getElementById("extremes_top");
    const bottomPercentage = document.getElementById("extremes_bottom");

    if (topPercentage) {
      topPercentage.addEventListener("input", (e) => this.updateTopPercentage(e.target.value));
    }

    if (bottomPercentage) {
      bottomPercentage.addEventListener("input", (e) => this.updateBottomPercentage(e.target.value));
    }

    // Linked percentages checkbox
    const linkCheckbox = document.getElementById("extremes_linked");
    if (linkCheckbox) {
      linkCheckbox.addEventListener("change", () => this.toggleLinkedPercentages());
    }

    // Selection mode toggle
    const selectionModeToggle = document.getElementById("extremes_mode");
    if (selectionModeToggle) {
      selectionModeToggle.addEventListener("change", () => this.toggleSelectionMode());
    }

    // Clustering method selection
    const clusteringMethodSelect = document.getElementById("clusteringMethodSelect");
    if (clusteringMethodSelect) {
      clusteringMethodSelect.addEventListener("change", () => this.updateClusteringParameters());
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
    // Refresh the existing analyses list to show any changes
    try {
      this.loadAnalysisList();
    } catch (e) {
      // If manager cannot load, fallback to global function
      try {
        if (typeof refreshAnalysisList === 'function') refreshAnalysisList();
        else if (typeof loadAnalysisList === 'function') loadAnalysisList();
      } catch (e2) {}
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
      // also capture full editor DOM to persist exact state/contents
      const fullDom = this.collectFullAnalysisEditor();
      // capture full controls state (values, checked, options, visibility)
      const controlsState = this.collectAllControls();

      // attach controls_state into the configuration so it's part of the saved JSON
      try { config.controls_state = controlsState; } catch (e) { /* ignore if config is not object */ }

      const response = await DatasetUtils.api.call(`/dataset/${this.datasetId}/analysis/save`, {
        method: "POST",
        body: JSON.stringify({
          analysis_name: analysisName,
          analysis_description: document.getElementById("analysisDescription").value.trim(),
          configuration: config,
          full_dom: fullDom,
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

  // Serialize the analysis editor DOM subtree into a hierarchical JSON structure
  collectFullAnalysisEditor() {
    const root = document.getElementById('analysisEditorSection');
    if (!root) return null;

    function serializeNode(node) {
      // Text node
      if (node.nodeType === Node.TEXT_NODE) {
        return { type: 'text', text: node.textContent.trim() };
      }

      // Element node
      const obj = {
        type: 'element',
        tag: node.tagName.toLowerCase(),
        id: node.id || null,
        name: node.name || null,
        classes: node.className ? String(node.className).split(/\s+/).filter(Boolean) : [],
        attributes: {},
        children: []
      };

      // Capture attributes (skip large data blobs)
      if (node.attributes) {
        Array.from(node.attributes).forEach((attr) => {
          const key = attr.name;
          const val = attr.value;
          if (key.startsWith('data-') && val.length > 1000) return; // skip huge data-* attrs
          obj.attributes[key] = val;
        });
      }

      // Capture value / checked states for form controls
      if (node.tagName === 'INPUT' || node.tagName === 'SELECT' || node.tagName === 'TEXTAREA') {
        try {
          if (node.type === 'checkbox' || node.type === 'radio') {
            obj.checked = !!node.checked;
          }
        } catch (e) {}

        try {
          obj.value = node.value !== undefined ? node.value : null;
        } catch (e) {
          obj.value = null;
        }
      }

      // Recursively serialize children
      node.childNodes.forEach((child) => {
        const c = serializeNode(child);
        if (c) obj.children.push(c);
      });

      return obj;
    }

    return serializeNode(root);
  }

  // Collect states of all form controls inside the analysis editor (values, checked, options, visibility)
  collectAllControls() {
    const root = document.getElementById('analysisEditorSection');
    if (!root) return {};

    const controls = {};
    const elems = root.querySelectorAll('input, select, textarea, button');
    let anonIdx = 0;

    elems.forEach((el) => {
      const key = el.id || el.name || `elem_${anonIdx++}`;
      // Only collect the minimal set requested:
      // - textboxes/textarea: value (string, may be empty)
      // - sliders (input[type=range]) and numeric inputs: value
      // - checkboxes/radios: checked (boolean)
      // - selects: selected option text (for file selects: filename), for multiple selects an array of texts
      const info = { id: el.id || null, name: el.name || null, tag: el.tagName.toLowerCase() };

      try {
        if (el.tagName === 'INPUT') {
          const t = (el.type || '').toLowerCase();
          if (t === 'checkbox' || t === 'radio') {
            info.checked = !!el.checked;
            info.value = el.value !== undefined ? el.value : '';
          } else if (t === 'range' || t === 'number') {
            info.value = el.value !== undefined ? el.value : '';
          } else if (t === 'text' || t === 'email' || t === 'search' || t === 'password' || t === 'tel' || t === 'url' || t === 'hidden') {
            info.value = el.value !== undefined ? el.value : '';
          } else {
            // fallback: capture value for other input types (e.g., date)
            info.value = el.value !== undefined ? el.value : '';
          }
        } else if (el.tagName === 'SELECT') {
          if (el.multiple) {
            info.selected_text = Array.from(el.selectedOptions).map(o => o.text);
          } else {
            const sel = el.selectedOptions[0];
            // special-case the dataset file selects to store filename text
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
    const isValueMode = document.getElementById("extremes_mode").checked;

    return {
      mode: isValueMode ? "value" : "percentage",
      topPercentage: parseInt(document.getElementById("extremes_top").value),
      bottomPercentage: parseInt(document.getElementById("extremes_bottom").value),
      linked: document.getElementById("extremes_linked").checked,
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
        // Use the new API structure with attribute_discarding_policies array
        let policiesArray = [];
        if (Array.isArray(data.attribute_discarding_policies)) {
          policiesArray = data.attribute_discarding_policies;
        }
        this.displayDiscardingPolicies(policiesArray);
        this.discardingPoliciesData = policiesArray;
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

    // Use only the control_name as provided by backend, no fallback
    let groupsArray = [];
    if (Array.isArray(columnGroups)) {
      groupsArray = columnGroups.map((g) => ({ ...g }));
    } else if (typeof columnGroups === 'object' && columnGroups !== null) {
      groupsArray = Object.values(columnGroups).map((val) => ({ ...val }));
    }

    const groupsHTML = groupsArray
      .map((group) => {
        const controlName = group.control_name;
        const fieldCount = Array.isArray(group.columns) ? group.columns.length : 0;
        const value = typeof group.default_value !== 'undefined' ? group.default_value : '';
        return `
            <div class="col-md-6 col-lg-4 mb-3">
              <div class="card" id="group_card_${controlName}" name="group_card_${controlName}">
                <div class="card-body">
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" value="${value}" id="${controlName}" name="${controlName}" data-field-count="${fieldCount}" onchange="window.analysisManager && window.analysisManager.updateColumnGroupsSummary()" checked>
                    <label class="form-check-label" for="${controlName}">
                      <strong>${controlName}</strong>
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
        const parameterInputs = this.generateParameterInputs(policy.policy_key, policy.parameters);
        const isEnabled = policy.enabled ? 'checked' : '';

        return `
            <div class="col-12 mb-4">
              <div class="card discarding-policy-card" id="policy_card_${policy.policy_key}" name="policy_card_${policy.policy_key}" data-policy-key="${policy.policy_key}">
                <div class="card-header">
                  <div class="d-flex align-items-center justify-content-between">
                    <div class="form-check">
                      <input class="form-check-input" type="checkbox" id="policy_${policy.policy_key}" name="policy_${policy.policy_key}" ${isEnabled}>
                      <label class="form-check-label" for="policy_${policy.policy_key}">
                        ${policy.label}
                        <small class="text-muted d-block">${policy.description}</small>
                      </label>
                    </div>
                    <button type="button" class="btn btn-outline-info btn-sm" onclick="showDiscardingPolicyInfo('${policy.policy_key}')">
                      <i class="fas fa-info-circle me-1"></i>Info
                    </button>
                  </div>
                </div>
                <div class="card-body" id="policy_body_${policy.policy_key}" name="policy_body_${policy.policy_key}" style="display: ${policy.enabled ? 'block' : 'none'}">
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
      const checkbox = document.getElementById(`policy_${policy.policy_key}`);
      if (checkbox) {
        checkbox.addEventListener('change', () => this.togglePolicyBody(policy.policy_key));
      }
    });

    this.updateDiscardingPolicySummary();
  }

  // Generate parameter inputs for a policy
  generateParameterInputs(policyKey, parameters) {
    // Render inputs for known parameter types (static, float, int, select, fallback to text)
    return Object.entries(parameters)
      .map(([paramKey, paramConfig]) => {
        // STATIC: informational text / lists
        if (paramConfig.type === 'static') {
          if (paramKey === 'subgroups' && typeof paramConfig.description === 'string') {
            const parts = paramConfig.description.split(/\.|;|\n/).map(p => p.trim()).filter(p => p.length > 0);
            const items = parts.map(p => {
              if (p.indexOf(':') !== -1) {
                const [left, right] = p.split(/:\s*(.+)/);
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
                    <div class="form-text">${paramConfig.description || ''}</div>
                  </div>`;
        }

        // NUMERIC (float / int)
        if (paramConfig.type === 'float' || paramConfig.type === 'int') {
          const step = paramConfig.step !== undefined ? paramConfig.step : (paramConfig.type === 'int' ? 1 : 'any');
          const minAttr = paramConfig.min !== undefined ? `min="${paramConfig.min}"` : '';
          const maxAttr = paramConfig.max !== undefined ? `max="${paramConfig.max}"` : '';
          const value = paramConfig.default !== undefined ? paramConfig.default : '';
          const controlName = paramConfig.control_name || `${policyKey}_param_${paramKey}`;

          return `<div class="col-md-6 mb-2">
                    <label class="form-label fw-bold" for="${controlName}">${paramConfig.label || paramKey}</label>
                    <input type="number" class="form-control" id="${controlName}" name="${controlName}" value="${value}" step="${step}" ${minAttr} ${maxAttr}>
                    <div class="form-text">${paramConfig.description || ''}</div>
                  </div>`;
        }

        // SELECT
        if (paramConfig.type === 'select') {
          const opts = (paramConfig.options || []).map(o => {
            const sel = (o.value === paramConfig.default) ? 'selected' : '';
            return `<option value="${o.value}" ${sel}>${o.label}</option>`;
          }).join('');
          const controlName = paramConfig.control_name || `${policyKey}_param_${paramKey}`;

          return `<div class="col-md-6 mb-2">
                    <label class="form-label fw-bold" for="${controlName}">${paramConfig.label || paramKey}</label>
                    <select class="form-select" id="${controlName}" name="${controlName}">${opts}</select>
                    <div class="form-text">${paramConfig.description || ''}</div>
                  </div>`;
        }

        // FALLBACK: text input
        const controlName = paramConfig.control_name || `${policyKey}_param_${paramKey}`;
        return `<div class="col-md-6 mb-2">
                  <label class="form-label fw-bold" for="${controlName}">${paramConfig.label || paramKey}</label>
                  <input type="text" class="form-control" id="${controlName}" name="${controlName}" value="${paramConfig.default !== undefined ? paramConfig.default : ''}">
                  <div class="form-text">${paramConfig.description || ''}</div>
                </div>`;
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
        this.displayBrackenTimePoints(data.bracken_time_points, data.default_time_point);
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

    // Handle different API response formats
    let timePointsArray = timePoints;
    if (!Array.isArray(timePoints) && timePoints && typeof timePoints === 'object') {
      // If timePoints is an object {key: description}, convert to array format
      timePointsArray = Object.entries(timePoints).map(([key, description]) => ({
        key: key,
        title: key, // Use key as title, or format if needed
        description: description || ''
      }));
    } else if (!timePoints) {
      // If timePoints is null, undefined, or falsy, default to empty array
      timePointsArray = [];
    }

    // Add time point options
    timePointsArray.forEach((timePoint, index) => {
      const option = document.createElement("option");
      option.value = timePoint.control_name_post_analysis;
      option.textContent = timePoint.label;

      // Store description
      this.timePointDescriptions[timePoint.control_name_post_analysis] = timePoint.description;

      // Set as selected if it's the default, otherwise don't select any by default
      if (defaultTimePoint && (timePoint.control_name_post_analysis === defaultTimePoint || timePoint.value === defaultTimePoint)) {
        option.selected = true;
      }

      timePointSelect.appendChild(option);
    });

    // Store the first option value for later
    if (timePointsArray.length > 0) {
      this.firstTimePointKey = timePointsArray[0].control_name_post_analysis;
    }


    // Update description - placeholder should be selected initially
    this.updateTimePointDescription();
    // Populate sample timepoints comparison UI
    try { this.displaySampleTimepoints(timePointsArray); } catch(e) { /* ignore if UI not present */ }
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
      card.id = `sample_tp_card_${tp.control_name_post_analysis}`;
      card.setAttribute('name', `sample_tp_card_${tp.control_name_post_analysis}`);
      card.innerHTML = `
        <div class="form-check">
          <input class="form-check-input sample-timepoint-checkbox" type="checkbox" value="${tp.control_name_post_analysis}" id="${tp.control_name_post_analysis}" name="${tp.control_name_post_analysis}">
          <label class="form-check-label" for="${tp.control_name_post_analysis}">
            <strong>${tp.label}</strong>
            <div class="text-muted small">${(tp.description || '').substring(0,120)}${(tp.description||'').length>120?'...':''}</div>
          </label>
        </div>
      `;

      col.appendChild(card);
      container.appendChild(col);
    });

    // Store timepoints data for visibility updates
    this.sampleTimepointsData = timePoints;

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

    const selectedTp = this.sampleTimepointsData ? this.sampleTimepointsData.find(tp => tp.value === selectedValue) : null;
    const selectedControlName = selectedTp ? selectedTp.control_name_post_analysis : '';

    const checkboxes = container.querySelectorAll('.sample-timepoint-checkbox');
    checkboxes.forEach(cb => {
      if (cb.value === selectedControlName) {
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
    // Assume stratifications is an array of objects
    const stratificationsHTML = Array.isArray(stratifications)
      ? stratifications.map((strat, idx) => {
          const controlName = strat.control_name_post_analysis || `strat_${idx}`;
          const stratName = DatasetUtils.formatGroupName(strat.name || controlName);
          const description = strat.description || "";
          const subgroupsHtml = Array.isArray(strat.subgroups)
            ? `<div class="mt-2"><strong>Subgroups:</strong><ul class="mb-0 ps-3">${strat.subgroups.map(sg => `<li><strong>${sg.name}:</strong> <span class='text-muted'>${sg.condition}</span></li>`).join('')}</ul></div>`
            : "";
          return `
            <div class="col mb-2">
              <div class="card" id="strat_card_${controlName}" name="strat_card_${controlName}">
                <div class="card-body">
                  <div class="form-check">
                    <input class="form-check-input" type="checkbox" ${strat.default ? 'checked' : ''} value="${controlName}" id="${controlName}" name="${controlName}" onchange="window.analysisManager && window.analysisManager.updateStratificationSummary()">
                    <label class="form-check-label" for="${controlName}">
                      <strong>${stratName}</strong>
                      <small class="text-muted d-block">${description}</small>
                    </label>
                  </div>
                  ${subgroupsHtml}
                </div>
              </div>
            </div>
          `;
        }).join("")
      : "";
    container.innerHTML = stratificationsHTML;
    this.updateStratificationSummary();
  }

  // Show stratifications error
  showStratificationsError(message) {
    const container = document.getElementById("stratificationContainer");
    if (container) {
      container.innerHTML = `<div class="alert alert-warning" role="alert">
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Unable to load stratifications:</strong> ${message}
      </div>`;
    }
  }

  // Load clustering methods
  async loadClusteringMethods() {
    try {
      const data = await DatasetUtils.api.getClusteringMethods(this.datasetId);

      if (data.success) {
        // Handle new API structure with array of methods and default_method
        let methodsArray = [];
        let defaultMethod = null;

        if (Array.isArray(data.clustering_methods)) {
          methodsArray = data.clustering_methods;
          defaultMethod = data.default_method;
        } else if (Array.isArray(data.methods)) {
          // Fallback for old structure
          methodsArray = data.methods;
        } else if (data.methods) {
          // Convert old object format to array
          methodsArray = Object.entries(data.methods).map(([key, method]) => ({
            method_key: key,
            name: method.name,
            parameters: method.parameters || {}
          }));
        }

        this.displayClusteringMethods(methodsArray, defaultMethod);
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

    // Clear all existing options
    methodSelect.innerHTML = '';

    // Store clustering methods data for parameter updates
    this.clusteringMethodsData = clusteringMethods;

    // Handle array format from new API
    let methodsArray = [];
    if (Array.isArray(clusteringMethods)) {
      methodsArray = clusteringMethods;
    } else if (typeof clusteringMethods === 'object' && clusteringMethods !== null) {
      // Fallback for old object format
      methodsArray = Object.entries(clusteringMethods).map(([key, method]) => ({
        method_key: key,
        name: method.name,
        ...method
      }));
    }

    // Add method options
    methodsArray.forEach((method) => {
      const option = document.createElement("option");
      option.value = method.method_key;
      option.textContent = method.name;

      if (defaultMethod && method.method_key === defaultMethod) {
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

  // Update clustering parameters when method is selected
  updateClusteringParameters() {
    const methodSelect = document.getElementById("clusteringMethodSelect");
    const parametersForm = document.getElementById("clusteringParametersForm");
    const methodDescription = document.getElementById("clusteringMethodDescription");

    if (!methodSelect || !parametersForm || !this.clusteringMethodsData) return;

    const selectedMethodKey = methodSelect.value;
    if (!selectedMethodKey) {
      parametersForm.innerHTML = "";
      // Clear description when no method is selected
      if (methodDescription) methodDescription.textContent = "";
      return;
    }

    // Find the selected method
    const selectedMethod = this.clusteringMethodsData.find(method => method.method_key === selectedMethodKey);
    if (!selectedMethod || !selectedMethod.parameters) {
      parametersForm.innerHTML = "";
      if (methodDescription) methodDescription.textContent = "";
      return;
    }

    // Update description with the selected method's description
    if (methodDescription) {
      methodDescription.textContent = selectedMethod.description || "";
    }

    // Generate parameter inputs
    const parameterInputs = this.generateClusteringParameterInputs(selectedMethod.parameters);
    parametersForm.innerHTML = `
      <div class="row">
        ${parameterInputs}
      </div>
    `;
  }

  // Generate parameter inputs for clustering methods
  generateClusteringParameterInputs(parameters) {
    if (!parameters) return "";

    return Object.entries(parameters).map(([paramKey, paramConfig]) => {
      const paramId = `clustering_param_${paramKey}`;
      const label = paramConfig.name || paramKey;
      const description = paramConfig.description || "";
      const defaultValue = paramConfig.default !== undefined ? paramConfig.default : "";
      const colClass = Object.keys(parameters).length > 2 ? "col-md-6" : "col-md-4";

      if (paramConfig.type === "select" && paramConfig.options) {
        const options = paramConfig.options.map(option => {
          const isSelected = option === defaultValue ? "selected" : "";
          const isBest = option === paramConfig.best_component ? " (Best)" : "";
          return `<option value="${option}" ${isSelected}>${option}${isBest}</option>`;
        }).join("");

        return `
          <div class="${colClass} mb-3">
            <label for="${paramId}" class="form-label">
              <i class="fas fa-cog text-primary me-2"></i>
              ${label}
            </label>
            <select class="form-select" id="${paramId}" name="${paramId}" onchange="updateClusteringSummary()">
              <option value="">Select ${label.toLowerCase()}...</option>
              ${options}
            </select>
            <div class="form-text">
              ${description}
              ${paramConfig.best_component && paramConfig.best_component !== "auto" ? `<br><small class="text-success"><i class="fas fa-star me-1"></i>Best: ${paramConfig.best_component}</small>` : ""}
            </div>
          </div>
        `;
      } else if (paramConfig.type === "number") {
        const step = paramConfig.step || 1;
        const min = paramConfig.min !== undefined ? `min="${paramConfig.min}"` : "";
        const max = paramConfig.max !== undefined ? `max="${paramConfig.max}"` : "";

        return `
          <div class="${colClass} mb-3">
            <label for="${paramId}" class="form-label">
              <i class="fas fa-cog text-primary me-2"></i>
              ${label}
            </label>
            <input type="number" class="form-control" id="${paramId}" name="${paramId}"
                   value="${defaultValue}" step="${step}" ${min} ${max}
                   onchange="updateClusteringSummary()">
            <div class="form-text">
              ${description}
              ${paramConfig.best_component && paramConfig.best_component !== "auto" ? `<br><small class="text-success"><i class="fas fa-star me-1"></i>Best: ${paramConfig.best_component}</small>` : ""}
            </div>
          </div>
        `;
      }

      return "";
    }).join("");
  }

  // Load analysis methods
  async loadAnalysisMethods() {
    try {
      const data = await DatasetUtils.api.getAnalysisMethods(this.datasetId);

      if (data.success) {
        // Use data.analysis_methods instead of data.methods
        const methodsArray = data.analysis_methods || [];
        // Store methods for UI usage and info modal
        this.analysisMethodsData = methodsArray.map(method => ({
          key: method.control_name,
          postAnalysisKey: method.control_name_post_analysis,
          title: method.name,
          description: method.description,
          parameters: method.parameters,
          pros: method.pros,
          cons: method.cons,
          limitations: method.cons, // Using cons as limitations if not separate
          expectations: method.use_cases ? method.use_cases.join('; ') : ''
        }));

        // Pre-create all parameter containers for each method
        this.createAllAnalysisMethodParameterContainers(methodsArray);
        this.displayAnalysisMethods(methodsArray);
        this.displayAnalysisMethodsComparison(this.analysisMethodsData);
      } else {
        this.showAnalysisMethodError(data.message);
      }
    } catch (error) {
      console.error("Failed to load analysis methods:", error);
      this.showAnalysisMethodError("Failed to load analysis methods");
    }
  }

  // Create all parameter containers for each analysis method (hidden by default)
  createAllAnalysisMethodParameterContainers(methodsArray) {
    const parent = document.getElementById("analysisMethodParametersContainers");
    if (!parent) return;
    parent.innerHTML = "";
    methodsArray.forEach(method => {
      const container = document.createElement("div");
      container.id = `analysisMethodParameters_${method.control_name}`;
      container.className = "analysis-method-parameters-container";
      container.style.display = "none";
      container.innerHTML = `
        <div class="row">
          <div class="col-12">
            <h6 class="mb-3">
              <i class="fas fa-sliders-h me-2"></i>
              Method Parameters (${method.name})
            </h6>
            <div>
              ${this.generateAnalysisMethodParameterInputs(method)}
            </div>
          </div>
        </div>
      `;
      parent.appendChild(container);
    });
  }

  // Generate parameter inputs for a method using control_name for id/name
  generateAnalysisMethodParameterInputs(method) {
    if (!method.parameters) return "";
    // parameters is already an object or array from the API
    const params = Array.isArray(method.parameters)
      ? method.parameters
      : Object.values(method.parameters);
    return params.map(param => {
      const id = param.control_name;
      if (!id) {
        console.error("Parameter missing control_name:", param);
        return ""; // Skip invalid parameters
      }
      const label = param.name || param.label || param.key || id;
      const desc = param.description || "";
      const def = param.default !== undefined ? param.default : "";
      if (param.type === "select" && param.options) {
        const opts = param.options.map(o => `<option value="${o}" ${o === def ? "selected" : ""}>${o}</option>`).join("");
        return `<div class="mb-2"><label class="form-label fw-bold" for="${id}">${label}</label><select class="form-select" id="${id}" name="${id}">${opts}</select><div class="form-text">${desc}</div></div>`;
      } else if (param.type === "boolean") {
        const checked = def ? "checked" : "";
        return `<div class="mb-2"><label class="form-label fw-bold" for="${id}">${label}</label><input type="checkbox" class="form-check-input" id="${id}" name="${id}" ${checked}><div class="form-text">${desc}</div></div>`;
      } else if (param.type === "number") {
        const min = param.min !== undefined ? `min="${param.min}"` : "";
        const max = param.max !== undefined ? `max="${param.max}"` : "";
        const step = param.step !== undefined ? `step="${param.step}"` : "any";
        return `<div class="mb-2"><label class="form-label fw-bold" for="${id}">${label}</label><input type="number" class="form-control" id="${id}" name="${id}" value="${def}" ${min} ${max} step="${step}"><div class="form-text">${desc}</div></div>`;
      } else {
        return `<div class="mb-2"><label class="form-label fw-bold" for="${id}">${label}</label><input type="text" class="form-control" id="${id}" name="${id}" value="${def}"><div class="form-text">${desc}</div></div>`;
      }
    }).join("");
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
      card.id = `analysis_method_card_${m.key}`;
      card.setAttribute('name', `analysis_method_card_${m.key}`);

      const safeTitle = m.title || m.name || m.key;
      const safeDesc = m.description || '';

      card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
          <div>
            <div class="form-check">
              <input class="form-check-input analysis-method-checkbox" type="checkbox" value="${m.postAnalysisKey}" id="${m.postAnalysisKey}" name="${m.postAnalysisKey}">
              <label class="form-check-label" for="analysis_method_${m.postAnalysisKey}"><strong>${safeTitle}</strong></label>
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
    if (!container) {
      return;
    }

    const selectedValue = selected ? selected.value : '';
    // Show the option's visible text rather than the value/key
    let selectedText = '';
    try {
      selectedText = selected && selected.options && selected.selectedIndex >= 0 ? selected.options[selected.selectedIndex].text : '';
    } catch (e) {
      selectedText = selectedValue;
    }
    if (selectedDisplay) selectedDisplay.textContent = selectedText || 'None';

    // Find the postAnalysisKey for the selected method
    const selectedMethod = this.analysisMethodsData ? this.analysisMethodsData.find(m => m.key === selectedValue) : null;
    const selectedPostAnalysisKey = selectedMethod ? selectedMethod.postAnalysisKey : '';

    const checkboxes = container.querySelectorAll('.analysis-method-checkbox');

    // First, enable the previously selected method's checkbox if it exists
    if (this.previousSelectedPostAnalysisKey && this.previousSelectedPostAnalysisKey !== selectedPostAnalysisKey) {
      checkboxes.forEach(cb => {
        if (cb.value === this.previousSelectedPostAnalysisKey) {
          const card = cb.closest('.analysis-method-card');
          cb.disabled = false;
          const label = cb.nextElementSibling;
          if (label) label.classList.remove('text-muted');
          if (card) {
            card.classList.remove('bg-light', 'opacity-50');
          }
        }
      });
    }

    // Then, disable the currently selected method's checkbox
    checkboxes.forEach(cb => {
      const card = cb.closest('.analysis-method-card');
      if (cb.value === selectedPostAnalysisKey) {
        cb.checked = false;
        cb.disabled = true;
        const label = cb.nextElementSibling;
        if (label) label.classList.add('text-muted');
        if (card) {
          card.classList.add('bg-light', 'opacity-50');
        }
      }
    });

    // Update the previous selection tracker
    this.previousSelectedPostAnalysisKey = selectedPostAnalysisKey;

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

  // Display analysis methods (only called ONCE at load)
  displayAnalysisMethods(methodsArray) {
    const methodSelect = document.getElementById("analysisMethodSelect");
    if (!methodSelect) return;

    // Clear existing options except first
    while (methodSelect.children.length > 1) {
      methodSelect.removeChild(methodSelect.lastChild);
    }

    // Find the default selected method
    let defaultMethod = null;
    methodsArray.forEach(method => {
      if (method.selected) {
        defaultMethod = method.control_name;
      }
    });

    // Add method options
    methodsArray.forEach(method => {
      const option = document.createElement("option");
      option.value = method.control_name;
      option.textContent = method.name;
      if (defaultMethod && method.control_name === defaultMethod) {
        option.selected = true;
      }
      methodSelect.appendChild(option);
    });

    // Add change event listener to update visibility when selection changes
    methodSelect.addEventListener('change', () => {
      this.updateAnalysisMethod();
      this.updateAnalysisMethodsVisibility();
    });

    // Update description and trigger parameter display for default method
    if (defaultMethod) {
      this.updateAnalysisMethodDescription(defaultMethod);
      this.updateAnalysisMethod();
      this.updateAnalysisMethodsVisibility();
    }
  }

  // Show/hide parameter containers for selected method (NO fetch, robust to missing container)
  updateAnalysisMethod() {
  console.log('DatasetAnalysisManager.updateAnalysisMethod called');
  const select = document.getElementById("analysisMethodSelect");
  const containersParent = document.getElementById("analysisMethodParametersContainers");
  if (!select || !containersParent) {
    console.log('select or containersParent not found');
    return;
  }
  const selectedControlName = select.value;
  console.log('selectedControlName:', selectedControlName);

  // Update description
  this.updateAnalysisMethodDescription(selectedControlName);

  // Hide all
  Array.from(containersParent.children).forEach(child => {
    if (child && child.style) child.style.display = "none";
  });
  // Show selected
  if (selectedControlName) {
    const showDiv = document.getElementById(`analysisMethodParameters_${selectedControlName}`);
    if (showDiv && showDiv.style) {
      showDiv.style.display = "block";
    } else {
      // Fallback: show a warning in the UI for missing container, but do not throw
      console.warn(`No parameter container found for analysis method: ${selectedControlName}`);
      if (typeof DatasetUtils !== 'undefined' && DatasetUtils.showAlert) {
        DatasetUtils.showAlert(`No parameter UI for selected method (${selectedControlName})`, "warning");
      }
    }
  }
	// Update comparison visibility
	console.log('calling updateAnalysisMethodsVisibility');
  }

  // Update analysis method description
  updateAnalysisMethodDescription(selectedControlName) {
    const descriptionElement = document.getElementById("analysisMethodDescription");
    if (!descriptionElement) return;

    if (!selectedControlName) {
      descriptionElement.textContent = "Choose a method for multivariate survival analysis";
      return;
    }

    // Find the method in stored data
    const method = this.analysisMethodsData ? this.analysisMethodsData.find(m => m.key === selectedControlName) : null;
    if (method && method.description) {
      descriptionElement.textContent = method.description;
    } else {
      descriptionElement.textContent = "Method description not available";
    }
  }

  // Toggle selection mode
  toggleSelectionMode() {
    const toggle = document.getElementById("extremes_mode");
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

    const linkCheckbox = document.getElementById("extremes_linked");
    if (linkCheckbox && linkCheckbox.checked) {
      // When linked, update the other input and its display directly to avoid
      // calling the counterpart function which would create a recursive loop.
      const bottomPercentage = document.getElementById("extremes_bottom");
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

    const linkCheckbox = document.getElementById("extremes_linked");
    if (linkCheckbox && linkCheckbox.checked) {
      // When linked, update the other input and its display directly to avoid
      // calling the counterpart function which would create a recursive loop.
      const topPercentage = document.getElementById("extremes_top");
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
    const linkCheckbox = document.getElementById("extremes_linked");

    if (linkCheckbox && linkCheckbox.checked) {
      const topPercentage = document.getElementById("extremes_top");
      const bottomPercentage = document.getElementById("extremes_bottom");

      if (topPercentage && bottomPercentage) {
        bottomPercentage.value = topPercentage.value;
        this.updateBottomPercentage(topPercentage.value);
      }
    }
  }

  // Update extreme time point summary
  updateExtremeTimePointSummary() {
    const topPercentage = document.getElementById("extremes_top");
    const bottomPercentage = document.getElementById("extremes_bottom");
    const summaryText = document.getElementById("extremeTimePointSummaryText");
    const topPatientsCount = document.getElementById("topPatientsCount");
    const bottomPatientsCount = document.getElementById("bottomPatientsCount");
    const totalPatientsCount = document.getElementById("totalPatientsCount");
    const selectionModeToggle = document.getElementById("extremes_mode");

    if (!topPercentage || !bottomPercentage || !summaryText) return;

    const topPercent = parseInt(topPercentage.value);
    const bottomPercent = parseInt(bottomPercentage.value);
    const isValueMode = selectionModeToggle ? selectionModeToggle.checked : false;

    // Get total patient count from the selected patient file
    const patientFileSelect = document.getElementById("editorPatientFileSelect");

    if (patientFileSelect && patientFileSelect.value) {
      // Fetch actual patient count from API
      DatasetUtils.api.call(`/dataset/${this.datasetId}/file/${patientFileSelect.value}/patient-count`)
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
            this.updateExtremeTimePointSummaryFallback();
          }
        })
        .catch((error) => {
          console.error("Error loading patient count:", error);
          this.updateExtremeTimePointSummaryFallback();
        });
    } else {
      this.updateExtremeTimePointSummaryFallback();
    }
  }



  // Update extreme time point summary fallback
  updateExtremeTimePointSummaryFallback() {
    const topPercentage = document.getElementById("extremes_top");
    const bottomPercentage = document.getElementById("extremes_bottom");
    const summaryText = document.getElementById("extremeTimePointSummaryText");
    const topPatientsCount = document.getElementById("topPatientsCount");
    const bottomPatientsCount = document.getElementById("bottomPatientsCount");
    const totalPatientsCount = document.getElementById("totalPatientsCount");
    const selectionModeToggle = document.getElementById("extremes_mode");

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

    // Reset checkboxes (default to checked) - exclude stratifications to preserve defaults
    const checkboxes = document.querySelectorAll(
      '#columnGroupsContainer input[type="checkbox"]'
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
    const topPercentage = document.getElementById("extremes_top");
    const bottomPercentage = document.getElementById("extremes_bottom");
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

    // Ensure any static elements in the editor have name attributes matching their ids
    try { this.ensureEditorIdsAndNames(); } catch (e) { /* ignore */ }
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
        // Use the new API structure with microbial_discarding_policies array
        let policiesArray = [];
        if (Array.isArray(data.microbial_discarding_policies)) {
          policiesArray = data.microbial_discarding_policies;
        }
        this.displayMicrobialDiscardingPolicies(policiesArray);
        this.microbialDiscardingPoliciesData = policiesArray;
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
        const parameterInputs = this.generateParameterInputs(policy.policy_key, policy.parameters);
        const isEnabled = policy.enabled ? 'checked' : '';

        return `
        <div class="col-12 mb-4">
          <div class="card microbial-discarding-policy-card" id="microbial_policy_card_${policy.policy_key}" name="microbial_policy_card_${policy.policy_key}" data-policy-key="${policy.policy_key}">
            <div class="card-header">
              <div class="d-flex align-items-center justify-content-between">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" id="microbial_policy_${policy.policy_key}" name="microbial_policy_${policy.policy_key}" ${isEnabled}>
                  <label class="form-check-label" for="microbial_policy_${policy.policy_key}">
                    ${policy.label}
                    <small class="text-muted d-block">${policy.description}</small>
                  </label>
                </div>
                <button type="button" class="btn btn-outline-info btn-sm" onclick="showMicrobialDiscardingPolicyInfo('${policy.policy_key}')">
                  <i class="fas fa-info-circle me-1"></i>Info
                </button>
              </div>
            </div>
            <div class="card-body" id="microbial_policy_body_${policy.policy_key}" name="microbial_policy_body_${policy.policy_key}" style="display: ${policy.enabled ? 'block' : 'none'}">
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
      const checkbox = document.getElementById(`microbial_policy_${policy.policy_key}`);
      if (checkbox) {
        checkbox.addEventListener('change', () => this.toggleMicrobialPolicyBody(policy.policy_key));
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
        this.displayMicrobialGroupingPolicies(data.microbial_grouping_methods);
        this.microbialGroupingData = data.microbial_grouping_methods;
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
      const parameterInputs = this.generateParameterInputs(method.method_key, method.parameters);
      const isChecked = method.enabled ? 'checked' : '';
      return `
          <div class="col-12 mb-4">
            <div class="card microbial-grouping-card" id="microbial_grouping_card_${method.method_key}" name="microbial_grouping_card_${method.method_key}" data-method-key="${method.method_key}">
              <div class="card-header">
                <div class="d-flex align-items-center justify-content-between">
                  <div class="form-check">
                    <input class="form-check-input" type="radio" name="microbialGroupingMethod" id="${method.control_name}" value="${method.method_key}" ${isChecked}>
                    <label class="form-check-label" for="${method.control_name}">
                      ${method.name}
                      <small class="text-muted d-block">${method.description}</small>
                    </label>
                  </div>
                  <button type="button" class="btn btn-outline-info btn-sm" onclick="showMicrobialGroupingInfo('${method.method_key}')">
                    <i class="fas fa-info-circle me-1"></i>Info
                  </button>
                </div>
              </div>
              <div class="card-body" id="microbial_grouping_body_${method.method_key}" name="microbial_grouping_body_${method.method_key}" style="display: ${method.enabled ? 'block' : 'none'}">
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
      const radio = document.getElementById(`${method.control_name}`);
      if (radio) {
        radio.addEventListener('change', () => this.toggleMicrobialGroupingBody(method.method_key));
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

  // Ensure every input and card inside the analysis editor has a unique id and a name equal to that id
  ensureEditorIdsAndNames() {
    const section = document.getElementById('analysisEditorSection');
    if (!section) return;

    // Generate ids for elements that are missing them and ensure name == id
    const selectors = 'input, select, textarea, button, div.card';
    const elems = Array.from(section.querySelectorAll(selectors));
    let counter = 1;
    elems.forEach((el) => {
      // skip elements outside the form area
      if (!el) return;

      // If element has no id, create one using a deterministic base
      if (!el.id || el.id.trim() === '') {
        const baseCandidates = [el.getAttribute('data-policy-key'), el.getAttribute('data-method-key'), el.className, el.tagName.toLowerCase()];
        let base = baseCandidates.find(b => b && b.length > 0) || 'elem';
        base = String(base).replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_\-]/g, '').toLowerCase();
        let newId = `${base}_${counter}`;
        while (document.getElementById(newId)) {
          counter += 1;
          newId = `${base}_${counter}`;
        }
        el.id = newId;
        counter += 1;
      }

      // For radio inputs keep existing grouping name if present; otherwise set name=id
      if (el.tagName.toLowerCase() === 'input' && el.type === 'radio') {
        if (!el.name || el.name.trim() === '') {
          el.name = el.id;
        }
        // do not overwrite existing radio group names
      } else {
        try { el.name = el.id; } catch (e) { /* ignore readonly name attributes */ }
      }
    });
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

  // Load cluster representative methods
  async loadClusterRepresentativeMethods() {
    try {
      const data = await DatasetUtils.api.call(`/dataset/${this.datasetId}/metadata/cluster-representative-methods`);

      if (data.success) {
        this.displayClusterRepresentativeMethods(data.cluster_representative_methods, data.default_method);
        // Load all method details for the details section
        this.loadAllClusterRepresentativeMethodDetails(data.cluster_representative_methods);
        this.clusterRepresentativeMethodsData = data.cluster_representative_methods;
      } else {
        this.showClusterRepresentativeError(data.message);
      }
    } catch (error) {
      console.error("Failed to load cluster representative methods:", error);
      this.showClusterRepresentativeError("Failed to load cluster representative methods");
    }
  }

  // Display cluster representative methods
  displayClusterRepresentativeMethods(clusterRepMethods, defaultMethod = null) {
    const methodSelect = document.getElementById("clusterRepresentativeMethod");
    if (!methodSelect) return;

    // Clear existing options (except the first one)
    while (methodSelect.children.length > 1) {
      methodSelect.removeChild(methodSelect.lastChild);
    }

    // Add methods to dropdown
    if (Array.isArray(clusterRepMethods)) {
      // Handle array format from API
      clusterRepMethods.forEach((method) => {
        const option = document.createElement("option");
        option.value = method.method_key;
        option.textContent = method.name;
        methodSelect.appendChild(option);
      });
    } else {
      // Handle object format (legacy)
      Object.entries(clusterRepMethods).forEach(([methodKey, methodConfig]) => {
        const option = document.createElement("option");
        option.value = methodKey;
        option.textContent = methodConfig.name;
        methodSelect.appendChild(option);
      });
    }

    // Set default method if provided
    if (defaultMethod) {
      methodSelect.value = defaultMethod;
      this.updateClusterRepresentativeMethod();
    }

    console.log(`Loaded ${Array.isArray(clusterRepMethods) ? clusterRepMethods.length : Object.keys(clusterRepMethods).length} cluster representative methods`);
  }

  // Update cluster representative method
  updateClusterRepresentativeMethod() {
    const methodSelect = document.getElementById("clusterRepresentativeMethod");
    const container = document.getElementById("clusterRepresentativeContainer");
    const descriptionElement = document.getElementById("clusterRepresentativeDescription");

    if (!methodSelect || !container || !descriptionElement) return;

    const selectedMethod = methodSelect.value;

    // Hide all method cards
    const allCards = document.querySelectorAll('[id^="clusterRepCard_"]');
    allCards.forEach(card => card.style.display = 'none');

    if (!selectedMethod) {
      descriptionElement.textContent = "Select a method to see its description";
      return;
    }

    // Show the selected method's card
    const selectedCard = document.getElementById(`clusterRepCard_${selectedMethod}`);
    if (selectedCard) {
      selectedCard.style.display = 'block';
    }

    // Update description
    if (this.clusterRepresentativeMethodsData) {
      const method = Array.isArray(this.clusterRepresentativeMethodsData)
        ? this.clusterRepresentativeMethodsData.find(m => m.method_key === selectedMethod)
        : this.clusterRepresentativeMethodsData[selectedMethod];

      if (method) {
        descriptionElement.textContent = method.description;
        this.updateClusterRepresentativeSummary();
      } else {
        descriptionElement.textContent = "Method description not available";
      }
    }
  }

  // Load all cluster representative method details
  loadAllClusterRepresentativeMethodDetails(methods) {
    const detailsContainer = document.getElementById("clusterRepresentativeDetails");
    if (!detailsContainer) return;

    let html = '';

    if (Array.isArray(methods)) {
      // Handle array format from API
      methods.forEach((method) => {
        html += `
          <div id="clusterRepCard_${method.method_key}" class="card" style="display: none;">
              <div class="card-body">
                  <h6 class="card-title">
                      <i class="fas fa-info-circle me-2"></i>
                      ${method.name}
                  </h6>
                  <p class="card-text"><strong>Method Type:</strong> ${method.method}</p>
                  <p class="card-text"><strong>Direction:</strong> ${method.direction}</p>
                  <p class="card-text"><strong>Explanation:</strong> ${method.explanation}</p>
              </div>
          </div>
        `;
      });
    } else {
      // Handle object format (legacy)
      const methodKeys = Object.keys(methods);
      methodKeys.forEach((methodKey) => {
        const method = methods[methodKey];
        html += `
          <div id="clusterRepCard_${methodKey}" class="card" style="display: none;">
              <div class="card-body">
                  <h6 class="card-title">
                      <i class="fas fa-info-circle me-2"></i>
                      ${method.name}
                  </h6>
                  <p class="card-text"><strong>Method Type:</strong> ${method.method}</p>
                  <p class="card-text"><strong>Direction:</strong> ${method.direction}</p>
                  <p class="card-text"><strong>Explanation:</strong> ${method.explanation}</p>
              </div>
          </div>
        `;
      });
    }

    detailsContainer.innerHTML = html;
  }

  // Show cluster representative error
  showClusterRepresentativeError(message) {
    const detailsContainer = document.getElementById("clusterRepresentativeDetails");
    if (!detailsContainer) return;

    detailsContainer.innerHTML = `
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        </div>
    `;
  }

  // Update cluster representative summary
  updateClusterRepresentativeSummary() {
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

  // Show cluster representative info
  showClusterRepresentativeInfo() {
    const methodSelect = document.getElementById("clusterRepresentativeMethod");
    if (!methodSelect || !methodSelect.value) {
      DatasetUtils.showAlert("Please select a cluster representative method first", "warning");
      return;
    }

    const selectedMethod = methodSelect.value;

    // Find method in stored data
    if (this.clusterRepresentativeMethodsData) {
      const method = Array.isArray(this.clusterRepresentativeMethodsData)
        ? this.clusterRepresentativeMethodsData.find(m => m.method_key === selectedMethod)
        : this.clusterRepresentativeMethodsData[selectedMethod];

      if (method) {
        this.showClusterRepresentativeInfoModal(method);
      } else {
        DatasetUtils.showAlert("Method information not available", "error");
      }
    }
  }

  // Show cluster representative info modal
  showClusterRepresentativeInfoModal(method) {
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

  // Reset cluster representative to default
  resetClusterRepresentativeToDefault() {
    const methodSelect = document.getElementById("clusterRepresentativeMethod");
    if (!methodSelect) return;

    // Reset to default method (abundance_highest)
    methodSelect.value = "abundance_highest";
    this.updateClusterRepresentativeMethod();

    DatasetUtils.showAlert("Cluster representative method reset to default (Highest Mean Abundance)", "success");
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
    container.style.display = isVisible ? "none" : "grid";
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
    button.innerHTML = `<i class="fas fa-eye me-1"></i>${isVisible ? "Show" : "Hide"} Details`;
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
  if (info) {
    showPolicyInfoModal(info);
  } else {
    // Fallback: try to fetch from API if data not available
    fetch(`/dataset/${window.datasetId}/metadata/analysis-methods/${methodKey}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success && data.method) {
          const fallbackInfo = {
            title: data.method.name || methodKey,
            description: data.method.description || '',
            algorithm: methodKey,
            parameters: data.method.parameters ? Object.entries(data.method.parameters).map(([key, param]) => ({
              name: param.name || key,
              default: param.default !== undefined ? param.default : '',
              description: param.description || ''
            })) : [],
            pros: data.method.pros || [],
            cons: data.method.cons || [],
            limitations: data.method.limitations || data.method.cons || [],
            expectations: data.method.expectations || ''
          };
          showPolicyInfoModal(fallbackInfo);
        } else {
          showToast("Analysis method information not available", "warning");
        }
      })
      .catch((error) => {
        console.error("Error fetching analysis method info:", error);
        showToast("Failed to load analysis method information", "error");
      });
  }
};

function getAnalysisMethodInfo(methodKey) {
  // First try to use stored data from analysis manager
  if (window.analysisManager && window.analysisManager.analysisMethodsData) {
    const method = window.analysisManager.analysisMethodsData.find(m => m.key === methodKey);
    if (method) {
      // Build modal info structure compatible with showPolicyInfoModal
      const params = method.parameters ? Object.entries(method.parameters).map(([key, param]) => ({
        name: param.name || param.label || key,
        default: param.default !== undefined ? param.default : '',
        description: param.description || ''
      })) : [];
      return {
        title: method.title || method.name || method.key,
        description: method.description || '',
        algorithm: method.key || '',
        parameters: params,
        pros: method.pros || [],
        cons: method.cons || [],
        limitations: method.limitations || method.cons || [],
        expectations: method.expectations || ''
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
    const policy = window.analysisManager.discardingPoliciesData.find(p => p.policy_key === policyKey);
    if (policy && policy.info) {
      // Build modal info structure compatible with showPolicyInfoModal
      const params = policy.parameters ? Object.entries(policy.parameters).map(([key, param]) => ({
        name: param.label || key,
        default: param.default !== undefined ? param.default : '',
        description: param.description || ''
      })) : [];
      return {
        title: policy.info.title || policy.label || policyKey,
        description: policy.info.description || '',
        algorithm: policy.info.algorithm || '',
        parameters: params,
        pros: policy.info.pros || [],
        cons: policy.info.cons || [],
        limitations: policy.info.limitations || [],
        expectations: policy.info.expectations || ''
      };
    }
  }
  return null;
}

function getMicrobialDiscardingPolicyInfo(policyKey) {
  // Get the policy data from the global analysis manager
  if (window.analysisManager && window.analysisManager.microbialDiscardingPoliciesData) {
    const policy = window.analysisManager.microbialDiscardingPoliciesData.find(p => p.policy_key === policyKey);
    if (policy && policy.info) {
      // Build modal info structure compatible with showPolicyInfoModal
      const params = policy.parameters ? Object.entries(policy.parameters).map(([key, param]) => ({
        name: param.label || key,
        default: param.default !== undefined ? param.default : '',
        description: param.description || ''
      })) : [];
      return {
        title: policy.info.title || policy.label || policyKey,
        description: policy.info.description || '',
        algorithm: policy.info.algorithm || '',
        parameters: params,
        pros: policy.info.pros || [],
        cons: policy.info.cons || [],
        limitations: policy.info.limitations || [],
        expectations: policy.info.expectations || ''
      };
    }
  }
  return null;
}

function getMicrobialGroupingInfo(methodKey) {
  // Get the method data from the global analysis manager
  if (window.analysisManager && window.analysisManager.microbialGroupingData) {
    const method = window.analysisManager.microbialGroupingData.find(m => m.method_key === methodKey);
    return method ? method.info : null;
  }
  return null;
}

function getClusteringMethodInfo(methodKey) {
  // Find the method in the stored data
  const method = window.analysisManager ? window.analysisManager.clusteringMethodsData.find(m => m.method_key === methodKey) : null;
  if (!method) return null;

  // Build policy info for modal
  const params = method.parameters ? Object.entries(method.parameters).map(([key, param]) => ({
    name: param.name || key,
    default: param.default !== undefined ? param.default : '',
    description: param.description || ''
  })) : [];

  return {
    title: method.name || methodKey,
    description: method.description || '',
    algorithm: method.method_key || '',
    parameters: params,
    pros: method.pros || [],
    cons: method.cons || [],
    limitations: method.limitations || [],
    expectations: method.expectations ? method.expectations.join('; ') : ''
  };
}

// Make it global so the HTML onchange can call it
window.updateAnalysisMethod = function() {
  if (window.analysisManager) {
    window.analysisManager.updateAnalysisMethod();
  }
};

window.showClusteringMethodInfo = function (methodKey) {
  const info = getClusteringMethodInfo(methodKey);
  if (info) showPolicyInfoModal(info);
};

window.updateClusterRepresentativeMethod = function () {
  if (window.analysisManager) {
    window.analysisManager.updateClusterRepresentativeMethod();
  }
};

window.resetClusterRepresentativeToDefault = function () {
  if (window.analysisManager) {
    window.analysisManager.resetClusterRepresentativeToDefault();
  }
};

window.showClusterRepresentativeInfo = function () {
  if (window.analysisManager) {
    window.analysisManager.showClusterRepresentativeInfo();
  }
};

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
    selection_mode: document.getElementById("extremes_mode")?.checked || false,
    top_percentage: document.getElementById("extremes_top")?.value || "",
    bottom_percentage: document.getElementById("extremes_bottom")?.value || "",
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
    // Use control_name from metadata for id/name
    let groupId = group.control_name;
    if (!groupId) {
      // Fallback if control_name is missing
      let baseId = (displayName || '').split('\n')[0].replace(/\s+/g, ' ');
      if (!baseId) baseId = `colGroup${groupIndex}`;
      groupId = baseId;
      let uniqCounter = 1;
      // Ensure the id is unique within this render
      while (usedIds.has(groupId) || document.getElementById(groupId)) {
        groupId = `${baseId}_${uniqCounter}`;
        uniqCounter++;
      }
    }
    usedIds.add(groupId);
    const columnCount = group.columns.length;
    const isChecked = group.default_value ? 'checked' : '';

    // Create a list of field names, sorted as they appear in the metadata file
    const fieldNames = group.columns
      .map((field) => `<span class="badge bg-light text-dark me-1 mb-1">${field}</span>`)
      .join("");

    html += `
            <div class="col-md-6 mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${groupId}" name="${groupId}" onchange="updateColumnGroupsSummary()" ${isChecked}>
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
    option.value = timePoint.control_name_post_analysis;
    option.textContent = timePoint.title; // Use title from metadata instead of formatted key
    option.setAttribute("data-description", timePoint.description);
    option.setAttribute("data-suffix", timePoint.suffix);
    option.setAttribute("data-function", timePoint.function);

    // Store description for later access
    window.brackenTimePointDescriptions[timePoint.control_name_post_analysis] = timePoint.description;

    // Set as selected if it's the default
    if (defaultTimePoint && (timePoint.control_name_post_analysis === defaultTimePoint || timePoint.value === defaultTimePoint)) {
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
  // stratifications is now an ordered array from the backend
  stratifications.forEach((stratification) => {
    const stratId = stratification.control_name_post_analysis || `strat_${index}_${stratification.key}`;
    
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
      <div class="col mb-2">
        <div class="card">
          <div class="card-body">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" ${stratification.default ? 'checked' : ''} value="${stratId}" id="${stratId}" name="${stratId}" onchange="(window.analysisManager && window.analysisManager.updateStratificationSummary) ? window.analysisManager.updateStratificationSummary() : updateStratificationSummary()">
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
  stratificationContainer.innerHTML = html;

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

  stratificationContainer.style.display = isVisible ? "none" : "grid";
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

  if (window.analysisManager && typeof window.analysisManager.loadClusteringMethods === 'function') {
    window.analysisManager.loadClusteringMethods();
  } else {
    // Fallback implementation
    fetch(`/dataset/${datasetId}/metadata/clustering-methods`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          displayClusteringMethods(data.clustering_methods || data.methods, data.default_method);
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
}

function displayClusteringMethods(clusteringMethods, defaultMethod = null) {
  const methodSelect = document.getElementById("clusteringMethodSelect");
  if (!methodSelect) return;

  // Clear existing options (except the first one)
  while (methodSelect.children.length > 1) {
    methodSelect.removeChild(methodSelect.lastChild);
  }

  // Handle both array and object formats for backward compatibility
  let methodsArray = [];
  if (Array.isArray(clusteringMethods)) {
    methodsArray = clusteringMethods;
  } else if (typeof clusteringMethods === 'object') {
    // Convert object to array for backward compatibility
    methodsArray = Object.entries(clusteringMethods).map(([key, method]) => ({
      method_key: key,
      name: method.name,
      description: method.description
    }));
  }

  // Add clustering method options
  methodsArray.forEach((method) => {
    const option = document.createElement("option");
    option.value = method.method_key;
    option.textContent = method.name;
    option.setAttribute("data-description", method.description);

    // Set as selected if it's the default
    if (defaultMethod && method.method_key === defaultMethod) {
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
  if (window.analysisManager && typeof window.analysisManager.updateClusteringParameters === 'function') {
    window.analysisManager.updateClusteringParameters();
  } else {
    // Fallback implementation
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
      if (methodDescription) methodDescription.textContent = "";
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
  if (window.showClusteringMethodInfo && typeof window.showClusteringMethodInfo === 'function') {
    const methodSelect = document.getElementById("clusteringMethodSelect");
    if (methodSelect && methodSelect.value) {
      window.showClusteringMethodInfo(methodSelect.value);
    } else {
      showToast("Please select a clustering method first", "warning");
    }
  } else {
    // Fallback implementation
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
                <strong class="me-auto">${
                  type.charAt(0).toUpperCase() + type.slice(1)
                }</strong>
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
  const toggle = document.getElementById("extremes_mode");
  const modeLabel = document.getElementById("extremes_mode_label");
  const modeDescription = document.getElementById("extremes_mode_description");
  const topLabel = document.getElementById("extremes_top_label");
  const bottomLabel = document.getElementById("extremes_bottom_label");
  const topDescription = document.getElementById("extremes_top_description");
  const bottomDescription = document.getElementById("extremes_bottom_description");

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
    if (topDescription) topDescription.textContent = "Percentage of patients with highest time values";
    if (bottomDescription) bottomDescription.textContent = "Percentage of patients with lowest time values";
  }

  // Update summary to reflect the new mode
  if (window.analysisManager) {
    window.analysisManager.updateExtremeTimePointSummary();
  }
}

function updateTopPercentage(value) {
  const topPercentageValue = document.getElementById("extremes_top_value");
  const linkCheckbox = document.getElementById("extremes_linked");

  if (topPercentageValue) {
    topPercentageValue.textContent = value + "%";
  }

  // If linked, update bottom percentage to match
  if (linkCheckbox && linkCheckbox.checked) {
    const bottomPercentage = document.getElementById("extremes_bottom");
    const bottomPercentageValue = document.getElementById("extremes_bottom_value");
    if (bottomPercentage && bottomPercentageValue) {
      bottomPercentage.value = value;
      bottomPercentageValue.textContent = value + "%";
    }
  }

  if (window.analysisManager) {
    window.analysisManager.updateExtremeTimePointSummary();
  }
}

function updateBottomPercentage(value) {
  const bottomPercentageValue = document.getElementById("extremes_bottom_value");
  const linkCheckbox = document.getElementById("extremes_linked");

  if (bottomPercentageValue) {
    bottomPercentageValue.textContent = value + "%";
  }

  // If linked, update top percentage to match
  if (linkCheckbox && linkCheckbox.checked) {
    const topPercentage = document.getElementById("extremes_top");
    const topPercentageValue = document.getElementById("extremes_top_value");
    if (topPercentage && topPercentageValue) {
      topPercentage.value = value;
      topPercentageValue.textContent = value + "%";
    }
  }

  if (window.analysisManager) {
    window.analysisManager.updateExtremeTimePointSummary();
  }
}

function toggleLinkedPercentages() {
  const linkCheckbox = document.getElementById("extremes_linked");
  const topPercentage = document.getElementById("extremes_top");
  const bottomPercentage = document.getElementById("extremes_bottom");

  if (linkCheckbox && linkCheckbox.checked) {
    // Link them by setting bottom to match top
    if (topPercentage && bottomPercentage) {
      bottomPercentage.value = topPercentage.value;
      updateBottomPercentage(topPercentage.value);
    }
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

function showAnalysisMethodInfo(methodKey) {
  if (!methodKey) {
    showToast("Please select an analysis method first", "warning");
    return;
  }

  // First try to get info from cached data using getAnalysisMethodInfo
  const info = getAnalysisMethodInfo(methodKey);
  if (info) {
    showPolicyInfoModal(info);
    return;
  }

  // Fallback to API fetch if cached data not available
  fetch(`/dataset/${window.datasetId}/metadata/analysis-methods/${methodKey}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Normalize parameters to ensure it's an array
        const method = data.method;
        const params = method.parameters ? (Array.isArray(method.parameters) ? method.parameters.map(p => ({
          name: p.name || p.label || p.key,
          default: p.default !== undefined ? p.default : '',
          description: p.description || ''
        })) : Object.entries(method.parameters).map(([key, param]) => ({
          name: param.name || param.label || key,
          default: param.default !== undefined ? param.default : '',
          description: param.description || ''
        }))) : [];

        const info = {
          title: method.title || method.name || method.key,
          description: method.description || '',
          algorithm: method.key || '',
          parameters: params,
          pros: method.pros || [],
          cons: method.cons || [],
          limitations: method.limitations || method.cons || [],
          expectations: method.expectations || ''
        };
        showPolicyInfoModal(info);
      } else {
        showAnalysisMethodError(data.error || "Failed to load method information");
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
  if (window.analysisManager) {
    window.analysisManager.updateExtremeTimePointSummary();
  }

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
