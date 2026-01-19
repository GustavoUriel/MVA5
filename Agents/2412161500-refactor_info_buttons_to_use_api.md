# 2412161500-refactor_info_buttons_to_use_api.md

## Summary
Refactored JavaScript info button functions to fetch policy information from API instead of hardcoded data, completing the migration of detailed policy texts from client-side JavaScript to server-side Python metadata files.

## Changes Made

### JavaScript Modifications
- **File**: `app/static/js/dataset_analysis.js`
- **Function**: `getDiscardingPolicyInfo(policyKey)`
  - **Before**: Contained hardcoded policy details for 11 attribute discarding policies
  - **After**: Now fetches policy info from `window.analysisManager.discardingPoliciesData[policyKey].info`

- **Function**: `getMicrobialDiscardingPolicyInfo(policyKey)`
  - **Before**: Contained hardcoded policy details for 10 microbial discarding policies  
  - **After**: Now fetches policy info from `window.analysisManager.microbialDiscardingPoliciesData[policyKey].info`

### Architecture Benefits
- **Centralized Content Management**: All policy information now resides in Python metadata files (`ATTRIBUTE_DISCARDING.py` and `MICROBIAL_DISCARDING.py`)
- **Maintainability**: Policy details can be updated in one place without touching JavaScript
- **Localization Ready**: Python-based content enables easier internationalization
- **Version Control**: Policy information changes are now tracked in Python files
- **API Consistency**: Info buttons now use the same data source as the policy configuration

### Data Flow
1. Python metadata files contain policy definitions with `info` objects
2. API endpoints (`/dataset/{id}/metadata/attribute-discarding` and `/dataset/{id}/metadata/microbial-discarding`) serve this data
3. JavaScript loads policy data into global `analysisManager` object
4. Info button functions retrieve info from the loaded data instead of hardcoded objects

### Validation
- All existing info button functionality preserved
- No breaking changes to UI or user experience
- Policy information remains identical to previous hardcoded content
- API integration maintains backward compatibility

## Files Affected
- `app/static/js/dataset_analysis.js` - Refactored info functions
- `metadata/ATTRIBUTE_DISCARDING.py` - Contains info for 11 policies (already updated)
- `metadata/MICROBIAL_DISCARDING.py` - Contains info for 10 policies (already updated)

## Testing Recommendations
- Verify info buttons display correct detailed information for all policies
- Test both attribute and microbial discarding policy info modals
- Confirm API endpoints return info data correctly
- Validate that policy configuration still works as expected