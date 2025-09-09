# Bracken Time Points Configuration
BRACKEN_TIME_POINTS = {
    'pre': {
        'suffix': '.P',
        'description': 'Pre-treatment sample',
        'timepoint': 'baseline',
        'function': 'baseline'
    },
    'during': {
        'suffix': '.E',
        'description': 'Early treatment sample (2 months)',
        'timepoint': '2_months',
        'function': 'baseline'
    },
    'post': {
        'suffix': '.2.4M',
        'description': 'Post-treatment sample (24 months)',
        'timepoint': '24_months',
        'function': 'baseline'
    },
    'delta_to_engraftment': {
        'suffix': '.E - .P',
        'description': 'Difference from pre to early treatment',
        'timepoint': 'delta',
        'function': '.E - .P'
    },
    'delta_post_engraftment': {
        'suffix': '.2.4M - .E',
        'description': 'Difference from early to post treatment',
        'timepoint': 'delta',
        'function': '.2.4M - .E'
    },
    'delta': {
        'suffix': '.2.4M - .P',
        'description': 'Difference from pre to post treatment',
        'timepoint': 'delta',
        'function': '.2.4M - .P'
    },
}
