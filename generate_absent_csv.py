import pandas as pd
import os
import sys

# ==================== CONFIGURATION ====================
CURRENT_CSV = "current_employees.csv"          # Your enhanced CSV with multi-skills
ABSENT_EXCEL = "absentReport 2026-01-05.xlsx"  # Absent report
OUTPUT_CSV = "actual_absent_manpower.csv"      # Output with full details
# =====================================================

print("=== Compal Actual Absent Manpower Generator ===")
print("Working folder:", os.getcwd())
print()

# Load current employees
if not os.path.exists(CURRENT_CSV):
    print(f"ERROR: '{CURRENT_CSV}' not found! Generate it first from Excel.")
    sys.exit(1)

print(f"Loading '{CURRENT_CSV}'...")
current_df = pd.read_csv(CURRENT_CSV)

# Critical fix: Clean ID by removing '.0' and convert to string
current_df['ID'] = current_df['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Remove invalid rows
current_df = current_df[current_df['ID'] != '']
current_df = current_df[current_df['ID'] != 'nan']

total_operators = len(current_df)
print(f"Loaded {total_operators} main operators")
print("Sample cleaned main IDs:", sorted(current_df['ID'].unique())[:15])
print()

# Load absent report
if not os.path.exists(ABSENT_EXCEL):
    print(f"ERROR: '{ABSENT_EXCEL}' not found!")
    sys.exit(1)

print(f"Loading '{ABSENT_EXCEL}'...")
absent_df = pd.read_excel(ABSENT_EXCEL, dtype=str)  # All as string
print(f"Report rows: {len(absent_df)}")

# Find USER ID column
id_col = None
for col in absent_df.columns:
    if 'USER' in str(col).upper() and 'ID' in str(col).upper():
        id_col = col
        break
if id_col is None:
    print("ERROR: USER ID column not found!")
    sys.exit(1)
print(f"Using '{id_col}' for absent IDs")

# Clean and filter absent
absent_df[id_col] = absent_df[id_col].str.strip()
absent_only = absent_df[absent_df['STATUS'] == 'A-A']
absent_ids = set(absent_only[id_col])
print(f"Absent in report: {len(absent_ids)}")
print("Sample absent IDs:", sorted(list(absent_ids))[:15])
print()

# Match main IDs
matched_count = len(set(current_df['ID']) & absent_ids)
print(f"MATCHED: {matched_count} absent main operators!\n")

if matched_count > 0:
    print("Matched Main IDs:", sorted(set(current_df['ID']) & absent_ids))

# Generate absent list with ALL columns (including multi-skills)
absent_final = current_df[current_df['ID'].isin(absent_ids)].copy()
absent_final.sort_values(by=['Area', 'Station', 'Name'], inplace=True)
absent_final.reset_index(drop=True, inplace=True)

# Save
absent_final.to_csv(OUTPUT_CSV, index=False)
print(f"\nSUCCESS! '{OUTPUT_CSV}' generated with {matched_count} rows (full details + backups)")
print("Path:", os.path.abspath(OUTPUT_CSV))

# Summary
present_count = total_operators - matched_count
print("\n" + "="*60)
print("ATTENDANCE SUMMARY - December 17, 2025")
print("="*60)
print(f"Total Main Operators : {total_operators}")
print(f"Absent               : {matched_count}")
print(f"Present              : {present_count}")
print(f"Attendance Rate      : {round(present_count / total_operators * 100, 1) if total_operators else 0}%")

if matched_count > 0:
    print("\nAbsent Operators (with multi-skill backups):")
    print(absent_final.to_string(index=False))

print("\n=== DONE! Refresh folder and check the CSV ===")