import os
import requests
from utils.db_utils import connect_to_db
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL_MARKETSTACK")
api_key = os.getenv("MARKETSTACK_API_KEY")
symbols = os.getenv("SYMBOLS_EOD")

def fetch_marketstack_eod(date: str):
    url = f"{base_url}/eod/{date}"
    params = {
        "access_key": api_key,
        "symbols": symbols
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch marketstack eod: {response.status_code} {response.text}")
    return response.json()

def update_marketstack_eod(eod: dict):
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO stock_prices (ticker, date, open, high, low, close, volume, asset_type, price_currency, daily_change, daily_return, volatility, avg_price, turnover, gap, range_ratio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker, date) DO UPDATE
        SET open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                asset_type = EXCLUDED.asset_type,
                price_currency = EXCLUDED.price_currency
    """
    count = 0
    for item in eod['data']:
        daily_change = item['close'] - item['open']
        daily_return = ((item['close'] - item['open']) / item['open']) * 100
        volatility = item['high'] - item['low']
        avg_price = (item['high'] + item['low']+ item['close']) / 3
        turnover = item['volume'] * item['close']
        gap = (item['high'] - item['low']) / item['open'] * 100
        range_ratio = (item['high'] - item['low']) / item['open'] * 100

        cursor.execute(sql, (item['symbol'], 
                item['date'], 
                item['open'], 
                item['high'], 
                item['low'], 
                item['close'], 
                item['volume'], 
                item['asset_type'], 
                item['price_currency'],
                daily_change,
                daily_return,
                volatility,
                avg_price,
                turnover,
                gap,
                range_ratio
                )
            )
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return count
