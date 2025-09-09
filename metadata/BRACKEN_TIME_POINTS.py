# Bracken Time Points Configuration
BRACKEN_TIME_POINTS = {
    'pre': {
        'suffix': '.P',
        'description': 'Pre-treatment sample',
        'timepoint': 'baseline'
        'function': 'baseline'
    },
    'during': {
        'suffix': '.E',
        'description': 'Early treatment sample (2 months)',
        'timepoint': '2_months'
        'function': 'baseline'
    },
    'post': {
        'suffix': '.2.4M',
        'description': 'Post-treatment sample (24 months)',
        'timepoint': '24_months'
        'function': 'baseline'
    }
    'delta_to_engraftment': {
        'suffix': '',
        'description': 'Post-treatment sample (24 months)',
        'timepoint': '24_months'
        'function': '.P - .E'
    }
    'delta_post_engraftment': {
        'suffix': '.2.4M',
        'description': 'Post-treatment sample (24 months)',
        'timepoint': '24_months'
        'function': '.2.4M - .E'
    }
    'delta': {
        'suffix': '.2.4M',
        'description': 'Post-treatment sample (24 months)',
        'timepoint': '24_months'
        'function': '.2.4M - .P'
    }
}
