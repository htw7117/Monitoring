import yfinance as yf
import requests
import os
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

def get_rate(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.fast_info.last_price

def send_teams_message(usdjpy, usdkrw):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))

    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "환율 정기 알림",
        "themeColor": "0078D4",
        "title": "💱 환율 정기 알림",
        "sections": [{
            "facts": [
                {"name": "USD/JPY", "value": f"**{usdjpy:.3f} 엔**"},
                {"name": "USD/KRW", "value": f"**{usdkrw:.2f} 원**"},
                {"name": "시간", "value": kst.strftime("%Y-%m-%d %H:%M:%S (KST)")},
            ]
        }]
    }

    res = requests.post(TEAMS_WEBHOOK_URL, json=card)
    print(f"[{kst.strftime('%H:%M:%S')}] JPY {usdjpy:.3f} / KRW {usdkrw:.2f}  {'✅' if res.status_code in (200,202) else '❌'}")

usdjpy = get_rate("JPY=X")
usdkrw = get_rate("KRW=X")
send_teams_message(usdjpy, usdkrw)
