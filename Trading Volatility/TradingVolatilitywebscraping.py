import os
import requests
import json
import csv
import time
from datetime import datetime

# API相关信息
ENDPOINT = 'https://stocks.tradingvolatility.net/api'


def _load_dotenv_if_available():
    """Load a local .env file if python-dotenv is installed. Optional."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _require_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(
            f"Missing required environment variable: {name}\n"
            f"Copy .env.example to .env, fill in your own Trading Volatility API key, "
            f"and re-run. (.env is git-ignored.)"
        )
    return value


# 需要查询的ticker列表（已去重：原列表中 MHO、MOD、SMCI 各出现两次）
tickers = [
    'NUE', 'VLO', 'ARCH', 'COP', 'AMR', 'BXC', 'SU', 'TA', 'CVX',
    'LTHM', 'MHO', 'XOM', 'HLIT', 'SMCI', 'DINO', 'MOD', 'MPC',
    'TEX', 'JXN', 'URI', 'ASC', 'PERI', 'TGLS', 'ACLS', 'CAAP', 'POWL', 'UBER',
    'CRM', 'AMPH', 'GRBK', 'STRL', 'META', 'GOOGL', 'TMUS', 'ANF', 'CLS', 'MFC',
    'APP', 'CMCSA', 'PEP', 'TWLO', 'OKTA', 'CAH', 'RCL',
    'EAT', 'GCT', 'GM', 'BLBD', 'SKYW', 'SFM', 'BRK.B'
]


def main():
    _load_dotenv_if_available()
    api_key = _require_env('TRADINGVOLATILITY_API_KEY')

    # 用于存储所有响应的字典
    all_responses = {}

    # 获取每个ticker的gamma数据并存储
    for i, ticker in enumerate(tickers):
        params = {
            'username': api_key,
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


if __name__ == "__main__":
    main()