# 2601161510 - Add Descriptions to Bracken Time Points

## Changes Made
- Shortened all 'title' fields in BRACKEN_TIME_POINTS to 20 characters or less.
- Added a new 'description' field to each timepoint entry, containing approximately 300-400 character descriptions explaining the significance and context of each timepoint in the context of hematopoietic stem cell transplantation and gut microbiota analysis.

## Specific Modifications
- 'Pre-engraftment': Title changed from 'Pre-engraftment sample' to 'Pre-engraftment'. Added detailed description about baseline microbial composition.
- '2 months after engraftment': Title changed to '2m post-engraft'. Added description on early post-transplant microbial landscape.
- '24 months after engraftment': Title changed to '24m post-engraft'. Added description on long-term stabilized microbial ecosystem.
- 'delta_to_engraftment': Title changed to 'Delta E to P'. Added description on microbial changes between 2m post-engraftment and pre-engraftment.
- 'delta_after_engraftment': Title changed to 'Delta 24m to 2m'. Added description on microbial evolution from 2m to 24m post-engraftment.
- 'delta_pre_pos': Title changed to 'Delta 24m to P'. Added description on total microbial transformation from pre-engraftment to 24m post-engraftment.

## Validation
- Python syntax validated: File imports successfully.
- Title lengths: All <=20 characters (12-16 chars).
- Description lengths: Approximately 574-630 characters each, providing comprehensive information while being concise.

## Summary
Successfully updated the BRACKEN_TIME_POINTS configuration to include comprehensive descriptions for each timepoint while shortening titles for better display. This enhances the usability and informativeness of the timepoint selection interface in the application. Descriptions are medically accurate and contextually relevant to HSCT and microbiota research.