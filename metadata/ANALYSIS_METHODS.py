ANALYSIS_METHODS = {
    'cox_proportional_hazards': {
        'name': 'Cox Proportional Hazards Regression',
        'description': 'Semi-parametric survival analysis method that models the hazard ratio as a function of covariates while allowing the baseline hazard to be unspecified.',
        'category': 'Survival Analysis',
        'parameters': {
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty to prevent overfitting'
            },
            'l1_ratio': {
                'name': 'L1 Ratio',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.1,
                'default': 0.0,
                'description': 'Ratio of L1 to L2 penalty (0 = pure L2, 1 = pure L1)'
            },
            'max_iter': {
                'name': 'Maximum Iterations',
                'type': 'number',
                'min': 100,
                'max': 10000,
                'step': 100,
                'default': 1000,
                'description': 'Maximum number of iterations for convergence'
            },
            'tolerance': {
                'name': 'Convergence Tolerance',
                'type': 'number',
                'min': 1e-8,
                'max': 1e-3,
                'step': 1e-4,
                'default': 1e-6,
                'description': 'Tolerance for convergence criteria'
            }
        },
        'pros': [
            'Handles censored data naturally',
            'No assumptions about baseline hazard distribution',
            'Provides hazard ratios for easy interpretation',
            'Can handle time-dependent covariates',
            'Robust to outliers in survival times'
        ],
        'cons': [
            'Assumes proportional hazards assumption',
            'Requires sufficient events for stable estimates',
            'Can be sensitive to model specification',
            'May not perform well with very small sample sizes'
        ],
        'use_cases': [
            'Identifying risk factors for survival',
            'Comparing treatment effects on survival',
            'Building predictive models for time-to-event outcomes',
            'Adjusting for confounding variables'
        ]
    },
    
    'accelerated_failure_time': {
        'name': 'Accelerated Failure Time (AFT) Model',
        'description': 'Parametric survival analysis method that models the logarithm of survival time as a linear function of covariates.',
        'category': 'Survival Analysis',
        'parameters': {
            'distribution': {
                'name': 'Distribution',
                'type': 'select',
                'options': ['weibull', 'exponential', 'log-normal', 'log-logistic'],
                'default': 'weibull',
                'description': 'Parametric distribution for survival times'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty'
            }
        },
        'pros': [
            'Provides time ratios (easier interpretation than hazard ratios)',
            'Can model the full survival distribution',
            'More efficient than Cox when distribution is correctly specified',
            'Handles censored data well'
        ],
        'cons': [
            'Requires correct specification of survival distribution',
            'Less flexible than Cox regression',
            'Sensitive to distributional assumptions',
            'May not fit well if data doesn\'t follow assumed distribution'
        ],
        'use_cases': [
            'When survival time distribution is known',
            'Comparing acceleration/deceleration factors',
            'Predicting median survival times',
            'When parametric estimates are preferred'
        ]
    },
    
    'kaplan_meier': {
        'name': 'Kaplan-Meier Estimator',
        'description': 'Non-parametric method for estimating survival probabilities over time, providing the foundation for survival curve visualization.',
        'category': 'Survival Analysis',
        'parameters': {
            'alpha': {
                'name': 'Confidence Level',
                'type': 'number',
                'min': 0.8,
                'max': 0.99,
                'step': 0.01,
                'default': 0.95,
                'description': 'Confidence level for survival curve confidence intervals'
            },
            'ci_method': {
                'name': 'CI Method',
                'type': 'select',
                'options': ['log-log', 'linear', 'log'],
                'default': 'log-log',
                'description': 'Method for calculating confidence intervals'
            },
            'label_survival_function': {
                'name': 'Label Survival Function',
                'type': 'boolean',
                'default': True,
                'description': 'Whether to label the survival function on the plot'
            }
        },
        'pros': [
            'No distributional assumptions',
            'Handles censored data naturally',
            'Provides unbiased survival estimates',
            'Easy to visualize and interpret',
            'Robust and widely accepted'
        ],
        'cons': [
            'Cannot incorporate covariates directly',
            'Limited to descriptive analysis',
            'Confidence intervals can be wide with small samples',
            'Step function appearance may not reflect smooth survival'
        ],
        'use_cases': [
            'Visualizing survival curves',
            'Estimating median survival times',
            'Comparing survival between groups',
            'Descriptive survival analysis'
        ]
    },
    
    'log_rank_test': {
        'name': 'Log-Rank Test',
        'description': 'Non-parametric statistical test for comparing survival distributions between two or more groups.',
        'category': 'Survival Analysis',
        'parameters': {
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing'
            },
            'weight_function': {
                'name': 'Weight Function',
                'type': 'select',
                'options': ['wilcoxon', 'tarone-ware', 'peto', 'fleming-harrington'],
                'default': 'wilcoxon',
                'description': 'Weighting function for the test statistic'
            }
        },
        'pros': [
            'Non-parametric (no distributional assumptions)',
            'Sensitive to differences throughout the survival curve',
            'Widely used and accepted',
            'Can handle multiple groups',
            'Robust to outliers'
        ],
        'cons': [
            'Assumes proportional hazards',
            'Less powerful than parametric tests when assumptions are met',
            'May miss differences in early vs. late survival',
            'Cannot quantify the magnitude of difference'
        ],
        'use_cases': [
            'Comparing survival between treatment groups',
            'Testing for differences in survival curves',
            'Initial screening for survival differences',
            'Validating results from other methods'
        ]
    },
    
    'restricted_mean_survival_time': {
        'name': 'Restricted Mean Survival Time (RMST)',
        'description': 'Non-parametric method that estimates the mean survival time up to a specified time point, providing an alternative to hazard ratios.',
        'category': 'Survival Analysis',
        'parameters': {
            'tau': {
                'name': 'Restriction Time',
                'type': 'number',
                'min': 1,
                'max': 1000,
                'step': 1,
                'default': 60,
                'description': 'Time point up to which mean survival is calculated (in time units)'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for confidence intervals'
            },
            'return_variance': {
                'name': 'Return Variance',
                'type': 'boolean',
                'default': True,
                'description': 'Whether to return variance estimates'
            }
        },
        'pros': [
            'No proportional hazards assumption',
            'Easy to interpret (mean survival time)',
            'Robust to model misspecification',
            'Can be used when hazard ratios are not meaningful',
            'Provides absolute rather than relative measures'
        ],
        'cons': [
            'Requires choosing a restriction time point',
            'May lose information beyond restriction time',
            'Less familiar to many researchers',
            'Can be sensitive to choice of tau'
        ],
        'use_cases': [
            'When proportional hazards assumption is violated',
            'Comparing treatments with crossing survival curves',
            'When absolute survival time differences are important',
            'Complementary analysis to Cox regression'
        ]
    },
    
    'random_survival_forest': {
        'name': 'Random Survival Forest',
        'description': 'Machine learning method that extends random forests to survival data, handling high-dimensional covariates and complex interactions.',
        'category': 'Machine Learning',
        'parameters': {
            'n_estimators': {
                'name': 'Number of Trees',
                'type': 'number',
                'min': 10,
                'max': 1000,
                'step': 10,
                'default': 100,
                'description': 'Number of trees in the forest'
            },
            'max_depth': {
                'name': 'Maximum Depth',
                'type': 'number',
                'min': 1,
                'max': 50,
                'step': 1,
                'default': 10,
                'description': 'Maximum depth of the trees'
            },
            'min_samples_split': {
                'name': 'Min Samples Split',
                'type': 'number',
                'min': 2,
                'max': 100,
                'step': 1,
                'default': 10,
                'description': 'Minimum number of samples required to split a node'
            },
            'min_samples_leaf': {
                'name': 'Min Samples Leaf',
                'type': 'number',
                'min': 1,
                'max': 50,
                'step': 1,
                'default': 5,
                'description': 'Minimum number of samples required in a leaf node'
            },
            'max_features': {
                'name': 'Max Features',
                'type': 'select',
                'options': ['sqrt', 'log2', 'auto', '0.5', '0.7', '0.9'],
                'default': 'sqrt',
                'description': 'Number of features to consider for best split'
            }
        },
        'pros': [
            'Handles high-dimensional data well',
            'Captures complex interactions automatically',
            'No assumptions about data distribution',
            'Provides variable importance measures',
            'Robust to outliers and missing data'
        ],
        'cons': [
            'Less interpretable than parametric methods',
            'Can overfit with small sample sizes',
            'Computationally intensive',
            'May not perform well with very few events',
            'Black box approach'
        ],
        'use_cases': [
            'High-dimensional survival analysis',
            'Feature selection and ranking',
            'Non-linear relationship detection',
            'Ensemble survival prediction',
            'When traditional methods fail'
        ]
    },
    
    'gradient_boosting_survival': {
        'name': 'Gradient Boosting Survival Analysis',
        'description': 'Machine learning method that combines multiple weak learners to create a strong survival prediction model.',
        'category': 'Machine Learning',
        'parameters': {
            'n_estimators': {
                'name': 'Number of Estimators',
                'type': 'number',
                'min': 10,
                'max': 1000,
                'step': 10,
                'default': 100,
                'description': 'Number of boosting stages'
            },
            'learning_rate': {
                'name': 'Learning Rate',
                'type': 'number',
                'min': 0.01,
                'max': 1.0,
                'step': 0.01,
                'default': 0.1,
                'description': 'Learning rate shrinks the contribution of each tree'
            },
            'max_depth': {
                'name': 'Maximum Depth',
                'type': 'number',
                'min': 1,
                'max': 20,
                'step': 1,
                'default': 3,
                'description': 'Maximum depth of the individual regression estimators'
            },
            'subsample': {
                'name': 'Subsample',
                'type': 'number',
                'min': 0.1,
                'max': 1.0,
                'step': 0.1,
                'default': 1.0,
                'description': 'Fraction of samples to be used for fitting individual base learners'
            }
        },
        'pros': [
            'High predictive accuracy',
            'Handles mixed data types well',
            'Can capture complex patterns',
            'Provides feature importance',
            'Robust to outliers'
        ],
        'cons': [
            'Can overfit with small samples',
            'Computationally intensive',
            'Many hyperparameters to tune',
            'Less interpretable than linear models',
            'Sensitive to hyperparameter choices'
        ],
        'use_cases': [
            'High-accuracy survival prediction',
            'Complex non-linear relationships',
            'Feature selection',
            'Ensemble modeling',
            'When maximum predictive performance is needed'
        ]
    },
    
    'frailty_model': {
        'name': 'Frailty Model',
        'description': 'Extension of Cox regression that accounts for unobserved heterogeneity or clustering in survival data.',
        'category': 'Survival Analysis',
        'parameters': {
            'frailty_distribution': {
                'name': 'Frailty Distribution',
                'type': 'select',
                'options': ['gamma', 'lognormal', 'inverse_gaussian'],
                'default': 'gamma',
                'description': 'Distribution for the frailty term'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty'
            }
        },
        'pros': [
            'Accounts for unobserved heterogeneity',
            'Handles clustered survival data',
            'More realistic modeling of individual differences',
            'Can improve model fit',
            'Provides frailty estimates'
        ],
        'cons': [
            'More complex than standard Cox regression',
            'Requires more computational resources',
            'Can be sensitive to frailty distribution choice',
            'May be difficult to interpret',
            'Requires sufficient clusters for stable estimates'
        ],
        'use_cases': [
            'Clustered survival data (e.g., family studies)',
            'When unobserved heterogeneity is suspected',
            'Multi-center clinical trials',
            'Genetic studies with family clusters',
            'When standard Cox regression assumptions are violated'
        ]
    },
    
    'competing_risks': {
        'name': 'Competing Risks Analysis',
        'description': 'Method for analyzing time-to-event data when multiple types of events can occur, where the occurrence of one event prevents the observation of others.',
        'category': 'Survival Analysis',
        'parameters': {
            'method': {
                'name': 'Analysis Method',
                'type': 'select',
                'options': ['cause_specific', 'subdistribution', 'both'],
                'default': 'both',
                'description': 'Type of competing risks analysis to perform'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty'
            }
        },
        'pros': [
            'Appropriate for multiple event types',
            'Provides cause-specific and subdistribution hazards',
            'Accounts for competing events properly',
            'More realistic modeling of complex outcomes',
            'Can identify different risk factors for different events'
        ],
        'cons': [
            'More complex than standard survival analysis',
            'Requires careful interpretation of results',
            'May have lower power than standard methods',
            'Can be computationally intensive',
            'Requires sufficient events of each type'
        ],
        'use_cases': [
            'Multiple event types (e.g., death from different causes)',
            'Treatment studies with competing outcomes',
            'When events are mutually exclusive',
            'Complex clinical outcomes',
            'When standard survival analysis is inappropriate'
        ]
    }
}

# Default analysis method
DEFAULT_ANALYSIS_METHOD = 'cox_proportional_hazards'

# Method categories for organization
METHOD_CATEGORIES = {
    'Survival Analysis': [
        'cox_proportional_hazards',
        'accelerated_failure_time', 
        'kaplan_meier',
        'log_rank_test',
        'restricted_mean_survival_time',
        'frailty_model',
        'competing_risks'
    ],
    'Machine Learning': [
        'random_survival_forest',
        'gradient_boosting_survival'
    ]
}

# Method descriptions for UI
METHOD_DESCRIPTIONS = {
    'cox_proportional_hazards': 'Most widely used survival analysis method. Models hazard ratios while allowing flexible baseline hazard.',
    'accelerated_failure_time': 'Parametric method that models survival time directly. Good when distribution is known.',
    'kaplan_meier': 'Non-parametric method for estimating survival curves. Foundation for survival visualization.',
    'log_rank_test': 'Statistical test for comparing survival distributions between groups.',
    'restricted_mean_survival_time': 'Alternative to hazard ratios. Estimates mean survival up to a time point.',
    'random_survival_forest': 'Machine learning method for high-dimensional survival data with complex interactions.',
    'gradient_boosting_survival': 'High-accuracy machine learning method for survival prediction.',
    'frailty_model': 'Extension of Cox regression that accounts for unobserved heterogeneity.',
    'competing_risks': 'Method for analyzing multiple mutually exclusive event types.'
}


def get_analysis_methods_for_ui():
    """Return a list of analysis methods formatted for the UI comparison card and info modal.

    Each method dict contains:
      - key: the method key
      - title: display name
      - description: short description
      - info: dict with title, description, pros, cons, limitations, expectations, parameters
    """
    methods = []
    for key, meta in ANALYSIS_METHODS.items():
        params = []
        for pkey, pmeta in meta.get('parameters', {}).items():
            params.append({
                'name': pkey,
                'label': pmeta.get('name') or pkey,
                'default': pmeta.get('default'),
                'description': pmeta.get('description', '')
            })

        info = {
            'title': meta.get('name'),
            'description': meta.get('description') or METHOD_DESCRIPTIONS.get(key, ''),
            'pros': meta.get('pros', []),
            'cons': meta.get('cons', []),
            'limitations': meta.get('cons', []),
            'expectations': meta.get('use_cases', []) or [METHOD_DESCRIPTIONS.get(key, '')],
            'parameters': params
        }

        methods.append({
            'key': key,
            'title': meta.get('name'),
            'name': meta.get('name'),
            'description': METHOD_DESCRIPTIONS.get(key, meta.get('description', '')),
            'info': info
        })

    return methods
