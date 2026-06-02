import requests
import os
from datetime import datetime
import zoneinfo

TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]
FRED_API_KEY = os.environ["FRED_API_KEY"]

SERIES = {
    "🇺🇸 미국 기준금리": {"id": "FEDFUNDS", "unit": "%"},
    "🇯🇵 일본 기준금리": {"id": "IRSTCB01JPM156N", "unit": "%"},
    "🇺🇸 미국 CPI":     {"id": "CPIAUCSL", "unit": "p"},
}

def get_fred_data(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 2
    }
    res = requests.get(url, params=params)
    observations = res.json()["observations"]
    current = float(observations[0]["value"])
    previous = float(observations[1]["value"])
    date = observations[0]["date"]
    return current, previous, date

def format_change(current, previous, unit):
    change = current - previous
    arrow = "🔺" if change > 0 else "🔻" if change < 0 else "➡️"
    return f"{arrow} {change:+.2f} {unit}"

def send_teams_message(data):
    kst = datetime.now(zoneinfo.ZoneInfo("Asia/Seoul"))

    body = [
        {
            "type": "TextBlock",
            "text": "🏦 경제지표 알림",
            "weight": "Bolder",
            "size": "Large",
            "color": "Accent"
        }
    ]

    for name, info in data.items():
        current, previous, date = info["values"]
        unit = info["unit"]

        body.append({
            "type": "TextBlock",
            "text": name,
            "weight": "Bolder",
            "size": "Medium",
            "spacing": "Medium"
        })
        body.append({
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {"type": "TextBlock", "text": "현재", "weight": "Bolder"},
                        {"type": "TextBlock", "text": "이전 대비", "weight": "Bolder"},
                        {"type": "TextBlock", "text": "기준일", "weight": "Bolder"},
                    ]
                },
                {
                    "type": "Column",
                    "width": "stretch",
                    "items": [
                        {"type": "TextBlock", "text": f"{current:.2f} {unit}"},
                        {"type": "TextBlock", "text": format_change(current, previous, unit)},
                        {"type": "TextBlock", "text": date},
                    ]
                }
            ]
        })

    body.append({
        "type": "TextBlock",
        "text": f"조회 시간: {kst.strftime('%Y-%m-%d %H:%M:%S (KST)')}",
        "size": "Small",
        "spacing": "Medium"
    })

    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": body
            }
        }]
    }

    res = requests.post(TEAMS_WEBHOOK_URL, json=card)
    for name, info in data.items():
        print(f"[{kst.strftime('%H:%M:%S')}] {name} {info['values'][0]:.2f}{info['unit']}  {'✅' if res.status_code in (200,202) else '❌'}")

data = {}
for name, info in SERIES.items():
    data[name] = {
        "values": get_fred_data(info["id"]),
        "unit": info["unit"]
    }

send_teams_message(data)
