# Cluster Representative Selection Methods
# Different criteria for choosing the representative taxonomy from within a cluster
# Based on actual taxonomy.csv structure with 25,611 taxonomies

CLUSTER_REPRESENTATIVE_METHODS = {
    'variance_highest': {
        'name': 'Highest Variance',
        'description': 'Select the taxonomy with the highest variance across all patients',
        'method': 'variance',
        'direction': 'max',
        'explanation': 'Chooses the most variable taxonomy as representative, useful for identifying highly dynamic species'
    },
    'variance_lowest': {
        'name': 'Lowest Variance',
        'description': 'Select the taxonomy with the lowest variance across all patients',
        'method': 'variance',
        'direction': 'min',
        'explanation': 'Chooses the most stable taxonomy as representative, useful for identifying consistent species'
    },
    'abundance_highest': {
        'name': 'Highest Mean Abundance',
        'description': 'Select the taxonomy with the highest mean abundance across all patients',
        'method': 'abundance',
        'direction': 'max',
        'explanation': 'Chooses the most abundant taxonomy as representative, useful for identifying dominant species'
    },
    'abundance_lowest': {
        'name': 'Lowest Mean Abundance',
        'description': 'Select the taxonomy with the lowest mean abundance across all patients',
        'method': 'abundance',
        'direction': 'min',
        'explanation': 'Chooses the least abundant taxonomy as representative, useful for identifying rare species'
    },
    'prevalence_highest': {
        'name': 'Highest Prevalence',
        'description': 'Select the taxonomy present in the most patients',
        'method': 'prevalence',
        'direction': 'max',
        'explanation': 'Chooses the most widespread taxonomy as representative, useful for identifying common species'
    },
    'prevalence_lowest': {
        'name': 'Lowest Prevalence',
        'description': 'Select the taxonomy present in the fewest patients',
        'method': 'prevalence',
        'direction': 'min',
        'explanation': 'Chooses the least widespread taxonomy as representative, useful for identifying rare species'
    },
    'taxonomic_level_highest': {
        'name': 'Highest Taxonomic Level',
        'description': 'Select the taxonomy with the highest taxonomic level (most specific)',
        'method': 'taxonomic_level',
        'direction': 'max',
        'explanation': 'Chooses the most specific taxonomy as representative, useful for detailed analysis'
    },
    'taxonomic_level_lowest': {
        'name': 'Lowest Taxonomic Level',
        'description': 'Select the taxonomy with the lowest taxonomic level (most general)',
        'method': 'taxonomic_level',
        'direction': 'min',
        'explanation': 'Chooses the most general taxonomy as representative, useful for broad analysis'
    },
    'genus_priority': {
        'name': 'Genus Priority',
        'description': 'Select the taxonomy with the most well-known genus',
        'method': 'genus_priority',
        'direction': 'max',
        'explanation': 'Chooses taxonomy from the most clinically/biologically important genus'
    },
    'species_completeness': {
        'name': 'Species Completeness',
        'description': 'Select the taxonomy with complete species identification (not sp.)',
        'method': 'species_completeness',
        'direction': 'max',
        'explanation': 'Prefers taxonomies with complete species names over generic "sp." designations'
    },
    'clinical_importance': {
        'name': 'Clinical Importance',
        'description': 'Select the taxonomy with highest clinical importance score',
        'method': 'clinical_importance',
        'direction': 'max',
        'explanation': 'Chooses the most clinically relevant taxonomy as representative'
    },
    'pathogenicity_highest': {
        'name': 'Highest Pathogenicity',
        'description': 'Select the taxonomy with the highest pathogenicity score',
        'method': 'pathogenicity',
        'direction': 'max',
        'explanation': 'Chooses the most pathogenic taxonomy as representative, useful for disease analysis'
    },
    'pathogenicity_lowest': {
        'name': 'Lowest Pathogenicity',
        'description': 'Select the taxonomy with the lowest pathogenicity score',
        'method': 'pathogenicity',
        'direction': 'min',
        'explanation': 'Chooses the least pathogenic taxonomy as representative, useful for beneficial species analysis'
    },
    'research_popularity': {
        'name': 'Research Popularity',
        'description': 'Select the taxonomy with highest research popularity based on genus/species',
        'method': 'research_popularity',
        'direction': 'max',
        'explanation': 'Chooses the most researched taxonomy as representative, useful for well-studied species'
    },
    'alphabetical_first': {
        'name': 'Alphabetically First',
        'description': 'Select the taxonomy that comes first alphabetically by species name',
        'method': 'alphabetical',
        'direction': 'min',
        'explanation': 'Chooses the first taxonomy alphabetically for consistent ordering'
    },
    'alphabetical_last': {
        'name': 'Alphabetically Last',
        'description': 'Select the taxonomy that comes last alphabetically by species name',
        'method': 'alphabetical',
        'direction': 'max',
        'explanation': 'Chooses the last taxonomy alphabetically for consistent ordering'
    },
    'phylum_priority': {
        'name': 'Phylum Priority',
        'description': 'Select the taxonomy from the most important phylum',
        'method': 'phylum_priority',
        'direction': 'max',
        'explanation': 'Chooses taxonomy from the most clinically/biologically important phylum'
    },
    'class_priority': {
        'name': 'Class Priority',
        'description': 'Select the taxonomy from the most important class',
        'method': 'class_priority',
        'direction': 'max',
        'explanation': 'Chooses taxonomy from the most clinically/biologically important class'
    },
    'order_priority': {
        'name': 'Order Priority',
        'description': 'Select the taxonomy from the most important order',
        'method': 'order_priority',
        'direction': 'max',
        'explanation': 'Chooses taxonomy from the most clinically/biologically important order'
    },
    'family_priority': {
        'name': 'Family Priority',
        'description': 'Select the taxonomy from the most important family',
        'method': 'family_priority',
        'direction': 'max',
        'explanation': 'Chooses taxonomy from the most clinically/biologically important family'
    },
    'median_abundance': {
        'name': 'Median Abundance',
        'description': 'Select the taxonomy with the median abundance value',
        'method': 'abundance',
        'direction': 'median',
        'explanation': 'Chooses the taxonomy with median abundance as representative, useful for balanced analysis'
    },
    'mode_abundance': {
        'name': 'Mode Abundance',
        'description': 'Select the taxonomy with the most common abundance value',
        'method': 'abundance',
        'direction': 'mode',
        'explanation': 'Chooses the taxonomy with the most common abundance as representative, useful for typical analysis'
    },
    'random_selection': {
        'name': 'Random Selection',
        'description': 'Randomly select a taxonomy from the cluster',
        'method': 'random',
        'direction': 'random',
        'explanation': 'Randomly chooses a taxonomy as representative, useful for unbiased analysis'
    }
}

# Default representative selection method
DEFAULT_REPRESENTATIVE_METHOD = 'abundance_highest'

# Method categories for organization
METHOD_CATEGORIES = {
    'statistical': {
        'name': 'Statistical Methods',
        'description': 'Methods based on statistical measures',
        'methods': ['variance_highest', 'variance_lowest', 'abundance_highest', 'abundance_lowest', 
                   'prevalence_highest', 'prevalence_lowest', 'median_abundance', 'mode_abundance']
    },
    'taxonomic': {
        'name': 'Taxonomic Methods',
        'description': 'Methods based on taxonomic characteristics',
        'methods': ['taxonomic_level_highest', 'taxonomic_level_lowest', 'species_completeness',
                   'alphabetical_first', 'alphabetical_last']
    },
    'biological': {
        'name': 'Biological Methods',
        'description': 'Methods based on biological characteristics',
        'methods': ['pathogenicity_highest', 'pathogenicity_lowest', 'clinical_importance', 
                   'research_popularity', 'genus_priority']
    },
    'hierarchical': {
        'name': 'Hierarchical Methods',
        'description': 'Methods based on taxonomic hierarchy',
        'methods': ['phylum_priority', 'class_priority', 'order_priority', 'family_priority']
    },
    'utility': {
        'name': 'Utility Methods',
        'description': 'Methods for specific use cases',
        'methods': ['random_selection']
    }
}

# Scoring weights for composite methods
SCORING_WEIGHTS = {
    'abundance': 0.3,
    'prevalence': 0.2,
    'variance': 0.15,
    'clinical_importance': 0.15,
    'research_popularity': 0.1,
    'pathogenicity': 0.1
}

# Clinical importance scoring based on actual taxonomy data
CLINICAL_IMPORTANCE_SCORES = {
    # High clinical importance genera (score: 10)
    'high_importance': {
        'genera': ['Escherichia', 'Staphylococcus', 'Streptococcus', 'Clostridium', 
                  'Bacteroides', 'Prevotella', 'Lactobacillus', 'Bifidobacterium',
                  'Pseudomonas', 'Enterococcus', 'Klebsiella', 'Proteus',
                  'Salmonella', 'Listeria', 'Campylobacter', 'Helicobacter',
                  'Mycobacterium', 'Neisseria', 'Haemophilus', 'Vibrio'],
        'score': 10
    },
    # Medium clinical importance genera (score: 5)
    'medium_importance': {
        'genera': ['Bacillus', 'Corynebacterium', 'Propionibacterium', 'Fusobacterium',
                  'Veillonella', 'Porphyromonas', 'Tannerella', 'Treponema',
                  'Borrelia', 'Leptospira', 'Rickettsia', 'Chlamydia'],
        'score': 5
    },
    # Low clinical importance genera (score: 1)
    'low_importance': {
        'genera': ['Azorhizobium', 'Buchnera', 'Cellulomonas', 'Dictyoglomus',
                  'Methylophilus', 'Syntrophotalea', 'Shewanella', 'Myxococcus'],
        'score': 1
    }
}

# Pathogenicity scoring based on known pathogenic species
PATHOGENICITY_SCORES = {
    # High pathogenicity (score: 10)
    'high_pathogenic': {
        'species': ['Escherichia coli', 'Staphylococcus aureus', 'Streptococcus pyogenes',
                   'Clostridium botulinum', 'Clostridium perfringens', 'Clostridium tetani',
                   'Salmonella enterica', 'Listeria monocytogenes', 'Campylobacter jejuni',
                   'Helicobacter pylori', 'Mycobacterium tuberculosis', 'Neisseria meningitidis',
                   'Haemophilus influenzae', 'Vibrio cholerae', 'Bacillus anthracis'],
        'score': 10
    },
    # Medium pathogenicity (score: 5)
    'medium_pathogenic': {
        'species': ['Staphylococcus epidermidis', 'Streptococcus pneumoniae', 'Enterococcus faecalis',
                   'Klebsiella pneumoniae', 'Proteus mirabilis', 'Pseudomonas aeruginosa',
                   'Bacteroides fragilis', 'Prevotella intermedia', 'Fusobacterium nucleatum'],
        'score': 5
    },
    # Low pathogenicity (score: 1)
    'low_pathogenic': {
        'species': ['Lactobacillus acidophilus', 'Bifidobacterium bifidum', 'Propionibacterium acnes',
                   'Corynebacterium diphtheriae', 'Bacillus subtilis'],
        'score': 1
    },
    # Beneficial/commensal (score: -2)
    'beneficial': {
        'species': ['Lactobacillus casei', 'Lactobacillus rhamnosus', 'Bifidobacterium longum',
                   'Bifidobacterium infantis', 'Lactobacillus plantarum'],
        'score': -2
    }
}

# Research popularity scoring based on well-studied organisms
RESEARCH_POPULARITY_SCORES = {
    # Highly researched (score: 10)
    'high_research': {
        'genera': ['Escherichia', 'Staphylococcus', 'Streptococcus', 'Bacillus', 'Pseudomonas'],
        'score': 10
    },
    # Well researched (score: 7)
    'well_researched': {
        'genera': ['Clostridium', 'Lactobacillus', 'Bifidobacterium', 'Mycobacterium', 'Salmonella'],
        'score': 7
    },
    # Moderately researched (score: 4)
    'moderate_research': {
        'genera': ['Bacteroides', 'Prevotella', 'Enterococcus', 'Klebsiella', 'Proteus'],
        'score': 4
    },
    # Less researched (score: 1)
    'low_research': {
        'genera': ['Azorhizobium', 'Buchnera', 'Cellulomonas', 'Dictyoglomus', 'Methylophilus'],
        'score': 1
    }
}

# Taxonomic level scoring (based on completeness)
TAXONOMIC_LEVEL_SCORES = {
    'complete_species': 6,  # Full species name (e.g., "Escherichia coli")
    'genus_sp': 4,         # Genus with "sp." (e.g., "Pseudomonas sp.")
    'genus_only': 3,       # Only genus name
    'family_level': 2,     # Family level
    'order_level': 1,      # Order level
    'class_level': 0       # Class level or higher
}

# Validation rules for each method
VALIDATION_RULES = {
    'variance_highest': {
        'min_cluster_size': 2,
        'requires_numeric_data': True,
        'description': 'Requires at least 2 taxonomies and numeric abundance data'
    },
    'abundance_highest': {
        'min_cluster_size': 1,
        'requires_numeric_data': True,
        'description': 'Requires numeric abundance data'
    },
    'prevalence_highest': {
        'min_cluster_size': 1,
        'requires_numeric_data': False,
        'description': 'Works with presence/absence data'
    },
    'clinical_importance': {
        'min_cluster_size': 1,
        'requires_taxonomy_table': True,
        'description': 'Requires taxonomy table with genus and species information'
    },
    'pathogenicity_highest': {
        'min_cluster_size': 1,
        'requires_taxonomy_table': True,
        'description': 'Requires taxonomy table with species information'
    },
    'research_popularity': {
        'min_cluster_size': 1,
        'requires_taxonomy_table': True,
        'description': 'Requires taxonomy table with genus information'
    }
}

# Implementation helper functions
def get_taxonomic_level_score(taxonomy_row):
    """
    Calculate taxonomic level score based on taxonomy.csv structure
    """
    species = taxonomy_row.get('Species', '').strip()
    genus = taxonomy_row.get('Genus', '').strip()
    
    if species and species != 's__' and 'sp.' not in species:
        return TAXONOMIC_LEVEL_SCORES['complete_species']
    elif genus and 'sp.' in species:
        return TAXONOMIC_LEVEL_SCORES['genus_sp']
    elif genus:
        return TAXONOMIC_LEVEL_SCORES['genus_only']
    else:
        return TAXONOMIC_LEVEL_SCORES['class_level']

def get_clinical_importance_score(taxonomy_row):
    """
    Calculate clinical importance score based on genus
    """
    genus = taxonomy_row.get('Genus', '').strip()
    
    for category, data in CLINICAL_IMPORTANCE_SCORES.items():
        if genus in data['genera']:
            return data['score']
    
    return 0  # Unknown genus

def get_pathogenicity_score(taxonomy_row):
    """
    Calculate pathogenicity score based on species
    """
    species = taxonomy_row.get('Species', '').strip()
    
    for category, data in PATHOGENICITY_SCORES.items():
        if species in data['species']:
            return data['score']
    
    return 0  # Unknown species

def get_research_popularity_score(taxonomy_row):
    """
    Calculate research popularity score based on genus
    """
    genus = taxonomy_row.get('Genus', '').strip()
    
    for category, data in RESEARCH_POPULARITY_SCORES.items():
        if genus in data['genera']:
            return data['score']
    
    return 0  # Unknown genus

def is_species_complete(taxonomy_row):
    """
    Check if species name is complete (not "sp.")
    """
    species = taxonomy_row.get('Species', '').strip()
    return species and 'sp.' not in species and species != 's__'