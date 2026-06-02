import requests
import os
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]
FRED_API_KEY = os.environ["FRED_API_KEY"]

def get_fed_rate():
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "FEDFUNDS",      # 미국 기준금리
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",         # 최신순
        "limit": 2                    # 최근 2개 (현재 + 이전)
    }
    res = requests.get(url, params=params)
    observations = res.json()["observations"]
    current = float(observations[0]["value"])
    previous = float(observations[1]["value"])
    date = observations[0]["date"]
    return current, previous, date

def send_teams_message(current, previous, date):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))
    change = current - previous
    arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"

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
                        "text": "🏦 미국 기준금리 알림",
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
                                    {"type": "TextBlock", "text": "현재 기준금리", "weight": "Bolder"},
                                    {"type": "TextBlock", "text": "이전 대비", "weight": "Bolder"},
                                    {"type": "TextBlock", "text": "기준일", "weight": "Bolder"},
                                    {"type": "TextBlock", "text": "조회 시간", "weight": "Bolder"},
                                ]
                            },
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {"type": "TextBlock", "text": f"{current:.2f} %"},
                                    {"type": "TextBlock", "text": f"{arrow} {change:+.2f} %p"},
                                    {"type": "TextBlock", "text": date},
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
    print(f"[{kst.strftime('%H:%M:%S')}] 기준금리 {current:.2f}%  {'✅' if res.status_code in (200,202) else '❌'}")

current, previous, date = get_fed_rate()
send_teams_message(current, previous, date)
