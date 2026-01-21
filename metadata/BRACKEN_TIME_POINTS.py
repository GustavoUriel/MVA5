# Bracken Time Points Configuration
BRACKEN_TIME_POINTS = {
    'Pre-engraftment': {
        'suffix': '.P',
        'label': 'Pre-engraftment',
        'value': 'pre-engraftment',
        'function': 'baseline',
        'description': 'The pre-engraftment timepoint represents the baseline microbial composition before hematopoietic stem cell transplantation. This sample captures the native gut microbiota state, serving as a reference for post-transplant changes. Higher diversity correlates with better engraftment success. It helps assess initial microbial ecosystem, identify risk factors for complications like graft-versus-host disease, and predict microbiota shifts. Essential for longitudinal studies tracking microbiome resilience during transplant, enabling personalized medicine approaches in HSCT.'
    },
    '2 months after engraftment': {
        'suffix': '.E',
        'label': 'Early post-engraftment (2 months)',
        'value': 'early',
        'function': 'baseline',
        'description': 'Collected two months post-engraftment, this timepoint captures early post-transplant microbial landscape. Engraftment marks donor cell production of new blood cells. Microbiota shows shifts from baseline due to immunosuppressants, antibiotics, and diet. Composition predicts graft-versus-host disease risk. Includes opportunistic pathogens or beneficial commensals influencing immune reconstitution. Provides data on microbiome adaptation to new immunological environment. Crucial for identifying early dysbiosis indicators requiring intervention to prevent long-term complications.'
    },
    '24 months after engraftment': {
        'suffix': '.2.4M',
        'label': 'Post-engraftment (24 months)',
        'value': 'post-engraftment',
        'function': 'baseline',
        'description': 'This long-term sample at 24 months post-engraftment represents stabilized post-transplant microbial ecosystem. Microbiota undergoes recovery and adaptation to chronic immunosuppression. Diversity and composition indicate long-term outcomes, immune tolerance, and reduced complication risks. Reflects overall health, diet, and prophylactic treatments. Assesses microbiota resilience and new homeostasis. Linked to chronic GVHD and survival rates. Benchmark for evaluating microbiota-preserving strategies. Guides long-term management for transplant survivors, identifying risks for late complications.'
    },
    'delta_to_engraftment': {
        'suffix': '.E - .P',
        'label': 'Delta Pre to Early',
        'value': 'delta_e_p',
        'function': '.E - .P',
        'description': 'This delta measures microbial changes from 2-month post-engraftment to pre-engraftment baseline. Quantifies immediate transplant impact on gut microbiota. Captures shifts in abundance, diversity, and structure from conditioning, antibiotics, and early immunosuppression. Magnitude and direction correlate with outcomes like engraftment speed and complications. Positive deltas in beneficial taxa indicate successful adaptation; negative changes signal dysbiosis. Identifies biomarkers for GVHD risk. Guides early interventions to mitigate disruption and supports personalized transplant care.'
    },
    'delta_after_engraftment': {
        'suffix': '.2.4M - .E',
        'label': 'Delta Post to Early',
        'value': 'delta_24m_2m',
        'function': '.2.4M - .E',
        'description': 'This delta measures microbial evolution from 2 to 24 months post-engraftment, capturing long-term recovery trajectory. Quantifies changes in composition, diversity, and function over extended post-transplant period. Patterns predict long-term outcomes, chronic GVHD, and survival. Positive shifts towards commensals indicate successful reconstitution; persistent dysbiosis signals complications. Identifies trajectories for risk stratification. Informs long-term strategies including microbiota-modulating therapies. Provides insights into microbiome adaptive capacity under chronic immunosuppression and transplant stressors.'
    },
    'delta_pre_pos': {
        'suffix': '.2.4M - .P',
        'label': 'Delta Post to Pre',
        'value': 'delta_24m_p',
        'function': '.2.4M - .P',
        'description': 'This delta encompasses total microbial transformation from pre-engraftment to 24 months post-engraftment, offering comprehensive microbiota dynamics view. Captures cumulative transplant impact, conditioning, immunosuppression, and recovery on microbial communities. Trajectory correlates with success, complications, and outcomes. Reveals succession, resilience, and adaptation patterns. Significant shifts predict GVHD, infections risks. Enables recovery trajectory assessment and targeted intervention identification. Highlights profound transplant effects on gut ecosystem, emphasizing microbiota-preserving strategies in care.'
    },
}

# Default time point selection
DEFAULT_TIME_POINT = 'pre-engraftment'


def get_time_points():
    """Return list of time point dicts suitable for UI consumption."""
    result = []
    for key, val in BRACKEN_TIME_POINTS.items():
        result.append({
            'key': key,
            'label': val.get('label', key),
            'value': val.get('value', key),
            'description': val.get('description', '')
        })
    return result