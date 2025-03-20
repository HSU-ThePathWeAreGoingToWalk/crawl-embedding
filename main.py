from fastapi import FastAPI

import about_update_notices
from crawl import crawl_new_notices

app = FastAPI()

@app.post("/update-notices")
def update():

    # 1. 현재 DB에서 가장 최근 공지가 실린 날짜 가져오기
    standard = about_update_notices.get_latest_date()

    # 2. 크롤링 및 DB 저장
    crawl_new_notices()

    # 3. 현재 DB에서 standard 이후의 공지만 필터링 && 임베딩 이후 Pinecone에 저장
    # 코딩 예정


