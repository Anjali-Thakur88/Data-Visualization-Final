# Drug Safety Dashboard

This project is a Streamlit-based web application that provides insights into drug safety data using the openFDA API. The app allows users to explore adverse event reports for various drugs, visualize trends, and search for specific drugs.

## Features

- **Top Drugs**: Displays the top 10 most reported drugs from the last 100 adverse event reports.
- **Search by Drug**: Allows users to search for adverse event reports by entering a drug name.
- **Trends**: Visualizes the trend of adverse event reports for a specific drug over the past 180 days.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Anjali-Thakur88/Data-Visualization-Final.git
   cd Data-Visualization-Final
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run ds_final_project.py
   ```

2. Open the app in your browser at `http://localhost:8501`.

## File Structure

- `ds_final_project.py`: Main application file containing the Streamlit app logic.
- `requirements.txt`: List of Python dependencies required to run the app.

## API Information

This app uses the [openFDA API](https://open.fda.gov/apis/) to fetch drug adverse event data. Ensure you have an active internet connection to access the API.

## Notes

- The app caches data to improve performance. If you encounter outdated data, try clearing the cache by restarting the app.
- The app fetches a maximum of 100 adverse event reports due to API limitations.

## License

This project is licensed under the MIT License. See the LICENSE file for details.