import streamlit as st
from utils import get_osdk_client

st.set_page_config(page_title="Validation Dashboard", layout="wide")
st.title("Validation Results Dashboard (OSDK Powered)")

# --- DATA LOADING VIA OSDK MOCK ---
try:
    client = get_osdk_client('sample_data.json')
    # Access the OSDK ObjectSet
    ValidationRecord = client.ontology.objects.ValidationRecord
    
    # Get the full dataframe for the overview
    df = ValidationRecord.to_pandas()
except Exception as e:
    st.error(f"Error initializing OSDK Mock: {e}")
    st.stop()

# --- OVERALL STATS ---
total = ValidationRecord.count()
valid_count = ValidationRecord.where(
    ValidationRecord.object_type.validation_result.eq("Valid")
).count()
invalid_count = total - valid_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Validations", total)
with col2:
    st.metric("Valid ✓", int(valid_count), delta=f"{(valid_count/total*100):.1f}%" if total > 0 else "0.0%")
with col3:
    st.metric("InValid ✗", int(invalid_count), delta=f"{(invalid_count/total*100):.1f}%" if total > 0 else "0.0%", delta_color="inverse")

# --- ERROR ANALYSIS (OSDK FILTERING) ---
if invalid_count > 0:
    st.subheader("Top Error Analysis")
    
    # Use OSDK to get only Invalid records
    invalid_oset = ValidationRecord.where(ValidationRecord.object_type.validation_result.eq("InValid"))
    invalid_df = invalid_oset.to_pandas()
    
    if not invalid_df.empty:
        most_common_error = invalid_df["description"].mode()[0]
        # Use OSDK to filter for this specific error
        top_error_oset = invalid_oset.where(ValidationRecord.object_type.description.eq(most_common_error))
        top_error_df = top_error_oset.to_pandas()
        
        err_col1, err_col2, err_col3 = st.columns(3)
        with err_col1:
            st.metric("Most Frequent Error", most_common_error, f"{top_error_oset.count()} occurrences", delta_color="grey")
        with err_col2:
            st.metric("Top Supplier for Error", top_error_df["supplier"].mode()[0])
        with err_col3:
            st.metric("Top Entity for Error", top_error_df["entity"].mode()[0])

st.divider()

# --- SUPPLIER SECTION ---
st.subheader("Results by Supplier")

suppliers = df['supplier'].unique()
sort_by = st.radio("Sort suppliers by:", ("Most Recent Activity", "Name"), horizontal=True)

if sort_by == "Name":
    sorted_suppliers = sorted(suppliers)
else:
    latest_activity = df.groupby('supplier')['create_date'].max()
    sorted_suppliers = latest_activity.sort_values(ascending=False).index.tolist()

for supplier in sorted_suppliers:
    # USE OSDK TO GET SUPPLIER-SPECIFIC OBJECT SET
    supplier_oset = ValidationRecord.where(ValidationRecord.object_type.supplier.eq(supplier))
    supplier_df = supplier_oset.to_pandas()
    
    total_s = supplier_oset.count()
    valid_s = supplier_oset.where(ValidationRecord.object_type.validation_result.eq("Valid")).count()
    
    with st.expander(f"📦 {supplier} ({valid_s}/{total_s} passed)"):
        # ... (Metric and Plotting code remains similar, but uses supplier_df)
        st.line_chart(supplier_df.set_index('create_date').resample('D').size())
        
        # Displaying Invalid Items via OSDK
        invalids = supplier_oset.where(ValidationRecord.object_type.validation_result.eq("InValid")).to_pandas()
        if not invalids.empty:
            st.dataframe(invalids[['create_date', 'entity', 'description']])