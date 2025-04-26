from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base, Notice
from app.database import engine, SessionLocal
from app.get_latest_notice_date import get_latest_date
from app.crawl import crawl_new_notices
from app.parse_images import update_notice_with_image_text
from app.embedding import store_array_to_vector_db
from typing import List

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (프로덕션에서는 특정 도메인으로 제한하는 것이 좋음)
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # OPTIONS 메소드 명시적 허용
    allow_headers=["*"],
)

# SQLAlchemy 모델에 정의된 모든 테이블을 데이터베이스에 생성
# 이 코드는 애플리케이션 시작 시 한 번만 실행되며, 테이블이 이미 존재하면 아무 작업도 수행하지 않음
Base.metadata.create_all(bind=engine)

@app.post("/notices/sync", response_model=List[str])
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
    
    # 5. 파인콘에 업로드된 공지 제목 목록을 반환
    session = SessionLocal()
    try:
        # 업로드된 공지(기준일 이후의 공지) 제목 가져오기
        notices = session.query(Notice.title).filter(Notice.date > standard).all()
        
        # SQLAlchemy 결과를 단순 문자열 리스트로 변환
        titles = [notice[0] for notice in notices]
        return titles
    finally:
        session.close()
