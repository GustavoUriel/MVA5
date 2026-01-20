# 2601201440-additional_methods_from_250MVA.md

## Change Summary

On 2026-01-20 at 14:40, the file metadata/ANALYSIS_METHODS.py was updated to include all specifically designed multivariable time-to-event correlation methods listed in architecture/analysis/250.MVAMethods.md, while preserving the data structure and UI integration.

### Methods added:
- pls_survival (Partial Least Squares for Survival)
- spls_da (Sparse Partial Least Squares Discriminant Analysis)
- survival_neural_network
- dirichlet_multinomial_regression
- bayesian_survival_model

### Methods already present (from previous step):
- cox_proportional_hazards
- accelerated_failure_time
- random_survival_forest
- gradient_boosting_survival
- frailty_model
- competing_risks

---

**Summary:**
All methods from 250.MVAMethods.md that are specifically designed for multivariable correlation to event time are now present in ANALYSIS_METHODS.py.
