# 2601161200-restructure_analysis_config_tabs.md

## Summary
Restructured the analysis configuration page from 3 tabs to 5 tabs with new organization:

### Previous Structure (3 tabs):
1. **Data Sources** - File selection, extreme time points, column groups, bracken time points, population stratification
2. **Analysis Config** - Clustering parameters, cluster representative, analysis type  
3. **Report Config** - Report format and content options

### New Structure (5 tabs):
1. **Data Sources** - Select Data Files, Extreme Time Points Selection, Attributes Groups Selection
2. **Pre-Analysis** - Attributes Discarding Policy, Microbial Discarding Policy, Microbial Grouping, Clustering - Policy, Clustering - Naming
3. **Analysis** - Analysis Type
4. **Post-Analysis** - Population Sectors Comparison, Sample Timepoints Comparison, Microbial Grouping Comparison, Analysis Methods Comparison
5. **Output Options** - Report Format, Report Contents

## Changes Made
- Updated tab navigation from 3 to 5 tabs with new names and icons
- Reorganized existing content sections into appropriate new tabs
- Moved Analysis Information section to Data Sources tab
- Moved Clustering and Cluster Representative sections to Pre-Analysis tab (renamed)
- Moved Population Stratification to Post-Analysis tab (renamed to Population Sectors Comparison)
- Moved Report Format/Content to Output Options tab
- Created placeholder cards for new sections that don't exist yet:
  - Attributes Discarding Policy
  - Microbial Discarding Policy  
  - Microbial Grouping
  - Sample Timepoints Comparison
  - Microbial Grouping Comparison
  - Analysis Methods Comparison
- Updated section titles and descriptions to match new naming

## Additional Changes
- Corrected Analysis Information placement: kept it outside the tabs (as it was originally) and removed the duplicate inside Data Sources tab
- Removed duplicate Analysis Information section that was accidentally created during restructuring

## Files Modified
- `app\templates\dataset\analysis_config.html` - Complete restructure of tab navigation and content organization

## Next Steps
- Implement the placeholder sections with actual configuration controls
- Update JavaScript to handle new tab interactions
- Add any new API endpoints needed for the new configuration sections
- Test the new tab structure and ensure all existing functionality still works