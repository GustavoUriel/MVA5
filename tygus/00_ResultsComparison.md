# 00_ResultsComparison.md: Multi-Method Results Comparison Framework

This document specifies how to compare results across different MVA methods, variable selection approaches, grouping strategies, and complete pipeline runs to identify the most PFS-relevant microbes.

---

## 🎯 **Document Purpose**

This specification defines:
- How to compare results from different analytical methods
- Framework for consensus ranking across methods
- Strategies for identifying top predictive microbes
- Robustness assessment and validation approaches
- Clinical interpretation guidelines

**Use this document when:** Comparing different analysis approaches, identifying robust biomarkers, validating findings, or preparing results for publication.

---

## 📊 **Comparison Levels**

### **Level 1: Within-Stage Method Comparison**
Compare different methods within the same pipeline stage (e.g., Cox vs. Random Forest in MVA stage).
- **Single PipelineData object**
- **Methods applied to same data**
- **Results stored in same `results` section**

### **Level 2: Across-Stage Configuration Comparison**
Compare different upstream configurations (e.g., different variable selection methods).
- **Multiple PipelineData objects**
- **Different feature sets reaching MVA**
- **Requires external comparison framework**

### **Level 3: Complete Pipeline Comparison**
Compare entirely different pipeline strategies (e.g., SCFA-focused vs. pathogen-focused).
- **Multiple PipelineData objects**
- **Different microbial grouping from start**
- **Comprehensive comparison across all dimensions**

---

## 🔢 **Multi-Method Consensus Ranking Framework**

When you have results from multiple MVA methods and/or variable groupings, use this framework to identify the top N most PFS-relevant microbes.

### **Step 1: Score Standardization**

**Purpose:** Convert different scoring systems (hazard ratios, importance scores, attention weights) to comparable 0-1 scale.

**Input Data Sources:**
```python
{
    "cox_regression": {
        "hazard_ratios": {"taxon_A": 1.8, "taxon_B": 0.5, ...},
        "p_values": {"taxon_A": 0.02, "taxon_B": 0.03, ...}
    },
    "random_forest": {
        "importance_scores": {"taxon_A": 0.25, "taxon_B": 0.18, ...}
    },
    "neural_network": {
        "attention_weights": {"taxon_A": 0.32, "taxon_B": 0.28, ...}
    }
}
```

**Standardization Rules:**

1. **Cox Hazard Ratios:**
   ```python
   # Convert HR to standardized score
   hr_deviation = abs(hazard_ratio - 1.0)  # Distance from null (HR=1)
   hr_score = min(hr_deviation, 2.0) / 2.0  # Cap at 2.0, normalize to 0-1
   
   # Weight by statistical significance
   p_score = 1.0 - p_value  # Higher score = lower p-value
   
   # Combined standardized score
   standardized_cox = hr_score * p_score
   ```

2. **Random Forest Importance:**
   ```python
   # Already 0-1 normalized
   standardized_rf = importance_score
   ```

3. **Neural Network Attention:**
   ```python
   # Already 0-1 normalized
   standardized_nn = attention_weight
   ```

4. **Group Contributions:**
   ```python
   # For taxa in composite features
   group_score = group_importance * individual_contribution
   standardized_group = group_score
   ```

**Output Structure:**
```python
standardized_scores = {
    "taxon_name": {
        "cox_standardized": 0.85,
        "rf_standardized": 0.25,
        "nn_standardized": 0.32,
        "group_beneficial_bacteria": 0.40,
        "group_scfa_producers": 0.35
    }
}
```

---

### **Step 2: Consensus Score Calculation**

**Purpose:** Combine standardized scores from all methods into single consensus metric.

**Default Weighting Scheme:**
```python
default_weights = {
    "cox_regression": 0.30,      # Gold standard for survival analysis
    "random_forest": 0.25,       # Non-parametric robustness
    "neural_network": 0.25,      # Non-linear relationships
    "group_contributions": 0.20  # Composite feature context
}
```

**Calculation Method:**
```python
def calculate_consensus_score(standardized_scores, weights=None):
    """
    Calculate weighted consensus score for each taxon.
    
    Parameters:
    - standardized_scores: Dict of standardized scores per taxon per method
    - weights: Dict of weights per method category (optional)
    
    Returns:
    - Dict of consensus scores per taxon
    """
    if weights is None:
        weights = default_weights
    
    consensus_results = {}
    
    for taxon, scores in standardized_scores.items():
        # Collect available method scores
        available_scores = {}
        
        # MVA method scores
        if "cox_standardized" in scores:
            available_scores["cox_regression"] = scores["cox_standardized"]
        if "rf_standardized" in scores:
            available_scores["random_forest"] = scores["rf_standardized"]
        if "nn_standardized" in scores:
            available_scores["neural_network"] = scores["nn_standardized"]
        
        # Group contribution scores (average if multiple groups)
        group_scores = [
            score for key, score in scores.items() 
            if key.startswith("group_")
        ]
        if group_scores:
            available_scores["group_contributions"] = sum(group_scores) / len(group_scores)
        
        # Calculate weighted consensus
        weighted_sum = sum(
            weights[method] * score 
            for method, score in available_scores.items()
            if method in weights
        )
        
        # Normalize by number of available methods
        method_count = len(available_scores)
        total_weight = sum(weights[m] for m in available_scores.keys() if m in weights)
        
        consensus_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        consensus_results[taxon] = {
            "consensus_score": consensus_score,
            "method_scores": available_scores,
            "methods_used": list(available_scores.keys()),
            "method_count": method_count,
            "confidence": method_count / 4  # Fraction of possible methods (4 total)
        }
    
    return consensus_results
```

**Output Structure:**
```python
consensus_results = {
    "faecalibacterium_prausnitzii": {
        "consensus_score": 0.78,
        "method_scores": {
            "cox_regression": 0.85,
            "random_forest": 0.25,
            "neural_network": 0.32,
            "group_contributions": 0.38
        },
        "methods_used": ["cox_regression", "random_forest", "neural_network", "group_contributions"],
        "method_count": 4,
        "confidence": 1.0  # All 4 methods available
    },
    "bifidobacterium_longum": {
        "consensus_score": 0.71,
        "method_scores": {
            "cox_regression": 0.80,
            "random_forest": 0.18,
            "group_contributions": 0.30
        },
        "methods_used": ["cox_regression", "random_forest", "group_contributions"],
        "method_count": 3,
        "confidence": 0.75  # 3 of 4 methods
    }
}
```

---

### **Step 3: Ranking and Top-N Selection**

**Purpose:** Create ranked list of most PFS-relevant microbes.

**Ranking Method:**
```python
def create_final_ranking(consensus_results, top_n=10):
    """
    Create ranked list of top N microbes by consensus score.
    
    Parameters:
    - consensus_results: Output from calculate_consensus_score()
    - top_n: Number of top microbes to return
    
    Returns:
    - List of top N taxa names
    - Detailed ranking information per taxon
    """
    # Sort by consensus score (descending)
    ranked_taxa = sorted(
        consensus_results.items(),
        key=lambda x: x[1]["consensus_score"],
        reverse=True
    )
    
    # Extract top N
    top_taxa = []
    ranking_details = {}
    
    for rank, (taxon, data) in enumerate(ranked_taxa[:top_n], 1):
        top_taxa.append(taxon)
        ranking_details[taxon] = {
            "rank": rank,
            "consensus_score": data["consensus_score"],
            "method_scores": data["method_scores"],
            "methods_used": data["methods_used"],
            "confidence": data["confidence"],
            "evidence_strength": classify_evidence_strength(data)
        }
    
    return top_taxa, ranking_details

def classify_evidence_strength(taxon_data):
    """Classify evidence strength based on consensus and confidence"""
    score = taxon_data["consensus_score"]
    conf = taxon_data["confidence"]
    
    if score >= 0.75 and conf >= 0.75:
        return "strong"  # High score, high confidence
    elif score >= 0.60 and conf >= 0.50:
        return "moderate"  # Good score, reasonable confidence
    elif score >= 0.40:
        return "weak"  # Low score or low confidence
    else:
        return "insufficient"  # Very low score
```

**Output Structure:**
```python
top_10_microbes = [
    "faecalibacterium_prausnitzii",
    "bifidobacterium_longum",
    "lactobacillus_rhamnosus",
    # ... 7 more
]

ranking_details = {
    "faecalibacterium_prausnitzii": {
        "rank": 1,
        "consensus_score": 0.78,
        "method_scores": {...},
        "methods_used": ["cox", "rf", "nn", "groups"],
        "confidence": 1.0,
        "evidence_strength": "strong"
    },
    # ... details for each of top 10
}
```

---

### **Step 4: Method Agreement Analysis**

**Purpose:** Assess consistency across different analytical methods.

**Pairwise Agreement Calculation:**
```python
def analyze_method_agreement(consensus_results, top_n=10):
    """
    Analyze agreement between different methods for top N taxa.
    
    Returns:
    - Method-specific rankings
    - Pairwise overlap percentages
    - Consensus stability metric
    """
    # Get rankings from each method
    method_rankings = {}
    
    for taxon, data in consensus_results.items():
        for method, score in data["method_scores"].items():
            if method not in method_rankings:
                method_rankings[method] = []
            method_rankings[method].append((taxon, score))
    
    # Sort each method's ranking
    for method in method_rankings:
        method_rankings[method].sort(key=lambda x: x[1], reverse=True)
        method_rankings[method] = [taxon for taxon, _ in method_rankings[method][:top_n]]
    
    # Calculate pairwise agreement
    pairwise_agreement = {}
    methods = list(method_rankings.keys())
    
    for i in range(len(methods)):
        for j in range(i+1, len(methods)):
            method1, method2 = methods[i], methods[j]
            rank1 = set(method_rankings[method1])
            rank2 = set(method_rankings[method2])
            
            overlap = rank1 & rank2
            overlap_count = len(overlap)
            agreement_pct = overlap_count / top_n
            
            pairwise_agreement[f"{method1}_vs_{method2}"] = {
                "overlap_count": overlap_count,
                "agreement_percentage": agreement_pct,
                "shared_taxa": list(overlap),
                "unique_to_method1": list(rank1 - rank2),
                "unique_to_method2": list(rank2 - rank1)
            }
    
    # Calculate consensus stability (average pairwise agreement)
    stability = sum(
        data["agreement_percentage"] 
        for data in pairwise_agreement.values()
    ) / len(pairwise_agreement) if pairwise_agreement else 0
    
    # Categorize taxa by agreement level
    taxa_agreement = categorize_by_agreement(method_rankings, top_n)
    
    return {
        "method_rankings": method_rankings,
        "pairwise_agreement": pairwise_agreement,
        "consensus_stability": stability,
        "taxa_by_agreement": taxa_agreement
    }

def categorize_by_agreement(method_rankings, top_n):
    """Categorize taxa by how many methods ranked them in top N"""
    taxa_counts = {}
    methods = list(method_rankings.keys())
    
    for method, ranking in method_rankings.items():
        for taxon in ranking:
            taxa_counts[taxon] = taxa_counts.get(taxon, 0) + 1
    
    return {
        "perfect_agreement": [t for t, c in taxa_counts.items() if c == len(methods)],
        "high_agreement": [t for t, c in taxa_counts.items() if c >= len(methods) * 0.75],
        "moderate_agreement": [t for t, c in taxa_counts.items() if c >= len(methods) * 0.50],
        "low_agreement": [t for t, c in taxa_counts.items() if c < len(methods) * 0.50]
    }
```

**Output Structure:**
```python
agreement_analysis = {
    "method_rankings": {
        "cox_regression": ["taxon_A", "taxon_B", ...],  # Top 10 by Cox
        "random_forest": ["taxon_A", "taxon_C", ...],   # Top 10 by RF
        "neural_network": ["taxon_A", "taxon_B", ...]   # Top 10 by NN
    },
    "pairwise_agreement": {
        "cox_regression_vs_random_forest": {
            "overlap_count": 7,
            "agreement_percentage": 0.70,
            "shared_taxa": ["taxon_A", "taxon_B", ...],
            "unique_to_method1": ["taxon_X"],
            "unique_to_method2": ["taxon_Y", "taxon_Z"]
        }
    },
    "consensus_stability": 0.72,  # 72% average agreement
    "taxa_by_agreement": {
        "perfect_agreement": ["taxon_A"],  # In all methods' top 10
        "high_agreement": ["taxon_A", "taxon_B", "taxon_C"],
        "moderate_agreement": ["taxon_A", ..., "taxon_F"],
        "low_agreement": ["taxon_G", "taxon_H"]
    }
}
```

---

### **Step 5: Robustness Assessment**

**Purpose:** Assess stability of rankings through bootstrapping and sensitivity analysis.

**Bootstrap Stability:**
```python
def assess_ranking_robustness(consensus_results, n_bootstrap=100, top_n=10):
    """
    Assess robustness through bootstrap resampling.
    
    Returns:
    - Rank stability per position
    - Overall consistency metric
    - Confidence intervals
    """
    import numpy as np
    
    # Get all taxa and their consensus scores
    taxa_scores = [
        (taxon, data["consensus_score"]) 
        for taxon, data in consensus_results.items()
    ]
    
    bootstrap_ranks = []
    
    for _ in range(n_bootstrap):
        # Bootstrap sample of methods (with replacement)
        sample_indices = np.random.choice(
            len(taxa_scores), 
            len(taxa_scores), 
            replace=True
        )
        bootstrap_sample = [taxa_scores[i] for i in sample_indices]
        
        # Re-rank bootstrap sample
        bootstrap_sample.sort(key=lambda x: x[1], reverse=True)
        bootstrap_ranks.append([taxon for taxon, _ in bootstrap_sample])
    
    # Calculate rank stability for each position
    rank_stability = {}
    
    for position in range(min(top_n, len(taxa_scores))):
        taxa_at_position = [
            ranks[position] 
            for ranks in bootstrap_ranks 
            if position < len(ranks)
        ]
        
        # Most common taxon at this position
        from collections import Counter
        taxon_counts = Counter(taxa_at_position)
        most_common_taxon, count = taxon_counts.most_common(1)[0]
        stability_pct = count / len(taxa_at_position)
        
        rank_stability[f"rank_{position+1}"] = {
            "most_stable_taxon": most_common_taxon,
            "stability_percentage": stability_pct,
            "alternative_taxa": [t for t, c in taxon_counts.most_common(5)],
            "interpretation": interpret_stability(stability_pct)
        }
    
    # Overall consistency
    overall_consistency = sum(
        data["stability_percentage"] 
        for data in rank_stability.values()
    ) / len(rank_stability)
    
    return {
        "rank_stability": rank_stability,
        "overall_consistency": overall_consistency,
        "bootstrap_samples": n_bootstrap,
        "interpretation": interpret_stability(overall_consistency)
    }

def interpret_stability(stability_pct):
    """Interpret stability percentage"""
    if stability_pct >= 0.90:
        return "highly_stable"
    elif stability_pct >= 0.70:
        return "moderately_stable"
    elif stability_pct >= 0.50:
        return "somewhat_stable"
    else:
        return "unstable"
```

**Output Structure:**
```python
robustness = {
    "rank_stability": {
        "rank_1": {
            "most_stable_taxon": "faecalibacterium_prausnitzii",
            "stability_percentage": 0.94,
            "alternative_taxa": [
                ("faecalibacterium_prausnitzii", 94),
                ("bifidobacterium_longum", 6)
            ],
            "interpretation": "highly_stable"
        },
        "rank_2": {
            "most_stable_taxon": "bifidobacterium_longum",
            "stability_percentage": 0.78,
            "alternative_taxa": [
                ("bifidobacterium_longum", 78),
                ("lactobacillus_rhamnosus", 15),
                ("faecalibacterium_prausnitzii", 7)
            ],
            "interpretation": "moderately_stable"
        }
    },
    "overall_consistency": 0.85,
    "bootstrap_samples": 100,
    "interpretation": "highly_stable"
}
```

---

## 🔬 **Clinical Interpretation Framework**

### **Evidence Strength Classification**

**Strong Evidence (Consensus ≥0.75, Confidence ≥0.75):**
- Selected by all or most methods
- High statistical significance across methods
- Robust to methodological choices
- **Recommendation:** Priority for clinical validation and intervention studies

**Moderate Evidence (Consensus ≥0.60, Confidence ≥0.50):**
- Selected by multiple methods
- Moderate statistical significance
- Some sensitivity to methodological choices
- **Recommendation:** Include in validation studies, monitor closely

**Weak Evidence (Consensus ≥0.40):**
- Selected by few methods or low scores
- Marginal statistical significance
- High sensitivity to methodological choices
- **Recommendation:** Exploratory analysis, consider for hypothesis generation

**Insufficient Evidence (Consensus <0.40):**
- Inconsistent across methods
- Low statistical significance
- Not reliable for clinical decisions
- **Recommendation:** Do not prioritize for follow-up studies

---

### **Protective vs. Risk Classification**

For taxa with strong/moderate evidence:

**Protective Factors (HR < 1.0 in Cox):**
- Associated with longer PFS
- Higher abundance = better outcomes
- **Clinical implication:** Consider probiotic or dietary interventions to increase

**Risk Factors (HR > 1.0 in Cox):**
- Associated with shorter PFS
- Higher abundance = worse outcomes
- **Clinical implication:** Monitor for dysbiosis, consider targeted antibiotics or FMT

**Neutral/Unclear (HR ≈ 1.0 or conflicting results):**
- No clear association with PFS
- May have non-linear or interaction effects
- **Clinical implication:** Further research needed

---

## 📊 **Complete Comparison Workflow**

### **Workflow for Single Pipeline (Multiple MVA Methods)**

```python
# Step 1: Standardize scores across methods
standardized = standardize_scores(pipeline_data)

# Step 2: Calculate consensus scores
consensus = calculate_consensus_score(standardized)

# Step 3: Create top-N ranking
top_10, details = create_final_ranking(consensus, top_n=10)

# Step 4: Analyze method agreement
agreement = analyze_method_agreement(consensus, top_n=10)

# Step 5: Assess robustness
robustness = assess_ranking_robustness(consensus, n_bootstrap=100)

# Step 6: Generate final report
report = generate_comparison_report(
    top_10, details, agreement, robustness
)
```

---

### **Workflow for Multiple Pipelines (Different Configurations)**

```python
# Create comparison object for multiple runs
pipeline_comparison = {
    "run_1_scfa_focused": pipeline_data_1,
    "run_2_pathogen_focused": pipeline_data_2,
    "run_3_comprehensive": pipeline_data_3
}

# For each run, calculate consensus
run_consensus = {}
for run_name, pipeline in pipeline_comparison.items():
    standardized = standardize_scores(pipeline)
    consensus = calculate_consensus_score(standardized)
    top_10, details = create_final_ranking(consensus)
    
    run_consensus[run_name] = {
        "consensus": consensus,
        "top_10": top_10,
        "details": details
    }

# Compare across runs
cross_run_comparison = compare_pipeline_runs(run_consensus)

# Identify robust findings across all runs
robust_taxa = identify_robust_taxa_across_runs(run_consensus)
```

---

## 📋 **Comparison Report Structure**

### **Executive Summary**

```python
report = {
    "executive_summary": {
        "top_10_microbes": [...],
        "consensus_stability": 0.85,
        "ranking_robustness": 0.91,
        "evidence_distribution": {
            "strong": 4,
            "moderate": 3,
            "weak": 2,
            "insufficient": 1
        },
        "methods_used": ["cox", "rf", "nn"],
        "total_taxa_analyzed": 350
    }
}
```

### **Detailed Rankings**

```python
report["detailed_rankings"] = {
    "rank_1": {
        "taxon": "faecalibacterium_prausnitzii",
        "consensus_score": 0.78,
        "evidence_strength": "strong",
        "pfs_effect": "protective",
        "method_scores": {...},
        "bootstrap_stability": 0.94,
        "biological_interpretation": "SCFA producer, anti-inflammatory",
        "clinical_recommendation": "Priority for probiotic intervention"
    },
    # ... ranks 2-10
}
```

### **Method Comparison**

```python
report["method_comparison"] = {
    "performance_metrics": {
        "cox_regression": {"auroc": 0.82, "c_index": 0.79},
        "random_forest": {"auroc": 0.85, "c_index": 0.82},
        "neural_network": {"auroc": 0.87, "c_index": 0.84}
    },
    "agreement_matrix": {
        "cox_vs_rf": 0.70,
        "cox_vs_nn": 0.65,
        "rf_vs_nn": 0.80
    },
    "consensus_stability": 0.72,
    "interpretation": "Good agreement across methods (72%)"
}
```

### **Clinical Recommendations**

```python
report["clinical_recommendations"] = [
    {
        "priority": "high",
        "action": "Validate top 3 taxa in independent cohort",
        "taxa": ["faecalibacterium_prausnitzii", "bifidobacterium_longum", "lactobacillus_rhamnosus"],
        "rationale": "Strong evidence across all methods"
    },
    {
        "priority": "medium",
        "action": "Consider probiotic intervention study",
        "taxa": ["faecalibacterium_prausnitzii", "bifidobacterium_longum"],
        "rationale": "Protective factors with clinical relevance"
    },
    {
        "priority": "low",
        "action": "Monitor in clinical practice",
        "taxa": [...],
        "rationale": "Moderate evidence, needs validation"
    }
]
```

### **Research Priorities**

```python
report["research_priorities"] = [
    "Validate top-ranked taxa in independent MM cohort",
    "Investigate biological mechanisms for protective taxa",
    "Develop targeted microbiome modulation strategies",
    "Conduct pilot intervention study with top SCFA producers",
    "Monitor PFS outcomes in microbiome-guided treatment"
]
```

---

## 🎯 **Best Practices**

### **For Method Selection**
1. Use at least 2-3 MVA methods for robustness
2. Include Cox regression as gold standard for survival
3. Add non-parametric method (RF) for complex relationships
4. Consider neural networks for large datasets

### **For Consensus Ranking**
1. Use standardized scoring to ensure comparability
2. Weight methods based on study design appropriateness
3. Require minimum confidence threshold (≥0.50)
4. Bootstrap to assess ranking stability

### **For Clinical Translation**
1. Focus on taxa with strong evidence (consensus ≥0.75)
2. Prioritize taxa in perfect/high method agreement
3. Consider biological plausibility and mechanism
4. Validate in independent cohort before clinical application

### **For Reporting**
1. Report full methodology including weighting schemes
2. Show method-specific results alongside consensus
3. Include robustness metrics and confidence intervals
4. Provide biological interpretation for top taxa

---

## 📚 **Related Documentation**

- **00_DataFlow.md** - Complete data structure specification
- **06_MVAMethods.md** - Individual MVA method descriptions
- **03_VariableSelection.md** - Variable selection approaches
- **04_VariableGrouping.md** - Feature aggregation methods

---

## 🎯 **Summary**

This comparison framework provides:
- ✅ **Standardized scoring** across different MVA methods
- ✅ **Consensus ranking** for robust biomarker identification
- ✅ **Method agreement analysis** to assess consistency
- ✅ **Robustness assessment** through bootstrapping
- ✅ **Clinical interpretation** guidelines for translation
- ✅ **Complete reporting** structure for publication

**Use this framework to identify the most reliable, clinically relevant microbes for PFS prediction in Multiple Myeloma!** 🔬📊🏥
