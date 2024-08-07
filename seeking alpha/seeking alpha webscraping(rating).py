import os
import requests
import pandas as pd
import json
import time


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


# Tickers to query (de-duplicated: MHO, MOD and SMCI were each listed twice)
TICKERS = [
    'NUE', 'VLO', 'ARCH', 'COP', 'AMR', 'BXC', 'SU', 'TA', 'CVX',
    'LTHM', 'MHO', 'XOM', 'HLIT', 'SMCI', 'DINO', 'MOD', 'MPC',
    'TEX', 'JXN', 'URI', 'ASC', 'PERI', 'TGLS', 'ACLS', 'CAAP', 'POWL', 'UBER',
    'CRM', 'AMPH', 'GRBK', 'STRL', 'META', 'GOOGL', 'TMUS', 'ANF', 'CLS', 'MFC',
    'APP', 'CMCSA', 'PEP', 'TWLO', 'OKTA', 'CAH', 'RCL',
    'EAT', 'GCT', 'GM', 'BLBD', 'SKYW', 'SFM', 'BRK.B', 'ATGE'
]


def fetch_data(url, session, headers):
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return None


def fetch_and_process_latest_histories(ticker, session, headers):
    histories_url = f'https://seekingalpha.com/api/v3/symbols/{ticker}/rating/histories?page[number]=1'

    # Fetch data
    histories_data = fetch_data(histories_url, session, headers)

    # Process latest histories data
    if histories_data:
        histories_ratings = histories_data['data']
        if histories_ratings:
            latest_history = histories_ratings[0]['attributes']
            processed_data = {
                'Ticker': ticker,
                'Date': latest_history['asDate'],
                'SA Analysts Rating': latest_history['ratings'].get('authorsRating', None),
                'Wall Street Rating': latest_history['ratings'].get('sellSideRating', None),
                'Quant Rating': latest_history['ratings'].get('quantRating', None)
            }
            return processed_data
        else:
            print(f"No histories data found for {ticker}")
            return None
    else:
        print(f"Failed to fetch histories data for {ticker}")
        return None


def main():
    _load_dotenv_if_available()
    email = _require_env('SEEKINGALPHA_EMAIL')
    password = _require_env('SEEKINGALPHA_PASSWORD')

    # Create session object
    session = requests.Session()

    # Set request headers
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://seekingalpha.com',
        'Referer': 'https://seekingalpha.com/',
    }

    # Login information
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

    # Login request
    response = session.post(login_url, json=login_data, headers=headers)
    if response.status_code != 201:
        print(f"Login failed. Status code: {response.status_code}")
        return

    print("Login successful!")

    all_data = []

    for ticker in TICKERS:
        data = fetch_and_process_latest_histories(ticker, session, headers)
        if data:
            all_data.append(data)
        time.sleep(20)  # Adjust delay as needed

    if all_data:
        # Save all data to one CSV
        df = pd.DataFrame(all_data)
        df.to_csv('all_latest_quant_ratings_histories.csv', index=False)
        print("All data saved to all_latest_quant_ratings_histories.csv")
    else:
        print("No rating data retrieved.")


if __name__ == "__main__":
    main()