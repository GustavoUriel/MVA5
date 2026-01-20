2601181400-dynamic_analysis_method_controls.md

## Update Summary

- Enumerated all possible dynamic controls for each analysis method in the Analysis Type section.
- Appended these controls to metadata/temp/map.txt in the required indented format.
- Ensured the map now reflects every control that can be generated dynamically depending on the selected analysis method.

### Details
- Used JS logic from generateParameterInputs() and backend schemas to list all parameter types (number, select, text, etc.) for each method.
- Controls are now mapped for: Cox Proportional Hazards, Accelerated Failure Time, Competing Risks, Frailty Model, Gradient Boosting Survival, Kaplan-Meier, Log-Rank Test, Random Survival Forest, Restricted Mean Survival Time, and any other method defined in the backend.
- Each method's parameters are listed with their type, label, and possible options.

---

**Final Summary:**
All dynamic controls for analysis methods are now included in the map. The map.txt file is a complete hierarchical representation of all UI controls, both static and dynamic, for the analysis configuration page.
