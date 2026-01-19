COLUMN_GROUPS = {
    'demographics': {
        'title': 'Demographics',
        'columns': [
            'age', 'gender', 'race', 'ethnicity',
            'weight_kg', 'height_m', 'bmi', 'smoking', 'smoking_status'
        ]
    },

    'disease_characteristics': {
        'title': 'Disease Characteristics',
        'columns': [
            'igg', 'iga', 'biclonal', 'lightchain', 'igh_rearrangement',
            'hr_mutations', 'ultrahr_mutations', 'imwg_hr', 'functional_hr',
            'iss', 'riss', 'beta2microglobulin', 'creatinine', 'albumin'
        ]
    },

    'fish_indicators': {
        'title': 'Fish Indicators',
        'columns': [
            '3_monosomy', '3_gain', '5_gain', '7_gain', '9_monosomy', '9_gain',
            '11_monosomy', '11_gain', '13_monosomy', '15_gain', '17_monosomy',
            '19_gain', '21_gain', 'del_13q', 't_11_14', 't_4_14', 't_14_16',
            't_14_20', '1q_plus', 'del_1p32', 'del_17p', '6q21', 't_12_22'
        ]
    },

    'comorbidities': {
        'title': 'Comorbidities',
        'columns': ['es', 'esnoninfectiousfever', 'esnoninfectious_diarhhea', 'esrash']
    },

    'treatment_and_transplantation': {
        'title': 'Treatment And Transplantation',
        'columns': [
            'induction_therapy', 'melphalanmgperm2', 'first_transplant_date',
            'date_engraftment', 'last_date_of_contact', 'monthsfirst_transplant',
            'secona_transplant_date', 'monthssecona_transplantrk',
            'rk_updated_relapse_date', 'relapsemonthsfirst_transplant',
            'relapsemonthssecona_transplant', 'duration_pfs', 'pfs_status',
            'rk_updated_death_date', 'deathmonthsfirst_transplant',
            'deathmonthssecona_transplant', 'duration_survival', 'death_status'
        ]
    },

    'laboratory_values': {
        'title': 'Laboratory Values',
        'columns': [
            'beta2microglobulin', 'creatinine', 'albumin', 'ldh', 'hemoglobin',
            'platelet_count', 'neutrophil_count', 'lymphocyte_count'
        ]
    },

    'genomic_markers': {
        'title': 'Genomic Markers',
        'columns': [
            'tp53_mutation', 'rb1_deletion', 'myc_rearrangement',
            'cyclin_d1', 'cyclin_d2', 'cyclin_d3', 'maf_rearrangement'
        ]
    },

    'antiviral': {
        'title': 'Antiviral',
        'columns': ['Acyclovir', 'valACYclovir']
    },

    'antibiotics': {
        'title': 'Antibiotics',
        'columns': [
            'ciprofloxin', 'ciprofloxin_eng', 'levofloxin', 'levofloxin_eng',
            'moxifloxin', 'moxifloxin_eng', 'amoxicillin', 'amoxicillin_eng',
            'ampicillin', 'ampicillin_eng', 'cefipine', 'cefipine_eng',
            'cefazolin', 'cefazolin_eng', 'azithromycin', 'azithromycin_eng',
            'trimethoprim_sulfamethoxazole', 'trimethoprim_sulfamethoxazole_eng',
            'clindamycin', 'clindamycin_eng', 'metronidazole', 'metronidazole_eng',
            'piperacilin_tazobactam', 'piperacilin_tazobactam_eng',
            'vancomycin_iv', 'vancomycin_iv_eng', 'vancomycin_po', 'vancomycin_po_eng'
        ]
    },

    'antifungal': {
        'title': 'Antifungal',
        'columns': ['fluconazole', 'fluconazole_eng']
    }
}
