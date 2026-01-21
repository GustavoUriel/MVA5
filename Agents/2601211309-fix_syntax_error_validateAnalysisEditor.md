# 2601211309 - Fix syntax error in validateAnalysisEditor function

## Summary
Fixed a syntax error in dataset.js where there was an illegal return statement caused by duplicate function calls and mismatched braces in the validateAnalysisEditor function.

## Problem
The validateAnalysisEditor function had:
- Duplicate calls to window.analysisManager.updateExtremeTimePointSummary()
- Mismatched braces causing the return statement to be outside the function scope
- This resulted in "Illegal return statement" error at line 2746

## Root Cause
During the unification of extremeTimePointSummaryText handling, the code was left with both a conditional call inside an if statement and an unconditional call outside, plus extra braces.

## Changes Made
**dataset.js - validateAnalysisEditor function:**
- Removed duplicate call to window.analysisManager.updateExtremeTimePointSummary()
- Fixed brace matching to ensure proper function structure
- Kept only the conditional call with null check for window.analysisManager

## Code Fix
```javascript
// Before (broken):
if (window.analysisManager) {
  window.analysisManager.updateExtremeTimePointSummary();
}
  window.analysisManager.updateExtremeTimePointSummary();  // Duplicate call
}

// After (fixed):
if (window.analysisManager) {
  window.analysisManager.updateExtremeTimePointSummary();
}
```

## Validation
- Syntax error resolved
- Function structure is now correct
- Maintains the intended behavior of conditionally updating the extreme time point summary

## Summary
Successfully fixed the syntax error by removing duplicate code and correcting brace matching in the validateAnalysisEditor function.