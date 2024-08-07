import requests
import csv
import matplotlib.pyplot as plt
import pandas as pd

# Functions for combined_data.csv
def fetch_data(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")
        return None

def process_treasury_data(treasury_table):
    if treasury_table:
        processed_data = []
        for entry in treasury_table:
            data = {
                'MSTR/BTC Ratio': entry.get('MSTR/BTC', None),
                'BTC per Share': entry.get('BTC per Share', None),
                'Date': entry.get('Date', None)
            }
            processed_data.append(data)
        return processed_data
    else:
        print("No treasury data found")
        return None

def process_latest_point(raw_data):
    if raw_data:
        nav_premium = raw_data.get('nav_premium', [])
        dates = raw_data.get('dates', [])
        if len(dates) == len(nav_premium):
            return [{'Date': date, 'NAV Premium': nav} for date, nav in zip(dates, nav_premium)]
        else:
            print("Mismatch between dates and nav_premium lengths")
            return None
    return None

def save_to_csv(data, filename):
    if data:
        keys = data[0].keys()
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

# Functions for combined_data2.csv
def process_data_for_combined_data2(raw_data):
    if raw_data:
        dates = raw_data.get('dates', [])
        nav_premium = raw_data.get('nav_premium', [])
        mstr_btc_ratios = raw_data.get('mstr_btc_ratio', [])
        if len(dates) == len(nav_premium) == len(mstr_btc_ratios):
            processed_data = [{'Date': date, 'NAV Premium': nav, 'MSTR/BTC Ratio': ratio} 
                              for date, nav, ratio in zip(dates, nav_premium, mstr_btc_ratios)]
            return processed_data
        else:
            print("Mismatch between dates, nav_premium, and mstr_btc_ratios lengths")
            return None
    else:
        print("No data found")
        return None

# Function to save plots (from the original script)
def save_plot_to_file(data, filename, y_label, title, y_key, color='blue'):
    if data:
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])

        plt.figure(figsize=(10, 5))
        plt.plot(df['Date'], df[y_key], marker='o', linestyle='-', color=color)
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel(y_label)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(filename)
        print(f"Plot saved to {filename}")
        plt.close()
    else:
        print("No data to plot")

def main():
    url = "https://www.mstr-tracker.com/data"
    headers = {
        # Add any headers required for the request here
    }

    # Fetch data
    raw_data = fetch_data(url, headers=headers)

    if raw_data:
        # Process data for combined_data.csv
        treasury_table = raw_data.get('treasury_table', [])
        processed_treasury_data = process_treasury_data(treasury_table)
        processed_latest_point_data = process_latest_point(raw_data)

        if processed_treasury_data and processed_latest_point_data:
            combined_data = []
            latest_point_dict = {entry['Date']: entry['NAV Premium'] for entry in processed_latest_point_data}
            for entry in processed_treasury_data:
                date = entry.get('Date')
                if date in latest_point_dict:
                    combined_entry = {
                        'Date': date,
                        'MSTR/BTC Ratio': entry.get('MSTR/BTC Ratio'),
                        'BTC per Share': entry.get('BTC per Share'),
                        'NAV Premium': latest_point_dict[date]
                    }
                    combined_data.append(combined_entry)
            save_to_csv(combined_data, 'combined_data.csv')
        else:
            print("Not all data was available for combined_data.csv")

        # Process data for combined_data2.csv
        processed_data2 = process_data_for_combined_data2(raw_data)
        if processed_data2:
            save_to_csv(processed_data2, 'combined_data2.csv')
        else:
            print("Failed to process data for combined_data2.csv")

        # Generate plots
        if processed_latest_point_data:
            save_plot_to_file(processed_latest_point_data, 'nav_premium_plot.png', 'NAV Premium', 'NAV Premium Over Time', 'NAV Premium', 'orange')

        if processed_treasury_data:
            btc_data = [{'Date': entry['Date'], 'BTC per Share': entry['BTC per Share']} for entry in processed_treasury_data]
            save_plot_to_file(btc_data, 'btc_per_share_plot.png', 'BTC per Share', 'BTC per Share Over Time', 'BTC per Share', 'red')

        if processed_data2:
            save_plot_to_file(processed_data2, 'mstr_btc_ratio_plot2.png', 'MSTR/BTC Ratio', 'MSTR/BTC Ratio Over Time', 'MSTR/BTC Ratio', 'blue')

    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main()
