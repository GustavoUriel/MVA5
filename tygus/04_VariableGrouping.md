# 04_VariableGrouping.md: Variable Grouping Methods

This document presents **variable grouping methods** to combine selected variables into biologically meaningful composite features, preserving information while reducing dimensionality for analysis.

---

## 🎯 Phase 3 Overview

**Goal:** Group the selected variables (10-50 taxa) into interpretable composite features (3-10 groups) that capture biological patterns while maintaining statistical power.

**Why After Variable Selection:** Start with high-quality, clinically relevant taxa, then organize them into functional or ecological units.

---

## 📊 Variable Grouping Methods

### **1. Functional Pathway Grouping**
**Description:** Group taxa by shared metabolic functions and biochemical pathways, creating pathway-level features.

**Algorithm:**
```python
pathway_definitions = {
    'Butyrate_Production': ['Faecalibacterium', 'Roseburia', 'Eubacterium'],
    'Acetate_Production': ['Bifidobacterium', 'Lactobacillus', 'Blautia'],
    'Immunomodulation': ['Bifidobacterium', 'Lactobacillus', 'Faecalibacterium'],
}

for pathway, taxa_list in pathway_definitions.items():
    # Aggregate taxa in the same pathway
    available_taxa = [t for t in taxa_list if t in selected_taxa]
    if available_taxa:
        pathway_abundance = microbiome_data[available_taxa].sum(axis=1)
        grouped_data[f'{pathway}_Pathway'] = pathway_abundance
```

**Pros:**
- ✅ **Biologically interpretable** - Groups represent known functional processes
- ✅ **Hypothesis-driven** - Based on established microbial physiology
- ✅ **Mechanistic clarity** - Directly links to biological pathways
- ✅ **Clinical translation** - Pathway activities have therapeutic implications
- ✅ **Literature support** - Well-established functional categorizations

**Cons:**
- ❌ **Knowledge dependence** - Requires comprehensive pathway databases
- ❌ **Functional overlap** - Some taxa participate in multiple pathways
- ❌ **Incomplete annotations** - Not all taxa have known functions
- ❌ **Strain variation** - Functions may vary by bacterial strain
- ❌ **Context dependence** - Pathway importance varies by physiological state

**Limitations:**
- Depends on quality of functional annotations
- May miss novel or uncharacterized functions
- Requires expertise in microbial metabolism

**Why Choose:** Creates biologically meaningful features that directly relate to clinical outcomes and therapeutic interventions.

**Expected Results:** 3-8 pathway-based composite features

---

### **2. Taxonomic Hierarchy Grouping**
**Description:** Group taxa by evolutionary relationships (genus, family, phylum), aggregating phylogenetically related microbes.

**Algorithm:**
```python
taxonomic_levels = ['genus', 'family', 'phylum']

for level in taxonomic_levels:
    taxonomic_groups = group_by_taxonomy(selected_taxa, level)

    for group_name, taxa_list in taxonomic_groups.items():
        if len(taxa_list) > 1:  # Only group if multiple taxa
            group_abundance = microbiome_data[taxa_list].mean(axis=1)  # or sum
            grouped_data[f'{group_name}_{level}'] = group_abundance
```

**Pros:**
- ✅ **Evolutionarily grounded** - Reflects phylogenetic relationships
- ✅ **Conservative aggregation** - Related taxa often share functional traits
- ✅ **Stable classifications** - Less affected by taxonomic reclassification
- ✅ **Scalable resolution** - Can analyze at different taxonomic levels
- ✅ **Ecological validity** - Captures evolutionary constraints on function

**Cons:**
- ❌ **Functional heterogeneity** - Related taxa may have different functions
- ❌ **Resolution trade-offs** - Genus level may be too specific, phylum too broad
- ❌ **Classification dependence** - Results depend on taxonomic assignment accuracy
- ❌ **Ecological oversimplification** - Ignores functional convergence across phylogeny
- ❌ **Information loss** - Aggregates functionally distinct taxa

**Limitations:**
- Optimal taxonomic level varies by research question
- Requires high-quality taxonomic classifications
- May obscure functional differences within taxonomic groups

**Why Choose:** Provides evolutionary context and stable groupings that are reproducible across studies.

**Expected Results:** 4-12 taxonomic composite features at chosen level

---

### **3. Correlation-Based Clustering + PCA Aggregation**
**Description:** Identify clusters of highly correlated taxa and create PCA-based composite features.

**Algorithm:**
```python
# Calculate correlation matrix
corr_matrix = microbiome_data[selected_taxa].corr()

# Find clusters using hierarchical clustering or graph methods
clusters = identify_correlation_clusters(corr_matrix, threshold=0.7)

# Create composite for each cluster
for cluster_taxa in clusters:
    if len(cluster_taxa) > 1:
        # Use first principal component as composite
        pca = PCA(n_components=1)
        composite = pca.fit_transform(microbiome_data[cluster_taxa])
        grouped_data[f'Cluster_{cluster_id}_PC1'] = composite.flatten()
```

**Pros:**
- ✅ **Data-driven discovery** - Reveals natural microbial associations
- ✅ **Ecologically meaningful** - Groups represent co-occurring microbial communities
- ✅ **Preserves relationships** - Maintains multivariate correlation structure
- ✅ **Reduces redundancy** - Handles multicollinear taxa effectively
- ✅ **Unsupervised insight** - Discovers novel community patterns

**Cons:**
- ❌ **Interpretability challenges** - Composite features are linear combinations
- ❌ **Parameter sensitivity** - Correlation threshold affects clustering
- ❌ **Biological ambiguity** - Clusters may not represent functional groups
- ❌ **Stability concerns** - Clustering results may vary with preprocessing
- ❌ **No biological context** - Lacks functional or evolutionary meaning

**Limitations:**
- Arbitrary correlation threshold selection
- May group taxa that correlate for technical rather than biological reasons
- Composite interpretation requires understanding cluster composition

**Why Choose:** Reveals data-driven microbial community structures that may not be evident from taxonomy or function alone.

**Expected Results:** 3-8 correlation-based composite features

---

### **4. Time-Series Trajectory Grouping**
**Description:** Group taxa showing similar abundance patterns over transplant timepoints, capturing temporal dynamics.

**Algorithm:**
```python
# Extract temporal trajectories for each taxon
timepoints = ['Pre_transplant', 'Engraftment', '6_months', '12_months']
trajectories = []

for taxon in selected_taxa:
    trajectory = [microbiome_data.loc[microbiome_data['timepoint'] == tp, taxon].mean()
                  for tp in timepoints]
    trajectories.append(trajectory)

# Cluster similar trajectories
trajectory_clusters = TimeSeriesKMeans(n_clusters=k).fit_predict(trajectories)

# Create trajectory-based composites
for cluster_id in range(k):
    cluster_taxa = [selected_taxa[i] for i in range(len(selected_taxa))
                   if trajectory_clusters[i] == cluster_id]

    # Average trajectories within cluster
    cluster_trajectory = microbiome_data[cluster_taxa + ['timepoint']].groupby('timepoint').mean()
    grouped_data[f'Trajectory_Cluster_{cluster_id}'] = cluster_trajectory.mean(axis=1)
```

**Pros:**
- ✅ **Temporal dynamics** - Captures transplant recovery patterns
- ✅ **Clinical trajectories** - Links microbial changes to treatment response
- ✅ **Longitudinal insight** - Reveals how microbial communities evolve
- ✅ **Personalized medicine** - Different trajectories may predict different outcomes
- ✅ **Intervention timing** - Identifies optimal windows for microbiome modulation

**Cons:**
- ❌ **Data requirements** - Needs multiple timepoints per patient
- ❌ **Trajectory complexity** - Time-series clustering is computationally intensive
- ❌ **Missing data issues** - Incomplete trajectories complicate analysis
- ❌ **Parameter selection** - Number of trajectory clusters affects results
- ❌ **Interpretation difficulty** - Trajectory clusters may be hard to characterize

**Limitations:**
- Requires longitudinal study design
- Sensitive to timing and frequency of measurements
- May not be applicable with only pre/post transplant data
- Trajectory patterns may be hard to biologically interpret

**Why Choose:** Captures the temporal dimension of microbiome changes during treatment and recovery.

**Expected Results:** 3-6 trajectory-based composite features

---

### **5. Co-occurrence Network Grouping**
**Description:** Model taxa as network nodes and group those forming densely connected communities.

**Algorithm:**
```python
# Estimate sparse inverse covariance (precision matrix)
glasso = GraphicalLassoCV()
precision_matrix = glasso.fit(microbiome_data[selected_taxa].T).precision_

# Create network and detect communities
correlation_network = abs(precision_matrix)  # Absolute partial correlations
communities = community.louvain_communities(correlation_network)

# Create community composites
for community_id, community_taxa in enumerate(communities):
    if len(community_taxa) > 1:
        # Aggregate community abundance
        community_abundance = microbiome_data[community_taxa].mean(axis=1)
        grouped_data[f'Network_Community_{community_id}'] = community_abundance
```

**Pros:**
- ✅ **Ecological realism** - Captures microbial interaction networks
- ✅ **Systems approach** - Models microbiome as interconnected ecosystem
- ✅ **Robust correlations** - Uses partial correlations controlling for indirect effects
- ✅ **Network science foundation** - Leverages graph theory for biological insight
- ✅ **Community stability** - Network communities often more robust than individual taxa

**Cons:**
- ❌ **Computational complexity** - Network construction and community detection
- ❌ **Parameter sensitivity** - Sparsity parameters affect network structure
- ❌ **Interpretability challenges** - Community meanings not always clear
- ❌ **Algorithm dependence** - Different community detection methods give different results
- ❌ **Scale dependence** - Network properties depend on data preprocessing

**Limitations:**
- Requires careful parameter selection for network construction
- Community detection algorithms may not be deterministic
- May be sensitive to microbiome data compositionality
- Computational cost increases with number of taxa

**Why Choose:** Provides sophisticated ecological insight into microbial community organization and interactions.

**Expected Results:** 3-7 network community composite features

---

### **6. Sparse Canonical Correlation Analysis (SCCA) Grouping**
**Description:** Find linear combinations of taxa that maximally correlate with clinical variables, grouping taxa by shared clinical associations.

**Algorithm:**
```python
# Prepare data
X_microbiome = microbiome_data[selected_taxa]
X_clinical = clinical_data[['age', 'ISS', 'treatment_duration']]

# Apply sparse CCA
cca = CCA(n_components=3)
X_c, Y_c = cca.fit_transform(X_microbiome, X_clinical)

# Group taxa by CCA loadings
for component in range(3):
    component_taxa = selected_taxa[abs(cca.x_loadings_[:, component]) > threshold]
    if len(component_taxa) > 1:
        component_abundance = X_microbiome[component_taxa].mean(axis=1)
        grouped_data[f'CCA_Component_{component}'] = component_abundance
```

**Pros:**
- ✅ **Clinical integration** - Links microbiome directly to clinical variables
- ✅ **Multimodal insight** - Reveals microbiome-clinical covariation patterns
- ✅ **Sparse solution** - Identifies key taxa-clinical relationships
- ✅ **Systems biology** - Considers microbiome-clinical interactions
- ✅ **Biomarker discovery** - Components may serve as composite biomarkers

**Cons:**
- ❌ **Complexity** - Requires optimization of sparsity parameters
- ❌ **Computational cost** - Iterative algorithms for sparse CCA
- ❌ **Interpretability issues** - Canonical variates are linear combinations
- ❌ **Parameter sensitivity** - Sparsity level affects which taxa are grouped
- ❌ **Clinical variable dependence** - Results depend on which clinical variables are included

**Limitations:**
- Requires both microbiome and clinical data for all samples
- Sensitive to scaling of different data types
- Sparsity parameter selection affects grouping results
- May find spurious correlations in high-dimensional data

**Why Choose:** Integrates microbiome and clinical data to create clinically meaningful composite features.

**Expected Results:** 2-5 CCA component composite features

---

### **7. Functional Redundancy Grouping**
**Description:** Group taxa that perform similar functions, creating redundancy-aware composite features.

**Algorithm:**
```python
# Define functional redundancy matrix
functional_similarity = calculate_functional_similarity(selected_taxa)

# Cluster functionally similar taxa
functional_clusters = hierarchical_clustering(functional_similarity, threshold=0.8)

# Create redundancy composites
for cluster_taxa in functional_clusters:
    if len(cluster_taxa) > 1:
        # Weight by abundance (dominant taxa contribute more)
        weights = microbiome_data[cluster_taxa].mean() / microbiome_data[cluster_taxa].mean().sum()
        redundancy_score = (microbiome_data[cluster_taxa] * weights).sum(axis=1)
        grouped_data[f'Functional_Redundancy_{cluster_id}'] = redundancy_score
```

**Pros:**
- ✅ **Ecological realism** - Accounts for functional redundancy in microbial communities
- ✅ **Stability enhancement** - Redundancy makes features more robust
- ✅ **Community resilience** - Captures ecosystem-level functional capacity
- ✅ **Biological insight** - Reveals which functions are buffered by redundancy
- ✅ **Predictive stability** - Redundant functions less affected by individual taxa variation

**Cons:**
- ❌ **Complexity** - Requires functional similarity calculations
- ❌ **Data dependence** - Needs comprehensive functional annotations
- ❌ **Assumption dependence** - Functional similarity metrics are approximations
- ❌ **Computational cost** - Similarity matrix calculations for many taxa
- ❌ **Over-aggregation risk** - May group functionally distinct taxa

**Limitations:**
- Depends on quality of functional similarity measures
- May not capture context-dependent functional differences
- Requires large datasets for reliable redundancy estimation
- Functional annotations may be incomplete

**Why Choose:** Accounts for ecological redundancy, creating more stable and ecologically meaningful features.

**Expected Results:** 3-7 redundancy-based composite features

---

### **8. Adaptive Resonance Theory (ART) Grouping**
**Description:** Use neural network-based clustering to adaptively group taxa based on similarity patterns.

**Algorithm:**
```python
# Initialize ART network
art_network = FuzzyART(alpha=0.5, rho=0.7)

# Train on taxon abundance patterns
scaled_data = StandardScaler().fit_transform(microbiome_data[selected_taxa])
art_network.train(scaled_data)

# Extract clusters
art_clusters = art_network.get_clusters()

# Create ART-based composites
for cluster_id, cluster_taxa in enumerate(art_clusters):
    if len(cluster_taxa) > 1:
        cluster_abundance = microbiome_data[cluster_taxa].mean(axis=1)
        grouped_data[f'ART_Cluster_{cluster_id}'] = cluster_abundance
```

**Pros:**
- ✅ **Adaptive clustering** - Learns optimal number of clusters automatically
- ✅ **Robust to noise** - Neural network approach handles data variability
- ✅ **Non-linear patterns** - Can detect complex similarity relationships
- ✅ **Stability** - Less sensitive to initialization than traditional clustering
- ✅ **Scalability** - Works well with different data sizes

**Cons:**
- ❌ **Parameter sensitivity** - Vigilance and learning rate affect results
- ❌ **Interpretability issues** - Neural network clusters may be hard to understand
- ❌ **Computational cost** - Training neural networks for clustering
- ❌ **Black box nature** - Limited insight into why clusters are formed
- ❌ **Over-clustering risk** - May create too many small clusters

**Limitations:**
- Requires parameter tuning for optimal performance
- Results may not be reproducible across different runs
- Harder to biologically interpret than other methods
- May be overkill for most microbiome datasets

**Why Choose:** Provides sophisticated, adaptive clustering for complex microbial community patterns.

**Expected Results:** 4-10 ART-based composite features

---

### **9. Consensus Grouping**
**Description:** Apply multiple grouping methods and create consensus composites from overlapping groups.

**Algorithm:**
```python
# Apply multiple grouping methods
functional_groups = apply_functional_grouping(selected_taxa)
taxonomic_groups = apply_taxonomic_grouping(selected_taxa)
correlation_groups = apply_correlation_clustering(selected_taxa)

# Find consensus groups (taxa appearing together in multiple methods)
consensus_groups = find_consensus_across_methods(
    [functional_groups, taxonomic_groups, correlation_groups]
)

# Create consensus composites
for consensus_taxa in consensus_groups:
    if len(consensus_taxa) > 1:
        consensus_abundance = microbiome_data[consensus_taxa].mean(axis=1)
        grouped_data[f'Consensus_Group_{group_id}'] = consensus_abundance
```

**Pros:**
- ✅ **Robust grouping** - Groups supported by multiple lines of evidence
- ✅ **Method validation** - Cross-validation of different grouping approaches
- ✅ **Uncertainty reduction** - Reduces method-specific biases
- ✅ **Confidence enhancement** - Higher trust in consensus groups
- ✅ **Comprehensive insight** - Captures different aspects of microbial organization

**Cons:**
- ❌ **Computational cost** - Running multiple grouping methods
- ❌ **Result integration** - Complex to combine different grouping outputs
- ❌ **Conservative bias** - May miss groups only evident in single methods
- ❌ **Parameter harmonization** - Different methods may have conflicting parameters
- ❌ **Interpretation complexity** - Consensus groups may be harder to characterize

**Limitations:**
- Requires careful consideration of which methods to combine
- Consensus criteria are somewhat arbitrary
- May miss biologically important groups unique to specific methods
- Computational cost multiplies with number of methods

**Why Choose:** Provides high-confidence groupings validated across multiple approaches.

**Expected Results:** 3-6 consensus-based composite features

---

### **10. Custom Hybrid Grouping**
**Description:** Combine multiple grouping approaches based on research-specific requirements and hypotheses.

**Algorithm:**
```python
# Define hybrid grouping strategy
hybrid_groups = {}

# 1. Start with functional groups
functional_groups = define_functional_groups(selected_taxa)

# 2. Refine with correlation within functions
for func_name, func_taxa in functional_groups.items():
    if len(func_taxa) > 3:  # Only subdivide large groups
        subgroups = correlation_clustering(func_taxa, n_clusters=2)
        for i, subgroup in enumerate(subgroups):
            hybrid_groups[f'{func_name}_Subgroup_{i}'] = subgroup
    else:
        hybrid_groups[func_name] = func_taxa

# 3. Create hybrid composites
for group_name, group_taxa in hybrid_groups.items():
    group_abundance = microbiome_data[group_taxa].mean(axis=1)
    grouped_data[group_name] = group_abundance
```

**Pros:**
- ✅ **Research flexibility** - Adapt to specific study questions and hypotheses
- ✅ **Method integration** - Combine strengths of different approaches
- ✅ **Biological precision** - Tailor groupings to research context
- ✅ **Innovation potential** - Test novel grouping strategies
- ✅ **Result optimization** - Maximize relevance to research goals

**Cons:**
- ❌ **Design complexity** - Requires careful planning of hybrid approach
- ❌ **Validation challenges** - Custom methods harder to validate
- ❌ **Reproducibility concerns** - May not generalize to other studies
- ❌ **Documentation burden** - Need to thoroughly document custom logic
- ❌ **Peer review hurdles** - Novel approaches harder to justify

**Limitations:**
- Requires strong scientific rationale for custom groupings
- May need preliminary studies to design optimal hybrid approach
- Validation becomes more critical for novel strategies
- Results may be specific to the particular dataset

**Why Choose:** Maximum flexibility for research-specific grouping strategies and hypothesis testing.

**Expected Results:** Variable - depends on hybrid design (typically 4-12 composite features)

---

## 🎯 Implementation Strategy

### **Recommended Grouping Pipeline:**
```python
# Primary grouping (choose based on research focus)
if research_focus == 'functional':
    groups = apply_functional_pathway_grouping(selected_taxa)
elif research_focus == 'evolutionary':
    groups = apply_taxonomic_hierarchy_grouping(selected_taxa)
else:
    groups = apply_correlation_clustering(selected_taxa)

# Validation grouping (cross-check with different method)
validation_groups = apply_different_method(selected_taxa)

# Create final composites
for group_taxa in groups:
    if len(group_taxa) > 1:
        group_composite = create_composite_feature(microbiome_data[group_taxa])
        grouped_data[f'Primary_Group_{i}'] = group_composite
```

### **Quality Metrics:**
- **Within-group homogeneity:** Groups should show consistent abundance patterns
- **Between-group separation:** Groups should represent distinct microbial patterns
- **Biological interpretability:** Groups should have clear biological meaning
- **Clinical relevance:** Groups should relate to PFS outcomes
- **Stability:** Groups should be reproducible across subsamples

### **Validation Approaches:**
- **Cross-method consistency:** Verify groups appear in multiple grouping methods
- **Biological plausibility:** Ensure groups align with known microbial ecology
- **Clinical correlation:** Test if groups improve PFS prediction
- **Stability analysis:** Check robustness to parameter changes

This variable grouping phase transforms individual taxa into biologically meaningful composite features that capture the multivariate nature of microbial communities while maintaining interpretability and clinical relevance.