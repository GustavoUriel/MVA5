# column_names_mapping
import pandas as pd

COLUMNS = {
'patients' : [
    'patient_id','age','gender','race','ethnicity','weight_kg','height_m','bmi','bmi_1','smoking','smoking_status',
    'igg','iga','biclonal','lightchain','igh_rearrangement','3_monosomy','3_gain','5_gain','7_gain','9_monosomy','9_gain',
    '11_monosomy','11_gain','13_monosomy','15_gain','17_monosomy','19_gain','21_gain','del_13q_','t_11_14_','t_4_14_',
    't_14_16_','t_14_20_','1q_','del_1p32_','del_17p_','17_monosomy_1','6q21','t_12_22_','hr_mutations','ultrahr_mutations',
    'imwg_hr','functional_hr','iss','rISS','beta2microglobulin','creatinine','albumin','Induction_therapy','Melphalanmgperm2',
    'First_Transplant_Date','Date_Engraftment','ES','ESnoninfectiousfever','ESnoninfectious_diarhhea','Esrash','ISS',
    'Melphalanmgperm2_1','Last_Date_of_Contact','First_Transplant_Date_1','MonthsFirst_transplant','SecoNA_Transplant_Date',
    'MonthsSecoNA_transplantRK','RK_Updated_Relapse_Date','RelapsemonthsFirst_transplant','RelapsemonthsSecoNA_transplant',
    'Last_Date_of_Contact_1','Duration_PFS','PFS_Status','RK_Updated_Death_Date','Deathmonthsfirst_transplant','DeathmonthssecoNA_transplant',
    'Duration_Survival','Death_Status','Ciprofloxin','Start_Date','End_Date','Cipropfloxin_Eng','Start_DateEng','End_DateEng',
    'Levofloxin','Start_Date_1','End_Date_1','Levofloxin_Eng','Start_DateEng_1','End_DateEng_1','Moxifloxin','Start_Date_2','End_Date_2',
    'Moxifloxin_Eng','Start_DateEng_2','End_DateEng_2','Amoxicillin','Start_date','End_date','Amoxicillin_Eng','Start_DateEng_3',
    'End_DateEng_3','Ampicillin','Start_date_1','End_date_1','Ampicillin_Eng','Start_DateEng_4','End_DateEng_4','Cefipine','Start_Date_3',
    'End_Date_3','Cefipine_Eng','Start_DateEng_5','End_DateEng_5','Cefazolin','Start_Date_4','End_Date_4','Cefazolin_Eng','Start_DateEng_6',
    'End_DateEng_6','Azithromycin','Start_Date_5','End_Date_5','Azithromycin_Eng','Start_DateEng_7','End_DateEng_7',
    'Trimethoprim_sulfamethoxazole','Start_Date_6','End_Date_6','Trimethoprim_sulfamethoxazole_Eng','Start_DateEng_8','End_DateEng_8',
    'Clindamycin','Start_Date_7','End_Date_7','Clindamycin_Eng','Start_DateEng_9','End_DateEng_9','Metronidazole','Start_Date_8',
    'End_Date_8','Metronidazole_Eng','Start_DateEng_10','End_DateEng_10','Piperacilin_tazobactam','Start_Date_9','End_Date_9',
    'Piperacilin_tazobactam_Eng','Start_DateEng_11','End_DateEng_11','Vancomycin_IV','Start_Date_10','End_Date_10','Vancomycin_IV_Eng',
    'Start_DateEng_12','End_DateEng_12','Vancomycin_PO','Start_Date_11','End_Date_11','Vancomycin_PO_Eng','Start_DateEng_13',
    'End_DateEng_13','Fluconazole','Start_Date_12','End_Date_12','Fluconazole_Eng','Start_DateEng_14','End_DateEng_14'
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