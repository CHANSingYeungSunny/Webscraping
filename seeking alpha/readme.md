## README for Fetching and Processing Seeking Alpha Data

### First Program: Fetching and Processing Stock Picks Data

#### Overview
This program logs into Seeking Alpha, fetches current and closed stock picks data, processes the data, and saves it to CSV files.

#### Requirements
- Python 3.x
- Required libraries: `requests`, `pandas`, `json`

You can install the required libraries using:
```sh
pip install requests pandas
```

#### Usage
1. **Update Login Credentials**
   - Replace the `email` and `password` fields in the `login_data` dictionary with your Seeking Alpha login credentials.

2. **Run the Script**
   - Execute the script to log in, fetch data, process it, and save it to CSV files.
   ```sh
   python script_name.py
   ```

#### Script Details

- **fetch_data(url, session, headers):**
  - Fetches data from the provided URL using the given session and headers.
  - Returns the JSON response if the request is successful; otherwise, prints an error message and returns `None`.

- **process_data(data, included):**
  - Processes the fetched data to extract relevant stock information.
  - Returns a list of stock data.

- **Session Initialization:**
  - Creates a session object and sets the request headers.

- **Login Request:**
  - Sends a POST request to log in to Seeking Alpha using the provided credentials.
  - If login is successful, fetches current and closed stock picks data.

- **Data Processing:**
  - Parses and processes the fetched data.
  - Saves the processed data to `current_alpha_picks.csv` and `closed_alpha_picks.csv` files.

#### Example Output
Two CSV files will be generated:
- `current_alpha_picks.csv`
- `closed_alpha_picks.csv`

### Second Program: Fetching and Processing Latest Rating Histories

#### Overview
This program logs into Seeking Alpha, fetches the latest rating histories for a list of tickers, processes the data, and saves it to a CSV file.

#### Requirements
- Python 3.x
- Required libraries: `requests`, `pandas`, `json`, `time`

You can install the required libraries using:
```sh
pip install requests pandas
```

#### Usage
1. **Update Login Credentials**
   - Replace the `email` and `password` fields in the `login_data` dictionary with your Seeking Alpha login credentials.

2. **Run the Script**
   - Execute the script to log in, fetch rating histories for the tickers, process the data, and save it to a CSV file.
   ```sh
   python script_name.py
   ```

#### Script Details

- **fetch_data(url, session, headers):**
  - Fetches data from the provided URL using the given session and headers.
  - Returns the JSON response if the request is successful; otherwise, prints an error message and returns `None`.

- **fetch_and_process_latest_histories(ticker, session, headers):**
  - Fetches and processes the latest rating histories for the provided ticker.
  - Returns the processed data.

- **Session Initialization:**
  - Creates a session object and sets the request headers.

- **Login Request:**
  - Sends a POST request to log in to Seeking Alpha using the provided credentials.
  - If login is successful, fetches and processes rating histories for a predefined list of tickers.

- **Data Processing:**
  - Parses and processes the fetched data for each ticker.
  - Saves the processed data to `all_latest_quant_ratings_histories.csv` file.

#### Example Output
A CSV file will be generated:
- `all_latest_quant_ratings_histories.csv`
