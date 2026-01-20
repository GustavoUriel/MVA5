# 2601201430-filtered_analysis_methods.md

## Change Summary

On 2026-01-20 at 14:30, the file metadata/ANALYSIS_METHODS.py was modified to retain **only** those methods specifically designed to find correlation between multiple variables and a specific event time (e.g., PFS). All unrelated or descriptive-only methods were removed, preserving the original data structure and all related code.

### Methods retained:
- cox_proportional_hazards
- accelerated_failure_time
- random_survival_forest
- gradient_boosting_survival
- frailty_model
- competing_risks

### Methods removed:
- kaplan_meier
- log_rank_test
- restricted_mean_survival_time

### Other notes:
- The data structure, categories, and UI helper function were preserved and updated to reflect only the relevant methods.

---

**Summary:**
Filtered ANALYSIS_METHODS.py to include only multivariable time-to-event correlation methods, as per project requirements.
