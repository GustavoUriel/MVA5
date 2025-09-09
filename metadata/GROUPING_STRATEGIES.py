# Advanced Grouping Strategy Configuration
GROUPING_STRATEGIES = {
    'none': {
        'name': 'Standard Analysis',
        'description': 'Analyze all variables together without grouping',
        'groups': None,
        'method': 'standard_multivariate'
    },
    'fish_indicators': {
        'name': 'FISH Indicators Grouping',
        'description': 'Cytogenetic abnormalities grouped by biological significance',
        'groups': {
            'chromosome_gains': ['3_gain', '5_gain', '7_gain', '9_gain', '11_gain', '15_gain', '19_gain', '21_gain', '1q_plus'],
            'chromosome_losses': ['3_monosomy', '9_monosomy', '11_monosomy', '13_monosomy', '17_monosomy', 'del_13q', 'del_1p32', 'del_17p'],
            'high_risk_translocations': ['t_11_14', 't_4_14', 't_14_16', 't_14_20'],
            'other_abnormalities': ['6q21', 't_12_22'],
            # Can overlap for complex analysis
            'complex_abnormalities': ['1q_plus', 'del_17p', 'del_1p32']
        },
        'method': 'hierarchical_grouping'
    },
    'disease_characteristics': {
        'name': 'Disease Characteristics Grouping',
        'description': 'Clinical parameters grouped by pathophysiological systems',
        'groups': {
            'immunoglobulin_profile': ['igg', 'iga', 'biclonal', 'lightchain'],
            'disease_staging': ['iss', 'riss', 'beta2microglobulin', 'albumin', 'creatinine'],
            'molecular_risk': ['igh_rearrangement', 'hr_mutations', 'ultrahr_mutations'],
            'functional_assessment': ['imwg_hr', 'functional_hr']
        },
        'method': 'pathway_analysis'
    },
    'demographics': {
        'name': 'Demographics Grouping',
        'description': 'Patient characteristics grouped by risk stratification',
        'groups': {
            # Will be categorized as <65, 65-75, >75
            'age_stratification': ['age'],
            'physical_characteristics': ['weight_kg', 'height_m', 'bmi'],
            'lifestyle_factors': ['smoking', 'smoking_status'],
            'population_factors': ['gender', 'race', 'ethnicity']
        },
        'method': 'stratified_analysis'
    },
    'genomic_markers': {
        'name': 'Genomic Markers Grouping',
        'description': 'Molecular markers grouped by functional pathways',
        'groups': {
            'tumor_suppressor_pathway': ['tp53_mutation', 'rb1_deletion'],
            'oncogene_pathway': ['myc_rearrangement'],
            'cell_cycle_regulation': ['cyclin_d1', 'cyclin_d2', 'cyclin_d3'],
            'transcription_factors': ['maf_rearrangement']
        },
        'method': 'pathway_analysis'
    },
    'laboratory_values': {
        'name': 'Laboratory Values Grouping',
        'description': 'Lab parameters grouped by organ system function',
        'groups': {
            'kidney_function': ['creatinine', 'beta2microglobulin'],
            'liver_function': ['albumin', 'ldh'],
            'hematologic_parameters': ['hemoglobin', 'platelet_count', 'neutrophil_count', 'lymphocyte_count'],
            'inflammatory_markers': ['ldh', 'beta2microglobulin']  # Can overlap
        },
        'method': 'organ_system_analysis'
    },
    'treatment_response': {
        'name': 'Treatment Response Grouping',
        'description': 'Treatment variables grouped by response patterns',
        'groups': {
            'induction_therapy': ['induction_therapy'],
            'transplant_factors': ['melphalanmgperm2', 'first_transplant_date', 'date_engraftment', 'monthsfirst_transplant'],
            'secondary_transplant': ['secona_transplant_date', 'monthssecona_transplantrk'],
            'outcome_measures': ['duration_pfs', 'pfs_status', 'duration_survival', 'death_status'],
            'relapse_patterns': ['rk_updated_relapse_date', 'relapsemonthsfirst_transplant', 'relapsemonthssecona_transplant'],
            'survival_metrics': ['rk_updated_death_date', 'deathmonthsfirst_transplant', 'deathmonthssecona_transplant']
        },
        'method': 'temporal_analysis'
    }
}
