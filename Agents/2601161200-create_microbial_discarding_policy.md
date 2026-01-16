# Microbial Discarding Policy Implementation

## Summary
Created a complete Microbial Discarding Policy card system similar to the existing Attributes Discarding Policy. This includes metadata configuration, API endpoints, HTML UI components, and JavaScript functionality.

## Changes Made

### 1. Metadata Configuration (`metadata/MICROBIAL_DISCARDING.py`)
- Created comprehensive microbial discarding policies with 10 different filtering methods
- Each policy includes detailed parameters, descriptions, and default settings
- Policies focus on microbial-specific filtering criteria (prevalence, abundance, taxonomic level, etc.)
- Includes default settings for quick start configuration

### 2. API Endpoints (`app/modules/datasets/datasets_bp.py`)
- Added `/dataset/<int:dataset_id>/metadata/microbial-discarding` endpoint
  - Returns microbial discarding policy metadata
  - Handles policy ordering and configuration
- Added `/dataset/<int:dataset_id>/metadata/microbial-discarding/calculate-remaining` endpoint
  - Placeholder for calculating remaining microbial taxa after applying policies
  - Returns 501 status indicating implementation pending

### 3. HTML Template Updates (`app/templates/dataset/analysis_config.html`)
- Replaced placeholder content in Microbial Discarding Policy card
- Added dynamic policy container for loading policies
- Added summary section with policy count and calculate button
- Matches the structure and styling of the Attributes Discarding Policy

### 4. JavaScript Functionality (`app/static/js/dataset_analysis.js`)
- Added `loadMicrobialDiscardingPolicies()` function to fetch and display policies
- Added `displayMicrobialDiscardingPolicies()` to render policy cards with parameters
- Added `updateMicrobialDiscardingPolicySummary()` for policy status tracking
- Added `toggleMicrobialPolicyBody()` for expanding/collapsing policy details
- Added `calculateRemainingMicrobes()` global function for the calculate button
- Added `showMicrobialDiscardingPolicyInfo()` for policy information modals
- Added `getMicrobialDiscardingPolicyInfo()` with detailed information for each policy
- Updated initialization to load microbial discarding policies alongside attribute policies

## Technical Details

### Policy Types Implemented
1. **Prevalence Filtering** - Remove taxa below prevalence threshold
2. **Abundance Filtering** - Remove consistently low-abundance taxa
3. **Taxonomic Rarity Filtering** - Filter based on sample count thresholds
4. **Low Abundance Taxa Removal** - Remove taxa never exceeding abundance threshold
5. **Contaminant Filtering** - Remove taxa prevalent in negative controls
6. **Singleton Filtering** - Remove taxa detected in only one sample
7. **Variance-Based Selection** - Select most variable taxa
8. **Taxonomic Level Filtering** - Require minimum taxonomic classification
9. **Core Microbiome Filtering** - Retain only core microbiome taxa
10. **Combined Microbial Selection** - Consensus across multiple methods

### UI Components
- Policy cards with checkboxes for enabling/disabling
- Expandable parameter sections for each enabled policy
- Info buttons with detailed policy information modals
- Summary section showing enabled policy count
- Calculate button for estimating remaining taxa count

### API Structure
- Follows same pattern as attribute discarding endpoints
- Returns ordered policy list with parameters and metadata
- Includes error handling and success status reporting

## Integration Status
- All components created and integrated
- UI loads and displays policies correctly
- Policy toggling and parameter display functional
- Info modals provide detailed policy documentation
- API endpoints return proper data structure
- Follows existing codebase patterns and conventions

## Next Steps
- Implement actual calculation logic for remaining taxa estimation
- Add policy validation and parameter checking
- Integrate with analysis pipeline for actual data filtering
- Add policy presets and configuration saving