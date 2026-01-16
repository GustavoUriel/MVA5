# Fix Microbial Discarding Policy Show/Hide Button

## Issue
The Microbial Discarding Policy card was missing the show/hide button that allows users to toggle the visibility of the discarding policy cards. The policies were being loaded but remained hidden because the content container had `display: none` by default.

## Root Cause
The microbial discarding policy implementation was missing:
1. The show/hide toggle button in the card header
2. The JavaScript function to handle the toggle functionality

## Changes Made

### 1. HTML Template Update (`app/templates/dataset/analysis_config.html`)
- Added a show/hide button in the microbial discarding policy card header
- Button uses the same styling and structure as the attribute discarding policy
- Button ID: `toggleMicrobialDiscardingPolicyBtn`
- Button calls: `toggleMicrobialDiscardingPolicy()`

### 2. JavaScript Function Addition (`app/static/js/dataset_analysis.js`)
- Added `toggleMicrobialDiscardingPolicy()` function
- Toggles visibility of `microbialDiscardingPolicyContent` div
- Updates button text between "Show Policies" and "Hide Policies"
- Follows the exact same pattern as the attribute discarding toggle

## Result
The Microbial Discarding Policy card now has a functional show/hide button that allows users to:
- Initially see only the description and summary
- Click "Show Policies" to reveal all 10 discarding policy cards with their parameters
- Click "Hide Policies" to collapse the policy cards back to summary view

This matches the behavior of the Attributes Discarding Policy card exactly.