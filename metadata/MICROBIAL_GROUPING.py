MICROBIAL_GROUPING = {
    'not_grouping': {
        'name': 'No Grouping',
        'description': 'Do not group microbes; analyze all taxa individually.',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'No grouping will be applied.',
                'description': 'All taxa will be analyzed as individual features.'
            }
        },
        'enabled': False,
        'order': 0,
        'info': {
            'title': 'No Grouping',
            'description': 'No grouping strategy is applied. Each microbial taxon is treated as a separate feature in the analysis.',
            'algorithm': 'No grouping or aggregation is performed.',
            'parameters': [
                {'name': 'No grouping', 'default': 'N/A', 'description': 'All taxa are analyzed individually.'}
            ],
            'pros': [
                'Maximum resolution - all taxa considered',
                'No loss of information due to grouping',
                'Direct interpretation of individual taxa effects'
            ],
            'cons': [
                'High dimensionality',
                'Potential for overfitting',
                'Difficult to interpret large numbers of taxa'
            ],
            'limitations': [
                'No biological grouping or functional aggregation',
                'Results may be harder to summarize'
            ],
            'expectations': 'All available taxa are included as separate features.'
        }
    },
    'scfa_producers': {
        'name': 'SCFA Producers',
        'description': 'Group bacteria capable of producing short-chain fatty acids (butyrate, propionate, acetate)',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'SCFA Subgroups',
                'description': 'Butyrate producers: Faecalibacterium, Roseburia, Eubacterium, Coprococcus. Propionate producers: Bacteroides, Veillonella, Akkermansia, Phascolarctobacterium. Acetate producers: Bifidobacterium, Lactobacillus, Prevotella, Streptococcus.'
            }
        },
        'enabled': False,
        'order': 1,
        'info': {
            'title': 'SCFA Producers - Short-Chain Fatty Acid Producers',
            'description': 'Group bacteria capable of producing short-chain fatty acids (butyrate, propionate, acetate) through fermentation of dietary fibers.',
            'algorithm': 'Taxa are grouped based on known metabolic capabilities for SCFA production. Butyrate producers include Faecalibacterium, Roseburia, Eubacterium, Coprococcus. Propionate producers include Bacteroides, Veillonella, Akkermansia, Phascolarctobacterium. Acetate producers include Bifidobacterium, Lactobacillus, Prevotella, Streptococcus.',
            'parameters': [
                {'name': 'Include butyrate producers', 'default': 'Include', 'description': 'Whether to include taxa known for butyrate production'},
                {'name': 'Include propionate producers', 'default': 'Include', 'description': 'Whether to include taxa known for propionate production'},
                {'name': 'Include acetate producers', 'default': 'Include', 'description': 'Whether to include taxa known for acetate production'}
            ],
            'pros': [
                'Strong biological rationale - SCFAs are critical for gut health and immunity',
                'Multiple Myeloma relevance - SCFAs influence inflammation and treatment tolerance',
                'Well-studied mechanisms - Clear pathways linking SCFAs to health outcomes',
                'Therapeutic potential - SCFA modulation is clinically actionable',
                'Abundant literature - Extensive research on SCFA producers'
            ],
            'cons': [
                'Functional overlap - Some taxa produce multiple SCFAs',
                'Strain variation - SCFA production varies by bacterial strain',
                'Dietary dependence - Production depends on available substrates',
                'Limited to saccharolytic bacteria - Misses other functional groups'
            ],
            'limitations': [
                'Requires knowledge of bacterial metabolic capabilities',
                'May miss important non-SCFA producing taxa',
                'SCFA measurements needed for validation (optional)'
            ],
            'expectations': 'Groups 30-60 taxa focused on SCFA production pathways'
        }
    },

    'pathogenic_bacteria': {
        'name': 'Pathogenic Bacteria',
        'description': 'Group bacteria with known pathogenic potential in immunocompromised patients',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Pathogen Subgroups',
                'description': 'Enteric pathogens: Salmonella, Shigella, Campylobacter, Yersinia, Clostridium difficile. Opportunistic pathogens: Pseudomonas, Staphylococcus, Enterococcus, Klebsiella, Acinetobacter. Translocation risks: bacteria associated with gut barrier breach.'
            }
        },
        'enabled': False,
        'order': 2,
        'info': {
            'title': 'Pathogenic Bacteria - Pathogen and Opportunistic Pathogen Groups',
            'description': 'Group bacteria with known pathogenic potential, including enteric pathogens and opportunistic pathogens that can cause infections in immunocompromised patients.',
            'algorithm': 'Taxa are grouped based on documented pathogenicity in clinical settings. Enteric pathogens include Salmonella, Shigella, Campylobacter, Yersinia, Clostridium difficile. Opportunistic pathogens include Pseudomonas, Staphylococcus, Enterococcus, Klebsiella, Acinetobacter. Translocation risks include bacteria associated with gut barrier breach.',
            'parameters': [
                {'name': 'Include enteric pathogens', 'default': 'Include', 'description': 'Whether to include common enteric pathogens'},
                {'name': 'Include opportunistic pathogens', 'default': 'Include', 'description': 'Whether to include opportunistic pathogens'},
                {'name': 'Include translocation risks', 'default': 'Include', 'description': 'Whether to include bacteria associated with barrier breach'}
            ],
            'pros': [
                'Clinical relevance - Direct impact on transplant complications and mortality',
                'Immunosuppression focus - Addresses vulnerability during MM treatment',
                'Clear diagnostic criteria - Well-established pathogen identification',
                'Antibiotic resistance tracking - Monitor resistant strains',
                'Preventive medicine - Identify infection risks before complications'
            ],
            'cons': [
                'Low abundance - Pathogens often present at low levels in healthy gut',
                'Detection challenges - May require sensitive sequencing or culturing',
                'Context dependence - Pathogenicity depends on host immune status',
                'Overemphasis on harm - Misses beneficial microbes that prevent infections'
            ],
            'limitations': [
                'Pathogens may not be detectable in standard microbiome profiling',
                'Requires clinical correlation with infection outcomes',
                'May miss emerging or novel pathogens'
            ],
            'expectations': 'Groups 20-40 taxa focused on known pathogenic species'
        }
    },

    'immunomodulatory_bacteria': {
        'name': 'Immunomodulatory Bacteria',
        'description': 'Group bacteria that directly or indirectly modulate immune system function',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Immunomodulatory Subgroups',
                'description': 'Anti-inflammatory taxa: Faecalibacterium prausnitzii, Bifidobacterium spp., Lactobacillus spp. Treg inducers: Clostridia clusters IV and XIVa, Bacteroides fragilis. Innate immunity modulators: Akkermansia muciniphila, certain Bacteroides strains.'
            }
        },
        'enabled': False,
        'order': 3,
        'info': {
            'title': 'Immunomodulatory Bacteria - Immune System Influencing Microbes',
            'description': 'Group bacteria that directly or indirectly modulate immune system function, including Treg induction, Th17 modulation, and inflammatory responses.',
            'algorithm': 'Taxa are grouped based on documented immunomodulatory effects. Anti-inflammatory taxa include Faecalibacterium prausnitzii, Bifidobacterium spp., Lactobacillus spp. Treg inducers include Clostridia clusters IV and XIVa, Bacteroides fragilis. Innate immunity modulators include Akkermansia muciniphila, certain Bacteroides strains.',
            'parameters': [
                {'name': 'Include anti-inflammatory taxa', 'default': 'Include', 'description': 'Whether to include taxa with anti-inflammatory properties'},
                {'name': 'Include Treg inducers', 'default': 'Include', 'description': 'Whether to include taxa that induce regulatory T cells'},
                {'name': 'Include innate immunity modulators', 'default': 'Include', 'description': 'Whether to include taxa affecting innate immune responses'}
            ],
            'pros': [
                'Direct MM relevance - Immune dysregulation central to MM pathogenesis',
                'Transplant immunology - Critical for graft-vs-host and immune reconstitution',
                'Mechanistic clarity - Well-understood immune pathways',
                'Therapeutic targeting - Immunomodulatory microbes are druggable',
                'Biomarker potential - Immune status indicators'
            ],
            'cons': [
                'Functional complexity - Multiple immune pathways affected',
                'Host genetics influence - Immune responses vary by individual',
                'Context dependence - Effects vary by immune status and timing',
                'Measurement challenges - Immune effects hard to measure from sequencing alone'
            ],
            'limitations': [
                'Requires integration with immune profiling data for validation',
                'Effects may be indirect through metabolites rather than direct contact',
                'Strain-specific variations in immunomodulatory effects'
            ],
            'expectations': 'Groups 25-45 taxa with known immunomodulatory functions'
        }
    },

    'vitamin_synthesis': {
        'name': 'Vitamin Synthesis',
        'description': 'Group bacteria capable of synthesizing essential vitamins (B vitamins, vitamin K)',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Vitamin Synthesis Subgroups',
                'description': 'B vitamin producers: Bifidobacterium, Lactobacillus, Enterococcus, certain Clostridia. Vitamin K producers: Bacteroides, Enterococcus, certain Escherichia coli. Folate producers: Bifidobacterium, Lactobacillus, certain Lactobacilli.'
            }
        },
        'enabled': False,
        'order': 4,
        'info': {
            'title': 'Vitamin Synthesis - B Vitamin and Vitamin K Producers',
            'description': 'Group bacteria capable of synthesizing essential vitamins (B vitamins, vitamin K) that are critical for hematopoiesis, immune function, and coagulation.',
            'algorithm': 'Taxa are grouped based on documented vitamin synthesis capabilities. B vitamin producers include Bifidobacterium, Lactobacillus, Enterococcus, certain Clostridia. Vitamin K producers include Bacteroides, Enterococcus, certain Escherichia coli. Folate producers include Bifidobacterium, Lactobacillus, certain Lactobacilli.',
            'parameters': [
                {'name': 'Include B vitamin producers', 'default': 'Include', 'description': 'Whether to include taxa producing various B vitamins'},
                {'name': 'Include vitamin K producers', 'default': 'Include', 'description': 'Whether to include taxa producing vitamin K'},
                {'name': 'Include folate producers', 'default': 'Include', 'description': 'Whether to include taxa producing folate'}
            ],
            'pros': [
                'MM treatment relevance - Chemotherapy depletes vitamins, causes deficiencies',
                'Hematopoiesis support - Essential for blood cell production post-transplant',
                'Immune function - Vitamins critical for immune cell proliferation',
                'Clinical monitoring - Vitamin deficiencies are measurable biomarkers',
                'Nutritional supplementation - Direct therapeutic implications'
            ],
            'cons': [
                'Dietary confounding - Vitamin intake affects microbial production',
                'Host absorption - Microbial production doesn\'t guarantee bioavailability',
                'Functional redundancy - Multiple sources of same vitamins',
                'Measurement complexity - Requires vitamin level measurements for validation'
            ],
            'limitations': [
                'Effects depend on dietary vitamin intake',
                'Microbial production may not compensate for treatment-induced deficiencies',
                'Strain-specific variations in vitamin production capacity'
            ],
            'expectations': 'Groups 15-30 taxa involved in vitamin biosynthesis pathways'
        }
    },

    'bile_acid_metabolism': {
        'name': 'Bile Acid Metabolism',
        'description': 'Group bacteria involved in bile acid transformation and secondary bile acid production',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Bile Acid Subgroups',
                'description': 'Primary to secondary converters: 7α-dehydroxylating bacteria (Clostridium, Eubacterium). Bile acid deconjugators: certain Bacteroides, Lactobacillus, Bifidobacterium. Hydroxylation modifiers: various gut anaerobes.'
            }
        },
        'enabled': False,
        'order': 5,
        'info': {
            'title': 'Bile Acid Metabolism - Bile Acid Transforming Bacteria',
            'description': 'Group bacteria involved in bile acid deconjugation, dehydroxylation, and secondary bile acid production that influence lipid metabolism and inflammation.',
            'algorithm': 'Taxa are grouped based on bile acid transformation capabilities. Primary to secondary converters include 7α-dehydroxylating bacteria (Clostridium, Eubacterium). Bile acid deconjugators include certain Bacteroides, Lactobacillus, Bifidobacterium. Hydroxylation modifiers include various gut anaerobes.',
            'parameters': [
                {'name': 'Include primary to secondary converters', 'default': 'Include', 'description': 'Whether to include taxa that convert primary to secondary bile acids'},
                {'name': 'Include bile acid deconjugators', 'default': 'Include', 'description': 'Whether to include taxa that deconjugate bile acids'},
                {'name': 'Include hydroxylation modifiers', 'default': 'Include', 'description': 'Whether to include taxa that modify bile acid hydroxylation'}
            ],
            'pros': [
                'Metabolic relevance - Bile acids regulate lipid metabolism and inflammation',
                'FXR signaling - Bile acid receptors influence immune and metabolic homeostasis',
                'Gut barrier effects - Secondary bile acids modulate epithelial integrity',
                'Drug metabolism - May influence chemotherapy pharmacokinetics',
                'Metabolic syndrome link - Relevant to MM-associated metabolic complications'
            ],
            'cons': [
                'Complex chemistry - Multiple bile acid transformation pathways',
                'Dietary influence - Bile acid composition affected by diet',
                'Measurement challenges - Requires bile acid profiling for validation',
                'Limited MM literature - Less studied than other functional groups'
            ],
            'limitations': [
                'Effects vary by bile acid pool composition',
                'Microbial transformations may be host-specific',
                'Requires specialized analytical chemistry for validation'
            ],
            'expectations': 'Groups 12-25 taxa involved in bile acid transformation'
        }
    },

    'mucin_degraders': {
        'name': 'Mucin Degraders',
        'description': 'Group bacteria capable of degrading mucin glycoproteins in the gut mucus layer',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Mucin Degrader Subgroups',
                'description': 'Primary mucin specialists: Akkermansia muciniphila. Mucin utilizers: certain Bacteroides, Prevotella, Ruminococcus. Mucus layer modifiers: various gut anaerobes affecting mucus thickness.'
            }
        },
        'enabled': False,
        'order': 6,
        'info': {
            'title': 'Mucin Degraders - Mucus Layer Degrading Bacteria',
            'description': 'Group bacteria capable of degrading mucin glycoproteins in the gut mucus layer, affecting gut barrier integrity and pathogen susceptibility.',
            'algorithm': 'Taxa are grouped based on mucin degradation capabilities. Primary mucin specialists include Akkermansia muciniphila. Mucin utilizers include certain Bacteroides, Prevotella, Ruminococcus. Mucus layer modifiers include various gut anaerobes affecting mucus thickness.',
            'parameters': [
                {'name': 'Include primary mucin specialists', 'default': 'Include', 'description': 'Whether to include dedicated mucin degraders like Akkermansia'},
                {'name': 'Include mucin utilizers', 'default': 'Include', 'description': 'Whether to include taxa that utilize mucin as carbon source'},
                {'name': 'Include mucus layer modifiers', 'default': 'Include', 'description': 'Whether to include taxa affecting mucus layer properties'}
            ],
            'pros': [
                'Barrier function focus - Critical for preventing bacterial translocation',
                'Transplant relevance - Gut barrier integrity affects infection risk',
                'Inflammation link - Mucus breach can trigger chronic inflammation',
                'Pathogen protection - Intact mucus layer prevents pathogen adherence',
                'Therapeutic potential - Mucus restoration strategies exist'
            ],
            'cons': [
                'Ecological complexity - Mucus degradation has both positive and negative effects',
                'Measurement difficulty - Mucus layer thickness hard to quantify',
                'Context dependence - Effects vary by microbial community composition',
                'Limited MM studies - Less research than other functional groups'
            ],
            'limitations': [
                'Akkermansia overgrowth or depletion both potentially problematic',
                'Effects depend on overall microbial community balance',
                'Requires mucosal biopsy or advanced imaging for validation'
            ],
            'expectations': 'Groups 10-20 taxa involved in mucus layer interactions'
        }
    },

    'antibiotic_resistance_carriers': {
        'name': 'Antibiotic Resistance Carriers',
        'description': 'Group bacteria carrying antibiotic resistance genes or exhibiting resistance phenotypes',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Antibiotic Resistance Subgroups',
                'description': 'Intrinsic resistance: Enterococcus, Pseudomonas. Acquired resistance: mobile genetic elements. Multi-drug resistance: bacteria resistant to multiple classes.'
            }
        },
        'enabled': False,
        'order': 7,
        'info': {
            'title': 'Antibiotic Resistance Carriers - Resistant Bacteria Groups',
            'description': 'Group bacteria carrying antibiotic resistance genes or exhibiting resistance phenotypes that could complicate infections or influence treatment outcomes.',
            'algorithm': 'Taxa are grouped based on documented antibiotic resistance. Intrinsic resistance includes naturally resistant species (Enterococcus, Pseudomonas). Acquired resistance includes mobile genetic elements. Multi-drug resistance includes bacteria resistant to multiple classes.',
            'parameters': [
                {'name': 'Include intrinsic resistance', 'default': 'Include', 'description': 'Whether to include naturally resistant species'},
                {'name': 'Include acquired resistance', 'default': 'Include', 'description': 'Whether to include taxa with acquired resistance genes'},
                {'name': 'Include multi-drug resistance', 'default': 'Include', 'description': 'Whether to include multi-resistant bacteria'}
            ],
            'pros': [
                'Clinical urgency - Resistant infections are major transplant complications',
                'Treatment monitoring - Track resistance development during therapy',
                'Preventive medicine - Identify resistance risks before infections occur',
                'Antibiotic stewardship - Guide rational antibiotic use',
                'Long-term outcomes - Resistance affects overall survival and quality of life'
            ],
            'cons': [
                'Genetic complexity - Resistance mechanisms vary widely',
                'Detection challenges - Resistance may be present but not expressed',
                'Dynamic nature - Resistance can be gained or lost rapidly',
                'Limited by sequencing - Shotgun metagenomics needed for gene-level analysis'
            ],
            'limitations': [
                'Requires specialized bioinformatics for resistance gene identification',
                'Resistance may not predict clinical infection outcomes',
                'Effects depend on antibiotic exposure history'
            ],
            'expectations': 'Groups 15-35 taxa with known antibiotic resistance characteristics'
        }
    },

    'disease_associated_microbiome': {
        'name': 'Disease-Associated Microbiome Patterns',
        'description': 'Group bacteria associated with other diseases that may share mechanisms with Multiple Myeloma',
        'parameters': {
            'subgroups': {
                'type': 'static',
                'label': 'Disease-Associated Subgroups',
                'description': 'Autoimmune-associated: bacteria linked to rheumatoid arthritis, IBD. Metabolic syndrome: bacteria associated with insulin resistance, obesity. Cardiovascular: TMAO producers, bile acid metabolizers. Cancer-associated: Fusobacterium, certain Streptococcus.'
            }
        },
        'enabled': False,
        'order': 8,
        'info': {
            'title': 'Disease-Associated Microbiome Patterns',
            'description': 'Group bacteria associated with other diseases or conditions that may share mechanisms with Multiple Myeloma (inflammation, immune dysregulation, metabolic syndrome).',
            'algorithm': 'Taxa are grouped based on associations with other diseases. Autoimmune-associated includes bacteria linked to rheumatoid arthritis, IBD. Metabolic syndrome includes bacteria associated with insulin resistance, obesity. Cardiovascular includes TMAO producers, bile acid metabolizers. Cancer-associated includes Fusobacterium, certain Streptococcus.',
            'parameters': [
                {'name': 'Include autoimmune-associated', 'default': 'Include', 'description': 'Whether to include taxa associated with autoimmune diseases'},
                {'name': 'Include metabolic syndrome', 'default': 'Include', 'description': 'Whether to include taxa associated with metabolic disorders'},
                {'name': 'Include cardiovascular disease', 'default': 'Include', 'description': 'Whether to include taxa associated with heart disease'},
                {'name': 'Include cancer-associated', 'default': 'Include', 'description': 'Whether to include taxa associated with various cancers'}
            ],
            'pros': [
                'Mechanistic insights - Shared pathways between MM and other diseases',
                'Comorbidity understanding - MM patients often have multiple health issues',
                'Biomarker discovery - Disease-associated bacteria may predict MM outcomes',
                'Comparative biology - Learn from other disease microbiome research',
                'Preventive opportunities - Early intervention for disease-associated dysbiosis'
            ],
            'cons': [
                'Disease specificity - Associations may not translate directly to MM',
                'Context dependence - Effects vary by disease stage and treatment',
                'Limited MM validation - Most associations come from other diseases',
                'Multiple testing issues - Many associations may be spurious'
            ],
            'limitations': [
                'Requires careful validation in MM-specific context',
                'Associations may be correlative rather than causal',
                'Disease heterogeneity affects microbiome patterns'
            ],
            'expectations': 'Groups 40-80 taxa associated with various disease states'
        }
    }
}

# # Default settings for quick start
# DEFAULT_MICROBIAL_GROUPING_SETTINGS = {
#     'scfa_producers': {
#         'enabled': True,
#         'include_butyrate_producers': True,
#         'include_propionate_producers': True,
#         'include_acetate_producers': True
#     }
# }