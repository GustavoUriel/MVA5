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
        'order': 1
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
        'order': 2
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
        'order': 3
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
        'order': 4
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
        'order': 5
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
        'order': 6
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
        'order': 7
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
        'order': 8
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
        'order': 9
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
        'order': 10
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