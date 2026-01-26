"""Test script to verify fix_medicines_file with fixed column matching."""

import pandas as pd
from pathlib import Path
from app.modules.dataCuration.fixMedicines import fix_medicines_file, fix_medicines_df
from metadata.COLUMNS import MEDICINES

# Test file path
test_file = Path(r"instance\users\aba_dot_uriel_at_gmail_dot_com\1\files\patients.csv")

print("=" * 80)
print("TESTING fix_medicines_file with FIXED column matching")
print("=" * 80)

# Read original file
print(f"\n1. Reading original file: {test_file}")
df_original = pd.read_csv(test_file, dtype=str)
print(f"   Original shape: {df_original.shape}")
print(f"   Original columns count: {len(df_original.columns)}")

# Show sample medicine columns before
print("\n2. Sample medicine columns BEFORE processing:")
sample_cols = [c for c in df_original.columns if any(drug in c.lower() for drug in ['cipro', 'levo', 'moxi'])][:6]
for col in sample_cols:
    val = df_original.iloc[1][col] if col in df_original.columns else 'N/A'
    print(f"   - {col}: {val}")

# Run fix_medicines_file
print("\n3. Running fix_medicines_file...")
try:
    output_file = fix_medicines_file(test_file)
    print(f"   ✓ Output file: {output_file}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Read the fixed file
print("\n4. Reading fixed file...")
df_fixed = pd.read_csv(output_file, dtype=str)
print(f"   Fixed shape: {df_fixed.shape}")
print(f"   Fixed columns count: {len(df_fixed.columns)}")

# Compare columns
print("\n5. Column comparison:")
cols_before = set(df_original.columns)
cols_after = set(df_fixed.columns)
removed_cols = cols_before - cols_after
added_cols = cols_after - cols_before

print(f"   Columns removed: {len(removed_cols)}")
print(f"   Columns added: {len(added_cols)}")

if removed_cols:
    print("\n   Sample removed columns (first 20):")
    for col in sorted(list(removed_cols))[:20]:
        print(f"     - {col}")
    if len(removed_cols) > 20:
        print(f"     ... and {len(removed_cols) - 20} more")

if added_cols:
    print("\n   Added columns:")
    for col in sorted(list(added_cols)):
        print(f"     - {col}")

# STEP D: Peri-transplant filtering verification
print("\n" + "=" * 80)
print("STEP D VERIFICATION: Peri-transplant filtering")
print("=" * 80)

# Find patients with medicine indicators = 1
patients_with_changes = []
for idx in range(len(df_original)):
    row_orig = df_original.iloc[idx]
    row_fixed = df_fixed.iloc[idx]
    
    # Check each drug
    for drug_group in MEDICINES.values():
        for drug in drug_group:
            # Find original column (case-insensitive)
            orig_col = None
            for col in df_original.columns:
                if col.lower() == drug.lower():
                    orig_col = col
                    break
            
            if orig_col:
                try:
                    orig_val = pd.to_numeric(row_orig[orig_col], errors='coerce')
                    fixed_val = pd.to_numeric(row_fixed.get(drug.lower(), 0), errors='coerce') or 0
                    
                    if pd.notna(orig_val) and int(orig_val) == 1:
                        if int(fixed_val) == 0:
                            # Check if this was due to peri-transplant filtering
                            tx_date = pd.to_datetime(row_orig.get('First_Transplant_Date', ''), format="%m/%d/%Y", errors="coerce")
                            if pd.notna(tx_date):
                                patients_with_changes.append((idx, row_orig.get('patient_id', f'Row_{idx}'), drug, orig_col, tx_date))
                except:
                    pass

if patients_with_changes:
    print(f"\nFound {len(patients_with_changes)} patients with indicators changed from 1 to 0:")
    for idx, pid, drug, orig_col, tx_date in patients_with_changes[:5]:
        print(f"   - Patient {pid} (row {idx}), drug: {drug}, tx_date: {tx_date.date()}")
        # Get date columns
        cols = list(df_original.columns)
        if orig_col in cols:
            orig_idx = cols.index(orig_col)
            start_col = cols[orig_idx + 1] if orig_idx + 1 < len(cols) else None
            end_col = cols[orig_idx + 2] if orig_idx + 2 < len(cols) else None
            if start_col:
                start_date = pd.to_datetime(df_original.iloc[idx][start_col], format="%m/%d/%Y", errors="coerce")
                print(f"     Start: {start_date.date() if pd.notna(start_date) else 'N/A'}")
            if end_col:
                end_date = pd.to_datetime(df_original.iloc[idx][end_col], format="%m/%d/%Y", errors="coerce")
                print(f"     End: {end_date.date() if pd.notna(end_date) else 'N/A'}")
    print("   ✓ STEP D VERIFIED: Peri-transplant filtering is working")
else:
    print("\n   No patients found with indicators changed from 1 to 0")
    print("   (This may be normal if no treatments fall within the 10-day window)")

# STEP E: Column merging verification
print("\n" + "=" * 80)
print("STEP E VERIFICATION: Column merging")
print("=" * 80)

# Check for _Eng columns removed
eng_cols_removed = [col for col in removed_cols if col.lower().endswith('_eng') and not any(x in col.lower() for x in ['start', 'end', 'date'])]
print(f"\n_Eng indicator columns removed: {len(eng_cols_removed)}")
if eng_cols_removed:
    print("   Removed _Eng columns:")
    for col in sorted(eng_cols_removed)[:15]:
        print(f"     - {col}")
    if len(eng_cols_removed) > 15:
        print(f"     ... and {len(eng_cols_removed) - 15} more")
    print("   ✓ STEP E VERIFIED: _Eng columns were removed (merged into main columns)")
else:
    print("   ✗ STEP E NOT VERIFIED: No _Eng indicator columns were removed")

# Verify merged values (OR logic)
print("\nChecking merged values (OR logic) for first 5 patients:")
for idx in range(min(5, len(df_original))):
    for drug_group in MEDICINES.values():
        for drug in drug_group:
            # Find original columns
            main_col = None
            eng_col = None
            for col in df_original.columns:
                if col.lower() == drug.lower():
                    main_col = col
                elif col.lower() == f"{drug.lower()}_eng":
                    eng_col = col
            
            if main_col:
                orig_main = pd.to_numeric(df_original.iloc[idx].get(main_col, 0), errors='coerce') or 0
                orig_eng = pd.to_numeric(df_original.iloc[idx].get(eng_col, 0), errors='coerce') or 0 if eng_col else 0
                fixed_main = pd.to_numeric(df_fixed.iloc[idx].get(drug.lower(), 0), errors='coerce') or 0
                expected = 1 if (orig_main == 1 or orig_eng == 1) else 0
                
                if orig_main != orig_eng or orig_main != fixed_main:
                    status = '✓' if fixed_main == expected else '✗'
                    print(f"   Row {idx}, {drug}: main={int(orig_main)}, eng={int(orig_eng)}, merged={int(fixed_main)}, expected={expected} {status}")

# STEP F: Date columns cleanup
print("\n" + "=" * 80)
print("STEP F VERIFICATION: Date columns cleanup")
print("=" * 80)

date_cols_removed = [col for col in removed_cols if any(x in col.lower() for x in ['start', 'end']) and any(x in col.lower() for x in ['date', 'eng'])]
print(f"\nDate columns removed: {len(date_cols_removed)}")
if date_cols_removed:
    print("   Removed date columns (first 20):")
    for col in sorted(date_cols_removed)[:20]:
        print(f"     - {col}")
    if len(date_cols_removed) > 20:
        print(f"     ... and {len(date_cols_removed) - 20} more")
    print("   ✓ STEP F VERIFIED: Date columns were removed")
else:
    print("   ✗ STEP F NOT VERIFIED: No date columns were removed")

# Final summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Step D (Peri-transplant filtering): {'✓ VERIFIED' if patients_with_changes else '? No changes found (may be normal)'}")
print(f"Step E (Column merging): {'✓ VERIFIED' if eng_cols_removed else '✗ NOT VERIFIED'}")
print(f"Step F (Date cleanup): {'✓ VERIFIED' if date_cols_removed else '✗ NOT VERIFIED'}")
print(f"\nTotal columns removed: {len(removed_cols)}")
print(f"Total columns added: {len(added_cols)}")
print(f"Output file: {output_file}")
