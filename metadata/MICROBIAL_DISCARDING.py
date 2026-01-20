MICROBIAL_DISCARDING = {
    'prevalence_filtering': {
        'name': 'Prevalence Filtering',
        'description': 'Discard taxa present in fewer than a specified percentage of samples',
        'param_prefix': 'MiDi_Prevalence_',
        'parameters': {
            'detection_threshold': {
                'type': 'float',
                'default': 0.0,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Detection Threshold',
                'description': 'Minimum abundance to consider taxon present (default: >0)',
                'control_name': 'MiDi_Prevalence_detection_threshold'
            },
            'min_prevalence': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 1.0,
                'step': 0.01,
                'label': 'Minimum Prevalence (%)',
                'description': 'Minimum fraction of samples where taxon must be present',
                'control_name': 'MiDi_Prevalence_min_prevalence'
            }
        },
        'enabled': False,
        'order': 1,
        'info': {
            'title': 'Prevalence Filtering',
            'description': 'Discard microbial taxa present in fewer than a specified percentage of samples, removing unreliable measurements.',
            'algorithm': 'For each taxon: prevalence = (abundance > detection_threshold).sum() / total_samples; if prevalence < min_prevalence_threshold: discard_taxon',
            'parameters': [
                {'name': 'Detection threshold', 'default': '>0', 'description': 'Minimum abundance to consider taxon present'},
                {'name': 'Minimum prevalence', 'default': '10% of samples', 'description': 'Minimum fraction of samples where taxon must be present'}
            ],
            'pros': [
                'Data quality control - Eliminates measurement artifacts and rare taxa',
                'Statistical reliability - Focuses on consistently detectable microbes',
                'Computational efficiency - Reduces dataset size significantly',
                'Reproducibility - Removes taxa with unreliable abundance estimates',
                'Simple implementation - Easy to understand and apply'
            ],
            'cons': [
                'May discard important taxa - Some biologically relevant microbes may be rare',
                'Arbitrary thresholds - Prevalence cutoff is subjective',
                'Context dependence - Optimal prevalence varies by study design and technology',
                'False negatives - Rare pathogens or keystone species may be excluded'
            ],
            'limitations': [
                'Doesn\'t consider abundance levels, only presence/absence',
                'May be too conservative for some research questions',
                'Threshold selection requires biological knowledge'
            ],
            'expectations': 'Reduces taxa count by 20-60%, depending on threshold'
        }
    },

    'abundance_filtering': {
        'name': 'Abundance Filtering',
        'description': 'Discard taxa with consistently low abundance across samples',
        'param_prefix': 'MiDi_Abundance_',
        'parameters': {
            'min_mean_abundance': {
                'type': 'float',
                'default': 0.0001,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Mean Abundance (%)',
                'description': 'Minimum mean relative abundance threshold',
                'control_name': 'MiDi_Abundance_min_mean_abundance'
            },
            'min_median_abundance': {
                'type': 'float',
                'default': 0.00005,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Median Abundance (%)',
                'description': 'Minimum median relative abundance threshold',
                'control_name': 'MiDi_Abundance_min_median_abundance'
            }
        },
        'enabled': False,
        'order': 2,
        'info': {
            'title': 'Abundance Filtering',
            'description': 'Discard taxa with consistently low abundance across samples, focusing on ecologically important microbes.',
            'algorithm': 'For each taxon: mean_abundance = taxon_abundances.mean(); median_abundance = taxon_abundances.median(); if mean_abundance < min_mean_threshold or median_abundance < min_median_threshold: discard_taxon',
            'parameters': [
                {'name': 'Minimum mean abundance', 'default': '0.01% relative abundance', 'description': 'Minimum mean relative abundance threshold'},
                {'name': 'Minimum median abundance', 'default': '0.005% relative abundance', 'description': 'Minimum median relative abundance threshold'}
            ],
            'pros': [
                'Ecological relevance - Focuses on microbes that contribute meaningfully to community',
                'Measurement precision - Removes taxa near detection limits',
                'Biological signal - Prioritizes microbes with functional impact',
                'Data normalization - Complements relative abundance transformations',
                'Statistical power - Reduces noise in downstream analyses'
            ],
            'cons': [
                'Context dependence - Abundance thresholds vary by sample type and technology',
                'Functional bias - May exclude important low-abundance functional specialists',
                'Normalization effects - Results depend on abundance transformation method',
                'Sample variability - Abundance distributions vary across studies'
            ],
            'limitations': [
                'Arbitrary thresholds - No universal abundance cutoff exists',
                'Scale dependence - Results vary with sequencing depth and technology',
                'Biological context - Some low-abundance taxa are functionally important'
            ],
            'expectations': 'Reduces taxa count by 30-70%, depending on threshold and sample type'
        }
    },

    'taxonomic_rarity_filtering': {
        'name': 'Taxonomic Rarity Filtering',
        'description': 'Filter out rare taxa that appear in very few samples regardless of abundance',
        'param_prefix': 'MiDi_Rarity_',
        'parameters': {
            'min_sample_count': {
                'type': 'int',
                'default': 3,
                'min': 1,
                'max': 50,
                'step': 1,
                'label': 'Minimum Sample Count',
                'description': 'Minimum number of samples where taxon must be detected',
                'control_name': 'MiDi_Rarity_min_sample_count'
            },
            'rarity_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'label': 'Rarity Threshold',
                'description': 'Maximum proportion of samples where rare taxa are allowed',
                'control_name': 'MiDi_Rarity_rarity_threshold'
            }
        },
        'enabled': False,
        'order': 3,
        'info': {
            'title': 'Taxonomic Rarity Filtering',
            'description': 'Filter out rare taxa that appear in very few samples regardless of abundance, focusing on consistently detectable microbes.',
            'algorithm': 'For each taxon: sample_count = number of samples with abundance > detection_threshold; if sample_count < min_sample_count: discard_taxon',
            'parameters': [
                {'name': 'Minimum sample count', 'default': '3 samples', 'description': 'Minimum number of samples where taxon must be detected'},
                {'name': 'Rarity threshold', 'default': '1% of samples', 'description': 'Maximum proportion of samples where rare taxa are allowed'}
            ],
            'pros': [
                'Conservative approach - Ensures taxa are consistently detectable',
                'Measurement reliability - Focuses on taxa with multiple measurements',
                'Statistical stability - Reduces variance from sporadic detections',
                'Quality control - Removes potential contamination artifacts',
                'Simple and transparent - Easy to understand and communicate'
            ],
            'cons': [
                'May be too conservative - Excludes biologically relevant rare taxa',
                'Context dependence - Appropriate thresholds vary by study size',
                'Sample size bias - Larger studies can retain rarer taxa',
                'Technology dependence - Detection limits vary by sequencing platform'
            ],
            'limitations': [
                'Doesn\'t consider ecological importance of rare taxa',
                'May exclude important low-prevalence pathogens',
                'Threshold selection is somewhat arbitrary'
            ],
            'expectations': 'Reduces taxa count by 15-40%, depending on study size and detection threshold'
        }
    },

    'low_abundance_taxa_removal': {
        'name': 'Low Abundance Taxa Removal',
        'description': 'Remove taxa that never exceed a specified abundance threshold in any sample',
        'param_prefix': 'MiDi_LowAbundance_',
        'parameters': {
            'max_abundance_threshold': {
                'type': 'float',
                'default': 0.001,
                'min': 0.0,
                'max': 0.1,
                'step': 0.0001,
                'label': 'Maximum Abundance Threshold (%)',
                'description': 'Taxa exceeding this threshold in any sample will be retained',
                'control_name': 'MiDi_LowAbundance_max_abundance_threshold'
            },
            'keep_top_n': {
                'type': 'int',
                'default': 100,
                'min': 10,
                'max': 1000,
                'step': 10,
                'label': 'Keep Top N Taxa',
                'description': 'Always retain the N most abundant taxa regardless of threshold',
                'control_name': 'MiDi_LowAbundance_keep_top_n'
            }
        },
        'enabled': False,
        'order': 4,
        'info': {
            'title': 'Low Abundance Taxa Removal',
            'description': 'Remove taxa that never exceed a specified abundance threshold in any sample, focusing on potentially impactful microbes.',
            'algorithm': 'For each taxon: max_abundance = maximum abundance across all samples; if max_abundance < max_abundance_threshold: discard_taxon; keep top N most abundant taxa regardless',
            'parameters': [
                {'name': 'Maximum abundance threshold', 'default': '0.1% relative abundance', 'description': 'Taxa exceeding this threshold in any sample will be retained'},
                {'name': 'Keep top N taxa', 'default': '100 taxa', 'description': 'Always retain the N most abundant taxa regardless of threshold'}
            ],
            'pros': [
                'Ecological focus - Prioritizes microbes that can dominate communities',
                'Functional relevance - High abundance often correlates with ecological impact',
                'Data quality - Removes taxa consistently near detection limits',
                'Computational efficiency - Significantly reduces dataset size',
                'Biological plausibility - Low abundance taxa may be ecologically irrelevant'
            ],
            'cons': [
                'May exclude important taxa - Some functional specialists are low abundance',
                'Context dependence - Abundance thresholds vary by ecosystem',
                'Detection limit bias - Results depend on sequencing technology sensitivity',
                'Temporal variability - Abundance peaks may be missed in sampling'
            ],
            'limitations': [
                'Assumes abundance correlates with importance',
                'May miss rare but ecologically important taxa',
                'Threshold selection requires ecological knowledge'
            ],
            'expectations': 'Reduces taxa count by 40-80%, depending on threshold and ecosystem'
        }
    },

    'contaminant_filtering': {
        'name': 'Contaminant Filtering',
        'description': 'Remove potential contaminants based on prevalence in negative controls',
        'param_prefix': 'MiDi_Contaminant_',
        'parameters': {
            'control_prevalence_threshold': {
                'type': 'float',
                'default': 0.5,
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'label': 'Control Prevalence Threshold (%)',
                'description': 'Maximum prevalence allowed in negative controls',
                'control_name': 'MiDi_Contaminant_control_prevalence_threshold'
            },
            'control_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Control Abundance Threshold (%)',
                'description': 'Maximum abundance allowed in negative controls',
                'control_name': 'MiDi_Contaminant_control_abundance_threshold'
            }
        },
        'enabled': False,
        'order': 5,
        'info': {
            'title': 'Contaminant Filtering',
            'description': 'Remove potential contaminants based on prevalence in negative controls, ensuring data quality.',
            'algorithm': 'For each taxon: control_prevalence = prevalence in negative controls; control_abundance = mean abundance in controls; if control_prevalence > threshold or control_abundance > threshold: discard_taxon',
            'parameters': [
                {'name': 'Control prevalence threshold', 'default': '50% of controls', 'description': 'Maximum prevalence allowed in negative controls'},
                {'name': 'Control abundance threshold', 'default': '1% relative abundance', 'description': 'Maximum abundance allowed in negative controls'}
            ],
            'pros': [
                'Data quality assurance - Removes laboratory contamination artifacts',
                'Experimental validity - Ensures microbial signal is biological, not technical',
                'Reproducibility - Standardizes contamination removal across studies',
                'Method validation - Uses experimental controls for quality control',
                'Publication standards - Meets rigorous microbiome data quality requirements'
            ],
            'cons': [
                'Requires controls - Not applicable without negative control samples',
                'Control quality dependence - Results depend on control sample quality',
                'Conservative approach - May remove true low-level contaminants',
                'Control variability - Different labs may have different contamination profiles'
            ],
            'limitations': [
                'Limited to studies with proper negative controls',
                'May not detect all contamination types',
                'Control contamination may not reflect sample contamination'
            ],
            'expectations': 'Removes 5-20% of taxa, depending on laboratory and sequencing conditions'
        }
    },

    'singleton_filtering': {
        'name': 'Singleton Filtering',
        'description': 'Remove taxa that appear as singletons (detected in only one sample)',
        'param_prefix': 'MiDi_Singleton_',
        'parameters': {
            'remove_singletons': {
                'type': 'select',
                'default': 'strict',
                'options': [
                    {'value': 'strict', 'label': 'Strict (remove all singletons)'},
                    {'value': 'lenient', 'label': 'Lenient (keep if abundance > threshold)'},
                    {'value': 'none', 'label': 'Keep all singletons'}
                ],
                'label': 'Singleton Removal Strategy',
                'description': 'How to handle taxa detected in only one sample',
                'control_name': 'MiDi_Singleton_remove_singletons'
            },
            'singleton_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Singleton Abundance Threshold (%)',
                'description': 'Minimum abundance to retain singletons (for lenient mode)',
                'control_name': 'MiDi_Singleton_singleton_abundance_threshold'
            }
        },
        'enabled': False,
        'order': 6,
        'info': {
            'title': 'Singleton Filtering',
            'description': 'Remove taxa that appear as singletons (detected in only one sample), reducing potential artifacts.',
            'algorithm': 'For each taxon: detection_count = number of samples with abundance > detection_threshold; if detection_count == 1: apply singleton strategy',
            'parameters': [
                {'name': 'Singleton removal strategy', 'default': 'Strict removal', 'description': 'How to handle taxa detected in only one sample'},
                {'name': 'Singleton abundance threshold', 'default': '1% relative abundance', 'description': 'Minimum abundance to retain singletons (for lenient mode)'}
            ],
            'pros': [
                'Artifact removal - Eliminates likely sequencing or PCR errors',
                'Data quality - Focuses on consistently detectable taxa',
                'Statistical reliability - Removes highly variable singleton measurements',
                'Computational stability - Reduces noise in diversity calculations',
                'Biological plausibility - Singletons may represent contamination'
            ],
            'cons': [
                'May remove real taxa - Some microbes are legitimately rare',
                'Overly conservative - Excludes potentially important low-prevalence taxa',
                'Detection limit dependence - Results vary with sequencing sensitivity',
                'Biological context ignored - All singletons treated equally'
            ],
            'limitations': [
                'Doesn\'t distinguish between true rarity and artifacts',
                'May exclude important rare biosphere members',
                'Threshold for "singleton" may not be biologically meaningful'
            ],
            'expectations': 'Removes 10-30% of taxa, depending on sequencing depth and technology'
        }
    },

    'variance_based_selection': {
        'name': 'Variance-Based Selection',
        'description': 'Select taxa with highest variance across samples',
        'param_prefix': 'MiDi_Variance_',
        'parameters': {
            'num_taxa_to_select': {
                'type': 'int',
                'default': 50,
                'min': 5,
                'max': 200,
                'step': 5,
                'label': 'Number of Taxa to Select',
                'description': 'Maximum number of most variable taxa to retain',
                'control_name': 'MiDi_Variance_num_taxa_to_select'
            },
            'variance_metric': {
                'type': 'select',
                'default': 'coefficient_of_variation',
                'options': [
                    {'value': 'total_variance', 'label': 'Total Variance'},
                    {'value': 'coefficient_of_variation', 'label': 'Coefficient of Variation'}
                ],
                'label': 'Variance Metric',
                'description': 'Method to measure taxon variability',
                'control_name': 'MiDi_Variance_variance_metric'
            }
        },
        'enabled': False,
        'order': 7,
        'info': {
            'title': 'Variance-Based Selection',
            'description': 'Select taxa with highest variance across samples, focusing on microbes that vary between conditions.',
            'algorithm': 'For each taxon: calculate variance metric (total variance or coefficient of variation); rank taxa by variance; select top N most variable taxa',
            'parameters': [
                {'name': 'Number of taxa to select', 'default': '50 taxa', 'description': 'Maximum number of most variable taxa to retain'},
                {'name': 'Variance metric', 'default': 'Coefficient of variation', 'description': 'Method to measure taxon variability'}
            ],
            'pros': [
                'Biological relevance - Variable taxa often respond to environmental changes',
                'Differential abundance focus - Prioritizes taxa that differ between groups',
                'Statistical power - Variable taxa are easier to detect as significant',
                'Ecological insight - Highlights taxa involved in community dynamics',
                'Data-driven approach - Uses empirical variability patterns'
            ],
            'cons': [
                'May select noise - High variance doesn\'t always indicate biological signal',
                'Context dependence - Important taxa may be consistently present',
                'Scale dependence - Variance depends on abundance transformation',
                'Confounding factors - Variance may reflect technical rather than biological factors'
            ],
            'limitations': [
                'Assumes variable taxa are more important',
                'May miss consistently important taxa',
                'Variance calculation sensitive to outliers'
            ],
            'expectations': 'Selects 50-200 most variable taxa, depending on desired subset size'
        }
    },

    'taxonomic_level_filtering': {
        'name': 'Taxonomic Level Filtering',
        'description': 'Filter taxa based on their taxonomic classification level',
        'param_prefix': 'MiDi_TaxonomicLevel_',
        'parameters': {
            'min_taxonomic_level': {
                'type': 'select',
                'default': 'genus',
                'options': [
                    {'value': 'kingdom', 'label': 'Kingdom'},
                    {'value': 'phylum', 'label': 'Phylum'},
                    {'value': 'class', 'label': 'Class'},
                    {'value': 'order', 'label': 'Order'},
                    {'value': 'family', 'label': 'Family'},
                    {'value': 'genus', 'label': 'Genus'},
                    {'value': 'species', 'label': 'Species'}
                ],
                'label': 'Minimum Taxonomic Level',
                'description': 'Require taxa to be classified at least to this level',
                'control_name': 'MiDi_TaxonomicLevel_min_taxonomic_level'
            },
            'remove_unclassified': {
                'type': 'select',
                'default': 'strict',
                'options': [
                    {'value': 'strict', 'label': 'Remove all unclassified'},
                    {'value': 'lenient', 'label': 'Keep if identified at higher levels'},
                    {'value': 'none', 'label': 'Keep all taxa'}
                ],
                'label': 'Unclassified Taxa Handling',
                'description': 'How to handle taxa without complete classification',
                'control_name': 'MiDi_TaxonomicLevel_remove_unclassified'
            }
        },
        'enabled': False,
        'order': 8,
        'info': {
            'title': 'Taxonomic Level Filtering',
            'description': 'Filter taxa based on their taxonomic classification level, ensuring reliable taxonomic assignment.',
            'algorithm': 'For each taxon: check taxonomic classification depth; if classification level < min_required_level: discard_taxon',
            'parameters': [
                {'name': 'Minimum taxonomic level', 'default': 'Genus level', 'description': 'Require taxa to be classified at least to this level'},
                {'name': 'Unclassified taxa handling', 'default': 'Remove all unclassified', 'description': 'How to handle taxa without complete classification'}
            ],
            'pros': [
                'Taxonomic reliability - Ensures taxa are properly identified',
                'Comparative analysis - Enables cross-study comparisons',
                'Biological interpretation - Provides meaningful taxonomic context',
                'Database quality - Reflects quality of taxonomic reference database',
                'Standardization - Creates consistent taxonomic resolution across studies'
            ],
            'cons': [
                'Resolution loss - May exclude taxa only identifiable to higher levels',
                'Database dependence - Results vary with classification database quality',
                'Biological information loss - Higher-level taxa may be ecologically relevant',
                'Conservative approach - May be too restrictive for some analyses'
            ],
            'limitations': [
                'Depends on reference database completeness',
                'May exclude novel or poorly characterized taxa',
                'Arbitrary level cutoffs may not reflect biological reality'
            ],
            'expectations': 'Retains 60-90% of taxa, depending on classification database and required level'
        }
    },

    'core_microbiome_filtering': {
        'name': 'Core Microbiome Filtering',
        'description': 'Retain only taxa that are part of the core microbiome',
        'param_prefix': 'MiDi_CoreMicrobiome_',
        'parameters': {
            'core_prevalence_threshold': {
                'type': 'float',
                'default': 0.8,
                'min': 0.5,
                'max': 1.0,
                'step': 0.01,
                'label': 'Core Prevalence Threshold (%)',
                'description': 'Minimum prevalence to be considered core microbiome',
                'control_name': 'MiDi_CoreMicrobiome_core_prevalence_threshold'
            },
            'core_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 0.1,
                'step': 0.001,
                'label': 'Core Abundance Threshold (%)',
                'description': 'Minimum abundance to be considered core microbiome',
                'control_name': 'MiDi_CoreMicrobiome_core_abundance_threshold'
            }
        },
        'enabled': False,
        'order': 9,
        'info': {
            'title': 'Core Microbiome Filtering',
            'description': 'Retain only taxa that are part of the core microbiome, focusing on consistently present microbes.',
            'algorithm': 'For each taxon: calculate prevalence across all samples; if prevalence >= core_prevalence_threshold and mean_abundance >= core_abundance_threshold: retain_taxon',
            'parameters': [
                {'name': 'Core prevalence threshold', 'default': '80% of samples', 'description': 'Minimum prevalence to be considered core microbiome'},
                {'name': 'Core abundance threshold', 'default': '1% relative abundance', 'description': 'Minimum abundance to be considered core microbiome'}
            ],
            'pros': [
                'Ecological stability - Focuses on consistently present community members',
                'Functional importance - Core taxa often perform essential ecosystem functions',
                'Comparative studies - Enables cross-sample and cross-study comparisons',
                'Biological relevance - Core microbiome represents stable community structure',
                'Robust analysis - Less sensitive to sampling variability'
            ],
            'cons': [
                'Context dependence - Core microbiome varies by ecosystem and condition',
                'Temporal variability - Core taxa may change over time',
                'Definition ambiguity - No universal definition of "core"',
                'May miss important variable taxa - Focuses on presence, not change'
            ],
            'limitations': [
                'Arbitrary thresholds for core definition',
                'May exclude ecologically important but variable taxa',
                'Core composition changes with environmental conditions'
            ],
            'expectations': 'Retains 10-30 core taxa, depending on ecosystem and thresholds'
        }
    },

    'combined_microbial_selection': {
        'name': 'Combined Microbial Selection',
        'description': 'Apply multiple microbial selection methods and take consensus',
        'param_prefix': 'MiDi_CombinedSelection_',
        'parameters': {
            'consensus_rule': {
                'type': 'select',
                'default': 'intersection',
                'options': [
                    {'value': 'intersection', 'label': 'Intersection (ALL methods)'},
                    {'value': 'union', 'label': 'Union (ANY method)'},
                    {'value': 'weighted', 'label': 'Weighted Voting'}
                ],
                'label': 'Consensus Rule',
                'description': 'How to combine results from multiple methods',
                'control_name': 'MiDi_CombinedSelection_consensus_rule'
            },
            'min_agreement': {
                'type': 'int',
                'default': 2,
                'min': 1,
                'max': 5,
                'step': 1,
                'label': 'Minimum Agreement',
                'description': 'Minimum number of methods that must agree (for weighted voting)',
                'control_name': 'MiDi_CombinedSelection_min_agreement'
            }
        },
        'enabled': False,
        'order': 10,
        'info': {
            'title': 'Combined Microbial Selection',
            'description': 'Apply multiple microbial selection methods and take consensus to identify robustly selected taxa.',
            'algorithm': 'Apply multiple methods independently; combine results using specified consensus rule; retain taxa selected by consensus',
            'parameters': [
                {'name': 'Consensus rule', 'default': 'Intersection (ALL methods)', 'description': 'How to combine results from multiple methods'},
                {'name': 'Minimum agreement', 'default': '2 methods', 'description': 'Minimum number of methods that must agree (for weighted voting)'}
            ],
            'pros': [
                'Robust selection - Taxa selected by multiple methods are more reliable',
                'Method validation - Cross-validation of different filtering approaches',
                'Comprehensive evaluation - Considers multiple data quality aspects',
                'Uncertainty reduction - Reduces method-specific biases',
                'Confidence building - Multiple lines of evidence for retained taxa'
            ],
            'cons': [
                'Computational cost - Running multiple methods increases processing time',
                'Result complexity - Different methods may give conflicting results',
                'Decision complexity - Choosing appropriate consensus rule',
                'Conservative bias - Strict consensus may miss valid taxa',
                'Method dependence - Results depend on which methods are combined'
            ],
            'limitations': [
                'Requires careful selection of complementary methods',
                'Consensus rules are somewhat subjective',
                'May miss taxa only detectable by specific approaches',
                'Interpretation becomes more complex with multiple criteria'
            ],
            'expectations': 'Highly confident retention of 20-50 taxa supported by multiple quality criteria'
        }
    }
}

# Default settings for quick start
DEFAULT_MICROBIAL_DISCARDING_SETTINGS = {
    'prevalence_filtering': {
        'enabled': True,
        'detection_threshold': 0.0,
        'min_prevalence': 0.1
    },
    'abundance_filtering': {
        'enabled': True,
        'min_mean_abundance': 0.0001,
        'min_median_abundance': 0.00005
    }
}