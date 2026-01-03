import pandas as pd

# UPDATE THIS WITH YOUR EXACT EXCEL FILENAME (copy from folder, including extension)
excel_file = "Stationwise Manpower & Multi-Skilled Deplyoment For Dasboardx.xlsx"

# Read from "Master Sheet", skipping the first 3 rows (header starts at row 4, index 3)
df_raw = pd.read_excel(excel_file, sheet_name="Master Sheet", header=3)

# Drop completely empty rows
df_raw = df_raw.dropna(how='all').reset_index(drop=True)

# Display column names for debugging
print("Columns in DataFrame:")
print(df_raw.columns.tolist())
print(f"\nNumber of columns: {len(df_raw.columns)}")
print(f"\nFirst few rows of raw data:")
print(df_raw.head().to_string())

data = []

for _, row in df_raw.iterrows():
    # Main operator details
    # Column indices after header=3:
    # Column A (Area) -> index 0
    # Column B (Stations) -> index 1
    # Column E (NAME) -> index 3
    # Column F (ID) -> index 4
    
    area = row.iloc[0] if pd.notna(row.iloc[0]) else ''      # Column A - Area
    station = row.iloc[1] if pd.notna(row.iloc[1]) else ''   # Column B - Stations
    main_name = row.iloc[3] if len(row) > 3 and pd.notna(row.iloc[3]) else ''  # Column E - NAME
    main_id = row.iloc[4] if len(row) > 4 and pd.notna(row.iloc[4]) else ''    # Column F - ID

    # Skip if no main operator (empty row)
    if pd.isna(main_name) and pd.isna(main_id):
        continue

    entry = {
        'Area': area,
        'Station': station,
        'Name': str(main_name) if pd.notna(main_name) else '',
        'ID': str(main_id) if pd.notna(main_id) else '',
        'Multi_OP1_Name': '',
        'Multi_OP1_ID': '',
        'Multi_OP2_Name': '',
        'Multi_OP2_ID': '',
        'Multi_OP3_Name': '',
        'Multi_OP3_ID': '',
        'Multi_OP4_Name': '',
        'Multi_OP4_ID': '',
        'Multi_OP5_Name': '',
        'Multi_OP5_ID': '',
        'Multi_OP6_Name': '',
        'Multi_OP6_ID': '',
        'Multi_OP7_Name': '',
        'Multi_OP7_ID': ''
    }

    # Multi-Skill OP1: Name from column I (index 8), ID from column J (index 9)
    if len(row) > 9:
        entry['Multi_OP1_Name'] = str(row.iloc[8]) if pd.notna(row.iloc[8]) else ''
        entry['Multi_OP1_ID'] = str(row.iloc[9]) if pd.notna(row.iloc[9]) else ''

    # Multi-Skill OP2: Name from column N (index 13), ID from column O (index 14)
    if len(row) > 14:
        entry['Multi_OP2_Name'] = str(row.iloc[13]) if pd.notna(row.iloc[13]) else ''
        entry['Multi_OP2_ID'] = str(row.iloc[14]) if pd.notna(row.iloc[14]) else ''

    # Multi-Skill OP3: Name from column S (index 18), ID from column T (index 19)
    if len(row) > 19:
        entry['Multi_OP3_Name'] = str(row.iloc[18]) if pd.notna(row.iloc[18]) else ''
        entry['Multi_OP3_ID'] = str(row.iloc[19]) if pd.notna(row.iloc[19]) else ''

    # Multi-Skill OP4: Name from column X (index 23), ID from column Y (index 24)
    if len(row) > 24:
        entry['Multi_OP4_Name'] = str(row.iloc[23]) if pd.notna(row.iloc[23]) else ''
        entry['Multi_OP4_ID'] = str(row.iloc[24]) if pd.notna(row.iloc[24]) else ''

    # Multi-Skill OP5: Name from column AC (index 28), ID from column AD (index 29)
    if len(row) > 29:
        entry['Multi_OP5_Name'] = str(row.iloc[28]) if pd.notna(row.iloc[28]) else ''
        entry['Multi_OP5_ID'] = str(row.iloc[29]) if pd.notna(row.iloc[29]) else ''

    # Multi-Skill OP6: Name from column AH (index 33), ID from column AI (index 34)
    if len(row) > 34:
        entry['Multi_OP6_Name'] = str(row.iloc[33]) if pd.notna(row.iloc[33]) else ''
        entry['Multi_OP6_ID'] = str(row.iloc[34]) if pd.notna(row.iloc[34]) else ''

    # Multi-Skill OP7: Name from column AM (index 38), ID from column AN (index 39)
    if len(row) > 39:
        entry['Multi_OP7_Name'] = str(row.iloc[38]) if pd.notna(row.iloc[38]) else ''
        entry['Multi_OP7_ID'] = str(row.iloc[39]) if pd.notna(row.iloc[39]) else ''

    data.append(entry)

# Create final DataFrame
final_df = pd.DataFrame(data)

# Final clean: remove rows where main Name and ID are both empty
final_df = final_df[(final_df['Name'] != '') | (final_df['ID'] != '')]

# Save to CSV
output_csv = "current_employees.csv"
final_df.to_csv(output_csv, index=False)

print(f"\nSUCCESS! '{output_csv}' generated with {len(final_df)} operators.")
print(f"\nColumns ({len(final_df.columns)} total):")
print(final_df.columns.tolist())
print(f"\nFirst 10 rows:")
print(final_df.head(10).to_string(index=False))
print(f"\nSample rows with multi-skill backups:")
sample = final_df[(final_df['Multi_OP1_Name'] != '') | 
                  (final_df['Multi_OP2_Name'] != '') | 
                  (final_df['Multi_OP3_Name'] != '')].head(5)
print(sample.to_string(index=False) if len(sample) > 0 else "No multi-skill operators found")