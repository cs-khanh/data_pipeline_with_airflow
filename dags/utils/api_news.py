import os
import time
import requests
from utils.db_utils import connect_to_db
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("BASE_URL_NEWS")
api_key = os.getenv("NEWS_API_KEY")

def fetch_news(symbol: str,date: str):
    url = f"{base_url}/news/all"
    params = {
        "symbols": symbol,
        "filter_entities": "true",
        "language": "en",
        "published_on": date,
        "limit": 2,
        "api_token": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news: {response.status_code} {response.text}")

    return response.json()
def sentiment_label(sentiment_score: float):
    if sentiment_score > 0.5:
        return "Positive"
    elif sentiment_score < -0.5:
        return "Negative"
    else:
        return "Neutral"

def cal_impact_index(sentiment_score,relevance_score , match_score):
    if relevance_score == None:
        return abs(sentiment_score)* match_score * 100
    else:
        return abs(sentiment_score)* relevance_score * 100

def cal_weighted_sentiment(sentiment_score: float,relevance_score: float, match_score: float):
    if relevance_score == None:
        return abs(sentiment_score)* match_score
    else:
        return abs(sentiment_score)* relevance_score

def update_news(news: dict):
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO news (uuid, title, description, url, image_url, language, source, relevance_score, symbol, country, type, industry, match_score, sentiment_score, sentiment_label, impact_index, weighted_sentiment, published_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (uuid) DO UPDATE
        SET title = EXCLUDED.title,
            description = EXCLUDED.description,
            url = EXCLUDED.url,
            image_url = EXCLUDED.image_url,
            language = EXCLUDED.language,
            source = EXCLUDED.source,
            relevance_score = EXCLUDED.relevance_score,
            symbol = EXCLUDED.symbol,
            country = EXCLUDED.country,
            type = EXCLUDED.type,
            industry = EXCLUDED.industry,
            match_score = EXCLUDED.match_score,
            sentiment_score = EXCLUDED.sentiment_score,
            sentiment_label = EXCLUDED.sentiment_label,
            impact_index = EXCLUDED.impact_index,
            weighted_sentiment = EXCLUDED.weighted_sentiment,
            published_at = EXCLUDED.published_at
        """
    count = 0
    for item in news['data']:
        sentiment_score = item['entities'][0]['sentiment_score']
        relevance_score = item['relevance_score']
        match_score = item['entities'][0]['match_score']
        impact_index = cal_impact_index(sentiment_score,relevance_score, match_score)
        weighted_sentiment = cal_weighted_sentiment(sentiment_score,relevance_score, match_score)
        cursor.execute(sql, (item['uuid'], 
                    item['title'], 
                    item['description'], 
                    item['url'], 
                    item['image_url'], 
                    item['language'], 
                    item['source'], 
                    relevance_score, 
                    item['entities'][0]['symbol'], 
                    item['entities'][0]['country'], 
                    item['entities'][0]['type'], 
                    item['entities'][0]['industry'], 
                    match_score, 
                    sentiment_score,
                    sentiment_label(sentiment_score),
                    impact_index,
                    weighted_sentiment,

                    item['published_at'])
                )
        count += 1
    conn.commit()
    cursor.close()
    conn.close()
    return count