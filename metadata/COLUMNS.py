# column_names_mapping
import pandas as pd

COLUMNS = {
'patients' : [
    'patient_id','age','gender','race','ethnicity','weight_kg','height_m','bmi','bmi_1','smoking','smoking_status',
    'igg','iga','biclonal','lightchain','igh_rearrangement','3_monosomy','3_gain','5_gain','7_gain','9_monosomy','9_gain',
    '11_monosomy','11_gain','13_monosomy','15_gain','17_monosomy','19_gain','21_gain','del_13q_','t_11_14_','t_4_14_',
    't_14_16_','t_14_20_','1q_','del_1p32_','del_17p_','17_monosomy_1','6q21','t_12_22_','hr_mutations','ultrahr_mutations',
    'imwg_hr','functional_hr','iss','riss','beta2microglobulin','creatinine','albumin','induction_therapy','melphalanmgperm2',
    'first_transplant_date','date_engraftment','es','esnoninfectiousfever','esnoninfectious_diarhhea','esrash','iss',
    'melphalanmgperm2_1','last_date_of_contact','first_transplant_date_1','monthsfirst_transplant','secona_transplant_date',
    'monthssecona_transplantrk','rk_updated_relapse_date','relapsemonthsfirst_transplant','relapsemonthssecona_transplant',
    'last_date_of_contact_1','duration_pfs','pfs_status','rk_updated_death_date','deathmonthsfirst_transplant','deathmonthssecona_transplant',
    'duration_survival','death_status','ciprofloxin','start_date','end_date','ciprofloxin_eng','start_dateeng','end_dateeng',
    'levofloxin','start_date_1','end_date_1','levofloxin_eng','start_dateeng_1','end_dateeng_1','moxifloxin','start_date_2','end_date_2',
    'moxifloxin_eng','start_dateeng_2','end_dateeng_2','amoxicillin','start_date','end_date','amoxicillin_eng','start_dateeng_3',
    'end_dateeng_3','ampicillin','start_date_1','end_date_1','ampicillin_eng','start_dateeng_4','end_dateeng_4','cefipine','start_date_3',
    'end_date_3','cefipine_eng','start_dateeng_5','end_dateeng_5','cefazolin','start_date_4','end_date_4','cefazolin_eng','start_dateeng_6',
    'end_dateeng_6','azithromycin','start_date_5','end_date_5','azithromycin_eng','start_dateeng_7','end_dateeng_7',
    'trimethoprim_sulfamethoxazole','start_date_6','end_date_6','trimethoprim_sulfamethoxazole_eng','start_dateeng_8','end_dateeng_8',
    'clindamycin','start_date_7','end_date_7','clindamycin_eng','start_dateeng_9','end_dateeng_9','metronidazole','start_date_8',
    'end_date_8','metronidazole_eng','start_dateeng_10','end_dateeng_10','piperacilin_tazobactam','start_date_9','end_date_9',
    'piperacilin_tazobactam_eng','start_dateeng_11','end_dateeng_11','vancomycin_iv','start_date_10','end_date_10','vancomycin_iv_eng',
    'start_dateeng_12','end_dateeng_12','vancomycin_po','start_date_11','end_date_11','vancomycin_po_eng','start_dateeng_13',
    'end_dateeng_13','fluconazole','start_date_12','end_date_12','fluconazole_eng','start_dateeng_14','end_dateeng_14'
],

'taxonomy' : [
    'taxonomy_id', 'full_taxonomy', 'domain', 'phylum', 'class',
    'order', 'family', 'genus', 'species'
],

'bracken' : [ #the column names are unknown, but all the rows except the first one consist only of numbers, create here a definition for that
]
}

IDENTIFICATORS = {
    'taxonomy' : ['taxonomy_id', 'domain'],
    'patients': [ 'age', 'gender', 'race'],
    # 'bracken': no fixed column names; detection rule:
    #   If none of the above IDENTIFICATORS match, a file is considered
    #   'bracken' when all values in rows 2..end (i.e. skip first data
    #   row) are numeric. This module stores an empty list because
    #   column names are not used for detection; the detection logic
    #   should inspect row values instead (sample up to first 20 rows).
    'bracken': ['no column name check' ]
}

REQUIRED = {
    'taxonomy' : ['taxonomy_id', 'taxonomy' 'domain'],
    'patients': [ 'age', 'gender', 'race' ,'Duration_PFS','PFS_Status'],
    # 'bracken': no fixed column names; detection rule:
    #   If none of the above IDENTIFICATORS match, a file is considered
    #   'bracken' when all values in rows 2..end (i.e. skip first data
    #   row) are numeric. This module stores an empty list because
    #   column names are not used for detection; the detection logic
    #   should inspect row values instead (sample up to first 20 rows).
    'bracken': ['taxonomy_id' ]
}


# The lines below contained plain-text notes (antibiotic groups and examples)
# that were accidentally left in the module and caused a syntax/error issue.
# They are preserved here as comments for reference.
# Fluoroquinolones:	Ciprofloxin, Levofloxin, Moxifloxin
# Penicillins:	Amoxicillin, Ampicillin, Piperacilin-tazobactam
# Cephalosporins:	Cefipine (Cefepime), Cefazolin
# Macrolides:	Azithromycin
# Other_Antibiotics:	Trimethoprim-sulfamethoxazole, Clindamycin, Metronidazole, Vancomycin (IV and PO/Oral versions)
# Antifungals:	Fluconazole

# Grouped medicine dictionary (keys match the commented group names)
MEDICINES = {
    'Fluoroquinolones': ['ciprofloxin', 'levofloxin', 'moxifloxin'],
    'Penicillins': ['amoxicillin', 'ampicillin', 'piperacilin_tazobactam'],
    'Cephalosporins': ['cefipine', 'cefazolin'],
    'Macrolides': ['azithromycin'],
    'Other_Antibiotics': ['trimethoprim_sulfamethoxazole', 'clindamycin', 'metronidazole', 'vancomycin_iv', 'vancomycin_po'],
    'Antifungals': ['fluconazole']
}