"""Detailed test to verify fix_medicines_df steps d, e, and f with proper column matching."""

import pandas as pd
from pathlib import Path
from app.modules.dataCuration.fixMedicines import fix_medicines_df
from metadata.COLUMNS import MEDICINES

# Test file path
test_file = Path(r"instance\users\aba_dot_uriel_at_gmail_dot_com\1\files\patients.csv")

print("=" * 80)
print("DETAILED TEST: fix_medicines_df - Steps D, E, F")
print("=" * 80)

# Read and prepare DataFrame
print(f"\n1. Reading file: {test_file}")
df = pd.read_csv(test_file, dtype=str)
print(f"   Shape: {df.shape}")

# Manually normalize medicine column names to lowercase (as function expects)
print("\n2. Normalizing medicine column names to match function expectations...")
column_mapping = {}
for col in df.columns:
    col_lower = col.lower()
    # Check if this is a medicine column
    is_medicine_col = any(
        drug in col_lower for drug in 
        ['cipro', 'levo', 'moxi', 'amox', 'amp', 'cefipine', 'cefazolin', 
         'azith', 'trimethoprim', 'clinda', 'metro', 'vanco', 'flucon']
    )
    if is_medicine_col:
        # Map to lowercase version
        new_name = col_lower.replace(' ', '_').replace('-', '_')
        # Handle special cases
        if 'cipropfloxin' in new_name:
            new_name = new_name.replace('cipropfloxin', 'ciprofloxin')
        column_mapping[col] = new_name

df_test = df.rename(columns=column_mapping)
print(f"   Renamed {len(column_mapping)} medicine-related columns")

# Find a patient with medicine data
print("\n3. Finding patients with medicine indicators = 1...")
patients_with_meds = []
for idx, row in df_test.iterrows():
    for drug_group in MEDICINES.values():
        for drug in drug_group:
            main_col = drug
            if main_col in df_test.columns:
                try:
                    val = pd.to_numeric(row[main_col], errors='coerce')
                    if pd.notna(val) and int(val) == 1:
                        patients_with_meds.append((idx, row['patient_id'], main_col, row.get('First_Transplant_Date', 'N/A')))
                        break
                except:
                    pass
    if len(patients_with_meds) >= 3:
        break

print(f"   Found {len(patients_with_meds)} patients with medicine indicators")
for idx, pid, drug, tx_date in patients_with_meds[:3]:
    print(f"   - Row {idx}: {pid}, drug={drug}, tx_date={tx_date}")

# Select a patient to analyze in detail
if patients_with_meds:
    test_idx, test_pid, test_drug, test_tx = patients_with_meds[0]
    print(f"\n4. Analyzing patient {test_pid} (row {test_idx}) for drug {test_drug}")
    
    test_row_before = df_test.iloc[test_idx].copy()
    transplant_date = pd.to_datetime(test_row_before['First_Transplant_Date'], format="%m/%d/%Y", errors="coerce")
    print(f"   Transplant Date: {transplant_date}")
    
    # Get medicine columns for this drug
    main_col = test_drug
    eng_col = f"{test_drug}_eng"
    
    print(f"\n   BEFORE processing:")
    print(f"   - {main_col}: {test_row_before.get(main_col, 'N/A')}")
    if eng_col in df_test.columns:
        print(f"   - {eng_col}: {test_row_before.get(eng_col, 'N/A')}")
    
    # Find date columns (by position as function does)
    cols = list(df_test.columns)
    if main_col in cols:
        main_idx = cols.index(main_col)
        start_col = cols[main_idx + 1] if main_idx + 1 < len(cols) else None
        end_col = cols[main_idx + 2] if main_idx + 2 < len(cols) else None
        print(f"   - Start date col: {start_col} = {test_row_before.get(start_col, 'N/A')}")
        print(f"   - End date col: {end_col} = {test_row_before.get(end_col, 'N/A')}")
    
    if eng_col in cols:
        eng_idx = cols.index(eng_col)
        start_eng = cols[eng_idx + 1] if eng_idx + 1 < len(cols) else None
        end_eng = cols[eng_idx + 2] if eng_idx + 2 < len(cols) else None
        if start_eng:
            print(f"   - Start date Eng col: {start_eng} = {test_row_before.get(start_eng, 'N/A')}")
        if end_eng:
            print(f"   - End date Eng col: {end_eng} = {test_row_before.get(end_eng, 'N/A')}")

# Count columns before
cols_before = set(df_test.columns)
print(f"\n5. Columns BEFORE: {len(cols_before)}")

# Run fix_medicines_df
print("\n6. Running fix_medicines_df...")
try:
    df_fixed = fix_medicines_df(df_test.copy())
    print("   ✓ Function executed successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    df_fixed = df_test.copy()

# Count columns after
cols_after = set(df_fixed.columns)
print(f"   Columns AFTER: {len(cols_after)}")

# Compare columns
removed = cols_before - cols_after
added = cols_after - cols_before

print(f"\n7. COLUMN CHANGES:")
print(f"   Removed: {len(removed)} columns")
print(f"   Added: {len(added)} columns")

# STEP D: Peri-transplant filtering verification
print("\n" + "=" * 80)
print("STEP D VERIFICATION: Peri-transplant filtering")
print("=" * 80)

if patients_with_meds:
    test_idx, test_pid, test_drug, _ = patients_with_meds[0]
    row_before = df_test.iloc[test_idx]
    row_after = df_fixed.iloc[test_idx]
    transplant = pd.to_datetime(row_before['First_Transplant_Date'], format="%m/%d/%Y", errors="coerce")
    
    main_col = test_drug
    eng_col = f"{test_drug}_eng"
    
    # Get date columns
    cols = list(df_test.columns)
    main_idx = cols.index(main_col) if main_col in cols else -1
    start_col = cols[main_idx + 1] if main_idx >= 0 and main_idx + 1 < len(cols) else None
    end_col = cols[main_idx + 2] if main_idx >= 0 and main_idx + 2 < len(cols) else None
    
    if start_col and end_col and pd.notna(transplant):
        start_date = pd.to_datetime(row_before.get(start_col), format="%m/%d/%Y", errors="coerce")
        end_date = pd.to_datetime(row_before.get(end_col), format="%m/%d/%Y", errors="coerce")
        
        print(f"\nPatient {test_pid}, Drug: {test_drug}")
        print(f"  Transplant: {transplant.date()}")
        if pd.notna(start_date):
            print(f"  Start: {start_date.date()}")
        if pd.notna(end_date):
            print(f"  End: {end_date.date()}")
        
        # Check window
        if pd.notna(start_date) and pd.notna(end_date):
            days_before = (transplant - start_date).days
            days_after = (end_date - transplant).days
            print(f"  Days before transplant: {days_before}")
            print(f"  Days after transplant: {days_after}")
            
            in_window = (days_before >= 0 and days_before <= 10) and (days_after >= 0 and days_after <= 10)
            print(f"  Within 10-day window: {in_window}")
            
            val_before = pd.to_numeric(row_before.get(main_col, 0), errors='coerce')
            val_after = pd.to_numeric(row_after.get(main_col, 0), errors='coerce')
            print(f"  Indicator BEFORE: {val_before}")
            print(f"  Indicator AFTER: {val_after}")
            
            if in_window and val_before == 1:
                if val_after == 0:
                    print(f"  ✓ STEP D VERIFIED: Indicator correctly set to 0")
                else:
                    print(f"  ✗ STEP D FAILED: Indicator should be 0 but is {val_after}")
            else:
                print(f"  - Not in window or indicator was 0, no change expected")

# STEP E: Column merging verification
print("\n" + "=" * 80)
print("STEP E VERIFICATION: Column merging")
print("=" * 80)

eng_cols_removed = [c for c in removed if c.endswith('_eng') and not any(x in c.lower() for x in ['start', 'end', 'date'])]
print(f"\n_Eng indicator columns removed: {len(eng_cols_removed)}")
if eng_cols_removed:
    print("  Removed columns:")
    for col in sorted(eng_cols_removed)[:10]:
        print(f"    - {col}")
    print(f"  ✓ STEP E VERIFIED: {len(eng_cols_removed)} _Eng columns removed")
else:
    print("  ✗ STEP E NOT VERIFIED: No _Eng columns were removed")

# Check merged values
print("\nChecking merged values (OR logic):")
for drug_group in MEDICINES.values():
    for drug in drug_group:
        main_col = drug
        eng_col = f"{drug}_eng"
        if main_col in df_test.columns and main_col in df_fixed.columns:
            # Check a few rows
            for idx in range(min(5, len(df_test))):
                orig_main = pd.to_numeric(df_test.iloc[idx].get(main_col, 0), errors='coerce') or 0
                orig_eng = pd.to_numeric(df_test.iloc[idx].get(eng_col, 0), errors='coerce') if eng_col in df_test.columns else 0
                fixed_main = pd.to_numeric(df_fixed.iloc[idx].get(main_col, 0), errors='coerce') or 0
                expected = 1 if (orig_main == 1 or orig_eng == 1) else 0
                if orig_main != fixed_main or orig_eng != 0:
                    print(f"  {main_col} row {idx}: main={orig_main}, eng={orig_eng}, merged={fixed_main}, expected={expected} {'✓' if fixed_main == expected else '✗'}")

# STEP F: Date columns cleanup
print("\n" + "=" * 80)
print("STEP F VERIFICATION: Date columns cleanup")
print("=" * 80)

date_cols_removed = [c for c in removed if any(x in c.lower() for x in ['start', 'end']) and any(x in c.lower() for x in ['date', 'eng'])]
print(f"\nDate columns removed: {len(date_cols_removed)}")
if date_cols_removed:
    print("  Removed columns:")
    for col in sorted(date_cols_removed)[:20]:
        print(f"    - {col}")
    if len(date_cols_removed) > 20:
        print(f"    ... and {len(date_cols_removed) - 20} more")
    print(f"  ✓ STEP F VERIFIED: {len(date_cols_removed)} date columns removed")
else:
    print("  ✗ STEP F NOT VERIFIED: No date columns were removed")

# Final summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Step D (Peri-transplant filtering): {'✓ VERIFIED' if patients_with_meds and '✓' in str(locals().get('in_window', '')) else '? Check output above'}")
print(f"Step E (Column merging): {'✓ VERIFIED' if eng_cols_removed else '✗ NOT VERIFIED'}")
print(f"Step F (Date cleanup): {'✓ VERIFIED' if date_cols_removed else '✗ NOT VERIFIED'}")
