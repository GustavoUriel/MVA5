# Fix Info Buttons for Microbial and Attributes Discarding Policies

## Issue Description
The info buttons in microbial discarding policy and attributes discarding policies do not work. The JavaScript expects an 'info' field in the policy data to display detailed information in a modal, but there were two issues:
1. The backend API responses were not including the 'info' field
2. The frontend lookup functions were trying to access array data as if it were an object keyed by policy key

## Root Cause
1. Backend functions `get_attribute_discarding_policies` and `get_microbial_discarding_policies` in `datasets_bp.py` were missing the 'info' field in responses
2. Frontend functions `getDiscardingPolicyInfo` and `getMicrobialDiscardingPolicyInfo` were using `data[key]` syntax on arrays instead of finding by key

## Solution
1. Modified backend to include 'info' field in API responses
2. Changed frontend lookup to use `find(p => p.key === policyKey)` instead of direct key access

## Files Modified
- app/modules/datasets/datasets_bp.py
- app/static/js/dataset_analysis.js

## Changes Made
- Backend: Added `'info': policy_data['info']` to responses in both discarding policy functions
- Frontend: Changed policy lookup from `data[key]` to `data.find(p => p.key === key)`

## Testing
- Verified metadata files contain 'info' fields
- Confirmed frontend now properly finds policies by key in the array data structure

## Summary
Fixed info buttons by ensuring backend includes policy info and frontend correctly accesses array data. Buttons should now display detailed policy information in modals.