# 2601181400-change_microbial_grouping_to_radio_buttons.md

## Summary of Changes

### Files Modified:
1. `app/static/js/dataset_analysis.js` - Changed microbial grouping from checkboxes to radio buttons for single selection

### Changes Made:

#### 1. `displayMicrobialGroupingPolicies()` Function:
- Changed input type from `"checkbox"` to `"radio"`
- Added `name="microbialGroupingMethod"` attribute to group radio buttons
- Changed `isEnabled` to `isChecked` for clarity
- Updated event listener comments from "checkboxes" to "radio buttons"

#### 2. `collectMicrobialGrouping()` Function:
- Completely rewrote to return single selected method instead of all methods with enabled flags
- Now returns `null` if no method is selected, or an object with `method` (key) and `parameters`
- Collects parameters only from the selected method's card

#### 3. `updateMicrobialGroupingSummary()` Function:
- Changed to handle radio button selection instead of multiple checkboxes
- Shows "Selected: [Method Name]" instead of "Enabled: [Method1, Method2, ...]"
- Updates count to show "1 method" or "0 methods"

#### 4. `toggleMicrobialGroupingBody()` Function:
- Modified to hide all method bodies first, then show only the selected method's body
- Ensures only one method's parameters are visible at a time

#### 5. `resetAnalysisEditor()` Function:
- Added code to uncheck all microbial grouping radio buttons
- Hides all microbial grouping method bodies on reset

### Technical Details:
- **Selection Behavior**: Changed from multiple selection (checkboxes) to single selection (radio buttons)
- **Data Structure**: Collection now returns single method object instead of methods dictionary
- **UI Behavior**: Only selected method shows parameter form, others are hidden
- **Summary Display**: Shows selected method name instead of list of enabled methods

### User Experience Impact:
- Users can now select only one microbial grouping method at a time
- Parameter forms appear/disappear based on selection
- Clear visual indication of which method is selected
- Simplified summary showing single selected method

### Backward Compatibility:
- Analysis configuration data structure changed from methods dictionary to single method object
- Existing saved analyses may need to be updated or handled gracefully
- Frontend now expects single method selection instead of multiple

## Summary
Successfully changed microbial grouping UI from multi-select checkboxes to single-select radio buttons, ensuring only one grouping method can be selected at a time.