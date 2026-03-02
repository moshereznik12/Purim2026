import random
from datetime import datetime

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


print(datetime.fromtimestamp(1770068697.3560815).strftime(DATE_FORMAT))