import os
import requests
from utils.db_utils import connect_to_db
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("BASE_URL_EXCHANGERATE")
api_key = os.getenv("EXCHANGERATE_API_KEY")
currencies = os.getenv("CURRENCIES")
def fetch_exchangerate(date: str):
    url = f"{base_url}/historical"
    params = {
        "access_key": api_key,
        "date": date,
        "currencies": currencies
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch exchangerate: {response.status_code} {response.text}")
    return response.json()

def get_yesterday_rate(date: str, base_currency: str, target_currency: str):
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = """
        SELECT rate 
        FROM exchange_rates 
        WHERE date = (SELECT MAX(date) FROM exchange_rates WHERE date < %s)
          AND base_currency = %s 
          AND target_currency = %s
    """
    cursor.execute(sql, (date, base_currency, target_currency))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None

def update_exchangerate(exchangerate: dict):
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO exchange_rates (date, base_currency, target_currency, rate, inverse_rate, rate_change)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date, base_currency, target_currency) DO UPDATE
        SET rate = EXCLUDED.rate, rate_change = EXCLUDED.rate_change
    """
    date = exchangerate['date']
    base_currency = exchangerate['source']
    target= exchangerate['quotes']
    if not target:
        raise ValueError("No quotes found in exchangerate data")
    count = 0
    for target_currency, rate in target.items():
        inverse_rate = 1 / rate if rate else None
        yesterday_rate = get_yesterday_rate(date, base_currency, target_currency)
        if yesterday_rate and yesterday_rate > 0:
            rate_change = ((rate - float(yesterday_rate)) / float(yesterday_rate)) * 100
        else:
            rate_change = None
        cursor.execute(sql, (date, base_currency, target_currency, rate, inverse_rate, rate_change))
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return count