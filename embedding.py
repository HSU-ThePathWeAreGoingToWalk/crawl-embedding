import pymysql
import time
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

class Document:
    def __init__(self, page_content, metadata = None, id = None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
        self.id = id

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def store_array_to_vector_db(since_date: datetime):
    # DB 연결 및 cursor 생성
    db = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    # notice 테이블에서 기준일 이후 데이터 조회
    fetch_query = "SELECT id, title, content, date FROM notice WHERE date > %s"
    cursor.execute(fetch_query, (since_date,))
    rows = cursor.fetchall()

    # 임베딩 및 문서 생성
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'goheung-notice'
    documents = []
    for id, title, content, date in rows:
        date_object = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        unix_timestamp = int(time.mktime(date_object.replace(hour=0, minute=0, second=0, microsecond=0).timetuple()))
        combined_content = f"Title: {title}\nContent: {content}"
        metadata = {
            'title': title,
            'pub_date': unix_timestamp
        }
        documents.append(Document(combined_content, metadata, id=str(id)))

    PineconeVectorStore.from_documents(documents, embedding, index_name=index_name)
    print(f"{len(documents)}개의 문서가 Pinecone에 업로드되었습니다.")

    # 작업 후 연결 종료
    cursor.close()
    db.close()
