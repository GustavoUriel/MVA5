# 2601221224 - Change Analysis Save Location

## Changes Made

### 1. Modified `save_analysis_configuration` function
- Changed analysis folder path from `users/{user_email}/analysis` to `users/{user_email}/{dataset_id}/analysis`
- Updated relative_path in analysis config to include dataset_id: `users/{user_email}/{dataset_id}/analysis/{safe_name}.json`

### 2. Updated `list_saved_analyses` function
- Changed analysis folder path to include dataset_id: `users/{user_email}/{dataset_id}/analysis`

### 3. Updated `delete_analysis` function
- Changed analysis folder path to include dataset_id

### 4. Updated `duplicate_analysis` function
- Changed analysis folder path to include dataset_id
- Updated relative_path assignment in duplicated analysis to include dataset_id

### 5. Updated `rename_analysis` function
- Changed analysis folder path to include dataset_id

## Purpose
The analysis configurations are now saved in a dataset-specific folder structure: `instance/users/{user_email}/{dataset_id}/analysis/`. This organizes analyses by both user and dataset, preventing conflicts and making it easier to manage analyses per dataset.

## Summary
Successfully restructured the analysis save location to include dataset_id in the folder hierarchy, ensuring better organization and isolation of analysis configurations per dataset.
