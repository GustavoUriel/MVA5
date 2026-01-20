<!-- No-op placeholder to ensure file is writable before appending -->
Summary of change - collect controls in DOM order

What I changed:

Reasoning:

Backward compatibility:

Files edited:

Summary:

Additional changes (2026-01-19):

- Replaced the previous heuristic `reorderControls` implementations in both `app/static/js/dataset_analysis.js` and `app/static/js/dataset.js` with a deterministic mapper that returns the exact structure requested by the user:
	- Top-level: `{ analysis_config_structure: { sections: [...] } }`.
	- Sections and subsections follow this sequence and naming: "Analysis Information", "Data Sources", "Pre-Analysis", "Analysis", "Post-Analysis", "Output Options". Each subsection contains an `elements` array.
	- Elements are populated only with input/select/textarea controls discovered in the DOM, in DOM order.
	- For card-style policy/groups (e.g., discarding policies, microbial grouping), the code groups controls by card and emits `{ card_id, elements: [...] }` entries inside the subsection's `elements` list.

Files modified in this step:
- app/static/js/dataset_analysis.js (reorderControls now builds `analysis_config_structure` JSON)
- app/static/js/dataset.js (reorderControls now builds `analysis_config_structure` JSON)

Next steps:
- Scan repository for any code that loads or expects `configuration.controls_state` to be an object keyed by id, and update consumers or add a compatibility shim. (In-progress)

Summary of what I did now:
- Implemented exact-section mapping and card grouping into saved JSON. Controls are included only if they are actual inputs and appear in DOM order.
