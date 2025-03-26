from fastapi import FastAPI

from get_latest_notice_date import get_latest_date
from crawl import crawl_new_notices
from parse_images import update_notice_with_image_text
from embedding import store_array_to_vector_db

app = FastAPI()

@app.post("/notices/sync")
def update():

    # 1. 현재 MySql DB에서 가장 최근 공지가 실린 날짜 가져오기
    standard = get_latest_date()

    # 2. 기준일(standard) 이후의 공지만 크롤링 및 MySql DB에 저장
    crawl_new_notices(standard)

    # 3. MySQL 데이터베이스에 저장된 공지사항(notice) 중에서 이미지(URL)가 있는 항목들을 대상으로,
    #    해당 이미지에서 텍스트를 추출(OCR)한 후, 기존의 내용(content) 필드에 인식한 텍스트를 덧붙여 업데이트
    #    (기준일(standard) 이후의 공지 항목에 대해서만 수행)
    update_notice_with_image_text(standard)

    # 4. 기준일(standard) 이후의 공지 항목에 대해 임베딩 이후 Pinecone DB에 저장
    store_array_to_vector_db(standard)

