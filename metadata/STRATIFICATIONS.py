# Stratification Configuration for Population Division
# Defines how to divide the population based on comprehensive risk assessment using all relevant parameters within each group

STRATIFICATIONS = {
    'demographics': {
        'age': {
            'type': 'continuous',
            'method': 'quantile',
            'groups': {
                'young': {'min': 0, 'max': 50, 'label': 'Young (≤50 years)'},
                'middle_aged': {'min': 50, 'max': 65, 'label': 'Middle-aged (51-65 years)'},
                'elderly': {'min': 65, 'max': 100, 'label': 'Elderly (>65 years)'}
            }
        },
        'bmi': {
            'type': 'continuous',
            'method': 'clinical',
            'groups': {
                'underweight': {'min': 0, 'max': 18.5, 'label': 'Underweight (BMI <18.5)'},
                'normal': {'min': 18.5, 'max': 25, 'label': 'Normal (BMI 18.5-24.9)'},
                'overweight': {'min': 25, 'max': 30, 'label': 'Overweight (BMI 25-29.9)'},
                'obese': {'min': 30, 'max': 100, 'label': 'Obese (BMI ≥30)'}
            }
        },
        'smoking': {
            'type': 'categorical',
            'method': 'direct',
            'groups': {
                'never': {'values': ['Never', '0', 'No'], 'label': 'Never Smoked'},
                'former': {'values': ['Former', '1', 'Yes'], 'label': 'Former Smoker'},
                'current': {'values': ['Current', '2'], 'label': 'Current Smoker'}
            }
        }
    },

    'disease_characteristics': {
        'disease_risk_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['iss', 'riss', 'hr_mutations', 'ultrahr_mutations', 'imwg_hr', 'functional_hr', 'beta2microglobulin', 'creatinine', 'albumin'],
            'scoring_system': {
                'iss_score': {'I': 0, 'II': 1, 'III': 2},
                'riss_score': {'I': 0, 'II': 1, 'III': 2},
                'hr_mutations': {'Yes': 2, 'No': 0},
                'ultrahr_mutations': {'Yes': 3, 'No': 0},
                'imwg_hr': {'Yes': 1, 'No': 0},
                'functional_hr': {'Yes': 1, 'No': 0},
                'beta2microglobulin': {'high': 1, 'normal': 0},  # >3.5 mg/L
                'creatinine': {'high': 1, 'normal': 0},  # >2.0 mg/dL
                'albumin': {'low': 1, 'normal': 0}  # <3.5 g/dL
            },
            'groups': {
                'low_risk': {'min_score': 0, 'max_score': 2, 'label': 'Low Disease Risk'},
                'intermediate_risk': {'min_score': 3, 'max_score': 5, 'label': 'Intermediate Disease Risk'},
                'high_risk': {'min_score': 6, 'max_score': 8, 'label': 'High Disease Risk'},
                'ultra_high_risk': {'min_score': 9, 'max_score': 15, 'label': 'Ultra-High Disease Risk'}
            }
        }
    },

    'fish_indicators': {
        'fish_risk_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['del_17p', 't_4_14', 't_14_16', 't_14_20', '1q_plus', 'del_1p32', 'del_13q', 't_11_14', 't_12_22'],
            'scoring_system': {
                'high_risk_abnormalities': {
                    'del_17p': {'Yes': 3, 'No': 0},
                    't_4_14': {'Yes': 3, 'No': 0},
                    't_14_16': {'Yes': 3, 'No': 0},
                    't_14_20': {'Yes': 2, 'No': 0}
                },
                'intermediate_risk_abnormalities': {
                    '1q_plus': {'Yes': 2, 'No': 0},
                    'del_1p32': {'Yes': 2, 'No': 0}
                },
                'favorable_abnormalities': {
                    'del_13q': {'Yes': -1, 'No': 0},
                    't_11_14': {'Yes': -1, 'No': 0}
                },
                'other_abnormalities': {
                    't_12_22': {'Yes': 1, 'No': 0}
                }
            },
            'groups': {
                'favorable_risk': {'min_score': -2, 'max_score': 0, 'label': 'Favorable FISH Risk'},
                'standard_risk': {'min_score': 1, 'max_score': 3, 'label': 'Standard FISH Risk'},
                'high_risk': {'min_score': 4, 'max_score': 6, 'label': 'High FISH Risk'},
                'ultra_high_risk': {'min_score': 7, 'max_score': 15, 'label': 'Ultra-High FISH Risk'}
            }
        }
    },

    'comorbidities': {
        'comorbidity_risk_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['es', 'esnoninfectiousfever', 'esnoninfectious_diarhhea', 'esrash'],
            'scoring_system': {
                'es': {'Yes': 2, 'No': 0},
                'esnoninfectiousfever': {'Yes': 1, 'No': 0},
                'esnoninfectious_diarhhea': {'Yes': 1, 'No': 0},
                'esrash': {'Yes': 1, 'No': 0}
            },
            'groups': {
                'low_comorbidity': {'min_score': 0, 'max_score': 1, 'label': 'Low Comorbidity Risk'},
                'moderate_comorbidity': {'min_score': 2, 'max_score': 3, 'label': 'Moderate Comorbidity Risk'},
                'high_comorbidity': {'min_score': 4, 'max_score': 5, 'label': 'High Comorbidity Risk'}
            }
        }
    },

    'treatment_and_transplantation': {
        'treatment_outcome_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['induction_therapy', 'melphalanmgperm2', 'first_transplant_date', 'secona_transplant_date', 'pfs_status', 'death_status', 'duration_pfs', 'duration_survival'],
            'scoring_system': {
                'transplant_intensity': {
                    'single_transplant': 1,
                    'double_transplant': 2,
                    'no_transplant': 0
                },
                'induction_therapy_modernity': {
                    'carfilzomib': 3,
                    'bortezomib': 2,
                    'lenalidomide': 2,
                    'other': 1
                },
                'outcome_status': {
                    'alive_no_progression': 0,
                    'alive_with_progression': 1,
                    'dead_no_progression': 2,
                    'dead_with_progression': 3
                },
                'survival_duration': {
                    'long_survival': 0,  # >24 months
                    'medium_survival': 1,  # 12-24 months
                    'short_survival': 2  # <12 months
                }
            },
            'groups': {
                'excellent_outcome': {'min_score': 0, 'max_score': 2, 'label': 'Excellent Treatment Outcome'},
                'good_outcome': {'min_score': 3, 'max_score': 5, 'label': 'Good Treatment Outcome'},
                'moderate_outcome': {'min_score': 6, 'max_score': 8, 'label': 'Moderate Treatment Outcome'},
                'poor_outcome': {'min_score': 9, 'max_score': 15, 'label': 'Poor Treatment Outcome'}
            }
        }
    },

    'laboratory_values': {
        'laboratory_risk_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['beta2microglobulin', 'creatinine', 'albumin', 'ldh', 'hemoglobin', 'platelet_count', 'neutrophil_count', 'lymphocyte_count'],
            'scoring_system': {
                'beta2microglobulin': {'high': 2, 'normal': 0},  # >3.5 mg/L
                'creatinine': {'high': 2, 'normal': 0},  # >2.0 mg/dL
                'albumin': {'low': 2, 'normal': 0},  # <3.5 g/dL
                'ldh': {'elevated': 2, 'normal': 0},  # >250 U/L
                'hemoglobin': {'low': 1, 'normal': 0},  # <12 g/dL
                'platelet_count': {'low': 1, 'normal': 0},  # <150k/μL
                'neutrophil_count': {'low': 1, 'normal': 0},  # <1.5k/μL
                'lymphocyte_count': {'low': 1, 'normal': 0}  # <1.0k/μL
            },
            'groups': {
                'low_lab_risk': {'min_score': 0, 'max_score': 2, 'label': 'Low Laboratory Risk'},
                'moderate_lab_risk': {'min_score': 3, 'max_score': 5, 'label': 'Moderate Laboratory Risk'},
                'high_lab_risk': {'min_score': 6, 'max_score': 8, 'label': 'High Laboratory Risk'},
                'very_high_lab_risk': {'min_score': 9, 'max_score': 12, 'label': 'Very High Laboratory Risk'}
            }
        }
    },

    'genomic_markers': {
        'genomic_risk_profile': {
            'type': 'composite',
            'method': 'risk_scoring',
            'parameters': ['tp53_mutation', 'rb1_deletion', 'myc_rearrangement', 'cyclin_d1', 'cyclin_d2', 'cyclin_d3', 'maf_rearrangement'],
            'scoring_system': {
                'high_risk_mutations': {
                    'tp53_mutation': {'Yes': 3, 'No': 0},
                    'rb1_deletion': {'Yes': 2, 'No': 0}
                },
                'intermediate_risk_mutations': {
                    'myc_rearrangement': {'Yes': 2, 'No': 0},
                    'maf_rearrangement': {'Yes': 1, 'No': 0}
                },
                'cyclin_abnormalities': {
                    'cyclin_d1': {'Yes': 1, 'No': 0},
                    'cyclin_d2': {'Yes': 1, 'No': 0},
                    'cyclin_d3': {'Yes': 1, 'No': 0}
                }
            },
            'groups': {
                'low_genomic_risk': {'min_score': 0, 'max_score': 1, 'label': 'Low Genomic Risk'},
                'intermediate_genomic_risk': {'min_score': 2, 'max_score': 4, 'label': 'Intermediate Genomic Risk'},
                'high_genomic_risk': {'min_score': 5, 'max_score': 7, 'label': 'High Genomic Risk'},
                'ultra_high_genomic_risk': {'min_score': 8, 'max_score': 10, 'label': 'Ultra-High Genomic Risk'}
            }
        }
    }
}

# Stratification Methods Configuration
STRATIFICATION_METHODS = {
    'continuous': {
        'quantile': 'Divide into equal-sized groups based on quantiles',
        'clinical': 'Use clinically meaningful cutoffs',
        'median': 'Split at median value',
        'tertile': 'Divide into three equal groups'
    },
    'categorical': {
        'direct': 'Use categories as defined',
        'binary': 'Combine categories into binary groups',
        'clinical': 'Use clinically meaningful groupings'
    },
    'composite': {
        'risk_scoring': 'Calculate composite risk scores using weighted parameters',
        'rule_based': 'Apply logical rules to combine variables',
        'count_based': 'Count occurrences and group by frequency',
        'any_positive': 'Group by presence of any positive value'
    }
}

# Default Stratification Settings
DEFAULT_STRATIFICATION_SETTINGS = {
    'min_group_size': 10,  # Minimum number of patients per group
    'max_groups': 5,       # Maximum number of groups per stratification
    'missing_data_handling': 'exclude',  # 'exclude', 'separate_group', 'impute'
    'statistical_tests': ['chi_square', 'fisher_exact', 'mann_whitney'],
    'correction_method': 'fdr_bh'  # Multiple testing correction
}
