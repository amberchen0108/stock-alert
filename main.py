from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

BARK_KEY = "wbYsBbEhsHXTktBCNUVcjT"
BARK_URL = f"https://api.day.app/{BARK_KEY}"

URL = "https://www.futures-ai.com/stock-price-change-distribution"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL)
    page.wait_for_timeout(5000)

    # 👉 重點：直接抓「畫面文字」
    text = page.inner_text("body")

    browser.close()

# 👉 只抓三個最關鍵數字（跌 / 平 / 漲）
import re

matches = re.findall(r'(\d+)%', text)

print("全部數字：", matches[:10])

# 🔥 找「最可能的三個值」：跌 / 平 / 漲通常是 3 個連續
for i in range(len(matches) - 2):
    down = int(matches[i])
    flat = int(matches[i+1])
    up = int(matches[i+2])

    # 🎯 合理範圍判斷（避免亂抓）
    if down + flat + up == 100:
        break

now = datetime.now()

body = f"""日期:{now.strftime('%m/%d')}
時間:{now.strftime('%H:%M')}

跌家 {down}%
持平 {flat}%
漲家 {up}%"""

requests.post(
    BARK_URL,
    json={
        "title": "台股漲跌分布",
        "body": body
    }
)

# 🚨 警報
if down >= 70:
    requests.post(
        BARK_URL,
        json={
            "title": "⚠️ 市場警報",
            "body": "!!注意，跌家已達70%!!"
        }
    )