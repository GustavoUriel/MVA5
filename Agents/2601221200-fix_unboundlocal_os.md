# 2601221200-fix_unboundlocal_os

Date: 2026-01-22 12:00 (YYMMDDHHmm format used in filename)

Issue:
- UnboundLocalError raised when hitting `/dataset/<dataset_id>/file/<file_id>/patient-count`.
- Root cause: a local `import os` inside `get_patient_count` caused `os` to be treated as a local variable, but `os` was used earlier in the function before the local binding.

Files changed:
- app/modules/datasets/datasets_bp.py
  - Removed the inner `import os` inside `get_patient_count` so the function uses the module-level `os` import.

Reasoning:
- Removing the local import prevents Python from marking `os` as a local variable for the whole function scope, which resolves the UnboundLocalError.

What I did:
- Edited `get_patient_count` to remove `import os` from inside the `try` block. The function now uses the module-level `os` import.

Summary:
- Fixed UnboundLocalError by removing the local `import os` in `get_patient_count`.

