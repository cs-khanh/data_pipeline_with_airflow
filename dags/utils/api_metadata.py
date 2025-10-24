import os
import requests
from utils.db_utils import connect_to_db
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL_MARKETSTACK")
api_key = os.getenv("MARKETSTACK_API_KEY")

def fetch_marketstack_metadata(limit: int = 500):
    url = f"{base_url}/tickerslist"

    params = {
        "access_key": api_key,
        "limit": limit
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch marketstack metadata: {response.status_code} {response.text}")
    return response.json()

def update_marketstack_metadata(metadata: dict):
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO tickers_metadata (
            ticker, name, has_intraday, has_eod,
            stock_exchange_name, acronym, mic
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (ticker) DO UPDATE
        SET name = EXCLUDED.name,
            has_intraday = EXCLUDED.has_intraday,
            has_eod = EXCLUDED.has_eod,
            stock_exchange_name = EXCLUDED.stock_exchange_name,
            acronym = EXCLUDED.acronym,
            mic = EXCLUDED.mic;
    """
    count = 0
    for item in metadata['data']:
        cursor.execute(sql, (
            item['ticker'], 
            item['name'], 
            item['has_intraday'], 
            item['has_eod'],
            item['stock_exchange']['name'],
            item['stock_exchange']['acronym'], 
            item['stock_exchange']['mic']
        ))
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return count

def metadata_exits():

    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM tickers_metadata LIMIT 1")
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists
