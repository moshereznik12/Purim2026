import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Validation Dashboard", layout="wide")

st.title("Validation Results Dashboard")

# Load and process data
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # The request implies 'create_date' exists. Let's assume it's a string.
    # Using errors='coerce' will turn unparseable dates into NaT (Not a Time)
    df['create_date'] = pd.to_datetime(df['create_date'], unit='s', errors='coerce')
    # Fix potential typo in data
    df['validation_result'] = df['validation_result'].replace('InValid', 'Invalid')
    return df

try:
    df = load_data('sample_data.json')
except (FileNotFoundError, KeyError, Exception) as e:
    st.error(f"Error loading or processing data: {e}")
    st.info("Please make sure 'sample_data.json' exists and contains a 'create_date' field for each record.")
    st.stop()


# Display overall stats
total = len(df)
valid_count = (df["validation_result"] == "Valid").sum()
invalid_count = total - valid_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Validations", total)
with col2:
    st.metric("Valid ✓", int(valid_count), delta=f"{(valid_count/total*100):.1f}%" if total > 0 else "0.0%")
with col3:
    st.metric("Invalid ✗", int(invalid_count), delta=f"{(invalid_count/total*100):.1f}%" if total > 0 else "0.0%")

if invalid_count > 0:
    st.subheader("Top Error Analysis")
    invalid_df = df[df["validation_result"] == "Invalid"]
    
    # Find most frequent error
    if not invalid_df.empty and 'description' in invalid_df.columns:
        most_common_error = invalid_df["description"].mode()[0]
        error_freq = (invalid_df["description"] == most_common_error).sum()
        
        # Filter for items with the top error
        top_error_df = invalid_df[invalid_df["description"] == most_common_error]

        # Find supplier most associated with this error
        top_supplier = top_error_df["supplier"].mode()[0]
        supplier_freq = (top_error_df["supplier"] == top_supplier).sum()
        
        # Find entity most associated with this error
        top_entity = top_error_df["entity"].mode()[0]
        entity_freq = (top_error_df["entity"] == top_entity).sum()
        
        err_col1, err_col2, err_col3 = st.columns(3)
        with err_col1:
            st.metric("Most Frequent Error", most_common_error, f"{int(error_freq)} occurrences")
        with err_col2:
            st.metric("Top Supplier for Error", top_supplier, f"{int(supplier_freq)} occurrences")
        with err_col3:
            st.metric("Top Entity for Error", top_entity, f"{int(entity_freq)} occurrences")

st.divider()

# Results by supplier
st.subheader("Results by Supplier")

# Add sorting option
sort_by = st.radio(
    "Sort suppliers by:",
    ("Most Recent Activity", "Name"),
    horizontal=True,
    key='supplier_sort'
)

suppliers = df['supplier'].unique()

if sort_by == "Name":
    sorted_suppliers = sorted(suppliers)
else: # Most Recent Activity
    # Drop rows where create_date is NaT before grouping
    latest_activity = df.dropna(subset=['create_date']).groupby('supplier')['create_date'].max()
    sorted_suppliers = latest_activity.sort_values(ascending=False).index.tolist()


# Display per supplier
for supplier in sorted_suppliers:
    supplier_df = df[df['supplier'] == supplier].copy() # Use copy to avoid SettingWithCopyWarning
    
    valid_supplier = (supplier_df['validation_result'] == 'Valid').sum()
    total_supplier = len(supplier_df)
    invalid_supplier = total_supplier - valid_supplier
    
    with st.expander(f"📦 {supplier} ({valid_supplier}/{total_supplier} passed)"):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Valid", int(valid_supplier))
        with col2:
            st.metric("Invalid", int(invalid_supplier))
        
        # New Feature: Trend line
        st.write("#### Validation Trend")
        # Ensure create_date is sorted for the line chart
        supplier_df.sort_values('create_date', inplace=True)
        
        # Resample data by day to create a trend line
        # Set create_date as index for resampling
        trend_data = supplier_df.set_index('create_date')
        
        # Create columns for valid/invalid counts
        trend_data['valid_count'] = (trend_data['validation_result'] == 'Valid').astype(int)
        trend_data['invalid_count'] = (trend_data['validation_result'] == 'Invalid').astype(int)
        
        # Resample by day and sum counts. Use 'D' for day.
        daily_summary = trend_data[['valid_count', 'invalid_count']].resample('D').sum()
        
        if not daily_summary.empty:
            # Rename columns for clarity in the chart legend
            daily_summary.rename(columns={'valid_count': 'Valid', 'invalid_count': 'Invalid'}, inplace=True)
            st.line_chart(daily_summary)
        else:
            st.info("No date information available to plot a trend line.")

        # Show invalid results for this supplier
        invalid_items_df = supplier_df[supplier_df["validation_result"] == "Invalid"]
        if not invalid_items_df.empty:
            st.warning("Failed Validations:")
            # Using st.dataframe is often cleaner for tabular data
            display_df = invalid_items_df[['create_date', 'entity', 'description', 'id']].copy()
            display_df['create_date'] = display_df['create_date'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(display_df.sort_values('create_date', ascending=False), use_container_width=True)