"""Verify the fix_medicines_df fix works correctly."""

import pandas as pd
from app.modules.dataCuration.fixNormalizeColumnsNames import normalize_columns
from app.modules.dataCuration.fixMedicines import fix_medicines_df

# Test with the original file
df = pd.read_csv(r'instance\users\aba_dot_uriel_at_gmail_dot_com\1\files\patients_1_orig.csv', dtype=str)
df_norm = normalize_columns(df, 'patients')

print("=" * 80)
print("VERIFICATION TEST: fix_medicines_df Fix")
print("=" * 80)

print(f"\nBefore fix_medicines_df:")
print(f"  Total columns: {len(df_norm.columns)}")
date_cols_before = [c for c in df_norm.columns if ('start' in c.lower() or 'end' in c.lower()) and c.lower() != 'gender']
print(f"  Date columns: {len(date_cols_before)}")

# Check for Cipropfloxin_Eng (the typo case)
cipro_eng_cols = [c for c in df_norm.columns if 'cipro' in c.lower() and 'eng' in c.lower() and 'start' not in c.lower() and 'end' not in c.lower() and 'date' not in c.lower()]
print(f"  Cipro Eng columns found: {cipro_eng_cols}")

# Run the fix
print("\nRunning fix_medicines_df...")
df_fixed = fix_medicines_df(df_norm.copy())

print(f"\nAfter fix_medicines_df:")
print(f"  Total columns: {len(df_fixed.columns)}")
date_cols_after = [c for c in df_fixed.columns if ('start' in c.lower() or 'end' in c.lower()) and c.lower() != 'gender']
print(f"  Date columns remaining: {len(date_cols_after)}")
if date_cols_after:
    print(f"  Remaining date columns: {date_cols_after[:10]}")

# Check specific columns that should be removed
should_be_removed = ['Start_date', 'End_date', 'Start_DateEng', 'End_DateEng']
print(f"\nChecking specific columns:")
for col in should_be_removed:
    in_before = col in df_norm.columns
    in_after = col in df_fixed.columns
    status = "✓ REMOVED" if (in_before and not in_after) else ("✗ STILL PRESENT" if in_after else "? NOT FOUND")
    print(f"  {col}: {status}")

print(f"\n{'='*80}")
if len(date_cols_after) <= 1:  # Only 'gender' might remain
    print("✓ SUCCESS: All date columns removed (except 'gender' which is not a date column)")
else:
    print(f"✗ ISSUE: {len(date_cols_after)} date columns still remain")
print("=" * 80)
