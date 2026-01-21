# 2601200000-microbial_discarding_return_raw.md

## Change Summary

- Modified the `/dataset/<int:dataset_id>/metadata/microbial-discarding` endpoint in `datasets_bp.py` to return the `MICROBIAL_DISCARDING` metadata dictionary as-is, without converting it to an ordered list or altering its structure.

### Details
- Removed the logic that filtered and transformed the dictionary into a list.
- The endpoint now simply returns:

```python
return jsonify({
    'success': True,
    'discarding_policies': MICROBIAL_DISCARDING
})
```

## Final Summary
This update ensures the endpoint returns the raw `MICROBIAL_DISCARDING` dictionary, preserving all original structure and data types from the metadata module.
