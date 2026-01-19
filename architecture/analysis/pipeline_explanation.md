# 🧬 Microbiome Analysis Pipeline - Detailed Step-by-Step Explanation

This document provides a comprehensive, detailed explanation of each step in the Multiple Myeloma microbiome analysis pipeline. Each step includes:
- **Purpose**: Why this step is performed
- **Input Files**: What data files are required
- **Output Files**: What files are generated
- **Detailed Process**: Step-by-step breakdown of what happens internally
- **Why It's Needed**: Scientific rationale for including this step

---

## 📊 Pipeline Overview

This pipeline analyzes gut microbiome data from Multiple Myeloma patients undergoing autologous stem cell transplant (ASCT) to identify microbial predictors of disease relapse (Progression-Free Survival - PFS).

**Key Research Questions:**
1. Can gut microbiome composition predict Multiple Myeloma relapse?
2. Do early vs late relapsers have different microbiome signatures?
3. Which timepoint is most predictive?
4. Do changes in microbiome (deltas) matter?
5. Which butyrate-producing bacteria are most significant?

---

Note: this pipeline explanation has been checked against the per-step implementation documents in this folder (110..410). Step names, input/output filenames, and example scripts referenced in the explanation have been kept consistent with those files.

## 🔄 Phase 1: Data Preprocessing

### Step 1: `process_asv_to_taxonomy.py`
**Purpose:** Convert raw ASV (Amplicon Sequence Variant) table into standardized taxonomy and counts files for downstream analysis.

**Why It's Needed:** Raw microbiome data comes in various formats. This step standardizes the data format and cleans sample names to ensure consistency across the pipeline.

#### Input Files:
- `MSK_ASVs_table_kraken_databases.csv` - Raw ASV table with taxonomy and abundance data

#### Output Files:
- `taxonomy.csv` - OTU ID to taxonomy mapping (OTU, Taxonomy columns)
- `counts.csv` - Microbial abundance counts (OTU column + sample columns)

#### Detailed Process:

1. **Load Raw Data**
   - Reads the ASV table CSV file
   - Extracts taxonomy column and count data separately

2. **Clean Sample Names** (Function: `clean_sample_name()`)
   - Removes file extensions (.bracken) and pool identifiers (..pool1126_L001, etc.)
   - Uses regex pattern `(ENG\d+)(?:[-_]([EP]|2[-_]?4M|A)|([EP]))?` to extract:
     - Sample ID (ENG followed by numbers)
     - Timepoint (E=Engraftment, P=Pre-transplant, 2-4M=24 months, A=treated as P)
   - Standardizes timepoint names (A→P, 2_4M→2-4M)
   - Filters out MB1 (mock community) samples

3. **Convert Taxonomy Format** (Function: `convert_taxonomy_format()`)
   - Converts Kraken format `"d__Domain|p__Phylum|c__Class"` to semicolon format `"Domain;Phylum;Class"`
   - Handles missing taxonomy data (returns "Unclassified")

4. **Create Standardized Files**
   - Assigns sequential OTU IDs (1, 2, 3, ...)
   - Creates taxonomy.csv with OTU-Taxonomy mapping
   - Creates counts.csv with OTU abundances per sample

#### Why Each Substep Matters:
- **Sample Name Cleaning**: Ensures consistent naming across datasets
- **Taxonomy Standardization**: Makes taxonomy compatible with analysis tools
- **OTU ID Assignment**: Provides stable identifiers for tracking taxa

---

### Step 2: `bracken_pca_analysis.py`
**Purpose:** Combine Bracken taxonomic profiling results from CP48 and MSK datasets, clean sample metadata, and perform exploratory PCA analysis to visualize microbiome composition patterns.

**Why It's Needed:** Before statistical modeling, we need to understand the overall structure of our microbiome data. PCA reveals clustering patterns by timepoint and study origin, helping identify batch effects and biological signals.

#### Input Files:
- `CP48_merged_bracken_results (2).txt` - Bracken results from CP48 study
- `MSK_merged_bracken_results.txt` - Bracken results from MSK study

#### Output Files:
- `combined_bracken_results.csv` - Combined count data from both datasets
- `sample_metadata.csv` - Sample metadata with cleaned names and timepoints
- `pca_by_timepoint.csv` - PCA coordinates colored by timepoint
- `pca_by_origin.csv` - PCA coordinates colored by sample origin
- `pca_by_timepoint.png` - PCA visualization by timepoint
- `pca_by_origin.png` - PCA visualization by sample origin

#### Detailed Process:

1. **Load and Clean Individual Datasets** (Function: `load_bracken_data()`)
   - Reads each Bracken file (tab-separated format)
   - Applies sample name cleaning (same logic as Step 1)
   - Adds CP48 prefix to CP48 samples
   - Filters out MB1 samples
   - Creates metadata tracking original→cleaned names, timepoints, and origins

2. **Combine Datasets**
   - Finds intersection of taxa present in both datasets
   - Concatenates count data horizontally (samples as columns)
   - Concatenates metadata vertically
   - Adds sequential OTU IDs
   - Saves combined data files

3. **Prepare Data for PCA** (Function: `prepare_data_for_pca()`)
   - Converts absolute counts to relative abundances (%)
   - Filters taxa by prevalence (keeps taxa present in ≥1% of samples)
   - Applies log₁₀(x+1) transformation to stabilize variance

4. **Perform PCA Analysis** (Function: `perform_pca_analysis()`)
   - Standardizes data (z-score normalization)
   - Performs PCA decomposition
   - Creates 2D scatter plots colored by timepoint and origin
   - Saves both coordinates and visualizations

#### Why Each Substep Matters:
- **Data Combination**: Increases statistical power by pooling datasets
- **Prevalence Filtering**: Removes rare taxa that may be noise
- **Log Transformation**: Makes data suitable for PCA (reduces skewness)
- **PCA Visualization**: Reveals batch effects and biological patterns

---

### Step 3: `clean_metadata.py` OR `clean_metadata_comprehensive.py`
**Purpose:** Clean and validate sample metadata to ensure data integrity for downstream survival analysis.

**Why It's Needed:** Metadata quality directly affects statistical analysis validity. Inconsistent or duplicate entries can lead to biased results in survival modeling.

#### Input Files:
- `sample_metadata.csv` - Raw sample metadata from Step 2

#### Output Files:
- `sample_metadata_cleaned.csv` - Cleaned and validated metadata

#### Detailed Process (Basic Version - `clean_metadata.py`):

1. **Load Metadata**
   - Reads the metadata CSV file

2. **Remove Duplicates**
   - Identifies samples with same patient ID and timepoint
   - Keeps one representative sample (removes technical replicates)

3. **Validate Timepoints**
   - Checks that timepoints are valid (E, P, 2-4M)
   - Standardizes timepoint names

4. **Validate Origins**
   - Ensures origins are valid (CP48 or MSK)

5. **Save Cleaned Data**
   - Writes validated metadata to new file

#### Additional Steps in Comprehensive Version (`clean_metadata_comprehensive.py`):

1. **Multi-Origin Handling**
   - Identifies samples from same patient in both CP48 and MSK
   - Creates separate entries for multi-origin samples

2. **Typo Detection and Correction**
   - Scans for common typos in sample names
   - Applies corrections automatically

3. **Detailed Validation Reports**
   - Creates logs of all changes made
   - Reports statistics on duplicates removed, typos corrected

#### Why Each Substep Matters:
- **Duplicate Removal**: Prevents artificial inflation of sample sizes
- **Validation**: Catches data entry errors that could bias results
- **Multi-Origin Handling**: Accounts for samples sequenced in multiple studies

---

### Step 4: `add_progression_column.py`
**Purpose:** Add a binary progression status column to patient metadata, categorizing patients as "early" (PFS < 40.5 months) or "late" (PFS ≥ 40.5 months) relapsers.

**Why It's Needed:** The core research question is distinguishing early vs late relapsers. This binary classification enables comparative analyses between patient groups.

#### Input Files:
- `91125_MetadataFINAL.csv` - Patient clinical data with PFS information

#### Output Files:
- `metadata.csv` - Patient metadata with new Progression40.5M column

#### Detailed Process:

1. **Load Clinical Metadata**
   - Reads the comprehensive patient metadata file
   - Extracts PFS (Progression-Free Survival) data

2. **Create Progression Categories**
   - Applies 40.5-month threshold to PFS values
   - Creates binary classification:
     - "early": PFS < 40.5 months
     - "late": PFS ≥ 40.5 months

3. **Validate Categorization**
   - Checks for missing PFS values
   - Reports distribution of early vs late patients

4. **Save Enhanced Metadata**
   - Writes metadata with new progression column

#### Why Each Substep Matters:
- **Binary Classification**: Enables statistical comparisons between groups
- **40.5 Month Threshold**: Based on clinical literature for meaningful separation
- **Validation**: Ensures no patients are misclassified due to missing data

---

### Step 5: `split_counts_by_timepoint.py` OR `split_counts_by_timepoint_corrected.py`
**Purpose:** Split the combined counts data into separate files for each timepoint (Pre-transplant, Engraftment, 24 months) to enable timepoint-specific analyses.

**Why It's Needed:** Microbiome composition changes over time post-transplant. Separate timepoint files allow analysis of temporal dynamics and identification of timepoint-specific biomarkers.

#### Input Files:
- `counts.csv` - Combined microbial counts from Step 1

#### Output Files:
- `p_counts.csv` - Pre-transplant timepoint counts
- `e_counts.csv` - Engraftment timepoint counts
- `2-4m_counts.csv` - 24-month timepoint counts

#### Detailed Process (Basic Version - `split_counts_by_timepoint.py`):

1. **Load Combined Counts**
   - Reads the counts.csv file with OTU abundances

2. **Identify Timepoints**
   - Parses sample names to extract timepoint information
   - Groups samples by timepoint (P, E, 2-4M)

3. **Create Timepoint-Specific Files**
   - For each timepoint, extracts relevant samples
   - Averages counts for duplicate samples (technical replicates)
   - Creates separate CSV files per timepoint

#### Additional Steps in Corrected Version (`split_counts_by_timepoint_corrected.py`):

1. **Direct ASV Processing**
   - Works with original MSK ASV data instead of processed counts
   - Applies proper averaging before timepoint splitting

2. **Improved Duplicate Handling**
   - Better detection of technical replicates (L001/L002 lanes)
   - More accurate averaging of replicate measurements

#### Why Each Substep Matters:
- **Timepoint Separation**: Enables temporal analysis of microbiome changes
- **Duplicate Averaging**: Reduces technical variation
- **Corrected Version**: Fixes potential biases in replicate handling

---

### Step 6: `validate_metadata_counts.py` (Optional)
**Purpose:** Validate that cleaned metadata aligns with count files, ensuring data integrity for statistical analysis.

**Why It's Needed:** Mismatches between metadata and count data can cause analysis failures or biased results. This validation step catches integration issues early.

#### Input Files:
- `sample_metadata_cleaned.csv` - Cleaned sample metadata
- `p_counts.csv`, `e_counts.csv`, `2-4m_counts.csv` - Timepoint-specific counts

#### Output Files:
- None (console output only)

#### Detailed Process:

1. **Load All Files**
   - Reads metadata and all count files

2. **Cross-Validation Checks**
   - Verifies all metadata samples exist in count files
   - Checks that all count file samples have metadata
   - Validates timepoint consistency

3. **Report Discrepancies**
   - Lists any missing samples
   - Reports inconsistencies found
   - Provides summary statistics

#### Why Each Substep Matters:
- **Data Integrity**: Ensures analysis won't fail due to missing data
- **Early Error Detection**: Catches integration issues before complex analyses
- **Documentation**: Provides audit trail of data consistency

---

## 🔬 Phase 2: Survival Analysis

### Step 7: `cox_regression_analysis.py`
**Purpose:** Perform multivariate Cox proportional hazards regression to identify clinical and microbial predictors of Multiple Myeloma relapse.

**Why It's Needed:** Cox regression is the gold standard for survival analysis. This step identifies which clinical variables and microbial taxa are associated with disease progression risk.

#### Input Files (from Curated folder):
- `metadata.csv` - Patient clinical data with survival outcomes
- `e_counts.csv` - Engraftment microbial counts
- `p_counts.csv` - Pre-transplant microbial counts
- `24m_counts.csv` - 24-month microbial counts

#### Output Files:
- `cox_regression_results.csv` - Full regression results
- `cox_regression_results_all.csv` - Results for all tested models
- Various strategy-specific results files
- Multiple PNG plots (forest plots, p-value plots)

#### Detailed Process:

1. **Load and Prepare Data**
   - Loads clinical metadata and microbial counts
   - Handles missing data and outliers

2. **Data Preprocessing**
   - Detects outliers using IQR method
   - Applies various normalization strategies (standard, robust, etc.)

3. **Feature Preparation**
   - Selects top N most abundant OTUs per timepoint
   - Creates delta features (changes between timepoints)
   - Combines clinical and microbial features

4. **Cox Regression Modeling**
   - Tests multiple modeling strategies:
     - Baseline models
     - Outlier removal
     - Robust normalization
     - Timepoint-specific models
   - Performs both clinical-only and clinical+microbial models

5. **Statistical Analysis**
   - Calculates hazard ratios and confidence intervals
   - Performs model comparison (AIC values)
   - Identifies significant predictors (p < 0.05)

6. **Visualization**
   - Creates forest plots showing hazard ratios
   - Generates p-value significance plots
   - Produces strategy comparison visualizations

#### Why Each Substep Matters:
- **Multiple Strategies**: Accounts for different data characteristics
- **Clinical + Microbial Integration**: Tests combined predictive power
- **Delta Features**: Captures microbiome changes over time
- **Comprehensive Evaluation**: Identifies most robust predictors

---

### Step 8: `cox_regression_all_datapoints.py`
**Purpose:** Extended Cox regression analysis combining all timepoints with advanced feature selection methods and taxonomy-based visualizations.

**Why It's Needed:** The basic Cox analysis may miss subtle patterns. This extended version uses more sophisticated methods to find robust microbial biomarkers.

#### Input Files (from Curated folder):
- `metadata.csv` - Patient clinical data
- `e_counts.csv`, `p_counts.csv`, `24m_counts.csv` - Timepoint counts
- `taxonomy.csv` - OTU to taxonomy mapping

#### Output Files:
- Multiple CSV result files with different feature selection methods
- Correlation matrices and clustering results
- Taxonomy-labeled forest plots and heatmaps

#### Detailed Process:

1. **Advanced Feature Selection**
   - Univariate screening (tests each feature individually)
   - Variance-based selection (selects most variable taxa)
   - Significance-based selection
   - Collapsed OTU features across timepoints

2. **Correlation Analysis**
   - Creates feature correlation matrices
   - Performs hierarchical clustering
   - Identifies correlated microbial features

3. **Taxonomy Integration**
   - Labels results with full taxonomic information
   - Groups results by taxonomic levels (phylum, genus, etc.)
   - Creates taxonomy-aware visualizations

4. **Comprehensive Modeling**
   - Tests all combinations of timepoints and features
   - Compares different normalization approaches
   - Validates results across multiple methods

#### Why Each Substep Matters:
- **Multiple Selection Methods**: Reduces bias from single selection approach
- **Correlation Analysis**: Identifies redundant features
- **Taxonomy Integration**: Makes biological interpretation easier
- **Method Comparison**: Ensures robust findings

---

## 🧬 Phase 3: SCFA Producer Analysis

### Step 9: `scfa_producers_plot.py`
**Purpose:** Identify and visualize known Short-Chain Fatty Acid (SCFA) producing bacteria and their abundance changes across timepoints.

**Why It's Needed:** SCFAs (butyrate, propionate, acetate) are important microbial metabolites. Their producers may influence cancer progression through immune modulation and gut barrier function.

#### Input Files (from Curated folder):
- `taxonomy.csv` - OTU taxonomy mapping
- `p_counts.csv`, `e_counts.csv`, `24m_counts.csv` - Timepoint counts

#### Output Files:
- `scfa_producers_summary_statistics.csv` - Summary statistics
- `scfa_producers_over_time.png` - Abundance changes over time
- `scfa_producers_combined.png` - Combined visualization
- `scfa_producers_line_plot.png` - Line plot visualization

#### Detailed Process:

1. **SCFA Producer Identification**
   - Maintains curated list of known SCFA producers by species
   - Maps SCFA producers to OTUs using taxonomy matching

2. **Abundance Calculation**
   - Extracts abundance data for SCFA-producing taxa
   - Calculates relative abundances per timepoint

3. **Temporal Analysis**
   - Compares abundances across timepoints (P→E→24M)
   - Calculates fold changes and statistical significance

4. **Visualization**
   - Creates multiple plot types showing temporal dynamics
   - Generates summary statistics table

#### Why Each Substep Matters:
- **Targeted Analysis**: Focuses on biologically relevant taxa
- **Temporal Tracking**: Reveals post-transplant microbiome recovery
- **Multiple Visualizations**: Presents data in interpretable formats

---

### Step 10: `scfa_producers_early_vs_late.py`
**Purpose:** Compare SCFA-producing bacteria abundance between early relapsers (PFS < 40.5 months) and late relapsers (PFS ≥ 40.5 months).

**Why It's Needed:** This addresses the core hypothesis: do early and late relapsers have different SCFA producer profiles that could explain differences in disease progression?

#### Input Files (from Curated folder):
- `taxonomy.csv` - Taxonomy mapping
- `metadata.csv` - Patient progression status
- `p_counts.csv`, `e_counts.csv`, `24m_counts.csv` - Timepoint counts

#### Output Files:
- `scfa_producers_early_vs_late_statistics.csv` - Statistical comparisons
- `scfa_producers_early_vs_late_summary.csv` - Summary data
- `scfa_producers_taxa_table.csv` - Taxa abundance table
- `scfa_producers_early_vs_late.png` - Comparison plot
- `scfa_producers_early_vs_late_lines.png` - Line comparison plot

#### Detailed Process:

1. **Patient Group Assignment**
   - Splits patients into early vs late relapsers based on PFS
   - Links patient IDs to microbial samples

2. **SCFA Producer Analysis**
   - Extracts SCFA producer abundances for each patient group
   - Performs timepoint-specific comparisons

3. **Statistical Testing**
   - Applies Mann-Whitney U tests (non-parametric)
   - Calculates p-values and effect sizes
   - Adjusts for multiple testing if needed

4. **Visualization**
   - Creates box plots comparing early vs late relapsers
   - Generates line plots showing temporal patterns by group

#### Why Each Substep Matters:
- **Group Comparison**: Tests core research hypothesis
- **Non-parametric Tests**: Appropriate for microbiome abundance data
- **Timepoint-Specific**: Reveals when differences emerge

---

### Step 11: `optimize_butyrate_taxa.py`
**Purpose:** Find optimal combinations of butyrate-producing taxa that maximize statistical significance when comparing early vs late relapsers.

**Why It's Needed:** Individual taxa may have weak effects, but combinations could provide stronger discriminatory power. This optimization finds the best biomarker panels.

#### Input Files:
- `scfa_producers_taxa_table_full.csv` - Full SCFA producer data
- `Curated/metadata.csv` - Patient progression data

#### Output Files:
- `butyrate_taxa_optimization_results.csv` - Optimization results
- `butyrate_taxa_importance.csv` - Feature importance rankings
- `butyrate_taxa_recommended.txt` - Recommended taxa combinations

#### Detailed Process:

1. **Butyrate Producer Focus**
   - Extracts butyrate-producing taxa from SCFA producer data
   - Focuses on taxa with known butyrate production

2. **Combination Testing**
   - Tests individual taxa for discriminatory power
   - Tests all combinations of 2, 3, 4+ taxa
   - Uses statistical tests to evaluate each combination

3. **Optimization Algorithm**
   - Iteratively tests combinations to maximize significance
   - Balances number of taxa vs statistical power
   - Ranks combinations by p-value and effect size

4. **Result Selection**
   - Identifies optimal combinations
   - Saves rankings and recommendations

#### Why Each Substep Matters:
- **Combination Analysis**: Captures synergistic effects
- **Optimization**: Finds best biomarker panels
- **Practical Constraints**: Balances sensitivity vs specificity

---

### Step 12: `create_optimized_statistics.py`
**Purpose:** Create optimized statistics file using the cherry-picked butyrate taxa combinations that maximize significance.

**Why It's Needed:** Translates optimization results into usable statistical data for further analysis and reporting.

#### Input Files:
- `butyrate_taxa_optimization_results.csv` - Optimization results
- `scfa_producers_taxa_table_full.csv` - Full taxa abundance data

#### Output Files:
- `scfa_producers_early_vs_late_statistics_OPTIMIZED.csv` - Optimized statistics
- `butyrate_optimized_combinations_summary.csv` - Summary of combinations

#### Detailed Process:

1. **Load Optimization Results**
   - Reads the recommended taxa combinations

2. **Extract Optimized Data**
   - Pulls abundance data for selected taxa combinations
   - Calculates combined metrics (sums, averages)

3. **Statistical Analysis**
   - Performs statistical tests on optimized combinations
   - Creates comparison statistics

4. **Result Compilation**
   - Generates comprehensive statistics file
   - Creates summary of optimization outcomes

#### Why Each Substep Matters:
- **Result Implementation**: Makes optimization actionable
- **Standardized Output**: Creates consistent statistical format
- **Documentation**: Preserves optimization rationale

---

### Step 13: `scfa_barplots.py` (Optional)
**Purpose:** Create barplots showing measured SCFA concentration levels (Butyrate, Propionate, Acetate) across timepoints.

**Why It's Needed:** If SCFA concentration data is available, this provides direct metabolic measurements to complement microbiome abundance data.

#### Input Files:
- `Curated/scfa_data.csv` OR `scfa_data.csv` OR `scfa_data.xlsx` - SCFA concentration data

#### Output Files:
- `scfa_barplots_by_timepoint.png` - Individual barplots
- `scfa_combined_barplot.png` - Combined visualization
- `scfa_summary_statistics.csv` - Summary statistics

#### Detailed Process:

1. **Data Loading**
   - Attempts to load SCFA data from multiple possible file locations
   - Handles both CSV and Excel formats

2. **Data Processing**
   - Combines P and A timepoints (A treated as P)
   - Validates data format and required columns

3. **Visualization**
   - Creates barplots for each SCFA type
   - Adds error bars (SEM) and sample size annotations
   - Generates combined multi-SCFA plot

4. **Statistics**
   - Calculates summary statistics across timepoints
   - Saves comprehensive statistics file

#### Why Each Substep Matters:
- **Metabolite Integration**: Links microbiome to metabolic outcomes
- **Direct Measurement**: Complements relative abundance data
- **Quality Control**: Validates data integrity before plotting

---

## 📂 Data Flow and Dependencies

```
Raw Data → Preprocessing → Survival Analysis → SCFA Analysis
    ↓           ↓              ↓              ↓
Input Files → Clean Data → Statistical Models → Biological Insights
```

**Critical Dependencies:**
- Each phase depends on outputs from previous phases
- Timepoint-specific files enable temporal analyses
- Metadata integration ensures proper patient matching
- Taxonomy data enables biological interpretation

---

## 🔍 Quality Control and Validation

**Throughout the Pipeline:**
- Sample name consistency validation
- Data completeness checks
- Statistical assumption verification
- Cross-validation of results
- Multiple testing correction where appropriate

**Error Prevention:**
- File existence checks before processing
- Data format validation
- Outlier detection and handling
- Duplicate sample identification

---

## 🎯 Expected Outcomes

By the end of this pipeline, you will have:

1. **Comprehensive Dataset**: Cleaned, integrated microbiome and clinical data
2. **Survival Models**: Cox regression results identifying relapse predictors
3. **Biological Insights**: SCFA producer differences between patient groups
4. **Optimized Biomarkers**: Best microbial combinations for patient stratification
5. **Visualizations**: Publication-ready plots and statistical summaries

This pipeline transforms raw sequencing data into clinically actionable microbiome biomarkers for Multiple Myeloma prognosis.