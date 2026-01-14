# 01_DataCuration.md: Data Curation and Preprocessing Methods

This document presents **data curation and preprocessing methods** for preparing raw microbiome and clinical data for downstream analysis in Multiple Myeloma research.

---

## 🎯 Phase 1 Overview

**Goal:** Transform raw sequencing data and clinical metadata into clean, analysis-ready datasets that meet quality standards and are appropriate for microbiome statistical analysis.

**Why First:** Poor data quality leads to unreliable results. Data curation ensures all subsequent analyses are built on a solid foundation.

---

## 📊 Data Curation Methods

### **1. Raw Data Import and Format Standardization**
**Description:** Load raw microbiome sequencing data and clinical metadata, standardizing formats for consistent processing.

**Supported Input Formats:**
- **Microbiome Data:** BIOM, QIIME2 artifacts, CSV/TSV count tables, FASTQ (for reprocessing)
- **Taxonomy Data:** QIIME2 taxonomy files, SILVA/Greengenes assignments, custom taxonomy tables
- **Clinical Data:** CSV, Excel, REDCap exports, electronic health records

**Algorithm:**
```python
# Load microbiome data
if format == 'biom':
    biom_table = biom.load_table('data.biom')
    otu_table = biom_table.to_dataframe()
elif format == 'qiime2':
    artifact = qiime2.Artifact.load('feature-table.qza')
    otu_table = artifact.view(pd.DataFrame)

# Load clinical data
clinical_data = pd.read_csv('clinical_metadata.csv')

# Standardize column names and data types
otu_table.columns = otu_table.columns.astype(str)  # Ensure sample IDs are strings
clinical_data['patient_id'] = clinical_data['patient_id'].astype(str)
```

**Pros:**
- ✅ **Format flexibility** - Handles diverse input data types
- ✅ **Data integrity** - Preserves original data during conversion
- ✅ **Metadata linkage** - Ensures microbiome and clinical data can be matched
- ✅ **Reproducibility** - Documented import procedures

**Cons:**
- ❌ **Format dependencies** - Requires specific libraries for different formats
- ❌ **File size issues** - Large BIOM files may require significant memory
- ❌ **Version compatibility** - Different software versions may produce incompatible formats

**Limitations:**
- Cannot handle corrupted or improperly formatted files
- May require manual intervention for complex custom formats
- Limited support for proprietary formats

**Why Choose:** Essential first step for any microbiome analysis workflow.

**Expected Results:** Standardized DataFrames ready for quality control and filtering

---

### **2. Sample Metadata Curation**
**Description:** Clean and validate clinical metadata, ensuring completeness and consistency for PFS analysis.

**Key Operations:**
- **Missing data handling:** Identify and impute/fill missing values
- **Data type validation:** Ensure dates, numbers, categories are correct
- **Value range checks:** Validate clinical values are within expected ranges
- **Duplicate detection:** Remove duplicate patient records
- **Cross-validation:** Check consistency between related variables

**Algorithm:**
```python
def curate_metadata(metadata_df):
    # Handle missing values
    metadata_df = impute_missing_values(metadata_df)

    # Validate data types
    metadata_df = validate_data_types(metadata_df)

    # Check value ranges
    metadata_df = validate_value_ranges(metadata_df)

    # Remove duplicates
    metadata_df = remove_duplicates(metadata_df)

    return metadata_df

# Specific PFS validation
def validate_pfs_data(metadata_df):
    # Ensure PFS duration > 0
    valid_pfs = metadata_df['pfs_days'] > 0

    # Ensure event indicator is 0 or 1
    valid_events = metadata_df['pfs_event'].isin([0, 1])

    # Check for reasonable PFS ranges (e.g., 30-3650 days)
    valid_range = (metadata_df['pfs_days'] >= 30) & (metadata_df['pfs_days'] <= 3650)

    return metadata_df[valid_pfs & valid_events & valid_range]
```

**Pros:**
- ✅ **Data quality assurance** - Identifies errors before analysis
- ✅ **PFS validation** - Ensures survival data integrity
- ✅ **Integration readiness** - Prepares data for microbiome-clinical merging
- ✅ **Audit trail** - Documents all curation decisions

**Cons:**
- ❌ **Subjective decisions** - How to handle missing data is researcher-dependent
- ❌ **Domain knowledge required** - Understanding clinical variable meanings
- ❌ **Time-intensive** - Manual review often needed for complex cases
- ❌ **Documentation burden** - Need to record all curation steps

**Limitations:**
- Cannot detect all data quality issues automatically
- May require clinical expert input for complex cases
- Some curation decisions are irreversible

**Why Choose:** Critical for ensuring reliable clinical correlations and PFS modeling.

**Expected Results:** Clean, validated clinical metadata with complete PFS information

---

### **3. Microbiome Data Quality Control**
**Description:** Assess and improve microbiome data quality through technical and biological validation.

**Quality Metrics:**
- **Library size distribution:** Check sequencing depth consistency
- **Rarefaction analysis:** Assess sampling completeness
- **Contamination screening:** Remove potential contaminant sequences
- **Technical replicate correlation:** Assess technical reproducibility

**Algorithm:**
```python
def quality_control_microbiome(otu_table):
    # Library size analysis
    library_sizes = otu_table.sum(axis=0)
    plt.hist(library_sizes, bins=50)
    plt.title('Library Size Distribution')
    plt.show()

    # Identify low-quality samples
    min_library_size = np.percentile(library_sizes, 10)  # Bottom 10%
    low_quality_samples = library_sizes < min_library_size

    # Rarefaction curves
    rarefaction_curves = []
    for sample in otu_table.columns[:10]:  # Sample of samples
        curve = calculate_rarefaction_curve(otu_table[sample])
        rarefaction_curves.append(curve)

    # Remove contaminants (if reference available)
    if contaminant_reference:
        otu_table = remove_contaminants(otu_table, contaminant_reference)

    return otu_table[~low_quality_samples]
```

**Pros:**
- ✅ **Technical validation** - Ensures sequencing quality and consistency
- ✅ **Biological relevance** - Removes contaminants and artifacts
- ✅ **Statistical readiness** - Prepares data for normalization and analysis
- ✅ **Reproducibility assessment** - Quantifies technical variation

**Cons:**
- ❌ **Parameter dependence** - Thresholds for quality metrics are subjective
- ❌ **Computational cost** - Rarefaction and contamination screening intensive
- ❌ **False positives** - May remove valid low-abundance taxa
- ❌ **Method variability** - Different QC approaches give different results

**Limitations:**
- Cannot detect all sources of technical variation
- Rarefaction assumes infinite sampling (not realistic)
- Contaminant databases may be incomplete

**Why Choose:** Essential for ensuring microbiome data reliability and statistical validity.

**Expected Results:** High-quality microbiome data with documented quality metrics

---

### **4. Sample Matching and Integration**
**Description:** Link microbiome samples with clinical metadata, ensuring proper sample-to-patient correspondence.

**Key Challenges:**
- **ID mismatches:** Different naming conventions between datasets
- **Missing samples:** Some patients may lack microbiome or clinical data
- **Time point alignment:** Match samples to correct clinical time points
- **Batch effects:** Account for technical differences between runs

**Algorithm:**
```python
def match_samples(microbiome_data, clinical_data):
    # Standardize sample IDs
    microbiome_ids = standardize_sample_ids(microbiome_data.columns)
    clinical_ids = standardize_sample_ids(clinical_data['sample_id'])

    # Find matches
    matched_ids = set(microbiome_ids) & set(clinical_ids)

    # Handle unmatched samples
    unmatched_microbiome = set(microbiome_ids) - matched_ids
    unmatched_clinical = set(clinical_ids) - matched_ids

    # Create integrated dataset
    matched_microbiome = microbiome_data[matched_ids]
    matched_clinical = clinical_data[clinical_data['sample_id'].isin(matched_ids)]

    return matched_microbiome, matched_clinical, unmatched_microbiome, unmatched_clinical

# Time point alignment for longitudinal studies
def align_timepoints(microbiome_data, clinical_data, time_tolerance=7):  # 7 days
    aligned_pairs = []

    for clinical_sample in clinical_data.iterrows():
        clinical_time = clinical_sample['collection_date']

        # Find microbiome samples within time window
        time_diffs = abs(microbiome_dates - clinical_time)
        closest_idx = np.argmin(time_diffs)

        if time_diffs[closest_idx] <= time_tolerance:
            aligned_pairs.append((clinical_sample.name, microbiome_samples[closest_idx]))

    return aligned_pairs
```

**Pros:**
- ✅ **Data integration** - Combines microbiome and clinical information
- ✅ **Sample integrity** - Ensures correct patient-sample linkages
- ✅ **Longitudinal alignment** - Proper time point matching for repeated measures
- ✅ **Batch tracking** - Documents technical variables for confounding control

**Cons:**
- ❌ **ID complexity** - Sample naming conventions vary widely
- ❌ **Missing data issues** - Not all patients have complete data
- ❌ **Time alignment challenges** - Exact timing rarely matches perfectly
- ❌ **Manual intervention** - Complex cases require human review

**Limitations:**
- Cannot resolve ambiguous sample IDs automatically
- May lose samples due to incomplete matching
- Time alignment assumes collection dates are accurate
- Batch effect correction requires additional statistical methods

**Why Choose:** Fundamental for ensuring microbiome-clinical associations are valid.

**Expected Results:** Integrated dataset with matched microbiome and clinical samples

---

### **5. Abundance Normalization and Transformation**
**Description:** Transform raw counts to appropriate scales for statistical analysis, addressing microbiome data characteristics.

**Normalization Methods:**
- **Relative abundance:** Convert to percentages (compositional data issue)
- **Centered log-ratio (CLR):** Accounts for compositionality
- **Total sum scaling (TSS):** Simple relative abundance
- **Rarefaction:** Subsample to equal library sizes

**Transformation Options:**
- **Log transformation:** Stabilize variance for parametric methods
- **Square root:** For count data with variance-mean relationship
- **Presence/absence:** For prevalence-based analyses

**Algorithm:**
```python
def normalize_microbiome_data(otu_table, method='clr'):
    if method == 'relative':
        # Convert to relative abundance
        normalized = otu_table.div(otu_table.sum(axis=0), axis=1) * 100

    elif method == 'clr':
        # Centered log-ratio transformation
        from skbio.stats.composition import clr
        # Add pseudocount for zeros
        otu_table_pseudo = otu_table + 1
        normalized = pd.DataFrame(
            clr(otu_table_pseudo.values.T).T,
            index=otu_table.index,
            columns=otu_table.columns
        )

    elif method == 'tss':
        # Total sum scaling
        normalized = otu_table.div(otu_table.sum(axis=0), axis=1)

    elif method == 'rarefaction':
        # Subsample to minimum library size
        min_size = otu_table.sum(axis=0).min()
        normalized = rarefy_counts(otu_table, min_size)

    # Apply transformation
    if transform == 'log':
        normalized = np.log(normalized + 1)
    elif transform == 'sqrt':
        normalized = np.sqrt(normalized)

    return normalized
```

**Pros:**
- ✅ **Statistical appropriateness** - Addresses microbiome data characteristics
- ✅ **Method compatibility** - Prepares data for different analysis approaches
- ✅ **Variance stabilization** - Improves performance of parametric methods
- ✅ **Interpretability** - Clear units and scales for results

**Cons:**
- ❌ **Method dependence** - Different methods give different results
- ❌ **Zero handling** - CLR and log transforms require pseudocounts
- ❌ **Compositionality issues** - Relative abundance loses total biomass information
- ❌ **Biological interpretation** - Transformed scales may be harder to interpret

**Limitations:**
- No single "correct" normalization method exists
- Rarefaction can be statistically inefficient
- Transformations may not be appropriate for all taxa
- Results can vary significantly by method choice

**Why Choose:** Essential for ensuring statistical analyses are appropriate for microbiome data characteristics.

**Expected Results:** Normalized abundance matrix ready for downstream analysis

---

### **6. Data Splitting and Cross-Validation Setup**
**Description:** Divide data into training/validation/test sets for robust model evaluation and prevent overfitting.

**Splitting Strategies:**
- **Random split:** Simple train/test division
- **Stratified split:** Maintain class proportions (for PFS events)
- **Time-based split:** Train on early data, test on later data
- **Patient-based split:** Ensure all samples from a patient in same set

**Algorithm:**
```python
def create_data_splits(microbiome_data, clinical_data, method='stratified'):
    # Combine data
    full_data = microbiome_data.T.join(clinical_data.set_index('sample_id'))

    if method == 'random':
        # Simple random split
        train_data, test_data = train_test_split(full_data, test_size=0.2, random_state=42)

    elif method == 'stratified':
        # Maintain PFS event proportions
        train_data, test_data = train_test_split(
            full_data,
            test_size=0.2,
            stratify=full_data['pfs_event'],
            random_state=42
        )

    elif method == 'patient_based':
        # Split by patients, not samples
        patients = clinical_data['patient_id'].unique()
        train_patients, test_patients = train_test_split(patients, test_size=0.2, random_state=42)

        train_mask = clinical_data['patient_id'].isin(train_patients)
        test_mask = clinical_data['patient_id'].isin(test_patients)

        train_data = full_data[train_mask]
        test_data = full_data[test_mask]

    elif method == 'time_based':
        # Train on early data, test on recent data
        cutoff_date = pd.to_datetime('2022-01-01')  # Example cutoff
        train_data = full_data[full_data['collection_date'] < cutoff_date]
        test_data = full_data[full_data['collection_date'] >= cutoff_date]

    return train_data, test_data
```

**Pros:**
- ✅ **Overfitting prevention** - Separate data for training and evaluation
- ✅ **Model validation** - Assess performance on unseen data
- ✅ **Generalizability assessment** - Test robustness across different data subsets
- ✅ **Reproducibility** - Consistent splits for method comparison

**Cons:**
- ❌ **Sample size reduction** - Smaller training sets may reduce power
- ❌ **Split dependence** - Results can vary with different random splits
- ❌ **Temporal bias** - Time-based splits may not reflect future data
- ❌ **Patient confounding** - Related samples may leak information

**Limitations:**
- No split strategy eliminates all potential biases
- Small datasets limit split proportions
- Patient-based splits reduce effective sample size
- Cross-validation requires sufficient data for meaningful folds

**Why Choose:** Critical for ensuring model performance estimates are realistic and preventing overfitting.

**Expected Results:** Properly partitioned datasets for training, validation, and testing

---

### **7. Data Export and Documentation**
**Description:** Save curated datasets in standard formats with comprehensive metadata for reproducibility and sharing.

**Export Formats:**
- **Analysis-ready:** Pickled Python objects, HDF5, Feather
- **Universal:** CSV, TSV for broad compatibility
- **Microbiome-specific:** BIOM format with metadata
- **Publication:** Excel files for reviewers

**Documentation Requirements:**
- **Processing steps:** Complete audit trail of curation decisions
- **Quality metrics:** Summary statistics and quality control results
- **Parameter choices:** Justification for normalization and filtering choices
- **Version control:** Track dataset versions and changes

**Algorithm:**
```python
def export_curated_data(microbiome_data, clinical_data, output_dir):
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Export microbiome data
    microbiome_data.to_csv(f'{output_dir}/microbiome_curated.csv')
    microbiome_data.to_hdf(f'{output_dir}/microbiome_curated.h5', key='data')

    # Export clinical data
    clinical_data.to_csv(f'{output_dir}/clinical_curated.csv')

    # Create metadata file
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'n_samples': microbiome_data.shape[1],
        'n_taxa': microbiome_data.shape[0],
        'normalization_method': 'clr',
        'filtering_criteria': 'prevalence > 1%, abundance > 0.001%',
        'processing_steps': [
            'Raw data import',
            'Quality control',
            'Normalization (CLR)',
            'Sample matching',
            'Data splitting'
        ]
    }

    with open(f'{output_dir}/curation_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    # Create README
    readme_content = generate_readme(microbiome_data, clinical_data, metadata)
    with open(f'{output_dir}/README.md', 'w') as f:
        f.write(readme_content)
```

**Pros:**
- ✅ **Reproducibility** - Complete documentation of data processing
- ✅ **Sharing capability** - Standard formats for collaboration
- ✅ **Version tracking** - Clear record of data evolution
- ✅ **Future-proofing** - Data ready for re-analysis

**Cons:**
- ❌ **Storage requirements** - Multiple formats increase file sizes
- ❌ **Documentation effort** - Comprehensive metadata requires time
- ❌ **Format limitations** - Some information may not export cleanly
- ❌ **Update complexity** - Changes require re-export and re-documentation

**Limitations:**
- Cannot capture all processing nuances in metadata
- Some data transformations may not be reversible
- File format compatibility varies across systems
- Large datasets may require compression or chunking

**Why Choose:** Essential for scientific reproducibility and collaboration.

**Expected Results:** Complete data package with multiple formats and comprehensive documentation

---

## 🎯 Implementation Strategy

### **Recommended Curation Pipeline:**
```
Raw Data Import → Metadata Curation → Quality Control → Sample Matching → Normalization → Data Splitting → Export
    ↓                ↓                   ↓              ↓             ↓            ↓             ↓
Format             Clinical Data       Technical        Integration   Statistical   Validation   Documentation
Standardization    Validation         Validation       & Alignment    Preparation   Setup        & Sharing
```

### **Quality Control Checkpoints:**
- **After import:** Verify data integrity and format correctness
- **After curation:** Check clinical data completeness and PFS validity
- **After QC:** Assess microbiome data quality and technical metrics
- **After matching:** Validate sample-to-patient linkages and time alignment
- **After normalization:** Confirm data distributions are appropriate for analysis
- **Before export:** Final validation of integrated dataset

### **Automation vs Manual Decisions:**
- **Automated:** Format conversion, basic validation, normalization
- **Semi-automated:** Quality control thresholds, missing data imputation
- **Manual:** Complex clinical data issues, sample matching ambiguities

### **Scalability Considerations:**
- **Large datasets:** Process in chunks, use memory-efficient formats
- **Cloud processing:** Utilize scalable computing resources for big data
- **Incremental curation:** Build curation pipelines that can be rerun
- **Caching:** Save intermediate results to avoid recomputation

This data curation phase establishes the foundation for reliable, reproducible microbiome analysis by ensuring data quality, proper integration, and appropriate preparation for statistical modeling.