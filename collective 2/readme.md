# Financial Data Scraper

This project scrapes financial metrics from a given strategy on Collective2 and downloads the strategy CSV data. It also logs in to the website to scrape open positions data.

## Prerequisites

- Python 3.x
- Required libraries: `requests`, `beautifulsoup4`, `pandas`, `csv`

## Installation

Install the required libraries using pip:

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

### 1. Scrape Financial Metrics

This function scrapes key financial metrics from a specified strategy page on Collective2 and saves the data to a CSV file.

```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_financial_metrics():
    url_stats = 'https://collective2.com/details/144065368'
    response = requests.get(url_stats)
    soup = BeautifulSoup(response.content, 'html.parser')

    stats_row = soup.find('div', class_='statsUnderRow')
    annual_return_element = stats_row.find('div', class_='stNum pos')
    annual_return = annual_return_element.find('span').text.strip() if annual_return_element else 'N/A'

    max_drawdown_element = soup.find('div', class_='stNum neg')
    max_drawdown = max_drawdown_element.find('span').text.strip() if max_drawdown_element else 'N/A'

    num_trades_element = soup.find_all('div', class_='statBlk')
    num_trades = 'N/A'
    for element in num_trades_element:
        num_trades_text = element.find('div', class_='stWord')
        if num_trades_text and num_trades_text.text.strip() == 'Num Trades':
            num_trades = element.find('div', class_='stNum').find('span').text.strip()
            break

    win_trades = 'N/A'
    for element in num_trades_element:
        win_trades_text = element.find('div', class_='stWord')
        if win_trades_text and win_trades_text.text.strip() == 'Win Trades':
            win_trades = element.find('div', class_='stNum').find('span').text.strip()
            break

    profit_factor = 'N/A'
    for element in num_trades_element:
        profit_factor_text = element.find('div', class_='stWord')
        if profit_factor_text and profit_factor_text.text.strip() == 'Profit Factor':
            profit_factor_span = element.find('div', class_='stNum').find('span')
            profit_factor = profit_factor_span.text.strip().split(':')[0].strip()
            break

    win_months = 'N/A'
    for element in num_trades_element:
        win_months_text = element.find('div', class_='stWord')
        if win_months_text and win_months_text.text.strip() == 'Win Months':
            win_months = element.find('div', class_='stNum').find('span').text.strip()
            break

    data = {
        'Annual Return (Compounded)': [annual_return],
        'Max Drawdown': [max_drawdown],
        'Num Trades': [num_trades],
        'Win Trades': [win_trades],
        'Profit Factor': [profit_factor],
        'Win Months': [win_months]
    }

    df = pd.DataFrame(data)
    df.to_csv('financial_metrics.csv', index=False)
    print('Financial metrics data saved to financial_metrics.csv')
```

### 2. Download Strategy CSV Data

This function downloads the strategy CSV data from Collective2.

```python
import requests

def download_strategy_csv():
    url_csv = 'https://collective2.com/strategy/csv/144065368'
    response = requests.get(url_csv)
    if response.status_code == 200:
        with open('strategy_data.csv', 'wb') as file:
            file.write(response.content)
        print("Strategy CSV file downloaded successfully.")
    else:
        print(f"Failed to download CSV file. Status code: {response.status_code}")
```

### 3. Login and Scrape Open Positions

This function logs in to the Collective2 website and scrapes the open positions data, saving it to a CSV file.

```python
import requests
from bs4 import BeautifulSoup
import csv

def login_and_scrape_open_positions():
    login_url = "https://collective2.com/cgi-perl/login.mpl"
    login_page_url = "https://collective2.com/securelogin/"
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    })

    # Optional pre-existing cookie jar, supplied as JSON via COLLECTIVE2_COOKIES.
    # Left unset by default: the login below establishes the session on its own.
    cookies_json = os.environ.get('COLLECTIVE2_COOKIES')
    if cookies_json:
        session.cookies.update(json.loads(cookies_json))

    login_page_response = session.get(login_page_url)
    login_page_soup = BeautifulSoup(login_page_response.content, 'html.parser')

    hidden_inputs = login_page_soup.find_all("input", type="hidden")
    login_data = {input_.get("name"): input_.get("value") for input_ in hidden_inputs}
    login_data.update({
        "email": os.environ['COLLECTIVE2_EMAIL'],
        "password": os.environ['COLLECTIVE2_PASSWORD']
    })

    headers = {
        "authority": "collective2.com",
        "method": "POST",
        "path": "/cgi-perl/login.mpl",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "origin": "https://collective2.com",
        "priority": "u=0, i",
        "referer": "https://collective2.com/securelogin/",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    response = session.post(login_url, data=login_data, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    dashboard_indicator = soup.find("title")
    if response.status_code == 200 and dashboard_indicator and "Dashboard" in dashboard_indicator.text:
        print("Login successful!")

        target_url = "https://collective2.com/details/144065368"
        response = session.get(target_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        open_positions_div = soup.find("div", {"class": "comp-strategyOverview__openPositions"})
        if open_positions_div:
            open_positions_table = open_positions_div.find("table", {"class": "positions"})
            if open_positions_table:
                rows = open_positions_table.find_all("tr")
                data = []
                for row in rows[1:]:
                    cells = row.find_all("td")
                    if len(cells) == 9:
                        date = cells[0].text.strip()
                        symbol = cells[1].text.strip()
                        description = cells[

2].text.strip()
                        side = cells[3].text.strip()
                        quant = cells[4].text.strip()
                        basis = cells[5].text.strip()
                        price = cells[6].text.strip()
                        unrealized_pl = cells[7].text.strip()
                        realized_pl = cells[8].text.strip()
                        data.append([date, symbol, description, side, quant, basis, price, unrealized_pl, realized_pl])
                    else:
                        print(f"Row does not have enough columns: {row}")

                with open('open_positions.csv', mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Date", "Symbol", "Description", "Side", "Quant", "Basis", "Price", "Unrealized P/L", "Realized P/L"])
                    writer.writerows(data)
                print("Open positions data saved to open_positions.csv")
            else:
                print("Open positions table not found")
        else:
            print("Open positions section not found")
    else:
        print("Login failed, please check your login information and network connection.")
```

### Execute All Functions

You can execute all the functions in sequence to scrape financial metrics, download the strategy CSV, and scrape open positions data.

```python
scrape_financial_metrics()
download_strategy_csv()
login_and_scrape_open_positions()
```

