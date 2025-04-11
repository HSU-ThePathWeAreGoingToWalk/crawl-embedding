import time
from datetime import datetime
from models import Notice
from database import SessionLocal
from config import DATABASE

class Document:
    """
    벡터 데이터베이스에 저장할 문서를 나타내는 클래스
    
    Attributes:
        page_content (str): 문서의 내용
        metadata (dict): 문서의 메타데이터 (제목, 날짜 등)
        id (str): 문서의 고유 식별자
    """
    def __init__(self, page_content, metadata = None, id = None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
        self.id = id

def store_array_to_vector_db(since_date: datetime):
    """
    기준일 이후의 공지사항을 벡터 데이터베이스(Pinecone)에 저장
    
    Args:
        since_date (datetime): 기준일. 이 날짜 이후의 공지사항만 처리
    
    Returns:
        None
    """
    session = SessionLocal()
    try:
        # notice 테이블에서 기준일 이후 데이터 조회
        rows = session.query(Notice).filter(Notice.date > since_date).all()
        
        if not rows:
            print("처리할 공지사항이 없습니다.")
            return

        # 임베딩 및 문서 생성
        documents = []
        for notice in rows:
            
            # 날짜를 Unix 타임스탬프로 변환 (시간 정보 제거)
            date_object = datetime.strptime(str(notice.date), "%Y-%m-%d %H:%M:%S")
            unix_timestamp = int(time.mktime(date_object.replace(hour=0, minute=0, second=0, microsecond=0).timetuple()))
            
            # 제목과 내용을 결합하여 문서 생성
            combined_content = f"Title: {notice.title}\nContent: {notice.content}"
            
            # 메타데이터 설정
            metadata = {
                'title': notice.title,
                'pub_date': unix_timestamp
            }
            
            # Document 객체 생성 및 리스트에 추가
            documents.append(Document(combined_content, metadata, id=str(notice.id)))

        # config.py에서 가져온 DATABASE 객체를 사용하여 Pinecone에 문서 저장
        DATABASE.add_documents(documents)
        print(f"{len(documents)}개의 문서가 Pinecone에 업로드되었습니다.")
    
    finally:
        # 세션 종료 (예외 발생 여부와 관계없이 항상 실행)
        session.close()