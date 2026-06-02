import yfinance as yf
import requests
import os
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

STOCKS = {
    "SK하이닉스": "000660.KS",
    "삼성전자": "005930.KS",
}

def get_stock_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.fast_info.last_price

def send_teams_message(prices):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))

    if kst.weekday() >= 5:
        print("주말 - 알림 생략")
        return
    if not (9 <= kst.hour < 15 or (kst.hour == 15 and kst.minute <= 30)):
        print("장 마감 시간 - 알림 생략")
        return

    name_items = [{"type": "TextBlock", "text": name, "weight": "Bolder"} for name in prices]
    price_items = [{"type": "TextBlock", "text": f"{price:,.0f} 원"} for price in prices.values()]
    name_items.append({"type": "TextBlock", "text": "시간", "weight": "Bolder"})
    price_items.append({"type": "TextBlock", "text": kst.strftime("%Y-%m-%d %H:%M:%S (KST)")})

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
                        "text": "📈 한국 주식 정기 알림",
                        "weight": "Bolder",
                        "size": "Large",
                        "color": "Accent"
                    },
                    {
                        "type": "ColumnSet",
                        "columns": [
                            {"type": "Column", "width": "stretch", "items": name_items},
                            {"type": "Column", "width": "stretch", "items": price_items}
                        ]
                    }
                ]
            }
        }]
    }

    res = requests.post(TEAMS_WEBHOOK_URL, json=card)
    for name, price in prices.items():
        print(f"[{kst.strftime('%H:%M:%S')}] {name} {price:,.0f}원  {'✅' if res.status_code in (200,202) else '❌'}")

prices = {name: get_stock_price(symbol) for name, symbol in STOCKS.items()}
send_teams_message(prices)
