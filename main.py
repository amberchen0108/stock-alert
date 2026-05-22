from playwright.sync_api import sync_playwright
import requests
from datetime import datetime
import os
import re

# =========================
# Bark 設定（從 GitHub Secret 讀取）
# =========================
BARK_KEY = os.environ["BARK_KEY"]
BARK_URL = f"https://api.day.app/{BARK_KEY}"

# =========================
# 網站
# =========================
URL = "https://www.futures-ai.com/stock-price-change-distribution"

# =========================
# Playwright 抓資料
# =========================
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL)

    # 等待頁面載入
    page.wait_for_timeout(5000)

    # 抓畫面文字
    text = page.inner_text("body")

    browser.close()

# =========================
# 找百分比
# =========================
matches = re.findall(r'(\d+)%', text)

print("原始抓取：", matches[:20])

down = None
flat = None
up = None

# 找加總 = 100 的三個數字
for i in range(len(matches) - 2):

    a = int(matches[i])
    b = int(matches[i + 1])
    c = int(matches[i + 2])

    if a + b + c == 100:
        down = a
        flat = b
        up = c
        break

# 如果沒找到（保底）
if down is None:
    down = int(matches[0])
    flat = int(matches[1])
    up = int(matches[2])

# =========================
# 日期時間
# =========================
now = datetime.now()

date_text = now.strftime("%m/%d")
time_text = now.strftime("%H:%M")

# =========================
# 推播內容
# =========================
body = f"""日期:{date_text}
時間:{time_text}

跌家 {down}%
持平 {flat}%
漲家 {up}%"""

# =========================
# 發送 Bark
# =========================
response = requests.post(
    BARK_URL,
    json={
        "title": "台股漲跌分布",
        "body": body
    }
)

print(response.text)

# =========================
# 恐慌警報
# =========================
if down >= 70:

    requests.post(
        BARK_URL,
        json={
            "title": "⚠️ 市場警報",
            "body": "!!注意，跌家已達70%!!"
        }
    )

    print("已發送恐慌警報")
