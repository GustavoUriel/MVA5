Survival Analysis Models: Cox and Its Alternatives
1. 	Cox Proportional Hazards Model (Cox MVA)
• 	Description: Semi-parametric model that estimates hazard ratios without specifying the baseline hazard.
• 	When to Use: Best when the proportional hazards assumption holds and interpretability is key.
2. Restricted Mean Survival Time (RMST)
• 	Description: Measures the average survival time up to a pre-specified time point (τ), calculated as the area under the survival curve.
• 	When to Use: Ideal when proportional hazards are violated or when a clinically meaningful time horizon is needed. RMST offers intuitive interpretation and robustness in the presence of censoring.
3. Exponential & Log-Logistic Models
• 	Description: Parametric models with specific hazard shapes.
• 	When to Use: Useful when hazard rates are constant (Exponential) or have a peak (Log-Logistic).
4. 	Royston-Parmar Model
• 	Description: Flexible parametric survival model using splines to model the baseline hazard.
• 	When to Use: Ideal for smooth hazard estimates and improved prediction accuracy.
5. 	Accelerated Failure Time (AFT) Model
• 	Description: Models survival time directly with parametric distributions like Weibull or log-normal.
• 	When to Use: Useful when covariate effects are multiplicative on survival time rather than hazard.
6. 	Random Survival Forests
• 	Description: Non-parametric ensemble method using decision trees.
• 	When to Use: Great for high-dimensional data or complex interactions.
7. 	Piecewise Exponential Models
• 	Description: Divides time into intervals, assuming constant hazard within each.
• 	When to Use: Good for modeling time-varying hazards.
8. 	Deep Learning Models (e.g., DeepSurv)
• 	Description: Neural network-based survival models.
• 	When to Use: Suitable for large datasets with nonlinear relationships.