import json
import random
from datetime import datetime
import pandas as pd
from mock_data import create_mock_osdk_client

DATE_FORMAT = "%d-%m-%Y"
TODAY = datetime.now().strftime(DATE_FORMAT)


def get_random_timestamp(start_date_str: str, end_date_str: str = str(TODAY)) -> float:
    try:
        # Convert date strings to datetime objects
        start_date = datetime.strptime(start_date_str, DATE_FORMAT)
        end_date = datetime.strptime(end_date_str, DATE_FORMAT)
    except ValueError:
        raise ValueError(f"Incorrect date format. Please use '{DATE_FORMAT}'.")

    # Ensure the start date is not after the end date
    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    # Convert datetime objects to Unix timestamps (seconds since epoch)
    start_timestamp = start_date.timestamp()
    end_timestamp = end_date.timestamp()

    # Generate a random timestamp between the start and end timestamps
    return random.uniform(start_timestamp, end_timestamp)


def get_osdk_client(filepath='sample_data.json'):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Convert string dates to Timestamps as they would appear in the SDK
    for record in data:
        if 'create_date' in record:
            record['create_date'] = pd.Timestamp(record['create_date'], unit='s')
            
    # Initialize the Mock Client
    client = create_mock_osdk_client(data, "ValidationRecord")
    return client