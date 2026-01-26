import pandas as pd
from app.modules.dataCuration.fixNormalizeColumnsNames import normalize_columns
from app.modules.dataCuration.fixMedicines import fix_medicines_df

# Read and normalize (as the pipeline does)
df = pd.read_csv(r'instance\users\aba_dot_uriel_at_gmail_dot_com\1\files\patients_1_orig.csv', dtype=str)
df_norm = normalize_columns(df, 'patients')

print("After normalization:")
print(f"Total columns: {len(df_norm.columns)}")
date_cols_before = [c for c in df_norm.columns if 'start' in c.lower() or 'end' in c.lower()]
print(f"Date columns before fix_medicines_df: {len(date_cols_before)}")
print(f"Sample: {date_cols_before[:10]}")

# Check Ciprofloxin position
cols = list(df_norm.columns)
cipro_idx = next((i for i, c in enumerate(cols) if c.lower() == 'ciprofloxin'), -1)
if cipro_idx >= 0:
    print(f"\nCiprofloxin at index {cipro_idx}:")
    print(f"  Next 5 columns: {cols[cipro_idx:cipro_idx+6]}")

# Run fix_medicines_df
print("\nRunning fix_medicines_df...")
df_fixed = fix_medicines_df(df_norm.copy())

print(f"\nAfter fix_medicines_df:")
print(f"Total columns: {len(df_fixed.columns)}")
date_cols_after = [c for c in df_fixed.columns if 'start' in c.lower() or 'end' in c.lower()]
print(f"Date columns after: {len(date_cols_after)}")
print(f"Sample: {date_cols_after[:10]}")

print(f"\nDate columns that should have been removed but weren't:")
removed_should_be = set(date_cols_before) - set(date_cols_after)
print(f"Actually removed: {len(removed_should_be)}")
print(f"Still present: {len(set(date_cols_after) & set(date_cols_before))}")
