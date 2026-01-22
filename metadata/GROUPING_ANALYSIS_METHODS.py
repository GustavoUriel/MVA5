# Grouping Strategy Analysis Methods
GROUPING_ANALYSIS_METHODS = {
    'standard_multivariate': {
        'description': 'Standard penalized regression on all variables',
        'models': ['cox_lasso', 'cox_elastic_net', 'random_survival_forest'],
        'validation': 'nested_cv'
    },
    'hierarchical_grouping': {
        'description': 'Hierarchical analysis with group-level and within-group effects',
        'models': ['cox_frailty', 'group_lasso', 'hierarchical_cox'],
        'validation': 'group_cv'
    },
    'pathway_analysis': {
        'description': 'Pathway-based analysis with biological constraints',
        'models': ['pathway_lasso', 'group_bridge', 'sparse_group_lasso'],
        'validation': 'pathway_cv'
    },
    'stratified_analysis': {
        'description': 'Stratified analysis by subgroups',
        'models': ['stratified_cox', 'interaction_cox', 'subgroup_analysis'],
        'validation': 'stratified_cv'
    },
    'organ_system_analysis': {
        'description': 'Organ system-based functional analysis',
        'models': ['functional_cox', 'system_lasso', 'composite_scoring'],
        'validation': 'system_cv'
    },
    'temporal_analysis': {
        'description': 'Time-dependent analysis of treatment effects',
        'models': ['time_varying_cox', 'landmark_analysis', 'joint_modeling'],
        'validation': 'temporal_cv'
    }
}



# standard_multivariate: Applies standard penalized regression techniques across all variables without considering any grouping structure.
# hierarchical_grouping: Accounts for nested or hierarchical relationships between groups (e.g., variables within subgroups), using models that incorporate group-level effects.
# pathway_analysis: Focuses on biological pathways as constraints, analyzing variables grouped by functional pathways (e.g., metabolic or signaling pathways).
# stratified_analysis: Performs separate analyses for different subgroups (e.g., patient cohorts), allowing for subgroup-specific effects.
# organ_system_analysis: Groups variables by organ systems for functional analysis, treating systems as composite units.
# temporal_analysis: Handles time-dependent effects, analyzing how relationships change over time (e.g., treatment effects that vary).
