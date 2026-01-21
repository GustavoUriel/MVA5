# 2601211456-fix_discarding_policy_info_buttons.md

## Summary
Fixed the 'Info' buttons in 'Attributes Discarding Policy' and 'Microbial Discarding Policy' sections that were not displaying policy information. The issue was that the modal expected policyInfo to contain parameters, but the API's info object did not include parameters - they were separate fields in the policy object.

## Changes Made
- **getDiscardingPolicyInfo**: Modified to construct a complete policyInfo object by combining policy.info with parameters from policy.parameters, formatted as an array of objects with name, default, description.
- **getMicrobialDiscardingPolicyInfo**: Applied the same fix for microbial discarding policies.

## Validation
- Code structure verified manually.
- No syntax errors introduced.
- Info buttons should now display complete policy information including parameters in the modal.