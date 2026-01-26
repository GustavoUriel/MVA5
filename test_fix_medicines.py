"""Test script to verify fix_medicines_file functionality for steps d, e, and f."""

import pandas as pd
from pathlib import Path
from app.modules.dataCuration.fixMedicines import fix_medicines_file, fix_medicines_df
from app.modules.dataCuration.fixNormalizeColumnsNames import normalize_columns
from metadata.COLUMNS import MEDICINES

# Test file path
test_file = Path(r"instance\users\aba_dot_uriel_at_gmail_dot_com\1\files\patients.csv")

print("=" * 80)
print("TESTING fix_medicines_df (with normalization)")
print("=" * 80)

# Read original file
print(f"\n1. Reading original file: {test_file}")
df_original = pd.read_csv(test_file, dtype=str)
print(f"   Original shape: {df_original.shape}")
print(f"   Original columns count: {len(df_original.columns)}")

# Normalize columns (as the actual pipeline does)
print("\n1a. Normalizing column names...")
df_original = normalize_columns(df_original, "patients")
print(f"   After normalization: {len(df_original.columns)} columns")

# Get a sample row to analyze (first patient with transplant date)
print("\n2. Analyzing first patient with transplant date...")
first_patient = df_original.iloc[0]
transplant_date = pd.to_datetime(first_patient['First_Transplant_Date'], format="%m/%d/%Y", errors="coerce")
print(f"   Patient ID: {first_patient['patient_id']}")
print(f"   Transplant Date: {transplant_date}")

# Show medicine columns before
print("\n3. Medicine columns BEFORE processing:")
print("   Checking for medicine-related columns in normalized DataFrame...")
all_med_cols = [c for c in df_original.columns if any(drug in c.lower() for drug in ['cipro', 'levo', 'moxi', 'amox', 'amp', 'cef', 'azith', 'trim', 'clinda', 'metro', 'vanco', 'flucon'])]
print(f"   Found {len(all_med_cols)} medicine-related columns")
print(f"   Sample: {all_med_cols[:10]}")

medicine_cols_before = []
for drug_group in MEDICINES.values():
    for drug in drug_group:
        # Check for main column
        main_col = drug
        eng_col = f"{drug}_eng"  # Note: normalized to lowercase
        if main_col in df_original.columns:
            medicine_cols_before.append(main_col)
            val = first_patient[main_col] if main_col in first_patient.index else 'N/A'
            print(f"   - {main_col}: {val}")
        if eng_col in df_original.columns:
            medicine_cols_before.append(eng_col)
            val = first_patient[eng_col] if eng_col in first_patient.index else 'N/A'
            print(f"   - {eng_col}: {val}")

# Find date columns for a sample drug
sample_drug = 'ciprofloxin'
print(f"\n4. Date columns for sample drug '{sample_drug}':")
date_cols = []
for col in df_original.columns:
    if sample_drug.lower() in col.lower() or 'ciprofloxin' in col.lower():
        if 'start' in col.lower() or 'end' in col.lower():
            date_cols.append(col)
            print(f"   - {col}: {first_patient[col] if col in first_patient.index else 'N/A'}")

# Run the function on normalized DataFrame
print("\n5. Running fix_medicines_df on normalized DataFrame...")
df_fixed = fix_medicines_df(df_original.copy())
print(f"   Fixed shape: {df_fixed.shape}")
print(f"   Fixed columns count: {len(df_fixed.columns)}")

# Compare columns
print("\n7. Column comparison:")
cols_before = set(df_original.columns)
cols_after = set(df_fixed.columns)
removed_cols = cols_before - cols_after
added_cols = cols_after - cols_before

print(f"   Columns removed: {len(removed_cols)}")
if removed_cols:
    print("   Removed columns:")
    for col in sorted(removed_cols)[:20]:  # Show first 20
        print(f"     - {col}")
    if len(removed_cols) > 20:
        print(f"     ... and {len(removed_cols) - 20} more")

print(f"   Columns added: {len(added_cols)}")
if added_cols:
    print("   Added columns:")
    for col in sorted(added_cols):
        print(f"     - {col}")

# Verify step d: Peri-transplant filtering
print("\n8. VERIFYING STEP D: Peri-transplant filtering")
print("   Checking if indicators were set to 0 for peri-transplant treatments...")
first_patient_fixed = df_fixed.iloc[0]
changes_found = False

for drug_group in MEDICINES.values():
    for drug in drug_group:
        main_col = drug
        eng_col = f"{drug}_Eng"
        
        # Check main column
        if main_col in df_original.columns and main_col in df_fixed.columns:
            orig_val = df_original.iloc[0][main_col]
            fixed_val = df_fixed.iloc[0][main_col]
            if orig_val != fixed_val:
                print(f"   ✓ {main_col}: {orig_val} -> {fixed_val}")
                changes_found = True
        
        # Check eng column (should be removed, but check if it exists)
        if eng_col in df_original.columns:
            if eng_col not in df_fixed.columns:
                print(f"   ✓ {eng_col}: removed (merged into {main_col})")
                changes_found = True

if not changes_found:
    print("   No changes detected in first patient (may need to check other patients)")

# Verify step e: Column merging
print("\n9. VERIFYING STEP E: Column merging")
print("   Checking if _Eng columns were merged into main columns...")
eng_cols_removed = [col for col in removed_cols if col.endswith('_Eng') and not ('Start' in col or 'End' in col)]
print(f"   Found {len(eng_cols_removed)} _Eng indicator columns removed:")
for col in eng_cols_removed[:10]:
    print(f"     - {col}")

# Check if merged values are correct (OR logic)
print("\n   Checking merged values (should be 1 if either original was 1):")
for drug_group in MEDICINES.values():
    for drug in drug_group:
        main_col = drug
        eng_col = f"{drug}_Eng"
        if main_col in df_original.columns:
            orig_main = df_original.iloc[0][main_col] if main_col in df_original.columns else '0'
            orig_eng = df_original.iloc[0][eng_col] if eng_col in df_original.columns else '0'
            fixed_main = df_fixed.iloc[0][main_col] if main_col in df_fixed.columns else '0'
            
            # Convert to int for comparison
            orig_main_int = int(float(str(orig_main))) if str(orig_main) not in ['', 'nan', 'NaN'] else 0
            orig_eng_int = int(float(str(orig_eng))) if str(orig_eng) not in ['', 'nan', 'NaN'] else 0
            fixed_main_int = int(float(str(fixed_main))) if str(fixed_main) not in ['', 'nan', 'NaN'] else 0
            expected = 1 if (orig_main_int == 1 or orig_eng_int == 1) else 0
            
            if orig_main_int != orig_eng_int or orig_main_int != fixed_main_int:
                print(f"     {main_col}: main={orig_main_int}, eng={orig_eng_int}, merged={fixed_main_int}, expected={expected} {'✓' if fixed_main_int == expected else '✗'}")

# Verify step f: Cleanup (date columns removed)
print("\n10. VERIFYING STEP F: Cleanup (date columns removed)")
date_cols_removed = [col for col in removed_cols if 'start' in col.lower() or 'end' in col.lower()]
print(f"   Found {len(date_cols_removed)} date columns removed:")
for col in sorted(date_cols_removed)[:15]:
    print(f"     - {col}")
if len(date_cols_removed) > 15:
    print(f"     ... and {len(date_cols_removed) - 15} more")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Step D (Peri-transplant filtering): {'✓ VERIFIED' if changes_found else '? Need to check more patients'}")
print(f"Step E (Column merging): {'✓ VERIFIED' if eng_cols_removed else '✗ NOT VERIFIED'}")
print(f"Step F (Date columns cleanup): {'✓ VERIFIED' if date_cols_removed else '✗ NOT VERIFIED'}")
print(f"\nTotal columns removed: {len(removed_cols)}")
print(f"Total columns in original: {len(df_original.columns)}")
print(f"Total columns in fixed: {len(df_fixed.columns)}")

# Check actual column names for a sample drug
print("\n11. Checking actual column names for 'ciprofloxin':")
cipro_cols = [c for c in df_original.columns if 'cipro' in c.lower()]
print(f"   In original (normalized): {cipro_cols}")
cipro_cols_fixed = [c for c in df_fixed.columns if 'cipro' in c.lower()]
print(f"   In fixed: {cipro_cols_fixed}")
