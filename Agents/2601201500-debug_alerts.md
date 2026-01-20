# 2601201500 - Debug Alerts for Analysis Method Disabling

## Summary
Replaced console.log with alert() in window.updateAnalysisMethod and DatasetAnalysisManager.updateAnalysisMethod to debug why console logs are not appearing in browser console. This will show popup alerts to trace execution flow when dropdown changes.

## Changes Made
- In `window.updateAnalysisMethod()`: Changed all console.log to alert()
- In `DatasetAnalysisManager.updateAnalysisMethod()`: Changed console.log to alert() for key messages

## Expected Behavior
When user changes analysis method dropdown:
1. alert('function called')
2. alert('window.updateAnalysisMethod called - start')
3. alert('window.analysisManager: [object Object]') or 'undefined'
4. If manager exists: alert('calling window.analysisManager.updateAnalysisMethod')
5. alert('DatasetAnalysisManager.updateAnalysisMethod called')
6. alert('selectedKey: <selected value>')
7. alert('calling updateAnalysisMethodsVisibility')
8. alert('window.updateAnalysisMethod called - end')

If manager not found: alert('window.analysisManager not found')

## Next Steps
User to change dropdown and report which alerts appear, then check if selected method checkbox is disabled.