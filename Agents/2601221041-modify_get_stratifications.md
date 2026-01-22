# Modification of get_stratifications function

## Date: 2026-01-22 10:41

## Description
Modified the `get_stratifications` function in `app/modules/datasets/datasets_bp.py` to load metadata from `POPULATION_STRATIFICATIONS.py` instead of `POPULATION_SUBGROUPS.py`, following the same pattern as `get_clustering_methods`.

## Changes Made
- Changed the import from `load_metadata_module('POPULATION_SUBGROUPS')` to using `importlib.import_module('metadata.POPULATION_STRATIFICATIONS')`
- Updated variable names from `POPULATION_SUBGROUPS` to `POPULATION_STRATIFICATIONS`
- Added retrieval of `default_stratification` similar to `default_method` in clustering methods
- Changed the skip condition from `'DEFAULT_POPULATION_SUBGROUPS_SETTINGS'` to `'DEFAULT_POPULATION_STRATIFICATIONS_SETTINGS'`
- Added `default_stratification` to the JSON response

## Files Modified
- `c:\code\Rena Python\MVA5\app\modules\datasets\datasets_bp.py`

## Summary
Successfully updated the `get_stratifications` function to load stratifications metadata from `POPULATION_STRATIFICATIONS.py` using the same import pattern as `get_clustering_methods`, including support for a default stratification if defined in the metadata file.