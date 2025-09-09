ANALYSIS_METHODS = {
    'cox': {
        'name': 'Cox Proportional Hazards',
        'description': 'Survival analysis using Cox regression model',
        'parameters': ['alpha', 'penalizer', 'step_size']
    },
    'rmst': {
        'name': 'Restricted Mean Survival Time',
        'description': 'RMST difference analysis',
        'parameters': ['tau', 'alpha', 'return_variance']
    },
    'kaplan_meier': {
        'name': 'Kaplan-Meier Estimator',
        'description': 'Non-parametric survival analysis',
        'parameters': ['alpha', 'ci_labels']
    },
    'log_rank': {
        'name': 'Log-Rank Test',
        'description': 'Statistical test comparing survival distributions',
        'parameters': ['alpha']
    }
}
