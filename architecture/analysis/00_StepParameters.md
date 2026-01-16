# 00_StepParameters.md: Pipeline Step Parameter Specifications

This document specifies the parameter structures for each step in the microbiome analysis pipeline, including data validation rules and storage locations.

---

## 📊 **Parameter Storage Architecture**

### **Storage Location**
All step parameters are stored in the PipelineData configuration section:
```python
pipeline_data.config['parameters'][step_id] = {
    # Step-specific parameter dictionary
}
```

### **Parameter Access Pattern**
Steps retrieve parameters during execution:
```python
parameters = pipeline_data.config.get('parameters', {}).get(step_id, {})
```

### **Validation Rules**
- **Required parameters**: Must be present for step execution
- **Optional parameters**: Have default values if not provided
- **Type validation**: Parameters validated for correct data types
- **Range validation**: Numeric parameters checked for valid ranges

---

## 🔧 **Step Parameter Specifications**

### **Phase 1: Data Sources Selection**
**Step ID:** `data_sources`  
**Storage:** `pipeline_data.config['parameters']['data_sources']`

#### **Parameter Structure**
```python
{
    "patient_file_id": str,        # Required: Patient metadata file identifier
    "taxonomy_file_id": str,       # Required: Taxonomy mapping file identifier
    "bracken_file_id": str,        # Required: Bracken abundance file identifier
    "bracken_time_point": str      # Required: Time point selection key
}
```

#### **Validation Rules**
- **patient_file_id**: Non-empty string, must correspond to valid file in dataset
- **taxonomy_file_id**: Non-empty string, must correspond to valid file in dataset
- **bracken_file_id**: Non-empty string, must correspond to valid file in dataset
- **bracken_time_point**: Must be one of: `"pre_treatment"`, `"post_treatment"`, `"2-4_months"`

---

### **Phase 2: Extreme Points Selection**
**Step ID:** `extreme_points_selection`  
**Storage:** `pipeline_data.config['parameters']['extreme_points_selection']`

#### **Parameter Structure**
```python
{
    "selection_mode": str,         # Required: Selection method
    "top_percentage": float,       # Required: Percentage for late progressors
    "bottom_percentage": float,    # Required: Percentage for early progressors
    "time_variable": str,          # Optional: Clinical variable (default: "pfs_days")
    "linked_percentages": bool     # Optional: Link top/bottom percentages (default: true)
}
```

#### **Validation Rules**
- **selection_mode**: Must be one of: `"percentage_patients"`, `"percentage_range"`
- **top_percentage**: Float between 0 and 50 (exclusive)
- **bottom_percentage**: Float between 0 and 50 (exclusive)
- **time_variable**: Non-empty string, must exist in clinical data
- **linked_percentages**: Boolean value

---

### **Phase 3: Data Curation**
**Step ID:** `data_curation`  
**Storage:** `pipeline_data.config['parameters']['data_curation']`

#### **Parameter Structure**
```python
{
    "normalization_method": str,   # Optional: Normalization approach (default: "clr")
    "handle_missing_data": str,    # Optional: Missing data strategy (default: "impute")
    "quality_filters": dict,       # Optional: QC threshold dictionary
    "sample_matching": str,        # Optional: Sample matching method (default: "strict")
    "data_split_method": str       # Optional: Data splitting approach (default: "stratified")
}
```

#### **Validation Rules**
- **normalization_method**: Must be one of: `"clr"`, `"relative"`, `"tss"`, `"rarefaction"`
- **handle_missing_data**: Must be one of: `"impute"`, `"remove"`, `"ignore"`
- **quality_filters**: Dictionary with numeric threshold values
- **sample_matching**: Must be one of: `"strict"`, `"flexible"`, `"manual"`
- **data_split_method**: Must be one of: `"random"`, `"stratified"`, `"time_based"`, `"patient_based"`

---

### **Phase 4: Attribute Discarding (Variable Selection)**
**Step ID:** `attribute_discarding`  
**Storage:** `pipeline_data.config['parameters']['attribute_discarding']`

#### **Parameter Structure**
```python
{
    "selection_method": str,       # Required: Variable selection approach
    "target_n_taxa": int,          # Optional: Target number of taxa (default: 50)
    "prevalence_threshold": float, # Optional: Minimum prevalence (default: 0.1)
    "abundance_threshold": float,  # Optional: Minimum abundance (default: 0.001)
    "significance_threshold": float, # Optional: P-value threshold (default: 0.05)
    "clinical_covariates": list    # Optional: Clinical variables for adjustment
}
```

#### **Validation Rules**
- **selection_method**: Must be one of: `"prevalence"`, `"abundance"`, `"variance"`, `"univariate_pfs"`, `"multivariate_pfs"`, `"stability"`, `"information_theoretic"`, `"boruta"`, `"elastic_net"`, `"combined"`
- **target_n_taxa**: Integer ≥ 1
- **prevalence_threshold**: Float between 0 and 1
- **abundance_threshold**: Float > 0
- **significance_threshold**: Float between 0 and 1
- **clinical_covariates**: List of strings (clinical variable names)

---

### **Phase 5: Microbial Discarding**
**Step ID:** `microbial_discarding`  
**Storage:** `pipeline_data.config['parameters']['microbial_discarding']`

#### **Parameter Structure**
```python
{
    "selection_method": str,       # Optional: Microbial selection approach (default: "combined")
    "target_n_counts": int         # Optional: Target number of microbial counts (default: 50)
}
```

#### **Validation Rules**
- **selection_method**: Must be one of: `"prevalence"`, `"abundance"`, `"pfs_association"`, `"stability"`, `"combined"`
- **target_n_counts**: Integer ≥ 1

---

### **Phase 6: Attribute Group Selection**
**Step ID:** `attribute_group_selection`  
**Storage:** `pipeline_data.config['parameters']['attribute_group_selection']`

#### **Parameter Structure**
```python
{
    "selection_method": str,       # Required: Group selection approach
    "target_n_groups": int,        # Optional: Target number of groups (default: 5)
    "significance_threshold": float, # Optional: Significance threshold (default: 0.05)
    "stability_threshold": float,  # Optional: Bootstrap stability threshold (default: 0.7)
    "clinical_covariates": list    # Optional: Clinical variables for multivariate models
}
```

#### **Validation Rules**
- **selection_method**: Must be one of: `"univariate"`, `"multivariate"`, `"stability"`, `"boruta"`, `"consensus"`
- **target_n_groups**: Integer ≥ 1
- **significance_threshold**: Float between 0 and 1
- **stability_threshold**: Float between 0 and 1
- **clinical_covariates**: List of strings (clinical variable names)

---

### **Phase 7: Microbial Grouping**
**Step ID:** `microbial_grouping`  
**Storage:** `pipeline_data.config['parameters']['microbial_grouping']`

#### **Parameter Structure**
```python
{
    "grouping_strategy": str,      # Optional: Grouping approach (default: "scfa_producers")
    "custom_groups": dict          # Optional: Custom group definitions (default: {})
}
```

#### **Validation Rules**
- **grouping_strategy**: Must be one of: `"scfa_producers"`, `"pathogens"`, `"immunomodulators"`, `"bile_acid_metabolizers"`, `"butyrate_producers"`, `"custom"`
- **custom_groups**: Dictionary with group definitions (if grouping_strategy is "custom")

---

### **Phase 8: MVA Methods**
**Step ID:** `mva_methods`  
**Storage:** `pipeline_data.config['parameters']['mva_methods']`

#### **Parameter Structure**
```python
{
    "mva_method": str,             # Optional: Multivariate analysis method (default: "cox_regression")
    "clinical_covariates": list    # Optional: Clinical variables to include
}
```

#### **Validation Rules**
- **mva_method**: Must be one of: `"cox_regression"`, `"random_forest"`, `"neural_network"`, `"pls"`, `"svm"`, `"gradient_boosting"`
- **clinical_covariates**: List of strings (clinical variable names)

---

### **Phase 9: Population Subgroups Comparison**
**Step ID:** `population_subgroups`  
**Storage:** `pipeline_data.config['parameters']['population_subgroups']`

#### **Parameter Structure**
```python
{
    "subgroup_definitions": list,  # Optional: Subgroup variable names (default: ["age_groups", "smoking_status"])
    "min_subgroup_size": int       # Optional: Minimum samples per subgroup (default: 20)
}
```

#### **Validation Rules**
- **subgroup_definitions**: List of strings (clinical variable names for subgrouping)
- **min_subgroup_size**: Integer ≥ 5

---

### **Phase 10: Time Points Comparison**
**Step ID:** `timepoints_comparison`  
**Storage:** `pipeline_data.config['parameters']['timepoints_comparison']`

#### **Parameter Structure**
```python
{
    "timepoint_analyses": list,    # Optional: Time points to compare (default: ["pre_treatment", "2m_post", "24m_post"])
    "comparison_method": str       # Optional: Comparison approach (default: "meta_analysis")
}
```

#### **Validation Rules**
- **timepoint_analyses**: List of strings (valid time point identifiers)
- **comparison_method**: Must be one of: `"meta_analysis"`, `"effect_size_comparison"`, `"trajectory_analysis"`, `"clinical_relevance"`

---

### **Phase 11: Output Options**
**Step ID:** `output_options`  
**Storage:** `pipeline_data.config['parameters']['output_options']`

#### **Parameter Structure**
```python
{
    "output_formats": list,        # Optional: Output format types (default: ["statistical_report", "publication_figures"])
    "target_audience": str         # Optional: Target audience (default: "researchers")
}
```

#### **Validation Rules**
- **output_formats**: List containing any of: `"statistical_report"`, `"publication_figures"`, `"interactive_dashboard"`, `"data_package"`, `"clinical_summary"`, `"methods_compendium"`
- **target_audience**: Must be one of: `"researchers"`, `"clinicians"`, `"patients"`, `"administrators"`, `"general_public"`

---

## 🔍 **Parameter Validation Framework**

### **Global Validation Rules**
- **Presence validation**: Required parameters must exist
- **Type validation**: Parameters must be correct Python data types
- **Range validation**: Numeric parameters within acceptable bounds
- **Cross-validation**: Parameters consistent with each other
- **Dataset validation**: File IDs must correspond to actual dataset files

### **Validation Error Handling**
- **Missing parameters**: `ValueError` with descriptive message
- **Invalid values**: `ValueError` with validation details
- **Type mismatches**: `TypeError` with expected vs actual types
- **Range violations**: `ValueError` with acceptable range

### **Parameter State Management**
- **Initialization**: Parameters initialized with defaults on first access
- **Persistence**: Parameters survive pipeline serialization/deserialization
- **Updates**: Parameters can be modified between pipeline runs
- **Inheritance**: Downstream steps can access upstream parameters

---

## 📋 **Parameter Dependencies**

### **Sequential Dependencies**
- **Data Sources** parameters required before **Extreme Points** execution
- **Data Curation** parameters required before **Attribute Discarding** execution
- **Attribute Discarding** parameters required before **Attribute Group Selection** execution
- **Microbial Grouping** parameters required before **Attribute Group Selection** execution

### **Optional Dependencies**
- **Extreme Points** parameters enhance **Population Subgroups** analysis
- **Attribute Group Selection** parameters inform **MVA Methods** feature selection
- **MVA Methods** parameters influence **Output Options** format selection

---

## 🎯 **Parameter Change Events**

Each parameter save triggers a step-specific event for real-time UI updates:
- `DATA_SOURCE_CHANGED`: Data sources configuration modified
- `EXTREME_POINTS_CHANGED`: Extreme points selection parameters updated
- `DATA_CURATION_CHANGED`: Data curation settings changed
- `ATTRIBUTE_DISCARDING_CHANGED`: Variable selection parameters modified
- `MICROBIAL_DISCARDING_CHANGED`: Microbial selection parameters updated
- `ATTRIBUTE_GROUP_CHANGED`: Group selection parameters changed
- `MICROBIAL_GROUPING_CHANGED`: Microbial grouping strategy modified
- `MVA_METHODS_CHANGED`: Multivariate analysis method updated
- `POPULATION_SUBGROUPS_CHANGED`: Subgroup analysis parameters changed
- `TIMEPOINTS_COMPARISON_CHANGED`: Time point comparison settings modified
- `OUTPUT_OPTIONS_CHANGED`: Output format preferences updated

---

## 📊 **Parameter Audit Trail**

All parameter changes are logged in the provenance system:
```python
{
    "stage": "step_id",
    "action": "save_parameters",
    "parameters": { /* complete parameter set */ },
    "outcome": "success",
    "timestamp": "ISO8601_timestamp"
}
```

This comprehensive parameter specification ensures consistent configuration management across the entire microbiome analysis pipeline! 🔬⚙️📋