import json
import random
import uuid
from utils import get_random_timestamp

# Configuration
NUM_RECORDS = 1000
SUPPLIERS = ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"]
ERRORS = [
    "missing 'lalal' parameter",
    "missing 'email' field",
    "invalid timestamp",
    "schema validation failed",
    "duplicate transaction ID"
]
ENTITIES = ["Transaction", "Order", "Customer", "Product"]

data = []
for _ in range(NUM_RECORDS):
    # 80% chance of being Valid
    is_valid = random.random() < 0.8
    
    item = {
        "id": str(uuid.uuid4()),
        "create_date": get_random_timestamp(start_date_str="01-01-2026"),
        "entity": random.choice(ENTITIES),
        "supplier": random.choice(SUPPLIERS),
        "validation_result": "Valid" if is_valid else "InValid",
        "description": "" if is_valid else random.choice(ERRORS)
    }
    data.append(item)

# Write to file
output_file = "sample_data.json"
with open(output_file, "w") as f:
    json.dump(data, f, indent=2)

print(f"Successfully generated {NUM_RECORDS} records in {output_file}")