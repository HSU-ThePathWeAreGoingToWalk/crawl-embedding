from app.models import Notice
from app.database import SessionLocal
from datetime import datetime

def get_latest_date():

    # SQLAlchemy 세션 생성
    session = SessionLocal()
    
    try:
        # 가장 최근 날짜 조회 (내림차순 정렬 후 첫 번째 항목)
        latest_pub_date = session.query(Notice.date).order_by(Notice.date.desc()).first()
        
        # 결과가 있으면 날짜 반환, 없으면 datetime.min 반환
        latest_pub_date = latest_pub_date[0] if latest_pub_date else datetime.min
        print(f"가장 최근 공지사항 날짜: {latest_pub_date}")
        return latest_pub_date
    
    finally:
        # 세션 종료 (예외 발생 여부와 관계없이 항상 실행)
        session.close()