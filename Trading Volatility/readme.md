# README.md

## Overview

This Python script fetches gamma exposure (GEX) data for a list of stock tickers from the Trading Volatility API. The retrieved data is saved in both JSON and CSV formats. The script also ensures adherence to API rate limits by implementing a delay after a certain number of API calls.

## Prerequisites

- Python 3.x
- `requests` library
- `json` library
- `csv` library
- `time` library
- `datetime` library

## Setup

1. **Install Required Libraries**

    If you haven't already installed the required libraries, you can do so using `pip`:
    ```bash
    pip install requests
    ```

2. **API Key**

    Ensure you have a valid API key from Trading Volatility.

3. **Endpoint URL**

    The script uses the following API endpoint:
    ```
    https://stocks.tradingvolatility.net/api
    ```

## Configuration

- **API Key**: Supplied through the `TRADINGVOLATILITY_API_KEY` environment variable. Copy `.env.example` to `.env` and fill in your own key — `.env` is git-ignored, so the key is never committed.
- **Tickers**: The script fetches data for a list of stock tickers. You can modify the list of tickers as per your requirement.

## Usage

1. **Run the Script**

    Execute the script using Python:
    ```bash
    python script_name.py
    ```

    The script performs the following operations:
    - Fetches gamma data for each ticker from the API.
    - Saves the responses to a partial JSON file after each successful fetch.
    - Adheres to the API rate limit by pausing after every 20 requests.
    - Saves the final data in `gamma_responses.json`.
    - Extracts relevant data and saves it in `gamma_data.csv`.

2. **Intermediate Saves**

    The script saves the fetched data in `gamma_responses_partial.json` after each successful API call to prevent data loss in case of interruptions.

## Output

- **gamma_responses.json**: Contains all the API responses.
- **gamma_data.csv**: Contains extracted data with the following columns:
  - `ticker`: Stock ticker symbol
  - `nearest_gex_value`: Nearest Gamma Exposure (GEX) value
  - `implied_volatility`: Implied volatility
  - `rating`: Stock rating

## Error Handling

The script includes error handling for common issues such as:
- HTTP errors during the API request.
- JSON decoding errors for invalid responses.

## Example

```python
import requests
import json
import csv
import time
from datetime import datetime

# API相关信息
ENDPOINT = 'https://stocks.tradingvolatility.net/api'
API_KEY = os.environ['TRADINGVOLATILITY_API_KEY']

# 需要查询的ticker列表
tickers = [
    'NUE', 'VLO', 'ARCH', 'COP', 'AMR', 'BXC', 'SU', 'TA', 'CVX',
    'LTHM', 'MHO', 'XOM', 'HLIT', 'SMCI', 'DINO', 'MOD', 'MPC',
    'TEX', 'JXN', 'URI', 'ASC', 'PERI', 'TGLS', 'ACLS', 'CAAP', 'POWL', 'UBER',
    'CRM', 'AMPH', 'GRBK', 'STRL', 'META', 'GOOGL', 'TMUS', 'ANF', 'CLS', 'MFC',
    'APP', 'CMCSA', 'MHO', 'MOD', 'PEP', 'TWLO', 'OKTA', 'CAH', 'RCL', 'SMCI',
    'EAT', 'GCT', 'GM', 'BLBD', 'SKYW', 'SFM', 'BRK.B'
]

# 用于存储所有响应的字典
all_responses = {}

# 获取每个ticker的gamma数据并存储
for i, ticker in enumerate(tickers):
    params = {
        'username': API_KEY,
        'ticker': ticker,
        'format': 'json'
    }
    headers = {
        'Accept': 'application/json'
    }
    try:
        response = requests.get(f'{ENDPOINT}/gex/latest', params=params, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        all_responses[ticker] = data
        print(f"Fetched data for {ticker} at {datetime.now()}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for ticker {ticker}: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Error occurred for ticker {ticker}: {err}")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for ticker {ticker}. Response content: {response.text}")

    # 每次成功获取数据后立即保存当前的响应数据
    with open('gamma_responses_partial.json', 'w') as f:
        json.dump(all_responses, f, indent=4)

    # 避免超过API调用频率限制
    if (i + 1) % 20 == 0:
        print("Reached 20 API calls, sleeping for 60 seconds...")
        time.sleep(60)

# 最终保存所有响应数据到JSON文件中
with open('gamma_responses.json', 'w') as f:
    json.dump(all_responses, f, indent=4)

# 提取所需数据并存储到CSV文件中
with open('gamma_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['ticker', 'nearest_gex_value', 'implied_volatility', 'rating']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for ticker, data in all_responses.items():
        if ticker in data:
            row = {
                'ticker': ticker,  # 股票代码
                'nearest_gex_value': data[ticker].get('nearest_gex_value', 'N/A'),  # 最近的GEX值
                'implied_volatility': data[ticker].get('implied_volatility', 'N/A'),  # 隐含波动率
                'rating': data[ticker].get('rating', 'N/A')  # 评级
            }
            writer.writerow(row)

print("Data has been successfully stored in gamma_responses.json and gamma_data.csv.")
```

