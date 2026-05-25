from playwright.sync_api import sync_playwright
import requests
from datetime import datetime, timedelta
import os
import re

BARK_KEY = os.environ["BARK_KEY"]
BARK_URL = f"https://api.day.app/{BARK_KEY}"

URL = "https://www.futures-ai.com/stock-price-change-distribution"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL)

    page.wait_for_timeout(10000)

    text = page.inner_text("body")

    browser.close()

# =========================
# 精準抓取「47% 8% 45%」
# =========================

matches = re.findall(r'(\d+)%', text)

print(matches)

down = None
flat = None
up = None

# 尋找最合理組合
for i in range(len(matches)-2):

    a = int(matches[i])
    b = int(matches[i+1])
    c = int(matches[i+2])

    # 必須加總100
    if a + b + c == 100:

        # 排除奇怪大數字
        if a <= 100 and b <= 20 and c <= 100:

            down = a
            flat = b
            up = c

            break

# 找不到時保底
if down is None:

    down = 0
    flat = 0
    up = 0

# 台灣時間
now = datetime.utcnow() + timedelta(hours=8)

body = f"""日期:{now.strftime('%m/%d')}
時間:{now.strftime('%H:%M')}

跌家 {down}%
持平 {flat}%
漲家 {up}%"""

# 發送 Bark
requests.post(
    BARK_URL,
    json={
        "title": "台股漲跌分布",
        "body": body
    }
)

# 跌家警報
if down >= 70:

    requests.post(
        BARK_URL,
        json={
            "title": "⚠️ 市場警報",
            "body": "!!注意，跌家已達70%!!"
        }
    )
