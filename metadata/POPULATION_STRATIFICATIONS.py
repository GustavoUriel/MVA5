POPULATION_STRATIFICATIONS = {
    'fish_indicators': {
        'name': 'FISH Indicators Stratification',
        'description': 'Cytogenetic abnormalities grouped by FISH risk categories',
        'default': True,
        'control_name_post_analysis': 'PoStrat_FISH_post',
        'subgroups': [
            {'name': 'High-Risk', 'condition': 't(4;14), t(14;16), t(14;20), or del(17p) present'},
            {'name': 'Intermediate-Risk', 'condition': '1q+ or del(1p32) present, but no high-risk markers'},
            {'name': 'Favorable', 'condition': 'del(13q) or t(11;14) only; no high/intermediate-risk markers'}
        ],
        'info': {
            'title': 'FISH Indicators Grouping',
            'description': 'Stratifies patients based on fluorescence in situ hybridization (FISH) cytogenetic abnormalities, grouping them by their biological and prognostic significance.',
            'algorithm': 'Patients are assigned to FISH risk groups based on presence/absence of specific cytogenetic abnormalities. Risk scoring considers high-risk translocations (t(4;14), t(14;16), t(14;20), del(17p)), intermediate-risk abnormalities (1q+, del(1p32)), and favorable abnormalities (del(13q), t(11;14)).',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '25 patients', 'description': 'Ensures adequate statistical power in each subgroup'},
                {'name': 'Risk scoring method', 'default': 'Standard risk scoring', 'description': 'How to combine multiple FISH abnormalities into risk groups'}
            ],
            'pros': [
                'Biologically meaningful stratification based on genetic abnormalities',
                'Strong prognostic value for multiple myeloma outcomes',
                'Clinically actionable subgroups with different treatment approaches',
                'Well-established cytogenetic risk classification',
                'Identifies patients who may benefit from risk-adapted therapies'
            ],
            'cons': [
                'Requires FISH testing results for all patients',
                'Complex interpretation of multiple abnormalities',
                'Some abnormalities have overlapping prognostic implications',
                'Cost and availability of FISH testing may limit application'
            ],
            'limitations': [
                'Limited to patients with available FISH results',
                'May not capture all prognostic cytogenetic information',
                'Some abnormalities are rare and may result in small subgroups'
            ],
            'expectations': 'Creates 4-5 cytogenetic risk groups with distinct microbial profiles and treatment responses'
        }
    },

    'disease_characteristics': {
        'control_name_post_analysis': 'PoStrat_disease_post',
        'name': 'Disease Characteristics Stratification',
        'description': 'Clinical disease features grouped by risk categories',
        'default': False,
        'subgroups': [
            {'name': 'Low Risk', 'condition': 'ISS I or R-ISS I, no high-risk mutations, normal labs'},
            {'name': 'Intermediate Risk', 'condition': 'ISS II or R-ISS II, or single high-risk feature'},
            {'name': 'High Risk', 'condition': 'ISS III or R-ISS III, multiple high-risk mutations, abnormal labs'}
        ],
        'info': {
            'title': 'Disease Characteristics Grouping',
            'description': 'Stratifies patients based on clinical disease characteristics including staging (ISS/R-ISS), molecular risk factors, and functional assessments.',
            'algorithm': 'Composite risk scoring system combining ISS stage (I/II/III), R-ISS stage, high-risk mutations, ultra-high-risk mutations, IMWG high-risk features, functional high-risk, and laboratory parameters (beta-2 microglobulin, creatinine, albumin).',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '20 patients', 'description': 'Ensures statistical power in disease subgroups'},
                {'name': 'Risk score thresholds', 'default': 'Standard ISS/R-ISS', 'description': 'Boundaries for defining risk groups'}
            ],
            'pros': [
                'Clinically relevant stratification using established prognostic factors',
                'Comprehensive assessment combining multiple disease parameters',
                'Strong evidence base from clinical trials and studies',
                'Guides treatment intensity and clinical decision-making',
                'Identifies patients needing more aggressive therapeutic approaches'
            ],
            'cons': [
                'Requires complete clinical data for accurate stratification',
                'Some parameters may be correlated, leading to redundancy',
                'Thresholds may vary by patient population and treatment era',
                'May not capture emerging prognostic biomarkers'
            ],
            'limitations': [
                'Dependent on quality and completeness of clinical data',
                'Some high-risk features are relatively rare',
                'Scoring systems may need periodic updates as new data emerges'
            ],
            'expectations': 'Creates 3-4 disease risk groups with different microbial associations and survival outcomes'
        }
    },

    'demographics_age': {
        'name': 'Demographics — Age Stratification',
        'description': 'Age strata imported from metadata/STRATIFICATIONS.py (quantile or clinical boundaries).',
        'default': False,
        'control_name_post_analysis': 'PoStrat_age_post',
        'subgroups': [
            {'name': 'Young (≤50 years)', 'condition': 'Age ≤ 50'},
            {'name': 'Middle-aged (51-65 years)', 'condition': '51 ≤ Age ≤ 65'},
            {'name': 'Elderly (>65 years)', 'condition': 'Age > 65'}
        ],
        'info': {
            'title': 'Demographics — Age',
            'description': 'Age strata imported from metadata/STRATIFICATIONS.py (quantile or clinical boundaries).',
            'algorithm': 'Uses STRATIFICATIONS.demographics.age configuration (type="continuous", method="quantile" by default).',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '15 patients', 'description': 'Ensures adequate sample size in age subgroups'},
                {'name': 'Age group boundaries', 'default': 'Quantile/Clinical', 'description': 'Method for defining age bins'}
            ],
            'expectations': 'Creates three age strata by default per STRATIFICATIONS definitions.'
        }
    },

    'demographics_bmi': {
        'name': 'Demographics — BMI Stratification',
        'description': 'BMI strata imported from metadata/STRATIFICATIONS.py (clinical method).',
        'default': False,
        'control_name_post_analysis': 'PoStrat_bmi_post',
        'subgroups': [
            {'name': 'Underweight (BMI <18.5)', 'condition': 'BMI < 18.5'},
            {'name': 'Normal (BMI 18.5-24.9)', 'condition': '18.5 ≤ BMI < 25'},
            {'name': 'Overweight (BMI 25-29.9)', 'condition': '25 ≤ BMI < 30'},
            {'name': 'Obese (BMI ≥30)', 'condition': 'BMI ≥ 30'}
        ],
        'info': {
            'title': 'Demographics — BMI',
            'description': 'BMI strata imported from metadata/STRATIFICATIONS.py (clinical method).',
            'algorithm': 'Uses STRATIFICATIONS.demographics.bmi configuration (type="continuous", method="clinical").',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '15 patients', 'description': 'Ensures adequate sample size in BMI subgroups'},
                {'name': 'BMI categories', 'default': 'WHO categories', 'description': 'BMI classification scheme'}
            ],
            'expectations': 'Creates BMI strata per STRATIFICATIONS definitions.'
        }
    },

    'demographics_smoking': {
        'name': 'Demographics — Smoking Stratification',
        'description': 'Smoking strata imported from metadata/STRATIFICATIONS.py (categorical method).',
        'default': False,
        'control_name_post_analysis': 'PoStrat_smoking_post',
        'subgroups': [
            {'name': 'Never', 'condition': "values in ['Never','0','No']"},
            {'name': 'Former', 'condition': "values in ['Former','1','Yes']"},
            {'name': 'Current', 'condition': "values in ['Current','2']"}
        ],
        'info': {
            'title': 'Demographics — Smoking',
            'description': 'Smoking strata imported from metadata/STRATIFICATIONS.py (categorical method).',
            'algorithm': 'Uses STRATIFICATIONS.demographics.smoking configuration (type="categorical").',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '15 patients', 'description': 'Ensures adequate sample size in smoking subgroups'}
            ],
            'expectations': 'Creates smoking-status strata per STRATIFICATIONS definitions.'
        }
    },

    'genomic_markers': {
        'name': 'Genomic Markers Stratification',
        'default': False,
        'description': 'Molecular markers grouped by functional pathways',
        'control_name_post_analysis': 'PoStrat_genomic_post',
        'parameters': {
            'min_samples_per_group': {
                'type': 'int',
                'default': 10,
                'min': 5,
                'max': 50,
                'step': 5,
                'label': 'Minimum Samples per Group',
                'description': 'Minimum number of patients required in each genomic subgroup'
            },
            'mutation_detection_method': {
                'type': 'select',
                'default': 'any',
                'options': [
                    {'value': 'any', 'label': 'Any Mutation Detected'},
                    {'value': 'confirmed', 'label': 'Confirmed Pathogenic'},
                    {'value': 'functional', 'label': 'Functional Impact Assessed'}
                ],
                'label': 'Mutation Detection Criteria',
                'description': 'How to determine presence of genomic alterations'
            }
        },
        'enabled': False,
        'order': 7,
        'group_info': [
            '• **TP53 Mutated:** Any pathogenic TP53 mutation or deletion.',
            '• **MYC Rearranged:** Presence of MYC rearrangement.',
            '• **Cyclin D Abnormal:** D1/D2/D3 overexpression or rearrangement.',
            '• **MAF Rearranged:** MAF/MAFB rearrangement.',
            '  - **Assignment Rule:** Patient is assigned to all matching groups based on detected mutations.'
        ],
        'subgroups': [
            {'name': 'TP53 Mutated', 'condition': 'Pathogenic TP53 mutation or deletion present'},
            {'name': 'MYC Rearranged', 'condition': 'MYC rearrangement present'},
            {'name': 'Cyclin D Abnormal', 'condition': 'D1/D2/D3 overexpression or rearrangement present'},
            {'name': 'MAF Rearranged', 'condition': 'MAF/MAFB rearrangement present'}
        ],
        'info': {
            'title': 'Genomic Markers Grouping',
            'description': 'Stratifies patients based on genomic alterations in key pathways including tumor suppressor genes, oncogenes, cell cycle regulators, and transcription factors.',
            'algorithm': 'Patients are grouped based on mutations in TP53, RB1 deletion, MYC rearrangements, cyclin abnormalities (D1/D2/D3), and MAF rearrangements. Risk scoring considers functional impact and pathway involvement.',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '10 patients', 'description': 'Minimum size for genomic subgroups'},
                {'name': 'Mutation detection criteria', 'default': 'Any mutation detected', 'description': 'Standards for calling genomic alterations'}
            ],
            'pros': [
                'Direct biological insight into disease mechanisms',
                'Strong prognostic value for genomic alterations',
                'Identifies patients who may benefit from targeted therapies',
                'Growing evidence base from genomic studies',
                'Potential for predictive biomarker development'
            ],
            'cons': [
                'Requires comprehensive genomic testing',
                'Many alterations are rare, leading to small subgroups',
                'Complex interpretation of multiple concurrent alterations',
                'Cost and technical expertise required for testing'
            ],
            'limitations': [
                'Limited to patients with available genomic data',
                'Some alterations may not be functionally significant',
                'Genomic testing may not be routine in all clinical settings'
            ],
            'expectations': 'Creates 3-4 genomic risk groups with distinct microbial associations and therapeutic implications'
        }
    },

    'laboratory_values': {
        'name': 'Laboratory Values Stratification',
        'default': False,
        'description': 'Lab parameters grouped by organ system function',
        'control_name_post_analysis': 'PoStrat_laboratory_post',
        'parameters': {
            'min_samples_per_group': {
                'type': 'int',
                'default': 30,
                'min': 15,
                'max': 100,
                'step': 5,
                'label': 'Minimum Samples per Group',
                'description': 'Minimum number of patients required in each laboratory subgroup'
            },
            'lab_value_thresholds': {
                'type': 'select',
                'default': 'clinical',
                'options': [
                    {'value': 'clinical', 'label': 'Clinical Reference Ranges'},
                    {'value': 'population', 'label': 'Population-Based Percentiles'},
                    {'value': 'custom', 'label': 'Custom Thresholds'}
                ],
                'label': 'Laboratory Thresholds',
                'description': 'How to define abnormal vs normal laboratory values'
            }
        },
        'enabled': False,
        'order': 8,
        'group_info': [
            '• **Normal Function:** All labs within reference range.',
            '• **Mild Abnormality:** One or more labs mildly outside reference.',
            '• **Severe Abnormality:** One or more labs severely abnormal.',
            '  - **Assignment Rule:** Lab values are compared to clinical or population thresholds as defined in parameters.'
        ],
        'subgroups': [
            {'name': 'Normal Function', 'condition': 'All labs within reference range'},
            {'name': 'Mild Abnormality', 'condition': 'One or more labs mildly outside reference'},
            {'name': 'Severe Abnormality', 'condition': 'One or more labs severely abnormal'}
        ],
        'info': {
            'title': 'Laboratory Values Grouping',
            'description': 'Stratifies patients based on laboratory parameters reflecting organ system function, including renal, hepatic, hematologic, and inflammatory markers.',
            'algorithm': 'Composite laboratory risk scoring using beta-2 microglobulin, creatinine, albumin, LDH, hemoglobin, platelet count, neutrophil count, and lymphocyte count. Risk groups are defined by degree of organ dysfunction.',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '30 patients', 'description': 'Ensures power in laboratory-based subgroups'},
                {'name': 'Laboratory thresholds', 'default': 'Clinical reference ranges', 'description': 'Criteria for defining abnormal values'}
            ],
            'pros': [
                'Objective, quantitative measures of organ function',
                'Strong prognostic value in multiple myeloma',
                'Reflects treatment tolerability and complications risk',
                'Widely available in clinical practice',
                'Helps identify patients needing dose adjustments or supportive care'
            ],
            'cons': [
                'Laboratory values can change over time and with treatment',
                'May reflect disease activity rather than patient fitness',
                'Some values correlate with each other',
                'Reference ranges may vary by laboratory and population'
            ],
            'limitations': [
                'Single time point may not reflect dynamic changes',
                'Treatment effects can alter laboratory values',
                'Some tests may not be performed in all patients'
            ],
            'expectations': 'Creates 3-4 laboratory risk groups with different microbial profiles and treatment outcomes'
        }
    },

    'treatment_response': {
        'name': 'Treatment Response Stratification',
        'default': False,
        'description': 'Treatment variables grouped by response patterns',
        'control_name_post_analysis': 'PoStrat_treatment_post',
        'parameters': {
            'min_samples_per_group': {
                'type': 'int',
                'default': 15,
                'min': 10,
                'max': 50,
                'step': 5,
                'label': 'Minimum Samples per Group',
                'description': 'Minimum number of patients required in each treatment subgroup'
            },
            'response_definition': {
                'type': 'select',
                'default': 'imwg',
                'options': [
                    {'value': 'imwg', 'label': 'IMWG Response Criteria'},
                    {'value': 'ebmt', 'label': 'EBMT Response Criteria'},
                    {'value': 'custom', 'label': 'Custom Definitions'}
                ],
                'label': 'Response Criteria',
                'description': 'Standards for defining treatment response'
            }
        },
        'enabled': False,
        'order': 9,
        'group_info': [
            '• **Complete Response (CR):** Meets IMWG/EBMT criteria for CR.',
            '• **Partial Response (PR):** Meets criteria for PR.',
            '• **No Response (NR):** Does not meet PR or CR.',
            '• **Transplant Status:** Single, double, or no transplant.',
            '  - **Assignment Rule:** Response and treatment data are evaluated per selected criteria.'
        ],
        'subgroups': [
            {'name': 'Complete Response (CR)', 'condition': 'Meets IMWG/EBMT criteria for CR'},
            {'name': 'Partial Response (PR)', 'condition': 'Meets criteria for PR'},
            {'name': 'No Response (NR)', 'condition': 'Does not meet PR or CR'},
            {'name': 'Transplant: Single', 'condition': 'Single transplant performed'},
            {'name': 'Transplant: Double', 'condition': 'Double transplant performed'},
            {'name': 'Transplant: None', 'condition': 'No transplant performed'}
        ],
        'info': {
            'title': 'Treatment Response Grouping',
            'description': 'Stratifies patients based on treatment history, transplant status, and response to therapy, including induction regimens, transplant details, and outcome measures.',
            'algorithm': 'Patients are grouped by transplant status (single/double/none), induction therapy type, melphalan dose, transplant timing, and outcome measures (PFS status, death status, survival duration). Response patterns are analyzed longitudinally.',
            'parameters': [
                {'name': 'Minimum samples per group', 'default': '15 patients', 'description': 'Minimum size for treatment response subgroups'},
                {'name': 'Response criteria', 'default': 'IMWG criteria', 'description': 'Standards for assessing treatment response'}
            ],
            'pros': [
                'Directly relevant to clinical decision-making',
                'Identifies patients with different treatment needs',
                'Helps understand microbial changes with therapy',
                'Supports treatment optimization and sequencing',
                'May identify predictive biomarkers for response'
            ],
            'cons': [
                'Treatment effects may confound microbial associations',
                'Response assessment can be subjective',
                'Treatment regimens vary over time',
                'Some patients may have incomplete treatment data'
            ],
            'limitations': [
                'Limited to patients who have received treatment',
                'Treatment-related changes may mask baseline associations',
                'Response criteria may evolve over time',
                'Some treatments may alter microbiome directly'
            ],
            'expectations': 'Creates 3-4 treatment response groups with different microbial dynamics and clinical trajectories'
        }
    }
}

