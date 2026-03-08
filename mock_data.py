import json
import pandas as pd
from unittest.mock import MagicMock

class PropertyMock:
    """Mimics the OSDK property access (e.g., Object.object_type.property.eq())"""
    def __init__(self, name):
        self.name = name
    def eq(self, value): return ("eq", self.name, value)
    def gt(self, value): return ("gt", self.name, value)
    def lt(self, value): return ("lt", self.name, value)
    def exact(self): return self # Supports group_by(prop.exact())

class ObjectTypeMock:
    """Container for the object_type attribute."""
    def __init__(self, property_names):
        for name in property_names:
            setattr(self, name, PropertyMock(name))

class FoundryObjectMock:
    """Converts JSON dict to an object with dot-notation (record.id)."""
    def __init__(self, data):
        self.__dict__.update(data)
    def __repr__(self):
        return f"FoundryObject({getattr(self, 'id', 'No ID')})"

class GroupByMock:
    """Handles logic after .group_by() is called."""
    def __init__(self, data, group_prop):
        self._data = data
        self._group_prop = group_prop

    def count(self):
        """Returns OSDK-style list of buckets."""
        if not self._data: return []
        df = pd.DataFrame([obj.__dict__ for obj in self._data])
        counts = df.groupby(self._group_prop).size().reset_index(name='count')
        return [{"key": row[self._group_prop], "count": row['count']} for _, row in counts.iterrows()]

class ObjectSetMock:
    """The core SDK class for chaining and terminal actions."""
    def __init__(self, data, object_type):
        self._items = [FoundryObjectMock(d) if isinstance(d, dict) else d for d in data]
        self.object_type = object_type

    def where(self, condition):
        op, prop, val = condition
        if op == "eq":
            filtered = [d for d in self._items if getattr(d, prop) == val]
        elif op == "gt":
            filtered = [d for d in self._items if getattr(d, prop) > val]
        elif op == "lt":
            filtered = [d for d in self._items if getattr(d, prop) < val]
        else:
            filtered = self._items
        return ObjectSetMock(filtered, self.object_type)

    def group_by(self, property_mock):
        return GroupByMock(self._items, property_mock.name)
    
    def max(self, property_mock):
        if not self._items: return None
        return max(getattr(obj, property_mock.name) for obj in self._items)

    def min(self, property_mock):
        if not self._items: return None
        return min(getattr(obj, property_mock.name) for obj in self._items)

    def count(self):
        return len(self._items)

    def take(self, n):
        return self._items[:n]

    def to_pandas(self):
        return pd.DataFrame([obj.__dict__ for obj in self._items])

def create_mock_osdk_client(json_data, object_api_name):
    client = MagicMock()
    
    # 1. Setup Objects (Reading)
    props = list(json_data[0].keys()) if json_data else []
    obj_type = ObjectTypeMock(props)
    oset = ObjectSetMock(json_data, obj_type)
    setattr(client.ontology.objects, object_api_name, oset)
    
    # 2. Setup Actions (Writing)
    # MagicMock will automatically allow calls like client.ontology.actions.my_action()
    client.ontology.actions = MagicMock()
    
    return client

# --- APPLICATION USAGE ---

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


def example_usages():

    raw_data = load_data('sample_data.json').to_dict(orient='records') 

    # 2. Create the mock client
    client = create_mock_osdk_client(raw_data, "ValidationRecord")
    ValidationRecord = client.ontology.objects.ValidationRecord

    # 3. Test OSDK Syntax
    query = ValidationRecord.where(ValidationRecord.object_type.entity.eq("Transaction"))
    df_result = query.to_pandas()
    counts = ValidationRecord.group_by(ValidationRecord.object_type.entity).count()

    print(f"Transactions found: {len(df_result)}")
    print(f"Grouped Counts: {counts}")

    # more tests and usages
    # Standard OSDK: .where(ObjectType.property.eq(value))
    query = ValidationRecord.where(ValidationRecord.object_type.entity.eq("Transaction"))
    results = query.take(10)

    for record in results:
        print(f"Supplier: {record.supplier} | Status: {record.validation_result}")

    # create_date filetering usage
    # Create a cutoff date using the same Pandas type
    cutoff_date = pd.Timestamp(2026, 3, 1) # Example date

    # OSDK Syntax: Filter for records after Jan 1st, 2026
    recent_records = ValidationRecord.where(
        ValidationRecord.object_type.create_date.gt(cutoff_date)
    )

    results = recent_records.take(5)
    for record in results:
        print(f"Date: {record.create_date} | Entity: {record.entity}")

    # to_pandas usage
    # 1. Chain some filters
    cutoff = pd.Timestamp(2026, 3, 1)
    filtered_set = ValidationRecord.where(
        ValidationRecord.object_type.entity.eq("Transaction")
    ).where(
        ValidationRecord.object_type.create_date.gt(cutoff)
    )

    # 2. Convert back to Pandas
    df = filtered_set.to_pandas()

    print("Filtered DataFrame:")
    print(df[['id', 'entity', 'create_date']])


    # count and min\max usage
    # 1. Get Count
    total_transactions = ValidationRecord.where(
        ValidationRecord.object_type.entity.eq("Transaction")
    ).count()

    # 2. Get Max/Min Date
    latest_entry = ValidationRecord.max(ValidationRecord.object_type.create_date)

    print(f"Total Transactions: {total_transactions}")
    print(f"Latest Record Date: {latest_entry}")

    # group_by usage
    # 1. Group by Entity and count occurrences
    entity_counts = ValidationRecord.group_by(ValidationRecord.object_type.entity).count()

    print("Records by Entity Type:")
    for bucket in entity_counts:
        print(f"- {bucket['key']}: {bucket['count']}")

    # 2. Group by Supplier
    supplier_stats = ValidationRecord.group_by(ValidationRecord.object_type.supplier).count()

    print("\nRecords by Supplier:")
    for bucket in supplier_stats:
        print(f"- {bucket['key']}: {bucket['count']}")


if __name__ == "__main__":
    example_usages()
    # You can also run your tests here if you want, or use a testing framework like pytest.