import pandas as pd
from mock_data import create_mock_osdk_client
from unittest.mock import call

# --- The Function You Want To Test ---
def get_valid_transactions(client):
    """Example logic: Filter for Transactions and return as a DataFrame."""
    return (client.ontology.objects.ValidationRecord
            .where(client.ontology.objects.ValidationRecord.object_type.entity.eq("Transaction"))
            .to_pandas())

# --- The Tests ---
def test_get_valid_transactions_filtering():
    # Setup mock data
    mock_data = [
        {"id": "1", "entity": "Transaction", "create_date": pd.Timestamp(2026, 1, 1)},
        {"id": "2", "entity": "Customer", "create_date": pd.Timestamp(2026, 1, 2)},
    ]
    
    # Initialize mock client
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    
    # Execute the function
    result_df = get_valid_transactions(client)
    
    # Assertions
    assert len(result_df) == 1
    assert result_df.iloc[0]['entity'] == "Transaction"
    assert result_df.iloc[0]['id'] == "1"

def test_empty_results_handling():
    # Setup mock data with no transactions
    mock_data = [{"id": "2", "entity": "Customer"}]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    
    result_df = get_valid_transactions(client)
    
    assert result_df.empty

def test_date_range_filtering():
    mock_data = [
        {"id": "old", "create_date": pd.Timestamp(2020, 1, 1)},
        {"id": "new", "create_date": pd.Timestamp(2026, 1, 1)},
    ]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    ValidationRecord = client.ontology.objects.ValidationRecord
    
    # Direct test of the where clause with timestamps
    cutoff = pd.Timestamp(2025, 1, 1)
    filtered = ValidationRecord.where(ValidationRecord.object_type.create_date.gt(cutoff)).to_pandas()
    
    assert len(filtered) == 1
    assert filtered.iloc[0]['id'] == "new"

    def test_supplier_grouping_logic():
        mock_data = [
            {"supplier": "Supplier A", "entity": "Transaction"},
            {"supplier": "Supplier A", "entity": "Customer"},
            {"supplier": "Supplier B", "entity": "Transaction"},
        ]
        client = create_mock_osdk_client(mock_data, "ValidationRecord")
        obj = client.ontology.objects.ValidationRecord
        
        # Run OSDK group_by
        stats = obj.group_by(obj.object_type.supplier).count()
        
        # Convert results to a dict for easy checking
        results_dict = {item['key']: item['count'] for item in stats}
        
        assert results_dict["Supplier A"] == 2
        assert results_dict["Supplier B"] == 1

# --- Tests for Complex Chained Filtering ---

def test_multi_step_filtering():
    mock_data = [
        {"entity": "Transaction", "validation_result": "Valid", "id": "1"},
        {"entity": "Transaction", "validation_result": "Invalid", "id": "2"},
        {"entity": "Customer", "validation_result": "Valid", "id": "3"},
    ]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    obj = client.ontology.objects.ValidationRecord
    
    # Chain .where() calls
    filtered = (obj.where(obj.object_type.entity.eq("Transaction"))
                   .where(obj.object_type.validation_result.eq("Valid")))
    
    results = filtered.to_pandas()
    assert len(results) == 1
    assert results.iloc[0]['id'] == "1"

# --- Tests for Actions (Writing Data) ---

def update_supplier_description(client, record_id, new_desc):
    """Function to test: It calls a Foundry Action."""
    client.ontology.actions.update_validation_desc(
        target_id=record_id, 
        description=new_desc
    )

def test_action_execution_verification():
    client = create_mock_osdk_client([], "ValidationRecord")
    
    # Execute the function that calls an action
    update_supplier_description(client, "ff9e-abc", "Verified by Mock")
    
    # Verify the action was called with the right arguments
    client.ontology.actions.update_validation_desc.assert_called_once_with(
        target_id="ff9e-abc",
        description="Verified by Mock"
    )

def test_chained_where_clauses():
    """Verify that multiple .where() calls narrow down the data correctly."""
    mock_data = [
        {"id": "1", "entity": "Transaction", "validation_result": "Valid"},
        {"id": "2", "entity": "Transaction", "validation_result": "Invalid"},
        {"id": "3", "entity": "Customer", "validation_result": "Valid"},
    ]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    vr = client.ontology.objects.ValidationRecord

    # Applying two filters
    query = (vr.where(vr.object_type.entity.eq("Transaction"))
               .where(vr.object_type.validation_result.eq("Valid")))
    
    results = query.to_pandas()
    assert len(results) == 1
    assert results.iloc[0]['id'] == "1"

# --- Test 2: Date Range Boundary (Greater than AND Less than) ---
def test_date_range_sandwich():
    """Test filtering between two timestamps."""
    mock_data = [
        {"id": "too_early", "create_date": pd.Timestamp("2025-12-31")},
        {"id": "just_right", "create_date": pd.Timestamp("2026-01-05")},
        {"id": "too_late", "create_date": pd.Timestamp("2026-02-01")},
    ]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    vr = client.ontology.objects.ValidationRecord

    start = pd.Timestamp("2026-01-01")
    end = pd.Timestamp("2026-01-31")

    results = (vr.where(vr.object_type.create_date.gt(start))
                 .where(vr.object_type.create_date.lt(end))
                 .to_pandas())

    assert len(results) == 1
    assert results.iloc[0]['id'] == "just_right"

# --- Test 3: Aggregation on Grouped Data ---
def test_group_by_with_multiple_groups():
    """Verify that grouping handles multiple unique keys accurately."""
    mock_data = [
        {"supplier": "A", "entity": "X"},
        {"supplier": "A", "entity": "X"},
        {"supplier": "B", "entity": "Y"},
        {"supplier": "C", "entity": "Z"},
    ]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    
    buckets = client.ontology.objects.ValidationRecord.group_by(
        client.ontology.objects.ValidationRecord.object_type.supplier
    ).count()

    # Convert to dictionary for easy assertions
    counts = {b['key']: b['count'] for b in buckets}
    
    assert counts["A"] == 2
    assert counts["B"] == 1
    assert counts["C"] == 1

# --- Test 4: Action Sequence Verification ---
def test_multiple_action_calls():
    """Verify that multiple actions can be tracked and recorded in order."""
    mock_data = [{"id": "1", "supplier": "A"}, {"id": "2", "supplier": "B"}]
    client = create_mock_osdk_client(mock_data, "ValidationRecord")
    
    # Logic: Update every record's description
    for record in client.ontology.objects.ValidationRecord.take(10):
        client.ontology.actions.update_desc(record_id=record.id, text="Processed")

    # Verify order and content of calls
    expected_calls = [
        call(record_id="1", text="Processed"),
        call(record_id="2", text="Processed")
    ]
    client.ontology.actions.update_desc.assert_has_calls(expected_calls, any_order=True)