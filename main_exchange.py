import yfinance as yf
import requests
import os
import csv
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

def get_rate(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.fast_info.last_price

def send_teams_message(usdjpy, usdkrw):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))

    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "💱 환율 정기 알림",
                        "weight": "Bolder",
                        "size": "Large",
                        "color": "Accent"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {"type": "TextBlock", "text": "USD/JPY", "weight": "Bolder"},
                                    {"type": "TextBlock", "text": "USD/KRW", "weight": "Bolder"},
                                    {"type": "TextBlock", "text": "시간", "weight": "Bolder"},
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {"type": "TextBlock", "text": f"{usdjpy:.3f} 엔"},
                                    {"type": "TextBlock", "text": f"{usdkrw:.2f} 원"},
                                    {"type": "TextBlock", "text": kst.strftime("%Y-%m-%d %H:%M:%S (KST)")},
                                ]
                            }
                        ]
                    }
                ]
            }
        }]
    }

    res = requests.post(TEAMS_WEBHOOK_URL, json=card)
    print(f"[{kst.strftime('%H:%M:%S')}] JPY {usdjpy:.3f} / KRW {usdkrw:.2f}  {'✅' if res.status_code in (200,202) else '❌'}")

def save_to_csv(usdjpy, usdkrw):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))
    filepath = "data/exchange.csv"
    file_exists = os.path.isfile(filepath)

    os.makedirs("data", exist_ok=True)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["시간", "USD/JPY", "USD/KRW"])  # 헤더
        writer.writerow([
            kst.strftime("%Y-%m-%d %H:%M:%S"),
            round(usdjpy, 3),
            round(usdkrw, 2)
        ])

    print(f"CSV 저장 완료")

usdjpy = get_rate("JPY=X")
usdkrw = get_rate("KRW=X")
send_teams_message(usdjpy, usdkrw)
save_to_csv(usdjpy, usdkrw)
