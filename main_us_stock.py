import yfinance as yf
import requests
import os
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

STOCKS = {
    "GE Vernova": "GEV",
    "OKTA": "OKTA",
}

def get_stock_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    return ticker.fast_info.last_price

def send_teams_message(prices):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))
    et = datetime.now(zoneinfo.ZoneInfo("America/New_York"))

    # 장 운영 시간 체크 (평일 09:30~16:00 ET)
    if et.weekday() >= 5:
        print("주말 - 알림 생략")
        return
    market_open = et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et.replace(hour=16, minute=0, second=0, microsecond=0)
    if not (market_open <= et <= market_close):
        print("장 마감 시간 - 알림 생략")
        return

    name_items = [{"type": "TextBlock", "text": name, "weight": "Bolder"} for name in prices]
    price_items = [{"type": "TextBlock", "text": f"$ {price:,.2f}"} for price in prices.values()]
    name_items.append({"type": "TextBlock", "text": "시간 (KST)", "weight": "Bolder"})
    price_items.append({"type": "TextBlock", "text": kst.strftime("%Y-%m-%d %H:%M:%S")})

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
                        "text": "🇺🇸 미국 주식 정기 알림",
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
        print(f"[{kst.strftime('%H:%M:%S')}] {name} ${price:,.2f}  {'✅' if res.status_code in (200,202) else '❌'}")

prices = {name: get_stock_price(symbol) for name, symbol in STOCKS.items()}
send_teams_message(prices)
