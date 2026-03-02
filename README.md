# Validation Results Dashboard

This project is a Streamlit web application that displays a dashboard for validation results. It is designed to provide insights into data validation metrics, helping to identify trends and top errors.

## Features

*   **Overall Statistics:** View the total number of validations, with a breakdown of valid and invalid results.
*   **Top Error Analysis:** Automatically identifies the most frequent validation error and the suppliers and entities most associated with it.
*   **Results by Supplier:** Each supplier's validation results are detailed in an expandable section.
*   **Validation Trend:** A line chart shows the trend of valid and invalid validations over time for each supplier.
*   **Sortable Views:** Sort suppliers by name or by their most recent activity.
*   **Detailed Error View:** For each supplier, a table of their invalid validations is available.

## Project Structure

*   `dashboard.py`: The main Streamlit application file.
*   `generate_data.py`: A script to generate sample data for the dashboard.
*   `utils.py`: Contains utility functions, such as `get_random_timestamp`, used by `generate_data.py`.
*   `sample_data.json`: The sample data file used by the dashboard.
*   `requirements.txt`: A list of the Python packages required to run the project.
*   `Dockerfile`: A file to build a Docker container for the application.

## Setup and Usage

### Prerequisites

*   Python 3.6 or later
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moshereznik12/Purim2026.git
    cd Purim2026
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Generate the sample data:**
    ```bash
    python generate_data.py
    ```

### Running the Application

1.  **Run the Streamlit app:**
    ```bash
    streamlit run dashboard.py
    ```

2.  **Open your web browser** and go to the URL provided by Streamlit (usually `http://localhost:8501`).

## Docker

You can also run this application in a Docker container.

1.  **Build the Docker image:**
    ```bash
    docker build -t validation-dashboard .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8501:8501 validation-dashboard
    ```
