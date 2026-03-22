
from playwright.sync_api import sync_playwright

play = sync_playwright().start()
browser = play.chromium.launch(headless=False,args=["--start-maximized"])
page = browser.new_page(no_viewport=True)

page.goto("https://finance.naver.com/")
# page.pause()

###--------------------------------------------------### 뉴스 포커스 > 시황·전망 페이지로 이동
page.get_by_role("link", name="뉴스", exact=True).click()
page.locator("#contentarea_left2").get_by_role("link", name="시황·전망").click()

###--------------------------------------------------### 기사 데이터 추출
tag_list = page.locator(".realtimeNewsList > .newsList.top > dl")
subjects = tag_list.locator(".articleSubject").all()
summaries = tag_list.locator(".articleSummary").all()

news_body = []
for subject, summary in zip(subjects, summaries):
    title = subject.locator("a").get_attribute("title")
    url = subject.locator("a").get_attribute("href")
    press = summary.locator(".press").inner_text().strip()
    date = summary.locator(".wdate").inner_text().strip()
    description = summary.inner_text().replace(press, "").replace(date, "").replace("|", "").strip()
    description = description or None # 요약문이 없는 경우

    news_body.append({"title": title, "url": url, "summary": description, "press": press, "date": date})
    # print([title, url, description, press, date])

###--------------------------------------------------### json 저장
import os
import json
if os.path.exists("hw-finance.json"):
    with open("hw-finance.json", "r", encoding="utf-8") as fp:
        old = json.load(fp)["body"]
    old_id = {a["url"] for a in old} # 중복 체크용 id 생성
    news_body = [a for a in news_body if a["url"] not in old_id] # 중복 제거
else: old = []

# 누적 데이터 생성
body = old + news_body

dumped = json.dumps({"body": body}, indent=2, ensure_ascii=False)
with open("hw-finance.json", "w", encoding="utf-8") as fp:
    fp.write(dumped)