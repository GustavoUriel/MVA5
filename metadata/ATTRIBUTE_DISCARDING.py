ATTRIBUTE_DISCARDING = {
    'prevalence_filtering': {
        'name': 'Prevalence Filtering',
        'description': 'Discard taxa present in fewer than a specified percentage of samples',
        'parameters': {
            'detection_threshold': {
                'type': 'float',
                'default': 0.0,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Detection Threshold',
                'description': 'Minimum abundance to consider taxon present (default: >0)'
            },
            'min_prevalence': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 1.0,
                'step': 0.01,
                'label': 'Minimum Prevalence (%)',
                'description': 'Minimum fraction of samples where taxon must be present'
            }
        },
        'enabled': False,
        'order': 1,
        'info': {
            'title': 'Prevalence Filtering',
            'description': 'Discard taxa present in fewer than a specified percentage of samples, removing unreliable measurements.',
            'algorithm': 'For each taxon: prevalence = (abundance > detection_threshold).sum() / total_samples; if prevalence < min_prevalence_threshold: discard_taxon',
            'parameters': [
                {'name': 'Detection threshold', 'default': '>0', 'description': 'Minimum abundance to consider taxon present'},
                {'name': 'Minimum prevalence', 'default': '10% of samples', 'description': 'Minimum fraction of samples where taxon must be present'}
            ],
            'pros': [
                'Data quality control - Eliminates measurement artifacts and rare taxa',
                'Statistical reliability - Focuses on consistently detectable microbes',
                'Computational efficiency - Reduces dataset size significantly',
                'Reproducibility - Removes taxa with unreliable abundance estimates',
                'Simple implementation - Easy to understand and apply'
            ],
            'cons': [
                'May discard important taxa - Some biologically relevant microbes may be rare',
                'Arbitrary thresholds - Prevalence cutoff is subjective',
                'Context dependence - Optimal prevalence varies by study design and technology',
                'False negatives - Rare pathogens or keystone species may be excluded'
            ],
            'limitations': [
                'Doesn\'t consider abundance levels, only presence/absence',
                'May be too conservative for some research questions',
                'Threshold selection requires biological knowledge'
            ],
            'expectations': 'Reduces taxa count by 20-60%, depending on threshold'
        }
    },

    'abundance_filtering': {
        'name': 'Abundance Filtering',
        'description': 'Discard taxa with consistently low abundance across samples',
        'parameters': {
            'min_mean_abundance': {
                'type': 'float',
                'default': 0.0001,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Mean Abundance (%)',
                'description': 'Minimum mean relative abundance threshold'
            },
            'min_median_abundance': {
                'type': 'float',
                'default': 0.00005,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Median Abundance (%)',
                'description': 'Minimum median relative abundance threshold'
            }
        },
        'enabled': False,
        'order': 2,
        'info': {
            'title': 'Abundance Filtering',
            'description': 'Discard taxa with consistently low abundance across samples, focusing on ecologically important microbes.',
            'algorithm': 'For each taxon: mean_abundance = taxon_abundances.mean(); median_abundance = taxon_abundances.median(); if mean_abundance < min_mean_threshold or median_abundance < min_median_threshold: discard_taxon',
            'parameters': [
                {'name': 'Minimum mean abundance', 'default': '0.01% relative abundance', 'description': 'Minimum mean relative abundance threshold'},
                {'name': 'Minimum median abundance', 'default': '0.005% relative abundance', 'description': 'Minimum median relative abundance threshold'}
            ],
            'pros': [
                'Ecological relevance - Focuses on microbes that contribute meaningfully to community',
                'Measurement precision - Removes taxa near detection limits',
                'Biological signal - Prioritizes microbes with functional impact',
                'Data normalization - Complements relative abundance transformations',
                'Statistical power - Reduces noise in downstream analyses'
            ],
            'cons': [
                'Context dependence - Abundance thresholds vary by sample type and technology',
                'Functional bias - May exclude important low-abundance functional specialists',
                'Normalization effects - Results depend on abundance transformation method',
                'Sample variability - Abundance distributions vary across studies'
            ],
            'limitations': [
                'Requires appropriate abundance normalization (relative abundance, CLR, etc.)',
                'May miss conditionally abundant taxa (bloomers under specific conditions)',
                'Thresholds need validation against biological knowledge'
            ],
            'expectations': 'Further reduces taxa count by 10-40%, depending on thresholds'
        }
    },

    'variance_based_selection': {
        'name': 'Variance-Based Selection',
        'description': 'Select taxa with highest variance across samples',
        'parameters': {
            'num_taxa_to_select': {
                'type': 'int',
                'default': 50,
                'min': 5,
                'max': 200,
                'step': 5,
                'label': 'Number of Taxa to Select',
                'description': 'Maximum number of most variable taxa to retain'
            },
            'variance_metric': {
                'type': 'select',
                'default': 'coefficient_of_variation',
                'options': [
                    {'value': 'total_variance', 'label': 'Total Variance'},
                    {'value': 'coefficient_of_variation', 'label': 'Coefficient of Variation'}
                ],
                'label': 'Variance Metric',
                'description': 'Method to measure taxon variability'
            }
        },
        'enabled': False,
        'order': 3,
        'info': {
            'title': 'Variance-Based Selection',
            'description': 'Select taxa with highest variance across samples, identifying microbes that differ between patients or conditions.',
            'algorithm': 'For each taxon: variance = taxon_abundances.var(); coefficient_of_variation = variance / mean_abundance; rank_taxa_by_variance(); select_top_n_most_variable()',
            'parameters': [
                {'name': 'Number of taxa to select', 'default': '50', 'description': 'Maximum number of most variable taxa to retain'},
                {'name': 'Variance metric', 'default': 'Coefficient of Variation', 'description': 'Method to measure taxon variability'}
            ],
            'pros': [
                'Biological heterogeneity - Identifies taxa that vary between individuals',
                'Condition differences - Captures microbes that change with disease states',
                'Data-driven - No biological assumptions required',
                'Quality indicator - High variance suggests reliable measurements',
                'Exploratory power - Reveals major sources of microbiome variation'
            ],
            'cons': [
                'No clinical relevance - Doesn\'t consider relationship to outcomes',
                'Noise sensitivity - Technical variation can inflate variance',
                'Scale dependence - Affected by abundance transformations',
                'Arbitrary selection - "Top N" is subjective',
                'Context ignorance - May select taxa varying for non-biological reasons'
            ],
            'limitations': [
                'Doesn\'t distinguish biological from technical variation',
                'Rare taxa may appear highly variable due to sparsity',
                'Selection depends on study population characteristics'
            ],
            'expectations': 'Selects 20-100 most variable taxa from the microbial group'
        }
    },

    'univariate_pfs_screening': {
        'name': 'Univariate PFS Screening',
        'description': 'Test each taxon individually against PFS using statistical models',
        'parameters': {
            'statistical_test': {
                'type': 'select',
                'default': 'cox_regression',
                'options': [
                    {'value': 'cox_regression', 'label': 'Cox Regression'},
                    {'value': 'log_rank_test', 'label': 'Log-Rank Test'}
                ],
                'label': 'Statistical Test',
                'description': 'Method for testing PFS association'
            },
            'significance_threshold': {
                'type': 'float',
                'default': 0.05,
                'min': 0.001,
                'max': 0.2,
                'step': 0.001,
                'label': 'Significance Threshold',
                'description': 'P-value threshold for significance'
            },
            'multiple_testing_correction': {
                'type': 'select',
                'default': 'fdr',
                'options': [
                    {'value': 'none', 'label': 'None'},
                    {'value': 'bonferroni', 'label': 'Bonferroni'},
                    {'value': 'fdr', 'label': 'False Discovery Rate'}
                ],
                'label': 'Multiple Testing Correction',
                'description': 'Method to correct for multiple hypothesis testing'
            }
        },
        'enabled': False,
        'order': 4,
        'info': {
            'title': 'Univariate PFS Screening',
            'description': 'Test each taxon individually against PFS using statistical models, keeping only those showing significant associations.',
            'algorithm': 'For each taxon: model = fit_statistical_model(pfs_outcomes, taxon_abundance); if p_value < significance_threshold: keep_taxon',
            'parameters': [
                {'name': 'Statistical test', 'default': 'Cox Regression', 'description': 'Method for testing PFS association'},
                {'name': 'Significance threshold', 'default': 'p < 0.05', 'description': 'P-value threshold for significance'},
                {'name': 'Multiple testing correction', 'default': 'FDR', 'description': 'Method to correct for multiple hypothesis testing'}
            ],
            'pros': [
                'Direct clinical relevance - Only keeps taxa associated with outcomes',
                'Statistical rigor - Formal hypothesis testing for each taxon',
                'Easy interpretation - Clear inclusion criteria',
                'Biological insight - Reveals which microbes matter for disease progression',
                'Flexible thresholds - Can adjust stringency based on study goals'
            ],
            'cons': [
                'Ignores interactions - May miss taxa significant only in combination',
                'Multiple testing issues - Risk of false positives without correction',
                'Conservative approach - May exclude taxa with weak individual effects',
                'Sample size dependence - Power varies with number of events',
                'Context independence - Doesn\'t account for clinical covariates'
            ],
            'limitations': [
                'Requires sufficient PFS events for statistical power',
                'May miss synergistic effects between taxa',
                'Results sensitive to censoring patterns'
            ],
            'expectations': 'Retains 5-30% of taxa showing PFS associations'
        }
    },

    'multivariate_pfs_screening': {
        'name': 'Multivariate PFS Screening',
        'description': 'Test taxa in multivariate models including clinical variables',
        'parameters': {
            'significance_threshold': {
                'type': 'float',
                'default': 0.05,
                'min': 0.001,
                'max': 0.2,
                'step': 0.001,
                'label': 'Significance Threshold',
                'description': 'P-value threshold for significance after clinical adjustment'
            },
            'regularization_strength': {
                'type': 'float',
                'default': 0.1,
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'label': 'Regularization Strength',
                'description': 'Penalty strength for numerical stability'
            },
            'max_iterations': {
                'type': 'int',
                'default': 10,
                'min': 1,
                'max': 50,
                'step': 1,
                'label': 'Maximum Iterations',
                'description': 'Maximum iterations for iterative refinement'
            },
            'min_taxa_retain': {
                'type': 'int',
                'default': 5,
                'min': 1,
                'max': 20,
                'step': 1,
                'label': 'Minimum Taxa to Retain',
                'description': 'Minimum number of taxa to keep for model stability'
            }
        },
        'enabled': False,
        'order': 5,
        'info': {
            'title': 'Multivariate PFS Screening',
            'description': 'Test taxa in multivariate models including clinical variables, selecting those significant after adjusting for confounders.',
            'algorithm': 'Fit full multivariate model: PFS ~ clinical_vars + all_taxa; Extract significant taxa (p < 0.05 after clinical adjustment)',
            'parameters': [
                {'name': 'Significance threshold', 'default': 'p < 0.05', 'description': 'P-value threshold for significance after clinical adjustment'},
                {'name': 'Regularization strength', 'default': '0.1', 'description': 'Penalty strength for numerical stability'},
                {'name': 'Maximum iterations', 'default': '10', 'description': 'Maximum iterations for iterative refinement'},
                {'name': 'Minimum taxa to retain', 'default': '5', 'description': 'Minimum number of taxa to keep for model stability'}
            ],
            'pros': [
                'Clinically realistic - Considers clinical context and confounding',
                'Context-aware - Identifies taxa significant beyond clinical factors',
                'Multivariate validity - Accounts for taxon intercorrelations',
                'Clinical translation - Results relevant for patient stratification',
                'Confounding control - Adjusts for known clinical predictors'
            ],
            'cons': [
                'Computational intensity - Requires fitting large multivariate models',
                'Parameter instability - Large models can be numerically unstable',
                'Clinical variable dependence - Results depend on which covariates are included',
                'Overfitting risk - Too many taxa relative to sample size',
                'Interpretation complexity - Hard to attribute effects to individual taxa'
            ],
            'limitations': [
                'Requires sufficient sample size for multivariate model stability',
                'Sensitive to multicollinearity between taxa and clinical variables',
                'Clinical covariate selection affects which taxa appear significant'
            ],
            'expectations': 'Retains 3-15 taxa significant in multivariate clinical context'
        }
    },

    'stability_selection': {
        'name': 'Stability Selection',
        'description': 'Use bootstrap resampling to identify taxa with consistently significant PFS associations',
        'parameters': {
            'num_bootstraps': {
                'type': 'int',
                'default': 100,
                'min': 50,
                'max': 1000,
                'step': 50,
                'label': 'Number of Bootstraps',
                'description': 'Number of bootstrap samples for stability assessment'
            },
            'stability_threshold': {
                'type': 'float',
                'default': 0.7,
                'min': 0.5,
                'max': 0.95,
                'step': 0.05,
                'label': 'Stability Threshold',
                'description': 'Minimum fraction of bootstraps where taxon must be significant'
            },
            'bootstrap_sample_size': {
                'type': 'float',
                'default': 0.8,
                'min': 0.5,
                'max': 1.0,
                'step': 0.05,
                'label': 'Bootstrap Sample Size (%)',
                'description': 'Fraction of original sample size for each bootstrap'
            }
        },
        'enabled': False,
        'order': 6,
        'info': {
            'title': 'Stability Selection',
            'description': 'Use bootstrap resampling to identify taxa with consistently significant PFS associations across multiple subsamples.',
            'algorithm': 'For each bootstrap sample: fit PFS model; calculate stability scores based on consistency across bootstraps; select taxa above stability threshold',
            'parameters': [
                {'name': 'Number of bootstraps', 'default': '100', 'description': 'Number of bootstrap samples for stability assessment'},
                {'name': 'Stability threshold', 'default': '0.7', 'description': 'Minimum fraction of bootstraps where taxon must be significant'},
                {'name': 'Bootstrap sample size', 'default': '80%', 'description': 'Fraction of original sample size for each bootstrap'}
            ],
            'pros': [
                'Robust identification - Finds consistently associated taxa',
                'Controls overfitting - Reduces false positive selections',
                'Uncertainty quantification - Provides confidence in selections',
                'Cross-validation built-in - Bootstrap validation of associations',
                'Sample variability - Accounts for population heterogeneity'
            ],
            'cons': [
                'Computationally expensive - Requires many model fits',
                'Time-intensive - May take hours for large taxon sets',
                'Parameter dependence - Stability threshold affects results',
                'Conservative bias - May miss taxa with moderate associations'
            ],
            'limitations': [
                'Requires sufficient sample size for meaningful bootstrapping',
                'Assumes bootstrap samples represent population characteristics',
                'May be overly conservative for small datasets',
                'Computational cost scales with number of taxa'
            ],
            'expectations': 'Identifies 5-20 taxa with high stability scores (70%+ consistency)'
        }
    },

    'information_theoretic_selection': {
        'name': 'Information-Theoretic Selection',
        'description': 'Select taxa based on mutual information with PFS outcomes',
        'parameters': {
            'mi_estimator': {
                'type': 'select',
                'default': 'knn',
                'options': [
                    {'value': 'histogram', 'label': 'Histogram-based'},
                    {'value': 'knn', 'label': 'K-Nearest Neighbors'}
                ],
                'label': 'Mutual Information Estimator',
                'description': 'Method for estimating mutual information'
            },
            'num_permutations': {
                'type': 'int',
                'default': 1000,
                'min': 100,
                'max': 10000,
                'step': 100,
                'label': 'Number of Permutations',
                'description': 'Number of permutations for significance testing'
            },
            'significance_threshold': {
                'type': 'float',
                'default': 0.05,
                'min': 0.001,
                'max': 0.2,
                'step': 0.001,
                'label': 'Significance Threshold',
                'description': 'P-value threshold for significance'
            }
        },
        'enabled': False,
        'order': 7,
        'info': {
            'title': 'Information-Theoretic Selection',
            'description': 'Select taxa based on mutual information with PFS outcomes, capturing non-linear and complex relationships.',
            'algorithm': 'For each taxon: calculate mutual information I(taxon_abundance; pfs_outcome); test significance against null distribution',
            'parameters': [
                {'name': 'Mutual information estimator', 'default': 'K-Nearest Neighbors', 'description': 'Method for estimating mutual information'},
                {'name': 'Number of permutations', 'default': '1000', 'description': 'Number of permutations for significance testing'},
                {'name': 'Significance threshold', 'default': 'p < 0.05', 'description': 'P-value threshold for significance'}
            ],
            'pros': [
                'Non-linear relationships - Captures complex taxon-PFS associations',
                'No distribution assumptions - Works with any abundance distribution',
                'Information-theoretic foundation - Solid theoretical basis',
                'Model independence - Doesn\'t assume specific relationship form',
                'Robust to outliers - Less sensitive to extreme values'
            ],
            'cons': [
                'Computational cost - Especially for continuous variables',
                'Estimator sensitivity - Results depend on binning or k parameter',
                'Limited interpretability - MI scores don\'t indicate relationship direction',
                'Multiple testing - Requires careful correction for many taxa'
            ],
            'limitations': [
                'Requires sufficient sample size for reliable MI estimation',
                'Sensitive to discretization parameters for continuous variables',
                'Doesn\'t provide effect size or relationship direction',
                'May select redundant taxa with similar information content'
            ],
            'expectations': 'Selects 10-40 taxa with significant information shared with PFS'
        }
    },

    'boruta_algorithm': {
        'name': 'Boruta Algorithm',
        'description': 'Iterative algorithm using random forest to identify all features with predictive relevance',
        'parameters': {
            'num_shadow_features': {
                'type': 'int',
                'default': 3,
                'min': 1,
                'max': 10,
                'step': 1,
                'label': 'Shadow Features per Real Feature',
                'description': 'Number of randomized shadow features to create'
            },
            'max_iterations': {
                'type': 'int',
                'default': 100,
                'min': 10,
                'max': 1000,
                'step': 10,
                'label': 'Maximum Iterations',
                'description': 'Maximum iterations for Boruta algorithm'
            },
            'rf_num_trees': {
                'type': 'int',
                'default': 1000,
                'min': 100,
                'max': 10000,
                'step': 100,
                'label': 'Random Forest Trees',
                'description': 'Number of trees in random forest'
            }
        },
        'enabled': False,
        'order': 8,
        'info': {
            'title': 'Boruta Algorithm',
            'description': 'Iterative algorithm using random forest to identify all features with predictive relevance, not just the strongest ones.',
            'algorithm': 'Add shadow features; train random forest; compare real vs shadow feature importance; iteratively remove features less important than best shadow',
            'parameters': [
                {'name': 'Shadow features per real feature', 'default': '3', 'description': 'Number of randomized shadow features to create'},
                {'name': 'Maximum iterations', 'default': '100', 'description': 'Maximum iterations for Boruta algorithm'},
                {'name': 'Random forest trees', 'default': '1000', 'description': 'Number of trees in random forest'}
            ],
            'pros': [
                'All-relevant selection - Finds all predictive taxa, not just top performers',
                'Statistical foundation - Uses permutation testing for significance',
                'Handles correlations - Works well with correlated microbial features',
                'Robust to overfitting - Ensemble method reduces variance',
                'No parameter tuning - Algorithm determines optimal feature set'
            ],
            'cons': [
                'Computationally intensive - Multiple random forest trainings',
                'Time-consuming - May take significant time for large datasets',
                'Memory intensive - Random forest objects for each iteration',
                'Random forest dependence - Results depend on RF implementation',
                'May be overly inclusive - Includes marginally relevant features'
            ],
            'limitations': [
                'Requires sufficient sample size for stable random forest importance',
                'May be conservative in small datasets',
                'Computational requirements may be prohibitive for very large feature sets'
            ],
            'expectations': 'Selects 15-50 taxa with confirmed predictive relevance'
        }
    },

    'elastic_net_regularization': {
        'name': 'Elastic Net Regularization',
        'description': 'Use L1/L2 regularized regression to automatically select taxa with PFS predictive value',
        'parameters': {
            'l1_ratio': {
                'type': 'float',
                'default': 0.5,
                'min': 0.0,
                'max': 1.0,
                'step': 0.1,
                'label': 'L1 Ratio',
                'description': 'Balance between L1 (0) and L2 (1) regularization'
            },
            'max_iterations': {
                'type': 'int',
                'default': 1000,
                'min': 100,
                'max': 10000,
                'step': 100,
                'label': 'Maximum Iterations',
                'description': 'Maximum iterations for optimization'
            },
            'convergence_tolerance': {
                'type': 'float',
                'default': 1e-4,
                'min': 1e-8,
                'max': 1e-2,
                'step': 1e-5,
                'label': 'Convergence Tolerance',
                'description': 'Tolerance for convergence in optimization'
            }
        },
        'enabled': False,
        'order': 9,
        'info': {
            'title': 'Elastic Net Regularization',
            'description': 'Use L1/L2 regularized regression to automatically select taxa with PFS predictive value through coefficient shrinkage.',
            'algorithm': 'Optimize elastic net: minimize loss + λ₁||β||₁ + λ₂||β||₂; select taxa with non-zero coefficients',
            'parameters': [
                {'name': 'L1 ratio', 'default': '0.5', 'description': 'Balance between L1 (0) and L2 (1) regularization'},
                {'name': 'Maximum iterations', 'default': '1000', 'description': 'Maximum iterations for optimization'},
                {'name': 'Convergence tolerance', 'default': '1e-4', 'description': 'Tolerance for convergence in optimization'}
            ],
            'pros': [
                'Automated selection - No manual threshold setting required',
                'Handles correlations - L2 component manages multicollinear taxa',
                'Continuous selection - Gradual elimination rather than hard cutoffs',
                'Cross-validation built-in - Automatic parameter optimization',
                'Predictive focus - Selects for outcome prediction performance'
            ],
            'cons': [
                'Model dependence - Results depend on chosen base model',
                'Linear assumptions - Assumes linear relationships for selection',
                'Parameter sensitivity - Regularization balance affects results',
                'May miss weak signals - Conservative selection approach',
                'Computational cost - Especially for large feature sets'
            ],
            'limitations': [
                'Requires specification of base regression model',
                'Selection depends on regularization parameter choice',
                'May not capture non-linear taxon-PFS relationships',
                'Cross-validation can be computationally expensive'
            ],
            'expectations': 'Selects 5-25 taxa with non-zero coefficients in regularized model'
        }
    },

    'combined_multi_method': {
        'name': 'Combined Multi-Method Selection',
        'description': 'Apply multiple selection methods and take consensus to identify robustly selected taxa',
        'parameters': {
            'consensus_rule': {
                'type': 'select',
                'default': 'intersection',
                'options': [
                    {'value': 'intersection', 'label': 'Intersection (ALL methods)'},
                    {'value': 'union', 'label': 'Union (ANY method)'},
                    {'value': 'weighted', 'label': 'Weighted Voting'}
                ],
                'label': 'Consensus Rule',
                'description': 'How to combine results from multiple methods'
            },
            'min_agreement': {
                'type': 'int',
                'default': 2,
                'min': 1,
                'max': 5,
                'step': 1,
                'label': 'Minimum Agreement',
                'description': 'Minimum number of methods that must agree (for weighted voting)'
            }
        },
        'enabled': False,
        'order': 10,
        'info': {
            'title': 'Combined Multi-Method Selection',
            'description': 'Apply multiple selection methods and take consensus to identify robustly selected taxa.',
            'algorithm': 'Apply multiple methods; take intersection/union/weighted consensus of selected taxa',
            'parameters': [
                {'name': 'Consensus rule', 'default': 'Intersection', 'description': 'How to combine results from multiple methods'},
                {'name': 'Minimum agreement', 'default': '2', 'description': 'Minimum number of methods that must agree'}
            ],
            'pros': [
                'Robust selection - Taxa selected by multiple methods are more reliable',
                'Method validation - Cross-validation of different approaches',
                'Comprehensive coverage - Captures different types of associations',
                'Uncertainty reduction - Reduces method-specific biases',
                'Confidence building - Multiple lines of evidence for selected taxa'
            ],
            'cons': [
                'Computational cost - Running multiple methods increases time',
                'Result complexity - Different methods may give different answers',
                'Decision complexity - Choosing how to combine results',
                'Conservative bias - Strict consensus may miss valid taxa',
                'Method dependence - Results depend on which methods are combined'
            ],
            'limitations': [
                'Requires careful consideration of which methods to combine',
                'Consensus rules are somewhat arbitrary',
                'May miss taxa only detectable by specific methods',
                'Interpretation becomes more complex'
            ],
            'expectations': 'Highly confident selection of 5-20 taxa supported by multiple methods'
        }
    }
}

# Default settings for quick start
DEFAULT_DISCARDING_SETTINGS = {
    'prevalence_filtering': {
        'enabled': True,
        'detection_threshold': 0.0,
        'min_prevalence': 0.1
    },
    'abundance_filtering': {
        'enabled': True,
        'min_mean_abundance': 0.0001,
        'min_median_abundance': 0.00005
    }
}