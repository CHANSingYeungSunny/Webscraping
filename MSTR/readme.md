# README

## Overview

This script fetches, processes, and visualizes financial data from a specified URL. It performs the following tasks:
1. Fetches data from a remote source.
2. Processes and combines the data.
3. Saves the processed data to CSV files.
4. Generates and saves plots based on the processed data.

## Prerequisites

Ensure you have the following Python packages installed:
- `requests`
- `csv`
- `matplotlib`
- `pandas`

You can install these packages using pip:

```sh
pip install requests matplotlib pandas
```

## Files

### combined_data.csv
- Contains processed data with columns: `Date`, `MSTR/BTC Ratio`, `BTC per Share`, `NAV Premium`.

### combined_data2.csv
- Contains processed data with columns: `Date`, `NAV Premium`, `MSTR/BTC Ratio`.

### nav_premium_plot.png
- A plot of `NAV Premium` over time.

### btc_per_share_plot.png
- A plot of `BTC per Share` over time.

### mstr_btc_ratio_plot2.png
- A plot of `MSTR/BTC Ratio` over time.

## Functions

### fetch_data(url, headers=None)
Fetches data from the specified URL.

**Parameters:**
- `url`: The URL to fetch data from.
- `headers`: Optional headers for the request.

**Returns:**
- JSON data if the request is successful, otherwise `None`.

### process_treasury_data(treasury_table)
Processes treasury data from the fetched data.

**Parameters:**
- `treasury_table`: The treasury data to process.

**Returns:**
- List of processed data dictionaries.

### process_latest_point(raw_data)
Processes the latest point data from the fetched data.

**Parameters:**
- `raw_data`: The raw data fetched from the URL.

**Returns:**
- List of processed data dictionaries.

### save_to_csv(data, filename)
Saves the processed data to a CSV file.

**Parameters:**
- `data`: The data to save.
- `filename`: The name of the file to save the data to.

### process_data_for_combined_data2(raw_data)
Processes data for the combined_data2.csv file.

**Parameters:**
- `raw_data`: The raw data fetched from the URL.

**Returns:**
- List of processed data dictionaries.

### save_plot_to_file(data, filename, y_label, title, y_key, color='blue')
Generates and saves a plot to a file.

**Parameters:**
- `data`: The data to plot.
- `filename`: The name of the file to save the plot to.
- `y_label`: The label for the y-axis.
- `title`: The title of the plot.
- `y_key`: The key in the data to plot on the y-axis.
- `color`: The color of the plot line (default is blue).

## Main Function

The `main()` function orchestrates the data fetching, processing, saving, and plotting.

### Workflow
1. **Fetch Data:**
   - Calls `fetch_data()` to get the raw data from the specified URL.
   
2. **Process Data:**
   - Calls `process_treasury_data()` and `process_latest_point()` to process the fetched data.
   - Combines processed data and saves it to `combined_data.csv`.
   - Calls `process_data_for_combined_data2()` and saves the result to `combined_data2.csv`.

3. **Generate Plots:**
   - Calls `save_plot_to_file()` to generate and save plots for `NAV Premium`, `BTC per Share`, and `MSTR/BTC Ratio`.

## Usage

To run the script, simply execute it:

```sh
python script.py
```

Replace `script.py` with the actual name of your script file.

The script will output the processed data to CSV files and save the generated plots as PNG images in the same directory.
