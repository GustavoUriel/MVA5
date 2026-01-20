COLUMN_GROUPS = {
    'demographics': {
        'title': 'Demographics1',
        'name': 'Demographics2',
        'control_name': 'AttrGroup_Demographics',
        'columns': [
            'age', 'gender', 'race', 'ethnicity',
            'weight_kg', 'height_m', 'bmi', 'smoking', 'smoking_status'
        ],
        'default_value': False
    },

    'disease_characteristics': {
        'title': 'Disease Characteristics',
        'name': 'Disease Characteristics',
        'control_name': 'AttrGroup_Disease Characteristics',
        'columns': [
            'igg', 'iga', 'biclonal', 'lightchain', 'igh_rearrangement',
            'hr_mutations', 'ultrahr_mutations', 'imwg_hr', 'functional_hr',
            'iss', 'riss', 'beta2microglobulin', 'creatinine', 'albumin'
        ],
        'default_value': True
    },

    'fish_indicators': {
        'title': 'Fish Indicators',
        'name': 'Fish Indicators',
        'control_name': 'AttrGroup_Fish Indicators',
        'columns': [
            '3_monosomy', '3_gain', '5_gain', '7_gain', '9_monosomy', '9_gain',
            '11_monosomy', '11_gain', '13_monosomy', '15_gain', '17_monosomy',
            '19_gain', '21_gain', 'del_13q', 't_11_14', 't_4_14', 't_14_16',
            't_14_20', '1q_plus', 'del_1p32', 'del_17p', '6q21', 't_12_22'
        ],
        'default_value': True
    },

    'comorbidities': {
        'title': 'Comorbidities',
        'name': 'Comorbidities',
        'control_name': 'AttrGroup_Comorbidities',
        'columns': ['es', 'esnoninfectiousfever', 'esnoninfectious_diarhhea', 'esrash'],
        'default_value': True
    },

    'treatment_and_transplantation': {
        'title': 'Treatment And Transplantation',
        'name': 'Treatment And Transplantation',
        'control_name': 'AttrGroup_Treatment And Transplantation',
        'columns': [
            'induction_therapy', 'melphalanmgperm2', 'first_transplant_date',
            'date_engraftment', 'last_date_of_contact', 'monthsfirst_transplant',
            'secona_transplant_date', 'monthssecona_transplantrk',
            'rk_updated_relapse_date', 'relapsemonthsfirst_transplant',
            'relapsemonthssecona_transplant', 'duration_pfs', 'pfs_status',
            'rk_updated_death_date', 'deathmonthsfirst_transplant',
            'deathmonthssecona_transplant', 'duration_survival', 'death_status'
        ],
        'default_value': True
    },

    'laboratory_values': {
        'title': 'Laboratory Values',
        'name': 'Laboratory Values',
        'control_name': 'AttrGroup_Laboratory Values',
        'columns': [
            'beta2microglobulin', 'creatinine', 'albumin', 'ldh', 'hemoglobin',
            'platelet_count', 'neutrophil_count', 'lymphocyte_count'
        ],
        'default_value': True
    },

    'genomic_markers': {
        'title': 'Genomic Markers',
        'name': 'Genomic Markers',
        'control_name': 'AttrGroup_Genomic Markers',
        'columns': [
            'tp53_mutation', 'rb1_deletion', 'myc_rearrangement',
            'cyclin_d1', 'cyclin_d2', 'cyclin_d3', 'maf_rearrangement'
        ],
        'default_value': True
    },

    'antiviral': {
        'title': 'Antiviral',
        'name': 'Antiviral',
        'control_name': 'AttrGroup_Antiviral',
        'columns': ['Acyclovir', 'valACYclovir'],
        'default_value': True
    },

    'antibiotics': {
        'title': 'Antibiotics',
        'name': 'Antibiotics',
        'control_name': 'AttrGroup_Antibiotics',
        'columns': [
            'ciprofloxin', 'ciprofloxin_eng', 'levofloxin', 'levofloxin_eng',
            'moxifloxin', 'moxifloxin_eng', 'amoxicillin', 'amoxicillin_eng',
            'ampicillin', 'ampicillin_eng', 'cefipine', 'cefipine_eng',
            'cefazolin', 'cefazolin_eng', 'azithromycin', 'azithromycin_eng',
            'trimethoprim_sulfamethoxazole', 'trimethoprim_sulfamethoxazole_eng',
            'clindamycin', 'clindamycin_eng', 'metronidazole', 'metronidazole_eng',
            'piperacilin_tazobactam', 'piperacilin_tazobactam_eng',
            'vancomycin_iv', 'vancomycin_iv_eng', 'vancomycin_po', 'vancomycin_po_eng'
        ],
        'default_value': True
    },

    'antifungal': {
        'title': 'Antifungal',
        'name': 'Antifungal',
        'control_name': 'AttrGroup_Antifungal',
        'columns': ['fluconazole', 'fluconazole_eng'],
        'default_value': True
    }
}
