MICROBIAL_DISCARDING = {
    'prevalence_filtering': {
        'name': 'Prevalence Filtering',
        'description': 'Discard taxa present in fewer than a specified percentage of samples',
        'parameters': {
            'detection_threshold': {
                'type': 'float',
                'default': 0.0,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Detection Threshold',
                'description': 'Minimum abundance to consider taxon present (default: >0)'
            },
            'min_prevalence': {
                'type': 'float',
                'default': 0.1,
                'min': 0.01,
                'max': 1.0,
                'step': 0.01,
                'label': 'Minimum Prevalence (%)',
                'description': 'Minimum fraction of samples where taxon must be present'
            }
        },
        'enabled': False,
        'order': 1
    },

    'abundance_filtering': {
        'name': 'Abundance Filtering',
        'description': 'Discard taxa with consistently low abundance across samples',
        'parameters': {
            'min_mean_abundance': {
                'type': 'float',
                'default': 0.0001,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Mean Abundance (%)',
                'description': 'Minimum mean relative abundance threshold'
            },
            'min_median_abundance': {
                'type': 'float',
                'default': 0.00005,
                'min': 0.0,
                'max': 1.0,
                'step': 0.00001,
                'label': 'Minimum Median Abundance (%)',
                'description': 'Minimum median relative abundance threshold'
            }
        },
        'enabled': False,
        'order': 2
    },

    'taxonomic_rarity_filtering': {
        'name': 'Taxonomic Rarity Filtering',
        'description': 'Filter out rare taxa that appear in very few samples regardless of abundance',
        'parameters': {
            'min_sample_count': {
                'type': 'int',
                'default': 3,
                'min': 1,
                'max': 50,
                'step': 1,
                'label': 'Minimum Sample Count',
                'description': 'Minimum number of samples where taxon must be detected'
            },
            'rarity_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'label': 'Rarity Threshold',
                'description': 'Maximum proportion of samples where rare taxa are allowed'
            }
        },
        'enabled': False,
        'order': 3
    },

    'low_abundance_taxa_removal': {
        'name': 'Low Abundance Taxa Removal',
        'description': 'Remove taxa that never exceed a specified abundance threshold in any sample',
        'parameters': {
            'max_abundance_threshold': {
                'type': 'float',
                'default': 0.001,
                'min': 0.0,
                'max': 0.1,
                'step': 0.0001,
                'label': 'Maximum Abundance Threshold (%)',
                'description': 'Taxa exceeding this threshold in any sample will be retained'
            },
            'keep_top_n': {
                'type': 'int',
                'default': 100,
                'min': 10,
                'max': 1000,
                'step': 10,
                'label': 'Keep Top N Taxa',
                'description': 'Always retain the N most abundant taxa regardless of threshold'
            }
        },
        'enabled': False,
        'order': 4
    },

    'contaminant_filtering': {
        'name': 'Contaminant Filtering',
        'description': 'Remove potential contaminants based on prevalence in negative controls',
        'parameters': {
            'control_prevalence_threshold': {
                'type': 'float',
                'default': 0.5,
                'min': 0.0,
                'max': 1.0,
                'step': 0.01,
                'label': 'Control Prevalence Threshold (%)',
                'description': 'Maximum prevalence allowed in negative controls'
            },
            'control_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Control Abundance Threshold (%)',
                'description': 'Maximum abundance allowed in negative controls'
            }
        },
        'enabled': False,
        'order': 5
    },

    'singleton_filtering': {
        'name': 'Singleton Filtering',
        'description': 'Remove taxa that appear as singletons (detected in only one sample)',
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
                'description': 'How to handle taxa detected in only one sample'
            },
            'singleton_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 1.0,
                'step': 0.001,
                'label': 'Singleton Abundance Threshold (%)',
                'description': 'Minimum abundance to retain singletons (for lenient mode)'
            }
        },
        'enabled': False,
        'order': 6
    },

    'variance_based_selection': {
        'name': 'Variance-Based Selection',
        'description': 'Select taxa with highest variance across samples',
        'parameters': {
            'num_taxa_to_select': {
                'type': 'int',
                'default': 50,
                'min': 5,
                'max': 200,
                'step': 5,
                'label': 'Number of Taxa to Select',
                'description': 'Maximum number of most variable taxa to retain'
            },
            'variance_metric': {
                'type': 'select',
                'default': 'coefficient_of_variation',
                'options': [
                    {'value': 'total_variance', 'label': 'Total Variance'},
                    {'value': 'coefficient_of_variation', 'label': 'Coefficient of Variation'}
                ],
                'label': 'Variance Metric',
                'description': 'Method to measure taxon variability'
            }
        },
        'enabled': False,
        'order': 7
    },

    'taxonomic_level_filtering': {
        'name': 'Taxonomic Level Filtering',
        'description': 'Filter taxa based on their taxonomic classification level',
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
                'description': 'Require taxa to be classified at least to this level'
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
                'description': 'How to handle taxa without complete classification'
            }
        },
        'enabled': False,
        'order': 8
    },

    'core_microbiome_filtering': {
        'name': 'Core Microbiome Filtering',
        'description': 'Retain only taxa that are part of the core microbiome',
        'parameters': {
            'core_prevalence_threshold': {
                'type': 'float',
                'default': 0.8,
                'min': 0.5,
                'max': 1.0,
                'step': 0.01,
                'label': 'Core Prevalence Threshold (%)',
                'description': 'Minimum prevalence to be considered core microbiome'
            },
            'core_abundance_threshold': {
                'type': 'float',
                'default': 0.01,
                'min': 0.0,
                'max': 0.1,
                'step': 0.001,
                'label': 'Core Abundance Threshold (%)',
                'description': 'Minimum abundance to be considered core microbiome'
            }
        },
        'enabled': False,
        'order': 9
    },

    'combined_microbial_selection': {
        'name': 'Combined Microbial Selection',
        'description': 'Apply multiple microbial selection methods and take consensus',
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
                'description': 'How to combine results from multiple methods'
            },
            'min_agreement': {
                'type': 'int',
                'default': 2,
                'min': 1,
                'max': 5,
                'step': 1,
                'label': 'Minimum Agreement',
                'description': 'Minimum number of methods that must agree (for weighted voting)'
            }
        },
        'enabled': False,
        'order': 10
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