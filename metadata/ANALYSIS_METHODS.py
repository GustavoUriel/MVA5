ANALYSIS_METHODS = {
    'pls_survival': {
        'name': 'Partial Least Squares for Survival (PLS-Survival)',
        'description': 'Supervised extension of PLS adapted for censored survival data. Finds latent variables maximizing covariance between microbial groups and PFS outcomes.',
        'category': 'Machine Learning',
        'control_name': 'AnMe_pls_survival',
        'control_name_post_analysis': 'AnMe_pls_survival_post',
        'param_prefix': 'AnMe_PLS_',
        'selected': False,
        'parameters': {
            'n_components': {
                'name': 'Number of Components',
                'type': 'number',
                'min': 1,
                'max': 10,
                'step': 1,
                'default': 2,
                'description': 'Number of latent components to extract',
                'control_name': 'AnMe_PLS_n_components'
            },
            'cross_validation': {
                'name': 'Cross Validation',
                'type': 'boolean',
                'default': True,
                'description': 'Whether to use cross-validation for component selection',
                'control_name': 'AnMe_PLS_cross_validation'
            }
        },
        'pros': [
            'Direct PFS integration',
            'Handles multicollinearity',
            'Dimensionality reduction',
            'Variable importance (VIP scores)',
            'Predictive modeling'
        ],
        'cons': [
            'Complex interpretation',
            'Parameter selection required',
            'Less established for survival',
            'Assumes linearity'
        ],
        'use_cases': [
            'High-dimensional correlated data',
            'Latent pattern discovery',
            'Variable importance ranking'
        ]
    },
    'spls_da': {
        'name': 'Sparse Partial Least Squares Discriminant Analysis (sPLS-DA)',
        'description': 'Supervised sparse PLS-DA for PFS outcome discrimination and feature selection using microbial groups.',
        'category': 'Machine Learning',
        'control_name': 'AnMe_spls_da',
        'control_name_post_analysis': 'AnMe_spls_da_post',
        'param_prefix': 'AnMe_SPLSDA_',
        'selected': False,
        'parameters': {
            'n_components': {
                'name': 'Number of Components',
                'type': 'number',
                'min': 1,
                'max': 10,
                'step': 1,
                'default': 2,
                'description': 'Number of latent components',
                'control_name': 'AnMe_SPLSDA_n_components'
            },
            'sparsity': {
                'name': 'Sparsity Level',
                'type': 'number',
                'min': 0.1,
                'max': 1.0,
                'step': 0.1,
                'default': 0.5,
                'description': 'Proportion of features to keep (sparsity)',
                'control_name': 'AnMe_SPLSDA_sparsity'
            }
        },
        'pros': [
            'Direct PFS supervision',
            'Automatic feature selection',
            'Multiclass discrimination',
            'Handles correlations',
            'Predictive performance'
        ],
        'cons': [
            'Complexity',
            'Computational cost',
            'Parameter sensitivity',
            'Limited survival extension'
        ],
        'use_cases': [
            'Feature selection for PFS',
            'Discriminant analysis',
            'Sparse modeling'
        ]
    },
    'survival_neural_network': {
        'name': 'Survival Neural Network',
        'description': 'Deep learning models adapted for PFS analysis using microbial groups and clinical variables.',
        'category': 'Machine Learning',
        'control_name': 'AnMe_survival_neural_network',
        'param_prefix': 'AnMe_SNN_',
        'selected': False,
        'parameters': {
            'n_layers': {
                'name': 'Number of Hidden Layers',
                'type': 'number',
                'min': 1,
                'max': 5,
                'step': 1,
                'default': 2,
                'description': 'Number of hidden layers in the neural network',
                'control_name': 'AnMe_SNN_n_layers'
            },
            'layer_size': {
                'name': 'Layer Size',
                'type': 'number',
                'min': 8,
                'max': 512,
                'step': 8,
                'default': 64,
                'description': 'Number of neurons per hidden layer',
                'control_name': 'AnMe_SNN_layer_size'
            },
            'dropout': {
                'name': 'Dropout Rate',
                'type': 'number',
                'min': 0.0,
                'max': 0.5,
                'step': 0.05,
                'default': 0.1,
                'description': 'Dropout rate for regularization',
                'control_name': 'AnMe_SNN_dropout'
            }
        },
        'pros': [
            'Non-linear PFS modeling',
            'Feature learning',
            'Flexibility',
            'Scalability',
            'End-to-end learning'
        ],
        'cons': [
            'Black box nature',
            'Data hungry',
            'Computational cost',
            'Overfitting risk',
            'Parameter tuning required'
        ],
        'use_cases': [
            'Large sample size',
            'Complex non-linear relationships',
            'State-of-the-art prediction'
        ]
    },
    'dirichlet_multinomial_regression': {
        'name': 'Dirichlet Multinomial Regression',
        'description': 'Statistical model for microbiome compositional data, modeling group abundances as Dirichlet-multinomial distributed for PFS correlation.',
        'category': 'Statistical Modeling',
        'control_name': 'AnMe_dirichlet_multinomial_regression',
        'control_name_post_analysis': 'AnMe_dirichlet_multinomial_regression_post',
        'param_prefix': 'AnMe_DMR_',
        'selected': False,
        'parameters': {
            'overdispersion': {
                'name': 'Overdispersion Parameter',
                'type': 'number',
                'min': 0.01,
                'max': 10.0,
                'step': 0.01,
                'default': 1.0,
                'description': 'Overdispersion parameter for the Dirichlet-multinomial model',
                'control_name': 'AnMe_DMR_overdispersion'
            }
        },
        'pros': [
            'Compositionally aware',
            'Microbiome-specific',
            'Zero handling',
            'Ecologically meaningful',
            'Statistical rigor'
        ],
        'cons': [
            'Complexity',
            'Parameter estimation',
            'Limited software',
            'Computational cost',
            'Interpretability'
        ],
        'use_cases': [
            'Microbiome compositional data',
            'Community composition modeling',
            'Composition-aware hazard ratios'
        ]
    },
    'bayesian_survival_model': {
        'name': 'Bayesian Survival Model',
        'description': 'Probabilistic modeling of PFS using Bayesian inference with microbial groups, providing uncertainty quantification.',
        'category': 'Statistical Modeling',
        'control_name': 'AnMe_bayesian_survival_model',
        'control_name_post_analysis': 'AnMe_bayesian_survival_model_post',
        'param_prefix': 'AnMe_BSM_',
        'selected': False,
        'parameters': {
            'n_samples': {
                'name': 'Number of Posterior Samples',
                'type': 'number',
                'min': 100,
                'max': 10000,
                'step': 100,
                'default': 2000,
                'description': 'Number of MCMC samples for posterior estimation',
                'control_name': 'AnMe_BSM_n_samples'
            },
            'prior_scale': {
                'name': 'Prior Scale',
                'type': 'number',
                'min': 0.01,
                'max': 10.0,
                'step': 0.01,
                'default': 1.0,
                'description': 'Scale of the prior distribution for coefficients',
                'control_name': 'AnMe_BSM_prior_scale'
            }
        },
        'pros': [
            'Uncertainty quantification',
            'Prior knowledge integration',
            'Flexible modeling',
            'Robust to small samples',
            'Model comparison'
        ],
        'cons': [
            'Computational intensity',
            'Parameter tuning',
            'Convergence issues',
            'Interpretability challenges',
            'Software complexity'
        ],
        'use_cases': [
            'Small datasets',
            'Uncertainty quantification',
            'Probabilistic risk estimation'
        ]
    },
    'cox_proportional_hazards': {
        'name': 'Cox Proportional Hazards Regression',
        'description': 'Semi-parametric survival analysis method that models the hazard ratio as a function of covariates while allowing the baseline hazard to be unspecified.',
        'category': 'Survival Analysis',
        'control_name': 'AnMe_cox_proportional_hazards',
        'control_name_post_analysis': 'AnMe_cox_proportional_hazards_post',
        'param_prefix': 'AnMe_CPH_',
        'selected': True,
        'parameters': {
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing',
                'control_name': 'AnMe_CPH_alpha'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty to prevent overfitting',
                'control_name': 'AnMe_CPH_penalizer'
            },
            'l1_ratio': {
                'name': 'L1 Ratio',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.1,
                'default': 0.0,
                'description': 'Ratio of L1 to L2 penalty (0 = pure L2, 1 = pure L1)',
                'control_name': 'AnMe_CPH_l1_ratio'
            },
            'max_iter': {
                'name': 'Maximum Iterations',
                'type': 'number',
                'min': 100,
                'max': 10000,
                'step': 100,
                'default': 1000,
                'description': 'Maximum number of iterations for convergence',
                'control_name': 'AnMe_CPH_max_iter'
            },
            'tolerance': {
                'name': 'Convergence Tolerance',
                'type': 'number',
                'min': 1e-8,
                'max': 1e-3,
                'step': 1e-4,
                'default': 1e-6,
                'description': 'Tolerance for convergence criteria',
                'control_name': 'AnMe_CPH_tolerance'
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
        'control_name': 'AnMe_accelerated_failure_time',
        'control_name_post_analysis': 'AnMe_AFT_post',
        'param_prefix': 'AnMe_AFT_',
        'selected': False,
        'parameters': {
            'distribution': {
                'name': 'Distribution',
                'type': 'select',
                'options': ['weibull', 'exponential', 'log-normal', 'log-logistic'],
                'default': 'weibull',
                'description': 'Parametric distribution for survival times',
                'control_name': 'AnMe_AFT_distribution'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing',
                'control_name': 'AnMe_AFT_alpha'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty',
                'control_name': 'AnMe_AFT_penalizer'
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
        'control_name': 'AnMe_kaplan_meier',
        'control_name_post_analysis': 'AnMe_kaplan_meier_post',
        'param_prefix': 'AnMe_KM_',
        'selected': False,
        'parameters': {
            'alpha': {
                'name': 'Confidence Level',
                'type': 'number',
                'min': 0.8,
                'max': 0.99,
                'step': 0.01,
                'default': 0.95,
                'description': 'Confidence level for survival curve confidence intervals',
                'control_name': 'AnMe_KM_alpha'
            },
            'ci_method': {
                'name': 'CI Method',
                'type': 'select',
                'options': ['log-log', 'linear', 'log'],
                'default': 'log-log',
                'description': 'Method for calculating confidence intervals',
                'control_name': 'AnMe_KM_ci_method'
            },
            'label_survival_function': {
                'name': 'Label Survival Function',
                'type': 'boolean',
                'default': True,
                'description': 'Whether to label the survival function on the plot',
                'control_name': 'AnMe_KM_label_survival_function'
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
        'control_name': 'AnMe_log_rank_test',
        'control_name_post_analysis': 'AnMe_log_rank_test_post',
        'param_prefix': 'AnMe_LRT_',
        'parameters': {
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing',
                'control_name': 'AnMe_LRT_alpha'
            },
            'weight_function': {
                'name': 'Weight Function',
                'type': 'select',
                'options': ['wilcoxon', 'tarone-ware', 'peto', 'fleming-harrington'],
                'default': 'wilcoxon',
                'description': 'Weighting function for the test statistic',
                'control_name': 'AnMe_LRT_weight_function'
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
        'control_name': 'AnMe_restricted_mean_survival_time',
        'control_name_post_analysis': 'AnMe_RMST_post',
        'param_prefix': 'AnMe_RMST_',
        'selected': False,
        'parameters': {
            'tau': {
                'name': 'Restriction Time',
                'type': 'number',
                'min': 1,
                'max': 1000,
                'step': 1,
                'default': 60,
                'description': 'Time point up to which mean survival is calculated (in time units)',
                'control_name': 'AnMe_RMST_tau'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for confidence intervals',
                'control_name': 'AnMe_RMST_alpha'
            },
            'return_variance': {
                'name': 'Return Variance',
                'type': 'boolean',
                'default': True,
                'description': 'Whether to return variance estimates',
                'control_name': 'AnMe_RMST_return_variance'
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
        'control_name': 'AnMe_random_survival_forest',
        'control_name_post_analysis': 'AnMe_RSF_post',
        'param_prefix': 'AnMe_RSF_',
        'selected': False,
        'parameters': {
            'n_estimators': {
                'name': 'Number of Trees',
                'type': 'number',
                'min': 10,
                'max': 1000,
                'step': 10,
                'default': 100,
                'description': 'Number of trees in the forest',
                'control_name': 'AnMe_RSF_n_estimators'
            },
            'max_depth': {
                'name': 'Maximum Depth',
                'type': 'number',
                'min': 1,
                'max': 50,
                'step': 1,
                'default': 10,
                'description': 'Maximum depth of the trees',
                'control_name': 'AnMe_RSF_max_depth'
            },
            'min_samples_split': {
                'name': 'Min Samples Split',
                'type': 'number',
                'min': 2,
                'max': 100,
                'step': 1,
                'default': 10,
                'description': 'Minimum number of samples required to split a node',
                'control_name': 'AnMe_RSF_min_samples_split'
            },
            'min_samples_leaf': {
                'name': 'Min Samples Leaf',
                'type': 'number',
                'min': 1,
                'max': 50,
                'step': 1,
                'default': 5,
                'description': 'Minimum number of samples required in a leaf node',
                'control_name': 'AnMe_RSF_min_samples_leaf'
            },
            'max_features': {
                'name': 'Max Features',
                'type': 'select',
                'options': ['sqrt', 'log2', 'auto', '0.5', '0.7', '0.9'],
                'default': 'sqrt',
                'description': 'Number of features to consider for best split',
                'control_name': 'AnMe_RSF_max_features'
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
        'control_name': 'AnMe_gradient_boosting_survival',
        'control_name_post_analysis': 'AnMe_GBS_post',
        'param_prefix': 'AnMe_GBS_',
        'selected': False,
        'parameters': {
            'n_estimators': {
                'name': 'Number of Estimators',
                'type': 'number',
                'min': 10,
                'max': 1000,
                'step': 10,
                'default': 100,
                'description': 'Number of boosting stages',
                'control_name': 'AnMe_GBS_n_estimators'
            },
            'learning_rate': {
                'name': 'Learning Rate',
                'type': 'number',
                'min': 0.01,
                'max': 1.0,
                'step': 0.01,
                'default': 0.1,
                'description': 'Learning rate shrinks the contribution of each tree',
                'control_name': 'AnMe_GBS_learning_rate'
            },
            'max_depth': {
                'name': 'Maximum Depth',
                'type': 'number',
                'min': 1,
                'max': 20,
                'step': 1,
                'default': 3,
                'description': 'Maximum depth of the individual regression estimators',
                'control_name': 'AnMe_GBS_max_depth'
            },
            'subsample': {
                'name': 'Subsample',
                'type': 'number',
                'min': 0.1,
                'max': 1.0,
                'step': 0.1,
                'default': 1.0,
                'description': 'Fraction of samples to be used for fitting individual base learners',
                'control_name': 'AnMe_GBS_subsample'
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
        'control_name': 'AnMe_frailty_model',
        'control_name_post_analysis': 'AnMe_FM_post',
        'param_prefix': 'AnMe_FM_',
        'selected': False,
        'parameters': {
            'frailty_distribution': {
                'name': 'Frailty Distribution',
                'type': 'select',
                'options': ['gamma', 'lognormal', 'inverse_gaussian'],
                'default': 'gamma',
                'description': 'Distribution for the frailty term',
                'control_name': 'AnMe_FM_frailty_distribution'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing',
                'control_name': 'AnMe_FM_alpha'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty',
                'control_name': 'AnMe_FM_penalizer'
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
        'control_name': 'AnMe_competing_risks',
        'control_name_post_analysis': 'AnMe_CR_post',
        'param_prefix': 'AnMe_CR_',
        'selected': False,
        'parameters': {
            'method': {
                'name': 'Analysis Method',
                'type': 'select',
                'options': ['cause_specific', 'subdistribution', 'both'],
                'default': 'both',
                'description': 'Type of competing risks analysis to perform',
                'control_name': 'AnMe_CR_method'
            },
            'alpha': {
                'name': 'Significance Level',
                'type': 'number',
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'default': 0.05,
                'description': 'Alpha level for statistical significance testing',
                'control_name': 'AnMe_CR_alpha'
            },
            'penalizer': {
                'name': 'L2 Penalty',
                'type': 'number',
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'default': 0.0,
                'description': 'L2 regularization penalty',
                'control_name': 'AnMe_CR_penalizer'
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
    'random_survival_forest': 'Machine learning method for high-dimensional survival data with complex interactions.',
    'gradient_boosting_survival': 'High-accuracy machine learning method for survival prediction.',
    'frailty_model': 'Extension of Cox regression that accounts for unobserved heterogeneity.',
    'competing_risks': 'Method for analyzing multiple mutually exclusive event types.'
}

