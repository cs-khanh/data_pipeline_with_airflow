import os
import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL_WEBHOOK_SLACK")

def send_slack_message(message: str):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "text": message,
    }
    response = requests.post(URL, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to send slack message: {response.status_code} {response.text}")
    return response
