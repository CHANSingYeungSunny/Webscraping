import os
import requests
import pandas as pd
import json


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
            f"Copy .env.example to .env, fill in your own Seeking Alpha credentials, "
            f"and re-run. (.env is git-ignored.)"
        )
    return value


def fetch_data(url, session, headers):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"获取数据失败，状态码: {response.status_code}")
        return None


def process_data(data, included):
    stock_data = []
    for pick in data:
        attributes = pick['attributes']
        relationships = pick['relationships']
        ticker_id = relationships['ticker']['data']['id']
        ticker_info = included.get(ticker_id, {}).get('attributes', {})
        sector_id = ticker_info.get('sector', {}).get('data', {}).get('id', '')
        sector_info = included.get(sector_id, {}).get('attributes', {})

        holding = ticker_info.get('holding', None)
        if holding is not None:
            holding = float(holding) * 100  # 转换为百分比
        else:
            holding = 'N/A'

        stock_data.append([
            pick['id'],
            attributes['buy_price'],
            attributes['sell_price'],
            attributes.get('total_return'),
            attributes.get('price_return'),
            attributes['created_at'],
            attributes['removed_at'],
            attributes['article_title'],
            ticker_id,
            ticker_info.get('slug', ''),
            ticker_info.get('companyName', ''),
            sector_info.get('name', ''),
            ticker_info.get('rating', 'N/A'),
            holding
        ])
    return stock_data


def main():
    _load_dotenv_if_available()
    email = _require_env('SEEKINGALPHA_EMAIL')
    password = _require_env('SEEKINGALPHA_PASSWORD')

    # 创建会话对象
    session = requests.Session()

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://seekingalpha.com',
        'Referer': 'https://seekingalpha.com/',
    }

    # 登录信息
    login_url = 'https://seekingalpha.com/api/v3/login_tokens'
    login_data = {
        'data': {
            'type': 'loginTokens',
            'relationships': {
                'user': {
                    'data': {
                        'email': email,
                        'password': password
                    }
                }
            }
        }
    }

    # 登录请求
    response = session.post(login_url, json=login_data, headers=headers)
    if response.status_code != 201:
        print(f"登录失败。状态码: {response.status_code}")
        return

    print("登录成功!")
    # 获取 current 和 closed 数据的URL
    current_url = 'https://seekingalpha.com/api/v3/service_plans/458/picks?include=ticker%2Cticker.sector%2Cticker.tickerMetrics%2Cticker.tickerMetrics.metricType&page[size]=100&sort=undefined'
    closed_url = 'https://seekingalpha.com/api/v3/service_plans/458/picks?include=ticker%2Cticker.sector%2Cticker.tickerMetrics%2Cticker.tickerMetrics.metricType&page[size]=100&sort=undefined&status=closed'

    # 抓取数据
    current_data = fetch_data(current_url, session, headers)
    closed_data = fetch_data(closed_url, session, headers)

    # 解析数据
    if not (current_data and closed_data):
        print("未能成功获取所有数据")
        return

    included_current = {item['id']: item for item in current_data['included']}
    included_closed = {item['id']: item for item in closed_data['included']}
    current_stock_data = process_data(current_data['data'], included_current)
    closed_stock_data = process_data(closed_data['data'], included_closed)

    columns = [
        'ID', 'Buy Price', 'Sell Price', 'Total Return', 'Price Return',
        'Created At', 'Removed At', 'Article Title', 'Ticker ID', 'Ticker Symbol', 'Company Name', 'Sector', 'Rating', 'Holding %'
    ]

    # 保存数据到CSV文件
    pd.DataFrame(current_stock_data, columns=columns).to_csv('current_alpha_picks.csv', index=False)
    pd.DataFrame(closed_stock_data, columns=columns).to_csv('closed_alpha_picks.csv', index=False)

    print("数据已保存到current_alpha_picks.csv和closed_alpha_picks.csv文件中")


if __name__ == "__main__":
    main()