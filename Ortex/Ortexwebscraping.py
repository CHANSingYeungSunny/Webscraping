import os
import sys
import requests
import pandas as pd

# Credentials are read from the environment so they are never committed.
# Copy .env.example to .env and fill in your own values.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 时间段 -> 输出列名
TIME_PERIODS = {
    '7d': '7 days',
    '2w': '2 weeks',
    '1m': '1 month',
    '2m': '2 months',
    '3m': '3 months',
    '6m': '6 months',
    '12m': '12 months',
    '18m': '18 months',
}

# 目标股票（按市场分组）。已去重：原列表里 MHO、MOD、SMCI 各重复了一次。
STOCKS = {
    'NYSE': [
        'NUE', 'VLO', 'ARCH', 'COP', 'AMR', 'BXC', 'CVX', 'MHO', 'XOM', 'DINO',
        'MOD', 'MPC', 'TEX', 'JXN', 'URI', 'ASC', 'TGLS', 'CAAP', 'UBER', 'CRM',
        'GRBK', 'ANF', 'CLS', 'TWLO', 'CAH', 'RCL', 'EAT', 'GM',
    ],
    'Nasdaq': [
        'HLIT', 'SMCI', 'PERI', 'ACLS', 'POWL', 'AMPH', 'STRL', 'META', 'GOOGL',
        'TMUS', 'APP', 'CMCSA', 'PEP', 'OKTA', 'GCT', 'BLBD', 'SKYW', 'SFM',
    ],
}

LOGIN_URL = 'https://ortex-gui.ortex.com/account/external_auth?GUIv=2'


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
            f"Copy .env.example to .env, fill in your own Ortex credentials, "
            f"and re-run. (.env is git-ignored.)"
        )
    return value


def build_headers(csrf_token):
    """设置请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://app.ortex.com',
        'Referer': 'https://app.ortex.com/',
        'X-Csrftoken': csrf_token,
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }


# 登录函数
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
        print(response.text)  # 输出错误信息
        return False


# 从CSV文件加载股票ID
def load_stock_ids(csv_file=None):
    """Load the ticker -> Ortex stock_id mapping.

    Defaults to <script dir>/csv/id.csv, which is where the file actually lives.
    The previous default ('ortexSpider/id.csv') never existed, so the script
    failed with FileNotFoundError before making a single request.
    """
    if csv_file is None:
        csv_file = os.path.join(SCRIPT_DIR, 'csv', 'id.csv')
    if not os.path.exists(csv_file):
        raise SystemExit(
            f"Ticker ID mapping not found: {csv_file}\n"
            f"Expected columns: market, stock_name, stock_id."
        )
    df = pd.read_csv(csv_file)
    missing = {'market', 'stock_name', 'stock_id'} - set(df.columns)
    if missing:
        raise SystemExit(f"{csv_file} is missing required columns: {sorted(missing)}")
    return df


# 根据市场和股票名称查找股票ID
def get_stock_id(market, stock_name, stock_ids_df):
    row = stock_ids_df[(stock_ids_df['market'] == market) & (stock_ids_df['stock_name'] == stock_name)]
    if not row.empty:
        return row['stock_id'].values[0]
    else:
        print(f"未能找到市场 {market} 中的股票 {stock_name} 的ID")
        return None


# 获取数据函数
def fetch_data(url, session, headers):
    response = session.get(url, headers=headers)
    print(f"状态码: {response.status_code}")  # 打印状态码
    print(f"响应内容: {response.text}")  # 打印响应内容
    if response.status_code == 200:
        try:
            return response.json()  # Assuming the response is in JSON format
        except ValueError:
            print("响应内容不是JSON格式")
            return None
    else:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return None


# 处理数据函数
def process_data(data, time_period):
    results = []
    columns = ['Metric', 'Current', f'{time_period}', '% Change']
    for metric, values in data.items():
        if isinstance(values, dict):
            result = [metric, values.get('Current'), values.get(time_period), values.get('% Change')]
            results.append(result)
    return results, columns


# 获取股票数据
def fetch_and_save_metrics(session, headers, market, stock, timerange, stock_ids_df):
    # 获取股票ID
    stock_id = get_stock_id(market, stock, stock_ids_df)
    if not stock_id:
        print(f"无法获取股票 {stock} 的ID")
        return False

    # 定义API请求的URL
    metrics_url = f'https://ortex-gui.ortex.com/API/v2/id/{stock_id}/short_interest?format=flat&order&GUIv=2&timerange={timerange}'
    # 抓取数据
    metrics_data = fetch_data(metrics_url, session, headers)
    # 处理并保存数据
    if not metrics_data:
        print(f"未能成功获取 {stock} 的数据")
        return False

    time_period = TIME_PERIODS[timerange]
    processed_data, columns = process_data(metrics_data, time_period)

    # 创建文件夹
    folder_name = f'{market}_{stock}'
    os.makedirs(folder_name, exist_ok=True)

    # 创建DataFrame并保存到CSV文件
    filename = os.path.join(folder_name, f'{stock}_{time_period}_metrics.csv')
    df = pd.DataFrame(processed_data, columns=columns)
    df.to_csv(filename, index=False)
    print(f"{stock} 的数据已保存到 {filename} 文件中")
    return True


def main():
    _load_dotenv_if_available()

    email = _require_env('ORTEX_EMAIL')
    password = _require_env('ORTEX_PASSWORD')
    csrf_token = _require_env('ORTEX_CSRF_TOKEN')
    headers = build_headers(csrf_token)

    session = requests.Session()

    if not login_to_ortex(session, LOGIN_URL, email, password, headers):
        raise SystemExit("登录失败。请检查您的凭证。")

    stock_ids_df = load_stock_ids()

    failures = []
    for market, stock_list in STOCKS.items():
        for stock in stock_list:
            for timerange in TIME_PERIODS:
                ok = fetch_and_save_metrics(session, headers, market, stock, timerange, stock_ids_df)
                if not ok:
                    failures.append((market, stock, timerange))

    requested = sum(len(s) for s in STOCKS.values()) * len(TIME_PERIODS)
    print(f"\nDone: {requested - len(failures)}/{requested} ticker/window combinations saved.")
    if failures:
        print(f"{len(failures)} failed:")
        for market, stock, timerange in failures:
            print(f"  {market} {stock} {timerange}")


if __name__ == "__main__":
    main()