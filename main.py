import yfinance as yf
import requests
import os
from datetime import datetime

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

def get_usdjpy():
    ticker = yf.Ticker("JPY=X")
    return ticker.fast_info.last_price

def send_teams_message(rate):
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "USD/JPY 환율 정기 알림",
        "themeColor": "0078D4",
        "title": "💱 USD/JPY 환율 정기 알림",
        "sections": [{
            "facts": [
                {"name": "현재 환율", "value": f"**{rate:.3f} 엔**"},
                {"name": "시간", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            ]
        }]
    }
    res = requests.post(TEAMS_WEBHOOK_URL, json=card)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {rate:.3f} 엔  {'✅' if res.status_code in (200,202) else '❌'}")

rate = get_usdjpy()
send_teams_message(rate)
