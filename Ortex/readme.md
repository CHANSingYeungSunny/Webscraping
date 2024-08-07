# Ortex Data Fetcher

This script logs into the Ortex platform, fetches stock data for specified stocks from different markets, and saves the data into CSV files.

## Prerequisites

Ensure you have the following packages installed:

- `requests`
- `pandas`

You can install these packages using pip:

```bash
pip install requests pandas
```

## Usage

1. **Set Up Credentials:**

   Credentials come from the environment, so nothing secret is committed. Copy `.env.example`
   to `.env` (git-ignored) and fill in `ORTEX_EMAIL`, `ORTEX_PASSWORD` and `ORTEX_CSRF_TOKEN`.

2. **Prepare Stock IDs:**

   The ticker → Ortex stock ID mapping is read from `Ortex/csv/id.csv`, alongside this script.
   It must contain the columns `market`, `stock_name`, and `stock_id`. The script exits with a
   clear message if the file is missing or malformed.

3. **Run the Script:**

   Execute the script to log in to Ortex, fetch stock data, and save it to CSV files.

## Script Breakdown

### Import Necessary Modules

```python
import os
import requests
import pandas as pd
```

### Configuration

Set the login URL and user credentials:

```python
login_url = 'https://ortex-gui.ortex.com/account/external_auth?GUIv=2'
email = os.environ['ORTEX_EMAIL']
password = os.environ['ORTEX_PASSWORD']
csrf_token = os.environ['ORTEX_CSRF_TOKEN']
```

### Session and Headers

Initialize session and set headers:

```python
session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://app.ortex.com',
    'Referer': 'https://app.ortex.com/',
    'X-Csrftoken': csrf_token,
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
```

### Functions

- **Login Function:**

  Logs into Ortex and returns a boolean indicating success or failure.

  ```python
  def login_to_ortex(session, login_url, email, password, headers):
      login_data = {
          'username': email,
          'password': password
      }
      response = session.post(login_url, json=login_data, headers=headers)
      if response.status_code == 200:
          print("登录成功!")
          return True
      else:
          print(f"登录失败。状态码: {response.status_code}")
          print(response.text)
          return False
  ```

- **Load Stock IDs:**

  Loads stock IDs from `Ortex/csv/id.csv`, resolved relative to the script's own
  location so it works regardless of the working directory. Exits with a clear
  message if the file is missing or lacks the required columns.

  ```python
  def load_stock_ids(csv_file=None):
      if csv_file is None:
          csv_file = os.path.join(SCRIPT_DIR, 'csv', 'id.csv')
      if not os.path.exists(csv_file):
          raise SystemExit(f"Ticker ID mapping not found: {csv_file}")
      return pd.read_csv(csv_file)
  ```

- **Get Stock ID:**

  Finds the stock ID for a given market and stock name.

  ```python
  def get_stock_id(market, stock_name, stock_ids_df):
      row = stock_ids_df[(stock_ids_df['market'] == market) & (stock_ids_df['stock_name'] == stock_name)]
      if not row.empty:
          return row['stock_id'].values[0]
      else:
          print(f"未能找到市场 {market} 中的股票 {stock_name} 的ID")
          return None
  ```

- **Fetch Data:**

  Fetches data from a given URL.

  ```python
  def fetch_data(url, session, headers):
      response = session.get(url, headers=headers)
      print(f"状态码: {response.status_code}")
      print(f"响应内容: {response.text}")
      if response.status_code == 200:
          try:
              return response.json()
          except ValueError:
              print("响应内容不是JSON格式")
              return None
      else:
          print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
          return None
  ```

- **Process Data:**

  Processes fetched data into a structured format.

  ```python
  def process_data(data, time_period):
      results = []
      columns = ['Metric', 'Current', f'{time_period}', '% Change']
      for metric, values in data.items():
          if isinstance(values, dict):
              result = [metric, values.get('Current'), values.get(time_period), values.get('% Change')]
              results.append(result)
      return results, columns
  ```

- **Fetch and Save Metrics:**

  Fetches metrics for a given stock and saves the data into a CSV file.

  ```python
  def fetch_and_save_metrics(session, headers, market, stock, timerange, stock_ids_df):
      stock_id = get_stock_id(market, stock, stock_ids_df)
      if not stock_id:
          print(f"无法获取股票 {stock} 的ID")
          return

      metrics_url = f'https://ortex-gui.ortex.com/API/v2/id/{stock_id}/short_interest?format=flat&order&GUIv=2&timerange={timerange}'
      metrics_data = fetch_data(metrics_url, session, headers)
      if metrics_data:
          time_period = 'Current'
          if timerange == '7d':
              time_period = '7 days'
          elif timerange == '2w':
              time_period = '2 weeks'
          elif timerange == '1m':
              time_period = '1 month'
          elif timerange == '2m':
              time_period = '2 months'
          elif timerange == '3m':
              time_period = '3 months'
          elif timerange == '6m':
              time_period = '6 months'
          elif timerange == '12m':
              time_period = '12 months'
          elif timerange == '18m':
              time_period = '18 months'

          processed_data, columns = process_data(metrics_data, time_period)

          folder_name = f'{market}_{stock}'
          os.makedirs(folder_name, exist_ok=True)

          filename = os.path.join(folder_name, f'{stock}_{time_period}_metrics.csv')
          df = pd.DataFrame(processed_data, columns=columns)
          df.to_csv(filename, index=False)
          print(f"{stock} 的数据已保存到 {filename} 文件中")
      else:
          print(f"未能成功获取 {stock} 的数据")
  ```

### Main Execution

- **Login:**

  Logs into Ortex.

  ```python
  if login_to_ortex(session, login_url, email, password, headers):
  ```

- **Load Stock IDs:**

  Loads stock IDs from the CSV file.

  ```python
  stock_ids_df = load_stock_ids()
  ```

- **Fetch and Save Data:**

  Fetches and saves stock data for specified stocks and time ranges.

  ```python
  stocks = {
      'NYSE': ['NUE', 'VLO', 'ARCH', ...],
      'Nasdaq': ['HLIT', 'SMCI', 'PERI', ...]
  }
  for market, stock_list in stocks.items():
      for stock in stock_list:
          for timerange, period in time_ranges.items():
              fetch_and_save_metrics(session, headers, market, stock, timerange, stock_ids_df)
  ```

## Conclusion

This script helps in automating the process of fetching stock data from Ortex and saving it into structured CSV files for further analysis.
```

Adjust the stock lists and any other details as per your requirements.
