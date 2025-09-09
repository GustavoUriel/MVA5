# column_names_mapping
COLUMNS = {
'patients' : [
    'patient_id', 'age', 'gender', 'race', 'ethnicity',
    'weight_kg', 'height_m', 'bmi', 'smoking', 'smoking_status',
    'igg', 'iga', 'biclonal', 'lightchain', 'igh_rearrangement',
    '3_monosomy', '3_gain', '5_gain', '7_gain', '9_monosomy', '9_gain',
    '11_monosomy', '11_gain', '13_monosomy', '15_gain', '17_monosomy',
    '19_gain', '21_gain', 'del_13q', 't_11_14', 't_4_14', 't_14_16',
    't_14_20', '1q_plus', 'del_1p32', 'del_17p', '6q21', 't_12_22',
    'hr_mutations', 'ultrahr_mutations', 'imwg_hr', 'functional_hr',
    'iss', 'riss', 'beta2microglobulin', 'creatinine', 'albumin',
    'induction_therapy', 'melphalanmgperm2', 'first_transplant_date',
    'date_engraftment', 'es', 'esnoninfectiousfever',
    'esnoninfectious_diarhhea', 'esrash', 'last_date_of_contact',
    'monthsfirst_transplant', 'secona_transplant_date',
    'monthssecona_transplantrk', 'rk_updated_relapse_date',
    'relapsemonthsfirst_transplant', 'relapsemonthssecona_transplant',
    'duration_pfs', 'pfs_status', 'rk_updated_death_date',
    'deathmonthsfirst_transplant', 'deathmonthssecona_transplant',
    'duration_survival', 'death_status',
    'ciprofloxin', 'cipropfloxin_eng', 'levofloxin', 'levofloxin_eng',
    'moxifloxin', 'moxifloxin_eng', 'amoxicillin', 'amoxicillin_eng',
    'ampicillin', 'ampicillin_eng', 'cefipine', 'cefipine_eng',
    'cefazolin', 'cefazolin_eng', 'azithromycin', 'azithromycin_eng',
    'trimethoprim_sulfamethoxazole', 'trimethoprim_sulfamethoxazole_eng',
    'clindamycin', 'clindamycin_eng', 'metronidazole', 'metronidazole_eng',
    'piperacilin_tazobactam', 'piperacilin_tazobactam_eng',
    'vancomycin_iv', 'vancomycin_iv_eng', 'vancomycin_po', 'vancomycin_po_eng',
    'fluconazole', 'fluconazole_eng',
    'start_date', 'end_date', 'start_dateeng', 'end_dateeng'
],

'taxonomy' : [
    'taxonomy_id', 'full_taxonomy', 'domain', 'phylum', 'class',
    'order', 'family', 'genus', 'species'
]
 }

IDENTIFICATOS = {
'taxonomy' : ['taxonomy_id', 'domain'],
'patients': [ 'age', 'gender', 'race']
 }