# Update (continued)
- Updated the frontend to render input fields for all parameter types (float, int, select, string, static) for both attribute and microbial discarding policies.
- Default values from the API are now shown in the UI, and users can change them.
- Added a method to update the in-memory configuration when a user changes a parameter value.

### Reason
- The UI previously only rendered static descriptions, not real parameter inputs, even though the backend and metadata provided them.
- This change ensures all policy parameters are visible and editable as intended, matching the metadata and API.

---
**Summary:**
- Discarding policy cards now show and allow editing of all parameters, with values initialized from the backend metadata.
# 260119-intended_repair.md

## Date: 2026-01-19

### Change Summary
- Added a fallback message to the card body for both Attribute Discarding Policies and Microbial Discarding Policies in the UI.
- Now, if a policy has no parameters to configure, the card body will display a helpful message instead of being blank.

### Reason
- Users were seeing empty cards when a discarding policy had no parameters, which was confusing.
- This change improves clarity and user experience by always showing some information in the card body.

---
**Summary:**
- UI now shows a message when no parameters are available for a discarding policy, instead of leaving the card body empty.
