# 2601200000-add_control_name_microbial_discarding.md

## Change Summary
Added a `control_name` field to each parameter in every method in `metadata/MICROBIAL_DISCARDING.py`. The value is constructed as the parent's `param_prefix` plus the parameter name, matching the convention used in `ANALYSIS_METHODS.py`.

### Details
- For each method, every parameter in the `parameters` dict now has a `control_name` key.
- The value is always: `<param_prefix><parameter_name>`
- No other logic or structure was changed.

### Example
Before:
```python
'detection_threshold': {
    'type': 'float',
    ...
}
```
After:
```python
'detection_threshold': {
    'type': 'float',
    ...
    'control_name': 'MiDi_Prevalence_detection_threshold'
}
```

## Final Summary
All microbial discarding method parameters now have a unique `control_name` for UI and config consistency.
