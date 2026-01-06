import streamlit as st
import pandas as pd
import os
import altair as alt

st.set_page_config(page_title="OP Management", page_icon="👷", layout="wide")

st.markdown("""
    <style>
        .block-container {padding: 0.2rem 1rem !important;}
        .main > div {padding: 0;}
        header, footer {display: none !important;}
        #MainMenu {display: none !important;}
        h1 {
            font-size: 1.6rem;
            margin: 0.1rem 0 0.3rem 0;
            font-weight: 700;
            color: #1a237e;
            text-align: center;
        }
        .kpi-card {
            background: white;
            border-radius: 6px;
            padding: 0.4rem;
            margin: 0.2rem 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e0e0;
        }
        .kpi-value {
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin: 0.1rem 0;
            font-family: 'Segoe UI', 'Roboto', monospace;
        }
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 600;
            text-align: center;
            color: #546e7a;
            margin-bottom: 0.2rem;
        }
        .kpi-change {
            font-size: 0.7rem;
            text-align: center;
            font-weight: 500;
            padding: 1px 4px;
            border-radius: 8px;
            display: inline-block;
        }
        .gender-card {
            background: white;
            border-radius: 6px;
            padding: 0.5rem;
            margin: 0.3rem 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e0e0;
        }
        .gender-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.2rem;
            margin-top: 0.4rem;
            text-align: center;
        }
        .gender-stat-value {
            font-size: 1rem;
            font-weight: 700;
            display: block;
        }
        .gender-stat-label {
            font-size: 0.65rem;
            color: #666;
            display: block;
        }
        .custom-legend {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 5px;
            margin: 0.3rem 0;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 3px;
            font-size: 0.7rem;
            font-weight: 500;
        }
        .legend-color {
            width: 10px;
            height: 10px;
            border-radius: 2px;
        }
        .section-card {
            background: white;
            border-radius: 6px;
            padding: 0.5rem;
            margin: 0.3rem 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e0e0;
        }
        .date-header {
            text-align: center;
            font-size: 0.8rem;
            color: #546e7a;
            font-weight: 500;
            margin: 0.1rem 0 0.5rem 0;
            padding: 0.3rem;
            background: #f5f5f5;
            border-radius: 4px;
        }
        div[data-testid="column"] {
            padding: 0.1rem !important;
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.1rem !important;
        }
        .stMarkdown {
            margin-bottom: 0.1rem !important;
        }
        .vega-embed {
            padding: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Files
current_file = "current_employees.csv"
absent_file = "actual_absent_manpower.csv"

if not os.path.exists(current_file) or not os.path.exists(absent_file):
    st.error("Missing CSV files! Run generator scripts first.")
    st.stop()

# Read ID columns as strings to prevent float issues
id_columns = ['ID', 'Multi_OP1_ID', 'Multi_OP2_ID', 'Multi_OP3_ID']
dtype_dict = {col: str for col in id_columns}

current_df = pd.read_csv(current_file, dtype=dtype_dict)
absent_df = pd.read_csv(absent_file, dtype=dtype_dict)

# Clean IDs: remove any trailing .0, .00, etc. and 'nan'
for col in id_columns:
    if col in current_df.columns:
        current_df[col] = current_df[col].str.strip().str.replace(r'\.0+$', '', regex=True).replace({'nan': '', 'NaN': ''})
    if col in absent_df.columns:
        absent_df[col] = absent_df[col].str.strip().str.replace(r'\.0+$', '', regex=True).replace({'nan': '', 'NaN': ''})

current_df = current_df[current_df['Area'].isin(['CG', 'Offline', 'Assy', 'Testing', 'Packout'])]
absent_df = absent_df[absent_df['Area'].isin(['CG', 'Offline', 'Assy', 'Testing', 'Packout'])]

total = len(current_df[current_df['ID'] != ''])
absent_count = len(absent_df)
present_count = total - absent_count

MALE_COUNT = 22
FEMALE_COUNT = 118

stages = ['CG', 'Offline', 'Assy', 'Testing', 'Packout']
stage_data = []

for stage in stages:
    total_in_stage = len(current_df[(current_df['Area'] == stage) & (current_df['ID'] != '')])
    absent_in_stage_df = absent_df[absent_df['Area'] == stage]
    absent_in_stage = len(absent_in_stage_df)
    present_in_stage = total_in_stage - absent_in_stage

    absent_with_backup = 0
    absent_without_backup = 0
    for _, row in absent_in_stage_df.iterrows():
        has_backup = any(pd.notna(row[col]) and str(row[col]).strip() != '' 
                        for col in ['Multi_OP1_Name', 'Multi_OP2_Name', 'Multi_OP3_Name'])
        if has_backup:
            absent_with_backup += 1
        else:
            absent_without_backup += 1

    present_pct = round((present_in_stage / total_in_stage) * 100) if total_in_stage > 0 else 0

    stage_data.append({
        'Stage': stage,
        'P': present_in_stage,
        'W/B': absent_with_backup,
        'N/B': absent_without_backup,
        'Present %': present_pct
    })

stage_df = pd.DataFrame(stage_data)

# Attrition
attrition_data = [
    {'Month': 'Sep', 'Total Required MP': 215, 'Present MP': 211, 'Attrition': 10, 'Attrition %': 5.0},
    {'Month': 'Oct', 'Total Required MP': 215, 'Present MP': 227, 'Attrition': 9, 'Attrition %': 4.0},
    {'Month': 'Nov', 'Total Required MP': 215, 'Present MP': 214, 'Attrition': 12, 'Attrition %': 6.0},
    {'Month': 'Dec', 'Total Required MP': 215, 'Present MP': 200, 'Attrition': 12, 'Attrition %': 6.0},
]
attrition_df = pd.DataFrame(attrition_data)

# Header
st.markdown("<h1>👷 OP Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<div class='date-header'>📅 January 06, 2026 | CG • Offline • Assy • Testing • Packout</div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 3], gap="small")

with left_col:
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>TOTAL</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value' style='color:#1E88E5;'>{total}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
   
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>PRESENT</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value' style='color:#43A047;'>{present_count}</div>", unsafe_allow_html=True)
    present_pct_display = round(present_count/total*100, 1) if total > 0 else 0
    st.markdown(f"<div class='kpi-change' style='background-color:#E8F5E9; color:#2E7D32;'>↑{present_pct_display}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
   
    st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
    st.markdown("<div class='kpi-label'>ABSENT</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kpi-value' style='color:#E53935;'>{absent_count}</div>", unsafe_allow_html=True)
    absent_pct_display = round(absent_count/total*100, 1) if total > 0 else 0
    st.markdown(f"<div class='kpi-change' style='background-color:#FFEBEE; color:#C62828;'>↓{absent_pct_display}%</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
   
    st.markdown("<div class='gender-card'>", unsafe_allow_html=True)
    st.markdown("### 👥 Gender")
    gender_total = MALE_COUNT + FEMALE_COUNT
    if gender_total > 0:
        male_pct = round(MALE_COUNT/gender_total*100, 1)
        female_pct = round(FEMALE_COUNT/gender_total*100, 1)
        gender_data = pd.DataFrame({'Gender': ['Male', 'Female'], 'Count': [MALE_COUNT, FEMALE_COUNT]})
        pie_chart = alt.Chart(gender_data).mark_arc().encode(
            theta='Count:Q',
            color=alt.Color('Gender:N', scale=alt.Scale(domain=['Male', 'Female'], range=['#1E88E5', '#EC407A']), legend=None)
        ).properties(height=100, width=100)
        st.altair_chart(pie_chart, use_container_width=False, theme=None)
        st.markdown("""
        <div class="custom-legend">
            <div class="legend-item"><div class="legend-color" style="background-color: #1E88E5;"></div><span>M</span></div>
            <div class="legend-item"><div class="legend-color" style="background-color: #EC407A;"></div><span>F</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='gender-stats'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div><span class='gender-stat-value'>{gender_total}</span><span class='gender-stat-label'>Total</span></div>
        <div><span class='gender-stat-value'>{MALE_COUNT}</span><span class='gender-stat-label'>M({male_pct}%)</span></div>
        <div><span class='gender-stat-value'>{FEMALE_COUNT}</span><span class='gender-stat-label'>F({female_pct}%)</span></div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown("### 📊 Attendance")
    
    chart_col, table_col = st.columns([2.3, 1], gap="medium")
    
    with chart_col:
        chart_data = []
        for _, row in stage_df.iterrows():
            chart_data.append({'Stage': row['Stage'], 'Status': 'Present', 'Count': row['P'], 'Order': 1})
            chart_data.append({'Stage': row['Stage'], 'Status': 'w/Backup', 'Count': row['W/B'], 'Order': 2})
            chart_data.append({'Stage': row['Stage'], 'Status': 'No Backup', 'Count': row['N/B'], 'Order': 3})
        chart_df = pd.DataFrame(chart_data)
        
        chart = alt.Chart(chart_df).mark_bar(size=18).encode(
            x=alt.X('Stage:N', title=None, sort=stages, axis=alt.Axis(labelFontSize=9)),
            y=alt.Y('Count:Q', title=None, axis=alt.Axis(labelFontSize=8)),
            color=alt.Color('Status:N',
                scale=alt.Scale(domain=['Present', 'w/Backup', 'No Backup'],
                                range=['#43A047', '#FF9800', '#E53935']),
                legend=alt.Legend(title=None, orient='top', titleFontSize=9, labelFontSize=8),
                sort=['Present', 'w/Backup', 'No Backup']
            ),
            order=alt.Order('Order:Q', sort='ascending'),
            tooltip=['Stage', 'Status', 'Count']
        ).properties(height=220)
        
        st.altair_chart(chart, use_container_width=True, theme=None)
    
    with table_col:
        summary_table = stage_df[['Stage', 'P', 'W/B', 'N/B', 'Present %']].copy()
        summary_table['Present %'] = summary_table['Present %'].astype(str) + '%'
        summary_table = summary_table.rename(columns={'Present %': '%'}).reset_index(drop=True)
        
        def color_summary_row(row):
            pct_val = int(row['%'].replace('%', ''))
            nb = row['N/B']
            wb = row['W/B']
            
            if pct_val == 100:
                bg = '#E8F5E9'; color = '#2E7D32'
            elif nb > 0:
                bg = '#FFEBEE'; color = '#C62828'
            elif wb > 0:
                bg = '#FFF3E0'; color = '#EF6C00'
            else:
                bg = '#E8F5E9'; color = '#2E7D32'
                
            return [f'background-color: {bg}; color: {color}; font-weight: bold; text-align: center;'] * 5
        
        styled_summary = summary_table.style \
            .apply(color_summary_row, axis=1) \
            .set_table_styles([
                {'selector': 'th', 'props': 'font-size: 0.65rem !important; padding: 3px 5px !important; text-align: center; background: #f8f9fa;'},
                {'selector': 'td', 'props': 'font-size: 0.70rem !important; padding: 3px 5px !important; text-align: center;'}
            ]) \
            .hide(axis="index")
        
        st.dataframe(styled_summary, use_container_width=True, hide_index=True, height=200)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Attrition
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    attr_col1, attr_col2 = st.columns([2, 1], gap="small")
    with attr_col1:
        st.markdown("### 📈 Attrition Trend")
        month_order = ['Sep', 'Oct', 'Nov', 'Dec']
        line_chart = alt.Chart(attrition_df).mark_line(color='#E53935', strokeWidth=2).encode(
            x=alt.X('Month:N', title=None, sort=month_order, axis=alt.Axis(labelFontSize=9)),
            y=alt.Y('Attrition %:Q', title=None, axis=alt.Axis(labelFontSize=8), scale=alt.Scale(domain=[0, 7])),
            tooltip=['Month', 'Attrition %']
        ).properties(height=120)
        points = alt.Chart(attrition_df).mark_circle(color='#E53935', size=40).encode(
            x=alt.X('Month:N', sort=month_order),
            y='Attrition %:Q'
        )
        st.altair_chart(line_chart + points, use_container_width=True, theme=None)
   
    with attr_col2:
        st.markdown("#### Data")
        attr_table = attrition_df[['Month', 'Present MP', 'Attrition %']].copy()
        attr_table['Attrition %'] = attr_table['Attrition %'].apply(lambda x: f"{x:.1f}%")
        attr_table.columns = ['Mon', 'Pres', 'Attr%']
        def color_attr(val):
            if isinstance(val, str) and '%' in val:
                pct = float(val.replace('%', ''))
                if pct <= 3: return 'background-color:#C8E6C9;color:#000;'
                elif pct <= 4: return 'background-color:#FFF9C4;color:#000;'
                else: return 'background-color:#FFCDD2;color:#000;'
            return ''
        styled_attr = attr_table.style.applymap(color_attr, subset=['Attr%']).set_table_styles([
            {'selector': 'th', 'props': 'font-size:0.6rem;padding:1px 2px;text-align:center;'},
            {'selector': 'td', 'props': 'font-size:0.6rem;padding:1px 2px;text-align:center;'}
        ])
        st.dataframe(styled_attr, use_container_width=True, hide_index=True, height=140)
    st.markdown("</div>", unsafe_allow_html=True)
   
    # Absent Operators - FINAL VERSION: Clean IDs, correct columns
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    if absent_count > 0:
        st.markdown(f"### 🚨 Absent Operators ({absent_count})")
        display_df = absent_df.copy()
        
        # Rename backup columns
        display_df = display_df.rename(columns={
            "Area": "Area",
            "Station": "Station",
            "Name": "Name",
            "ID": "ID",
            "Multi_OP1_Name": "B1",
            "Multi_OP1_ID": "B1 ID",
            "Multi_OP2_Name": "B2",
            "Multi_OP2_ID": "B2 ID",
            "Multi_OP3_Name": "B3",
            "Multi_OP3_ID": "B3 ID"
        })
        
        # Final safety: remove any trailing .0 from backup IDs
        for col in ['B1 ID', 'B2 ID', 'B3 ID']:
            display_df[col] = display_df[col].str.replace(r'\.0+$', '', regex=True)
        
        # Select and order columns exactly as requested
        columns_order = ['Area', 'Station', 'Name', 'ID', 'B1', 'B1 ID', 'B2', 'B2 ID', 'B3', 'B3 ID']
        display_df = display_df[columns_order]
        
        # Clean display: empty cells appear blank
        display_df = display_df.fillna('')
        
        styled_display_df = display_df.style \
            .set_table_styles([
                {'selector': 'th', 'props': 'font-size: 0.65rem !important; padding: 3px 4px !important; text-align: center !important;'},
                {'selector': 'td', 'props': 'font-size: 0.65rem !important; padding: 2px 4px !important; text-align: center !important;'},
                {'selector': 'td:nth-child(3), td:nth-child(5), td:nth-child(7), td:nth-child(9)', 'props': 'text-align: left !important;'}  # Name + B1/B2/B3 names left-aligned
            ])
        
        st.dataframe(styled_display_df, use_container_width=True, hide_index=True, height=min(400, 40 + (absent_count * 25)))
        
        # Backup summary
        backup_available = len(absent_df[
            (absent_df['Multi_OP1_Name'].notna() & absent_df['Multi_OP1_Name'].str.strip() != '') |
            (absent_df['Multi_OP2_Name'].notna() & absent_df['Multi_OP2_Name'].str.strip() != '') |
            (absent_df['Multi_OP3_Name'].notna() & absent_df['Multi_OP3_Name'].str.strip() != '')
        ])
        backup_not_available = absent_count - backup_available
        
        st.markdown(f"""
        <div style='font-size:0.7rem; margin-top:5px;'>
            <b>Backup Summary:</b>
            <span style='color:#2E7D32;'>{backup_available} with backup</span> •
            <span style='color:#C62828;'>{backup_not_available} without backup</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style='font-size:0.65rem; color:#666; margin-top:3px;'>
            <b>Backup Operators:</b> B1 = Primary, B2 = Secondary, B3 = Tertiary
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 🎉 All Operators Present!")
        st.markdown("<div style='text-align:center;padding:0.5rem;background-color:#E8F5E9;border-radius:4px;font-size:0.8rem;'>✅ Perfect Attendance Today</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center;font-size:0.7rem;color:#666;margin-top:0.5rem;'>OP Dashboard • Full backup details shown</div>", unsafe_allow_html=True)