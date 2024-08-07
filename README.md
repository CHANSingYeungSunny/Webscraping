# Webscraping

Above are the folders including python files, csv, json and png files about webscraping of different websites.

## Setup

Every scraper takes its credentials from environment variables, so no secrets are
stored in this repository.

```bash
pip install requests pandas beautifulsoup4 matplotlib python-dotenv
cp .env.example .env     # then fill in your own credentials
```

`.env` is git-ignored. Without `python-dotenv`, export the same variables in your
shell instead. Each script exits with a message naming the variable it needs if one
is missing.

| Folder | Variables required |
|---|---|
| `MSTR/` | none (public JSON endpoint) |
| `Ortex/` | `ORTEX_EMAIL`, `ORTEX_PASSWORD`, `ORTEX_CSRF_TOKEN` |
| `Trading Volatility/` | `TRADINGVOLATILITY_API_KEY` |
| `collective 2/` | `COLLECTIVE2_EMAIL`, `COLLECTIVE2_PASSWORD` (optional `COLLECTIVE2_COOKIES`) |
| `seeking alpha/` | `SEEKINGALPHA_EMAIL`, `SEEKINGALPHA_PASSWORD` |

## Folders

| Folder | Source | Output |
|---|---|---|
| `MSTR/` | mstr-tracker.com JSON endpoint | `combined_data.csv`, `combined_data2.csv`, 3 plots |
| `Ortex/` | Ortex short-interest API (authenticated) | 356 per-ticker/per-window metric CSVs |
| `Trading Volatility/` | Trading Volatility GEX API | `gamma_responses.json`, `gamma_data.csv` |
| `collective 2/` | Collective2 strategy page (scraped + authenticated) | `financial_metrics.csv`, `strategy_data.csv`, `open_positions.csv` |
| `seeking alpha/` | Seeking Alpha picks and ratings API (authenticated) | `current_alpha_picks.csv`, `closed_alpha_picks.csv`, `all_latest_quant_ratings_histories.csv` |

## Note on `Ortex/csv/id.csv`

This is the ticker → Ortex stock ID mapping (`market`, `stock_name`, `stock_id`) that
the Ortex scraper requires. It is a data file, not a credential.