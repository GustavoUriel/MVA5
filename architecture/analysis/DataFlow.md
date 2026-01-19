# 00_DataFlow.md: Pipeline Data Structure and Flow Architecture

This document defines the **standardized data structure** that flows through the entire microbiome analysis pipeline and explains how data is stored, modified, and accumulated at each stage.

---

## 🎯 **Document Purpose**

This is the **technical specification** for implementing the modular microbiome analysis pipeline. It defines:
- The complete data structure architecture
- How data flows between pipeline stages
- Where each type of information is stored
- How stages interact with the data structure
- Individual taxa tracing capabilities
- Multi-method comparison framework

**Use this document when:** Building the pipeline implementation, debugging data flow issues, tracing individual microbes, or comparing analytical approaches.

Note: updated to reflect the pipeline stage names, data keys and provenance conventions used across the `architecture/analysis` step documents (110-410). The standardized `PipelineData` structure and the `taxa_provenance` schema match the other analysis documents for consistent implementation.

---

## 📊 **Core Design Principles**

### **1. Single Standardized Structure**
- **One data dictionary** flows through all pipeline stages
- **Consistent interface** for all methods and stages
- **No format transformations** needed between stages

### **2. Immutable Core Data**
- **Data section modified only once** during Data Curation stage
- **All subsequent stages preserve original data** for reproducibility
- **Analysis decisions tracked in metadata and results**

### **3. Accumulative Results**
- **Each stage adds information** without removing previous results
- **Complete analytical history preserved** for audit trail
- **Comprehensive provenance tracking** for reproducibility

### **4. Individual Taxa Traceability**
- **Every taxon tracked through entire pipeline**
- **Decision history recorded at each stage**
- **Group membership and exclusion reasons documented**

### **5. Multi-Method Consensus Framework**
- **Results from different methods comparable**
- **Consensus ranking across approaches**
- **Robust identification of top predictive features**

### **6. Researcher-Guided Analysis**
- **System provides tools and comparisons**, not automatic decisions
- **Researcher selects methods** and interprets results
- **Scientific judgment essential** for biological interpretation

---

## 🏗️ **Complete Data Structure Definition**

```python
PipelineData = {
    
    # ============================================
    # SECTION 1: CORE DATA
    # Modified only during Data Curation stage
    # ============================================
    "data": {
        "microbiome": DataFrame or None,    # Abundance/count data (taxa × samples)
        "clinical": DataFrame or None,      # Clinical metadata (samples × variables)
        "taxonomy": DataFrame or None       # Taxonomy assignments (taxa × ranks)
    },
    
    # ============================================
    # SECTION 2: METADATA
    # Processing history and quality information
    # ============================================
    "metadata": {
        "processing_history": [],           # List of completed stages in order
        "sample_info": {                    # Sample/taxon counts at current stage
            "n_samples": int,
            "n_taxa": int,
            "removed_samples": int,
            "removed_taxa": int
        },
        "data_quality": {},                 # QC results per stage
        "normalization": str or None,       # Applied normalization method
        "created_at": str,                  # Pipeline creation timestamp
        "version": str                      # Pipeline version number
    },
    
    # ============================================
    # SECTION 3: CONFIGURATION
    # Current stage settings
    # ============================================
    "config": {
        "stage_name": str or None,          # Current pipeline stage
        "parameters": {},                   # Stage-specific parameters
        "selected_methods": [],             # Chosen methods for current stage
        "random_seed": int,                 # For reproducibility (default: 42)
        "storage_mode": str                 # "full" or "lightweight"
    },
    
    # ============================================
    # SECTION 4: RESULTS (Stage-Organized)
    # Accumulated outputs from all stages
    # ============================================
    "results": {
        "data_curation": {
            "quality_metrics": {},          # Library sizes, rarefaction curves
            "normalization_info": {},       # Normalization parameters applied
            "contaminants_removed": []      # List of removed contaminant taxa
        },
        
        "microbial_grouping": {
            "group_definitions": {
                # Structure for each defined group
                "group_name": {
                    "description": str,              # Biological description
                    "selection_criteria": str,       # How taxa assigned
                    "literature_references": [],     # Supporting citations
                    "expected_pfs_relationship": str # Protective/risk/unknown
                }
            },
            "group_assignments": {
                # Taxon-to-group mappings
                "taxon_name": {
                    "assigned_groups": [],           # List of groups
                    "confidence_scores": {},         # Confidence per group
                    "assignment_method": str,        # How assigned
                    "timestamp": str                 # When assigned
                }
            },
            "taxa_coverage": {
                # How many taxa in each group
                "group_name": {
                    "n_taxa": int,
                    "taxa_list": [],
                    "prevalence_distribution": {}
                }
            }
        },
        
        "variable_selection": {
            "selection_results": {
                # Results from each selection method
                "method_name": {
                    "selected_taxa": [],             # Taxa passing filter
                    "excluded_taxa": [],             # Taxa failing filter
                    "selection_criteria": {},        # Thresholds used
                    "performance_metrics": {}        # Method-specific stats
                }
            },
            "selected_features": [],        # Final combined taxa list
            "method_comparison": {
                "overlap_matrix": {},       # Agreement between methods
                "consensus_taxa": [],       # Selected by all methods
                "controversial_taxa": []    # Selected by only some methods
            }
        },
        
        "variable_grouping": {
            "composite_features": {
                # Detailed structure for each composite
                "composite_name": {
                    "constituent_taxa": [],          # Taxa in this group
                    "aggregation_method": str,       # mean/pca/sum
                    "aggregated_data": Series,       # Combined values
                    "correlation_matrix": DataFrame, # Taxa intercorrelations
                    "variance_explained": float,     # % variance captured
                    "individual_contributions": {},  # Contribution per taxon
                    "biological_interpretation": str,
                    "timestamp": str
                }
            },
            "grouping_method": str,         # Overall approach used
            "variance_explained": {}        # Per-composite variance
        },
        
        "group_selection": {
            "selection_results": {
                # Results from each selection method
                "method_name": {
                    "selected_composites": [],
                    "excluded_composites": [],
                    "importance_scores": {},
                    "performance_metrics": {}
                }
            },
            "final_features": [],           # Selected composite list
            "importance_scores": {}         # Ranking of composites
        },
        
        "mva_methods": {
            "model_objects": {
                # Trained models (one per method)
                "method_name": Model_object
            },
            "performance_metrics": {
                # Performance evaluation (one per method)
                "method_name": {
                    "auroc": float,
                    "c_index": float,
                    "brier_score": float,
                    "log_likelihood": float,
                    "aic": float,
                    "bic": float,
                    "cross_validation": {
                        "mean_auroc": float,
                        "std_auroc": float,
                        "cv_folds": int
                    }
                }
            },
            "feature_importance": {
                # Feature importance per method
                "method_name": {
                    "feature_name": float  # Importance score
                }
            }
        },
        
        "output_options": {
            "exported_files": [],           # Paths to generated outputs
            "output_formats": [],           # Which formats created
            "publication_ready": bool       # All outputs generated
        },
        
        # NEW: Consensus analysis across all methods
        "consensus_analysis": {
            "standardized_scores": {
                # Normalized scores for each taxon across all methods
                "taxon_name": {
                    "cox_standardized": float,
                    "rf_standardized": float,
                    "nn_standardized": float,
                    "group_contributions": {},
                    "consensus_score": float,
                    "rank": int
                }
            },
            "method_agreement": {
                "perfect_agreement": [],     # Top in all methods
                "high_agreement": [],        # Top in most methods
                "moderate_agreement": [],    # Top in some methods
                "disagreement": []           # High in one, low in others
            },
            "top_n_rankings": {
                "top_10_microbes": [],
                "top_20_microbes": [],
                "ranking_details": {}
            },
            "robustness_metrics": {
                "consensus_stability": float,
                "method_correlation": float,
                "bootstrap_consistency": float
            }
        },
        
        # NEW: Focused analyses on specific groups
        "focused_analyses": {
            "composite_name": {
                "constituent_taxa_analysis": {},
                "individual_mva_results": {},
                "performance_comparison": {},
                "clinical_interpretation": str
            }
        }
    },
    
    # ============================================
    # SECTION 5: TAXA PROVENANCE (NEW)
    # Complete lifecycle tracking for each taxon
    # ============================================
    "taxa_provenance": {
        "taxon_name": {
            "initial_abundance": {
                "mean_relative_abundance": float,
                "prevalence": float,
                "detection_threshold": str
            },
            "microbial_grouping": {
                "assigned_groups": [],
                "group_confidence": {},
                "assignment_method": str,
                "assignment_timestamp": str
            },
            "variable_selection": {
                "methods_evaluated": {
                    "method_name": {
                        "passed": bool,
                        "criteria": str,
                        "score": float,
                        "p_value": float,
                        "reason": str
                    }
                },
                "final_decision": str,          # "included" or "excluded"
                "inclusion_reason": str or None,
                "exclusion_reason": str or None,
                "selection_timestamp": str
            },
            "variable_grouping": {
                "grouped_with": [],             # Other taxa in composite
                "composite_name": str or None,
                "grouping_method": str,
                "correlation_coefficient": float,
                "individual_contribution": float,
                "grouping_timestamp": str
            } or str,                           # "not_reached" if excluded earlier
            "group_selection": {
                "composite_evaluation": {},
                "final_composite_decision": str,
                "selection_timestamp": str
            } or str,                           # "not_reached" if excluded earlier
            "mva_analysis": {
                "method_name": {
                    "hazard_ratio": float,
                    "confidence_interval": list,
                    "p_value": float,
                    "feature_importance_rank": int,
                    "importance_score": float
                }
            } or str,                           # "not_reached" if excluded earlier
            "final_status": str,                # Final pipeline outcome
            "clinical_interpretation": str      # Biological/clinical meaning
        }
    },
    
    # ============================================
    # SECTION 6: CONTEXT (Working State)
    # What researcher is currently working with
    # ============================================
    "context": {
        "current_stage": str or None,       # Active pipeline stage
        "active_features": [],              # Currently selected taxa/groups
        "active_groups": {},                # Current group definitions in use
        "working_dataset": str,             # Which data version is active
        "previous_stages": []               # Chain of completed stages
    },
    
    # ============================================
    # SECTION 7: CHECKPOINTS
    # Save points for pipeline resumption
    # ============================================
    "checkpoints": {
        "stage_name": {
            "completed": bool,              # Whether stage finished successfully
            "timestamp": str,               # Completion timestamp
            "checkpoint_file": str,         # Path to saved checkpoint
            "can_resume_from": bool         # Whether resumption possible
        }
        # One entry per completed stage
    },
    
    # ============================================
    # SECTION 8: VALIDATION
    # Inter-stage requirements and checks
    # ============================================
    "validation": {
        "stage_requirements": {
            "stage_name": {
                "requires": [],             # Required data/results from prior stages
                "min_samples": int,         # Minimum sample size requirement
                "min_features": int,        # Minimum feature count requirement
                "data_types": []            # Required data types
            }
        },
        "validation_results": {
            "stage_name": {
                "passed": bool,             # Whether validation passed
                "warnings": [],             # Non-critical issues
                "errors": [],               # Critical issues blocking execution
                "recommendations": []       # Suggested improvements
            }
        }
    },
    
    # ============================================
    # SECTION 9: PERFORMANCE TRACKING
    # Computational resource usage
    # ============================================
    "performance": {
        "stage_timing": {
            "stage_name": {
                "start_time": str,          # Stage start timestamp
                "duration_seconds": float,  # Execution time
                "memory_peak_mb": float,    # Maximum memory usage
                "cpu_usage_percent": float  # Average CPU utilization
            }
        },
        "total_duration": float,            # Cumulative execution time
        "peak_memory_mb": float,            # Maximum memory across all stages
        "estimated_completion": str         # Predicted finish time (if running)
    },
    
    # ============================================
    # SECTION 10: USER ANNOTATIONS
    # Scientific reasoning and documentation
    # ============================================
    "annotations": {
        "stage_notes": {
            "stage_name": str               # Researcher notes about stage decisions
        },
        "feature_notes": {
            "feature_name": str             # Notes about specific taxa/groups
        },
        "decision_rationale": [
            {
                "stage": str,               # Which stage
                "decision": str,            # What was decided
                "reason": str,              # Why it was decided
                "alternatives_considered": [],  # Other options evaluated
                "impact": str               # Expected effect on results
            }
        ],
        "hypotheses": []                    # Research hypotheses being tested
    },
    
    # ============================================
    # SECTION 11: PROVENANCE
    # Complete audit trail
    # ============================================
    "provenance": {
        "input_files": [
            {
                "path": str,                # File path
                "format": str,              # File format
                "md5_hash": str,            # File integrity check
                "created": str              # File creation timestamp
            }
        ],
        "method_versions": {
            "library_name": str             # Software version (e.g., lifelines==0.27.0)
        },
        "parameters_used": {
            "stage_name": {}                # All parameters applied per stage
        },
        "execution_log": [
            {
                "timestamp": str,           # When action occurred
                "stage": str,               # Which stage
                "action": str,              # What happened
                "parameters": {},           # Parameters used
                "outcome": str              # Success/failure/warning
            }
        ]
    }
}
```

---

## 🔄 **Data Flow Through Pipeline Stages**

This section details exactly what data is added/modified at each stage.

### **Initial State: Empty Pipeline**

```python
PipelineData = {
    "data": {"microbiome": None, "clinical": None, "taxonomy": None},
    "metadata": {
        "processing_history": [],
        "created_at": "2026-01-12 15:30:00",
        "version": "1.0.0"
    },
    "config": {"random_seed": 42, "storage_mode": "full"},
    "results": {},
    "taxa_provenance": {},
    "context": {},
    "checkpoints": {},
    "validation": {},
    "performance": {},
    "annotations": {},
    "provenance": {"input_files": [], "execution_log": []}
}
```

---

### **Stage 1: Data Curation**

**INPUT:**
- Raw file paths in `config["parameters"]["input_files"]`
- Normalization method in `config["parameters"]["normalization"]`
- QC thresholds in `config["parameters"]["qc_thresholds"]`

**OPERATIONS:**
1. Load raw microbiome counts and clinical metadata
2. Apply quality control filters (min reads, prevalence)
3. Normalize abundance data (CLR, relative abundance, etc.)
4. Match samples between microbiome and clinical data
5. Initialize taxa provenance records

**DATA FILLED/MODIFIED:**

```python
# Core data populated (ONLY STAGE THAT MODIFIES THIS)
data["microbiome"] = normalized_abundance_dataframe
data["clinical"] = cleaned_clinical_dataframe
data["taxonomy"] = taxonomy_assignments_dataframe

# Metadata updated
metadata["processing_history"].append("data_curation")
metadata["sample_info"] = {
    "n_samples": 150,
    "n_taxa": 350,
    "removed_samples": 12,
    "removed_taxa": 85
}
metadata["normalization"] = "CLR"
metadata["data_quality"] = {
    "mean_library_size": 45000,
    "min_library_size": 12000,
    "max_library_size": 180000
}

# Results filled
results["data_curation"] = {
    "quality_metrics": {
        "pre_filter_taxa": 435,
        "post_filter_taxa": 350,
        "low_prevalence_removed": 75,
        "low_abundance_removed": 10
    },
    "normalization_info": {
        "method": "CLR",
        "parameters": {"pseudocount": 1}
    },
    "contaminants_removed": ["taxon_1", "taxon_2"]
}

# Taxa provenance initialized for each taxon
taxa_provenance["faecalibacterium_prausnitzii"] = {
    "initial_abundance": {
        "mean_relative_abundance": 0.025,
        "prevalence": 0.85,
        "detection_threshold": "present_in_85pct_samples"
    }
}
# ... (one entry per taxon)

# Provenance tracked
provenance["input_files"].append({
    "path": "raw_counts.csv",
    "format": "CSV",
    "md5_hash": "abc123...",
    "created": "2026-01-10"
})
provenance["execution_log"].append({
    "timestamp": "2026-01-12 15:35:00",
    "stage": "data_curation",
    "action": "normalization",
    "parameters": {"method": "CLR", "pseudocount": 1},
    "outcome": "success"
})

# Checkpoint saved
checkpoints["data_curation"] = {
    "completed": True,
    "timestamp": "2026-01-12 15:40:00",
    "checkpoint_file": "checkpoint_stage1.pkl",
    "can_resume_from": True
}

# Performance tracked
performance["stage_timing"]["data_curation"] = {
    "start_time": "2026-01-12 15:35:00",
    "duration_seconds": 300,
    "memory_peak_mb": 2048,
    "cpu_usage_percent": 75
}
```

---

### **Stage 2: Microbial Grouping**

**INPUT:**
- Curated data from `data["microbiome"]` and `data["taxonomy"]`
- Selected grouping categories in `config["parameters"]["grouping_categories"]`
- Custom group definitions (optional)

**OPERATIONS:**
1. Define functional microbial categories (SCFA producers, pathogens, etc.)
2. Assign each taxon to appropriate groups
3. Calculate group statistics and coverage
4. Update taxa provenance with group assignments

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["microbial_grouping"] = {
    "group_definitions": {
        "scfa_producers": {
            "description": "Bacteria producing short-chain fatty acids",
            "selection_criteria": "literature_based",
            "literature_references": ["Smith 2020", "Jones 2021"],
            "expected_pfs_relationship": "protective"
        },
        "pathogens": {
            "description": "Known pathogenic and opportunistic bacteria",
            "selection_criteria": "literature_based",
            "literature_references": ["Brown 2019"],
            "expected_pfs_relationship": "risk"
        }
    },
    "group_assignments": {
        "faecalibacterium_prausnitzii": {
            "assigned_groups": ["scfa_producers", "butyrate_producers"],
            "confidence_scores": {
                "scfa_producers": 0.95,
                "butyrate_producers": 0.90
            },
            "assignment_method": "literature_based",
            "timestamp": "2026-01-12 15:45:00"
        }
        # ... (one entry per taxon)
    },
    "taxa_coverage": {
        "scfa_producers": {
            "n_taxa": 45,
            "taxa_list": ["faecalibacterium_prausnitzii", ...],
            "prevalence_distribution": {"mean": 0.65, "std": 0.15}
        }
    }
}

# Taxa provenance updated for each taxon
taxa_provenance["faecalibacterium_prausnitzii"]["microbial_grouping"] = {
    "assigned_groups": ["scfa_producers", "butyrate_producers"],
    "group_confidence": {
        "scfa_producers": 0.95,
        "butyrate_producers": 0.90
    },
    "assignment_method": "literature_based",
    "assignment_timestamp": "2026-01-12 15:45:00"
}

# Context updated
context["active_groups"] = {
    "scfa_producers": ["faecalibacterium_prausnitzii", ...],
    "pathogens": [...]
}

# Metadata updated
metadata["processing_history"].append("microbial_grouping")

# Checkpoint and performance tracking...
```

---

### **Stage 3: Variable Selection**

**INPUT:**
- Curated data from `data["microbiome"]` and `data["clinical"]`
- Grouping information (optional)
- Selected methods in `config["selected_methods"]` (e.g., ["prevalence_filter", "pfs_univariate"])

**OPERATIONS:**
1. Apply each selection method independently
2. Record which taxa pass/fail each method
3. Combine results (intersection or union)
4. Update taxa provenance with selection decisions

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["variable_selection"] = {
    "selection_results": {
        "prevalence_filter": {
            "selected_taxa": ["faecalibacterium_prausnitzii", ...],
            "excluded_taxa": ["rare_taxon_1", ...],
            "selection_criteria": {"min_prevalence": 0.10},
            "performance_metrics": {
                "n_selected": 120,
                "n_excluded": 230
            }
        },
        "pfs_univariate": {
            "selected_taxa": ["faecalibacterium_prausnitzii", ...],
            "excluded_taxa": ["escherichia_coli", ...],
            "selection_criteria": {"p_threshold": 0.10},
            "performance_metrics": {
                "n_selected": 85,
                "n_excluded": 265,
                "mean_p_value": 0.045
            }
        }
    },
    "selected_features": [
        "faecalibacterium_prausnitzii",
        "bifidobacterium_longum",
        # ... final combined list (intersection or union)
    ],
    "method_comparison": {
        "overlap_matrix": {
            "prevalence_vs_pfs": 0.72  # 72% overlap
        },
        "consensus_taxa": ["faecalibacterium_prausnitzii", ...],  # In both
        "controversial_taxa": ["taxon_X", ...]  # Only in one method
    }
}

# Taxa provenance updated for EACH taxon
taxa_provenance["faecalibacterium_prausnitzii"]["variable_selection"] = {
    "methods_evaluated": {
        "prevalence_filter": {
            "passed": True,
            "criteria": "prevalence > 0.10",
            "score": 0.85,
            "reason": "high_prevalence"
        },
        "pfs_univariate": {
            "passed": True,
            "criteria": "p_value < 0.10",
            "score": 0.78,
            "p_value": 0.02,
            "hazard_ratio": 1.8,
            "reason": "significant_pfs_association"
        }
    },
    "final_decision": "included",
    "inclusion_reason": "passed_all_filters",
    "exclusion_reason": None,
    "selection_timestamp": "2026-01-12 16:00:00"
}

taxa_provenance["escherichia_coli"]["variable_selection"] = {
    "methods_evaluated": {
        "prevalence_filter": {
            "passed": True,
            "criteria": "prevalence > 0.10",
            "score": 0.45
        },
        "pfs_univariate": {
            "passed": False,
            "criteria": "p_value < 0.10",
            "score": 0.85,
            "p_value": 0.85,
            "hazard_ratio": 1.05,
            "reason": "no_significant_pfs_association"
        }
    },
    "final_decision": "excluded",
    "inclusion_reason": None,
    "exclusion_reason": "failed_pfs_univariate",
    "selection_timestamp": "2026-01-12 16:00:00"
}

# Context updated
context["active_features"] = [
    "faecalibacterium_prausnitzii",
    "bifidobacterium_longum",
    # ... selected taxa only
]

# Metadata updated
metadata["processing_history"].append("variable_selection")
metadata["sample_info"]["n_taxa"] = len(results["variable_selection"]["selected_features"])

# Checkpoint and performance tracking...
```

---

### **Stage 4: Variable Grouping**

**INPUT:**
- Selected features from `results["variable_selection"]["selected_features"]`
- Curated data for correlation analysis
- Grouping method in `config["parameters"]["grouping_method"]`

**OPERATIONS:**
1. Cluster correlated taxa into composite features
2. Calculate aggregated values (mean, PCA, etc.)
3. Track which taxa contribute to each composite
4. Update taxa provenance with grouping information

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["variable_grouping"] = {
    "composite_features": {
        "beneficial_bacteria_cluster": {
            "constituent_taxa": [
                "faecalibacterium_prausnitzii",
                "bifidobacterium_longum",
                "lactobacillus_rhamnosus",
                "akkermansia_muciniphila"
            ],
            "aggregation_method": "mean_abundance",
            "aggregated_data": pd.Series([...]),  # Combined values
            "correlation_matrix": pd.DataFrame([...]),  # Intercorrelations
            "variance_explained": 0.72,
            "individual_contributions": {
                "faecalibacterium_prausnitzii": 0.40,
                "bifidobacterium_longum": 0.30,
                "lactobacillus_rhamnosus": 0.18,
                "akkermansia_muciniphila": 0.12
            },
            "biological_interpretation": "SCFA-producing beneficial bacteria",
            "timestamp": "2026-01-12 16:15:00"
        },
        "pathogenic_cluster": {
            "constituent_taxa": ["escherichia_coli", "klebsiella_pneumoniae"],
            "aggregation_method": "pca_first_component",
            "aggregated_data": pd.Series([...]),
            "pca_loadings": {"escherichia_coli": 0.71, "klebsiella_pneumoniae": 0.71},
            "variance_explained": 0.65,
            "individual_contributions": {
                "escherichia_coli": 0.55,
                "klebsiella_pneumoniae": 0.45
            },
            "biological_interpretation": "Opportunistic pathogens",
            "timestamp": "2026-01-12 16:15:00"
        }
    },
    "grouping_method": "correlation_clustering",
    "variance_explained": {
        "beneficial_bacteria_cluster": 0.72,
        "pathogenic_cluster": 0.65
    }
}

# Taxa provenance updated for taxa that made it to this stage
taxa_provenance["faecalibacterium_prausnitzii"]["variable_grouping"] = {
    "grouped_with": [
        "bifidobacterium_longum",
        "lactobacillus_rhamnosus",
        "akkermansia_muciniphila"
    ],
    "composite_name": "beneficial_bacteria_cluster",
    "grouping_method": "correlation_clustering",
    "correlation_coefficient": 0.72,
    "individual_contribution": 0.40,
    "grouping_timestamp": "2026-01-12 16:15:00"
}

# For taxa excluded in variable selection
taxa_provenance["escherichia_coli"]["variable_grouping"] = "not_reached"

# Context updated
context["active_features"] = [
    "beneficial_bacteria_cluster",
    "pathogenic_cluster",
    # ... composite names now
]

# Metadata updated
metadata["processing_history"].append("variable_grouping")

# Checkpoint and performance tracking...
```

---

### **Stage 5: Group Selection**

**INPUT:**
- Composite features from `results["variable_grouping"]["composite_features"]`
- Selection methods in `config["selected_methods"]`

**OPERATIONS:**
1. Test each composite for PFS relevance
2. Rank composites by importance
3. Select final features for MVA
4. Update taxa provenance

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["group_selection"] = {
    "selection_results": {
        "univariate_screening": {
            "selected_composites": ["beneficial_bacteria_cluster"],
            "excluded_composites": ["pathogenic_cluster"],
            "importance_scores": {
                "beneficial_bacteria_cluster": 0.89,
                "pathogenic_cluster": 0.32
            },
            "performance_metrics": {
                "beneficial_bacteria_cluster": {"p_value": 0.005, "hr": 2.1},
                "pathogenic_cluster": {"p_value": 0.45, "hr": 1.2}
            }
        }
    },
    "final_features": ["beneficial_bacteria_cluster"],
    "importance_scores": {
        "beneficial_bacteria_cluster": 0.89
    }
}

# Taxa provenance updated for constituent taxa
taxa_provenance["faecalibacterium_prausnitzii"]["group_selection"] = {
    "composite_evaluation": {
        "univariate_screening": {
            "p_value": 0.005,
            "hazard_ratio": 2.1,
            "decision": "included"
        }
    },
    "final_composite_decision": "included",
    "selection_timestamp": "2026-01-12 16:30:00"
}

# Context updated
context["active_features"] = ["beneficial_bacteria_cluster"]

# Metadata updated
metadata["processing_history"].append("group_selection")

# Checkpoint and performance tracking...
```

---

### **Stage 6: MVA Methods**

**INPUT:**
- Clinical data with PFS outcomes from `data["clinical"]`
- Final features from `results["group_selection"]["final_features"]`
- Selected MVA methods in `config["selected_methods"]` (e.g., ["cox_regression", "random_forest"])

**OPERATIONS:**
1. Train each MVA model
2. Calculate performance metrics
3. Extract feature importance
4. Update taxa provenance with final results

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["mva_methods"] = {
    "model_objects": {
        "cox_regression": CoxPHFitter_trained_model,
        "random_forest": RandomForestSurvival_trained_model
    },
    "performance_metrics": {
        "cox_regression": {
            "auroc": 0.82,
            "c_index": 0.79,
            "brier_score": 0.16,
            "log_likelihood": -245.3,
            "aic": 498.6,
            "bic": 512.4,
            "cross_validation": {
                "mean_auroc": 0.80,
                "std_auroc": 0.04,
                "cv_folds": 5
            }
        },
        "random_forest": {
            "auroc": 0.85,
            "c_index": 0.82,
            "brier_score": 0.14,
            "oob_score": 0.83,
            "cross_validation": {
                "mean_auroc": 0.83,
                "std_auroc": 0.05,
                "cv_folds": 5
            }
        }
    },
    "feature_importance": {
        "cox_regression": {
            "beneficial_bacteria_cluster": 2.1,  # Hazard ratio
            "patient_age": -0.02,
            "iss_stage_3": -1.2
        },
        "random_forest": {
            "beneficial_bacteria_cluster": 0.45,  # Importance score 0-1
            "patient_age": 0.25,
            "iss_stage_3": 0.20
        }
    }
}

# Taxa provenance updated with MVA results
# Since composite was used, update each constituent taxon
for taxon in ["faecalibacterium_prausnitzii", "bifidobacterium_longum", ...]:
    taxa_provenance[taxon]["mva_analysis"] = {
        "cox_regression": {
            "hazard_ratio": 2.1,  # Composite HR
            "confidence_interval": [1.5, 2.9],
            "p_value": 0.005,
            "feature_importance_rank": 1,
            "note": "via_composite_beneficial_bacteria_cluster"
        },
        "random_forest": {
            "importance_score": 0.45,
            "feature_importance_rank": 1,
            "note": "via_composite_beneficial_bacteria_cluster"
        }
    }
    taxa_provenance[taxon]["final_status"] = "included_in_final_model"
    taxa_provenance[taxon]["clinical_interpretation"] = "Strong protective factor for PFS"

# Metadata updated
metadata["processing_history"].append("mva_methods")

# Checkpoint and performance tracking...
```

---

### **Stage 6b: Consensus Analysis (Automatic)**

**OPERATIONS:**
1. Standardize scores across all MVA methods
2. Calculate consensus rankings
3. Identify method agreement
4. Assess robustness

**DATA FILLED/MODIFIED:**

```python
# Results filled automatically after MVA stage
results["consensus_analysis"] = {
    "standardized_scores": {
        "faecalibacterium_prausnitzii": {
            "cox_standardized": 0.85,
            "rf_standardized": 0.45,
            "group_contributions": {
                "beneficial_bacteria_cluster": 0.40
            },
            "consensus_score": 0.78,
            "rank": 1
        },
        "bifidobacterium_longum": {
            "cox_standardized": 0.85,
            "rf_standardized": 0.45,
            "group_contributions": {
                "beneficial_bacteria_cluster": 0.30
            },
            "consensus_score": 0.71,
            "rank": 2
        }
        # ... for all taxa that reached MVA
    },
    "method_agreement": {
        "perfect_agreement": ["faecalibacterium_prausnitzii"],
        "high_agreement": ["bifidobacterium_longum", "lactobacillus_rhamnosus"],
        "moderate_agreement": [],
        "disagreement": []
    },
    "top_n_rankings": {
        "top_10_microbes": [
            "faecalibacterium_prausnitzii",
            "bifidobacterium_longum",
            "lactobacillus_rhamnosus",
            # ... top 10 by consensus score
        ],
        "ranking_details": {
            "faecalibacterium_prausnitzii": {
                "rank": 1,
                "consensus_score": 0.78,
                "method_scores": {"cox": 0.85, "rf": 0.45},
                "confidence": 0.95
            }
        }
    },
    "robustness_metrics": {
        "consensus_stability": 0.85,
        "method_correlation": 0.72,
        "bootstrap_consistency": 0.91
    }
}
```

---

### **Stage 7: Output Options**

**INPUT:**
- Complete pipeline data structure
- Selected output formats in `config["parameters"]["output_formats"]`

**OPERATIONS:**
1. Generate statistical reports
2. Create visualization plots
3. Export processed datasets
4. Document methodology

**DATA FILLED/MODIFIED:**

```python
# Results filled
results["output_options"] = {
    "exported_files": [
        "results/cox_regression_forest_plot.png",
        "results/consensus_ranking_table.csv",
        "results/taxa_provenance_report.html",
        "results/statistical_summary.pdf"
    ],
    "output_formats": [
        "statistical_report",
        "publication_figures",
        "interactive_dashboard"
    ],
    "publication_ready": True
}

# Metadata updated
metadata["processing_history"].append("output_options")

# Final checkpoint saved with complete pipeline
checkpoints["output_options"] = {
    "completed": True,
    "timestamp": "2026-01-12 17:00:00",
    "checkpoint_file": "checkpoint_final.pkl",
    "can_resume_from": True
}

# Total performance calculated
performance["total_duration"] = sum(
    stage["duration_seconds"] 
    for stage in performance["stage_timing"].values()
)
performance["peak_memory_mb"] = max(
    stage["memory_peak_mb"] 
    for stage in performance["stage_timing"].values()
)
```

---

## 🔍 **Querying Individual Taxa**

With the enhanced `taxa_provenance` section, you can trace any microbe through the entire pipeline:

### **Query 1: Where was a taxon excluded?**

```python
def find_exclusion_point(pipeline_data, taxon_name):
    """Find where and why a taxon was excluded"""
    record = pipeline_data["taxa_provenance"][taxon_name]
    
    if record["variable_selection"]["final_decision"] == "excluded":
        return {
            "stage": "variable_selection",
            "reason": record["variable_selection"]["exclusion_reason"],
            "methods_failed": [
                method for method, result in record["variable_selection"]["methods_evaluated"].items()
                if not result["passed"]
            ]
        }
    
    if isinstance(record["variable_grouping"], str) and record["variable_grouping"] == "not_reached":
        return {"stage": "excluded_before_grouping"}
    
    if record["group_selection"]["final_composite_decision"] == "excluded":
        return {
            "stage": "group_selection",
            "composite": record["variable_grouping"]["composite_name"]
        }
    
    return "Not excluded - included in final model"
```

### **Query 2: Get all groups a taxon belongs to**

```python
def get_taxon_groups(pipeline_data, taxon_name):
    """Get all groups a taxon was assigned to"""
    record = pipeline_data["taxa_provenance"][taxon_name]
    grouping = record.get("microbial_grouping", {})
    
    return {
        "assigned_groups": grouping.get("assigned_groups", []),
        "confidence_scores": grouping.get("group_confidence", {})
    }
```

### **Query 3: Get taxon's journey through pipeline**

```python
def trace_taxon_journey(pipeline_data, taxon_name):
    """Complete lifecycle trace of a taxon"""
    record = pipeline_data["taxa_provenance"][taxon_name]
    
    return {
        "initial_prevalence": record["initial_abundance"]["prevalence"],
        "groups": record["microbial_grouping"]["assigned_groups"],
        "variable_selection": record["variable_selection"]["final_decision"],
        "composite": record["variable_grouping"].get("composite_name") if isinstance(record["variable_grouping"], dict) else None,
        "group_selection": record["group_selection"].get("final_composite_decision") if isinstance(record["group_selection"], dict) else None,
        "mva_rank": record["mva_analysis"]["cox_regression"]["feature_importance_rank"] if isinstance(record["mva_analysis"], dict) else None,
        "final_status": record["final_status"],
        "clinical_interpretation": record["clinical_interpretation"]
    }
```

---

## 🎯 **Accessing Composite Constituents**

When you find a relevant composite group, extract its constituent taxa:

```python
def get_composite_constituents(pipeline_data, composite_name):
    """Get all taxa in a composite feature"""
    composites = pipeline_data["results"]["variable_grouping"]["composite_features"]
    composite_info = composites[composite_name]
    
    return {
        "constituent_taxa": composite_info["constituent_taxa"],
        "individual_contributions": composite_info["individual_contributions"],
        "variance_explained": composite_info["variance_explained"],
        "biological_interpretation": composite_info["biological_interpretation"]
    }
```

---

## 📊 **Multi-Method Comparison**

The `consensus_analysis` section enables robust identification of top microbes:

### **Get Top-N Most Relevant Microbes**

```python
def get_top_microbes(pipeline_data, n=10):
    """Get top N most PFS-relevant microbes by consensus"""
    consensus = pipeline_data["results"]["consensus_analysis"]
    
    return {
        "top_microbes": consensus["top_n_rankings"]["top_10_microbes"][:n],
        "ranking_details": consensus["top_n_rankings"]["ranking_details"],
        "method_agreement": consensus["method_agreement"],
        "robustness": consensus["robustness_metrics"]
    }
```

### **Compare Method Results**

```python
def compare_mva_methods(pipeline_data):
    """Compare performance across MVA methods"""
    metrics = pipeline_data["results"]["mva_methods"]["performance_metrics"]
    
    comparison = {}
    for method, perf in metrics.items():
        comparison[method] = {
            "auroc": perf["auroc"],
            "c_index": perf["c_index"],
            "cv_mean": perf["cross_validation"]["mean_auroc"],
            "cv_std": perf["cross_validation"]["std_auroc"]
        }
    
    return comparison
```

---

## 🏆 **Best Practices for Data Structure Usage**

### **1. Always Update Taxa Provenance**
Every stage that makes decisions about taxa MUST update `taxa_provenance` with:
- What criteria were evaluated
- Which criteria passed/failed
- Final decision and timestamp

### **2. Maintain Immutability of Core Data**
Only Data Curation modifies `data` section. All other stages read from `data`, write to `results`.

### **3. Use Checkpoints for Long Pipelines**
Save checkpoint after each stage to enable resumption without re-running expensive operations.

### **4. Document Decisions in Annotations**
Use `annotations` section to record scientific reasoning for method choices and interpretation.

### **5. Track Performance for Optimization**
Monitor `performance` section to identify bottlenecks and optimize resource allocation.

### **6. Validate Before Each Stage**
Check `validation["stage_requirements"]` before executing to catch configuration errors early.

---

## 📚 **Related Documentation**

- **00_ResultsComparison.md** - Detailed specifications for comparing multiple pipeline runs
- **00_DataAnalysis.md** - Overall pipeline architecture and philosophy
- **01_DataSourcesSelect.md** - Data source selection and validation
- **02_DataCuration.md** - Data processing methods
- **03_ExtremePointsSelection.md** - Extreme outcome patient selection
- **04_MicrobialGrouping.md** - Functional category definitions
- **05_VariableSelection.md** - Feature selection approaches
- **06_VariableGrouping.md** - Feature aggregation methods
- **07_GroupSelection.md** - Composite feature selection
- **08_MVAMethods.md** - Multivariate statistical approaches
- **09_OutputOptions.md** - Result presentation formats
- **10_PopulationSubgroupsComparison.md** - Population subgroup analysis
- **11_TimePointsComparison.md** - Cross-timepoint comparison analysis

---

## 🎯 **Summary**

This enhanced data structure provides:
- ✅ **Complete taxa traceability** through entire pipeline
- ✅ **Multi-method consensus ranking** for robust biomarker identification
- ✅ **Composite feature transparency** showing constituent taxa
- ✅ **Flexible comparison framework** for method evaluation
- ✅ **Production-ready architecture** for microbiome research

**Every taxon, every decision, every result is tracked, documented, and accessible!** 🔬📊🎯
